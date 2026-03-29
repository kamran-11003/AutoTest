"""
Base Test Runner
Executes a single test case against a live Playwright browser page.
Handles navigation, form filling, wizard progression, submission, and
calls the heuristic oracle.
"""

import sys
import json
import time
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from execution.test_result import TestResult, TestStatus, OracleMethod
from execution.heuristic_oracle import HeuristicOracle
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# Playwright timeout defaults (ms)
NAV_TIMEOUT   = 20_000
ACTION_TIMEOUT = 8_000


class BaseRunner:
    """
    Executes a single test case on a Playwright page.

    Returns a (TestResult, heuristic_result) tuple so the adaptive runner
    can decide whether to call the LLM oracle.
    """

    def __init__(self, screenshots_dir: str = "data/test_results/screenshots"):
        self.oracle = HeuristicOracle()
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    async def run(
        self,
        page,
        test_case: dict,
        take_screenshot: bool = True,
    ) -> Tuple[TestResult, dict]:
        """
        Execute one test case.

        Args:
            page:            Playwright Page
            test_case:       dict from test_storage (BVA/ECP/etc format)
            take_screenshot: Save screenshot for LLM oracle / report

        Returns:
            (TestResult, heuristic_dict)
            where heuristic_dict = {outcome, confidence, evidence}
        """
        test_id      = test_case.get("id", "unknown")
        form_url     = test_case.get("form_url", "")
        test_data    = test_case.get("test_data", {})
        expected     = test_case.get("expected_result", "")
        test_type    = test_case.get("type", "")
        test_value   = str(test_case.get("test_value", ""))
        screenshot_path: Optional[str] = None
        start_ms     = time.perf_counter() * 1000

        try:
            # ── Register dialog listener ─────────────────────────────────
            # Capture alert()/confirm()/prompt() messages before Playwright
            # auto-dismisses them.  Stored on the page object so the oracle
            # can read them via page._autotestai_dialog_messages.
            if not hasattr(page, '_autotestai_dialog_messages'):
                page._autotestai_dialog_messages = []

                async def _handle_dialog(dialog):
                    page._autotestai_dialog_messages.append(dialog.message)
                    try:
                        await dialog.dismiss()
                    except Exception:
                        pass

                page.on("dialog", _handle_dialog)

            # Clear previous messages for this test run
            page._autotestai_dialog_messages.clear()

            # ── Navigate ─────────────────────────────────────────────────
            if form_url:
                await page.goto(form_url, timeout=NAV_TIMEOUT, wait_until="domcontentloaded")
                await asyncio.sleep(0.5)

            original_url = page.url

            # ── Fill form fields ─────────────────────────────────────────
            if test_data:
                await self._fill_fields(page, test_data)

            # ── Submit ───────────────────────────────────────────────────
            submit_result = await self._click_submit(page)

            if submit_result == "disabled":
                duration_ms = time.perf_counter() * 1000 - start_ms
                logger.info(f"[{test_id}] Submit button disabled — skipping")
                result = TestResult(
                    test_id=test_id,
                    status=TestStatus.SKIPPED,
                    duration_ms=duration_ms,
                    evidence="Submit button was disabled — test unexecutable as loaded",
                    test_type=test_type,
                    form_url=form_url,
                    test_value=test_value,
                    expected_result=expected,
                )
                return result, {"outcome": "unclear", "confidence": 0, "evidence": "disabled submit button"}

            if submit_result == "not_found":
                duration_ms = time.perf_counter() * 1000 - start_ms
                logger.info(f"[{test_id}] No submit button found — skipping")
                result = TestResult(
                    test_id=test_id,
                    status=TestStatus.SKIPPED,
                    duration_ms=duration_ms,
                    evidence="No submit button found on page — decorative form or missing submission target",
                    test_type=test_type,
                    form_url=form_url,
                    test_value=test_value,
                    expected_result=expected,
                )
                return result, {"outcome": "unclear", "confidence": 0, "evidence": "no submit button"}

            # submit_result == "clicked"

            await asyncio.sleep(1.0)   # wait for page reaction

            # ── Screenshot ───────────────────────────────────────────────
            if take_screenshot:
                screenshot_path = str(
                    self.screenshots_dir / f"{test_id}.png"
                )
                try:
                    await page.screenshot(path=screenshot_path, full_page=False)
                except Exception:
                    screenshot_path = None

            # ── Heuristic oracle ─────────────────────────────────────────
            heuristic = await self.oracle.evaluate(page, original_url, expected)
            confidence = heuristic["confidence"]
            outcome    = heuristic["outcome"]

            # Map outcome to TestStatus.
            # Note: ERROR only when the oracle truly can't determine what happened
            # (outcome="unclear"). Low confidence alone does NOT mean ERROR —
            # the adaptive runner uses confidence to decide whether to also call
            # the LLM oracle; that is a separate concern from the status.
            if outcome == "success":
                status = TestStatus.PASSED
            elif outcome == "error":
                status = TestStatus.FAILED
            else:
                status = TestStatus.ERROR   # genuinely unclear — needs LLM

            duration_ms = time.perf_counter() * 1000 - start_ms

            result = TestResult(
                test_id         = test_id,
                status          = status,
                duration_ms     = duration_ms,
                oracle_method   = OracleMethod.HEURISTIC,
                confidence      = confidence,
                evidence        = heuristic["evidence"],
                screenshot_path = screenshot_path,
                test_type       = test_type,
                form_url        = form_url,
                test_value      = test_value,
                expected_result = expected,
            )
            return result, heuristic

        except Exception as e:
            duration_ms = time.perf_counter() * 1000 - start_ms
            logger.error(f"[{test_id}] Execution error: {e}")
            result = TestResult(
                test_id       = test_id,
                status        = TestStatus.ERROR,
                duration_ms   = duration_ms,
                error_message = str(e),
                test_type     = test_type,
                form_url      = form_url,
                test_value    = test_value,
                expected_result = expected,
            )
            return result, {"outcome": "unclear", "confidence": 0, "evidence": str(e)}

    # ── Private helpers ────────────────────────────────────────────────────

    async def _fill_fields(self, page, test_data: dict) -> Set[str]:
        """
        Fill form fields from *test_data* ``{field_name: value}``.

        Supports an optional ``_selectors`` key mapping field names to explicit
        CSS selectors (used for nameless fields captured during crawling).

        On wizard forms, if the primary field under test is not yet visible,
        calls ``_advance_wizard_to_field`` to navigate to the right step first.

        Returns the set of field names successfully filled.
        """
        selector_overrides: dict = {}
        if "_selectors" in test_data:
            selector_overrides = test_data.pop("_selectors") or {}

        filled: Set[str] = set()

        for field_name, value in test_data.items():
            if value is None or not field_name or field_name.startswith("_"):
                continue

            # If the field isn't visible yet, try advancing through wizard steps
            if not await self._is_field_visible(page, field_name):
                await self._advance_wizard_to_field(page, field_name, test_data, filled)

            ok = await self._fill_one(page, field_name, value, selector_overrides)
            if ok:
                filled.add(field_name)

        return filled

    async def _is_field_visible(self, page, field_name: str) -> bool:
        """Return True when any element for *field_name* (name or id) is visible."""
        for sel in [
            f"input[name='{field_name}']",
            f"textarea[name='{field_name}']",
            f"select[name='{field_name}']",
            f"#{field_name}",
        ]:
            try:
                el = await page.query_selector(sel)
                if el and await el.is_visible():
                    return True
            except Exception:
                pass
        return False

    async def _fill_one(self, page, field_name: str, value, selector_overrides: dict) -> bool:
        """
        Try to fill a single field using four fallback strategies.
        Returns True on success.
        """
        str_value = str(value)

        # Strategy 0: explicit CSS selector override (nameless/crawled fields)
        if field_name in selector_overrides:
            try:
                el = await page.query_selector(selector_overrides[field_name])
                if el:
                    await self._apply_value(el, str_value)
                    return True
            except Exception:
                pass

        # Strategy 1: name attribute (input / textarea / select)
        for selector in [
            f"input[name='{field_name}']",
            f"textarea[name='{field_name}']",
            f"select[name='{field_name}']",
        ]:
            try:
                el = await page.query_selector(selector)
                if el and await el.is_visible():
                    await self._apply_value(el, str_value)
                    return True
            except Exception:
                continue

        # Strategy 2: id attribute (also handles <select id="...">)
        try:
            el = await page.query_selector(f"#{field_name}")
            if el and await el.is_visible():
                await self._apply_value(el, str_value)
                return True
        except Exception:
            pass

        # Strategy 3: placeholder / aria-label substring match
        for attr in ["placeholder", "aria-label"]:
            try:
                el = await page.query_selector(f"input[{attr}*='{field_name}']")
                if el and await el.is_visible():
                    await self._apply_value(el, str_value)
                    return True
            except Exception:
                continue

        return False

    async def _apply_value(self, el, str_value: str) -> None:
        """Write *str_value* into element, bypassing HTML5 browser-side constraints.

        Uses a pure-JS approach: sets maxlength to a very large number (instead
        of removing it, which leaves the property at -1 and can still cause
        Playwright to truncate via keyboard simulation), then directly assigns
        node.value and fires input/change events.

        This ensures:
        - Long values are NOT truncated by the browser (maxLength=999999 >> any test value)
        - Short values below minlength ARE submitted (minlength removed)
        - Empty values for required fields ARE submitted (required removed)
        - Non-email/non-number format values are submitted (type coerced to text)
        - React/Vue/Angular controlled inputs update (native setter + input/change events)
        - Form constraint validation does not block submit (maxlength set high, not absent)
        """
        try:
            tag = (await el.get_attribute("tagName") or "input").lower()
            if tag == "select":
                await el.select_option(str_value)
            else:
                await el.evaluate(
                    """(node, val) => {
                        // Set maxlength to a huge value instead of removing it.
                        // Removing sets maxLength=-1 but some Playwright internals
                        // still truncate; a large explicit value is reliable.
                        node.setAttribute('maxlength', '999999');
                        node.setAttribute('minlength', '0');
                        node.removeAttribute('required');
                        node.removeAttribute('pattern');
                        if (node.type === 'email' || node.type === 'number') {
                            node.type = 'text';
                        }
                        // Use native setter so React/Vue hooks fire correctly.
                        var proto = Object.getPrototypeOf(node);
                        var descriptor = Object.getOwnPropertyDescriptor(proto, 'value');
                        if (descriptor && descriptor.set) {
                            descriptor.set.call(node, val);
                        } else {
                            node.value = val;
                        }
                        node.dispatchEvent(new Event('input',  {bubbles: true}));
                        node.dispatchEvent(new Event('change', {bubbles: true}));
                    }""",
                    str_value
                )
        except Exception:
            pass

    # ── Wizard navigation ──────────────────────────────────────────────────

    # Selectors for "advance to next step" buttons – intentionally NOT final submit
    _NEXT_SELECTORS = [
        "button:has-text('Next')",
        "button:has-text('Continue')",
        "button:has-text('Proceed')",
        "a:has-text('Next')",
        "a:has-text('Continue')",
        "input[value*='Next' i]",
        "input[value*='Continue' i]",
        "[class*='wizard-next']",
    ]

    async def _advance_wizard_to_field(
        self,
        page,
        target_field: str,
        test_data: dict,
        already_filled: Set[str],
        max_steps: int = 5,
    ) -> None:
        """
        Navigate through wizard steps until *target_field* becomes visible.

        For each step: fill visible companion fields → click Next → wait for
        the set of visible inputs to change (works for any wizard implementation,
        not just ones using a specific CSS class or data-step attribute).
        """
        for _ in range(max_steps):
            if await self._is_field_visible(page, target_field):
                break

            # Fill companion fields visible on the current step
            for fname, val in test_data.items():
                if not fname or fname.startswith("_") or fname in already_filled or val is None:
                    continue
                if await self._is_field_visible(page, fname):
                    ok = await self._fill_one(page, fname, val, {})
                    if ok:
                        already_filled.add(fname)

            # Click Next / Continue
            advanced = False
            for sel in self._NEXT_SELECTORS:
                try:
                    el = await page.query_selector(sel)
                    if not el or not await el.is_visible():
                        continue

                    # Snapshot visible inputs BEFORE click to detect change
                    pre_ids = await page.evaluate("""
                        () => Array.from(
                            document.querySelectorAll('input:not([type=hidden]),select,textarea')
                        ).filter(e => e.getBoundingClientRect().width > 0)
                         .map(e => e.id || e.name || e.type)
                    """)

                    await el.scroll_into_view_if_needed()
                    await asyncio.sleep(0.15)
                    await el.click(timeout=ACTION_TIMEOUT)

                    # Wait for the visible-input fingerprint to change
                    try:
                        pre_str = json.dumps(sorted(pre_ids))
                        await page.wait_for_function(
                            f"""
                            () => {{
                                const pre = {pre_str};
                                const cur = Array.from(
                                    document.querySelectorAll('input:not([type=hidden]),select,textarea')
                                ).filter(e => e.getBoundingClientRect().width > 0)
                                 .map(e => e.id || e.name || e.type);
                                cur.sort();
                                return JSON.stringify(cur) !== JSON.stringify(pre);
                            }}
                            """,
                            timeout=3500,
                        )
                    except Exception:
                        await asyncio.sleep(1.2)   # graceful fallback

                    advanced = True
                    break
                except Exception:
                    continue

            if not advanced:
                break   # No Next button / wizard stuck

    # ── Submit ─────────────────────────────────────────────────────────────

    async def _click_submit(self, page) -> str:
        """
        Find and click the FINAL submit button.

        Returns:
            ``"clicked"``    – a button was found and successfully clicked
            ``"disabled"``   – a button was found but is disabled (form prevents submit)
            ``"not_found"``  – no submit button exists on the page

        'Next' and 'Continue' are intentionally absent — those are wizard
        navigation buttons handled by ``_advance_wizard_to_field``.
        """
        submit_selectors = [
            "button[type='submit']",
            "input[type='submit']",
            "button[type='button']:has-text('Submit')",
            "button:has-text('Submit')",
            "button:has-text('Save')",
            "button:has-text('Register')",
            "button:has-text('Sign Up')",
            "button:has-text('Login')",
            "button:has-text('Sign In')",
            "button:has-text('Send')",
            "button:has-text('Confirm')",
            "button:has-text('Place Order')",
            "button:has-text('Finish')",
            "button:has-text('Done')",
            "[data-testid*='submit']",
        ]
        found_disabled = False
        for selector in submit_selectors:
            try:
                el = await page.query_selector(selector)
                if not el or not await el.is_visible():
                    continue
                # Check enabled state before attempting click
                if not await el.is_enabled():
                    found_disabled = True
                    logger.debug(f"Submit button found but disabled: {selector}")
                    continue
                await el.click(timeout=ACTION_TIMEOUT)
                return "clicked"
            except Exception:
                continue
        return "disabled" if found_disabled else "not_found"

