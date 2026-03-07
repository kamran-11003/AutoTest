"""
Modal and Overlay Handler
Automatically detects and dismisses blocking modals/popups
"""
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class ModalHandler:
    """Handles modal dialogs and overlay popups"""
    
    def __init__(self):
        # Comprehensive list of selectors for e-commerce modals
        self.close_button_selectors = [
            # Generic close buttons
            'button.close', 'button.modal-close', '.close-button',
            '[aria-label*="close" i]', '[aria-label*="dismiss" i]',
            'button:has-text("Close")', 'button:has-text("×")',
            'button:has-text("Dismiss")', 'button:has-text("No thanks")',
            'button:has-text("No Thank You")', 'button:has-text("Maybe Later")',
            'button:has-text("Skip")', 'button:has-text("Continue Shopping")',
            
            # Cookie consent
            '.cookie-consent button', '#cookie-banner button',
            '[class*="cookie"] button', '[id*="cookie"] button',
            'button:has-text("Accept")', 'button:has-text("Accept All")',
            'button:has-text("I Understand")', 'button:has-text("Got it")',
            
            # Newsletter/Email signup popups
            '[class*="newsletter"] button[class*="close"]',
            '[class*="signup"] button[class*="close"]',
            '[id*="newsletter"] button[class*="close"]',
            '[class*="modal"] button:has-text("No thanks")',
            '[class*="popup"] button:has-text("No thanks")',
            'button:has-text("Continue without signing up")',
            
            # Country/Region selectors (like Allbirds popup)
            'button:has-text("Confirm")', 
            'button:has-text("Continue")',
            '[class*="country"] button:has-text("Confirm")',
            '[class*="region"] button:has-text("Confirm")',
            '[class*="location"] button:has-text("Confirm")',
            
            # Age verification
            'button:has-text("Yes")', 'button:has-text("Enter")',
            '[class*="age"] button:has-text("Yes")',
            
            # Promotional overlays (Anker-style)
            '[class*="promo"] button[class*="close"]',
            '[class*="offer"] button[class*="close"]',
            '[class*="discount"] button[class*="close"]',
            
            # Generic overlay close icons
            'button[class*="icon-close"]', 'button[class*="icon-x"]',
            'svg[class*="close"]', '[data-testid="close"]',
            '[data-dismiss="modal"]', '[data-close]'
        ]
    
    async def dismiss_modals(self, page: Page, aggressive: bool = True) -> int:
        """
        Dismiss any blocking modals/overlays
        
        Args:
            page: Playwright page object
            aggressive: If True, tries multiple rounds of dismissal
        
        Returns:
            Number of modals dismissed
        """
        dismissed_count = 0
        max_rounds = 3 if aggressive else 1  # Try multiple times for stubborn modals
        
        for round_num in range(max_rounds):
            round_dismissed = 0
            
            # Try each selector
            for selector in self.close_button_selectors:
                try:
                    # Check if modal close button exists and is visible
                    close_buttons = await page.query_selector_all(selector)
                    
                    for close_button in close_buttons:
                        try:
                            is_visible = await close_button.is_visible()
                            if is_visible:
                                await close_button.click(timeout=2000)
                                await page.wait_for_timeout(500)
                                round_dismissed += 1
                                logger.debug(f"✅ Dismissed modal: {selector}")
                        except Exception as e:
                            # Button might have disappeared or not clickable
                            logger.debug(f"Click failed for {selector}: {str(e)[:30]}")
                            continue
                            
                except Exception as e:
                    logger.debug(f"Query failed for {selector}: {str(e)[:30]}")
                    continue
            
            dismissed_count += round_dismissed
            
            # If nothing dismissed this round, stop trying
            if round_dismissed == 0:
                break
            
            # Wait between rounds for new modals to appear
            if round_num < max_rounds - 1:
                await page.wait_for_timeout(800)
        
        # Additional strategy: Press Escape key (closes many modals)
        try:
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(300)
        except:
            pass
        
        if dismissed_count > 0:
            logger.info(f"🚫 Dismissed {dismissed_count} modal(s)/overlay(s)")
        
        return dismissed_count
    
    async def handle_country_selector(self, page: Page) -> bool:
        """
        Specifically handle country/region selector modals
        Common in e-commerce sites like Allbirds, Shopify stores
        
        Returns:
            True if country selector was handled
        """
        try:
            # Look for country selector modal with "Confirm" or "Continue" button
            country_selectors = [
                'button:has-text("Confirm")',
                'button:has-text("Continue to")',
                'button:has-text("Shop")',
                '[class*="country"] button:has-text("Confirm")',
                '[class*="region"] button:has-text("Continue")',
            ]
            
            for selector in country_selectors:
                try:
                    button = await page.query_selector(selector)
                    if button and await button.is_visible():
                        await button.click(timeout=2000)
                        await page.wait_for_timeout(1000)
                        logger.info(f"🌍 Handled country selector modal")
                        return True
                except:
                    continue
            
            return False
        except Exception as e:
            logger.debug(f"Country selector handling failed: {e}")
            return False
    
    async def dismiss_all_popups(self, page: Page) -> int:
        """
        Comprehensive popup dismissal - tries modals, country selectors, and escape key
        Use this as the main entry point for popup handling
        
        Returns:
            Total number of popups handled
        """
        total_dismissed = 0
        
        # Step 1: Dismiss generic modals
        total_dismissed += await self.dismiss_modals(page, aggressive=True)
        
        # Step 2: Handle country/region selectors specifically
        if await self.handle_country_selector(page):
            total_dismissed += 1
        
        # Step 3: Final escape key press
        try:
            await page.keyboard.press('Escape')
            await page.wait_for_timeout(300)
        except:
            pass
        
        return total_dismissed
    
    async def detect_blocking_overlay(self, page: Page) -> bool:
        """Check if there's a blocking overlay on the page"""
        js_code = """
        () => {
            // Look for common overlay patterns
            const overlays = document.querySelectorAll('[class*="modal"], [class*="overlay"], [class*="popup"], [class*="dialog"]');
            
            for (const overlay of overlays) {
                const style = window.getComputedStyle(overlay);
                const rect = overlay.getBoundingClientRect();
                
                // Check if overlay is visible and covers significant page area
                const isVisible = style.display !== 'none' && 
                                 style.visibility !== 'hidden' &&
                                 style.opacity !== '0';
                
                const coversScreen = rect.width > window.innerWidth * 0.5 &&
                                    rect.height > window.innerHeight * 0.5;
                
                if (isVisible && coversScreen) {
                    return true;
                }
            }
            
            return false;
        }
        """
        
        try:
            has_overlay = await page.evaluate(js_code)
            return has_overlay
        except:
            return False
