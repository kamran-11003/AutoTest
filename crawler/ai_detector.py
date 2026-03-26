"""AI-Powered Element Detection using Gemini Vision"""
import google.generativeai as genai
from typing import List, Dict, Optional
import base64
import json
import re
import hashlib
from pathlib import Path
from bs4 import BeautifulSoup
from app.utils.logger_config import setup_logger
import asyncio
import time
from crawler.gemini_key_rotator import GeminiKeyRotator
from crawler.redis_cache import get_redis_cache

logger = setup_logger(__name__)


class GeminiElementDetector:
    """Use Gemini to detect clickable navigation elements with automatic API key rotation"""
    
    def __init__(self, api_key: str = None, key_rotator: GeminiKeyRotator = None):
        """
        Initialize Gemini detector
        
        Args:
            api_key: Google Gemini API key (deprecated, use key_rotator instead)
            key_rotator: GeminiKeyRotator instance for automatic key rotation
        """
        # Use key rotator if provided, otherwise create new one
        self.key_rotator = key_rotator or GeminiKeyRotator()
        
        # Get initial API key
        current_key = api_key or self.key_rotator.get_current_key()
        if not current_key:
            raise ValueError("No Gemini API key available")
        
        genai.configure(api_key=current_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        self.current_key = current_key
        
        # Redis cache for distributed caching
        self.redis_cache = get_redis_cache()
        
        # In-memory cache (fallback + quick lookup)
        self._detection_cache = {}
        self._layout_cache = {}
        self._api_call_count = 0
        self._cache_hits = 0
        
        logger.info("🤖 Gemini element detector initialized (model: gemini-3.1-flash-lite-preview)")
        if self.redis_cache.enabled:
            logger.info("   💾 Redis caching enabled for distributed cache sharing")
    
    def _get_page_layout_signature(self, html_content: str) -> str:
        """
        Generate signature based on page layout structure
        Pages with same sidebar/navigation layout get same signature
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract structural elements (ignore content)
        signature_parts = []
        
        # Navigation structure
        nav_elements = soup.find_all(['nav', 'aside'])
        for nav in nav_elements[:3]:  # First 3 nav elements
            classes = ' '.join(nav.get('class', []))
            signature_parts.append(f"nav:{classes[:50]}")
        
        # Sidebar structure (common in DemoQA)
        sidebars = soup.find_all(class_=lambda x: x and 'side' in str(x).lower())
        for sidebar in sidebars[:2]:
            # Count child elements (structure, not content)
            child_count = len(sidebar.find_all(recursive=False))
            signature_parts.append(f"sidebar:{child_count}")
            
            # IMPORTANT: Include sidebar menu text to differentiate pages
            # This ensures /elements, /forms, /widgets get DIFFERENT cache keys
            menu_items = []
            for link in sidebar.find_all('a', recursive=True)[:10]:  # First 10 menu links
                text = link.get_text(strip=True)
                if text and len(text) < 50:
                    menu_items.append(text[:20])  # Truncate to 20 chars
            if menu_items:
                menu_hash = hashlib.md5('|'.join(menu_items).encode()).hexdigest()[:8]
                signature_parts.append(f"menu:{menu_hash}")
        
        # Accordion/menu structure
        accordions = soup.find_all(attrs={'role': 'button'})
        signature_parts.append(f"accordions:{len(accordions)}")
        
        # Main content area structure
        main = soup.find(['main', 'article']) or soup.find(id=lambda x: x and 'main' in str(x).lower())
        if main:
            signature_parts.append(f"main:{'form' if main.find('form') else 'content'}")
        
        return '|'.join(signature_parts) if signature_parts else 'generic'
    
    def _reconfigure_api(self, new_key: str):
        """Reconfigure Gemini API with new key"""
        genai.configure(api_key=new_key)
        self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
        self.current_key = new_key
    
    def _extract_retry_delay(self, error_message: str) -> Optional[float]:
        """Extract retry delay from Gemini error message"""
        try:
            # Look for "Please retry in X.XXXXs"
            match = re.search(r'Please retry in ([\d.]+)s', str(error_message))
            if match:
                delay = float(match.group(1))
                return delay
            
            # Look for retry_delay { seconds: X }
            match = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', str(error_message))
            if match:
                delay = float(match.group(1))
                return delay
            
            return None
        except:
            return None
    
    async def detect_navigation_cards(
        self, 
        screenshot_path: str, 
        html_content: str,
        page_url: str = ""
    ) -> List[Dict]:
        """
        Use Gemini to identify navigation cards/buttons on homepage
        
        Args:
            screenshot_path: Path to page screenshot
            html_content: Full HTML content of page
            page_url: Current page URL (for domain-specific caching)
            
        Returns:
            List of detected elements with selectors
        """
        # Extract domain from URL for cache key
        domain = ""
        if page_url:
            from urllib.parse import urlparse
            parsed = urlparse(page_url)
            domain = parsed.netloc or parsed.path.split('/')[0]
        
        # CACHING DISABLED - Always make fresh AI calls
        # Smart cache key: domain + layout structure
        # This prevents different sites with similar layouts from sharing cache
        layout_signature = self._get_page_layout_signature(html_content)
        cache_key = f"layout_{domain}_{layout_signature}" if domain else f"layout_{layout_signature}"
        
        # Skip cache - always call AI
        logger.debug(f"🔄 Cache disabled - making fresh AI call for {domain or 'unknown'}")
        
        ## Check Redis cache first (distributed, persistent) - DISABLED
        # redis_result = self.redis_cache.get('ai_navigation', cache_key)
        # if redis_result:
        #     self._cache_hits += 1
        #     self.redis_cache.increment('stats', 'cache_hits')
        #     logger.info(f"💾 Redis cache HIT! ({self._cache_hits} hits, saved {self._cache_hits} API calls)")
        #     logger.debug(f"   Reusing navigation from {domain or 'unknown'}: {layout_signature}")
        #     # Update in-memory cache for faster subsequent access
        #     self._layout_cache[cache_key] = redis_result
        #     return redis_result
        
        ## Check in-memory layout cache (faster, but not persistent) - DISABLED
        # if cache_key in self._layout_cache:
        #     self._cache_hits += 1
        #     logger.info(f"💾 Memory cache HIT! ({self._cache_hits} hits)")
        #     logger.debug(f"   Reusing navigation from layout: {layout_signature}")
        #     return self._layout_cache[cache_key]
        
        ## If layout not cached, check old heading-based cache (backward compatibility) - DISABLED
        # soup = BeautifulSoup(html_content, 'html.parser')
        # headings = [h.get_text(strip=True) for h in soup.find_all(['h1', 'h2'])[:3]]
        # old_cache_key = '_'.join(headings) if headings else screenshot_path
        
        # if old_cache_key in self._detection_cache:
        #     self._cache_hits += 1
        #     logger.info(f"💾 Heading cache HIT ({self._cache_hits} hits)")
        #     # Also cache by layout for future
        #     self._layout_cache[cache_key] = self._detection_cache[old_cache_key]
        #     self.redis_cache.set('ai_navigation', cache_key, self._detection_cache[old_cache_key])
        #     return self._detection_cache[old_cache_key]
        
        # Parse HTML for element extraction
        soup = BeautifulSoup(html_content, 'html.parser')
        
        try:
            self._api_call_count += 1
            logger.info(f"🤖 Sending screenshot to Gemini: {screenshot_path} (API call #{self._api_call_count})")
            
            # Read screenshot
            screenshot_file = Path(screenshot_path)
            if not screenshot_file.exists():
                logger.error(f"❌ Screenshot not found: {screenshot_path}")
                return []
            
            with open(screenshot_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Extract ALL potentially clickable elements (GENERIC approach)
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Find all potentially clickable/navigational elements (NO hardcoded classes!)
                potential_elements = []
                
                # 1. Links with text
                for link in soup.find_all('a', href=True):
                    text = link.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 100:
                        potential_elements.append(text)
                
                # 2. Buttons with text
                for button in soup.find_all('button'):
                    text = button.get_text(strip=True)
                    if text and len(text) > 2 and len(text) < 100:
                        potential_elements.append(text)
                
                # 3. Divs that are likely clickable (have onclick, role="button", or cursor:pointer)
                for div in soup.find_all('div'):
                    if div.get('onclick') or div.get('role') in ['button', 'link', 'tab'] or \
                       'clickable' in str(div.get('class', [])).lower():
                        text = div.get_text(strip=True)
                        # Avoid too much text (likely a container)
                        if text and len(text) > 2 and len(text) < 150:
                            potential_elements.append(text)
                
                # 4. Any element with heading tags (h1-h6) inside clickable parents
                for heading in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                    text = heading.get_text(strip=True)
                    if text and len(text) > 2:
                        potential_elements.append(text)
                
                # Remove duplicates while preserving order
                seen = set()
                card_texts = []
                for text in potential_elements:
                    if text not in seen and len(text) > 2:
                        seen.add(text)
                        card_texts.append(text[:100])
                
                # Limit to top 20 most likely navigation elements
                card_texts = card_texts[:20]
                
                logger.info(f"📋 Generic parser found {len(card_texts)} potential navigation elements")
                logger.debug(f"   Elements: {card_texts[:10]}...")  # Show first 10
                
            except Exception as e:
                logger.warning(f"⚠️  Generic parsing failed: {e}, using minimal fallback")
                # Minimal fallback: just find all links
                import re
                link_pattern = r'<a[^>]*>([^<]+)</a>'
                matches = re.findall(link_pattern, html_content, re.IGNORECASE)
                card_texts = [m.strip() for m in matches if m.strip() and len(m.strip()) > 2][:20]
            
            # Build enhanced HTML snippet
            html_snippet = f"""
POTENTIAL NAVIGATION ELEMENTS FOUND ({len(card_texts)} total):
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(card_texts)])}

