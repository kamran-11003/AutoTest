# 🌐 Small Websites for Testing

## Instructions
Each website has forms that are simple enough to crawl quickly but complex enough to test your system. Pick any 3 and run the crawl + test pipeline.

---

## Set 1: Simple Form Websites (Fastest)

### 1. **Example Contact Form**
**URL:** https://www.example.com/contact  
**Type:** Contact form  
**Estimated Tests:** 15-25  
**Forms:** Name, Email, Message (Simple, 3 fields)  
**Complexity:** ⭐ Easiest  

### 2. **HTTP Test Forms**
**URL:** https://www.httpbin.org/forms/post  
**Type:** Form submission test  
**Estimated Tests:** 20-30  
**Forms:** Text, file upload, checkbox, radio  
**Complexity:** ⭐⭐ Easy  

### 3. **HTML5 Form Elements**
**URL:** https://www.w3schools.com/html/html_form_elements.asp  
**Type:** Education demo  
**Estimated Tests:** 25-40  
**Forms:** All HTML5 input types  
**Complexity:** ⭐⭐ Easy  

---

## Set 2: Medium Complexity (Standard)

### 4. **Formspree Contact**
**URL:** https://formspree.io/  
**Type:** Form backend service  
**Estimated Tests:** 40-60  
**Forms:** Contact, survey, email capture  
**Complexity:** ⭐⭐⭐ Medium  

### 5. **W3Schools Form Demo**
**URL:** https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit  
**Type:** Interactive demo  
**Estimated Tests:** 35-50  
**Forms:** Basic HTML form submisson  
**Complexity:** ⭐⭐⭐ Medium  

### 6. **Bootstrap Form Examples**
**URL:** https://getbootstrap.com/docs/5.1/forms/form-control/  
**Type:** Framework documentation  
**Estimated Tests:** 50-70  
**Forms:** Text, email, number, select, checkbox  
**Complexity:** ⭐⭐⭐ Medium  

---

## Set 3: More Complex (Moderate Challenge)

### 7. **jQuery Form Validation**
**URL:** https://jqueryvalidation.org/  
**Type:** Validation framework demo  
**Estimated Tests:** 60-80  
**Forms:** Complex validation rules  
**Complexity:** ⭐⭐⭐⭐ Complex  

### 8. **Zendesk Contact Form**
**URL:** https://support.zendesk.com/hc/en-us/  
**Type:** Support portal  
**Estimated Tests:** 70-100  
**Forms:** Search, filter, contact  
**Complexity:** ⭐⭐⭐⭐ Complex  

### 9. **GitHub Sign Up**
**URL:** https://github.com/signup  
**Type:** Real-world signup  
**Estimated Tests:** 80-120  
**Forms:** Username, email, password, verification  
**Complexity:** ⭐⭐⭐⭐ Complex  

---

## Set 4: Light Websites (Recommended for Quick Testing)

### 10. **MDN HTML Forms**
**URL:** https://developer.mozilla.org/en-US/docs/Learn/Forms  
**Type:** Educational  
**Estimated Tests:** 30-50  
**Forms:** Multiple demo forms  
**Complexity:** ⭐⭐ Easy  
**⭐ RECOMMENDED:** Fast crawl, good form variety

### 11. **CSS Tricks Form Examples**
**URL:** https://css-tricks.com/form/  
**Type:** Blog examples  
**Estimated Tests:** 25-45  
**Forms:** Styled form components  
**Complexity:** ⭐⭐ Easy  
**⭐ RECOMMENDED:** Forms-only site, focused testing

### 12. **HTML Dog Forms**
**URL:** https://www.htmldog.com/guides/html/intermediate/forms/  
**Type:** Tutorial site  
**Estimated Tests:** 20-40  
**Forms:** Learn-by-example forms  
**Complexity:** ⭐⭐ Easy  
**⭐ RECOMMENDED:** Clean, simple HTML

---

## 🚀 Quick Start: Recommended Combination

**For FASTEST results (15-20 min per site), use:**

1. **https://www.w3schools.com/tags/tryit.asp?filename=tryhtml_form_submit** ← Medium, balanced
2. **https://css-tricks.com/form/** ← Easy, focused on forms
3. **https://developer.mozilla.org/en-US/docs/Learn/Forms** ← Educational, variety

**Total Estimated Tests:** ~100-135 tests combined  
**Expected Duration:** 45-60 min (3 sites × 15-20 min each)

---

## How to Test Each Website

1. **Crawl the website:**
   - In Streamlit, go to "🕸️ Crawl" tab
   - Paste URL
   - Set max pages to 5-10
   - Click "Start Crawl"

2. **Generate tests:**
   - Go to "🧪 Test Cases" tab
   - Select the crawl
   - Generate tests

3. **Execute tests:**
   - Go to "🚀 Execute Tests" tab
   - Set time limit to 15 minutes
   - API budget 10-15 calls
   - Set RL Mode: ON
   - Click "Run Tests"

4. **Collect reports:**
   - Copy results from console
   - Check log files:
     - `data/heuristics_logs/heuristics_analysis.txt`
     - `data/rl_optimizations/optimization_report.txt`
   - Fill into CRAWL_REPORT_TEMPLATE.md

---

## 📝 Report Template Fields to Fill

For each website, capture:
- **Crawl Results:** Pages, Forms, Fields, States
- **Test Distribution:** BVA, ECP, Decision Table, State Transition, Use Case counts
- **Execution Results:** Passed, Failed, Errors, Pass %, LLM calls, Cost, Duration
- **Heuristics Changes:** Before/after risk scores for all 6 factors
- **Reasoning:** What did RL agent learn?

---

## ⚠️ Note on Large Websites

These recommended sites are intentionally **small** to:
- ✅ Crawl quickly (< 10 min)
- ✅ Generate small test sets (20-100 tests)
- ✅ Execute fast (< 20 min)
- ✅ Complete in 1 hour total

If you pick large e-commerce or complex apps, crawl will take 30+ min and tests may timeout.

---

**Pick any 3 from the lists above and let me know when you're ready to run!**
