"""
run_test_websites.py  —  Single-website crawl → generate → AI-refine → execute pipeline
=========================================================================================

Runs the FULL pipeline for ONE website at a time (API rate-limit safe).
Run this script 8 times, once per website index (0-7).

Usage
-----
    python scripts/run_test_websites.py --site 0   # site1_contact
    python scripts/run_test_websites.py --site 1   # site2_booking
    python scripts/run_test_websites.py --site 2   # site3_register
    python scripts/run_test_websites.py --site 3   # site4_search
    python scripts/run_test_websites.py --site 4   # site5_feedback
    python scripts/run_test_websites.py --site 5   # site6_ecommerce (SSR multi-page)
    python scripts/run_test_websites.py --site 6   # site7_spa_taskboard (SPA)
    python scripts/run_test_websites.py --site 7   # site8_medical (multi-page clinic)

    # Or run all 8 sequentially (long — waits between each for API cool-down):
    python scripts/run_test_websites.py --site all

All artefacts are written to the standard data/ directories so the Streamlit
app can display them immediately:
    data/crawled_graphs/<site>_<timestamp>.json       ← crawl
    data/generated_tests/<site>_before_<ts>.json      ← raw tests
    data/generated_tests/<site>_after_<ts>.json       ← AI-refined tests
    data/generated_tests/test_index.json              ← updated index
    data/test_results/report_<site>_<ts>.html/json    ← execution report
    data/rl_run_results/test_websites_stats.json      ← aggregate data

Requirements
------------
    • Live-Server (VS Code extension) serving test_websites/ on http://127.0.0.1:5500
    • GEMINI_API_KEYS in .env
    • Playwright installed  (playwright install chromium)
"""

import sys
import asyncio
import json
import copy
import time
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from test_generator.test_orchestrator import TestOrchestrator
from test_generator.ai_refiner import GeminiTestRefiner
from test_generator.test_storage import TestStorage
from test_generator.file_linking import file_linking
from execution.adaptive_runner import AdaptiveRunner
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# ── Site definitions ──────────────────────────────────────────────────────────
BASE_URL = "http://localhost:5500/test_websites"