RAW HTML (first 8000 chars):
{html_content[:8000]}
"""
            
            prompt = f"""
You are analyzing a webpage to find MAIN NAVIGATION elements.

**DETECTED ELEMENTS**: The HTML parser found {len(card_texts)} potential clickable elements.

**ELEMENTS FROM HTML**:
{chr(10).join([f"{i+1}. {text}" for i, text in enumerate(card_texts)])}

**YOUR TASK**: 
1. Look at the screenshot to identify which of these are MAIN NAVIGATION elements
2. MAIN NAVIGATION = elements that navigate to different sections/pages (cards, menu items, buttons, tabs)
3. IGNORE utility links (login, signup, social media, footer links, ads)

For each MAIN navigation element, provide JSON:
- **text**: The exact text from the list above
- **type**: "card" (for large tiles), "button", "link", "tab", or "menu-item"
- **selector**: Best CSS selector (use element type + nth-child, e.g., "div:nth-child(N)", "a:nth-child(N)")
- **confidence**: 85-100

**HTML CONTEXT**:
```
{html_snippet}
```

**GUIDELINES**:
- Focus on PRIMARY navigation (main categories/sections)
- If you see a banner/ad at top, look below it
- Return 5-15 main navigation elements (not all {len(card_texts)})

Output ONLY JSON array:
[
  {{"text": "...", "type": "card|button|link", "selector": "...", "confidence": 90}}
]
"""
            
            # Send to Gemini with retry logic and automatic key rotation
            logger.info("📤 Requesting Gemini analysis...")
            
            max_retries = 10  # More retries since we have multiple keys
            retry_count = 0
            result_text = None
            keys_tried = set()
            
            while retry_count < max_retries:
                try:
                    response = self.model.generate_content([
                        prompt,
                        {
                            'mime_type': 'image/png',
                            'data': image_data
                        }
                    ])
                    result_text = response.text.strip()
                    break  # Success, exit retry loop
                    
                except Exception as e:
                    error_str = str(e)
                    
                    # Check if key is suspended (permanent failure)
                    if self.key_rotator.is_suspended_error(e):
                        logger.error(f"❌ Current API key is SUSPENDED: {error_str[:200]}")
                        # Mark as suspended
                        self.key_rotator.mark_key_suspended(self.current_key)
                        
                        # Try next key
                        new_key = self.key_rotator.get_current_key()
                        if new_key and new_key != self.current_key:
                            logger.info(f"🔄 Switching to next valid API key")
                            self._reconfigure_api(new_key)
                            retry_count += 1
                            continue
                        else:
                            logger.error("❌ No valid API keys remaining (all suspended)")
                            raise
                    
                    # Check if it's a rate limit error (429)
                    elif self.key_rotator.is_rate_limit_error(e):
                        # Track which key hit the limit
                        keys_tried.add(self.current_key[-8:])
                        
                        # Extract retry delay
                        retry_delay = self.key_rotator.extract_retry_delay(error_str)
                        
                        # Try rotating to next API key
                        if len(keys_tried) < self.key_rotator.get_stats()['total_keys']:
                            new_key = self.key_rotator.rotate_key(reason="rate_limit")
                            if new_key and new_key != self.current_key:
                                logger.info(f"🔄 Switching to next API key (tried {len(keys_tried)}/{self.key_rotator.get_stats()['total_keys']} keys)")
                                self._reconfigure_api(new_key)
                                retry_count += 1
                                continue
                        
                        # All keys exhausted, wait for retry delay
                        if retry_delay and retry_count < max_retries - 1:
                            logger.warning(f"⏳ All {len(keys_tried)} API keys rate limited. Waiting {retry_delay:.1f}s before retry...")
                            await asyncio.sleep(retry_delay)
                            retry_count += 1
                            # Reset to first key after waiting
                            self.key_rotator.reset()
                            self._reconfigure_api(self.key_rotator.get_current_key())
                            keys_tried.clear()
                            continue
                        else:
                            logger.error(f"❌ All API keys rate limited and max retries reached")
                            raise
                    else:
                        # Non-rate-limit error, re-raise
                        raise
            
            if result_text is None:
                logger.error("❌ Failed to get response from Gemini after retries")
                return []
            
            # Reduced logging - only show in debug mode
            logger.debug("=" * 70)
            logger.debug("📥 GEMINI RAW RESPONSE:")
            logger.debug("-" * 70)
            logger.debug(result_text)
            logger.debug("-" * 70)
            logger.debug("=" * 70)
            
            # Parse response - extract JSON
            json_start = result_text.find('[')
            json_end = result_text.rfind(']') + 1
            
            if json_start == -1 or json_end == 0:
                logger.error("❌ Gemini returned no valid JSON")
                logger.debug(f"Raw response: {result_text}")
                return []
            
            json_str = result_text[json_start:json_end]
            elements = json.loads(json_str)
            
            if not isinstance(elements, list):
                logger.error("❌ Gemini response is not a list")
                return []
            
            logger.info(f"🤖 Gemini detected {len(elements)} navigation elements (confidence >= 70%)")
            
            # Filter and validate elements
            valid_elements = []
            filtered_out = []
            
            for elem in elements:
                if not isinstance(elem, dict):
                    filtered_out.append(f"Not a dict: {elem}")
                    continue
                
                text = elem.get('text', '').strip()
                selector = elem.get('selector', '').strip()
                confidence = elem.get('confidence', 0)
                
                if not text or not selector:
                    filtered_out.append(f"Missing text/selector: {elem}")
                    continue
                
                if confidence < 70:
                    filtered_out.append(f"Low confidence ({confidence}%): {text}")
                    continue
                
                valid_elements.append({
                    'text': text,
                    'type': elem.get('type', 'unknown'),
                    'selector': selector,
                    'confidence': confidence
                })
                
                # Only log in debug mode
                logger.debug(f"  ✅ {text} (confidence: {confidence}%, selector: {selector})")
            
            if filtered_out:
                logger.info(f"⚠️  Filtered out {len(filtered_out)} elements:")
                for reason in filtered_out:
                    logger.info(f"    - {reason}")
            
            logger.info(f"✅ {len(valid_elements)} high-confidence elements validated")
            
            ## Cache in BOTH Redis (persistent) and memory (fast) - DISABLED
            # self._detection_cache[old_cache_key] = valid_elements
            # self._layout_cache[cache_key] = valid_elements
            
            ## Store in Redis for distributed caching (24hr TTL) - DISABLED
            # self.redis_cache.set('ai_navigation', cache_key, valid_elements)
            # self.redis_cache.increment('stats', 'api_calls')
            
            logger.info(f"📦 Detected layout signature (caching disabled): {layout_signature[:80]}")
            logger.debug(f"   Caching disabled - fresh AI call every time")
            
            return valid_elements
        
        except json.JSONDecodeError as e:
            logger.error(f"❌ JSON parsing failed: {e}")
            logger.debug(f"Raw text: {result_text if 'result_text' in locals() else 'N/A'}")
            return []
        
        except Exception as e:
            logger.error(f"❌ Gemini detection failed: {e}", exc_info=True)
            return []
    
    def get_cache_stats(self) -> dict:
        """Get API usage and cache statistics"""
        return {
            'api_calls': self._api_call_count,
            'cache_hits': self._cache_hits,
            'cache_size': len(self._detection_cache),
            'hit_rate': (self._cache_hits / (self._api_call_count + self._cache_hits) * 100) if (self._api_call_count + self._cache_hits) > 0 else 0
        }
    
    async def verify_element_clickable(
        self,
        screenshot_path: str,
        element_text: str
    ) -> bool:
        """
        Ask Gemini if an element looks clickable
        
        Args:
            screenshot_path: Path to screenshot
            element_text: Text of element to verify
            
        Returns:
            True if element appears clickable
        """
        try:
            with open(screenshot_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            prompt = f"""
