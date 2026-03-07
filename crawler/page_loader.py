"""
Page Loader
Playwright-based browser automation with session management
"""
import asyncio
from typing import Optional, Dict
from playwright.async_api import async_playwright, Browser, BrowserContext, Page, Playwright
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class PageLoader:
    """Manages browser instances and page loading with Playwright"""
    
    def __init__(
        self,
        browser_type: str = 'chromium',
        headless: bool = False,
        timeout: int = 30000,
        wait_for: str = 'domcontentloaded',
        additional_wait: int = 2000
    ):
        """
        Initialize page loader
        
        Args:
            browser_type: 'chromium', 'firefox', or 'webkit'
            headless: Run in headless mode
            timeout: Page load timeout in milliseconds
            wait_for: Wait strategy ('networkidle', 'load', 'domcontentloaded')
            additional_wait: Additional wait after page load (ms)
        """
        self.browser_type = browser_type
        self.headless = headless
        self.timeout = timeout
        self.wait_for = wait_for
        self.additional_wait = additional_wait
        
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        
        logger.info(f"PageLoader initialized: {browser_type}, headless={headless}")
    
    async def start(self, storage_state: Optional[str] = None):
        """
        Start browser instance
        
        Args:
            storage_state: Path to saved session file (cookies, localStorage)
        """
        try:
            self.playwright = await async_playwright().start()
            
            # Select browser
            if self.browser_type == 'chromium':
                browser_launcher = self.playwright.chromium
            elif self.browser_type == 'firefox':
                browser_launcher = self.playwright.firefox
            elif self.browser_type == 'webkit':
                browser_launcher = self.playwright.webkit
            else:
                raise ValueError(f"Unsupported browser: {self.browser_type}")
            
            # Launch browser with optimized args to speed up screenshots
            self.browser = await browser_launcher.launch(
                headless=self.headless,
                args=[
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--disable-blink-features=AutomationControlled',
                    '--font-render-hinting=none',  # Skip font rendering optimization
                    '--disable-font-subpixel-positioning',  # Faster font rendering
                ]
            )
            
            # Create context (with optional saved session)
            context_options = {
                'viewport': {'width': 1920, 'height': 1080},
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            if storage_state:
                context_options['storage_state'] = storage_state
                logger.info(f"📂 Loaded session from: {storage_state}")
            
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # CRITICAL: Inject script BEFORE any page loads to bypass font waiting
            await self.page.add_init_script("""
                // Override document.fonts to prevent Playwright from waiting
                Object.defineProperty(document, 'fonts', {
                    get: function() {
                        return {
                            ready: Promise.resolve(),
                            load: () => Promise.resolve(),
                            check: () => true,
                            status: 'loaded'
                        };
                    }
                });
                
                // Disable all animations globally
                const style = document.createElement('style');
                style.textContent = `
                    *, *::before, *::after {
                        animation-duration: 0.001s !important;
                        animation-delay: 0s !important;
                        transition-duration: 0.001s !important;
                        transition-delay: 0s !important;
                    }
                `;
                if (document.head) {
                    document.head.appendChild(style);
                } else {
                    document.addEventListener('DOMContentLoaded', () => {
                        document.head.appendChild(style);
                    });
                }
            """)
            
            logger.info("✅ Font bypass and animation disable injected")
            
            # Set default timeout
            self.page.set_default_timeout(self.timeout)
            
            logger.info("✅ Browser started successfully")
        
        except Exception as e:
            logger.error(f"❌ Error starting browser: {e}")
            raise
    
    async def load_page(self, url: str, wait_time: Optional[int] = None) -> Page:
        """
        Navigate to URL and wait for page to load
        
        Args:
            url: URL to navigate to
            wait_time: Override default additional wait time (ms)
        
        Returns:
            Loaded page object
        """
        try:
            logger.info(f"🌐 Loading: {url}")
            
            # Try primary navigation strategy
            try:
                await self.page.goto(url, wait_until=self.wait_for, timeout=self.timeout)
            except Exception as nav_error:
                # Fallback: If networkidle/load fails, try domcontentloaded
                if 'Timeout' in str(nav_error) and self.wait_for != 'domcontentloaded':
                    logger.warning(f"⚠️  {self.wait_for} timeout, falling back to domcontentloaded")
                    try:
                        await self.page.goto(url, wait_until='domcontentloaded', timeout=30000)
                    except Exception as fallback_error:
                        # Last resort: Just navigate without waiting
                        logger.warning(f"⚠️  domcontentloaded failed, using commit strategy")
                        await self.page.goto(url, wait_until='commit', timeout=15000)
                else:
                    raise nav_error
            
            # Additional wait for SPAs to stabilize and React/Vue to render
            wait = wait_time if wait_time is not None else self.additional_wait
            if wait > 0:
                await asyncio.sleep(wait / 1000)
            
            page_title = await self.page.title()
            logger.debug(f"✅ Page loaded: {page_title}")
            
            return self.page
        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Timeout loading {url}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading {url}: {e}")
            raise
    
    async def get_current_page(self) -> Page:
        """Get the current page object"""
        if not self.page:
            raise RuntimeError("Browser not started. Call start() first.")
        return self.page
    
    async def save_session(self, filepath: str):
        """
        Save current session (cookies, localStorage) to file
        
        Args:
            filepath: Path to save session file
        """
        try:
            await self.context.storage_state(path=filepath)
            logger.info(f"💾 Session saved: {filepath}")
        except Exception as e:
            logger.error(f"❌ Error saving session: {e}")
            raise
    
    async def close(self):
        """Close browser and cleanup"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("🛑 Browser closed")
        
        except Exception as e:
            logger.error(f"Error closing browser: {e}")
    
    async def wait_for_navigation(self, timeout: Optional[int] = None):
        """Wait for navigation to complete"""
        try:
            await self.page.wait_for_load_state(
                self.wait_for,
                timeout=timeout or self.timeout
            )
        except Exception as e:
            logger.warning(f"Navigation wait failed: {e}")
    
    async def take_screenshot(self, filepath: str):
        """Take screenshot of current page"""
        try:
            # Optimize page before screenshot to avoid font/animation delays
            try:
                await self.page.evaluate("""
                    () => {
                        // Force fonts to be ready immediately
                        if (document.fonts) {
                            document.fonts.ready = Promise.resolve();
                        }
                        
                        // Disable animations and transitions
                        const style = document.createElement('style');
                        style.textContent = `
                            *, *::before, *::after {
                                animation: none !important;
                                transition: none !important;
                            }
                        `;
                        document.head.appendChild(style);
                    }
                """)
            except:
                pass  # Continue if optimization fails
            
            # Force fonts ready before screenshot
            try:
                await self.page.evaluate("""
                    if (document.fonts) {
                        Object.defineProperty(document.fonts, 'ready', {
                            get: () => Promise.resolve(),
                            configurable: true
                        });
                        Object.defineProperty(document.fonts, 'status', {
                            get: () => 'loaded',
                            configurable: true
                        });
                    }
                """)
            except:
                pass
            
            # Try full page first, fallback to viewport
            try:
                await self.page.screenshot(
                    path=filepath, 
                    full_page=True,
                    timeout=10000,  # 10 seconds for full page (reduced from 30s)
                    animations="disabled"
                )
                logger.debug(f"📸 Full-page screenshot saved: {filepath}")
            except Exception as full_error:
                logger.debug(f"⚠️  Full-page timed out, using viewport: {full_error}")
                await self.page.screenshot(
                    path=filepath, 
                    full_page=False,  # Viewport only
                    timeout=5000,  # 5 seconds (reduced from 10s)
                    animations="disabled"
                )
                logger.debug(f"📸 Viewport screenshot saved: {filepath}")
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
    
    def get_url(self) -> str:
        """Get current page URL"""
        return self.page.url if self.page else ""
    
    def get_title(self) -> str:
        """Get current page title"""
        return self.page.title() if self.page else ""


async def manual_login_flow(start_url: str, session_file: str = "auth_session.json") -> PageLoader:
    """
    Helper function for manual login flow
    
    Args:
        start_url: URL to navigate to for login
        session_file: Path to save session after login
    
    Returns:
        Authenticated PageLoader instance
    """
    loader = PageLoader(headless=False)
    await loader.start()
    
    await loader.load_page(start_url)
    
    print("\n" + "="*60)
    print("⏸️  MANUAL LOGIN REQUIRED")
    print("="*60)
    print(f"Please log in to the website in the browser window.")
    print(f"After logging in successfully, return here and press ENTER.")
    print("="*60 + "\n")
    
    input("Press ENTER when ready to continue crawling... ")
    
    # Save session
    await loader.save_session(session_file)
    print(f"✅ Session saved to {session_file}")
    print("✅ Starting automated crawl...\n")
    
    return loader
