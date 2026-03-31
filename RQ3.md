# RQ3 — AI Test Refinement Evaluation on Controlled Test Websites

> **Phase 2 of the experiment uses five purpose-built test websites that
> enforce real input validation, eliminating the oracle-defeat conditions
> identified in Phase 1.**  Each website is served locally via Live Server at
> `http://127.0.0.1:5500/test_websites/` and its source lives in
> `test_websites/` in this repository.

---

## 3.1 Phase 2 — Controlled Test Websites

### Website Specifications

#### Site 1 — Contact Form (`site1_contact`)
URL: `http://localhost:5500/test_websites/site1_contact/index.html`  
Path: `test_websites/site1_contact/`

| Field | Type | Constraint | Validation Rule |
|---|---|---|---|
| `name` | text | required | length 2–50 |
| `email` | email | required | regex `[^@]+@[^@]+\.[^@]+` |
| `subject` | select | required | one of: General Inquiry, Support, Billing, Other |
| `message` | textarea | required | length 10–500 |

**Submit button:** "Submit"  
**On success:** redirects to `success.html` (URL change = oracle-detectable)  
**On failure:** inline `.error-msg` divs populated with red text

**Expected test outcomes:**

| Test Class | Example Input | Expected Result |
|---|---|---|
| BVA valid | name="Al" (exactly 2 chars) | PASS — form submits |
| BVA invalid | name="A" (1 char) | FAIL — error displayed |
| ECP invalid | email="notanemail" | FAIL — error displayed |
| ECP valid | email="user@test.com" | PASS (with other fields valid) |
| BVA boundary | message = 9 chars | FAIL |
| BVA boundary | message = 10 chars | PASS |

---

#### Site 2 — Hotel Booking (`site2_booking`)
URL: `http://localhost:5500/test_websites/site2_booking/index.html`  
Path: `test_websites/site2_booking/`

| Field | Type | Constraint | Validation Rule |
|---|---|---|---|
| `checkin` | date | required | ≥ today |
| `checkout` | date | required | > checkin |
| `guests` | number | required | integer 1–10 |
| `room` | select | required | one of: Standard, Deluxe, Suite, Penthouse |
| `email` | email | required | regex |

**On success:** redirects to `confirmed.html?ref=BKXXXXXX`  
**Cross-field rule:** checkout > checkin (both must be present)

**Expected test outcomes:**

| Test Class | Example | Expected Result |
|---|---|---|
| BVA valid | guests=1 | PASS |
| BVA valid | guests=10 | PASS |
| BVA invalid | guests=0 | FAIL |
| BVA invalid | guests=11 | FAIL |
| Cross-field invalid | checkout ≤ checkin | FAIL |
| Date past | checkin = yesterday | FAIL |

---

#### Site 3 — User Registration (`site3_register`)
URL: `http://localhost:5500/test_websites/site3_register/index.html`  
Path: `test_websites/site3_register/`

| Field | Type | Constraint | Validation Rule |
|---|---|---|---|
| `username` | text | required | 3–20 chars, `^[a-zA-Z0-9_]+$` |
| `email` | email | required | regex |
| `password` | password | required | ≥8 chars, ≥1 uppercase, ≥1 digit, ≥1 special char |
| `confirmPassword` | password | required | must match `password` |
| `age` | number | required | integer 18–120 |

**On success:** inline success banner: "✅ Account created! Welcome, {username}"

**Expected test outcomes:**

| Test Class | Example | Expected Result |
|---|---|---|
| BVA valid | username="abc" (3 chars) | PASS |
| BVA invalid | username="ab" (2 chars) | FAIL |
| ECP invalid | password="password" (no digit/special/upper) | FAIL |
| ECP valid | password="Test@123" | PASS |
| Cross-field | confirmPassword ≠ password | FAIL |
| BVA boundary | age=17 | FAIL |
| BVA boundary | age=18 | PASS |

---

#### Site 4 — Product Search (`site4_search`)
URL: `http://localhost:5500/test_websites/site4_search/index.html`  
Path: `test_websites/site4_search/`

| Field | Type | Constraint | Validation Rule |
|---|---|---|---|
| `keywords` | text | required | length ≥ 2 |
| `category` | select | required | one of: Electronics, Clothing, Books, Home & Garden, Sports |
| `minPrice` | number | optional | ≥ 0 |
| `maxPrice` | number | optional | ≥ minPrice, ≤ 10000 |

**On success:** reveals `#results` section with 3 dummy product cards  
**Cross-field rule:** maxPrice ≥ minPrice

**Expected test outcomes:**

| Test Class | Example | Expected Result |
|---|---|---|
| BVA valid | keywords="ab" (2 chars) | PASS |
| BVA invalid | keywords="a" (1 char) | FAIL |
| Cross-field invalid | minPrice=500, maxPrice=100 | FAIL |
| ECP valid | minPrice=0, maxPrice=10000 | PASS |
| ECP invalid | maxPrice=10001 | FAIL |

---

#### Site 5 — Feedback Survey (`site5_feedback`)
URL: `http://localhost:5500/test_websites/site5_feedback/index.html`  
Path: `test_websites/site5_feedback/`

| Field | Type | Constraint | Validation Rule |
|---|---|---|---|
| `name` | text | required | non-empty |
| `email` | email | optional | if provided: regex |
| `rating` | radio (1–5) | required | one selected |
| `categories` | checkboxes | required | ≥ 1 checked |
| `comment` | textarea | optional | length ≤ 300 |
| `phone` | text | optional | if provided: 7–15 digits |

**On success:** redirects to `thank-you.html`

**Expected test outcomes:**

| Test Class | Example | Expected Result |
|---|---|---|
| Required field | name="" | FAIL |
| Optional valid | email="" | PASS (if other fields valid) |
| Optional invalid | email="notvalid" | FAIL |
| BVA invalid | comment = 301 chars | FAIL |
| BVA valid | comment = 300 chars | PASS |
| Required group | no rating selected | FAIL |
| Required group | no category checked | FAIL |
| Optional valid | phone="" | PASS |
| Optional BVA | phone = 6 digits | FAIL |

---

## 3.2 Phase 2 Results

Updated after each pipeline run. Run: `python scripts/run_test_websites.py --site <0-4>`

| Site | Pages | Tests Before | Tests After | Δ | AI Enhanced | Passed | Failed | Pass % | LLM Calls | Cost ($) | Stop |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| site1_contact | 1 | 52 | 58 | +6 | 58 | 46 | 12 | 79.3% | 4 | 0.008 | completed |
| site2_booking | 1 | 41 | 46 | +5 | 46 | 38 | 8 | 82.6% | 5 | 0.010 | completed |
| site3_register | 1 | 66 | 72 | +6 | 72 | 61 | 11 | 84.7% | 2 | 0.004 | completed |
| site4_search | 1 | 32 | 38 | +6 | 38 | 25 | 13 | 65.8% | 1 | 0.002 | completed |
| site5_feedback | 1 | 116 | 117 | +1 | 97 | 88 | 29 | 75.2% | 6 | 0.012 | completed |
| **TOTAL** | **5** | **307** | **331** | **+24** | **311** | **258** | **73** | **77.9%** | **18** | **0.036** | |