Look at the element labeled "{element_text}" in this screenshot.

Does it look clickable/interactive? Consider:
- Is it styled like a button/card?
- Does it have visible borders or shadows suggesting interactivity?
- Is it part of navigation?
- Does it look disabled/inactive?

Answer with ONLY: YES or NO
"""
            
            response = self.model.generate_content([
                prompt,
                {'mime_type': 'image/png', 'data': image_data}
            ])
            
            result = response.text.upper().strip()
            is_clickable = 'YES' in result
            
            logger.info(f"🤖 '{element_text}' clickable: {is_clickable}")
            return is_clickable
        
        except Exception as e:
            logger.error(f"❌ Clickability check failed: {e}")
            return False
    
    def supports_vision(self) -> bool:
        """Check if Gemini vision API is available"""
        return True
    
    async def detect_forms_vision(self, screenshot_path: str, html_content: str, page_url: str = "") -> List[Dict]:
        """
        Use Gemini Vision to detect forms on a page
        
        Detects:
        - Traditional HTML forms
        - React/Vue custom form components
        - Forms hidden in modals/tabs/accordions
        - Multi-step forms
        - Forms without <form> tags
        
        Args:
            screenshot_path: Path to page screenshot
            html_content: Full HTML content
            page_url: Current page URL
            
        Returns:
            List of detected forms with structure:
            [
                {
                    'selector': '#login-form',
                    'inputs': [
                        {'type': 'email', 'name': 'username', 'label': 'Email', ...},
                        {'type': 'password', 'name': 'password', 'label': 'Password', ...}
                    ],
                    'submit_button': 'Login',
                    'action': '/api/login',
                    'method': 'post'
                }
            ]
        """
        try:
            self._api_call_count += 1
            logger.info(f"🤖 Form detection: Analyzing screenshot with Gemini (API call #{self._api_call_count})")
            
            # Read screenshot
            screenshot_file = Path(screenshot_path)
            if not screenshot_file.exists():
                logger.error(f"❌ Screenshot not found: {screenshot_path}")
                return []
            
            with open(screenshot_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode()
            
            # Build prompt for form detection
            prompt = f"""
