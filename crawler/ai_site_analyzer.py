"""
AI-Powered Site Analysis
Analyzes site structure ONCE to detect patterns, reducing repeated Gemini calls
Uses Redis for distributed caching across multiple crawler instances
"""
import google.generativeai as genai
from typing import Dict, List, Optional, Set
import json
import re
import asyncio
from pathlib import Path
from app.utils.logger_config import setup_logger
from crawler.redis_cache import get_redis_cache

logger = setup_logger(__name__)

class AISiteAnalyzer:
    """
    Analyzes website structure using AI to detect:
    1. Navigation patterns (where navigation elements appear)
    2. URL normalization rules (which URLs are duplicate patterns)
    3. Component signatures (product cards, user cards, etc.)
    
    OPTIMIZATION: Calls Gemini ONCE per site, caches results for all pages
    """
    
    def __init__(self, key_rotator=None):
        """Initialize AI site analyzer with key rotation support"""
        from crawler.gemini_key_rotator import GeminiKeyRotator
        self.key_rotator = key_rotator or GeminiKeyRotator()
        
        current_key = self.key_rotator.get_current_key()
        if not current_key:
            raise ValueError("No Gemini API key available")
        
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        
        # Redis cache for persistent site analysis
        self.redis_cache = get_redis_cache()
        
        # In-memory cache (fallback + quick lookup)
        self._site_analysis_cache: Dict[str, Dict] = {}
        self._url_patterns_cache: Dict[str, List[Dict]] = {}
        
        logger.info("🧠 AI Site Analyzer initialized (pattern detection + URL normalization)")
        if self.redis_cache.enabled:
            logger.info("   💾 Redis caching enabled - site analysis persists across runs")
    
    async def analyze_site_structure(
        self, 
        homepage_html: str, 
        sample_urls: List[str],
        domain: str
    ) -> Dict:
        """
        Analyze site structure ONCE to detect global patterns
        
        Args:
            homepage_html: HTML content of homepage
            sample_urls: 10-20 sample URLs from site
            domain: Site domain (for caching)
        
        Returns:
            Site analysis dict with:
            - navigation_selectors: CSS selectors for navigation areas
            - url_patterns: Regex patterns for URL normalization
            - component_patterns: Common component structures
        """
        cache_key = f"site_analysis_{domain}"
        
        # Check Redis cache first (persistent across runs)
        redis_result = self.redis_cache.get('site_analysis', cache_key)
        if redis_result:
            logger.info(f"💾 Using cached site analysis for {domain} (from Redis)")
            self._site_analysis_cache[cache_key] = redis_result
            return redis_result
        
        # Check in-memory cache (faster, but not persistent)
        if cache_key in self._site_analysis_cache:
            logger.info(f"💾 Using cached site analysis for {domain} (from memory)")
            return self._site_analysis_cache[cache_key]
        
        logger.info(f"🔍 Analyzing site structure for {domain} (ONE-TIME analysis)")
        
        # Extract navigation structure from homepage
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(homepage_html, 'html.parser')
        
        # Find potential navigation containers
        nav_containers = []
        for tag in ['nav', 'header', 'aside']:
            for element in soup.find_all(tag):
                classes = element.get('class', [])
                nav_containers.append({
                    'tag': tag,
                    'classes': ' '.join(classes) if classes else '',
                    'id': element.get('id', ''),
                    'text_sample': element.get_text(strip=True)[:100]
                })
        
        # Sample HTML structure
        homepage_structure = str(soup.find('body'))[:3000] if soup.find('body') else homepage_html[:3000]
        
        # Build prompt for site-wide analysis
        prompt = f"""You are analyzing a website to detect REUSABLE PATTERNS that apply to ALL pages.

**DOMAIN**: {domain}

**SAMPLE URLS** (from crawling):
{chr(10).join([f"{i+1}. {url}" for i, url in enumerate(sample_urls[:20])])}

**HOMEPAGE STRUCTURE**:
```html
{homepage_structure}
```

**NAVIGATION CONTAINERS FOUND**:
{json.dumps(nav_containers, indent=2)}

**YOUR TASKS**:

### 1. NAVIGATION PATTERN DETECTION
Identify WHERE navigation elements appear consistently across pages:
- CSS selectors for sidebar navigation
- CSS selectors for top menu/navbar
- CSS selectors for category cards
- Common parent containers for links

### 2. URL NORMALIZATION RULES
Analyze the sample URLs and create regex patterns for:
- Dynamic IDs: /user/123, /product/456 → /user/:id, /product/:id
- UUIDs: /item/550e8400-e29b-41d4-a716-446655440000 → /item/:uuid
- Slugs: /blog/my-long-article-title-here → /blog/:slug (if length > 30)
- Date patterns: /2024/10/27/article → /:year/:month/:day/:slug
- Query params: ?id=123&sort=asc → ?id=:number&sort=:string

**CRITICAL**: Only create patterns for URLs that appear MULTIPLE times with different values.
Example: If you see /product/123, /product/456, /product/789 → create pattern
But if you see /about, /contact, /pricing (all unique) → NO pattern

### 3. COMPONENT SIGNATURES
Identify repeated component structures:
- Product cards (if e-commerce)
- User cards (if social)
- Blog post cards
- Navigation menu items
- Accordion sections

**OUTPUT FORMAT** (JSON only):
```json
{{
  "navigation": {{
    "sidebar_selector": "CSS selector for sidebar or null",
    "navbar_selector": "CSS selector for top navigation or null",
    "category_cards_selector": "CSS selector for homepage category tiles or null",
    "accordion_selector": "CSS selector for collapsible menus or null",
    "common_patterns": ["pattern 1", "pattern 2"]
  }},
  "url_normalization": [
    {{
      "pattern": "/user/\\\\d+",
      "replacement": "/user/:id",
      "confidence": 95,
      "reason": "Found /user/123, /user/456, /user/789"
    }},
    {{
      "pattern": "/[a-z0-9]{{24}}",
      "replacement": "/:objectid",
      "confidence": 90,
      "reason": "MongoDB IDs detected in product URLs"
    }}
  ],
  "components": {{
    "has_product_cards": false,
    "has_user_cards": false,
    "has_category_cards": true,
    "has_accordions": true,
    "card_selector": "div.card or similar"
  }},
  "insights": {{
    "site_type": "documentation|ecommerce|blog|dashboard|other",
    "navigation_style": "sidebar|topnav|both|minimal",
    "spa_framework": "react|vue|angular|none|unknown"
  }}
}}
```

**IMPORTANT**:
1. Be CONSERVATIVE with URL patterns - only add if you see 3+ examples
2. For navigation, prefer SPECIFIC selectors over generic ones
3. If uncertain, return null/empty rather than guessing
"""

        # Retry with key rotation on quota errors
        max_retries = len(self.key_rotator.api_keys)
        last_error = None
        
        for attempt in range(max_retries):
            try:
                response = await self.model.generate_content_async(prompt)
                result_text = response.text.strip()
                
                # Extract JSON
                json_start = result_text.find('{')
                json_end = result_text.rfind('}') + 1
                
                if json_start == -1 or json_end == 0:
                    logger.error("❌ AI site analysis failed: No JSON returned")
                    return self._get_fallback_analysis()
                
                analysis = json.loads(result_text[json_start:json_end])
                
                # Cache in BOTH Redis (persistent) and memory (fast)
                self._site_analysis_cache[cache_key] = analysis
                self.redis_cache.set('site_analysis', cache_key, analysis, ttl=604800)  # 7 days TTL
                
                logger.info(f"✅ Site analysis complete for {domain}")
                logger.info(f"   Navigation style: {analysis.get('insights', {}).get('navigation_style', 'unknown')}")
                logger.info(f"   URL patterns detected: {len(analysis.get('url_normalization', []))}")
                logger.info(f"   Component types: {list(analysis.get('components', {}).keys())}")
                logger.info(f"   📦 Cached in Redis (accessible across all crawler instances)")
                
                return analysis
            
            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Check for rate limit errors
                if "429" in error_str or "quota" in error_str or "rate" in error_str:
                    if attempt < max_retries - 1:  # Not the last attempt
                        old_key = self.key_rotator.current_key_info()['key']
                        new_key = self.key_rotator.rotate_key("rate_limit")
                        logger.warning(f"🔄 Key rotation (attempt {attempt + 1}/{max_retries}): ...{old_key[-8:]} → ...{new_key[-8:]}")
                        
                        # Reconfigure Gemini with new key
                        genai.configure(api_key=new_key)
                        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
                        
                        await asyncio.sleep(1)  # Brief pause before retry
                        continue
                    else:
                        logger.error(f"❌ All {max_retries} API keys exhausted")
                else:
                    # Non-rate-limit error, don't retry
                    break
        
        # All retries failed
        logger.error(f"❌ AI site analysis error after {max_retries} attempts: {last_error}")
        return self._get_fallback_analysis()
    
    def get_navigation_selectors(self, domain: str) -> Dict[str, str]:
        """
        Get cached navigation selectors for a domain
        
        Returns:
            Dict with sidebar_selector, navbar_selector, etc.
        """
        cache_key = f"site_analysis_{domain}"
        if cache_key in self._site_analysis_cache:
            return self._site_analysis_cache[cache_key].get('navigation', {})
        return {}
    
    def get_url_normalization_patterns(self, domain: str) -> List[Dict]:
        """
        Get cached URL normalization patterns for a domain
        
        Returns:
            List of pattern dicts with pattern, replacement, confidence
        """
        cache_key = f"site_analysis_{domain}"
        if cache_key in self._site_analysis_cache:
            return self._site_analysis_cache[cache_key].get('url_normalization', [])
        return []
    
    def normalize_url(self, url: str, domain: str) -> str:
        """
        Normalize URL using AI-detected patterns
        
        Args:
            url: URL to normalize
            domain: Site domain
        
        Returns:
            Normalized URL (e.g., /product/123 → /product/:id)
        """
        patterns = self.get_url_normalization_patterns(domain)
        
        normalized = url
        for pattern_dict in patterns:
            try:
                pattern = pattern_dict['pattern']
                replacement = pattern_dict['replacement']
                normalized = re.sub(pattern, replacement, normalized)
            except Exception as e:
                logger.debug(f"Pattern application error: {e}")
        
        return normalized
    
    def should_skip_page(self, url: str, domain: str, visited_normalized: Set[str]) -> bool:
        """
        Check if page should be skipped based on normalized URL
        
        Args:
            url: Current URL
            domain: Site domain
            visited_normalized: Set of already visited normalized URLs
        
        Returns:
            True if should skip (duplicate), False if should crawl
        """
        normalized = self.normalize_url(url, domain)
        
        if normalized in visited_normalized:
            logger.info(f"⏭️  Skipping duplicate: {url} → {normalized}")
            return True
        
        return False
    
    def _get_fallback_analysis(self) -> Dict:
        """Fallback analysis if AI fails"""
        return {
            "navigation": {
                "sidebar_selector": None,
                "navbar_selector": "nav, header",
                "category_cards_selector": None,
                "accordion_selector": "[role='button'][aria-expanded]",
                "common_patterns": []
            },
            "url_normalization": [
                {
                    "pattern": r"/\d+",
                    "replacement": "/:id",
                    "confidence": 80,
                    "reason": "Generic numeric ID pattern"
                }
            ],
            "components": {
                "has_product_cards": False,
                "has_user_cards": False,
                "has_category_cards": False,
                "has_accordions": False,
                "card_selector": None
            },
            "insights": {
                "site_type": "unknown",
                "navigation_style": "unknown",
                "spa_framework": "unknown"
            }
        }
    
    def get_cache_stats(self) -> Dict:
        """Get caching statistics"""
        redis_stats = self.redis_cache.get_stats()
        
        return {
            "sites_analyzed": len(self._site_analysis_cache),
            "memory_cache_hits": len(self._site_analysis_cache),
            "domains": list(self._site_analysis_cache.keys()),
            "redis": redis_stats
        }
