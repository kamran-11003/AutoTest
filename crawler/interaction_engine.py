"""
Interaction Engine - AI-Powered Hidden Content Discovery
Handles accordions, modals, and expandable sections
"""
from typing import List, Dict, Set
from playwright.async_api import Page
from crawler.ai_client import UnifiedAIClient
from app.utils.logger_config import setup_logger
import asyncio

logger = setup_logger(__name__)


class InteractionEngine:
    """Discovers hidden content through interactions"""
    
    def __init__(self, ai_client: UnifiedAIClient):
        self.ai = ai_client
        self.expanded_elements: Set[str] = set()
    
    async def discover_via_interactions(
        self,
        page: Page,
        screenshot_path: str,
        current_url: str
    ) -> List[str]:
        """
        Discover URLs by expanding accordions and opening modals
        
        Returns:
            List of newly discovered URLs
        """
        discovered_urls = []
        
        try:
            html = await page.content()
            html_snippet = html[:5000]
            
            # Discover accordions
            logger.info("🔍 Detecting accordions...")
            accordion_urls = await self._handle_accordions(page, screenshot_path, html_snippet, current_url)
            discovered_urls.extend(accordion_urls)
            
            # Discover modals
            logger.info("🔍 Detecting modals...")
            modal_urls = await self._handle_modals(page, screenshot_path, html_snippet, current_url)
            discovered_urls.extend(modal_urls)
            
            logger.info(f"✅ Discovered {len(discovered_urls)} URLs via interactions")
            return discovered_urls
            
        except Exception as e:
            logger.error(f"❌ Interaction error: {e}")
            return []
    
    async def _handle_accordions(
        self,
        page: Page,
        screenshot_path: str,
        html_snippet: str,
        current_url: str
    ) -> List[str]:
        """Expand accordions and extract links"""
        discovered_urls = []
        
        try:
            accordions = await self.ai.detect_accordions(screenshot_path, html_snippet)
            
            if not accordions:
                logger.info("ℹ️  No accordions found")
                return []
            
            logger.info(f"📂 Found {len(accordions)} accordions")
            
            for idx, accordion in enumerate(accordions):
                if accordion.get('state') == 'expanded':
                    continue
                
                selector = accordion.get('selector')
                text = accordion.get('text', '')
                
                elem_sig = f"{current_url}|{selector}"
                if elem_sig in self.expanded_elements:
                    continue
                
                try:
                    logger.info(f"  📂 Expanding: {text}")
                    
                    # Click to expand
                    await page.click(selector, timeout=5000)
                    await asyncio.sleep(1)
                    
                    # Extract links from expanded content
                    links = await page.eval_on_selector_all(
                        'a[href]',
                        'elements => elements.map(e => e.href)'
                    )
                    
                    new_links = [l for l in links if l.startswith('http')]
                    logger.info(f"    ✅ Found {len(new_links)} links")
                    
                    discovered_urls.extend(new_links)
                    self.expanded_elements.add(elem_sig)
                    
                except Exception as e:
                    logger.warning(f"    ⚠️  Accordion {idx+1} failed: {e}")
            
            return discovered_urls
            
        except Exception as e:
            logger.error(f"❌ Accordion handling error: {e}")
            return []
    
    async def _handle_modals(
        self,
        page: Page,
        screenshot_path: str,
        html_snippet: str,
        current_url: str
    ) -> List[str]:
        """Open modals and extract links"""
        discovered_urls = []
        
        try:
            triggers = await self.ai.detect_modal_triggers(screenshot_path, html_snippet)
            
            if not triggers:
                logger.info("ℹ️  No modals found")
                return []
            
            logger.info(f"🔲 Found {len(triggers)} modal triggers")
            
            for idx, trigger in enumerate(triggers):
                selector = trigger.get('selector')
                text = trigger.get('text', '')
                
                elem_sig = f"{current_url}|{selector}"
                if elem_sig in self.expanded_elements:
                    continue
                
                try:
                    logger.info(f"  🔲 Opening modal: {text}")
                    
                    # Click trigger
                    await page.click(selector, timeout=5000)
                    await asyncio.sleep(1.5)
                    
                    # Extract links from modal
                    modal_selector = '[role="dialog"], .modal, [class*="modal"]'
                    modal = page.locator(modal_selector).first
                    
                    if await modal.count() > 0:
                        links = await modal.locator('a[href]').evaluate_all(
                            'elements => elements.map(e => e.href)'
                        )
                        
                        new_links = [l for l in links if l.startswith('http')]
                        logger.info(f"    ✅ Found {len(new_links)} links in modal")
                        
                        discovered_urls.extend(new_links)
                        
                        # Close modal (ESC key)
                        await page.keyboard.press('Escape')
                        await asyncio.sleep(0.5)
                    
                    self.expanded_elements.add(elem_sig)
                    
                except Exception as e:
                    logger.warning(f"    ⚠️  Modal {idx+1} failed: {e}")
                    # Try closing any open modal
                    await page.keyboard.press('Escape')
            
            return discovered_urls
            
        except Exception as e:
            logger.error(f"❌ Modal handling error: {e}")
            return []
    
    def reset_interactions(self):
        """Clear interaction tracking"""
        self.expanded_elements.clear()
        logger.info("🔄 Interactions reset")
    
    def get_stats(self) -> Dict:
        """Get interaction statistics"""
        return {
            'elements_expanded': len(self.expanded_elements)
        }
