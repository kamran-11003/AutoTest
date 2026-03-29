import copy
import json
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from test_generator.test_orchestrator import TestOrchestrator
from test_generator.ai_refiner import GeminiTestRefiner


def flatten_counts(test_cases: dict) -> dict:
    bva = len(test_cases.get("bva", []))
    ecp = len(test_cases.get("ecp", []))
    dt = len(test_cases.get("decision_table", []))
    st = len(test_cases.get("state_transition", []))
    uc = len(test_cases.get("use_case", []))
    total = bva + ecp + dt + st + uc
    return {
        "bva": bva,
        "ecp": ecp,
        "decision_table": dt,
        "state_transition": st,
        "use_case": uc,
        "total": total,
    }


def ai_enhanced_count(test_cases: dict) -> int:
    total = 0
    for _, tests in test_cases.items():
        if isinstance(tests, list):
            total += sum(1 for t in tests if isinstance(t, dict) and t.get("ai_enhanced") is True)
    return total


def slug_from_filename(name: str) -> str:
    return name.replace(".json", "")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    crawl_dir = root / "data" / "crawled_graphs"
    out_dir = root / "data" / "generated_tests"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Clean old generated test outputs and index for a fresh 6-site dataset
    for f in out_dir.glob("tests_*.json"):
        f.unlink(missing_ok=True)
    index_file = out_dir / "test_index.json"
    index_file.write_text("{}\n", encoding="utf-8")

    crawl_files = sorted(crawl_dir.glob("*.json"))
    orchestrator = TestOrchestrator()
    refiner = GeminiTestRefiner()
    can_refine = refiner.model is not None

    rows = []

    run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    for crawl_file in crawl_files:
        with crawl_file.open("r", encoding="utf-8") as f:
            crawl_data = json.load(f)

        url = "unknown"
        nodes = crawl_data.get("nodes", [])
        if nodes and isinstance(nodes[0], dict):
            url = nodes[0].get("url", "unknown")
        pages = len(nodes)

        before_results = orchestrator.generate_all_tests(str(crawl_file))
        before_cases = before_results.get("test_cases", {})
        before_counts = flatten_counts(before_cases)

        before_payload = {
            "stage": "before_refinement",
            "generated_at": datetime.now().isoformat(),
            "crawl_file": str(crawl_file),
            "crawl_url": url,
            "pages": pages,
            "test_results": before_results,
            "counts": before_counts,
        }

        base_slug = slug_from_filename(crawl_file.name)
        before_file = out_dir / f"{base_slug}_before_{run_stamp}.json"
        before_file.write_text(json.dumps(before_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        if can_refine:
            refined_cases = refiner.refine_tests(before_cases, crawl_data)
            refine_status = "refined"
        else:
            refined_cases = before_cases
            refine_status = "skipped_no_api_key"

        after_results = copy.deepcopy(before_results)
        after_results["test_cases"] = refined_cases
        after_counts = flatten_counts(refined_cases)
        after_results["summary"] = {
            "total_test_cases": after_counts["total"],
            "bva_count": after_counts["bva"],
            "ecp_count": after_counts["ecp"],
            "decision_table_count": after_counts["decision_table"],
            "state_transition_count": after_counts["state_transition"],
            "use_case_count": after_counts["use_case"],
            "by_type": {
                "bva": after_counts["bva"],
                "ecp": after_counts["ecp"],
                "decision_table": after_counts["decision_table"],
                "state_transition": after_counts["state_transition"],
                "use_case": after_counts["use_case"],
            },
        }

        after_payload = {
            "stage": "after_refinement",
            "generated_at": datetime.now().isoformat(),
            "crawl_file": str(crawl_file),
            "crawl_url": url,
            "pages": pages,
            "refinement_status": refine_status,
            "test_results": after_results,
            "counts": after_counts,
            "ai_enhanced_count": ai_enhanced_count(refined_cases),
            "before_file": str(before_file),
        }

        after_file = out_dir / f"{base_slug}_after_{run_stamp}.json"
        after_file.write_text(json.dumps(after_payload, indent=2, ensure_ascii=False), encoding="utf-8")

        rows.append(
            {
                "website": url,
                "crawl_file": crawl_file.name,
                "pages": pages,
                "before_total": before_counts["total"],
                "after_total": after_counts["total"],
                "delta": after_counts["total"] - before_counts["total"],
                "ai_enhanced": after_payload["ai_enhanced_count"],
                "status": refine_status,
                "before_file": before_file.name,
                "after_file": after_file.name,
            }
        )

    # Build RQ3 markdown table
    rq3 = root / "RQ3.md"
    lines = []
    lines.append("# RQ 3 - Test Execution/Validation Dataset (Before vs After AI Refinement)")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("| Website | Pages | Tests Before | Tests After | Delta | AI Enhanced | Refinement Status | Before File | After File |")
    lines.append("|---|---:|---:|---:|---:|---:|---|---|---|")

    for r in rows:
        lines.append(
            f"| {r['website']} | {r['pages']} | {r['before_total']} | {r['after_total']} | {r['delta']:+d} | {r['ai_enhanced']} | {r['status']} | {r['before_file']} | {r['after_file']} |"
        )

    total_before = sum(r["before_total"] for r in rows)
    total_after = sum(r["after_total"] for r in rows)
    total_enh = sum(r["ai_enhanced"] for r in rows)
    lines.append(
        f"| **TOTAL (6 websites)** | **{sum(r['pages'] for r in rows)}** | **{total_before}** | **{total_after}** | **{total_after-total_before:+d}** | **{total_enh}** |  |  |  |"
    )

    rq3.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Generated before/after datasets for {len(rows)} websites.")
    print(f"RQ3 table written to: {rq3}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