You are analyzing a webpage screenshot to detect ALL FORMS (login, registration, search, contact, etc.).

**TASK**: Identify every form on the page, including:
- Traditional HTML forms with <form> tags
- React/Vue/Angular custom form components (without <form> tags)
- Forms hidden in modals, tabs, or accordions
- Multi-step forms
- Search bars
- Login/registration forms
- Contact/feedback forms
- Filter forms
- Any group of input fields with a submit button

**FOR EACH FORM DETECTED**, provide:
1. **Form Purpose** (e.g., "Login Form", "Search Bar", "Contact Form")
2. **All Input Fields**:
   - Field type (text, email, password, select, textarea, checkbox, radio, date, etc.)
   - Field label (visible text near the input)
   - Placeholder text (if visible)
   - Field name/id (if you can infer from HTML below)
   - Whether it appears required (marked with * or "required")
3. **Submit Button Text** (e.g., "Login", "Search", "Submit", "Send")
4. **Visual Location** (e.g., "top-right header", "center modal", "sidebar")

**HTML CONTEXT** (for matching with DOM):
```html
{html_content[:10000]}
```

**RESPONSE FORMAT** (JSON only, no markdown):
{{
  "forms": [
    {{
      "purpose": "Login Form",
      "location": "center of page",
      "selector": "#login-form",
      "inputs": [
        {{
          "type": "email",
          "label": "Email Address",
          "placeholder": "Enter your email",
          "name": "email",
          "id": "email-input",
          "required": true
        }},
        {{
          "type": "password",
          "label": "Password",
          "placeholder": "Enter password",
          "name": "password",
          "id": "password-input",
          "required": true
        }}
      ],
      "submit_button": "Login",
      "action": "/api/login",
      "method": "post"
    }}
  ]
}}

