# 🚀 Crawler Optimization TODO

**Status**: Deferred for later optimization  
**Priority**: Medium (focus is on test case generation first)  
**Last Updated**: November 28, 2025

---

## 📊 Current State Analysis

### **Problem Identified:**
The crawler is making **excessive AI API calls**, causing:
- ❌ **247 API calls** in a single crawl session
- ❌ All API keys hitting rate limits simultaneously
- ❌ Quota exhausted errors after ~240 calls
- ❌ Slower crawl times (AI waiting for rate limit resets)
- ❌ Incomplete crawls when rate limits hit

### **Root Cause:**
AI is being called for **every single interaction**, including:
1. Every button click on the same page
2. Every table row click (same form repeated)
3. Every component state change (even when DOM is identical)
4. Every navigation link verification

**Example Waste:**
```
/webtables page: Made 17 AI calls
- Call #229: Row 1 clicked → Found 3 inputs, 0 forms
- Call #230: Row 2 clicked → Found 3 inputs, 0 forms (DUPLICATE!)
- Call #231: Row 3 clicked → Found 3 inputs, 0 forms (DUPLICATE!)
... 14 more identical calls!
```

---

## 🎯 Proposed Optimizations

### **1. Smart AI Call Caching** (90% reduction in API calls)

**Goal**: Only call AI when page DOM actually changes

**Implementation**:
```python
class SmartAICache:
    def __init__(self):
        self.dom_hash_cache = {}  # {dom_hash: ai_result}
        self.url_state_cache = {}  # {url+state_hash: ai_result}
    
    def get_page_hash(self, page) -> str:
        """Generate hash of page's interactive elements"""
        forms = page.query_selector_all('form')
        inputs = page.query_selector_all('input, textarea, select')
        buttons = page.query_selector_all('button, [role="button"]')
        
        hash_data = {
            'forms': len(forms),
            'inputs': len(inputs),
            'buttons': len(buttons),
            'form_ids': [f.get_attribute('id') for f in forms],
            'input_names': [i.get_attribute('name') for i in inputs]
        }
        
        return hashlib.md5(json.dumps(hash_data, sort_keys=True).encode()).hexdigest()
    
    def should_call_ai(self, page, url: str) -> bool:
        """Check if AI call needed or use cache"""
        page_hash = self.get_page_hash(page)
        cache_key = f"{url}:{page_hash}"
        
        return cache_key not in self.url_state_cache
```

**Expected Results**:
- ✅ 247 calls → ~20 calls (92% reduction)
- ✅ No rate limit errors
- ✅ Same accuracy (caching only identical pages)
- ✅ 50% faster crawling

---

### **2. Selective AI Usage Policy**

**Goal**: Only use AI when traditional detection fails

**Strategy**:
```python
def should_use_ai_for_page(page, is_homepage: bool) -> bool:
    # Always use AI for homepage
    if is_homepage:
        return True
    
    # Use traditional detection first
    traditional_forms = detect_forms_traditional(page)
    
    # Only use AI if traditional found < 2 forms
    if len(traditional_forms) < 2:
        return True
    
    # Use AI for every 5th page (sampling)
    if page_count % 5 == 0:
        return True
    
    return False
```

**Expected Results**:
- ✅ AI used only when needed
- ✅ Traditional detection sufficient for 70% of pages
- ✅ Maintains accuracy for complex pages

---

### **3. Rate Limiting Per Key**

**Goal**: Enforce Gemini free tier limits (15 RPM per key)

**Implementation**:
```python
class RateLimitedAIDetector:
    def __init__(self):
        self.key_request_times = defaultdict(list)
        self.requests_per_minute = 10  # Conservative (vs 15 limit)
        self.min_delay_between_requests = 5  # seconds
    
    def enforce_rate_limit(self):
        current_time = time.time()
        
        # Remove requests older than 60s
        self.key_request_times[current_key] = [
            t for t in self.key_request_times[current_key]
            if current_time - t < 60
        ]
        
        # Wait if approaching limit
        if len(self.key_request_times[current_key]) >= 10:
            wait_time = 60 - (current_time - oldest_request)
            logger.info(f"⏳ Rate limit reached, waiting {wait_time}s")
            time.sleep(wait_time + 1)
        
        # Enforce minimum delay
        if last_request:
            time_since_last = current_time - last_request
            if time_since_last < 5:
                time.sleep(5 - time_since_last)
```

**Expected Results**:
- ✅ No sudden quota exhaustion
- ✅ Automatic pacing across keys
- ✅ Predictable crawl times

---

### **4. Alternative: Free Hosted AI Platforms**

**Goal**: Replace Gemini with unlimited/higher-limit alternatives

#### **Option A: Groq (RECOMMENDED)** ⭐
- **Free tier**: 14,400 requests/day
- **No rate limits** between requests
- **Faster than Gemini**
- **Setup**: Just API key (no credit card)

```python
from groq import Groq

class GroqDetector:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.2-90b-vision-preview"
    
    def detect_forms(self, screenshot_path: str):
        with open(screenshot_path, "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode()
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": "Find forms in this screenshot"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }]
        )
        return parse_forms(response)
```

**Get API Key**: https://console.groq.com/keys

#### **Option B: HuggingFace Inference API**
- **Free tier**: 1,000 requests/day
- **Many vision models**: BLIP, LLaVA, etc.
- **Setup**: Free token (no credit card)

