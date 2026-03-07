# AutoTestAI — Result Evaluation Guide

## Test Server v2 Specification

**URL:** `http://127.0.0.1:5001/login`  
**Form fields:** `username` (text) + `password` (password)  
**Form ID:** `loginForm`

| Field    | HTML constraint | True server constraint |
|----------|-----------------|------------------------|
| username | minlength=3, maxlength=15 | Same (no discrepancy) |
| password | minlength=**6**, maxlength=30 | minlength=**8** (BUG-1) |

---

## Intentional Bugs

| ID | Type | Description | Which tests detect it |
|----|------|-------------|----------------------|
| **BUG-1** | BVA off-by-one | HTML says password `minlength=6`, server rejects `len < 8`. Passwords of 6 or 7 chars fail at server but pass browser validation. | `bva_length_password_1` (6 chars, expected success → FAIL), `bva_length_password_2` (7 chars, expected success → FAIL) |
| **BUG-2** | ECP reserved value | Username `"admin"` is always rejected with error, even when length is valid. | `ecp_text_username_special` or any test that uses `"admin"` as username |
| **BUG-3** | ECP undocumented rule | Any username containing a digit (0–9) is rejected. No HTML hint. Tests using `"TestUser1"`, `"user1"` will unexpectedly fail. | UseCase tests that use `TestUser1`, any ECP valid test with numeric username |

---

## How to Evaluate a Run

### Step 1 — Check overall pass rate

| Result | Interpretation |
|--------|---------------|
| **100% pass** | All tests have correct `expected_result` values matching server behaviour — no bugs detected OR all are known/documented bugs already captured |
| **75–99% pass** | Good coverage; failures should map to known bugs or test design issues |
| **< 75% pass** | Likely test design problem (wrong `expected_result`, invalid `test_data`, or server not running) |

---

### Step 2 — Classify each failure

For every FAILED test, ask:

**A. Is the `expected_result` wrong?**
- Check: Does the value in `test_value` actually cause an error?
- Example: `email_1` value `"aaaaa"` (no `@`) → browser rejects it → form never submits → heuristic sees form still present → outcome = `error`. If test said `expected=success`, that's a test design error.
- Fix: Correct `expected_result` in JSON or in the generator.

**B. Is the `test_data` incomplete or invalid?**
- Check: `test_data` must include ALL required fields with valid values, except the one under test.
- Example: UseCase test with empty `test_data` → form submits blank → always fails.
- Fix: Populate companion fields with valid values.

**C. Is this a genuine server bug (test correctly detected it)?**
- Check: `expected_result=success` but server returned error.
- Example: `bva_length_password_1` sends 6-char password, expects success (per HTML), but server rejects it (BUG-1).
- This is **correct detection** — the test passed its job.

---

### Step 3 — Expected failures for this server

These tests SHOULD fail because they correctly detect the intentional bugs:

| Test ID | Expected result in JSON | Server returns | Verdict |
|---------|------------------------|----------------|---------|
| `bva_length_*_password_1` | `success` (6 chars) | `error` (BUG-1: server needs 8) | ✅ Bug detected |
| `bva_length_*_password_2` | `success` (7 chars) | `error` (BUG-1: server needs 8) | ✅ Bug detected |
| any test with `username=admin` | `success` | `error` (BUG-2) | ✅ Bug detected |
| UseCase tests using `TestUser1` | `success` | `error` (BUG-3: digit in username) | ✅ Bug detected |

> A test FAILING because it detected a real server bug is a **success** for the testing system, not a problem. The goal is detection, not passing.

---

### Step 4 — Evaluate RL oracle decisions

In the report footer: `Heuristic: X | LLM: Y | Early Stop: Z`

| Metric | Good sign | Bad sign |
|--------|-----------|----------|
| `ε` (epsilon) in logs | Decreasing run-over-run (e.g. 1.0 → 0.8 → 0.5) | Stuck at 1.0 (not learning) |
| LLM% | Drops after 2–3 runs (agent learns heuristic works) | Stays high (agent not learning) |
| `stop_reason` | `completed` | `server_unreachable` (start the server), `time_limit` (increase limit), `rl_stop` (oracle confusion) |
| Heuristic confidence | 85% on clear pass/fail, 65% on ambiguous | All 65% (oracle not distinguishing outcomes) |

---

### Step 5 — Acceptable result for this demo server

After generating fresh tests against `http://127.0.0.1:5001/login`:

| Category | Count | Expected pass |
|----------|-------|---------------|
| BVA — username | 6 | 6/6 (boundaries match HTML & server) |
| BVA — password | 6 | **4/6** (tests 1 & 2 detect BUG-1) |
| ECP — username | ~5 | **4/5** (admin test detects BUG-2) |
| ECP — password | ~5 | 5/5 |
| Use Case | 2–3 | **0–1** (digit in username triggers BUG-3) |

**Target overall: ~80% pass** with the ~20% failures mapping exactly to the 3 documented bugs.  
If you get significantly fewer passes, there is likely a test design issue to fix.  
If you get 100% passes, either the `expected_result` values are wrong, or the bugs were not probed.

---

## Quick Checklist Before Running

- [ ] Server started: `cd test_server && python server.py`
- [ ] Server reachable: open `http://127.0.0.1:5001/login` in browser
- [ ] Fresh crawl done on `http://127.0.0.1:5001`
- [ ] Tests generated from the crawl graph
- [ ] `test_data` includes all required companion fields (check JSON)
- [ ] `expected_result` accounts for the 3 documented bugs
