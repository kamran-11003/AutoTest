"""
generate_refine.py  —  Run ONLY Step 2 (generate) + Step 3 (AI refine)
=======================================================================
Uses the existing crawl JSON files from a previous crawl_verify run.
Skips re-crawling and execution (no browser needed).

Usage
-----
    python scripts/generate_refine.py --site 5   # site6_ecommerce
    python scripts/generate_refine.py --site 6   # site7_spa_taskboard
    python scripts/generate_refine.py --site 7   # site8_medical
    python scripts/generate_refine.py --site all # all three new sites

Results are written to:
    data/generated_tests/<site_id>_before_<ts>.json   ← raw tests
    data/generated_tests/<site_id>_after_<ts>.json    ← AI-refined tests
    data/temp_paper_results.json                       ← partial paper summary
"""

import sys
import json
import copy
import argparse
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# ── Site definitions (must match run_test_websites.py SITES list) ─────────────

BASE_URL = "http://localhost:5500/test_websites"

SITES = [
    {"id": "site1_contact",      "name": "Contact Form",               "url": f"{BASE_URL}/site1_contact/index.html"},
    {"id": "site2_booking",      "name": "Hotel Booking",              "url": f"{BASE_URL}/site2_booking/index.html"},
    {"id": "site3_register",     "name": "User Registration",          "url": f"{BASE_URL}/site3_register/index.html"},
    {"id": "site4_search",       "name": "Product Search",             "url": f"{BASE_URL}/site4_search/index.html"},
    {"id": "site5_feedback",     "name": "Feedback Survey",            "url": f"{BASE_URL}/site5_feedback/index.html"},
    {"id": "site6_ecommerce",    "name": "E-Commerce (Next.js SSR)",   "url": "http://localhost:3006"},
    {"id": "site7_spa_taskboard","name": "Task Board (React SPA)",     "url": "http://localhost:3007"},
    {"id": "site8_medical",      "name": "Medical Clinic (Express+EJS)","url": "http://localhost:3008"},
]

TEMP_PAPER_RESULTS = ROOT / "data" / "temp_paper_results.json"

# ── ANSI colours ──────────────────────────────────────────────────────────────
GREEN  = "\033[92m"; YELLOW = "\033[93m"; RED = "\033[91m"
CYAN   = "\033[96m"; BOLD   = "\033[1m";  RESET = "\033[0m"

def ok(t):   return f"  {GREEN}✔  {t}{RESET}"
def warn(t): return f"  {YELLOW}⚠  {t}{RESET}"
def err(t):  return f"  {RED}✘  {t}{RESET}"
def info(t): return f"  {CYAN}ℹ  {t}{RESET}"
def hdr(t):
    return f"\n{BOLD}{CYAN}{'═'*70}{RESET}\n{BOLD}{CYAN}  {t}{RESET}\n{BOLD}{CYAN}{'═'*70}{RESET}"


# ── Locate the latest crawl file for a site ───────────────────────────────────

