"""
AI-Powered Component Detector
Uses Gemini to intelligently detect interactive components, navigation, and generate realistic form data
"""
import os
import json
import re
import asyncio
from typing import List, Dict, Optional
from playwright.async_api import Page
import google.generativeai as genai
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class AIComponentDetector:
    """
    Uses AI (Gemini or Ollama) to detect components and generate intelligent crawling strategies
    """
    
    def __init__(self, enabled: bool = True):
        """
        Initialize AI component detector
        
        Args:
            enabled: Whether AI detection is enabled
        """
        self.enabled = enabled
        self.provider = None
        self.model = None
        
        if enabled:
            ai_provider = os.getenv('AI_PROVIDER', 'gemini').lower()
            
            if ai_provider == 'ollama':
                # Use Ollama
                try:
                    import requests
                    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
                    text_model = os.getenv('OLLAMA_TEXT_MODEL', 'codellama:13b')
                    
                    # Test connection
                    headers = {}
                    if 'ngrok' in ollama_host:
                        headers["ngrok-skip-browser-warning"] = "true"
                        headers["User-Agent"] = "Mozilla/5.0"
                    
                    response = requests.get(f"{ollama_host}/api/tags", headers=headers, timeout=10)
                    
                    if response.status_code == 200:
                        self.provider = 'ollama'
                        self.ollama_host = ollama_host
                        self.model = text_model
                        self.ollama_headers = headers
                        logger.info(f"✅ AI Component Detector enabled (Ollama: {text_model})")
                    else:
                        self.enabled = False
                        logger.error(f"❌ Ollama connection failed: {response.status_code}")
                        
                except Exception as e:
                    self.enabled = False
                    logger.error(f"❌ Error connecting to Ollama: {e}")
                    
            elif ai_provider == 'gemini':
                # Use Gemini with key rotation
                from crawler.gemini_key_rotator import GeminiKeyRotator
                self.key_rotator = GeminiKeyRotator()
                
                current_key = self.key_rotator.get_current_key()
                if current_key:
                    try:
                        genai.configure(api_key=current_key)
                        self.model = genai.GenerativeModel('gemini-1.5-flash')
                        self.provider = 'gemini'
                        logger.info(f"✅ AI Component Detector enabled with {self.key_rotator.get_stats()['total_keys']} Gemini API keys")
                    except Exception as e:
                        self.enabled = False
                        logger.error(f"❌ Error configuring Gemini: {e}")
                else:
                    self.enabled = False
                    logger.warning("⚠️  AI_PROVIDER=gemini but no API keys found")
            else:
                self.enabled = False
                logger.warning(f"⚠️  Unknown AI_PROVIDER: {ai_provider}")
        else:
            logger.info("AI Component Detector disabled")
    
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
    
    async def _call_ai(self, prompt: str) -> str:
        """
        Call AI provider (Gemini or Ollama) with retry logic
        
        Args:
            prompt: The prompt to send
            
        Returns:
            AI response text
        """
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.provider == 'ollama':
                    # Call Ollama
                    import requests
                    
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 2000
                        }
                    }
                    
                    response = await asyncio.to_thread(
                        requests.post,
                        f"{self.ollama_host}/api/generate",
                        json=payload,
                        headers=self.ollama_headers,
                        timeout=300  # 5 minute timeout for slow ngrok connections
                    )
                    
                    if response.status_code != 200:
                        raise Exception(f"Ollama API error: {response.status_code}")
                    
                    result = response.json()
                    return result.get('response', '')
                    
                else:
                    # Call Gemini with key rotation
                    response = await asyncio.to_thread(
                        self.model.generate_content,
                        prompt
                    )
                    return response.text
                    
            except Exception as e:
                error_str = str(e)
                
                # Handle rate limits with key rotation for Gemini
                if self.provider == 'gemini' and self.key_rotator.is_rate_limit_error(e):
                    new_key = self.key_rotator.rotate_key(reason="rate_limit")
                    if new_key:
                        logger.info(f"🔄 Switching to next Gemini API key")
                        genai.configure(api_key=new_key)
                        self.model = genai.GenerativeModel('gemini-1.5-flash')
                        retry_count += 1
                        continue
                    
                    # No more keys, wait
                    retry_delay = self.key_rotator.extract_retry_delay(error_str)
                    if retry_delay and retry_count < max_retries - 1:
                        logger.warning(f"⏳ All API keys rate limited. Waiting {retry_delay:.1f}s...")
                        await asyncio.sleep(retry_delay)
                        self.key_rotator.reset()
                        genai.configure(api_key=self.key_rotator.get_current_key())
                        self.model = genai.GenerativeModel('gemini-1.5-flash')
                        retry_count += 1
                        continue
                raise
        
        raise Exception("Max retries reached")
    
    async def detect_navigation_elements(self, page: Page) -> List[Dict]:
        """
        Use AI to detect ALL navigation elements including hidden ones
        
        Args:
            page: Playwright page object
        
        Returns:
            List of navigation element selectors and descriptions
        """
        if not self.enabled:
            return []
        
        try:
            # Get page HTML
            html = await page.content()
            
            # Limit size
            if len(html) > 15000:
                html = html[:15000] + "..."
            
            prompt = f"""
You are analyzing a web page to find ALL navigation elements. This includes:
- Links (<a> tags)
- Buttons that navigate
- Dropdown menus
- Accordions with nested navigation
- Sidebars with expandable items
- Tab navigation
- Breadcrumbs
- Any clickable element that leads to different content

HTML:
```html
{html}
```

Return a JSON array of navigation elements with this structure:
[
  {{
    "selector": "CSS selector to find element",
    "type": "link|button|dropdown|accordion|tab",
    "description": "What this element does",
    "needs_expand": true/false
  }}
]

Focus on elements that reveal MORE navigation when clicked/expanded.
Return ONLY valid JSON, no markdown.
"""
            
            # Call AI with retry logic
            response_text = await self._call_ai(prompt)
            
            if not response_text:
                return []
            
            # Parse response
            text = response_text.strip()
            
            # Remove markdown if present
            if text.startswith('```'):
                text = text.split('```')[1]
                if text.startswith('json'):
                    text = text[4:]
                text = text.strip()
            
            elements = json.loads(text)
            
            logger.info(f"🤖 AI detected {len(elements)} navigation elements")
            
            return elements
        
        except Exception as e:
            logger.error(f"AI navigation detection error: {e}")
            return []
    
    async def generate_form_data(self, page: Page, input_element: Dict) -> str:
        """
        Use AI to generate realistic, context-aware form data
        
        Args:
            page: Playwright page object
            input_element: Input element info (type, name, placeholder, label)
        
        Returns:
            Generated data value
        """
        if not self.enabled:
            return self._fallback_data(input_element)
        
        try:
            # Get context around input
            input_type = input_element.get('type', 'text')
            name = input_element.get('name', '')
            label = input_element.get('label', '')
            placeholder = input_element.get('placeholder', '')
            
            prompt = f"""
Generate realistic test data for this form field:
- Type: {input_type}
- Name: {name}
- Label: {label}
- Placeholder: {placeholder}

Requirements:
- Must be valid for the field type
- Should be realistic (real names, valid emails, etc.)
- For dates, use near-future dates (2024-2025)
- For phone, use format: +1234567890
- Keep it SHORT (under 50 characters)

Return ONLY the data value, no explanation.
"""
            
            # Call AI with retry logic
            response_text = await self._call_ai(prompt)
            
            if not response_text:
                return self._fallback_data(input_element)
            
            data = response_text.strip().strip('"\'')
            
            logger.debug(f"🤖 AI generated data for {name}: {data}")
            
            return data
        
        except Exception as e:
            logger.error(f"AI data generation error: {e}")
            return self._fallback_data(input_element)
    
    def _fallback_data(self, input_element: Dict) -> str:
        """
        Fallback data generation without AI
        
        Args:
            input_element: Input element info
        
        Returns:
            Fallback data value
        """
        input_type = input_element.get('type', 'text').lower()
        name = input_element.get('name', '').lower()
        
        # Smart fallbacks based on field name/type
        if input_type == 'email' or 'email' in name:
            return 'test@example.com'
        elif input_type == 'password' or 'password' in name:
            return 'Test@123456'
        elif input_type == 'tel' or 'phone' in name:
            return '+1234567890'
        elif input_type == 'url' or 'website' in name:
            return 'https://example.com'
        elif input_type == 'date' or 'date' in name:
            return '2024-12-31'
        elif input_type == 'time' or 'time' in name:
            return '14:30'
        elif input_type == 'number' or 'age' in name or 'amount' in name:
            return '42'
        elif input_type == 'color':
            return '#FF5733'
        elif 'name' in name:
            return 'Test User'
        elif 'address' in name:
            return '123 Main St, City, Country'
        else:
            return 'Test Value'
    
    async def detect_spa_components(self, page: Page) -> Dict:
        """
        Detect SPA framework and components
        
        Args:
            page: Playwright page object
        
        Returns:
            Dict with framework info and component structure
        """
        if not self.enabled:
            return {}
        
        try:
            # Detect framework
            js_code = """
            () => {
                const info = {
                    framework: 'unknown',
                    hasReact: !!window.React || !!document.querySelector('[data-reactroot]'),
                    hasVue: !!window.Vue || !!document.querySelector('[data-v-]'),
                    hasAngular: !!window.angular || !!window.ng || !!document.querySelector('[ng-version]'),
                    hasSvelte: !!document.querySelector('[class*="svelte"]'),
                };
                
                if (info.hasReact) info.framework = 'React';
                else if (info.hasVue) info.framework = 'Vue';
                else if (info.hasAngular) info.framework = 'Angular';
                else if (info.hasSvelte) info.framework = 'Svelte';
                
                return info;
            }
            """
            
            framework_info = await page.evaluate(js_code)
            
            logger.info(f"🤖 Detected framework: {framework_info.get('framework', 'Unknown')}")
            
            return framework_info
        
        except Exception as e:
            logger.error(f"SPA component detection error: {e}")
            return {}
