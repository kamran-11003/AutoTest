"""
Execute test suites for site6, site7, site8 (new framework sites).

Usage:
    python scripts/execute_sites.py --site all        # run all 3 new sites
    python scripts/execute_sites.py --site 6          # run site6 only
    python scripts/execute_sites.py --site 7          # run site7 only
    python scripts/execute_sites.py --site 8          # run site8 only
    python scripts/execute_sites.py --no-llm          # force heuristic-only

Behaviour:
    - Pre-flight Gemini quota check for all 12 keys.
    - If 0 working keys  → NullOracle (heuristic-only) + api_budget=99999.
    - If live keys found → StrictLLMOracle; on quota failure during execution
      → stop immediately, delete partial report, mark site as failed.
    - On completion writes:
        data/execution_results_<ts>.txt  — per-site summary TXT
        data/temp_paper_results.json     — execution columns filled
"""

import sys
import asyncio
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from execution.adaptive_runner import AdaptiveRunner
from execution.llm_oracle import LLMOracle
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# ── Config ─────────────────────────────────────────────────────────────────
API_BUDGET   = 30          # max LLM calls per site (only used when keys available)
TIME_LIMIT_S = 1800        # 30-minute per-site wall-clock cap
HEADLESS     = True

GEN_DIR      = ROOT / "data" / "generated_tests"
RESULTS_DIR  = ROOT / "data" / "test_results"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

SITE_MAP = {
    "6": "site6_ecommerce",
    "7": "site7_spa_taskboard",
    "8": "site8_medical",
}

PAPER_RESULTS_FILE = ROOT / "data" / "temp_paper_results.json"


# ── Custom Oracle Classes ────────────────────────────────────────────────────

class LLMQuotaError(RuntimeError):
    """Raised when a live LLM call hits quota during execution."""
    pass


class NullOracle(LLMOracle):
    """Returns 'unclear' instantly without any API call.
    After 3 consecutive 'unclear' returns, AdaptiveRunner sets
    _llm_all_exhausted=True and switches to pure heuristics."""

    def __init__(self):
        self.rotator = None
        self.api_calls_made = 0

    async def evaluate(self, page, test_case, screenshot_path=None):
        return {
            "outcome":    "unclear",
            "confidence": 0,
            "evidence":   "LLM disabled — heuristic-only mode",
        }


class StrictLLMOracle(LLMOracle):
    """Wraps LLMOracle; raises LLMQuotaError instead of returning 'unclear'
    on quota/key exhaustion so the caller can stop+clean immediately."""

    async def evaluate(self, page, test_case, screenshot_path=None):
        result = await super().evaluate(page, test_case, screenshot_path)
        evidence = result.get("evidence", "")
        if result.get("outcome") == "unclear" and (
            "quota" in evidence.lower()
            or "exhausted" in evidence.lower()
            or "no gemini api keys" in evidence.lower()
            or "429" in evidence
        ):
            raise LLMQuotaError(f"Gemini quota exhausted during execution: {evidence}")
        return result


# ── Quota Pre-flight ─────────────────────────────────────────────────────────

def check_api_quota() -> int:
    """Test all Gemini keys; return count of working ones."""
    try:
        from crawler.gemini_key_rotator import GeminiKeyRotator
        import google.generativeai as genai

        rotator = GeminiKeyRotator()
        keys = rotator.api_keys if hasattr(rotator, "api_keys") else []
        if not keys:
            # Try to read keys directly
            from config.gemini_keys import GEMINI_API_KEYS
            keys = GEMINI_API_KEYS
    except Exception:
        keys = []

    if not keys:
        print("  [quota] No API keys found — heuristic-only mode")
        return 0

    working = 0
    for key in keys:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            model.generate_content("ping", generation_config={"max_output_tokens": 1})
            working += 1
        except Exception as e:
            err = str(e).lower()
            if "quota" in err or "429" in err or "exhausted" in err:
                pass  # quota hit
            # expired / invalid key also counts as 0
    return working


# ── Helpers ──────────────────────────────────────────────────────────────────

def find_after_file(site_id: str) -> Path:
    """Find the latest *_after_*.json for this site_id."""
    candidates = sorted(GEN_DIR.glob(f"{site_id}_after_*.json"))
    if not candidates:
        raise FileNotFoundError(f"No after-file found for {site_id} in {GEN_DIR}")
    return candidates[-1]


def clean_partial_reports(site_id: str):
    """Delete incomplete report files left behind on failure."""
    deleted = []
    for pattern in [f"report_{site_id}_*.html", f"report_{site_id}_*.json"]:
        for f in RESULTS_DIR.glob(pattern):
            f.unlink(missing_ok=True)
            deleted.append(f.name)
    tmp_ss = ROOT / "data" / "test_results" / "_tmp_screenshot.png"
    if tmp_ss.exists():
        tmp_ss.unlink(missing_ok=True)
        deleted.append(tmp_ss.name)
    if deleted:
        print(f"  [clean] Removed partial files: {deleted}")


