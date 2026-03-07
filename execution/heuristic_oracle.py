"""
Heuristic Oracle
Zero-cost, zero-API outcome verification using DOM analysis.
Runs after every test submission.  When confidence < 70 the RL agent
decides whether to escalate to the LLM oracle.
"""

import re
from typing import Dict


# Keywords that strongly suggest a successful submission
SUCCESS_KEYWORDS = [
    "success", "successfully", "thank you", "thank-you", "thankyou",
    "submitted", "submission received", "confirmed", "complete",
    "congratulations", "welcome", "logged in", "signed in",
    "registration complete", "account created", "order placed",
    "payment accepted", "saved", "updated", "created",
]

# Keywords that strongly suggest an error / rejection
ERROR_KEYWORDS = [
    "error", "invalid", "incorrect", "wrong", "failed", "failure",
    "required", "must be", "please enter", "please provide",
    "not found", "does not exist", "unauthorized", "forbidden",
    "password is", "username is", "email is", "field is",
    "try again", "went wrong", "problem", "issue",
]

# CSS selectors / ARIA-like attributes for toast / alert banners
ALERT_SELECTORS = [
    "[role='alert']",
    "[role='status']",
    ".alert", ".notification", ".toast", ".snackbar",
    ".message", ".feedback", ".banner",
    "#error-message", "#success-message",
    ".error", ".success", ".warning", ".info",
    "[class*='alert']", "[class*='toast']", "[class*='error']",
    "[class*='success']",
]


class HeuristicOracle:
    """
    Interprets a Playwright page after form submission without any API calls.

    Returns:
        {
            "outcome":    "success" | "error" | "unclear",
            "confidence": 0-100,
            "evidence":   str   (human-readable explanation)
        }
    """

    async def evaluate(
        self,
        page,
        original_url: str,
        expected_result: str,
    ) -> Dict:
        """
        Evaluate the page state after test execution.

        Args:
            page:            Playwright Page object (already past submission)
            original_url:    URL the test started from
            expected_result: 'valid' | 'invalid' | raw expected string from test case
        """
        signals: list[str] = []
        score_positive = 0
        score_negative = 0

        # ── 1. URL CHANGE ──────────────────────────────────────────────────
        current_url = page.url
        if current_url != original_url:
            signals.append(f"URL changed → {current_url}")
            score_positive += 25
        else:
            signals.append("URL unchanged (stayed on same page)")
            score_negative += 10

        # ── 2. PAGE TITLE ──────────────────────────────────────────────────
        try:
            title = (await page.title()).lower()
            if any(k in title for k in SUCCESS_KEYWORDS):
                signals.append(f"Page title contains success keyword: '{title}'")
                score_positive += 20
            elif any(k in title for k in ERROR_KEYWORDS):
                signals.append(f"Page title contains error keyword: '{title}'")
                score_negative += 20
        except Exception:
            pass

        # ── 3. DOM KEYWORD SCAN (visible text) ────────────────────────────
        try:
            body_text = (await page.inner_text("body")).lower()
            found_success = [k for k in SUCCESS_KEYWORDS if k in body_text]
            found_error   = [k for k in ERROR_KEYWORDS   if k in body_text]

            if found_success:
                signals.append(f"Body contains success words: {found_success[:3]}")
                score_positive += 15 * min(len(found_success), 3)
            if found_error:
                signals.append(f"Body contains error words: {found_error[:3]}")
                score_negative += 10 * min(len(found_error), 3)
        except Exception:
            pass

        # ── 4. ALERT / TOAST BANNERS ──────────────────────────────────────
        for selector in ALERT_SELECTORS:
            try:
                elements = await page.query_selector_all(selector)
                for el in elements[:3]:
                    text = (await el.inner_text()).strip().lower()
                    if not text:
                        continue
                    if any(k in text for k in SUCCESS_KEYWORDS):
                        signals.append(f"Alert/toast success: '{text[:80]}'")
                        score_positive += 30
                    elif any(k in text for k in ERROR_KEYWORDS):
                        signals.append(f"Alert/toast error: '{text[:80]}'")
                        score_negative += 30
            except Exception:
                continue

        # ── 5. FORM STILL PRESENT ─────────────────────────────────────────
        try:
            form_present = await page.query_selector("form")
            if form_present:
                signals.append("Form is still present on page (possible failure)")
                score_negative += 5
            else:
                signals.append("No form on page (likely navigated away)")
                score_positive += 10
        except Exception:
            pass

        # ── 6. MAP AGAINST EXPECTED RESULT ────────────────────────────────
        expected_lower = expected_result.lower()
        if "valid" in expected_lower and "invalid" not in expected_lower:
            # Test expected success — positive signals are confirmations
            total = score_positive + score_negative
            if total == 0:
                confidence = 40
                outcome = "unclear"
            elif score_positive > score_negative:
                confidence = min(90, 50 + score_positive)
                outcome = "success"
            else:
                confidence = min(85, 50 + score_negative)
                outcome = "error"
        elif "invalid" in expected_lower or "error" in expected_lower:
            # Test expected error — negative signals confirm correct rejection
            if score_negative >= score_positive:
                confidence = min(90, 50 + score_negative)
                outcome = "success"   # rejection was expected, so this IS success
            else:
                confidence = min(85, 50 + score_positive)
                outcome = "error"
        else:
            # Generic expected result
            if score_positive > score_negative + 10:
                confidence = min(85, 50 + score_positive - score_negative)
                outcome = "success"
            elif score_negative > score_positive + 10:
                confidence = min(85, 50 + score_negative - score_positive)
                outcome = "error"
            else:
                confidence = 40
                outcome = "unclear"

        # Clamp confidence
        confidence = max(10, min(95, confidence))

        evidence = " | ".join(signals) if signals else "No strong signals detected"
        return {
            "outcome":    outcome,
            "confidence": confidence,
            "evidence":   evidence,
        }
