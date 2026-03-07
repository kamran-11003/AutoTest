"""
Interaction Simulator
Simulates user interactions (clicks, form fills, hovers, etc.)
"""
import asyncio
from typing import Dict, Optional
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class InteractionSimulator:
    """Simulates user interactions to discover hidden content"""
    
    # Synthetic test data for form filling
    SYNTHETIC_DATA = {
        'text': 'TestUser123',
        'email': 'test@example.com',
        'password': 'Test@1234',
        'number': '12345',
        'tel': '+1234567890',
        'url': 'https://example.com',
        'date': '2024-01-01',
        'search': 'test query',
        'name': 'John Doe',
        'username': 'testuser',
        'firstName': 'John',
        'lastName': 'Doe'
    }
    
    def __init__(
        self,
        click_links: bool = True,
        submit_forms: bool = False,  # Dry-run by default for safety
        expand_accordions: bool = True,
        open_modals: bool = True,
        hover_menus: bool = True,
        timeout: int = 5000,
        state_manager = None
    ):
        """
        Initialize interaction simulator
        
        Args:
            click_links: Whether to click navigation links
            submit_forms: Whether to actually submit forms (DANGEROUS!)
            expand_accordions: Expand collapsed sections
            open_modals: Open modal dialogs
            hover_menus: Hover to reveal dropdown menus
            timeout: Timeout for each interaction (ms)
            state_manager: StateManager instance for session management
        """
        self.click_links = click_links
        self.submit_forms = submit_forms
        self.expand_accordions = expand_accordions
        self.open_modals = open_modals
        self.hover_menus = hover_menus
        self.timeout = timeout
        self.state_manager = state_manager
        
        logger.info(
            f"InteractionSimulator initialized "
            f"(submit_forms={submit_forms}, expand={expand_accordions})"
        )
    
    async def click_link(self, page: Page, selector: str) -> bool:
        """
        Click a link and wait for navigation
        
        Args:
            page: Playwright page
            selector: CSS selector for link
        
        Returns:
            True if navigation occurred
        """
        if not self.click_links:
            return False
        
        try:
            # Check if element exists and is visible
            element = await page.query_selector(selector)
            if not element:
                return False
            
            if not await element.is_visible():
                return False
            
            # Get href before clicking
            href = await element.get_attribute('href')
            if not href or href.startswith('#') or href.startswith('javascript:'):
                return False
            
            # Click and wait for navigation
            old_url = page.url
            await element.click(timeout=self.timeout)
            await page.wait_for_load_state('networkidle', timeout=self.timeout)
            
            new_url = page.url
            navigated = (new_url != old_url)
            
            if navigated:
                logger.debug(f"✅ Clicked link: {selector} -> {new_url}")
            
            return navigated
        
        except Exception as e:
            logger.debug(f"Error clicking link {selector}: {e}")
            return False
    
    async def fill_and_submit_form(self, page: Page, form_data: Dict) -> bool:
        """
        Fill form inputs and optionally submit
        
        Args:
            page: Playwright page
            form_data: Dict with input selectors and values
        
        Returns:
            True if form was submitted
        """
        try:
            # Check if this is a login form
            is_login_form = False
            current_url = page.url.lower()
            
            # Detect login forms by URL or form content
            if any(pattern in current_url for pattern in ['login', 'signin', 'sign-in', 'auth']):
                is_login_form = True
            else:
                # Check form inputs for login indicators
                for selector in form_data.keys():
                    selector_lower = selector.lower()
                    if any(term in selector_lower for term in ['username', 'password', 'email', 'login']):
                        is_login_form = True
                        break
            
            # Fill inputs
            for selector, value in form_data.items():
                try:
                    await page.fill(selector, str(value), timeout=self.timeout)
                    logger.debug(f"Filled {selector} = {value}")
                except Exception as e:
                    logger.debug(f"Could not fill {selector}: {e}")
            
            # Submit only if enabled (safety feature)
            if self.submit_forms:
                logger.warning("⚠️  Submitting form (dry-run mode disabled!)")
                submit_button = await page.query_selector(
                    'button[type="submit"], input[type="submit"]'
                )
                if submit_button:
                    old_url = page.url
                    await submit_button.click(timeout=self.timeout)
                    await page.wait_for_load_state('networkidle', timeout=self.timeout)
                    
                    new_url = page.url
                    submitted = (new_url != old_url)
                    
                    if submitted:
                        logger.info(f"✅ Form submitted: {old_url} -> {new_url}")
                        
                        # Mark authentication if login form was submitted successfully
                        if is_login_form and self.state_manager:
                            self.state_manager.mark_authenticated(f"login_form:{old_url}")
                    
                    return submitted
            else:
                logger.debug("✋ Form submission skipped (dry-run mode)")
                return False
        
        except Exception as e:
            logger.error(f"Error submitting form: {e}")
            return False
    
    async def expand_accordion(self, page: Page, selector: str) -> bool:
        """
        Expand an accordion/collapsible element
        
        Args:
            page: Playwright page
            selector: CSS selector for accordion trigger
        
        Returns:
            True if expansion occurred
        """
        if not self.expand_accordions:
            return False
        
        try:
            element = await page.query_selector(selector)
            if not element:
                return False
            
            # Check if already expanded
            aria_expanded = await element.get_attribute('aria-expanded')
            if aria_expanded == 'true':
                return False  # Already expanded
            
            # Click to expand
            await element.click(timeout=self.timeout)
            await asyncio.sleep(0.5)  # Wait for animation
            
            logger.debug(f"✅ Expanded accordion: {selector}")
            return True
        
        except Exception as e:
            logger.debug(f"Error expanding accordion {selector}: {e}")
            return False
    
    async def open_modal(self, page: Page, trigger_selector: str) -> bool:
        """
        Open a modal dialog
        
        Args:
            page: Playwright page
            trigger_selector: Selector for element that opens modal
        
        Returns:
            True if modal opened
        """
        if not self.open_modals:
            return False
        
        try:
            trigger = await page.query_selector(trigger_selector)
            if not trigger:
                return False
            
            await trigger.click(timeout=self.timeout)
            await asyncio.sleep(0.5)  # Wait for modal animation
            
            # Check if modal appeared
            modal = await page.query_selector('[role="dialog"], .modal, [aria-modal="true"]')
            if modal:
                logger.debug(f"✅ Opened modal: {trigger_selector}")
                return True
            
            return False
        
        except Exception as e:
            logger.debug(f"Error opening modal {trigger_selector}: {e}")
            return False
    
    async def hover_menu(self, page: Page, selector: str) -> bool:
        """
        Hover over element to reveal dropdown menu
        
        Args:
            page: Playwright page
            selector: Selector for hover target
        
        Returns:
            True if menu appeared
        """
        if not self.hover_menus:
            return False
        
        try:
            element = await page.query_selector(selector)
            if not element:
                return False
            
            await element.hover(timeout=self.timeout)
            await asyncio.sleep(0.5)  # Wait for menu animation
            
            logger.debug(f"✅ Hovered: {selector}")
            return True
        
        except Exception as e:
            logger.debug(f"Error hovering {selector}: {e}")
            return False
    
    async def discover_hidden_elements(self, page: Page) -> Dict:
        """
        Try to discover hidden elements by expanding accordions, hovering, etc.
        
        Args:
            page: Playwright page
        
        Returns:
            Dict with counts of discovered elements
        """
        discovered = {
            'accordions_expanded': 0,
            'modals_opened': 0,
            'menus_revealed': 0
        }
        
        try:
            # Find and expand accordions
            accordion_selectors = [
                '[aria-expanded="false"]',
                '.accordion-trigger',
                '.collapse-trigger',
                'details summary'
            ]
            
            for selector in accordion_selectors:
                elements = await page.query_selector_all(selector)
                for elem in elements[:5]:  # Limit to first 5
                    try:
                        if await self.expand_accordion(page, selector):
                            discovered['accordions_expanded'] += 1
                    except:
                        pass
            
            # Find and hover menu triggers
            menu_selectors = [
                '.dropdown-trigger',
                '[aria-haspopup="true"]',
                'nav > ul > li'
            ]
            
            for selector in menu_selectors:
                elements = await page.query_selector_all(selector)
                for elem in elements[:5]:  # Limit to first 5
                    try:
                        if await self.hover_menu(page, selector):
                            discovered['menus_revealed'] += 1
                    except:
                        pass
            
            logger.info(
                f"🔍 Hidden elements discovered: "
                f"{discovered['accordions_expanded']} accordions, "
                f"{discovered['menus_revealed']} menus"
            )
        
        except Exception as e:
            logger.error(f"Error discovering hidden elements: {e}")
        
        return discovered
    
    def get_synthetic_value(self, input_type: str, input_name: str) -> str:
        """
        Get synthetic test value for an input field
        
        Args:
            input_type: Input type (text, email, password, etc.)
            input_name: Input name attribute
        
        Returns:
            Synthetic value string
        """
        # Match by type
        if input_type in self.SYNTHETIC_DATA:
            return self.SYNTHETIC_DATA[input_type]
        
        # Match by name (case-insensitive)
        name_lower = input_name.lower()
        for key in self.SYNTHETIC_DATA:
            if key.lower() in name_lower:
                return self.SYNTHETIC_DATA[key]
        
        # Default
        return self.SYNTHETIC_DATA['text']