def update_paper_results(site_id: str, summary: dict):
    """Write execution columns back into temp_paper_results.json."""
    if not PAPER_RESULTS_FILE.exists():
        return
    try:
        data = json.loads(PAPER_RESULTS_FILE.read_text(encoding="utf-8"))
        # Support both schemas:
        # 1) {"site_id": {...}, ...}
        # 2) {"sites": {"site_id": {...}}, ...}
        if isinstance(data.get("sites"), dict):
            entries = data["sites"]
        else:
            entries = data

        target_entry = None
        for key, entry in entries.items():
            if isinstance(entry, dict) and (entry.get("site_id") == site_id or key == site_id):
                target_entry = entry
                break

        if target_entry is None:
            print(f"  [paper] Warning: no matching entry found for {site_id}")
            return

        target_entry["pass_rate"] = summary.get("pass_rate", 0)
        target_entry["passed"] = summary.get("passed", 0)
        target_entry["failed"] = summary.get("failed", 0)
        target_entry["errors"] = summary.get("errors", 0)
        target_entry["api_calls"] = summary.get("api_calls", 0)
        target_entry["api_cost"] = summary.get("api_cost", 0.0)
        target_entry["duration_s"] = summary.get("duration_s", 0)
        target_entry["stop_reason"] = summary.get("stop_reason", "")
        target_entry["heur_decisions"] = summary.get("heur_decisions", 0)
        target_entry["llm_decisions"] = summary.get("llm_decisions", 0)
        target_entry["execution_status"] = summary.get("status", "ok")
        target_entry["executed_at"] = datetime.now().isoformat()

        if isinstance(data, dict):
            data["updated_at"] = datetime.now().isoformat()

        PAPER_RESULTS_FILE.write_text(
            json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"  [paper] Updated temp_paper_results.json for {site_id}")
    except Exception as e:
        print(f"  [paper] Warning: could not update paper results: {e}")


def save_execution_txt(results: list, ts: str):
    """Save all-sites execution summary to a detailed TXT file."""
    txt_path = ROOT / "data" / f"execution_results_{ts}.txt"
    lines = [
        "=" * 70,
        "  EXECUTION RESULTS — SITE6 / SITE7 / SITE8",
        f"  Generated : {datetime.now().isoformat()}",
        f"  Sites run : {len(results)}",
        "=" * 70,
        "",
    ]

    for r in results:
        sid = r["site_id"]
        lines += [
            f"Site: {sid}",
            f"  After-file : {r.get('after_file', 'N/A')}",
            f"  Status     : {r['status']}",
        ]
        if r["status"] == "ok":
            lines += [
                f"  Tests run  : {r['total']}",
                f"  Passed     : {r['passed']}  ({r['pass_rate']:.1f}%)",
                f"  Failed     : {r['failed']}",
                f"  Errors     : {r['errors']}",
                f"  Skipped    : {r['skipped']}",
                f"  Duration   : {r['duration_s']:.1f}s",
                f"  Stop reason: {r['stop_reason']}",
                f"  Oracle     : heur={r['heur_decisions']}  llm={r['llm_decisions']}",
                f"  API calls  : {r['api_calls']}  (${r['api_cost']:.4f})",
            ]
        else:
            lines.append(f"  Error      : {r.get('error', 'unknown')}")
        lines.append("")

    # Totals for ok runs
    ok = [r for r in results if r["status"] == "ok"]
    if ok:
        total_t  = sum(r["total"]   for r in ok)
        total_p  = sum(r["passed"]  for r in ok)
        total_f  = sum(r["failed"]  for r in ok)
        total_e  = sum(r["errors"]  for r in ok)
        total_dur= sum(r["duration_s"] for r in ok)
        overall  = total_p / total_t * 100 if total_t else 0
        lines += [
            "-" * 70,
            "AGGREGATE (ok runs only)",
            f"  Total tests: {total_t}",
            f"  Passed     : {total_p}  ({overall:.1f}%)",
            f"  Failed     : {total_f}",
            f"  Errors     : {total_e}",
            f"  Duration   : {total_dur:.1f}s",
        ]

    txt_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[saved] Execution TXT: {txt_path}")
    return txt_path


# ── Execute one site ─────────────────────────────────────────────────────────