SITES = [
    {
        "id":          "site1_contact",
        "name":        "Contact Form",
        "url":         f"{BASE_URL}/site1_contact/index.html",
        "description": "4-field contact form: name(2-50), email, subject(select), message(10-500)",
        "forms": [
            {
                "name": "contactForm",
                "submit_button": "Submit",
                "fields": {
                    "name":    {"type": "text",   "min": 2,  "max": 50,  "required": True},
                    "email":   {"type": "email",  "required": True},
                    "subject": {"type": "select", "options": ["General Inquiry","Support","Billing","Other"], "required": True},
                    "message": {"type": "textarea","min": 10, "max": 500, "required": True},
                },
            }
        ],
    },
    {
        "id":          "site2_booking",
        "name":        "Hotel Booking",
        "url":         f"{BASE_URL}/site2_booking/index.html",
        "description": "Hotel booking: checkin(≥today), checkout(>checkin), guests(1-10), room(select), email",
        "forms": [
            {
                "name": "bookingForm",
                "submit_button": "Book Now",
                "fields": {
                    "checkin":  {"type": "date",   "required": True,  "min": "today"},
                    "checkout": {"type": "date",   "required": True,  "min": "checkin+1"},
                    "guests":   {"type": "number", "min": 1, "max": 10, "required": True},
                    "room":     {"type": "select", "options": ["Standard","Deluxe","Suite","Penthouse"], "required": True},
                    "email":    {"type": "email",  "required": True},
                },
            }
        ],
    },
    {
        "id":          "site3_register",
        "name":        "User Registration",
        "url":         f"{BASE_URL}/site3_register/index.html",
        "description": "Registration: username(3-20 alphanumeric), email, password(≥8,upper+digit+special), confirm, age(18-120)",
        "forms": [
            {
                "name": "registerForm",
                "submit_button": "Register",
                "fields": {
                    "username":        {"type": "text",     "min": 3, "max": 20, "pattern": r"^[a-zA-Z0-9_]+$", "required": True},
                    "email":           {"type": "email",    "required": True},
                    "password":        {"type": "password", "min": 8, "required": True, "rules": "uppercase+digit+special"},
                    "confirmPassword": {"type": "password", "required": True, "match": "password"},
                    "age":             {"type": "number",   "min": 18, "max": 120, "required": True},
                },
            }
        ],
    },
    {
        "id":          "site4_search",
        "name":        "Product Search",
        "url":         f"{BASE_URL}/site4_search/index.html",
        "description": "Search: keywords(≥2), category(select), minPrice(≥0), maxPrice(≥min,≤10000)",
        "forms": [
            {
                "name": "searchForm",
                "submit_button": "Search Products",
                "fields": {
                    "keywords": {"type": "text",   "min": 2,  "required": True},
                    "category": {"type": "select", "options": ["Electronics","Clothing","Books","Home & Garden","Sports"], "required": True},
                    "minPrice": {"type": "number", "min": 0,     "max": 10000, "required": False},
                    "maxPrice": {"type": "number", "min": 0,     "max": 10000, "required": False, "gte": "minPrice"},
                },
            }
        ],
    },
    {
        "id":          "site5_feedback",
        "name":        "Feedback Survey",
        "url":         f"{BASE_URL}/site5_feedback/index.html",
        "description": "Survey: name(required), email(optional), rating(radio 1-5), categories(checkbox ≥1), comment(≤300), phone(optional 7-15 digits)",
        "forms": [
            {
                "name": "feedbackForm",
                "submit_button": "Submit Feedback",
                "fields": {
                    "name":       {"type": "text",     "required": True},
                    "email":      {"type": "email",    "required": False},
                    "rating":     {"type": "radio",    "required": True,  "options": ["1","2","3","4","5"]},
                    "categories": {"type": "checkbox", "required": True,  "min_checked": 1},
                    "comment":    {"type": "textarea", "required": False, "max": 300},
                    "phone":      {"type": "text",     "required": False, "pattern": r"^\d{7,15}$"},
                },
            }
        ],
    },
    # ── NEW: Site 6 — Next.js SSR E-Commerce (port 3006, 4 pages, 2 forms) ──
    {
        "id":          "site6_ecommerce",
        "name":        "E-Commerce (Next.js SSR)",
        "url":         "http://localhost:3006",
        "description": "Next.js SSR e-commerce: login(email,password≥6) + checkout(name,email,address,city,zip 5-digit,card 13-19,expiry MM/YY,cvv 3-4)",
        "forms": [
            {
                "name": "loginForm",
                "submit_button": "Sign In",
                "fields": {
                    "loginEmail":    {"type": "email",    "required": True},
                    "loginPassword": {"type": "password", "min": 6, "required": True},
                },
            },
            {
                "name": "checkoutForm",
                "submit_button": "Place Order",
                "fields": {
                    "fullName":      {"type": "text",  "min": 2, "max": 60, "required": True},
                    "shippingEmail": {"type": "email", "required": True},
                    "address":       {"type": "text",  "min": 5, "max": 120, "required": True},
                    "city":          {"type": "text",  "min": 2, "max": 50,  "required": True},
                    "zipCode":       {"type": "text",  "required": True, "pattern": r"^\d{5}$"},
                    "cardNumber":    {"type": "text",  "min": 13, "max": 19, "required": True, "pattern": r"^\d{13,19}$"},
                    "expiry":        {"type": "text",  "required": True, "pattern": r"^(0[1-9]|1[0-2])\/\d{2}$"},
                    "cvv":           {"type": "text",  "min": 3, "max": 4,  "required": True, "pattern": r"^\d{3,4}$"},
                },
            },
        ],
    },
    # ── NEW: Site 7 — React+Vite SPA TaskBoard (port 3007, 3 routes, 3 forms) ──
    {
        "id":          "site7_spa_taskboard",
        "name":        "Task Board (React SPA)",
        "url":         "http://localhost:3007",
        "description": "React+Vite SPA with 3 routes/forms: signup(user,email,pw≥8+upper+digit,role), task(title,desc,priority,category,dueDate), settings(displayName,bio≤200,timezone)",
        "forms": [
            {
                "name": "signupForm",
                "submit_button": "Create Account",
                "fields": {
                    "username":       {"type": "text",     "min": 3, "max": 20, "pattern": r"^[a-zA-Z0-9_]+$", "required": True},
                    "signupEmail":    {"type": "email",    "required": True},
                    "signupPassword": {"type": "password", "min": 8, "required": True, "rules": "uppercase+digit"},
                    "role":           {"type": "select",   "options": ["developer","designer","manager","qa"], "required": True},
                },
            },
            {
                "name": "taskForm",
                "submit_button": "Add Task",
                "fields": {
                    "taskTitle": {"type": "text",     "min": 3, "max": 100, "required": True},
                    "taskDesc":  {"type": "textarea", "min": 10, "max": 500, "required": True},
                    "priority":  {"type": "select",   "options": ["low","medium","high","critical"], "required": True},
                    "category":  {"type": "select",   "options": ["frontend","backend","devops","testing","design"], "required": True},
                    "dueDate":   {"type": "date",     "required": True, "min": "today"},
                },
            },
            {
                "name": "settingsForm",
                "submit_button": "Save Settings",
                "fields": {
                    "displayName":  {"type": "text",     "min": 2, "max": 50, "required": True},
                    "bio":          {"type": "textarea", "required": False, "max": 200},
                    "timezone":     {"type": "select",   "options": ["UTC-8","UTC-5","UTC+0","UTC+1","UTC+5","UTC+8"], "required": True},
                    "emailNotify":  {"type": "checkbox", "required": False},
                },
            },
        ],
    },
    # ── NEW: Site 8 — Express+EJS Medical Clinic (port 3008, 4 routes, 2 forms) ──
    {
        "id":          "site8_medical",
        "name":        "Medical Clinic",
        "url":         "http://localhost:3008",
        "description": "Express+EJS clinic: appointment(doctor,date≥today+noSunday,time,visitType,reason 10-300) + patient(first/lastName 2-30,dob past,gender,phone 10-15 digits,email,emergency 2-50,bloodType)",
        "forms": [
            {
                "name": "appointmentForm",
                "submit_button": "Book Appointment",
                "fields": {
                    "doctor":    {"type": "select",   "options": ["dr_johnson","dr_chen","dr_davis","dr_patel"], "required": True},
                    "appDate":   {"type": "date",     "required": True, "min": "today", "rules": "no_sunday"},
                    "appTime":   {"type": "select",   "options": ["09:00","10:00","11:00","14:00","15:00","16:00"], "required": True},
                    "visitType": {"type": "select",   "options": ["new","followup","emergency","checkup"], "required": True},
                    "reason":    {"type": "textarea", "min": 10, "max": 300, "required": True},
                },
            },
            {
                "name": "patientForm",
                "submit_button": "Register Patient",
                "fields": {
                    "firstName":        {"type": "text",   "min": 2, "max": 30, "required": True},
                    "lastName":         {"type": "text",   "min": 2, "max": 30, "required": True},
                    "dob":              {"type": "date",   "required": True, "max": "today", "rules": "past_date_max_120y"},
                    "gender":           {"type": "select", "options": ["male","female","other"], "required": True},
                    "patientPhone":     {"type": "text",   "required": True, "pattern": r"^\d{10,15}$"},
                    "patientEmail":     {"type": "email",  "required": True},
                    "emergencyContact": {"type": "text",   "min": 2, "max": 50, "required": True},
                    "bloodType":        {"type": "select", "options": ["A+","A-","B+","B-","AB+","AB-","O+","O-"], "required": True},
                },
            },
        ],
    },
]

