"""
Form Filler - AI-Powered Intelligent Form Handling
Discovers URLs through form interactions
"""
from typing import List, Dict, Set
from playwright.async_api import Page
from crawler.ai_client import UnifiedAIClient
from app.utils.logger_config import setup_logger
import asyncio

logger = setup_logger(__name__)


class FormFiller:
    """Handles form detection, filling, and multi-step flows"""
    
    def __init__(self, ai_client: UnifiedAIClient):
        self.ai = ai_client
        self.filled_forms: Set[str] = set()  # Track filled forms by signature
    
    async def discover_via_forms(
        self,
        page: Page,
        screenshot_path: str,
        current_url: str
    ) -> List[str]:
        """
        Discover new URLs by filling forms
        
        Args:
            page: Playwright page
            screenshot_path: Page screenshot
            current_url: Current URL
            
        Returns:
            List of newly discovered URLs
        """
        discovered_urls = []
        
        try:
            # Get HTML snippet
            html = await page.content()
            html_snippet = html[:5000]
            
            # Detect all forms
            logger.info("🔍 Detecting forms...")
            forms = await self.ai.detect_forms(screenshot_path, html_snippet)
            
            if not forms:
                logger.info("ℹ️  No forms found")
                return []
            
            logger.info(f"📋 Found {len(forms)} forms")
            
            for idx, form in enumerate(forms):
                form_sig = self._get_form_signature(form, current_url)
                
                if form_sig in self.filled_forms:
                    logger.info(f"⏭️  Form {idx+1} already filled")
                    continue
                
                logger.info(f"📝 Processing form {idx+1}: {form.get('purpose')}")
                
                # Handle based on type
                if form.get('is_multi_step'):
                    urls = await self._handle_multi_step_form(page, form, current_url)
                else:
                    urls = await self._handle_simple_form(page, form, current_url)
                
                discovered_urls.extend(urls)
                self.filled_forms.add(form_sig)
                
                # Return to original page
                await page.goto(current_url, wait_until='domcontentloaded', timeout=10000)
                await asyncio.sleep(1)
            
            logger.info(f"✅ Discovered {len(discovered_urls)} URLs via forms")
            return discovered_urls
            
        except Exception as e:
            logger.error(f"❌ Form discovery error: {e}")
            return []
    
    async def _handle_simple_form(
        self,
        page: Page,
        form: Dict,
        current_url: str
    ) -> List[str]:
        """Handle single-step form"""
        try:
            fields = form.get('fields', [])
            submit_sel = form.get('submit_selector')
            
            if not submit_sel:
                logger.warning("⚠️  No submit button")
                return []
            
            # Fill each field
            for field in fields:
                selector = field.get('selector')
                purpose = field.get('purpose')
                field_type = field.get('type')
                
                if not selector:
                    continue
                
                # Generate test data via AI
                value = await self.ai.generate_form_data(purpose, field_type)
                
                logger.info(f"  📝 {purpose}: {value}")
                
                # Fill field
                if field_type == 'select':
                    await page.select_option(selector, index=0)
                elif field_type == 'checkbox':
                    await page.check(selector)
                else:
                    await page.fill(selector, value)
                
                await asyncio.sleep(0.3)
            
            # Submit and capture new URL
            await page.click(submit_sel)
            await asyncio.sleep(2)
            
            new_url = page.url
            if new_url != current_url:
                logger.info(f"  ✅ New URL: {new_url}")
                return [new_url]
            
            return []
            
        except Exception as e:
            logger.error(f"❌ Simple form error: {e}")
            return []
    
    async def _handle_multi_step_form(
        self,
        page: Page,
        form: Dict,
        current_url: str
    ) -> List[str]:
        """Handle multi-step form (e.g., role selection → specific form)"""
        discovered_urls = []
        
        try:
            # Step 1: Identify options (e.g., radio buttons)
            options = await page.locator('input[type="radio"]').count()
            
            if options == 0:
                logger.info("  ℹ️  No multi-step options found")
                return await self._handle_simple_form(page, form, current_url)
            
            logger.info(f"  🔄 Multi-step form: {options} options")
            
            # Try each option
            for i in range(min(options, 3)):  # Limit to 3 options
                try:
                    # Return to form
                    await page.goto(current_url, wait_until='domcontentloaded', timeout=10000)
                    await asyncio.sleep(1)
                    
                    # Select option
                    radio = page.locator('input[type="radio"]').nth(i)
                    await radio.check()
                    await asyncio.sleep(0.5)
                    
                    # Submit selection
                    submit_sel = form.get('submit_selector')
                    if submit_sel:
                        await page.click(submit_sel)
                        await asyncio.sleep(2)
                    
                    # Fill subsequent form
                    new_url = page.url
                    if new_url != current_url:
                        logger.info(f"    ✅ Step {i+1} URL: {new_url}")
                        discovered_urls.append(new_url)
                    
                except Exception as e:
                    logger.warning(f"    ⚠️  Option {i+1} failed: {e}")
            
            return discovered_urls
            
        except Exception as e:
            logger.error(f"❌ Multi-step form error: {e}")
            return []
    
    def _get_form_signature(self, form: Dict, url: str) -> str:
        """Create unique signature for form"""
        purpose = form.get('purpose', 'unknown')
        selector = form.get('selector', '')
        field_count = len(form.get('fields', []))
        
        return f"{url}|{purpose}|{selector}|{field_count}"
    
    def reset_filled_forms(self):
        """Clear filled form tracking"""
        self.filled_forms.clear()
        logger.info("🔄 Filled forms reset")
    
    def get_stats(self) -> Dict:
        """Get form filling statistics"""
        return {
            'forms_filled': len(self.filled_forms)
        }
