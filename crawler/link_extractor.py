"""
Link Extractor
Discovers all navigable URLs (visible links + sitemap + SPA routes + Action-Verify-Back)
"""
import asyncio
import os
from typing import List, Set, Optional
from playwright.async_api import Page
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from app.utils.logger_config import setup_logger
from crawler.intelligent_link_filter import IntelligentLinkFilter
from crawler.page_snapshot import PageSnapshot
from crawler.ai_detector import GeminiElementDetector

logger = setup_logger(__name__)


class LinkExtractor:
    """Extracts links from pages using multiple strategies"""
    
    def __init__(
        self,
        same_origin_only: bool = True,
        exclude_patterns: List[str] = None,
        action_verify_back_enabled: bool = False,
        max_clickables_per_page: int = 10,
        use_intelligent_filtering: bool = True,
        save_snapshots: bool = True,
        state_manager = None
    ):
        """
        Initialize link extractor
        
        Args:
            same_origin_only: Only extract links from same domain
            exclude_patterns: URL patterns to exclude (e.g., /logout, /delete)
            action_verify_back_enabled: Enable Action-Verify-Back for JS navigation
            max_clickables_per_page: Max clickable elements to test per page
            use_intelligent_filtering: Filter duplicate components before clicking
            save_snapshots: Save page snapshots for debugging
            state_manager: StateManager instance for session management
        """
        self.same_origin_only = same_origin_only
        self.exclude_patterns = exclude_patterns or [
            '/logout', '/signout', '/sign-out',
            '/delete', '/remove',
            'javascript:', 'mailto:', 'tel:'
        ]
        self.action_verify_back_enabled = action_verify_back_enabled
        self.max_clickables_per_page = max_clickables_per_page
        self.use_intelligent_filtering = use_intelligent_filtering
        self.save_snapshots = save_snapshots
        self.state_manager = state_manager
        
        # Initialize intelligent filter
        self.intelligent_filter = IntelligentLinkFilter() if use_intelligent_filtering else None
        
        # Initialize snapshot manager
        self.snapshot_manager = PageSnapshot() if save_snapshots else None
        
        # Initialize shadow DOM detector
        from crawler.shadow_dom_detector import ShadowDOMDetector
        self.shadow_dom_detector = ShadowDOMDetector()
        
        # Initialize AI detector based on AI_PROVIDER
        self.ai_detector = None
        ai_provider = os.getenv('AI_PROVIDER', 'gemini').lower()
        use_ai = os.getenv('USE_AI_DETECTION', 'false').lower() == 'true'
        
        if use_ai:
            try:
                if ai_provider == 'ollama':
                    # Use Ollama models
                    from crawler.ollama_detector import OllamaElementDetector
                    ollama_host = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
                    vision_model = os.getenv('OLLAMA_VISION_MODEL', 'llava:13b')
                    self.ai_detector = OllamaElementDetector(ollama_host, vision_model)
                    logger.info(f"🤖 Ollama AI detector enabled (host: {ollama_host}, model: {vision_model})")
                elif ai_provider == 'gemini':
                    # Use Gemini with key rotation
                    from crawler.gemini_key_rotator import GeminiKeyRotator
                    self.key_rotator = GeminiKeyRotator()
                    if self.key_rotator.get_current_key():
                        self.ai_detector = GeminiElementDetector(key_rotator=self.key_rotator)
                        logger.info(f"🤖 Gemini AI detector enabled with {self.key_rotator.get_stats()['total_keys']} API keys")
                    else:
                        logger.warning("⚠️  AI_PROVIDER=gemini but no API keys found")
                else:
                    logger.warning(f"⚠️  Unknown AI_PROVIDER: {ai_provider}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize AI detector: {e}")
        else:
            logger.info("ℹ️  AI detector disabled (set USE_AI_DETECTION=true to enable)")
        
        logger.info(
            f"LinkExtractor initialized (same_origin={same_origin_only}, "
            f"AVB={'ON' if action_verify_back_enabled else 'OFF'}, "
            f"intelligent_filter={'ON' if use_intelligent_filtering else 'OFF'}, "
            f"snapshots={'ON' if save_snapshots else 'OFF'})"
        )
    
    async def extract_all_links(self, page: Page, base_url: str, use_ai: bool = True) -> List[str]:
        """
        Extract all links from page using Action-Verify-Back (primary method)
        
        Args:
            page: Playwright page object
            base_url: Base URL for filtering
            use_ai: Whether to use AI for navigation detection (default: True)
        
        Returns:
            List of unique, filtered URLs
        """
        all_links: Set[str] = set()
        
        # Store base_url for filtering
        self.start_url = base_url
        
        # STRATEGY 1: Extract static <a href> links (always do this first)
        visible_links = await self._extract_visible_links(page)
        all_links.update(visible_links)
        
        # STRATEGY 2: Action-Verify-Back for JavaScript navigation (augments static links)
        # This discovers JS-driven navigation that doesn't use <a> tags
        if self.action_verify_back_enabled:
            avb_links = await self._extract_via_action_verify_back(page, base_url, use_ai=use_ai)
            all_links.update(avb_links)
        
        # Filter links
        filtered_links = self._filter_links(list(all_links), base_url)
        
        logger.info(f"🔗 Extracted {len(filtered_links)} unique links")
        
        return filtered_links
    
    async def _extract_visible_links(self, page: Page) -> List[str]:
        """Extract all visible <a href> elements"""
        js_code = """
        () => {
            const links = [];
            document.querySelectorAll('a[href]').forEach(el => {
                const href = el.href;
                if (href && !href.includes('javascript:') && !href.startsWith('#')) {
                    links.push(href);
                }
            });
            return links;
        }
        """
        
        try:
            links = await page.evaluate(js_code)
            logger.debug(f"Found {len(links)} visible links")
            return links
        except Exception as e:
            logger.error(f"Error extracting visible links: {e}")
            return []
    
    async def _extract_from_sitemap(self, base_url: str) -> List[str]:
        """Parse sitemap.xml if available"""
        sitemap_urls = [
            f"{base_url}/sitemap.xml",
            f"{base_url}/sitemap_index.xml",
            f"{base_url}/robots.txt"
        ]
        
        links = []
        
        for sitemap_url in sitemap_urls:
            try:
                response = requests.get(sitemap_url, timeout=5)
                if response.status_code == 200:
                    if 'xml' in sitemap_url:
                        soup = BeautifulSoup(response.content, 'lxml-xml')
                        urls = soup.find_all('loc')
                        links.extend([url.text for url in urls])
                        logger.debug(f"Found {len(urls)} URLs in sitemap")
                    else:
                        # Parse robots.txt for sitemap references
                        for line in response.text.split('\n'):
                            if line.lower().startswith('sitemap:'):
                                sitemap_ref = line.split(':', 1)[1].strip()
                                links.append(sitemap_ref)
            except Exception as e:
                logger.debug(f"Could not fetch {sitemap_url}: {e}")
        
        return links
    
    async def _detect_spa_routes(self, page: Page) -> List[str]:
        """Detect SPA routes from JavaScript (React Router, Vue Router, etc.)"""
        # Simplified implementation - would need framework-specific detection
        js_code = r"""
        () => {
            const routes = [];
            
            // Try to find React Router routes
            if (window.__REACT_ROUTER_CONTEXT__) {
                // Extract routes from context
            }
            
            // Try to find Vue Router routes
            if (window.__VUE_ROUTER__) {
                // Extract routes
            }
            
            // Look for route definitions in script tags
            const scripts = Array.from(document.scripts);
            scripts.forEach(script => {
                const content = script.textContent || '';
                // Simple regex to find route patterns
                const matches = content.match(/['"]\/[a-zA-Z0-9/_-]+['"]/g);
                if (matches) {
                    routes.push(...matches.map(m => m.replace(/['"]/g, '')));
                }
            });
            
            return [...new Set(routes)];
        }
        """
        
        try:
            routes = await page.evaluate(js_code)
            # Convert relative routes to absolute URLs
            base_url = page.url.split('?')[0].split('#')[0]
            absolute_routes = [urljoin(base_url, route) for route in routes]
            logger.debug(f"Detected {len(absolute_routes)} SPA routes")
            return absolute_routes
        except Exception as e:
            logger.error(f"Error detecting SPA routes: {e}")
            return []
    
    async def _detect_navigation_with_ai(self, page: Page, base_url: str) -> List[dict]:
        """
        Use AI to detect navigation elements on homepage
        
        This is used as the PRIMARY detection method on homepages because:
        1. Visual understanding identifies navigation patterns reliably
        2. Works across different HTML structures (generic solution)
        3. Semantic recognition of "navigation" vs "content" elements
        
        Args:
            page: Playwright page object
            base_url: Base URL (for homepage detection)
        
        Returns:
            List of element dicts compatible with AVB format
        """
        if not self.ai_detector:
            return []
        
        current_url = page.url
        is_homepage = current_url.rstrip('/') == base_url.rstrip('/')
        
        # CHANGED: Use AI on ALL pages, not just homepage
        # if not is_homepage:
        #     return []
        
        try:
            page_type = "homepage" if is_homepage else "sub-page"
            ai_provider = os.getenv('AI_PROVIDER', 'gemini').lower()
            logger.info(f"🤖 Using {ai_provider.upper()} AI to detect navigation elements on {page_type}")
            
            # EXPAND ACCORDIONS/MENUS BEFORE AI DETECTION
            # This ensures AI sees ALL navigation links, not just collapsed sections
            try:
                expanded_count = await page.evaluate("""
                    async () => {
                        let expanded = 0;
                        
                        // Strategy 1: Click elements that look like accordion headers/menu toggles
                        const accordionSelectors = [
                            'div.element-list > div > div > div:first-child',  // DemoQA specific
                            '[class*="accordion"]',
                            '[class*="collapse"]',
                            '[class*="toggle"]',
                            '[role="button"][aria-expanded="false"]',
                            'button[aria-expanded="false"]',
                            '.menu-item:not(.active)',
                            '[data-toggle="collapse"]'
                        ];
                        
                        for (const selector of accordionSelectors) {
                            const elements = document.querySelectorAll(selector);
                            for (const el of elements) {
                                try {
                                    // Check if element is clickable and not already expanded
                                    const isCollapsed = el.getAttribute('aria-expanded') === 'false' ||
                                                       !el.classList.contains('active') ||
                                                       !el.classList.contains('open');
                                    
                                    if (isCollapsed && (el.onclick || el.getAttribute('onclick') || 
                                        window.getComputedStyle(el).cursor === 'pointer')) {
                                        el.click();
                                        expanded++;
                                        // Small delay to allow animation
                                        await new Promise(resolve => setTimeout(resolve, 100));
                                    }
                                } catch (e) {
                                    // Ignore errors, continue with next element
                                }
                            }
                        }
                        
                        return expanded;
                    }
                """)
                
                if expanded_count > 0:
                    logger.info(f"📂 Expanded {expanded_count} accordion/menu sections before AI detection")
                    # Wait for any animations to complete
                    await page.wait_for_timeout(500)
            except Exception as e:
                logger.debug(f"Accordion expansion error (non-fatal): {e}")
            
            # Create snapshots directory if needed
            os.makedirs("snapshots", exist_ok=True)
            screenshot_path = f"snapshots/ai_analysis_{hash(current_url) % 10000}.png"
            
            # Hide common banner/watermark elements before screenshot
            try:
                await page.evaluate("""
                    () => {
                        // Hide common banner selectors
                        const bannerSelectors = [
                            'div.banner', 'div.advertisement', 'div.ad-banner',
                            '#banner', '#advertisement', '.top-banner',
                            'div[class*="banner"]', 'div[class*="promo"]',
                            'div[id*="banner"]', 'iframe[class*="ad"]'
                        ];
                        
                        bannerSelectors.forEach(sel => {
                            document.querySelectorAll(sel).forEach(el => {
                                el.style.display = 'none';
                            });
                        });
                        
                        // Speed up screenshot by disabling animations and font loading
                        if (document.fonts) {
                            // Force fonts to be "ready" immediately
                            document.fonts.ready = Promise.resolve();
                        }
                        
                        // Disable all CSS animations and transitions
                        const style = document.createElement('style');
                        style.textContent = `
                            *, *::before, *::after {
                                animation-duration: 0s !important;
                                animation-delay: 0s !important;
                                transition-duration: 0s !important;
                                transition-delay: 0s !important;
                            }
                        `;
                        document.head.appendChild(style);
                    }
                """)
            except:
                pass  # If hiding fails, continue anyway
            
            # Force fonts to be ready BEFORE taking screenshot (prevents blocking)
            try:
                await page.evaluate("""
                    // Override document.fonts.ready to immediately resolve
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
            
            # Take screenshot with TWO attempts: full page first, then viewport-only fallback
            screenshot_success = False
            
            # Attempt 1: Try full page (but with shorter timeout)
            try:
                await page.screenshot(
                    path=screenshot_path, 
                    full_page=True,
                    timeout=10000,  # 10 seconds for full page (reduced from 30s)
                    animations="disabled",
                )
                screenshot_success = True
                logger.debug(f"✅ Full-page screenshot captured")
            except Exception as full_page_error:
                logger.debug(f"⚠️  Full-page screenshot timed out, trying viewport-only...")
                
                # Attempt 2: Viewport-only (much faster, but misses content below fold)
                try:
                    await page.screenshot(
                        path=screenshot_path, 
                        full_page=False,  # Just visible viewport
                        timeout=5000,  # 5 seconds (reduced from 10s)
                        animations="disabled",
                    )
                    screenshot_success = True
                    logger.info(f"✅ Viewport screenshot captured (full-page failed)")
                except Exception as viewport_error:
                    logger.error(f"❌ Both screenshot attempts failed: {viewport_error}")
            
            if not screenshot_success:
                logger.info("⚠️  Falling back to traditional link detection")
                return []
            
            # Get HTML content and current URL
            html_content = await page.content()
            current_url = page.url
            
            # Use Gemini to detect navigation elements
            ai_elements = await self.ai_detector.detect_navigation_cards(
                screenshot_path, 
                html_content,
                current_url  # Pass URL for domain-specific caching
            )
            
            if not ai_elements:
                logger.warning("⚠️  AI detected no navigation elements, falling back to traditional detection")
                return []
            
            logger.info(f"🤖 AI found {len(ai_elements)} navigation elements: {[e['text'] for e in ai_elements]}")
            
            # Convert AI format to AVB format
            avb_elements = []
            for ai_elem in ai_elements:
                avb_elements.append({
                    'tag': 'AI_DETECTED',
                    'text': ai_elem['text'],
                    'class': '',
                    'id': '',
                    'href': '',
                    'selector': ai_elem.get('selector', ''),
                    'confidence': 'ai_high',
                    'ai_confidence': ai_elem['confidence']
                })
            
            return avb_elements
            
        except Exception as e:
            logger.error(f"❌ Error in AI navigation detection: {e}")
            return []
    
    async def _extract_via_action_verify_back(self, page: Page, base_url: str, use_ai: bool = True) -> List[str]:
        """
        Extract links via Action-Verify-Back approach with PARALLEL processing
        
        This method:
        1. Finds ALL clickable elements (buttons, divs with onclick, etc.)
        2. Clicks each element in PARALLEL using browser contexts
        3. Verifies if URL changed
        4. Records new URLs
        
        OPTIMIZED: Uses parallel browser contexts for speed
        
        Args:
            page: Playwright page object
            base_url: Base URL for filtering
            use_ai: Whether to use AI for navigation detection (default: True)
        
        Returns:
            List of URLs discovered via JavaScript navigation
        """
        discovered_urls: Set[str] = set()
        original_url = page.url
        
        # JavaScript to find all clickable elements with STRICT criteria
        js_code = f"""
        () => {{
            const clickableElements = [];
            const seen = new Set();
            
            // STRATEGY 1: Find primary navigation elements (high confidence)
            const primarySelectors = [
                'a[href]',  // Traditional links
                'button',   // Actual buttons
                '[role="button"]',  // ARIA buttons
                '[role="link"]',    // ARIA links
                'input[type="submit"]',
                'input[type="button"]'
            ];
            
            primarySelectors.forEach(selector => {{
                document.querySelectorAll(selector).forEach(el => {{
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                     style.visibility !== 'hidden' &&
                                     style.display !== 'none' &&
                                     style.opacity !== '0';
                    
                    if (isVisible) {{
                        const key = el.outerHTML;
                        if (!seen.has(key)) {{
                            seen.add(key);
                            const text = el.textContent || el.getAttribute('aria-label') || '';
                            const trimmedText = text.trim().substring(0, 50);
                            
                            clickableElements.push({{
                                tag: el.tagName,
                                text: trimmedText,
                                class: el.className || '',
                                id: el.id || '',
                                href: el.href || '',
                                confidence: 'high'
                            }});
                        }}
                    }}
                }});
            }});
            
            // STRATEGY 2: Find elements with explicit click handlers (medium confidence)
            document.querySelectorAll('*').forEach(el => {{
                const hasOnClick = el.onclick !== null || el.getAttribute('onclick') !== null;
                const hasPointerCursor = window.getComputedStyle(el).cursor === 'pointer';
                
                // Check for common navigation contexts
                const inNavContext = el.closest('nav, [role="navigation"], .navigation, .menu, .navbar, .category-cards, .home-body, [class*="card"]');
                
                // Check for card/navigation classes
                const className = el.className || '';
                const classStr = typeof className === 'string' ? className : '';
                const hasNavClass = /card|category|nav-item|menu-item|clickable/i.test(classStr);
                
                // Medium confidence: onclick+pointer OR (pointer+navContext) OR (pointer+navClass)
                const isLikelyClickable = (hasOnClick && hasPointerCursor) || 
                                         (hasPointerCursor && inNavContext) ||
                                         (hasPointerCursor && hasNavClass);
                
                if (isLikelyClickable) {{
                    const rect = el.getBoundingClientRect();
                    const style = window.getComputedStyle(el);
                    const isVisible = rect.width > 0 && rect.height > 0 && 
                                     style.visibility !== 'hidden' &&
                                     style.display !== 'none' &&
                                     style.opacity !== '0';
                    
                    if (isVisible) {{
                        const key = el.outerHTML;
                        if (!seen.has(key)) {{
                            seen.add(key);
                            const text = el.textContent || '';
                            const trimmedText = text.trim().substring(0, 50);
                            
                            // Skip if it's a container with lots of text (likely not a button)
                            if (trimmedText.length > 100) return;
                            
                            clickableElements.push({{
                                tag: el.tagName,
                                text: trimmedText,
                                class: el.className || '',
                                id: el.id || '',
                                confidence: 'medium'
                            }});
                        }}
                    }}
                }}
            }});
            
            // Limit to configured maximum
            return clickableElements.slice(0, {self.max_clickables_per_page});
        }}
        """
        
        try:
            # TRY AI DETECTION FIRST (only if use_ai=True)
            ai_elements = []
            if use_ai:
                ai_elements = await self._detect_navigation_with_ai(page, base_url)
            
            if ai_elements:
                # Use AI-detected elements
                clickable_elements = ai_elements
                logger.info(f"🤖 Using {len(clickable_elements)} AI-detected navigation elements")
            else:
                # Fallback to traditional JavaScript detection
                clickable_elements = await page.evaluate(js_code)
                logger.info(f"🎯 Found {len(clickable_elements)} clickable elements (traditional detection)")
            
            # ADD SHADOW DOM ELEMENTS (if any exist)
            try:
                shadow_elements = await self.shadow_dom_detector.extract_shadow_elements(page)
                if shadow_elements:
                    clickable_elements.extend(shadow_elements)
                    logger.info(f"🌓 Added {len(shadow_elements)} shadow DOM elements")
            except Exception as e:
                logger.warning(f"⚠️  Shadow DOM detection failed: {e}")
            
            # Store original clickables for snapshot
            original_clickables = clickable_elements.copy()
            
            # DEDUPLICATE BY TEXT FIRST (critical for repeated accordion items)
            seen_texts = {}
            deduplicated = []
            for element in clickable_elements:
                text = element.get('text', '').strip()
                href = element.get('href', '')
                
                # Create unique key from text + href
                key = f"{text}|{href}"
                
                if key not in seen_texts:
                    seen_texts[key] = element
                    deduplicated.append(element)
            
            if len(deduplicated) < len(clickable_elements):
                logger.info(f"🔄 Deduplication: {len(clickable_elements)} → {len(deduplicated)} elements (removed {len(clickable_elements) - len(deduplicated)} duplicates)")
            
            clickable_elements = deduplicated
            
            # INTELLIGENT FILTERING: Remove duplicate components BEFORE clicking
            if self.use_intelligent_filtering and self.intelligent_filter:
                clickable_elements = await self.intelligent_filter.filter_clickables_by_component(
                    page,
                    clickable_elements
                )
                logger.info(f"🧠 After intelligent filtering: {len(clickable_elements)} unique components")
            
            # Additional filtering: Remove external links and same-page links
            current_url = page.url
            base_domain = urlparse(base_url).netloc
            
            filtered_by_url = []
            for element in clickable_elements:
                href = element.get('href', '')
                
                # Skip if no href (keep non-link clickables like buttons)
                if not href:
                    filtered_by_url.append(element)
                    continue
                
                # Parse href
                try:
                    parsed_href = urlparse(href)
                    
                    # Skip external domains (if same_origin_only enabled)
                    if self.same_origin_only and parsed_href.netloc and parsed_href.netloc != base_domain:
                        logger.debug(f"⏭️  Skipping external link: {href}")
                        continue
                    
                    # Skip same-page links (anchors/current URL)
                    clean_current = current_url.split('#')[0].split('?')[0].rstrip('/')
                    clean_href = href.split('#')[0].split('?')[0].rstrip('/')
                    
                    if clean_href == clean_current:
                        logger.debug(f"⏭️  Skipping same-page link: {href}")
                        continue
                    
                    filtered_by_url.append(element)
                
                except Exception as e:
                    logger.debug(f"URL parse error for {href}: {e}")
                    filtered_by_url.append(element)  # Keep on error (fail-safe)
            
            clickable_elements = filtered_by_url
            if len(filtered_by_url) < len(clickable_elements):
                logger.info(f"🎯 After URL filtering: {len(clickable_elements)} actionable links")
            
            # Process clickables in parallel batches for speed
            batch_size = 3  # Reduced from 5 to 3 for better deduplication
            
            click_attempts = 0
            successful_clicks = 0
            skipped_duplicates = 0
            
            for batch_start in range(0, len(clickable_elements), batch_size):
                batch = clickable_elements[batch_start:batch_start + batch_size]
                
                # Create tasks for parallel execution
                tasks = [
                    self._click_and_verify(page.context, original_url, element, discovered_urls)
                    for element in batch
                ]
                
                # Execute batch in parallel
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Collect discovered URLs
                for element, result in zip(batch, results):
                    click_attempts += 1
                    if isinstance(result, str) and result:
                        if result not in discovered_urls:
                            discovered_urls.add(result)
                            successful_clicks += 1
                            logger.info(f"✅ AVB: '{element.get('text', '')[:40]}' → {result}")
                        else:
                            skipped_duplicates += 1
                            logger.debug(f"⏭️  Skipped duplicate URL: {result}")
                    elif isinstance(result, Exception):
                        logger.debug(f"⚠️  AVB exception for '{element.get('text', '')[:30]}': {str(result)[:50]}")
            
            logger.info(f"🔍 Action-Verify-Back: {successful_clicks}/{click_attempts} clicks discovered URLs ({len(discovered_urls)} unique)")
            
            if skipped_duplicates > 0:
                logger.info(f"⏭️  Skipped {skipped_duplicates} duplicate URLs during AVB")
            
            if successful_clicks == 0 and click_attempts > 0:
                logger.warning(f"⚠️  NO URLs discovered from {click_attempts} clickable elements! Check selectors.")
            
            # CAPTURE SNAPSHOT for debugging
            if self.save_snapshots and self.snapshot_manager:
                await self.snapshot_manager.capture_snapshot(
                    page=page,
                    url=original_url,
                    clickable_elements=original_clickables,
                    filtered_elements=clickable_elements,
                    discovered_urls=list(discovered_urls)
                )
            
            return list(discovered_urls)
        
        except Exception as e:
            logger.error(f"Error in Action-Verify-Back: {e}")
            return []
    
    async def _click_and_verify(self, browser_context, original_url: str, element: dict, discovered_urls: Set[str] = None) -> str:
        """
        Click an element in a new page context and verify navigation
        
        Args:
            browser_context: Browser context to create new page
            original_url: Original URL to load
            element: Element info dict
            discovered_urls: Set of already discovered URLs to avoid re-clicking
        
        Returns:
            New URL if navigation occurred, empty string otherwise
        """
        # Initialize discovered_urls if not provided
        if discovered_urls is None:
            discovered_urls = set()
        
        # Check if should skip element to preserve session
        if self.state_manager and self.state_manager.should_skip_action(
            element.get('text', ''), 
            element
        ):
            logger.debug(f"⏭️  Skipping '{element.get('text', '')}' (preserve session)")
            return ""
        
        new_page = None
        try:
            # Create new page in parallel
            new_page = await browser_context.new_page()
            
            # Load original URL
            await new_page.goto(original_url, wait_until='domcontentloaded', timeout=10000)
            await new_page.wait_for_timeout(500)
            
            # Capture original DOM state BEFORE clicking
            original_dom_hash = await new_page.evaluate("""
                () => {
                    // Get main content area (exclude nav/header/footer)
                    const main = document.querySelector('main, [role="main"], #root > div, .content, .main-content') || document.body;
                    const content = main.innerText + main.innerHTML.length;
                    
                    // Simple hash function
                    let hash = 0;
                    for (let i = 0; i < content.length; i++) {
                        const char = content.charCodeAt(i);
                        hash = ((hash << 5) - hash) + char;
                        hash = hash & hash; // Convert to 32bit integer
                    }
                    return hash;
                }
            """)
            
            text = element.get('text', '').strip()
            
            # Strip icon font characters (Unicode private use area U+E000-U+F8FF)
            # These are commonly used by icon fonts (Material Icons, FontAwesome, etc.)
            import re
            text_clean = re.sub(r'[\ue000-\uf8ff]', '', text).strip()
            
            logger.debug(f"🔍 AVB: Trying to click '{text[:30]}...' (cleaned: '{text_clean}')")
            
            # Build selectors to try (in order of reliability)
            selectors_to_try = []
            
            # 0. Try AI-provided selector first (highest reliability for AI-detected elements)
            if element.get('selector') and element.get('confidence') == 'ai_high':
                # AI selectors are relative nth-child() selectors, need broader matching
                ai_selector = element['selector']
                logger.debug(f"🤖 AI element detected, using text-based matching")
                
                # For AI elements, use JavaScript-based text search (most reliable)
                # Use cleaned text (without icon fonts) for matching
                text_for_matching = text_clean if text_clean else text
                if text_for_matching and len(text_for_matching) > 2:
                    # Escape special characters for JavaScript
                    text_escaped = text_for_matching.replace("'", "\\'").replace('"', '\\"')
                    
                    # Strategy 1: Find by exact text in common clickable elements
                    # Strip icon fonts from both sides for comparison
                    js_selector = f"""
                        (() => {{
                            const elements = Array.from(document.querySelectorAll('div, a, button, span, li'));
                            const target = elements.find(el => {{
                                // Strip icon font characters (Unicode private use area)
                                const text = el.textContent.trim().replace(/[\ue000-\uf8ff]/g, '').trim();
                                const style = window.getComputedStyle(el);
                                return text === '{text_escaped}' && 
                                       el.offsetParent !== null &&
                                       (style.cursor === 'pointer' || el.onclick || el.href);
                            }});
                            if (target) {{
                                target.click();
                                return true;
                            }}
                            return false;
                        }})()
                    """
                    selectors_to_try.append(('javascript_click', js_selector))
                    
                    # Strategy 2: Find by text (broader match with click) 
                    js_selector_broad = f"""
                        (() => {{
                            const elements = Array.from(document.querySelectorAll('div, a, button'));
                            // Strip icon font characters from element text
                            const target = elements.find(el => el.textContent.trim().replace(/[\ue000-\uf8ff]/g, '').trim() === '{text_escaped}');
                            if (target) {{
                                target.scrollIntoView({{ behavior: 'instant', block: 'center' }});
                                target.click();
                                return true;
                            }}
                            return false;
                        }})()
                    """
                    selectors_to_try.append(('javascript_click', js_selector_broad))
                    
                    # Strategy 3: Playwright text selector (very reliable)
                    # Use cleaned text for better matching
                    selectors_to_try.append(('text', f'text="{text_for_matching[:50]}"'))
                    
                    # Strategy 4: Partial text match
                    selectors_to_try.append(('text', f'text=/.*{text_for_matching[:20]}.*/i'))
                
                logger.debug(f"🎯 AI element '{text[:30]}' - will try {len(selectors_to_try)} strategies")
                logger.debug(f"🎯 AI element '{text[:30]}' - will try {len(selectors_to_try)} strategies")
            
            # 1. Try href for links (most reliable for non-AI elements)
            elif element.get('href'):
                href = element['href']
                selectors_to_try.append(('css', f"a[href='{href}']"))
            
            # 2. Try ID (unique identifier)
            if element.get('id') and not element.get('confidence') == 'ai_high':
                selectors_to_try.append(('css', f"#{element['id']}"))
            
            # 3. Try class + tag combination
            if element.get('class') and not element.get('confidence') == 'ai_high':
                class_str = str(element['class'])
                classes = class_str.split()
                if classes:
                    selectors_to_try.append(('css', f"{element['tag'].lower()}.{classes[0]}"))
            
            # 4. Try text content (fallback for non-AI elements)
            if text and len(text) > 2 and not element.get('confidence') == 'ai_high':
                # Use shorter text for better matching
                short_text = text[:30].strip()
                if short_text:
                    selectors_to_try.append(('text', f'text="{short_text}"'))
            
            # Try clicking with each selector
            clicked = False
            clicked_selector = None
            for idx, (selector_type, sel) in enumerate(selectors_to_try):
                try:
                    logger.debug(f"  Attempt {idx+1}/{len(selectors_to_try)}: [{selector_type}] {sel[:80] if isinstance(sel, str) and len(sel) < 100 else '...'}")
                    
                    if selector_type == 'javascript_click':
                        # Execute JavaScript that finds AND clicks element
                        result = await new_page.evaluate(sel)
                        if result:  # JavaScript returned true (click succeeded)
                            clicked = True
                            clicked_selector = 'javascript_click'
                            logger.debug(f"  ✅ Clicked successfully via JavaScript")
                        else:
                            logger.debug(f"  ❌ JavaScript click returned false (element not found)")
                            continue
                    elif selector_type == 'javascript':
                        # Execute JavaScript to find element, then click via Playwright
                        element_handle = await new_page.evaluate_handle(sel)
                        if element_handle:
                            await element_handle.click(timeout=3000)
                            clicked = True
                            clicked_selector = 'javascript'
                    elif selector_type == 'text':
                        # Playwright text selector
                        await new_page.click(sel, timeout=3000)
                        clicked = True
                        clicked_selector = sel
                    else:  # css
                        await new_page.wait_for_selector(sel, timeout=2000, state='visible')
                        await new_page.click(sel, timeout=3000)
                        clicked = True
                        clicked_selector = sel
                    
                    if clicked:
                        logger.debug(f"  ✅ Click confirmed")
                        # Wait for potential navigation
                        await new_page.wait_for_timeout(1000)
                        break
                    
                except Exception as click_err:
                    logger.debug(f"  ❌ Failed: {str(click_err)[:50]}")
                    continue
            
            if not clicked:
                logger.debug(f"⚠️  Could not click '{element.get('text', '')[:30]}' - tried {len(selectors_to_try)} selectors")
                return ""
            
            # Wait for potential DOM changes after click
            await new_page.wait_for_timeout(1000)
            
            # Check if URL changed
            new_url = new_page.url
            
            # Check if DOM changed significantly (for SPAs)
            new_dom_hash = await new_page.evaluate("""
                () => {
                    const main = document.querySelector('main, [role="main"], #root > div, .content, .main-content') || document.body;
                    const content = main.innerText + main.innerHTML.length;
                    
                    let hash = 0;
                    for (let i = 0; i < content.length; i++) {
                        const char = content.charCodeAt(i);
                        hash = ((hash << 5) - hash) + char;
                        hash = hash & hash;
                    }
                    return hash;
                }
            """)
            
            url_changed = new_url != original_url
            dom_changed = abs(new_dom_hash - original_dom_hash) > 1000  # Significant change threshold
            
            if url_changed:
                logger.debug(f"✅ AVB SUCCESS (URL): '{element.get('text', '')[:30]}' → {new_url}")
                return new_url
            elif dom_changed:
                # SPA component change detected - HYBRID APPROACH
                component_name = element.get('text', 'unknown').lower().replace(' ', '-').replace('/', '-')
                virtual_url = f"{original_url}#component-{component_name}"
                
                logger.debug(f"✅ AVB SUCCESS (DOM): '{element.get('text', '')[:30]}' → Component state")
                
                # OPTIMIZATION: Analyze component immediately BUT cache to avoid re-analysis
                # This ensures SPAs work while preventing duplicate API calls
                from crawler.dom_analyzer import DOMAnalyzer
                dom_analyzer = DOMAnalyzer(ai_detector=self.ai_detector)
                
                try:
                    # Analyze the component state once
                    analysis = await dom_analyzer.analyze_page(new_page)
                    title = await new_page.title()
                    
                    # Store in component_states for orchestrator
                    if not hasattr(self, 'component_states'):
                        self.component_states = []
                    
                    self.component_states.append({
                        'url': virtual_url,
                        'title': f"{title} - {element.get('text', 'Component')}",
                        'analysis': analysis,
                        'trigger_element': element.get('text', ''),
                        'cached': True  # Mark as already analyzed to prevent re-crawling
                    })
                    
                    logger.info(f"📦 Stored component state: {virtual_url}")
                except Exception as e:
                    logger.error(f"❌ Error analyzing component state: {e}")
                
                # Don't return URL - we've already analyzed it
                return ""
            else:
                logger.debug(f"⚠️  No navigation: '{element.get('text', '')[:30]}' (URL and DOM unchanged)")
            
            return ""
        
        except Exception as e:
            logger.debug(f"❌ Click-verify error for '{element.get('text', '')[:30]}': {str(e)[:100]}")
            return ""
        
        finally:
            # Always close the page
            if new_page:
                try:
                    await new_page.close()
                except:
                    pass
    
    def _filter_links(self, links: List[str], base_url: str) -> List[str]:
        """Filter links based on rules"""
        filtered = []
        base_parsed = urlparse(base_url)
        
        for link in links:
            try:
                parsed = urlparse(link)
                
                # Same origin check
                if self.same_origin_only and parsed.netloc != base_parsed.netloc:
                    continue
                
                # Exclude patterns check
                if any(pattern in link.lower() for pattern in self.exclude_patterns):
                    continue
                
                # Build clean link
                clean_link = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if parsed.query:
                    clean_link += f"?{parsed.query}"
                
                # Preserve fragment ONLY for virtual component URLs (SPA state detection)
                if parsed.fragment and parsed.fragment.startswith('component-'):
                    clean_link += f"#{parsed.fragment}"
                
                filtered.append(clean_link)
            
            except Exception as e:
                logger.debug(f"Error parsing link {link}: {e}")
        
        return list(set(filtered))
    
    def get_ai_stats(self) -> dict:
        """Get AI detector statistics"""
        if self.ai_detector:
            return self.ai_detector.get_cache_stats()
        return {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'total_detections': 0
        }
    
    def get_component_states(self) -> list:
        """
        Get component states discovered during crawl
        These are SPA component views analyzed immediately without URL navigation
        """
        return getattr(self, 'component_states', [])
    
    def clear_component_states(self):
        """Clear component states (call after processing)"""
        self.component_states = []
