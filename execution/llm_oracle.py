"""
LLM Oracle (Gemini Vision)
Interprets a post-submission screenshot using Gemini 2.0 Flash.
Called only when the heuristic oracle reports confidence < 70
AND the RL agent decides action = 1 (escalate).

Cost: ~$0.002 per call.
"""

import sys
import base64
import json
import asyncio
import re
from pathlib import Path
from typing import Dict, Optional

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from crawler.gemini_key_rotator import GeminiKeyRotator
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


ORACLE_PROMPT_TEMPLATE = """You are a test oracle for web application testing.

A test case was executed:
- Test Type: {test_type}
- Test Value Submitted: {test_value}
- Expected Result: {expected_result}
- Original URL: {original_url}
- Current URL: {current_url}

Look at the screenshot of the page AFTER form submission.

Determine:
1. Did the form submission SUCCEED (page changed, success message, redirect) or FAIL (error message, validation warning, page unchanged)?
2. Does the outcome MATCH the expected result?

Respond ONLY with a JSON object (no markdown, no explanation):
{{
  "outcome": "success" or "error",
  "confidence": <integer 0-100>,
  "evidence": "<one sentence describing what you saw>"
}}
"""


class LLMOracle:
    """
    Calls Gemini Vision with a screenshot to determine test outcome.
    Reuses the existing GeminiKeyRotator for key rotation and rate limits.
    """

    def __init__(self):
        self.rotator = GeminiKeyRotator()
        self.api_calls_made = 0

    async def evaluate(
        self,
        page,
        test_case: dict,
        screenshot_path: Optional[str] = None,
    ) -> Dict:
        """
        Take a screenshot and ask Gemini to interpret the result.

        Args:
            page:            Playwright Page object
            test_case:       The test case dict (needs test_type, test_value,
                             expected_result, form_url)
            screenshot_path: If provided, save screenshot here; else temp path

        Returns:
            {"outcome": str, "confidence": int, "evidence": str}
        """
        # ── Screenshot ────────────────────────────────────────────────────
        save_path = screenshot_path or f"data/test_results/_tmp_screenshot.png"
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)

        try:
            await page.screenshot(path=save_path, full_page=False)
        except Exception as e:
            logger.warning(f"Screenshot failed: {e}")
            return {"outcome": "unclear", "confidence": 0,
                    "evidence": f"Screenshot capture failed: {e}"}

        # ── Build prompt ──────────────────────────────────────────────────
        current_url = page.url
        prompt = ORACLE_PROMPT_TEMPLATE.format(
            test_type       = test_case.get("type", "unknown"),
            test_value      = test_case.get("test_value", ""),
            expected_result = test_case.get("expected_result", ""),
            original_url    = test_case.get("form_url", ""),
            current_url     = current_url,
        )

        # ── Call Gemini with key rotation ─────────────────────────────────
        api_key = self.rotator.get_current_key()
        if not api_key:
            return {"outcome": "unclear", "confidence": 0,
                    "evidence": "No Gemini API keys available"}

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-3.1-flash-lite-preview")

            with open(save_path, "rb") as f:
                img_bytes = f.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            # Run synchronous SDK call in executor to keep async clean
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content([
                    prompt,
                    {"mime_type": "image/png", "data": img_b64},
                ])
            )

            self.api_calls_made += 1
            self.rotator.mark_success()

            raw = response.text.strip()
            # Strip markdown code fences if present
            raw = re.sub(r"^```[a-z]*\n?", "", raw, flags=re.MULTILINE)
            raw = re.sub(r"```$", "", raw, flags=re.MULTILINE).strip()

            parsed = json.loads(raw)
            return {
                "outcome":    parsed.get("outcome", "unclear"),
                "confidence": int(parsed.get("confidence", 50)),
                "evidence":   parsed.get("evidence", "LLM evaluation"),
            }

        except json.JSONDecodeError:
            logger.warning(f"LLM oracle: non-JSON response: {raw[:200]}")
            # Try to extract outcome from plain text
            text_lower = raw.lower()
            if "success" in text_lower:
                return {"outcome": "success", "confidence": 55,
                        "evidence": "Parsed from non-JSON LLM response"}
            elif "error" in text_lower or "fail" in text_lower:
                return {"outcome": "error", "confidence": 55,
                        "evidence": "Parsed from non-JSON LLM response"}
            return {"outcome": "unclear", "confidence": 30,
                    "evidence": "LLM returned unparseable response"}

        except Exception as e:
            logger.error(f"LLM oracle error: {e}")
            # Rotate key on error
            self.rotator.rotate_key()
            return {"outcome": "unclear", "confidence": 0,
                    "evidence": f"LLM call failed: {type(e).__name__}"}
