"""
Component-Based State Manager
Uses browser DevTools API to detect React/Vue components and normalize them
Treats components as the primary unit of state (not HTML or URLs)
"""
import hashlib
import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from playwright.async_api import Page
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class ComponentState:
    """Represents a normalized component state"""
    component_id: str  # Normalized ID
    component_name: str  # React/Vue component name
    component_type: str  # 'react' | 'vue' | 'angular' | 'generic'
    props: Dict  # Normalized props (dynamic values replaced)
    children_count: int
    has_navigation: bool
    url: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ComponentStateManager:
    """
    Component-based state management using browser DevTools API
    Normalizes components to prevent millions of duplicate states
    """
    
    def __init__(self):
        """Initialize component state manager"""
        self.seen_components: Set[str] = set()  # Normalized component IDs
        self.component_states: Dict[str, ComponentState] = {}
        self.url_to_components: Dict[str, List[str]] = {}
        
        logger.info("ComponentStateManager initialized (DevTools-based)")
    
    async def detect_components_via_devtools(self, page: Page) -> List[Dict]:
        """
        Use browser DevTools API to detect React/Vue/Angular components
        This is how React DevTools actually works!
        
        Args:
            page: Playwright page object
        
        Returns:
            List of detected components with their structure
        """
        js_code = """
        () => {
            const components = [];
            
            // ========================================
            // 1. REACT COMPONENT DETECTION (Real DevTools Method)
            // ========================================
            
            // Check for React Fiber (React 16+)
            const findReactFiber = (el) => {
                for (let key in el) {
                    if (key.startsWith('__reactFiber') || key.startsWith('__reactInternalInstance')) {
                        return el[key];
                    }
                }
                return null;
            };
            
            // Get React components from DOM
            const getAllReactComponents = () => {
                const reactComponents = [];
                const allElements = document.querySelectorAll('*');
                
                allElements.forEach(el => {
                    const fiber = findReactFiber(el);
                    if (fiber) {
                        let component = fiber;
                        while (component) {
                            if (component.type && typeof component.type === 'function') {
                                const componentName = component.type.name || component.type.displayName || 'Anonymous';
                                
                                // Extract props (normalize dynamic values)
                                const props = {};
                                if (component.memoizedProps) {
                                    for (let key in component.memoizedProps) {
                                        const value = component.memoizedProps[key];
                                        
                                        // Normalize dynamic values
                                        if (typeof value === 'string') {
                                            // Keep structure, replace specific values
                                            if (value.match(/^\\d+$/)) props[key] = ':number';
                                            else if (value.match(/^[a-f0-9-]{36}$/i)) props[key] = ':uuid';
                                            else if (value.length > 50) props[key] = ':long_string';
                                            else props[key] = value;
                                        } else if (typeof value === 'number') {
                                            props[key] = ':number';
                                        } else if (typeof value === 'boolean') {
                                            props[key] = value;
                                        } else if (value === null || value === undefined) {
                                            props[key] = ':null';
                                        } else if (typeof value === 'function') {
                                            props[key] = ':function';
                                        } else if (typeof value === 'object') {
                                            props[key] = ':object';
                                        }
                                    }
                                }
                                
                                // Count children
                                let childCount = 0;
                                if (component.child) {
                                    let child = component.child;
                                    while (child) {
                                        childCount++;
                                        child = child.sibling;
                                    }
                                }
                                
                                // Check if component has navigation elements
                                const hasNav = el.querySelector('a, button, [role="button"], [onclick]') !== null;
                                
                                reactComponents.push({
                                    name: componentName,
                                    type: 'react',
                                    props: props,
                                    children: childCount,
                                    hasNavigation: hasNav,
                                    element: el.tagName.toLowerCase()
                                });
                            }
                            component = component.return;
                        }
                    }
                });
                
                return reactComponents;
            };
            
            // ========================================
            // 2. VUE COMPONENT DETECTION (Real DevTools Method)
            // ========================================
            
            const getAllVueComponents = () => {
                const vueComponents = [];
                
                // Vue 3 detection
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    // Vue 3 attaches __vueParentComponent
                    if (el.__vueParentComponent) {
                        const vueInstance = el.__vueParentComponent;
                        const componentName = vueInstance.type?.name || vueInstance.type?.__name || 'Anonymous';
                        
                        const props = {};
                        if (vueInstance.props) {
                            for (let key in vueInstance.props) {
                                const value = vueInstance.props[key];
                                // Same normalization as React
                                if (typeof value === 'string' && value.match(/^\\d+$/)) {
                                    props[key] = ':number';
                                } else {
                                    props[key] = typeof value;
                                }
                            }
                        }
                        
                        const hasNav = el.querySelector('a, button, [role="button"]') !== null;
                        
                        vueComponents.push({
                            name: componentName,
                            type: 'vue',
                            props: props,
                            children: el.children.length,
                            hasNavigation: hasNav,
                            element: el.tagName.toLowerCase()
                        });
                    }
                    
                    // Vue 2 detection (__vue__)
                    if (el.__vue__) {
                        const vueInstance = el.__vue__;
                        const componentName = vueInstance.$options?.name || vueInstance.$options?._componentTag || 'Anonymous';
                        
                        vueComponents.push({
                            name: componentName,
                            type: 'vue',
                            props: vueInstance.$props || {},
                            children: el.children.length,
                            hasNavigation: el.querySelector('a, button') !== null,
                            element: el.tagName.toLowerCase()
                        });
                    }
                });
                
                return vueComponents;
            };
            
            // ========================================
            // 3. ANGULAR COMPONENT DETECTION
            // ========================================
            
            const getAllAngularComponents = () => {
                const angularComponents = [];
                
                const allElements = document.querySelectorAll('*');
                allElements.forEach(el => {
                    // Angular attaches __ngContext__
                    if (el.__ngContext__) {
                        const context = el.__ngContext__;
                        
                        angularComponents.push({
                            name: el.tagName.toLowerCase().replace('-', ''),
                            type: 'angular',
                            props: {},
                            children: el.children.length,
                            hasNavigation: el.querySelector('a, button') !== null,
                            element: el.tagName.toLowerCase()
                        });
                    }
                });
                
                return angularComponents;
            };
            
            // ========================================
            // 4. DETECT ALL COMPONENTS
            // ========================================
            
            try {
                components.push(...getAllReactComponents());
            } catch (e) {
                console.log('React detection error:', e);
            }
            
            try {
                components.push(...getAllVueComponents());
            } catch (e) {
                console.log('Vue detection error:', e);
            }
            
            try {
                components.push(...getAllAngularComponents());
            } catch (e) {
                console.log('Angular detection error:', e);
            }
            
            // Deduplicate by component signature
            const seen = new Set();
            const uniqueComponents = components.filter(comp => {
                const signature = JSON.stringify({
                    name: comp.name,
                    type: comp.type,
                    props: comp.props
                });
                
                if (seen.has(signature)) {
                    return false;
                }
                seen.add(signature);
                return true;
            });
            
            return uniqueComponents;
        }
        """
        
        try:
            components = await page.evaluate(js_code)
            
            logger.info(f"🔍 Detected {len(components)} unique components via DevTools")
            
            # Log framework breakdown
            react_count = sum(1 for c in components if c['type'] == 'react')
            vue_count = sum(1 for c in components if c['type'] == 'vue')
            angular_count = sum(1 for c in components if c['type'] == 'angular')
            
            if react_count:
                logger.info(f"  ⚛️  React: {react_count} components")
            if vue_count:
                logger.info(f"  🟢 Vue: {vue_count} components")
            if angular_count:
                logger.info(f"  🅰️  Angular: {angular_count} components")
            
            return components
        
        except Exception as e:
            logger.error(f"DevTools component detection error: {e}")
            return []
    
    def normalize_component(self, component: Dict) -> str:
        """
        Normalize component to prevent millions of duplicate states
        
        Component normalization:
        - Same component name + normalized props = same component
        - Dynamic values in props are replaced with placeholders
        
        Args:
            component: Component dict from DevTools
        
        Returns:
            Normalized component ID (hash)
        """
        # Create normalized signature
        signature = {
            'name': component['name'],
            'type': component['type'],
            'props': component.get('props', {}),  # Already normalized in JS
            'has_navigation': component.get('hasNavigation', False)
        }
        
        # Generate hash from signature
        signature_str = json.dumps(signature, sort_keys=True)
        component_hash = hashlib.sha256(signature_str.encode()).hexdigest()[:8]
        
        return component_hash
    
    async def analyze_page_components(self, page: Page, url: str) -> List[ComponentState]:
        """
        Analyze page and extract normalized component states
        
        Args:
            page: Playwright page object
            url: Current URL
        
        Returns:
            List of new (unseen) component states
        """
        # Detect all components via DevTools
        components = await self.detect_components_via_devtools(page)
        
        new_components = []
        
        for comp in components:
            # Normalize component
            comp_id = self.normalize_component(comp)
            
            # Check if we've seen this component before
            if comp_id in self.seen_components:
                logger.debug(f"⏭️  Skipping duplicate component: {comp['name']}")
                continue
            
            # New component!
            self.seen_components.add(comp_id)
            
            # Create component state
            comp_state = ComponentState(
                component_id=comp_id,
                component_name=comp['name'],
                component_type=comp['type'],
                props=comp.get('props', {}),
                children_count=comp.get('children', 0),
                has_navigation=comp.get('hasNavigation', False),
                url=url
            )
            
            self.component_states[comp_id] = comp_state
            
            # Track URL -> components mapping
            if url not in self.url_to_components:
                self.url_to_components[url] = []
            self.url_to_components[url].append(comp_id)
            
            new_components.append(comp_state)
            
            logger.info(f"✅ New {comp['type']} component: {comp['name']} ({comp_id})")
        
        return new_components
    
    def get_navigation_components(self) -> List[ComponentState]:
        """
        Get all components that have navigation elements
        These are the components we should interact with
        
        Returns:
            List of components with navigation
        """
        return [
            comp for comp in self.component_states.values()
            if comp.has_navigation
        ]
    
    def get_stats(self) -> Dict:
        """Get component statistics"""
        react_count = sum(1 for c in self.component_states.values() if c.component_type == 'react')
        vue_count = sum(1 for c in self.component_states.values() if c.component_type == 'vue')
        angular_count = sum(1 for c in self.component_states.values() if c.component_type == 'angular')
        nav_count = sum(1 for c in self.component_states.values() if c.has_navigation)
        
        return {
            'total_components': len(self.component_states),
            'react_components': react_count,
            'vue_components': vue_count,
            'angular_components': angular_count,
            'navigation_components': nav_count,
            'urls_analyzed': len(self.url_to_components)
        }
