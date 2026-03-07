"""
Intelligent Link Filter
Prevents clicking duplicate components (e.g., 100 product cards)
Uses component detection BEFORE clicking to filter intelligently
"""
from typing import List, Dict, Set
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class IntelligentLinkFilter:
    """
    Filters clickable elements intelligently using component analysis
    Prevents wasteful clicking of duplicate components
    """
    
    def __init__(self):
        """Initialize intelligent link filter"""
        self.seen_component_signatures: Set[str] = set()
        logger.info("IntelligentLinkFilter initialized")
    
    async def filter_clickables_by_component(
        self,
        page: Page,
        clickable_elements: List[Dict]
    ) -> List[Dict]:
        """
        Filter clickable elements to avoid duplicates
        
        Strategy:
        1. Detect which component each clickable belongs to
        2. Normalize component (ProductCard(id=1) → ProductCard(id=:number))
        3. Keep ONLY ONE clickable per unique component type
        
        Example:
        Input: 100 product cards
        Output: 1 product card (representative)
        
        Args:
            page: Playwright page
            clickable_elements: List of clickable element dicts
        
        Returns:
            Filtered list (one per component type)
        """
        if not clickable_elements:
            return []
        
        # Reduced logging - only show summary
        # logger.info(f"🧠 Intelligent filtering: {len(clickable_elements)} clickables...")
        
        # Inject component detection for each clickable
        filtered_elements = []
        component_representatives: Dict[str, Dict] = {}  # signature → element
        
        for element in clickable_elements:
            try:
                # Get component signature for this element
                signature = await self._get_component_signature(page, element)
                
                if not signature:
                    # No component detected - keep it (might be traditional link)
                    filtered_elements.append(element)
                    continue
                
                # Check if we've seen this component type before
                if signature not in component_representatives:
                    # First time seeing this component type - keep it
                    component_representatives[signature] = element
                    logger.debug(f"✅ Keeping representative: {signature}")
                else:
                    # Already have a representative for this component type - skip
                    logger.debug(f"⏭️  Skipping duplicate: {signature}")
            
            except Exception as e:
                logger.debug(f"Filter error for element: {e}")
                # On error, keep the element (fail-safe)
                filtered_elements.append(element)
        
        # Add all representatives to filtered list
        filtered_elements.extend(component_representatives.values())
        
        # Only log if significant filtering occurred
        saved_clicks = len(clickable_elements) - len(filtered_elements)
        if saved_clicks > 0:
            logger.info(f"🎯 Filtered {len(clickable_elements)} → {len(filtered_elements)} (saved {saved_clicks} clicks)")
        else:
            logger.debug(f"🎯 No duplicates found: {len(clickable_elements)} unique elements")
        
        return filtered_elements
    
    async def _get_component_signature(self, page: Page, element: Dict) -> str:
        """
        Get normalized component signature for a clickable element
        
        Args:
            page: Playwright page
            element: Clickable element dict
        
        Returns:
            Normalized component signature (e.g., "ProductCard:number")
        """
        # Build selector for this element
        selector = self._build_selector(element)
        
        if not selector:
            return ""
        
        # JavaScript to get component for this element
        js_code = f"""
        (selector) => {{
            try {{
                const el = document.querySelector(selector);
                if (!el) return null;
                
                // Check for React component
                for (let key in el) {{
                    if (key.startsWith('__reactFiber') || key.startsWith('__reactInternalInstance')) {{
                        const fiber = el[key];
                        let component = fiber;
                        
                        // Walk up to find component (not DOM element)
                        while (component) {{
                            if (component.type && typeof component.type === 'function') {{
                                const componentName = component.type.name || 
                                                     component.type.displayName || 
                                                     'Anonymous';
                                
                                // Extract and normalize props
                                const normalizedProps = {{}};
                                if (component.memoizedProps) {{
                                    for (let propKey in component.memoizedProps) {{
                                        const value = component.memoizedProps[propKey];
                                        
                                        // Normalize dynamic values
                                        if (typeof value === 'string') {{
                                            if (value.match(/^\\d+$/)) normalizedProps[propKey] = ':number';
                                            else if (value.match(/^[a-f0-9-]{{36}}$/i)) normalizedProps[propKey] = ':uuid';
                                            else if (value.length > 50) normalizedProps[propKey] = ':string';
                                            else normalizedProps[propKey] = value;
                                        }} else if (typeof value === 'number') {{
                                            normalizedProps[propKey] = ':number';
                                        }} else if (typeof value === 'boolean') {{
                                            normalizedProps[propKey] = ':boolean';
                                        }} else if (typeof value === 'function') {{
                                            normalizedProps[propKey] = ':function';
                                        }}
                                    }}
                                }}
                                
                                // CONTEXT-AWARE: Check if navigation element
                                const classList = Array.from(el.classList);
                                const elementId = el.id || '';
                                const text = (el.textContent || '').trim().substring(0, 50);
                                
                                const isNavigationContext = 
                                    el.closest('.element-list, .left-pannel, [class*="sidebar"], [class*="menu"], nav, [class*="list"]') !== null ||
                                    /nav|menu|item-\\d+|sidebar/.test(elementId) ||
                                    /btn.*light|nav-item|menu-item/.test(classList.join(' '));
                                
                                // Create signature
                                let signature = componentName + ':' + JSON.stringify(normalizedProps);
                                
                                // NAVIGATION: Add unique ID + text to make distinct
                                if (isNavigationContext) {{
                                    if (elementId) {{
                                        signature += ':id=' + elementId;
                                    }}
                                    if (text.length > 0) {{
                                        const textHash = text.toLowerCase().replace(/\\s+/g, '_').substring(0, 20);
                                        signature += ':text=' + textHash;
                                    }}
                                }}
                                
                                return signature;
                            }}
                            component = component.return;
                        }}
                    }}
                }}
                
                // Check for Vue component
                if (el.__vueParentComponent || el.__vue__) {{
                    const vueInstance = el.__vueParentComponent || el.__vue__;
                    const componentName = vueInstance.$options?.name || 
                                         vueInstance.type?.name || 
                                         'VueComponent';
                    
                    // Normalize Vue props
                    const normalizedProps = {{}};
                    const props = vueInstance.props || vueInstance.$props || {{}};
                    
                    for (let key in props) {{
                        const value = props[key];
                        if (typeof value === 'string') {{
                            if (value.match(/^\\d+$/)) normalizedProps[key] = ':number';
                            else if (value.match(/^[a-f0-9-]{{36}}$/i)) normalizedProps[key] = ':uuid';
                            else normalizedProps[key] = ':string';
                        }} else if (typeof value === 'number') {{
                            normalizedProps[key] = ':number';
                        }}
                    }}
                    
                    return componentName + ':' + JSON.stringify(normalizedProps);
                }}
                
                // ========================================
                // FALLBACK: Smart context-aware signature
                // ========================================
                
                // Strategy: Different logic for navigation vs data elements
                const classList = Array.from(el.classList);
                const tag = el.tagName.toLowerCase();
                const elementId = el.id || '';
                const text = (el.textContent || '').trim().substring(0, 50);
                
                // CONTEXT DETECTION
                // Navigation elements: sidebar, menu items with unique IDs/text
                const isNavigationContext = 
                    el.closest('.element-list, .left-pannel, [class*="sidebar"], [class*="menu"], nav, [class*="list"]') !== null ||
                    /nav|menu|item-\d+|sidebar/.test(elementId) ||
                    /btn.*light|nav-item|menu-item/.test(classList.join(' '));
                
                // Data elements: product cards, user cards with dynamic IDs
                const isDataContext = 
                    /card|product|user|post|article|listing/.test(classList.join(' ')) &&
                    !isNavigationContext;  // Navigation takes priority
                
                // Check data attributes
                const dataAttrs = {{}};
                for (let attr of el.attributes) {{
                    if (attr.name.startsWith('data-')) {{
                        const value = attr.value;
                        if (value.match(/^\\d+$/)) {{
                            dataAttrs[attr.name] = ':number';
                        }} else if (value.match(/^[a-f0-9-]{{36}}$/i)) {{
                            dataAttrs[attr.name] = ':uuid';
                        }} else if (value.length > 20) {{
                            dataAttrs[attr.name] = ':string';
                        }} else {{
                            dataAttrs[attr.name] = value;
                        }}
                    }}
                }}
                
                // BUILD SIGNATURE
                let signature = tag;
                
                // Add class
                if (classList.length > 0) {{
                    signature += ':' + classList[0];
                }}
                
                // NAVIGATION: Include ID + text (keep unique)
                if (isNavigationContext) {{
                    if (elementId) {{
                        signature += ':id=' + elementId;
                    }}
                    if (text.length > 0) {{
                        const textHash = text.toLowerCase().replace(/\s+/g, '_').substring(0, 20);
                        signature += ':text=' + textHash;
                    }}
                }}
                // DATA: Normalize IDs (treat as duplicates)
                else if (isDataContext) {{
                    if (elementId) {{
                        let normalizedId = elementId;
                        if (/\d+/.test(normalizedId)) {{
                            normalizedId = normalizedId.replace(/\d+/g, ':number');
                        }}
                        signature += ':id=' + normalizedId;
                    }}
                }}
                // DEFAULT: Include ID if not numeric
                else {{
                    if (elementId && !/^\d+$/.test(elementId)) {{
                        signature += ':id=' + elementId;
                    }}
                }}
                
                // Add data attributes
                if (Object.keys(dataAttrs).length > 0) {{
                    signature += ':data=' + JSON.stringify(dataAttrs);
                }}
                
                // Add href for links
                if (tag === 'a' && el.href) {{
                    const href = el.href;
                    let hrefPattern = href;
                    
                    const hasNumericId = /\/\d+($|\/)/.test(hrefPattern);
                    const hasUuid = /[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/i.test(hrefPattern);
                    
                    if (hasNumericId) {{
                        hrefPattern = hrefPattern.replace(/\/\d+/g, '/:id');
                    }}
                    if (hasUuid) {{
                        hrefPattern = hrefPattern.replace(/[a-f0-9]{{8}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{4}}-[a-f0-9]{{12}}/gi, ':uuid');
                    }}
                    
                    signature += ':href=' + hrefPattern;
                }}
                
                return signature || null;
            }} catch (e) {{
                return null;
            }}
        }}
        """
        
        try:
            signature = await page.evaluate(js_code, selector)
            return signature or ""
        except Exception as e:
            logger.debug(f"Component signature error: {e}")
            return ""
    
    def _build_selector(self, element: Dict) -> str:
        """Build CSS selector for element"""
        # Try href (for links)
        if element.get('href'):
            return f"a[href='{element['href']}']"
        
        # Try ID
        if element.get('id'):
            return f"#{element['id']}"
        
        # Try class
        if element.get('class'):
            classes = str(element['class']).split()
            if classes:
                return f"{element['tag'].lower()}.{classes[0]}"
        
        # Fallback to text
        text = element.get('text', '').replace("'", "\\'")
        if text and len(text) > 2:
            return f"{element['tag'].lower()}:has-text('{text[:30]}')"
        
        return ""
