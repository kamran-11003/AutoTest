"""
Run RL-based adaptive test execution on all 6 real-world websites.

Usage:
    python scripts/run_rl_6sites.py

Outputs:
    data/rl_run_results/rl_stats.txt        — machine-friendly stats summary
    data/rl_run_results/crawl_report.md     — human-readable paper-ready report
    data/test_results/<crawl_id>.*          — per-website HTML/JSON reports
    data/rl_performance/rl_performance.csv  — cumulative performance log

Handles API quota gracefully:
    If Gemini quota is exhausted mid-run the runner automatically falls back to
    heuristic-only for the remainder and records stop_reason = "budget_exhausted".
    The script saves partial results so you can re-run later to collect the rest.

RL Goals Active (all 3 fixed this session):
    Goal 1 – Adaptive early stopping   (threshold driven by historical pass rate)
    Goal 2 – Persisted risk scores      (loaded from data/rl_optimizations/)
    Goal 3 – Pattern learning oracle    (subtype stats override DQN action)
"""

import sys
import asyncio
import json
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# ── Config ────────────────────────────────────────────────────────────────────
# Tune these to match your daily Gemini quota.
# The runner hard-stops on budget_exhausted and saves partial results.
API_BUDGET   = 40          # max LLM calls per website run
TIME_LIMIT_S = 300         # 5-minute per-site wall-clock cap
HEADLESS     = True

AFTER_TEST_FILES = sorted((ROOT / "data" / "generated_tests").glob("*_after_*.json"))

# Map test file → friendly site name
def _site_name(path: Path) -> str:
    stem = path.stem
    # strip _after_<timestamp> suffix
    for sep in ("_after_",):
        idx = stem.find(sep)
        if idx != -1:
            stem = stem[:idx]
    return stem

OUTPUT_DIR = ROOT / "data" / "rl_run_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── Run one suite ─────────────────────────────────────────────────────────────

async def run_suite(test_file: Path, crawl_id: str) -> dict:
    """Load a test suite and execute it with AdaptiveRunner. Returns summary dict."""
    from execution.adaptive_runner import AdaptiveRunner

    print(f"\n{'='*60}")
    print(f"  Testing: {crawl_id}")
    print(f"  File   : {test_file.name}")
    print(f"  Budget : {API_BUDGET} LLM calls  |  Time: {TIME_LIMIT_S}s")
    print(f"{'='*60}")

    with open(test_file, "r", encoding="utf-8") as fh:
        raw = json.load(fh)

    # The after-test files wrap the actual test_cases under test_results.
    # _flatten_and_sort expects a dict that contains a "test_cases" key.
    suite = raw.get("test_results", raw)

    runner = AdaptiveRunner(
        api_budget   = API_BUDGET,
        time_limit_s = TIME_LIMIT_S,
        rl_mode      = True,
        headless     = HEADLESS,
    )

    t0 = time.perf_counter()
    try:
        report = await runner.execute(suite, crawl_id=crawl_id)
    except Exception as exc:
        elapsed = round(time.perf_counter() - t0, 1)
        print(f"  [ERROR] Runner crashed: {exc}")
        return {
            "crawl_id"      : crawl_id,
            "status"        : "crash",
            "error"         : str(exc),
            "duration_s"    : elapsed,
            "total"         : 0,
            "passed"        : 0,
            "failed"        : 0,
            "errors"        : 0,
            "skipped"       : 0,
            "pass_rate"     : 0.0,
            "api_calls"     : 0,
            "api_cost"      : 0.0,
            "stop_reason"   : "crash",
            "heur_decisions": 0,
            "llm_decisions" : 0,
            "pattern_overrides": 0,
            "stop_decisions": 0,
            "rl_mode"       : True,
        }

    summary = {
        "crawl_id"         : crawl_id,
        "status"           : "ok",
        "error"            : None,
        "duration_s"       : report.duration_s,
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
        "rl_mode"          : True,
    }

    print(f"  Result : {report.passed}/{report.total} passed "
          f"({report.pass_rate}%)  |  stop={report.stop_reason}")
    print(f"  Oracle : heur={report.heuristic_decisions} llm={report.llm_decisions} "
          f"pattern_overrides={report.pattern_overrides}")
    print(f"  Cost   : {report.api_calls_used} calls  ${report.api_cost:.3f}  "
          f"{report.duration_s:.1f}s")

    return summary


# ── Write rl_stats.txt ────────────────────────────────────────────────────────