def find_crawl_file(site_id: str) -> Path | None:
    crawl_dir = ROOT / "data" / "crawled_graphs"
    # prefer _verify_ files (from crawl_verify.py), fall back to regular files
    candidates = sorted(
        list(crawl_dir.glob(f"{site_id}_verify_*.json")) +
        list(crawl_dir.glob(f"{site_id}_*.json")),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


# ── Step 2: Generate ──────────────────────────────────────────────────────────

def step_generate(site: dict, crawl_file: str) -> tuple[dict | None, str | None]:
    from test_generator.test_orchestrator import TestOrchestrator

    print(info(f"Generating tests from: {Path(crawl_file).name}"))
    out_dir = ROOT / "data" / "generated_tests"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        orchestrator = TestOrchestrator()
        test_results = orchestrator.generate_all_tests(crawl_file)
        tc = test_results.get("test_cases", {})
        counts  = {k: len(v) for k, v in tc.items()}
        total   = sum(counts.values())

        before_payload = {
            "stage":        "before_refinement",
            "generated_at": datetime.now().isoformat(),
            "crawl_file":   crawl_file,
            "crawl_url":    site["url"],
            "site_id":      site["id"],
            "test_results": test_results,
            "counts":       counts,
            "total":        total,
        }
        before_file = out_dir / f"{site['id']}_before_{ts}.json"
        before_file.write_text(
            json.dumps(before_payload, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        _update_test_index(out_dir, site["id"], before_file.name, ts, total)

        print(ok(
            f"Generated {total} tests  "
            f"(BVA={counts.get('bva',0)} ECP={counts.get('ecp',0)} "
            f"DT={counts.get('decision_table',0)} ST={counts.get('state_transition',0)} "
            f"UC={counts.get('use_case',0)})"
        ))
        print(ok(f"Saved → {before_file.relative_to(ROOT)}"))
        return test_results, str(before_file)

    except Exception as exc:
        print(err(f"Generate failed: {exc}"))
        logger.exception(f"Generate failed for {site['id']}")
        return None, None


# ── Step 3: AI Refine ─────────────────────────────────────────────────────────

def step_refine(site: dict, test_results: dict, crawl_data: dict | None,
                before_file: str) -> tuple[dict, str]:
    from test_generator.ai_refiner import GeminiTestRefiner

    print(info("Running AI refinement (Gemini) …"))
    out_dir = ROOT / "data" / "generated_tests"
    ts      = datetime.now().strftime("%Y%m%d_%H%M%S")

    refiner = GeminiTestRefiner()
    tc      = test_results.get("test_cases", {})

    if refiner.model is not None and crawl_data is not None:
        try:
            refined_tc    = refiner.refine_tests(tc, crawl_data)
            refine_status = "refined"
        except Exception as exc:
            logger.warning(f"AI refinement failed ({exc}), using raw tests")
            refined_tc    = tc
            refine_status = f"failed: {exc}"
    else:
        refined_tc    = tc
        refine_status = "skipped_no_api_key" if refiner.model is None else "skipped_no_crawl"

    after_results = copy.deepcopy(test_results)
    after_results["test_cases"] = refined_tc
    counts = {k: len(v) for k, v in refined_tc.items()}
    total  = sum(counts.values())
    after_results["summary"] = {
        "total_test_cases":       total,
        "bva_count":              counts.get("bva", 0),
        "ecp_count":              counts.get("ecp", 0),
        "decision_table_count":   counts.get("decision_table", 0),
        "state_transition_count": counts.get("state_transition", 0),
        "use_case_count":         counts.get("use_case", 0),
    }

    ai_enhanced = sum(
        1 for tests in refined_tc.values() if isinstance(tests, list)
        for t in tests if isinstance(t, dict) and t.get("ai_enhanced") is True
    )

    after_payload = {
        "stage":              "after_refinement",
        "generated_at":       datetime.now().isoformat(),
        "crawl_url":          site["url"],
        "site_id":            site["id"],
        "refinement_status":  refine_status,
        "test_results":       after_results,
        "counts":             counts,
        "total":              total,
        "ai_enhanced_count":  ai_enhanced,
        "before_file":        Path(before_file).name,
    }
    after_file = out_dir / f"{site['id']}_after_{ts}.json"
    after_file.write_text(
        json.dumps(after_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    _update_test_index(out_dir, site["id"], after_file.name, ts, total,
                        ai_refined=(refine_status == "refined"))

    status_str = f"{GREEN}refined{RESET}" if refine_status == "refined" else f"{YELLOW}{refine_status}{RESET}"
    print(ok(f"Refinement: {status_str}  AI-enhanced: {ai_enhanced}/{total}"))
    print(ok(f"Saved → {after_file.relative_to(ROOT)}"))
    return after_results, str(after_file)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _update_test_index(out_dir: Path, site_id: str, filename: str, ts: str,
                        total: int, ai_refined: bool = False):
    index_file = out_dir / "test_index.json"
    if index_file.exists():
        try:
            index = json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            index = {}
    else:
        index = {}
    h = site_id
    index[h] = {
        "site_id":     site_id,
        "filename":    filename,
        "timestamp":   ts,
        "total":       total,
        "version":     index.get(h, {}).get("version", 0) + 1,
        "ai_refined":  ai_refined,
        "last_updated":datetime.now().isoformat(),
    }
    index_file.write_text(json.dumps(index, indent=2), encoding="utf-8")


# ── Temp paper results ────────────────────────────────────────────────────────

def load_paper_results() -> dict:
    """Load existing temp paper results or create fresh structure."""
    if TEMP_PAPER_RESULTS.exists():
        try:
            return json.loads(TEMP_PAPER_RESULTS.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "description": "Partial pipeline results for paper update. Add execution results separately.",
        "generated_at": datetime.now().isoformat(),
        "sites": {},
    }


def save_paper_result(site: dict, crawl_file: Path, before_file: str,
                      after_file: str, after_results: dict,
                      refine_status: str) -> None:
    """Append/update this site's data in temp_paper_results.json."""
    paper = load_paper_results()

    counts    = after_results.get("summary", {})
    total     = counts.get("total_test_cases", 0)
    ai_enh    = sum(
        1 for tests in after_results.get("test_cases", {}).values()
        if isinstance(tests, list)
        for t in tests if isinstance(t, dict) and t.get("ai_enhanced") is True
    )

    # Read crawl meta so the paper knows pages/forms
    crawl_data = json.loads(crawl_file.read_text(encoding="utf-8"))
    pages  = len(crawl_data.get("nodes", []))
    forms  = sum(len(n.get("forms", [])) for n in crawl_data.get("nodes", []))
    fields = sum(
        len(f.get("inputs") or f.get("fields", []))
        for n in crawl_data.get("nodes", [])
        for f in n.get("forms", [])
    )

    paper["sites"][site["id"]] = {
        "site_id":          site["id"],
        "site_name":        site["name"],
        "url":              site["url"],
        "framework":        _detect_framework(site["id"]),
        "crawl_file":       crawl_file.name,
        "pages_crawled":    pages,
        "forms_detected":   forms,
        "fields_detected":  fields,
        "total_tests":      total,
        "bva":              counts.get("bva_count", 0),
        "ecp":              counts.get("ecp_count", 0),
        "decision_table":   counts.get("decision_table_count", 0),
        "state_transition": counts.get("state_transition_count", 0),
        "use_case":         counts.get("use_case_count", 0),
        "ai_enhanced":      ai_enh,
        "refinement_status":refine_status,
        "before_file":      Path(before_file).name,
        "after_file":       Path(after_file).name,
        "generated_at":     datetime.now().isoformat(),
        # execution columns — filled in later when execution runs
        "pass_rate":        None,
        "passed":           None,
        "failed":           None,
        "api_calls":        None,
        "api_cost":         None,
        "duration_s":       None,
    }
    paper["updated_at"] = datetime.now().isoformat()
    TEMP_PAPER_RESULTS.parent.mkdir(parents=True, exist_ok=True)
    TEMP_PAPER_RESULTS.write_text(json.dumps(paper, indent=2, ensure_ascii=False), encoding="utf-8")
    print(ok(f"Paper temp data saved → {TEMP_PAPER_RESULTS.relative_to(ROOT)}"))


def _detect_framework(site_id: str) -> str:
    mapping = {
        "site1_contact":       "Plain HTML",
        "site2_booking":       "Plain HTML",
        "site3_register":      "Plain HTML",
        "site4_search":        "Plain HTML",
        "site5_feedback":      "Plain HTML",
        "site6_ecommerce":     "Next.js 14 (SSR)",
        "site7_spa_taskboard": "React 18 + Vite 5 (SPA)",
        "site8_medical":       "Express 4 + EJS (SSR)",
    }
    return mapping.get(site_id, "Unknown")


# ── Main pipeline (generate + refine only) ────────────────────────────────────

def process_site(site_idx: int) -> dict | None:
    site = SITES[site_idx]
    print(hdr(f"GENERATE + REFINE: {site['name']}"))
    print(info(f"Site ID : {site['id']}"))
    print(info(f"URL     : {site['url']}"))

    # Find crawl file
    crawl_path = find_crawl_file(site["id"])
    if crawl_path is None:
        print(err(f"No crawl file found for {site['id']} — run crawl_verify.py first"))
        return None
    print(ok(f"Crawl file: {crawl_path.name}  ({crawl_path.stat().st_size // 1024} KB)"))

    # Load crawl data (needed for AI refiner context)
    crawl_data = json.loads(crawl_path.read_text(encoding="utf-8"))

    # Step 2 — Generate
    test_results, before_file = step_generate(site, str(crawl_path))
    if test_results is None:
        return None

    # Step 3 — Refine
    after_results, after_file = step_refine(site, test_results, crawl_data, before_file)

    # Extract refinement status from the after_file payload
    after_payload = json.loads(Path(after_file).read_text(encoding="utf-8"))
    refine_status = after_payload.get("refinement_status", "unknown")

    # Save paper-ready summary
    save_paper_result(site, crawl_path, before_file, after_file, after_results, refine_status)

    return {
        "site_id":         site["id"],
        "site_name":       site["name"],
        "crawl_file":      crawl_path.name,
        "total_tests":     after_results.get("summary", {}).get("total_test_cases", 0),
        "refine_status":   refine_status,
        "after_file":      Path(after_file).name,
    }


def print_final_table(results: list[dict]) -> None:
    print(hdr("GENERATE + REFINE — FINAL TABLE"))
    print(f"  {'Site':<35} {'Tests':>6} {'Refined?':>10}  {'After File'}")
    print(f"  {'─'*35} {'─'*6} {'─'*10}  {'─'*35}")
    for r in results:
        refined = f"{GREEN}yes{RESET}" if r["refine_status"] == "refined" else f"{YELLOW}{r['refine_status']}{RESET}"
        print(f"  {r['site_name']:<35} {r['total_tests']:>6} {refined:>10}  {r['after_file']}")
    print()
    total_tests = sum(r["total_tests"] for r in results)
    print(ok(f"Total tests generated: {total_tests}  across {len(results)} sites"))
    print(info(f"Paper temp results at: data/temp_paper_results.json"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate + AI-refine tests from crawl data")
    parser.add_argument(
        "--site", required=True,
        help="Site index 0-7, or 'all' to process all 8 sites, or 'new' for sites 5-7 only",
    )
    args = parser.parse_args()

    if args.site == "new":
        indices = [5, 6, 7]
    elif args.site == "all":
        indices = list(range(len(SITES)))
    else:
        idx = int(args.site)
        if idx < 0 or idx >= len(SITES):
            print(f"  Site index must be 0-{len(SITES)-1}, got {idx}")
            sys.exit(1)
        indices = [idx]

    results = []
    for i in indices:
        r = process_site(i)
        if r:
            results.append(r)

    if len(results) > 1:
        print_final_table(results)


if __name__ == "__main__":
    main()
