"""AI-Powered Element Detection using Ollama"""
from typing import List, Dict, Optional
import base64
import json
import re
from pathlib import Path
from app.utils.logger_config import setup_logger
import asyncio
import time
import requests

logger = setup_logger(__name__)


class OllamaElementDetector:
    """Use Ollama to detect clickable navigation elements"""
    
    def __init__(self, host: str, vision_model: str):
        """
        Initialize Ollama detector
        
        Args:
            host: Ollama server URL (e.g., http://localhost:11434)
            vision_model: Vision model name (e.g., llava:13b)
        """
        self.host = host.rstrip('/')
        self.vision_model = vision_model
        
        # Cache for detected elements (avoid repeated API calls)
        self._detection_cache = {}
        self._api_call_count = 0
        self._cache_hits = 0
        
        logger.info(f"🤖 Ollama element detector initialized (host: {host}, model: {vision_model})")
    
    async def detect_navigation_cards(
        self, 
        screenshot_path: str, 
        html_snippet: str = "", 
        page_url: str = ""
    ) -> List[Dict[str, str]]:
        """
        Detect navigation cards/tiles using Ollama vision model
        
        Args:
            screenshot_path: Path to screenshot image
            html_snippet: HTML context (optional)
            page_url: URL of the page (optional)
            
        Returns:
            List of detected elements with selectors
        """
        cache_key = f"{screenshot_path}:{hash(html_snippet[:500])}"
        
        if cache_key in self._detection_cache:
            self._cache_hits += 1
            logger.debug(f"✅ Cache hit! ({self._cache_hits} total hits)")
            return self._detection_cache[cache_key]
        
        prompt = self._build_detection_prompt(html_snippet, page_url)
        
        try:
            result = await self._analyze_screenshot(screenshot_path, prompt)
            elements = self._parse_detection_result(result)
            
            # Cache successful results
            if elements:
                self._detection_cache[cache_key] = elements
            
            self._api_call_count += 1
            logger.info(f"🔍 Detected {len(elements)} navigation elements (API calls: {self._api_call_count}, cache hits: {self._cache_hits})")
            
            return elements
            
        except Exception as e:
            logger.error(f"❌ Navigation detection failed: {e}")
            return []
    
    def _build_detection_prompt(self, html_snippet: str = "", page_url: str = "") -> str:
        """Build prompt for Ollama vision analysis"""
        prompt = """Analyze this webpage screenshot and identify ALL CLICKABLE NAVIGATION ELEMENTS.

Focus on:
1. Navigation Cards/Tiles - Large clickable boxes/panels with text and icons
2. Menu Items - Navigation links in headers, sidebars, footers
3. Buttons - Clickable buttons for navigation or actions
4. Links - Text links that navigate to other pages

For EACH element found, provide:
- text: The visible text on the element
- type: card|button|link|menu-item
- selector: A CSS selector to identify it (use classes, IDs, or descriptive attributes)
- confidence: Your confidence level (0-100)

Return ONLY a JSON array in this exact format:
[
  {
    "text": "Element text",
    "type": "card",
    "selector": ".navigation-card:nth-child(1)",
    "confidence": 95
  }
]

"""
        
        if html_snippet:
            prompt += f"\nHTML context (first 1000 chars):\n{html_snippet[:1000]}\n"
        
        if page_url:
            prompt += f"\nPage URL: {page_url}\n"
        
        prompt += "\nIMPORTANT: Return ONLY the JSON array, no other text."
        
        return prompt
    
    async def _analyze_screenshot(self, screenshot_path: str, prompt: str) -> str:
        """
        Send screenshot to Ollama for analysis
        
        Args:
            screenshot_path: Path to image file
            prompt: Analysis prompt
            
        Returns:
            Response text from Ollama
        """
        try:
            # Read and encode image
            with open(screenshot_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Prepare request for Ollama API
            payload = {
                "model": self.vision_model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Lower temperature for more consistent output
                    "num_predict": 2000  # Allow longer responses
                }
            }
            
            # Add ngrok bypass headers if using ngrok
            headers = {
                "Content-Type": "application/json"
            }
            if 'ngrok' in self.host:
                headers["ngrok-skip-browser-warning"] = "true"
                headers["User-Agent"] = "Mozilla/5.0"
            
            # Make request to Ollama
            logger.info(f"📤 Sending vision request to Ollama (this may take 2-5 minutes over ngrok)...")
            logger.debug(f"📤 Sending request to {self.host}/api/generate")
            
            start_time = time.time()
            response = await asyncio.to_thread(
                requests.post,
                f"{self.host}/api/generate",
                json=payload,
                headers=headers,
                timeout=300  # 5 minute timeout for vision models (can be slow over ngrok)
            )
            elapsed = time.time() - start_time
            logger.info(f"✅ Ollama responded in {elapsed:.1f}s")
            
            if response.status_code != 200:
                logger.error(f"❌ Ollama API error: {response.status_code} - {response.text}")
                return ""
            
            result = response.json()
            return result.get('response', '')
            
        except Exception as e:
            logger.error(f"❌ Screenshot analysis error: {e}")
            return ""
    
    def _parse_detection_result(self, text: str) -> List[Dict[str, str]]:
        """
        Parse Ollama response into list of elements
        
        Args:
            text: Raw response from Ollama
            
        Returns:
            List of element dictionaries
        """
        try:
            # Try to extract JSON array from response
            # Ollama might include extra text before/after JSON
            json_match = re.search(r'\[.*\]', text, re.DOTALL)
            
            if json_match:
                json_str = json_match.group()
                elements = json.loads(json_str)
                
                # Filter high confidence elements (>= 70%)
                filtered = []
                for elem in elements:
                    confidence = elem.get('confidence', 0)
                    if confidence >= 70:
                        # Ensure all required fields exist
                        if 'text' in elem and 'selector' in elem:
                            filtered.append({
                                'text': elem['text'],
                                'type': elem.get('type', 'link'),
                                'selector': elem['selector'],
                                'confidence': confidence
                            })
                
                return filtered
            else:
                logger.warning("⚠️  No JSON array found in Ollama response")
                return []
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse JSON from Ollama: {e}")
            logger.debug(f"Raw response: {text[:500]}")
            return []
        except Exception as e:
            logger.error(f"❌ Parsing error: {e}")
            return []
    
    def get_stats(self) -> Dict[str, int]:
        """Get detection statistics"""
        return {
            'api_calls': self._api_call_count,
            'cache_hits': self._cache_hits,
            'cached_pages': len(self._detection_cache)
        }
    
    def clear_cache(self):
        """Clear detection cache"""
        self._detection_cache.clear()
        logger.info("🗑️  Detection cache cleared")
