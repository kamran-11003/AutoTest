"""
Authentication Manager - AI-Powered Login & Session Handling
"""
from typing import Optional, Dict
from playwright.async_api import Page
from crawler.ai_client import UnifiedAIClient
from app.utils.logger_config import setup_logger
import asyncio

logger = setup_logger(__name__)


class AuthManager:
    """Handles authentication with AI login detection"""
    
    def __init__(self, ai_client: UnifiedAIClient, credentials: Optional[Dict] = None):
        """
        Args:
            ai_client: UnifiedAIClient instance
            credentials: {"username": "...", "password": "..."} or None
        """
        self.ai = ai_client
        self.credentials = credentials
        self.logged_in = False
        self.login_url = None
    
    async def detect_and_login(
        self, 
        page: Page, 
        screenshot_path: str,
        force: bool = False
    ) -> bool:
        """
        Detect if page requires login and auto-login if credentials provided
        
        Args:
            page: Playwright page
            screenshot_path: Path to current page screenshot
            force: Force login even if already logged in
            
        Returns:
            True if logged in (or login not needed), False if login failed
        """
        if self.logged_in and not force:
            logger.info("✅ Already logged in")
            return True
        
        if not self.credentials:
            logger.info("ℹ️  No credentials provided, skipping auth")
            return True
        
        try:
            # Get HTML snippet
            html = await page.content()
            html_snippet = html[:5000]
            
            # AI detection
            logger.info("🔍 Checking if login page...")
            detection = await self.ai.detect_login_page(screenshot_path, html_snippet)
            
            if not detection.get('is_login_page'):
                logger.info("✅ Not a login page")
                return True
            
            auth_type = detection.get('auth_type', 'login')
            confidence = detection.get('confidence', 0)
            
            logger.info(f"🔐 Login page detected ({auth_type}, {confidence}% confidence)")
            
            # Perform login
            if auth_type == 'login':
                success = await self._perform_login(page, detection)
                if success:
                    self.logged_in = True
                    self.login_url = page.url
                    logger.info("✅ Login successful!")
                return success
            else:
                logger.info(f"⚠️  Auth type '{auth_type}' not supported, skipping")
                return True
                
        except Exception as e:
            logger.error(f"❌ Auth error: {e}")
            return False
    
    async def _perform_login(self, page: Page, detection: Dict) -> bool:
        """Fill login form and submit"""
        try:
            username_sel = detection.get('username_selector')
            password_sel = detection.get('password_selector')
            submit_sel = detection.get('submit_selector')
            
            if not all([username_sel, password_sel, submit_sel]):
                logger.error("❌ Missing selectors")
                return False
            
            # Fill username
            logger.info(f"📝 Filling username: {username_sel}")
            await page.fill(username_sel, self.credentials['username'])
            await asyncio.sleep(0.5)
            
            # Fill password
            logger.info(f"📝 Filling password: {password_sel}")
            await page.fill(password_sel, self.credentials['password'])
            await asyncio.sleep(0.5)
            
            # Submit
            logger.info(f"🔘 Clicking submit: {submit_sel}")
            await page.click(submit_sel)
            await asyncio.sleep(2)
            
            # Verify success (check if still on login page)
            current_url = page.url
            if current_url != self.login_url:
                logger.info(f"✅ URL changed: {current_url}")
                return True
            
            # Check for error messages
            error_indicators = await page.locator('text=/error|invalid|incorrect/i').count()
            if error_indicators > 0:
                logger.error("❌ Login failed (error message found)")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Login failed: {e}")
            return False
    
    async def should_skip_element(self, element_text: str, element_classes: str, element_href: str) -> bool:
        """
        Check if clicking element will log out user
        
        Returns:
            True if should SKIP (will logout), False if safe to click
        """
        if not self.logged_in:
            return False
        
        # Quick text check first
        logout_keywords = ['logout', 'log out', 'sign out', 'signout', 'exit']
        text_lower = element_text.lower()
        
        if any(kw in text_lower for kw in logout_keywords):
            logger.warning(f"⚠️  Skipping logout element: {element_text}")
            return True
        
        # AI semantic check for edge cases
        try:
            is_logout = await self.ai.is_logout_action(element_text, element_classes, element_href)
            if is_logout:
                logger.warning(f"⚠️  AI detected logout: {element_text}")
            return is_logout
        except:
            return False
    
    def get_session_info(self) -> Dict:
        """Get current session info"""
        return {
            'logged_in': self.logged_in,
            'login_url': self.login_url,
            'has_credentials': self.credentials is not None
        }
    
    def reset_session(self):
        """Reset login state"""
        self.logged_in = False
        self.login_url = None
        logger.info("🔄 Session reset")
