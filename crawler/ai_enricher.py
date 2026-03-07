"""
AI Enricher
Uses Gemini API to detect non-semantic interactive elements
"""
import os
import json
import asyncio
from typing import Dict, List, Optional
from dotenv import load_dotenv
from app.utils.logger_config import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

# Try to import Gemini SDK
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed. AI enrichment disabled.")


class AIEnricher:
    """AI-powered semantic analysis using Gemini or Ollama"""
    
    def __init__(
        self,
        enabled: bool = True,
        max_dom_size: int = 5000,
        rate_limit_delay: float = 1.0,
        api_key: Optional[str] = None
    ):
        """
        Initialize AI enricher
        
        Args:
            enabled: Whether AI enrichment is enabled
            max_dom_size: Maximum DOM size to send to API (characters)
            rate_limit_delay: Delay between API calls (seconds)
            api_key: Gemini API key (defaults to GEMINI_API_KEY env var, ignored for Ollama)
        """
        self.enabled = enabled
        self.max_dom_size = max_dom_size
        self.rate_limit_delay = rate_limit_delay
        self.call_count = 0
        self.provider = None
        self.model = None
        
        if self.enabled:
            # Check which AI provider to use
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
                        logger.info(f"✅ Ollama AI enrichment enabled (host: {ollama_host}, model: {text_model})")
                    else:
                        logger.error(f"❌ Ollama connection failed: {response.status_code}")
                        self.enabled = False
                        
                except Exception as e:
                    logger.error(f"❌ Error connecting to Ollama: {e}")
                    self.enabled = False
                    
            elif ai_provider == 'gemini':
                # Use Gemini with key rotation
                if not GEMINI_AVAILABLE:
                    logger.warning("⚠️  AI_PROVIDER=gemini but google-generativeai not installed")
                    self.enabled = False
                else:
                    from crawler.gemini_key_rotator import GeminiKeyRotator
                    self.key_rotator = GeminiKeyRotator()
                    
                    current_key = self.key_rotator.get_current_key()
                    if not current_key:
                        logger.warning("⚠️  AI_PROVIDER=gemini but no API keys found")
                        self.enabled = False
                    else:
                        try:
                            genai.configure(api_key=current_key)
                            self.model = genai.GenerativeModel('gemini-2.0-flash')
                            self.provider = 'gemini'
                            logger.info(f"✅ Gemini AI enrichment enabled with {self.key_rotator.get_stats()['total_keys']} API keys (gemini-2.0-flash)")
                        except Exception as e:
                            logger.error(f"❌ Error configuring Gemini: {e}")
                            self.enabled = False
            else:
                logger.warning(f"⚠️  Unknown AI_PROVIDER: {ai_provider}")
                self.enabled = False
        else:
            logger.info("⚠️  AI enrichment disabled by configuration")
    
    async def enrich_page(self, page_html: str, url: str) -> Dict:
        """
        Send page DOM to Gemini for semantic analysis
        
        Args:
            page_html: HTML content of the page
            url: Page URL for context
        
        Returns:
            Dict with detected elements:
            {
                "page_type": "login|dashboard|product|generic",
                "forms": [...],
                "buttons": [...],
                "links": [...],
                "interactive_elements": [...]
            }
        """
        if not self.enabled:
            return self._empty_result()
        
        try:
            # Rate limiting
            if self.call_count > 0:
                await asyncio.sleep(self.rate_limit_delay)
            
            # Truncate HTML to max size
            truncated_html = page_html[:self.max_dom_size]
            
            # Build prompt
            prompt = self._build_analysis_prompt(truncated_html, url)
            
            # Call Gemini API
            logger.debug(f"🤖 Calling Gemini API for {url}")
            response = await self._call_gemini(prompt)
            
            self.call_count += 1
            
            # Parse response
            result = self._parse_response(response)
            
            logger.info(f"🤖 AI enrichment: Found {len(result.get('forms', []))} forms, "
                       f"{len(result.get('buttons', []))} buttons, "
                       f"{len(result.get('interactive_elements', []))} interactive elements")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in AI enrichment: {e}")
            return self._empty_result()
    
    def _build_analysis_prompt(self, html: str, url: str) -> str:
        """Build structured prompt for Gemini"""
        prompt = f"""You are a QA analyst analyzing a webpage's structure to identify interactive elements.

URL: {url}

HTML Snippet (first {len(html)} characters):
```html
{html}
```

Analyze this webpage and identify:
1. Interactive elements that behave like forms but may not use <form> tags
2. Clickable elements that act as buttons but use <div>, <span>, or other non-semantic tags
3. Logical groupings of input fields
4. The overall page type (login, dashboard, product listing, etc.)

Return ONLY valid JSON in this exact format (no markdown, no explanation):
{{
  "page_type": "login|dashboard|product|form|generic",
  "forms": [
    {{
      "inputs": [
        {{
          "type": "text|email|password|number|etc",
          "label": "User-visible label or inferred purpose",
          "identifier": "CSS selector or description"
        }}
      ],
      "submit_button": "CSS selector or description of submit element"
    }}
  ],
  "buttons": [
    {{
      "text": "Button text or inferred action",
      "selector": "CSS selector",
      "action": "submit|navigate|toggle|etc"
    }}
  ],
  "interactive_elements": [
    {{
      "type": "accordion|modal|dropdown|tab|etc",
      "identifier": "CSS selector or description",
      "purpose": "Brief description of what it does"
    }}
  ],
  "links": [
    {{
      "text": "Link text",
      "url": "href value",
      "purpose": "navigation|action"
    }}
  ]
}}

Be conservative - only identify elements you're confident about. If unsure, return empty arrays.
"""
        return prompt
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call AI API (Gemini or Ollama) with retry logic"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.provider == 'ollama':
                    # Call Ollama API
                    import requests
                    
                    payload = {
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": 0.3,
                            "num_predict": 3000
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
                    # Call Gemini API with key rotation
                    loop = asyncio.get_event_loop()
                    response = await loop.run_in_executor(
                        None,
                        lambda: self.model.generate_content(prompt)
                    )
                    return response.text
                
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if self.provider == 'gemini' and self.key_rotator.is_rate_limit_error(e):
                    # Try rotating to next API key
                    new_key = self.key_rotator.rotate_key(reason="rate_limit")
                    if new_key:
                        logger.info(f"🔄 Switching to next Gemini API key")
                        genai.configure(api_key=new_key)
                        self.model = genai.GenerativeModel('gemini-2.0-flash')
                        retry_count += 1
                        continue
                    
                    # No more keys, wait for retry delay
                    retry_delay = self.key_rotator.extract_retry_delay(error_str)
                    if retry_delay and retry_count < max_retries - 1:
                        logger.warning(f"⏳ All API keys rate limited. Waiting {retry_delay:.1f}s before retry...")
                        await asyncio.sleep(retry_delay)
                        self.key_rotator.reset()
                        genai.configure(api_key=self.key_rotator.get_current_key())
                        self.model = genai.GenerativeModel('gemini-2.0-flash')
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"❌ All API keys rate limited and max retries reached")
                        logger.error(f"API call failed: {e}")
                        raise
                else:
                    logger.error(f"API call failed: {e}")
                    raise
        
        raise Exception("Max retries reached")
    
    def _extract_retry_delay(self, error_message: str) -> Optional[float]:
        """Extract retry delay from Gemini error message"""
        try:
            import re
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
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parse Gemini JSON response"""
        try:
            # Remove markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith('```json'):
                cleaned = cleaned[7:]
            if cleaned.startswith('```'):
                cleaned = cleaned[3:]
            if cleaned.endswith('```'):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            result = json.loads(cleaned)
            
            return result
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {e}")
            logger.debug(f"Response was: {response_text[:200]}")
            return self._empty_result()
    
    def _empty_result(self) -> Dict:
        """Return empty result structure"""
        return {
            'page_type': 'generic',
            'forms': [],
            'buttons': [],
            'interactive_elements': [],
            'links': []
        }
    
    def get_stats(self) -> Dict:
        """Get AI enrichment statistics"""
        return {
            'enabled': self.enabled,
            'total_calls': self.call_count,
            'sdk_available': GEMINI_AVAILABLE
        }
