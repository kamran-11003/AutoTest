"""
Unified AI Client - Complete Intelligence for Web Crawling
Supports: Gemini (now) and Ollama (later)
"""
import os
from typing import Optional, List, Dict
from app.utils.logger_config import setup_logger
import base64
import json
import re
import asyncio

logger = setup_logger(__name__)


class UnifiedAIClient:
    """Complete AI interface for all crawling intelligence tasks"""
    
    def __init__(self):
        """Initialize AI client based on AI_PROVIDER in .env"""
        self.provider = os.getenv('AI_PROVIDER', 'gemini').lower()
        self.client = None
        self.model = None
        
        if self.provider == 'gemini':
            self._init_gemini()
        elif self.provider == 'ollama':
            self._init_ollama()
        else:
            raise ValueError(f"Unsupported AI_PROVIDER: {self.provider}")
    
    def _init_gemini(self):
        """Initialize Gemini"""
        try:
            import google.generativeai as genai
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found")
            
            genai.configure(api_key=api_key)
            self.client = genai
            self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
            
            logger.info("✅ Gemini AI initialized (gemini-3.1-flash-lite-preview)")
        except Exception as e:
            logger.error(f"❌ Gemini init failed: {e}")
            raise
    
    def _init_ollama(self):
        """Initialize Ollama"""
        try:
            import ollama
            
            # Get Ollama configuration from environment
            ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
            vision_model = os.getenv('OLLAMA_VISION_MODEL', 'llava:13b')
            text_model = os.getenv('OLLAMA_TEXT_MODEL', 'codellama:13b')
            
            # Configure Ollama client with host
            self.client = ollama.Client(host=ollama_host)
            
            # Test connection by listing models
            models = self.client.list()
            logger.info(f"✅ Ollama connected to {ollama_host}")
            logger.info(f"   Available models: {[m['name'] for m in models.get('models', [])]}")
            
            # Store models for different tasks
            self.vision_model = vision_model
            self.text_model = text_model
            self.model = vision_model  # Default to vision model
            
            logger.info(f"✅ Ollama AI initialized (Vision: {vision_model}, Text: {text_model})")
        except Exception as e:
            logger.error(f"❌ Ollama init failed: {e}")
            logger.error("   Check OLLAMA_HOST in .env")
            raise
    
    # ==================== NAVIGATION DETECTION ====================
    
    async def detect_navigation_elements(
        self, 
        screenshot_path: str, 
        html_snippet: str
    ) -> List[Dict]:
        """Detect ALL navigation elements on page"""
        prompt = f"""Analyze this webpage to find ALL NAVIGATION elements.

Types to detect:
1. Navigation Cards/Tiles - Large clickable boxes
2. Menu Items - Top/side navigation links  
3. Buttons - Navigation buttons
4. Tabs - Switch between sections

For EACH element provide JSON:
{{
  "text": "visible text",
  "type": "card|button|link|tab|menu-item",
  "selector": "CSS selector",
  "confidence": 0-100
}}

HTML context:
{html_snippet[:2000]}

Output JSON array: [...]"""
        
        response = await self._analyze_screenshot(screenshot_path, prompt)
        elements = self._extract_json_array(response)
        
        # Filter high confidence
        return [e for e in elements if e.get('confidence', 0) >= 70]
    
    # ==================== ACCORDION DETECTION ====================
    
    async def detect_accordions(self, screenshot_path: str, html_snippet: str) -> List[Dict]:
        """Detect collapsible/expandable sections"""
        prompt = f"""Find all ACCORDION/COLLAPSIBLE sections.

Look for:
- Sections with +/- icons
- Arrow indicators (▼ ▶)
- "Expand/Collapse" buttons
- FAQ-style sections

For each provide JSON:
{{
  "text": "section header",
  "selector": "CSS selector to click",
  "state": "collapsed|expanded",
  "confidence": 0-100
}}

HTML context:
{html_snippet[:2000]}

Output JSON array: [...]"""
        
        response = await self._analyze_screenshot(screenshot_path, prompt)
        return self._extract_json_array(response)
    
    # ==================== MODAL DETECTION ====================
    
    async def detect_modal_triggers(self, screenshot_path: str, html_snippet: str) -> List[Dict]:
        """Detect buttons/links that open modals"""
        prompt = f"""Identify elements that trigger MODAL DIALOGS.

Common triggers:
- "View Details", "More Info" links
- Settings/config icons
- Help buttons
- Image galleries

For each provide JSON:
{{
  "text": "button text",
  "selector": "CSS selector",
  "modal_type": "info|gallery|settings|other",
  "confidence": 0-100
}}

HTML context:
{html_snippet[:2000]}

Output JSON array: [...]"""
        
        response = await self._analyze_screenshot(screenshot_path, prompt)
        return self._extract_json_array(response)
    
    # ==================== FORM DETECTION ====================
    
    async def detect_forms(self, screenshot_path: str, html_snippet: str) -> List[Dict]:
        """Detect all forms and their fields"""
        prompt = f"""Identify all FORMS on this page.

For each form provide JSON:
{{
  "purpose": "search|login|register|contact|filter|other",
  "selector": "form CSS selector",
  "fields": [
    {{
      "selector": "input selector",
      "type": "text|email|password|select|checkbox",
      "purpose": "username|email|search|name|etc",
      "required": true/false
    }}
  ],
  "submit_selector": "button selector",
  "is_multi_step": true/false,
  "confidence": 0-100
}}

HTML context:
{html_snippet[:2000]}

Output JSON array: [...]"""
        
        response = await self._analyze_screenshot(screenshot_path, prompt)
        return self._extract_json_array(response)
    
    # ==================== LOGIN DETECTION ====================
    
    async def detect_login_page(self, screenshot_path: str, html_snippet: str) -> Dict:
        """Detect if page is login/authentication page"""
        prompt = f"""Is this a LOGIN/AUTHENTICATION page?

Look for:
- Username/email input
- Password input
- "Login", "Sign In" buttons

Provide JSON:
{{
  "is_login_page": true/false,
  "auth_type": "login|register|reset-password|none",
  "username_selector": "CSS selector or null",
  "password_selector": "CSS selector or null",
  "submit_selector": "CSS selector or null",
  "confidence": 0-100
}}

HTML context:
{html_snippet[:2000]}

Output JSON object: {{...}}"""
        
        response = await self._analyze_screenshot(screenshot_path, prompt)
        return self._extract_json_object(response)
    
    # ==================== LOGOUT DETECTION ====================
    
    async def is_logout_action(self, element_text: str, element_classes: str, element_href: str) -> bool:
        """Detect if element will trigger logout"""
        prompt = f"""Will clicking this LOG OUT the user?

Element:
- Text: "{element_text}"
- Classes: "{element_classes}"
- Href: "{element_href}"

Answer JSON:
{{
  "is_logout": true/false,
  "confidence": 0-100
}}

Output JSON: {{...}}"""
        
        response = await self._analyze_text(prompt)
        result = self._extract_json_object(response)
        return result.get('is_logout', False) and result.get('confidence', 0) >= 70
    
    # ==================== SEMANTIC DEDUPLICATION ====================
    
    async def find_semantic_duplicates(self, elements: List[Dict]) -> List[int]:
        """Find semantically duplicate elements, return indices to KEEP"""
        if len(elements) <= 1:
            return list(range(len(elements)))
        
        element_list = "\n".join([
            f"{i}: {elem.get('type', 'unknown')} - '{elem.get('text', '')[:50]}'"
            for i, elem in enumerate(elements)
        ])
        
        prompt = f"""Identify SEMANTIC DUPLICATES.

Elements:
{element_list}

Two are DUPLICATES if same action:
- "Login" and "Sign In" → DUPLICATE
- "Products" and "Shop" → DUPLICATE

NOT duplicates:
- "Products" and "Categories" → DIFFERENT
- "Login" and "Register" → DIFFERENT

Provide JSON array of UNIQUE indices to KEEP:
[0, 2, 5, ...]

Output JSON array: [...]"""
        
        response = await self._analyze_text(prompt)
        indices = self._extract_json_array(response)
        
        valid = [i for i in indices if isinstance(i, int) and 0 <= i < len(elements)]
        return valid if valid else list(range(len(elements)))
    
    # ==================== FORM DATA GENERATION ====================
    
    async def generate_form_data(self, field_purpose: str, field_type: str) -> str:
        """Generate test data for form field"""
        prompt = f"""Generate TEST DATA for:

Field purpose: {field_purpose}
Field type: {field_type}

Examples:
- email → test@example.com
- name → John Doe
- phone → +1234567890
- search → test query

Respond with ONLY the value."""
        
        response = await self._analyze_text(prompt)
        return response.strip().strip('"').strip("'")
    
    # ==================== HELPER METHODS ====================
    
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
    
    async def _analyze_screenshot(self, screenshot_path: str, prompt: str) -> str:
        """Analyze screenshot with AI (with automatic retry on rate limit)"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.provider == 'gemini':
                    import PIL.Image
                    image = PIL.Image.open(screenshot_path)
                    response = self.model.generate_content([prompt, image])
                    return response.text
                else:
                    # Ollama vision analysis
                    with open(screenshot_path, 'rb') as f:
                        image_data = base64.b64encode(f.read()).decode()
                    
                    # Use vision model for screenshot analysis
                    response = await asyncio.to_thread(
                        self.client.generate,
                        model=self.vision_model,
                        prompt=prompt,
                        images=[image_data],
                        options={'temperature': 0.3}  # Lower temperature for more consistent output
                    )
                    return response.get('response', '')
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if '429' in error_str or 'quota' in error_str.lower():
                    retry_delay = self._extract_retry_delay(error_str)
                    
                    if retry_delay and retry_count < max_retries - 1:
                        logger.warning(f"⏳ Rate limit hit. Waiting {retry_delay:.1f}s before retry {retry_count + 1}/{max_retries - 1}...")
                        await asyncio.sleep(retry_delay)
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"❌ Rate limit exceeded (no retry delay found or max retries reached)")
                        return ""
                else:
                    logger.error(f"❌ Screenshot analysis error: {e}")
                    return ""
        
        return ""
    
    async def _analyze_text(self, prompt: str) -> str:
        """Analyze text with AI (with automatic retry on rate limit)"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                if self.provider == 'gemini':
                    response = self.model.generate_content(prompt)
                    return response.text
                else:
                    # Use text model for text-only analysis
                    response = await asyncio.to_thread(
                        self.client.generate,
                        model=self.text_model,
                        prompt=prompt,
                        options={'temperature': 0.3}
                    )
                    return response.get('response', '')
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if '429' in error_str or 'quota' in error_str.lower():
                    retry_delay = self._extract_retry_delay(error_str)
                    
                    if retry_delay and retry_count < max_retries - 1:
                        logger.warning(f"⏳ Rate limit hit. Waiting {retry_delay:.1f}s before retry {retry_count + 1}/{max_retries - 1}...")
                        await asyncio.sleep(retry_delay)
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"❌ Rate limit exceeded (no retry delay found or max retries reached)")
                        return ""
                else:
                    logger.error(f"❌ Text analysis error: {e}")
                    return ""
        
        return ""
    
    def _extract_json_array(self, text: str) -> List:
        """Extract JSON array from text"""
        try:
            match = re.search(r'\[.*\]', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return []
        except:
            return []
    
    def _extract_json_object(self, text: str) -> Dict:
        """Extract JSON object from text"""
        try:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                return json.loads(match.group())
            return {}
        except:
            return {}
    
    def get_provider_info(self) -> Dict:
        """Get current provider info"""
        return {
            'provider': self.provider,
            'model': self.model if isinstance(self.model, str) else 'gemini-3.1-flash-lite-preview',
            'cost': 'Free tier (15 req/min)' if self.provider == 'gemini' else 'FREE (local)'
        }