# ── Pipeline constants ────────────────────────────────────────────────────────
API_BUDGET    = 60    # Gemini LLM calls per site during execution
TIME_LIMIT_S  = 600   # 10 min wall-clock per site
API_COOLDOWN  = 15    # seconds to wait between sites (rate-limit guard)
HEADLESS      = True
MAX_PAGES     = 10    # multi-page sites need more (site6=4, site8=4)
MAX_DEPTH     = 3


# ── Streamlit-visible state helpers ──────────────────────────────────────────

def _status_file() -> Path:
    """JSON file Streamlit reads to show live pipeline progress."""
    p = ROOT / "data" / "pipeline_status.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    return p


def update_status(site_id: str, step: str, detail: str = "", data: dict = None):
    """Write current pipeline stage to data/pipeline_status.json."""
    status = {
        "site_id":    site_id,
        "step":       step,
        "detail":     detail,
        "updated_at": datetime.now().isoformat(),
        "data":       data or {},
    }
    _status_file().write_text(json.dumps(status, indent=2), encoding="utf-8")
    print(f"  [{site_id}] {step}: {detail}")


# ── Step 1: Crawl ─────────────────────────────────────────────────────────────

async def step_crawl(site: dict) -> tuple[dict | None, str | None]:
    """
    Crawl the site and save crawl data.
    Returns (crawl_data, crawl_filepath_str) or (None, None) on failure.
    """
    from crawler.orchestrator import CrawlerOrchestrator

    update_status(site["id"], "crawling", f"Crawling {site['url']}")

    try:
        orch = CrawlerOrchestrator(config_path=str(ROOT / "config" / "crawler_config.yaml"))
        # Override limits for targeted crawl of small test sites
        orch.max_pages = MAX_PAGES
        orch.max_depth = MAX_DEPTH

        crawl_data = await orch.start_crawl(
            start_url=site["url"],
            manual_login=False,
        )

        # Persist crawl
        out_dir = ROOT / "data" / "crawled_graphs"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        crawl_file = out_dir / f"{site['id']}_{ts}.json"
        crawl_file.write_text(
            json.dumps(crawl_data, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        pages = len(crawl_data.get("nodes", []))
        forms = sum(len(n.get("forms", [])) for n in crawl_data.get("nodes", []))
        update_status(
            site["id"], "crawled",
            f"Pages: {pages}, Forms: {forms}",
            {"pages": pages, "forms": forms, "crawl_file": crawl_file.name},
        )
        return crawl_data, str(crawl_file)

    except Exception as exc:
        update_status(site["id"], "crawl_failed", str(exc))
        logger.error(f"Crawl failed for {site['id']}: {exc}")
        return None, None


# ── Step 2: Generate tests ────────────────────────────────────────────────────

def step_generate(site: dict, crawl_file: str) -> tuple[dict | None, str | None]:
    """Generate test cases from the crawl file.  Returns (test_results, before_file_str)."""
    update_status(site["id"], "generating", "Running TestOrchestrator …")

    out_dir = ROOT / "data" / "generated_tests"
    out_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    try:
        orchestrator = TestOrchestrator()
        test_results = orchestrator.generate_all_tests(crawl_file)
        tc = test_results.get("test_cases", {})
        counts = {k: len(v) for k, v in tc.items()}
        total  = sum(counts.values())

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

        # Update test index
        _update_test_index(out_dir, site["id"], before_file.name, ts, total)

        update_status(
            site["id"], "generated",
            f"Total tests: {total}  (BVA={counts.get('bva',0)} ECP={counts.get('ecp',0)} "
            f"DT={counts.get('decision_table',0)} ST={counts.get('state_transition',0)} "
            f"UC={counts.get('use_case',0)})",
            {"counts": counts, "total": total, "before_file": before_file.name},
        )
        return test_results, str(before_file)

    except Exception as exc:
        update_status(site["id"], "generate_failed", str(exc))
        logger.error(f"Generate failed for {site['id']}: {exc}")
        return None, None


# ── Step 3: AI Refinement ─────────────────────────────────────────────────────

def step_refine(site: dict, test_results: dict, crawl_data: dict | None, before_file: str) -> tuple[dict, str]:
    """
    AI-refine the test cases.  If API unavailable, pass through unchanged.
    Returns (refined_results, after_file_str).
    """
    update_status(site["id"], "refining", "Calling Gemini for AI refinement …")

    out_dir = ROOT / "data" / "generated_tests"
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    refiner = GeminiTestRefiner()
    tc      = test_results.get("test_cases", {})

    if refiner.model is not None and crawl_data is not None:
        try:
            refined_tc     = refiner.refine_tests(tc, crawl_data)
            refine_status  = "refined"
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
        "total_test_cases":      total,
        "bva_count":             counts.get("bva", 0),
        "ecp_count":             counts.get("ecp", 0),
        "decision_table_count":  counts.get("decision_table", 0),
        "state_transition_count":counts.get("state_transition", 0),
        "use_case_count":        counts.get("use_case", 0),
    }

    # Count AI-enhanced tests
    ai_enhanced = sum(
        1 for tests in refined_tc.values() if isinstance(tests, list)
        for t in tests if isinstance(t, dict) and t.get("ai_enhanced") is True
    )

    after_payload = {
        "stage":           "after_refinement",
        "generated_at":    datetime.now().isoformat(),
        "crawl_url":       site["url"],
        "site_id":         site["id"],
        "refinement_status": refine_status,
        "test_results":    after_results,
        "counts":          counts,
        "total":           total,
        "ai_enhanced_count": ai_enhanced,
        "before_file":     Path(before_file).name,
    }
    after_file = out_dir / f"{site['id']}_after_{ts}.json"
    after_file.write_text(
        json.dumps(after_payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Update test index with final after version
    _update_test_index(out_dir, site["id"], after_file.name, ts, total, ai_refined=(refine_status == "refined"))

    update_status(
        site["id"], "refined",
        f"Status: {refine_status}  AI-enhanced: {ai_enhanced}/{total}",
        {"refine_status": refine_status, "ai_enhanced": ai_enhanced, "total": total, "after_file": after_file.name},
    )
    return after_results, str(after_file)


# ── Step 4: Execute tests ─────────────────────────────────────────────────────

async def step_execute(site: dict, after_results: dict, after_file: str) -> dict:
    """Run AdaptiveRunner on the refined test suite.  Returns summary dict."""
    update_status(site["id"], "executing", f"Running {after_results['summary']['total_test_cases']} tests …")

    runner = AdaptiveRunner(
        api_budget   = API_BUDGET,
        time_limit_s = TIME_LIMIT_S,
        rl_mode      = True,
        headless     = HEADLESS,
    )

    crawl_id = site["id"]
    suite    = after_results  # already a dict with test_cases key

    t0 = time.perf_counter()
    try:
        report = await runner.execute(suite, crawl_id=crawl_id)
    except Exception as exc:
        elapsed = round(time.perf_counter() - t0, 1)
        logger.error(f"Execution crashed for {site['id']}: {exc}")
        update_status(site["id"], "execute_failed", str(exc))
        return _crash_summary(crawl_id, exc, elapsed)

    summary = {
        "site_id":          site["id"],
        "site_name":        site["name"],
        "url":              site["url"],
        "crawl_id":         crawl_id,
        "status":           "ok",
        "total":            report.total,
        "passed":           report.passed,
        "failed":           report.failed,
        "errors":           report.errors,
        "skipped":          report.skipped,
        "pass_rate":        report.pass_rate,
        "api_calls":        report.api_calls_used,
        "api_cost":         round(report.api_cost, 4),
        "duration_s":       report.duration_s,
        "stop_reason":      report.stop_reason,
        "heur_decisions":   report.heuristic_decisions,
        "llm_decisions":    report.llm_decisions,
        "pattern_overrides":report.pattern_overrides,
        "after_file":       Path(after_file).name,
        "executed_at":      datetime.now().isoformat(),
    }

    update_status(
        site["id"], "done",
        f"Pass: {report.passed}/{report.total} ({report.pass_rate}%)  "
        f"LLM: {report.api_calls_used}  Cost: ${report.api_cost:.3f}",
        summary,
    )
    return summary


# ── Helpers ───────────────────────────────────────────────────────────────────

def _crash_summary(crawl_id: str, exc: Exception, elapsed: float) -> dict:
    return {
        "site_id": crawl_id, "site_name": crawl_id, "url": "",
        "status": "crash", "error": str(exc),
        "total": 0, "passed": 0, "failed": 0, "errors": 0, "skipped": 0,
        "pass_rate": 0.0, "api_calls": 0, "api_cost": 0.0,
        "duration_s": elapsed, "stop_reason": "crash",
        "heur_decisions": 0, "llm_decisions": 0, "pattern_overrides": 0,
        "executed_at": datetime.now().isoformat(),
    }


def _update_test_index(out_dir: Path, site_id: str, filename: str, ts: str, total: int, ai_refined: bool = False):
    """Keep data/generated_tests/test_index.json up-to-date."""
    index_file = out_dir / "test_index.json"
    if index_file.exists():
        try:
            index = json.loads(index_file.read_text(encoding="utf-8"))
        except Exception:
            index = {}
    else:
        index = {}

    # Use site_id as the stable key (not a crawl hash so Streamlit can find it easily)
    h = hashlib.md5(site_id.encode()).hexdigest()
    index[h] = {
        "site_id":     site_id,
        "filename":    filename,
        "timestamp":   ts,
        "total_tests": total,
        "version":     index.get(h, {}).get("version", 0) + 1,
        "ai_refined":  ai_refined,
        "last_updated":datetime.now().isoformat(),
    }
    index_file.write_text(json.dumps(index, indent=2), encoding="utf-8")


def _append_aggregate(summary: dict):
    """Append/update data/rl_run_results/test_websites_stats.json."""
    agg_dir = ROOT / "data" / "rl_run_results"
    agg_dir.mkdir(parents=True, exist_ok=True)
    agg_file = agg_dir / "test_websites_stats.json"

    if agg_file.exists():
        try:
            agg = json.loads(agg_file.read_text(encoding="utf-8"))
        except Exception:
            agg = {"sites": {}, "updated_at": ""}
    else:
        agg = {"sites": {}, "updated_at": ""}

    agg["sites"][summary["site_id"]] = summary
    agg["updated_at"] = datetime.now().isoformat()
    agg_file.write_text(json.dumps(agg, indent=2), encoding="utf-8")


# ── Full pipeline for one site ────────────────────────────────────────────────

async def run_site(site: dict) -> dict:
    print(f"\n{'='*70}")
    print(f"  PIPELINE: {site['name']}  ({site['id']})")
    print(f"  URL     : {site['url']}")
    print(f"{'='*70}")

    # Step 1 — Crawl
    crawl_data, crawl_file = await step_crawl(site)
    if crawl_file is None:
        logger.error("Crawl failed — aborting pipeline for this site")
        return _crash_summary(site["id"], RuntimeError("crawl failed"), 0)

    # Step 2 — Generate
    test_results, before_file = step_generate(site, crawl_file)
    if test_results is None:
        return _crash_summary(site["id"], RuntimeError("generate failed"), 0)

    # Step 3 — AI Refine
    after_results, after_file = step_refine(site, test_results, crawl_data, before_file)

    # Step 4 — Execute
    summary = await step_execute(site, after_results, after_file)

    # Save to aggregate stats
    _append_aggregate(summary)

    return summary


# ── Entry point ───────────────────────────────────────────────────────────────

async def main():
    parser = argparse.ArgumentParser(
        description="Run crawl→generate→refine→execute pipeline for test websites"
    )
    parser.add_argument(
        "--site",
        default="all",
        help="Site index (0-7) or 'all' to run every site sequentially",
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)",
    )
    parser.add_argument(
        "--no-headless",
        dest="headless",
        action="store_false",
        help="Show browser window during crawl/execution",
    )
    args = parser.parse_args()

    global HEADLESS
    HEADLESS = args.headless

    if args.site == "all":
        indices = list(range(len(SITES)))
    else:
        try:
            indices = [int(args.site)]
        except ValueError:
            print(f"ERROR: --site must be 0-{len(SITES)-1} or 'all'")
            sys.exit(1)

    results = []
    for i in indices:
        if i < 0 or i >= len(SITES):
            print(f"ERROR: site index {i} is out of range (0-{len(SITES)-1})")
            continue

        summary = await run_site(SITES[i])
        results.append(summary)
        _print_summary(summary)

        # Rate-limit guard between sites
        if i != indices[-1]:
            print(f"\n  ⏳ Waiting {API_COOLDOWN}s before next site …")
            await asyncio.sleep(API_COOLDOWN)

    # Final aggregate table
    print("\n" + "="*70)
    print("  FINAL RESULTS — TEST WEBSITES")
    print("="*70)
    print(f"{'Site':<22} {'Tests':>6} {'Passed':>7} {'Pass%':>6} {'LLM':>5} {'Cost':>8} {'Stop':>16}")
    print("-"*70)
    for r in results:
        print(
            f"{r['site_id']:<22} {r['total']:>6} {r['passed']:>7} "
            f"{r['pass_rate']:>5.1f}% {r['llm_decisions']:>5} "
            f"${r['api_cost']:>7.3f} {r['stop_reason']:>16}"
        )
    print("="*70)

    # Persist final aggregate
    agg_dir = ROOT / "data" / "rl_run_results"
    agg_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    (agg_dir / f"run_{ts}.json").write_text(
        json.dumps(results, indent=2), encoding="utf-8"
    )
    print(f"\n  Stats written to data/rl_run_results/run_{ts}.json")
    print(f"  Live status    at data/pipeline_status.json")
    print(f"  Crawls         at data/crawled_graphs/")
    print(f"  Tests          at data/generated_tests/")
    print(f"  Reports        at data/test_results/")


def _print_summary(r: dict):
    print(f"\n  {'─'*60}")
    print(f"  DONE  : {r['site_id']}  ({r.get('site_name', '')})")
    print(f"  Tests : {r['passed']}/{r['total']} passed  ({r['pass_rate']:.1f}%)")
    print(f"  Oracle: heur={r['heur_decisions']} llm={r['llm_decisions']} overrides={r['pattern_overrides']}")
    print(f"  Cost  : {r['api_calls']} calls  ${r['api_cost']:.3f}  {r['duration_s']:.1f}s")
    print(f"  Stop  : {r['stop_reason']}")


if __name__ == "__main__":
    asyncio.run(main())
