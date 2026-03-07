"""
Use Case Testing Generator

Generates end-to-end user scenario test cases based on common user workflows
(e.g., "Add product, apply coupon, checkout").
"""

from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class UseCaseGenerator:
    """Generate Use Case / End-to-End scenario test cases"""
    
    def __init__(self):
        self.test_cases = []

    # ── Helpers ────────────────────────────────────────────────────────────

    def _sample_form_data(self, inputs: List[Dict]) -> Dict:
        """
        Build a dict of sample valid field values from a list of input dicts.
        Used to populate test_data so the runner can actually fill the form.
        """
        sample = {}
        for inp in inputs:
            name = inp.get('name') or inp.get('id', '')
            if not name or inp.get('type') in ('submit', 'button', 'hidden', 'reset', 'image'):
                continue
            nl = name.lower()
            if 'email' in nl:
                sample[name] = 'test@example.com'
            elif 'password' in nl:
                sample[name] = 'TestPass1!'
            elif 'age' in nl:
                sample[name] = 30
            elif 'username' in nl or nl in ('name', 'user', 'login'):
                sample[name] = 'TestUser1'
            elif inp.get('type') == 'number':
                mn = inp.get('min', 1)
                mx = inp.get('max', 100)
                try:
                    sample[name] = int((int(mn) + int(mx)) / 2)
                except Exception:
                    sample[name] = 50
            else:
                sample[name] = 'TestValue'
        return sample

    def _sample_data_from_nodes(self, nodes: List[Dict]) -> Dict:
        """Extract sample field values from the first form found in nodes."""
        for node in nodes:
            for form in node.get('forms', []):
                sample = self._sample_form_data(form.get('inputs', []))
                if sample:
                    return sample
        return {}

    # ── Public entry point ─────────────────────────────────────────────────

    def generate(self, graph_data: Dict, form_data: Dict = None) -> List[Dict[str, Any]]:
        """
        Generate use case test cases from graph and form data
        
        Args:
            graph_data: Dictionary containing nodes and edges from crawler
            form_data: Optional dictionary containing form information
            
        Returns:
            List of test case dictionaries
        """
        self.test_cases = []
        
        if not graph_data:
            logger.warning("No graph data provided")
            return []
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Detect common e-commerce patterns
        self.test_cases.extend(self._generate_ecommerce_scenarios(nodes, edges))
        
        # Detect form submission workflows
        if form_data:
            self.test_cases.extend(self._generate_form_scenarios(form_data, nodes, edges))
        
        # Detect authentication workflows
        self.test_cases.extend(self._generate_auth_scenarios(nodes, edges, nodes))
        
        # Detect search workflows
        self.test_cases.extend(self._generate_search_scenarios(nodes, edges))
        
        logger.info(f"Generated {len(self.test_cases)} Use Case test cases")
        return self.test_cases
    
    def _generate_ecommerce_scenarios(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate e-commerce use case scenarios"""
        test_cases = []
        
        # Build URL list for pattern matching
        urls = [node.get('url', '') for node in nodes]
        
        # GENERIC: Detect ANY multi-step workflow (not just e-commerce)
        # Look for pages with forms that lead to other pages
        form_nodes = [n for n in nodes if len(n.get('forms', [])) > 0]
        multi_step = len(form_nodes) >= 2  # At least 2 form pages suggests a workflow
        
        # AI refinement will identify actual workflow type (e-commerce, booking, registration, etc.)
        has_product = multi_step
        has_cart = multi_step
        has_checkout = multi_step
        
        product_url = next((url for url in urls if 'product' in url.lower()), None)
        cart_url = next((url for url in urls if 'cart' in url.lower() or 'bag' in url.lower()), None)
        checkout_url = next((url for url in urls if 'checkout' in url.lower()), None)
        
        # Scenario 1: Complete Purchase Flow
        if has_product and has_cart and has_checkout:
            test_cases.append({
                'id': 'usecase_ecommerce_complete_purchase',
                'type': 'Use Case',
                'subtype': 'e-commerce',
                'scenario_name': 'Complete Purchase Flow',
                'steps': [
                    {
                        'step': 1,
                        'action': 'navigate',
                        'target': product_url,
                        'description': 'Navigate to product page',
                        'verification': 'Product page loaded successfully'
                    },
                    {
                        'step': 2,
                        'action': 'click',
                        'target': '.add-to-cart, .add-to-bag, [data-action="add-to-cart"]',
                        'description': 'Click Add to Cart button',
                        'verification': 'Product added to cart'
                    },
                    {
                        'step': 3,
                        'action': 'navigate',
                        'target': cart_url,
                        'description': 'Navigate to cart page',
                        'verification': 'Cart shows 1 item'
                    },
                    {
                        'step': 4,
                        'action': 'click',
                        'target': '.checkout-button, .proceed-to-checkout, [data-action="checkout"]',
                        'description': 'Proceed to checkout',
                        'verification': 'Checkout page loaded'
                    },
                    {
                        'step': 5,
                        'action': 'fill_form',
                        'target': 'checkout_form',
                        'description': 'Fill checkout form with shipping details',
                        'verification': 'Form validation passed'
                    },
                    {
                        'step': 6,
                        'action': 'submit',
                        'target': 'checkout_form',
                        'description': 'Submit order',
                        'verification': 'Order confirmation page displayed'
                    }
                ],
                'expected_result': 'success',
                'description': 'End-to-end purchase: Browse product → Add to cart → Checkout → Complete order',
                'preconditions': ['User not logged in', 'Empty cart'],
                'postconditions': ['Order placed', 'Cart empty']
            })
        
        # Scenario 2: Add Multiple Products
        if has_product and has_cart:
            test_cases.append({
                'id': 'usecase_ecommerce_multiple_products',
                'type': 'Use Case',
                'subtype': 'e-commerce',
                'scenario_name': 'Add Multiple Products to Cart',
                'steps': [
                    {
                        'step': 1,
                        'action': 'navigate',
                        'target': product_url,
                        'description': 'Navigate to first product',
                        'verification': 'Product page loaded'
                    },
                    {
                        'step': 2,
                        'action': 'click',
                        'target': '.add-to-cart',
                        'description': 'Add first product to cart',
                        'verification': 'Cart count = 1'
                    },
                    {
                        'step': 3,
                        'action': 'navigate',
                        'target': product_url,
                        'description': 'Navigate to second product',
                        'verification': 'Different product page loaded'
                    },
                    {
                        'step': 4,
                        'action': 'click',
                        'target': '.add-to-cart',
                        'description': 'Add second product to cart',
                        'verification': 'Cart count = 2'
                    },
                    {
                        'step': 5,
                        'action': 'navigate',
                        'target': cart_url,
                        'description': 'View cart',
                        'verification': 'Cart shows 2 items'
                    }
                ],
                'expected_result': 'success',
                'description': 'Add multiple products: Add product 1 → Add product 2 → View cart',
                'preconditions': ['Empty cart'],
                'postconditions': ['Cart contains 2 items']
            })
        
        # Scenario 3: Remove from Cart
        if has_cart:
            test_cases.append({
                'id': 'usecase_ecommerce_remove_from_cart',
                'type': 'Use Case',
                'subtype': 'e-commerce',
                'scenario_name': 'Remove Item from Cart',
                'steps': [
                    {
                        'step': 1,
                        'action': 'navigate',
                        'target': cart_url,
                        'description': 'Navigate to cart page',
                        'verification': 'Cart page loaded with items'
                    },
                    {
                        'step': 2,
                        'action': 'click',
                        'target': '.remove-item, .delete-item, [data-action="remove"]',
                        'description': 'Click remove item button',
                        'verification': 'Item removed from cart'
                    },
                    {
                        'step': 3,
                        'action': 'verify',
                        'description': 'Verify cart updated',
                        'verification': 'Cart count decreased by 1'
                    }
                ],
                'expected_result': 'success',
                'description': 'Remove item from cart: View cart → Remove item → Verify removal',
                'preconditions': ['Cart has at least 1 item'],
                'postconditions': ['Item removed from cart']
            })
        
        return test_cases
    
    def _generate_form_scenarios(self, form_data: Dict, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate form submission use case scenarios"""
        test_cases = []
        
        if not form_data or 'forms' not in form_data:
            return []
        
        for form in form_data.get('forms', [])[:5]:  # Limit to 5 forms
            form_url = form.get('url', 'unknown')
            form_id = form.get('id', 'unknown')
            form_type = self._detect_form_type(form)
            
            # Generate scenario based on form type
            if form_type == 'contact':
                test_cases.append(self._generate_contact_form_scenario(form, form_url, form_id))
            elif form_type == 'registration':
                test_cases.append(self._generate_registration_scenario(form, form_url, form_id))
            elif form_type == 'search':
                test_cases.append(self._generate_search_form_scenario(form, form_url, form_id))
        
        return [tc for tc in test_cases if tc]  # Filter None values
    
    def _generate_auth_scenarios(self, nodes: List[Dict], edges: List[Dict], all_nodes: List[Dict] = None) -> List[Dict]:
        """Generate authentication workflow scenarios"""
        test_cases = []
        
        urls = [node.get('url', '') for node in nodes]
        sample_data = self._sample_data_from_nodes(all_nodes or nodes)
        
        # GENERIC: Detect forms with multiple steps (any workflow, not just login/register)
        # Look for multi-step forms across pages
        form_pages = [n for n in nodes if len(n.get('forms', [])) > 0]
        has_forms = len(form_pages) > 0
        
        # AI refinement will improve these generic scenarios with actual workflow names
        has_login = has_forms  # Generic: any form-based flow
        has_register = has_forms  # Will be refined by AI
        has_profile = len([n for n in nodes if len(n.get('links', [])) > 3]) > 0  # Pages with navigation
        
        if has_login:
            login_url = next((url for url in urls if 'login' in url.lower() or 'signin' in url.lower()), None)
            
            test_cases.append({
                'id': 'usecase_auth_login',
                'type': 'Use Case',
                'subtype': 'authentication',
                'scenario_name': 'User Login Flow',
                'form_url': login_url or (urls[0] if urls else ''),
                'test_data': sample_data,
                'steps': [
                    {
                        'step': 1,
                        'action': 'navigate',
                        'target': login_url,
                        'description': 'Navigate to login page',
                        'verification': 'Login form displayed'
                    },
                    {
                        'step': 2,
                        'action': 'fill',
                        'target': 'email',
                        'value': 'test@example.com',
                        'description': 'Enter email address',
                        'verification': 'Email field populated'
                    },
                    {
                        'step': 3,
                        'action': 'fill',
                        'target': 'password',
                        'value': 'Test123!@#',
                        'description': 'Enter password',
                        'verification': 'Password field populated'
                    },
                    {
                        'step': 4,
                        'action': 'submit',
                        'target': 'login_form',
                        'description': 'Submit login form',
                        'verification': 'Successfully logged in, redirected to dashboard/profile'
                    }
                ],
                'expected_result': 'success',
                'description': 'User login: Navigate to login → Enter credentials → Submit → Verify logged in',
                'preconditions': ['User not logged in', 'Valid credentials exist'],
                'postconditions': ['User logged in', 'Session created']
            })
        
        if has_register:
            register_url = next((url for url in urls if 'register' in url.lower() or 'signup' in url.lower()), None)
            
            test_cases.append({
                'id': 'usecase_auth_register',
                'type': 'Use Case',
                'subtype': 'authentication',
                'scenario_name': 'New User Registration',
                'form_url': register_url or (urls[0] if urls else ''),
                'test_data': sample_data,
                'steps': [
                    {
                        'step': 1,
                        'action': 'navigate',
                        'target': register_url,
                        'description': 'Navigate to registration page',
                        'verification': 'Registration form displayed'
                    },
                    {
                        'step': 2,
                        'action': 'fill_form',
                        'target': 'registration_form',
                        'description': 'Fill registration form',
                        'verification': 'All fields populated'
                    },
                    {
                        'step': 3,
                        'action': 'submit',
                        'target': 'registration_form',
                        'description': 'Submit registration',
                        'verification': 'Account created, confirmation message shown'
                    }
                ],
                'expected_result': 'success',
                'description': 'User registration: Navigate → Fill form → Submit → Verify account created',
                'preconditions': ['User not registered'],
                'postconditions': ['New account created', 'User logged in or verification email sent']
            })
        
        return test_cases
    
    def _generate_search_scenarios(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate search workflow scenarios"""
        test_cases = []
        
        urls = [node.get('url', '') for node in nodes]
        has_search = any('search' in url.lower() for url in urls)
        
        if has_search:
            test_cases.append({
                'id': 'usecase_search_basic',
                'type': 'Use Case',
                'subtype': 'search',
                'scenario_name': 'Basic Search Flow',
                'steps': [
                    {
                        'step': 1,
                        'action': 'locate',
                        'target': '.search-input, [type="search"], [name="search"], [name="q"]',
                        'description': 'Locate search input',
                        'verification': 'Search input visible'
                    },
                    {
                        'step': 2,
                        'action': 'fill',
                        'target': 'search',
                        'value': 'test query',
                        'description': 'Enter search query',
                        'verification': 'Query entered'
                    },
                    {
                        'step': 3,
                        'action': 'submit',
                        'target': 'search_form',
                        'description': 'Submit search',
                        'verification': 'Search results page loaded'
                    },
                    {
                        'step': 4,
                        'action': 'verify',
                        'description': 'Verify search results',
                        'verification': 'Results displayed matching query'
                    }
                ],
                'expected_result': 'success',
                'description': 'Search flow: Enter query → Submit → View results',
                'preconditions': [],
                'postconditions': ['Search results displayed']
            })
        
        return test_cases
    
    def _detect_form_type(self, form: Dict) -> str:
        """Detect form type based on field names and structure"""
        inputs = form.get('inputs', [])
        field_names = [(inp.get('name') or '').lower() for inp in inputs]
        
        # Contact form detection
        if any(name in field_names for name in ['message', 'subject', 'inquiry']):
            return 'contact'
        
        # Registration form detection
        if any(name in field_names for name in ['password', 'confirm_password', 'username']):
            return 'registration'
        
        # Search form detection
        if any(name in field_names for name in ['search', 'q', 'query']):
            return 'search'
        
        return 'generic'
    
    def _generate_contact_form_scenario(self, form: Dict, form_url: str, form_id: str) -> Dict:
        """Generate contact form scenario"""
        return {
            'id': f'usecase_contact_{form_id}',
            'type': 'Use Case',
            'subtype': 'form_submission',
            'scenario_name': 'Submit Contact Form',
            'steps': [
                {
                    'step': 1,
                    'action': 'navigate',
                    'target': form_url,
                    'description': 'Navigate to contact page',
                    'verification': 'Contact form displayed'
                },
                {
                    'step': 2,
                    'action': 'fill_form',
                    'target': form_id,
                    'description': 'Fill contact form fields',
                    'verification': 'All required fields populated'
                },
                {
                    'step': 3,
                    'action': 'submit',
                    'target': form_id,
                    'description': 'Submit contact form',
                    'verification': 'Success message displayed'
                }
            ],
            'expected_result': 'success',
            'description': 'Contact form submission: Navigate → Fill form → Submit → Verify confirmation',
            'form_url': form_url,
            'form_id': form_id,
            'preconditions': [],
            'postconditions': ['Form submitted', 'Confirmation message shown']
        }
    
    def _generate_registration_scenario(self, form: Dict, form_url: str, form_id: str) -> Dict:
        """Generate registration form scenario"""
        sample_data = self._sample_form_data(form.get('inputs', []))
        return {
            'id': f'usecase_registration_{form_id}',
            'type': 'Use Case',
            'subtype': 'form_submission',
            'scenario_name': 'User Registration',
            'form_url': form_url,
            'form_id': form_id,
            'test_data': sample_data,
            'steps': [
                {
                    'step': 1,
                    'action': 'navigate',
                    'target': form_url,
                    'description': 'Navigate to registration page',
                    'verification': 'Registration form displayed'
                },
                {
                    'step': 2,
                    'action': 'fill_form',
                    'target': form_id,
                    'description': 'Fill registration details',
                    'verification': 'All fields populated with valid data'
                },
                {
                    'step': 3,
                    'action': 'submit',
                    'target': form_id,
                    'description': 'Submit registration',
                    'verification': 'Account created successfully'
                }
            ],
            'expected_result': 'success',
            'description': 'Registration: Navigate → Fill form → Submit → Verify account created',
            'preconditions': ['User not registered'],
            'postconditions': ['Account created', 'User can log in']
        }
    
    def _generate_search_form_scenario(self, form: Dict, form_url: str, form_id: str) -> Dict:
        """Generate search form scenario"""
        return {
            'id': f'usecase_search_{form_id}',
            'type': 'Use Case',
            'subtype': 'form_submission',
            'scenario_name': 'Perform Search',
            'steps': [
                {
                    'step': 1,
                    'action': 'locate',
                    'target': form_id,
                    'description': 'Locate search form',
                    'verification': 'Search form visible'
                },
                {
                    'step': 2,
                    'action': 'fill',
                    'target': 'search',
                    'value': 'test query',
                    'description': 'Enter search query',
                    'verification': 'Query entered'
                },
                {
                    'step': 3,
                    'action': 'submit',
                    'target': form_id,
                    'description': 'Submit search',
                    'verification': 'Search results displayed'
                }
            ],
            'expected_result': 'success',
            'description': 'Search: Enter query → Submit → View results',
            'form_url': form_url,
            'form_id': form_id,
            'preconditions': [],
            'postconditions': ['Search results shown']
        }