def write_stats_txt(results: list, run_ts: str):
    stats_path = OUTPUT_DIR / "rl_stats.txt"
    lines = [
        "=" * 70,
        "  RL ADAPTIVE EXECUTION — STATS SUMMARY",
        f"  Generated : {run_ts}",
        f"  Sites run : {len(results)}",
        "=" * 70,
        "",
        f"{'Site':<45} {'Tests':>6} {'Pass%':>6} {'LLM':>4} {'Ovrd':>5} {'$':>7} {'Stop':>18}",
        "-" * 100,
    ]
    totals = dict(total=0, passed=0, failed=0, errors=0, skipped=0,
                  api_calls=0, api_cost=0.0, heur=0, llm=0, ovrd=0, dur=0.0)

    for r in results:
        site = r["crawl_id"][:44]
        lines.append(
            f"{site:<45} {r['total']:>6} {r['pass_rate']:>5.1f}% "
            f"{r['llm_decisions']:>4} {r['pattern_overrides']:>5} "
            f"${r['api_cost']:>6.3f} {r['stop_reason']:>18}"
        )
        totals["total"]    += r["total"]
        totals["passed"]   += r["passed"]
        totals["failed"]   += r["failed"]
        totals["errors"]   += r["errors"]
        totals["skipped"]  += r["skipped"]
        totals["api_calls"]+= r["api_calls"]
        totals["api_cost"] += r["api_cost"]
        totals["heur"]     += r["heur_decisions"]
        totals["llm"]      += r["llm_decisions"]
        totals["ovrd"]     += r["pattern_overrides"]
        totals["dur"]      += r["duration_s"]

    total_decisions = totals["heur"] + totals["llm"]
    pct_llm   = totals["llm"]  / total_decisions * 100 if total_decisions else 0
    pct_heur  = totals["heur"] / total_decisions * 100 if total_decisions else 0
    pct_ovrd  = totals["ovrd"] / total_decisions * 100 if total_decisions else 0
    overall_pass = totals["passed"] / totals["total"] * 100 if totals["total"] else 0

    lines += [
        "-" * 100,
        "",
        "TOTALS",
        f"  Tests run      : {totals['total']}",
        f"  Passed         : {totals['passed']}  ({overall_pass:.1f}%)",
        f"  Failed         : {totals['failed']}",
        f"  Errors         : {totals['errors']}",
        f"  Skipped(cache) : {totals['skipped']}",
        f"  Total duration : {totals['dur']:.1f}s",
        "",
        "ORACLE DECISIONS",
        f"  Heuristic      : {totals['heur']}  ({pct_heur:.1f}%)",
        f"  LLM            : {totals['llm']}  ({pct_llm:.1f}%)",
        f"  Pattern overrides (Goal 3): {totals['ovrd']}  ({pct_ovrd:.1f}%)",
        "",
        "API COSTS",
        f"  Total calls    : {totals['api_calls']}",
        f"  Total cost     : ${totals['api_cost']:.4f}",
        "",
        "RL GOALS STATUS",
        "  Goal 1 – Adaptive early stopping   : ACTIVE (threshold from pass-rate history)",
        "  Goal 2 – Persisted risk scores      : ACTIVE (loaded from rl_optimizations/)",
        "  Goal 3 – Pattern learning oracle    : ACTIVE (subtype history overrides DQN)",
        "",
        "=" * 70,
    ]

    stats_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n[RL Stats] Written to {stats_path}")
    return totals


# ── Write crawl_report.md ─────────────────────────────────────────────────────