async def execute_site(site_id: str, use_null_oracle: bool, api_budget: int) -> dict:
    """Run adaptive test execution for one site. Returns summary dict."""
    from execution.reporter import Reporter

    base = {
        "site_id": site_id, "status": "ok", "error": None, "after_file": "",
        "duration_s": 0, "total": 0, "passed": 0, "failed": 0,
        "errors": 0, "skipped": 0, "pass_rate": 0.0,
        "api_calls": 0, "api_cost": 0.0, "stop_reason": "",
        "heur_decisions": 0, "llm_decisions": 0,
        "pattern_overrides": 0, "stop_decisions": 0,
    }

    print(f"\n{'='*60}")
    print(f"  Site: {site_id}")
    mode = "heuristic-only (NullOracle)" if use_null_oracle else f"LLM+heuristic (budget={api_budget})"
    print(f"  Mode: {mode}")

    # Find after-file
    try:
        after_file = find_after_file(site_id)
    except FileNotFoundError as e:
        print(f"  [ERROR] {e}")
        return {**base, "status": "error", "error": str(e)}

    base["after_file"] = after_file.name
    print(f"  File: {after_file.name}")
    print(f"{'='*60}")

    # Load test suite
    raw = json.loads(after_file.read_text(encoding="utf-8"))
    test_suite = raw.get("test_results", raw)   # runner needs {"test_cases": {...}}

    # Build runner
    effective_budget = 99999 if use_null_oracle else api_budget
    runner = AdaptiveRunner(
        api_budget   = effective_budget,
        time_limit_s = TIME_LIMIT_S,
        rl_mode      = True,
        headless     = HEADLESS,
    )
    if use_null_oracle:
        runner.llm = NullOracle()
    else:
        runner.llm = StrictLLMOracle()

    t0 = time.perf_counter()
    try:
        report = await runner.execute(test_suite, crawl_id=site_id)
    except LLMQuotaError as exc:
        elapsed = round(time.perf_counter() - t0, 1)
        print(f"  [QUOTA FAILURE] LLM call failed after {elapsed}s: {exc}")
        clean_partial_reports(site_id)
        return {**base, "status": "llm_quota_failure", "error": str(exc),
                "duration_s": elapsed}
    except Exception as exc:
        elapsed = round(time.perf_counter() - t0, 1)
        print(f"  [ERROR] Runner crashed after {elapsed}s: {exc}")
        clean_partial_reports(site_id)
        return {**base, "status": "crash", "error": str(exc),
                "duration_s": elapsed}

    # Write report
    try:
        reporter = Reporter()
        html_path = reporter.write(report, crawl_id=site_id)
        print(f"  [report] Saved: {html_path}")
    except Exception as e:
        print(f"  [report] Warning — could not write HTML report: {e}")

    summary = {
        "site_id"          : site_id,
        "status"           : "ok",
        "error"            : None,
        "after_file"       : after_file.name,
        "duration_s"       : round(report.duration_s, 1),
        "total"            : report.total,
        "passed"           : report.passed,
        "failed"           : report.failed,
        "errors"           : report.errors,
        "skipped"          : report.skipped,
        "pass_rate"        : report.pass_rate,
        "api_calls"        : report.api_calls_used,
        "api_cost"         : round(report.api_cost, 4),
        "stop_reason"      : report.stop_reason,
        "heur_decisions"   : report.heuristic_decisions,
        "llm_decisions"    : report.llm_decisions,
        "pattern_overrides": report.pattern_overrides,
        "stop_decisions"   : report.stop_decisions,
    }

    print(f"  Result : {report.passed}/{report.total} passed ({report.pass_rate}%)")
    print(f"  Oracle : heur={report.heuristic_decisions} llm={report.llm_decisions}")
    print(f"  Stop   : {report.stop_reason}  |  Duration: {report.duration_s:.1f}s")

    update_paper_results(site_id, summary)
    return summary


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(description="Execute tests for site6/7/8")
    parser.add_argument(
        "--site", default="all",
        help="Which site(s) to run: 6, 7, 8, or all (default: all)"
    )
    parser.add_argument(
        "--no-llm", action="store_true",
        help="Force heuristic-only mode (skip LLM pre-flight)"
    )
    args = parser.parse_args()

    # Determine which sites to run
    if args.site == "all":
        sites = list(SITE_MAP.values())
    elif args.site in SITE_MAP:
        sites = [SITE_MAP[args.site]]
    else:
        # Accept full site_id too (e.g. "site6_ecommerce")
        if args.site in SITE_MAP.values():
            sites = [args.site]
        else:
            print(f"[ERROR] Unknown site '{args.site}'. Use 6, 7, 8, or 'all'.")
            sys.exit(1)

    # Pre-flight quota check
    use_null_oracle = args.no_llm
    if not use_null_oracle:
        print("\n[pre-flight] Checking Gemini API quota ...")
        try:
            working = check_api_quota()
            print(f"[pre-flight] Working keys: {working}/12")
        except Exception as e:
            print(f"[pre-flight] Quota check error: {e} — defaulting to heuristic-only")
            working = 0

        if working == 0:
            print("[pre-flight] No working API keys — switching to heuristic-only mode")
            use_null_oracle = True
        else:
            print(f"[pre-flight] {working} key(s) available — LLM mode enabled")

    # Run each site sequentially
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    all_results = []

    for site_id in sites:
        result = await execute_site(
            site_id        = site_id,
            use_null_oracle= use_null_oracle,
            api_budget     = API_BUDGET,
        )
        all_results.append(result)

    # Save consolidated TXT
    save_execution_txt(all_results, ts)

    # Print final summary
    print("\n" + "=" * 60)
    print("EXECUTION COMPLETE")
    print("=" * 60)
    for r in all_results:
        if r["status"] == "ok":
            print(f"  {r['site_id']:<35} {r['passed']:>4}/{r['total']:<4} "
                  f"({r['pass_rate']:5.1f}%)  {r['stop_reason']}")
        else:
            print(f"  {r['site_id']:<35} FAILED: {r['status']} — {r['error']}")


if __name__ == "__main__":
    asyncio.run(main())
