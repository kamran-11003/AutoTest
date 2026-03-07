"""
Shadow DOM Detector
Traverses Shadow DOM trees to find hidden interactive elements
"""
from typing import List, Dict
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class ShadowDOMDetector:
    """Detects and extracts elements from Shadow DOM"""
    
    async def extract_shadow_elements(self, page: Page) -> List[Dict]:
        """
        Recursively extract all interactive elements from Shadow DOM
        
        Returns:
            List of element dicts with shadow=True flag
        """
        js_code = """
        () => {
            const elements = [];
            
            // Recursive function to traverse shadow trees
            function traverseShadowDOM(root, path = []) {
                // Get all elements in current root
                const allElements = root.querySelectorAll('*');
                
                allElements.forEach((el, index) => {
                    // Check if element has shadow root
                    if (el.shadowRoot) {
                        // Recurse into shadow root
                        traverseShadowDOM(el.shadowRoot, [...path, `[shadow-host="${el.tagName.toLowerCase()}"]`, 'shadowRoot']);
                    }
                    
                    // Check if element is interactive
                    const isInteractive = (
                        el.tagName === 'A' ||
                        el.tagName === 'BUTTON' ||
                        el.tagName === 'INPUT' ||
                        el.getAttribute('role') === 'button' ||
                        el.onclick !== null ||
                        window.getComputedStyle(el).cursor === 'pointer'
                    );
                    
                    if (isInteractive) {
                        const rect = el.getBoundingClientRect();
                        const isVisible = rect.width > 0 && rect.height > 0 && el.offsetParent !== null;
                        
                        if (isVisible) {
                            elements.push({
                                tag: el.tagName,
                                text: (el.textContent || el.value || '').trim().substring(0, 50),
                                href: el.href || '',
                                type: el.type || '',
                                shadow: path.length > 0,
                                shadowPath: path.join(' > '),
                                selector: path.length > 0 
                                    ? path.join(' ') + ` > ${el.tagName.toLowerCase()}:nth-child(${index + 1})`
                                    : null
                            });
                        }
                    }
                });
            }
            
            // Start traversal from document root
            traverseShadowDOM(document);
            
            return elements;
        }
        """
        
        try:
            shadow_elements = await page.evaluate(js_code)
            shadow_count = len([e for e in shadow_elements if e.get('shadow')])
            if shadow_count > 0:
                logger.info(f"🌑 Found {shadow_count} elements in Shadow DOM")
            return shadow_elements
        except Exception as e:
            logger.error(f"Shadow DOM extraction error: {e}")
            return []
    
    async def click_shadow_element(self, page: Page, shadow_path: str) -> bool:
        """Click an element inside Shadow DOM using JavaScript"""
        js_code = f"""
        () => {{
            try {{
                // Parse shadow path: e.g., "[shadow-host='my-app'] > shadowRoot > button"
                const parts = "{shadow_path}".split(' > ');
                let current = document;
                
                for (const part of parts) {{
                    if (part === 'shadowRoot') {{
                        // Move into shadow root
                        current = current.shadowRoot;
                    }} else if (part.startsWith('[shadow-host=')) {{
                        // Find shadow host element
                        const tag = part.match(/shadow-host="([^"]+)"/)[1];
                        current = current.querySelector(tag);
                    }} else {{
                        // Regular CSS selector
                        current = current.querySelector(part);
                    }}
                    
                    if (!current) {{
                        console.error('Element not found in path:', part);
                        return false;
                    }}
                }}
                
                // Click the final element
                if (current && current.click) {{
                    current.click();
                    return true;
                }}
                return false;
            }} catch (e) {{
                console.error('Shadow DOM click error:', e);
                return false;
            }}
        }}
        """
        
        try:
            success = await page.evaluate(js_code)
            return success
        except Exception as e:
            logger.debug(f"Shadow element click error: {e}")
            return False