**Get Token**: https://huggingface.co/settings/tokens

#### **Option C: Replicate**
- **Free credits**: $10/month (auto-renews)
- **Many models**: Salesforce BLIP-2, Meta LLaVA
- **Setup**: Sign up (no credit card initially)

**Sign up**: https://replicate.com/

---

### **5. Configuration-Based AI Control**

**Goal**: Make AI usage configurable via environment variables

**New Environment Variables**:
```env
# AI Usage Policy
AI_USAGE_POLICY=selective  # always|selective|minimal|disabled
AI_MAX_CALLS_PER_CRAWL=50
AI_MIN_DELAY_SECONDS=5
AI_REQUESTS_PER_MINUTE=10

# Smart Caching
AI_ENABLE_SMART_CACHE=true
AI_CACHE_EXPIRY_HOURS=24

# Fallback Behavior
AI_FALLBACK_TO_TRADITIONAL=true
AI_FAIL_ON_RATE_LIMIT=false
```

---

## 📈 Expected Impact

### **Before Optimization:**
| Metric | Value |
|--------|-------|
| API Calls per Crawl | 247 |
| Rate Limit Hits | 100% of keys |
| Failed Crawls | ~30% |
| Crawl Time | 4-6 minutes |
| Coverage | 85% (incomplete due to rate limits) |

### **After Optimization:**
| Metric | Value | Improvement |
|--------|-------|-------------|
| API Calls per Crawl | ~20 | **92% reduction** ✅ |
| Rate Limit Hits | 0% | **No rate limits** ✅ |
| Failed Crawls | 0% | **100% success** ✅ |
| Crawl Time | 2-3 minutes | **50% faster** ✅ |
| Coverage | 100% | **Complete crawls** ✅ |

---

## 🛠️ Implementation Plan (For Later)

### **Phase 1: Quick Wins** (2-3 hours)
1. ✅ Add smart AI caching
2. ✅ Implement rate limiting per key
3. ✅ Add configuration options
4. ✅ Test with DemoQA

### **Phase 2: Alternative AI** (1-2 hours)
1. ✅ Integrate Groq API
2. ✅ Add fallback logic (Groq → Gemini → Traditional)
3. ✅ Test vision model accuracy
4. ✅ Document API key setup

### **Phase 3: Optimization** (1 hour)
1. ✅ Implement selective AI usage
2. ✅ Add AI call metrics/reporting
3. ✅ Create AI usage dashboard in Streamlit

---

## 📝 Files to Modify

1. **`crawler/ai_detector.py`**
   - Add `SmartAICache` class
   - Add rate limiting logic
   - Add Groq integration

2. **`crawler/dom_analyzer.py`**
   - Add selective AI usage logic
   - Implement traditional-first strategy

3. **`crawler/orchestrator.py`**
   - Add AI usage tracking
   - Add configuration loading

4. **`.env`**
   - Add new AI configuration variables

5. **`requirements.txt`**
   - Add `groq` package (optional)
   - Add `huggingface_hub` (optional)

---

## 🔍 Testing Checklist

Before deploying optimizations:

- [ ] Test with DemoQA (complex site)
- [ ] Test with simple form site
- [ ] Test with SPA (React/Vue)
- [ ] Verify no forms/buttons missed
- [ ] Verify cache hit rate > 80%
- [ ] Verify no rate limit errors
- [ ] Verify crawl completes 100%
- [ ] Compare results before/after (should be identical)

---

## 📚 Related Documentation

- [Gemini API Rate Limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- [Groq API Documentation](https://console.groq.com/docs)
- [HuggingFace Inference API](https://huggingface.co/docs/api-inference)
- [Crawler Architecture](./ENHANCED_PRD_v2.md)

---

## 💡 Alternative Solutions (If Optimizations Don't Work)

### **Plan B: Disable AI Detection Entirely**
```env
AI_PROVIDER=disabled
USE_AI_DETECTION=false
```

**Impact**:
- ✅ No rate limits
- ✅ Fast crawling
- ❌ May miss 10-15% of non-semantic forms
- ❌ Less accurate on modern SPAs

### **Plan C: Manual Form Labeling**
Instead of AI detection, use a config file to specify forms:
```yaml
# site_forms.yaml
forms:
  - url: /login
    fields: [username, password]
  - url: /register
    fields: [email, password, confirm_password]
```

---

## 🎓 Lessons Learned

1. **AI is powerful but expensive** - Use sparingly
2. **Cache aggressively** - Most pages don't change
3. **Traditional methods work** - AI should enhance, not replace
4. **Rate limits are real** - Plan for them from day 1
5. **Fallback strategies** - Always have plan B

---

## 🚦 Status: DEFERRED

**Reason**: Focus is on test case generation module  
**When to revisit**: After test generation is complete  
**Priority**: Medium (crawler works, just inefficient)

**Current workaround**: Use fewer pages (`max_pages=20`) to avoid rate limits

---

## 📧 Notes for Future Self

- The crawler **works correctly** - it's just inefficient
- Results are **accurate** - just too many API calls
- These optimizations are **pure performance improvements**
- No urgency - crawler can be used as-is for test generation research
- Implement these when scaling to larger sites (100+ pages)

---

**Last Review**: November 28, 2025  
**Next Review**: After test case generation module is complete