def write_crawl_report_md(results: list, totals: dict, run_ts: str):
    md_path = OUTPUT_DIR / "crawl_report.md"

    total_decisions = totals["heur"] + totals["llm"]
    pct_llm   = totals["llm"]  / total_decisions * 100 if total_decisions else 0
    pct_heur  = totals["heur"] / total_decisions * 100 if total_decisions else 0
    overall_pass = totals["passed"] / totals["total"] * 100 if totals["total"] else 0

    lines = [
        "# RL Adaptive Test Execution — Crawl Report",
        "",
        f"**Generated:** {run_ts}  ",
        f"**Websites tested:** {len(results)}  ",
        f"**RL mode:** Enabled (DQN + Adaptive Early Stopping + Pattern Learning)  ",
        "",
        "## RL Goals Summary",
        "",
        "| Goal | Description | Status |",
        "|------|-------------|--------|",
        "| Goal 1 | **Adaptive Early Stopping** — threshold adapts from historical pass-rate trends | ✅ Active |",
        "| Goal 2 | **Persisted Risk Scores** — optimizer scores loaded back at run start | ✅ Active |",
        "| Goal 3 | **Pattern-Learning Oracle** — subtype history can override DQN action | ✅ Active |",
        "",
        "## Per-Website Results",
        "",
        "| Website | Pages | Tests | Passed | Failed | Errors | Pass% | LLM Calls | Pattern Overrides | Cost | Stop Reason |",
        "|---------|-------|-------|--------|--------|--------|-------|-----------|-------------------|------|-------------|",
    ]

    # Page counts from crawl files (best-effort)
    crawl_pages = {
        "uitestingplayground_com"                       : 22,
        "qa-alchemist_vercel_app"                       : 6,
        "qa-tester-practice-website_vercel_app"         : 9,
        "qa-testing-hu_vercel_app"                      : 3,
        "the-qa-testers-gauntlet_vercel_app"            : 6,
        "www_httpbin_org_forms_post"                    : 2,
    }

    for r in results:
        cid = r["crawl_id"]
        pages = next((v for k, v in crawl_pages.items() if k in cid), "?")
        status_icon = "✅" if r["status"] == "ok" else "❌"
        lines.append(
            f"| {status_icon} `{cid}` "
            f"| {pages} "
            f"| {r['total']} "
            f"| {r['passed']} "
            f"| {r['failed']} "
            f"| {r['errors']} "
            f"| {r['pass_rate']:.1f}% "
            f"| {r['llm_decisions']} "
            f"| {r['pattern_overrides']} "
            f"| ${r['api_cost']:.3f} "
            f"| `{r['stop_reason']}` |"
        )

    lines += [
        "",
        "## Aggregate Statistics",
        "",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total tests executed | {totals['total']} |",
        f"| Overall pass rate | {overall_pass:.1f}% |",
        f"| Tests passed | {totals['passed']} |",
        f"| Tests failed | {totals['failed']} |",
        f"| Tests errored | {totals['errors']} |",
        f"| Tests skipped (cache) | {totals['skipped']} |",
        f"| Total execution time | {totals['dur']:.1f}s |",
        f"| Heuristic oracle decisions | {totals['heur']} ({pct_heur:.1f}%) |",
        f"| LLM oracle decisions | {totals['llm']} ({pct_llm:.1f}%) |",
        f"| Pattern-learning overrides | {totals['ovrd']} |",
        f"| Total API calls | {totals['api_calls']} |",
        f"| Total API cost | ${totals['api_cost']:.4f} |",
        "",
        "## Oracle Decision Distribution",
        "",
        "```",
        f"  Heuristic  : {'█' * max(1, int(pct_heur / 2))} {pct_heur:.1f}%",
        f"  LLM        : {'█' * max(1, int(pct_llm  / 2))} {pct_llm:.1f}%",
        "```",
        "",
        "## Research Question Mapping",
        "",
        "| RQ | Question | Evidence |",
        "|----|----------|----------|",
        "| RQ1 | Effectiveness: Does RL oracle selection maintain/improve validation quality? | Pass rates above + oracle breakdown |",
        "| RQ2 | Efficiency: How much API cost/time does RL save vs LLM-only? | LLM % column + cost column above |",
        "| RQ3 | Prioritization: Do risk-scored test classes improve early fault discovery? | See RQ3.md for before/after |",
        "| RQ4 | Generalization: Does policy transfer to unseen websites? | 4 additional sites (planned) |",
        "| RQ5 | Component Impact: Which component contributes most? | Pattern overrides column |",
        "",
        "## Notes",
        "",
        "- Tests sourced from AI-refined (`_after_`) test suites generated by Gemini.",
        "- RL agent checkpoint: `data/rl_model/dqn_checkpoint.pth`",
        "- Heuristic stats: `data/heuristics_logs/heuristics_analysis.txt`",
        "- Score updates: `data/rl_optimizations/score_updates.jsonl`",
        "- Performance log: `data/rl_performance/rl_performance.csv`",
        "",
        "---",
        "*Generated by `scripts/run_rl_6sites.py`*",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[Crawl Report] Written to {md_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    if not AFTER_TEST_FILES:
        print("No *_after_*.json files found in data/generated_tests/. "
              "Run scripts/regenerate_refine_rq3.py first.")
        sys.exit(1)

    run_ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results  = []
    api_limit_hit = False

    for tf in sorted(AFTER_TEST_FILES):
        cid = _site_name(tf)

        if api_limit_hit:
            print(f"\n[SKIP] {cid} — API quota exhausted in a previous site run.")
            results.append({
                "crawl_id": cid, "status": "skipped_quota",
                "error": "API quota exhausted in earlier run", "duration_s": 0,
                "total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0,
                "pass_rate": 0.0, "api_calls": 0, "api_cost": 0.0,
                "stop_reason": "skipped_quota", "heur_decisions": 0,
                "llm_decisions": 0, "pattern_overrides": 0, "stop_decisions": 0,
                "rl_mode": True,
            })
            continue

        r = await run_suite(tf, cid)
        results.append(r)

        # If budget was fully exhausted, assume quota is gone for all remaining sites
        if r["stop_reason"] == "budget_exhausted" and r["api_calls"] >= API_BUDGET:
            print("\n[WARNING] API budget fully used — remaining sites will run "
                  "heuristic-only or be skipped.")
            # Don't set api_limit_hit here — let the runner handle it gracefully
            # per-site with heuristic fallback.  Only skip if a hard crash occurs.

        if r["status"] == "crash" and "quota" in str(r.get("error", "")).lower():
            api_limit_hit = True

    totals = write_stats_txt(results, run_ts)
    write_crawl_report_md(results, totals, run_ts)

    print("\n" + "=" * 60)
    print("  ALL RUNS COMPLETE")
    print(f"  Stats  : {OUTPUT_DIR / 'rl_stats.txt'}")
    print(f"  Report : {OUTPUT_DIR / 'crawl_report.md'}")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
