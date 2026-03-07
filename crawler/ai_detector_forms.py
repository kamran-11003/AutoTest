"""
AI-Powered Form Detection Extension
Adds form detection capabilities to GeminiElementDetector
"""
import json
import re
from typing import List, Dict
from pathlib import Path
import base64
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


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
```json
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
```

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