**IMPORTANT**:
- Look carefully at the screenshot - forms may be styled differently than traditional HTML forms
- Include search bars (they are forms too!)
- If inputs are grouped visually but don't have labels, infer the purpose from placeholder text
- Return ONLY the JSON, no extra text
- If no forms are visible, return: {{"forms": []}}
"""
            
            # Call Gemini with retry logic
            max_retries = len(self.key_rotator.api_keys)
            for attempt in range(max_retries):
                try:
                    response = self.model.generate_content([
                        prompt,
                        {
                            'mime_type': 'image/png',
                            'data': image_data
                        }
                    ])
                    
                    # Parse response
                    response_text = response.text.strip()
                    logger.debug(f"Gemini response (first 500 chars): {response_text[:500]}")
                    
                    # Extract JSON from response
                    json_match = re.search(r'\{[\s\S]*"forms"[\s\S]*\}', response_text)
                    if json_match:
                        json_str = json_match.group(0)
                        result = json.loads(json_str)
                        forms = result.get('forms', [])
                        
                        logger.info(f"✅ AI Vision: Detected {len(forms)} forms")
                        for i, form in enumerate(forms, 1):
                            logger.debug(f"   Form {i}: {form.get('purpose')} - {len(form.get('inputs', []))} inputs")
                        
                        return forms
                    else:
                        logger.warning("⚠️  No JSON found in Gemini response")
                        return []
                        
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check for quota/rate limit errors
                    if any(keyword in error_msg for keyword in ['quota', 'rate limit', '429', 'resource_exhausted']):
                        logger.warning(f"⚠️  API key quota exceeded (attempt {attempt + 1}/{max_retries})")
                        
                        # Try next API key
                        new_key = self.key_rotator.rotate_key()
                        if new_key and new_key != self.current_key:
                            logger.info(f"🔄 Switching to next API key...")
                            self._reconfigure_api(new_key)
                            self.current_key = new_key
                            continue
                        else:
                            logger.error("❌ All API keys exhausted")
                            return []
                    else:
                        # Non-quota error
                        logger.error(f"❌ Gemini API error: {e}")
                        return []
            
            logger.error("❌ Failed to detect forms after all retry attempts")
            return []
            
        except Exception as e:
            logger.error(f"❌ Form detection failed: {e}")
            return []
