"""
Boundary Value Analysis (BVA) Test Generator

Generates test cases for numeric, date, and length-constrained inputs
by testing min, max, just-inside, and just-outside boundaries.

Now with smart constraint defaults for fields without explicit constraints.
"""

from typing import Dict, List, Any
import logging
from test_generator.field_label_extractor import extract_field_label
from test_generator.constraint_manager import constraint_manager

logger = logging.getLogger(__name__)


class BVAGenerator:
    """Generate Boundary Value Analysis test cases"""
    
    def __init__(self):
        self.test_cases = []
    
    def _get_unique_field_id(self, input_field: Dict) -> str:
        """Generate unique field identifier using id and name attributes"""
        field_id = input_field.get('id', '')
        field_name = input_field.get('name', '')
        if field_id:
            return field_id
        elif field_name:
            return field_name
        else:
            selector = input_field.get('selector', 'unknown')
            return selector.replace('[', '_').replace(']', '_').replace('"', '').replace(' ', '_')
    
    def generate(self, form_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate BVA test cases from form input data
        
        Args:
            form_data: Dictionary containing form structure with inputs
            
        Returns:
            List of test case dictionaries
        """
        self.test_cases = []
        
        if not form_data or 'forms' not in form_data:
            logger.warning("No forms found in form_data")
            return []
        
        for form in form_data.get('forms', []):
            form_url = form.get('url', 'unknown')
            form_id = form.get('signature', form.get('id', 'unknown'))
            form_action = form.get('form_action', form.get('action', 'unknown'))
            page_title = form.get('page_title', 'Unknown Page')
            
            # Create context dictionary
            form_context = {
                'url': form_url,
                'id': form_id,
                'action': form_action,
                'title': page_title
            }
            
            # Test ALL inputs - no skipping (universal approach)
            form_inputs = form.get('inputs', [])
            
            for input_field in form_inputs:
                test_cases = self._generate_for_input(input_field, form_context)
                self.test_cases.extend(test_cases)
        
        logger.info(f"Generated {len(self.test_cases)} BVA test cases")
        return self.test_cases
    
    def _generate_for_input(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate BVA test cases for a single input field"""
        field_type = (input_field.get('type') or '').lower()
        field_name = input_field.get('name') or 'unknown'
        field_unique_id = self._get_unique_field_id(input_field)
        
        test_cases = []
        
        # SMART CONSTRAINT MANAGEMENT: Apply defaults if missing
        input_field = constraint_manager.apply_smart_defaults(input_field)
        
        # Check for numeric constraints (works for ANY field with min/max/step)
        has_numeric = (input_field.get('min') is not None or 
                      input_field.get('max') is not None or 
                      input_field.get('step') is not None or
                      field_type in ['number', 'range'])
        
        # Check for length constraints (works for ANY text-like field)
        has_length = (input_field.get('minlength') is not None or 
                     input_field.get('maxlength') is not None)
        
        # Generate based on what constraints exist (not field type)
        if has_numeric:
            test_cases = self._generate_numeric_bva(input_field, form_context)
        elif has_length:
            test_cases = self._generate_length_bva(input_field, form_context)
        elif field_type in ['date', 'datetime-local', 'month', 'week', 'time']:
            test_cases = self._generate_date_bva(input_field, form_context)
        # Default: treat unknown types as text with default length boundaries
        elif field_type not in ['checkbox', 'radio', 'submit', 'button', 'hidden', 'file', 'reset', 'image']:
            # Smart defaults already applied above
            test_cases = self._generate_length_bva(input_field, form_context)
        
        return test_cases
    
    def _generate_numeric_bva(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate BVA test cases for numeric inputs"""
        field_name = input_field.get('name', input_field.get('id', 'unnamed_field'))
        field_unique_id = self._get_unique_field_id(input_field)
        # Use generic field label extraction
        field_label = extract_field_label(input_field, form_context)
        min_val = input_field.get('min')
        max_val = input_field.get('max')
        step = input_field.get('step', 1)
        
        test_cases = []
        
        # Convert to numeric
        try:
            if min_val is not None:
                min_val = float(min_val)
            if max_val is not None:
                max_val = float(max_val)
            step = float(step) if step else 1
        except (ValueError, TypeError):
            logger.warning(f"Invalid numeric values for {field_name}")
            return []
        
        # Default values if not specified
        if min_val is None:
            min_val = 0
        if max_val is None:
            max_val = 100
        
        # Generate boundary test cases
        test_values = []
        
        # Below minimum
        test_values.append({
            'value': min_val - step,
            'expected': 'error',
            'description': f'Below minimum boundary ({min_val - step})'
        })
        
        # At minimum
        test_values.append({
            'value': min_val,
            'expected': 'success',
            'description': f'At minimum boundary ({min_val})'
        })
        
        # Just above minimum
        test_values.append({
            'value': min_val + step,
            'expected': 'success',
            'description': f'Just above minimum ({min_val + step})'
        })
        
        # Just below maximum
        test_values.append({
            'value': max_val - step,
            'expected': 'success',
            'description': f'Just below maximum ({max_val - step})'
        })
        
        # At maximum
        test_values.append({
            'value': max_val,
            'expected': 'success',
            'description': f'At maximum boundary ({max_val})'
        })
        
        # Above maximum
        test_values.append({
            'value': max_val + step,
            'expected': 'error',
            'description': f'Above maximum boundary ({max_val + step})'
        })
        
        # Create test case objects
        for idx, test_value in enumerate(test_values):
            test_cases.append({
                'id': f"bva_numeric_{form_context['id']}_{field_unique_id}_{idx}",
                'type': 'BVA',
                'subtype': 'numeric',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'form_action': form_context['action'],
                'page_title': form_context['title'],
                'field_name': field_name,
                'field_label': field_label,
                'field_type': input_field.get('type'),
                'test_value': test_value['value'],
                'expected_result': test_value['expected'],
                'description': f"{field_label or field_name}: {test_value['description']} on {form_context['title']}",
                'test_data': {
                    field_name: test_value['value']
                },
                'constraints': {
                    'min': min_val,
                    'max': max_val,
                    'step': step
                }
            })
        
        return test_cases
    
    def _generate_date_bva(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate BVA test cases for date inputs"""
        from datetime import datetime, timedelta
        
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        min_date = input_field.get('min')
        max_date = input_field.get('max')
        
        test_cases = []
        
        # Default date range (today to 1 year from now)
        if not min_date:
            min_date = datetime.now().strftime('%Y-%m-%d')
        if not max_date:
            max_date = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')
        
        try:
            min_dt = datetime.fromisoformat(min_date)
            max_dt = datetime.fromisoformat(max_date)
        except (ValueError, TypeError):
            logger.warning(f"Invalid date values for {field_name}")
            return []
        
        # Generate boundary test cases
        test_dates = [
            {
                'value': (min_dt - timedelta(days=1)).strftime('%Y-%m-%d'),
                'expected': 'error',
                'description': 'Before minimum date'
            },
            {
                'value': min_dt.strftime('%Y-%m-%d'),
                'expected': 'success',
                'description': 'At minimum date boundary'
            },
            {
                'value': (min_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
                'expected': 'success',
                'description': 'Just after minimum date'
            },
            {
                'value': (max_dt - timedelta(days=1)).strftime('%Y-%m-%d'),
                'expected': 'success',
                'description': 'Just before maximum date'
            },
            {
                'value': max_dt.strftime('%Y-%m-%d'),
                'expected': 'success',
                'description': 'At maximum date boundary'
            },
            {
                'value': (max_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
                'expected': 'error',
                'description': 'After maximum date'
            }
        ]
        
        for idx, test_date in enumerate(test_dates):
            test_cases.append({
                'id': f"bva_date_{form_context['id']}_{field_unique_id}_{idx}",
                'type': 'BVA',
                'subtype': 'date',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'field_name': field_name,
                'field_type': input_field.get('type'),
                'test_value': test_date['value'],
                'expected_result': test_date['expected'],
                'description': test_date['description'],
                'test_data': {
                    field_name: test_date['value']
                },
                'constraints': {
                    'min': min_date,
                    'max': max_date
                }
            })
        
        return test_cases
    
    def _email_of_length(self, n: int) -> str:
        """
        Build a syntactically valid email address of exactly n characters.
        Respects RFC 5321: local part ≤ 64 chars.
        For n < 5 (can't fit a valid email format) returns 'a'*n — intentionally
        invalid so the browser/server rejects it (these are 'error' test cases).

        Format: local@b×N.c  where local ≤ 64, domain length fills the rest.
        Minimum valid email: a@b.c = 5 chars (local=1, domain=3)
        """
        if n < 5:
            return 'a' * n          # no @ possible → browser rejects → error ✅
        # local@<domain>.c  — local part capped at 64 per RFC 5321
        # Structure: local + '@' + middle + '.c'  → n = len(local)+1+len(middle)+2
        # So len(middle) = n - len(local) - 3
        local_len = min(n - 4, 64)  # at most 64, need at least 1 char remaining for domain
        middle_len = n - local_len - 3  # accounts for '@' (1) + '.' (1) + 'c' (1)
        if middle_len < 1:
            # Shouldn't happen for n≥5, but fall back gracefully
            local_len = n - 4
            return 'a' * local_len + '@b.c'
        return 'a' * local_len + '@' + 'b' * middle_len + '.c'

    def _generate_length_bva(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate BVA test cases for text inputs with length constraints"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_type = (input_field.get('type') or '').lower()
        min_length = input_field.get('minlength', 0)
        max_length = input_field.get('maxlength', 255)
        
        try:
            min_length = int(min_length)
            max_length = int(max_length)
        except (ValueError, TypeError):
            logger.warning(f"Invalid length values for {field_name}")
            return []
        
        # Choose value builder based on field type.
        # Email fields need a valid format (user@domain) so the browser's HTML5
        # validator doesn't block submission before length is even checked.
        # For 'error' boundary cases (below min / above max) we still use plain
        # 'a'*N — the browser will reject regardless of format.
        def make_value(n: int) -> str:
            if field_type == 'email':
                return self._email_of_length(n)
            return 'a' * n if n >= 0 else ''

        test_cases = []
        
        # Generate test strings
        test_values = [
            {
                'value': make_value(min_length - 1) if min_length > 0 else '',
                'expected': 'error' if min_length > 0 else 'success',
                'description': f'Below minimum length ({min_length - 1} chars)'
            },
            {
                'value': make_value(min_length),
                'expected': 'success',
                'description': f'At minimum length ({min_length} chars)'
            },
            {
                'value': make_value(min_length + 1),
                'expected': 'success',
                'description': f'Just above minimum ({min_length + 1} chars)'
            },
            {
                'value': make_value(max_length - 1),
                'expected': 'success',
                'description': f'Just below maximum ({max_length - 1} chars)'
            },
            {
                'value': make_value(max_length),
                'expected': 'success',
                'description': f'At maximum length ({max_length} chars)'
            },
            {
                'value': make_value(max_length + 1),
                'expected': 'error',
                'description': f'Above maximum length ({max_length + 1} chars)'
            }
        ]
        
        for idx, test_value in enumerate(test_values):
            test_cases.append({
                'id': f"bva_length_{form_context['id']}_{field_unique_id}_{idx}",
                'type': 'BVA',
                'subtype': 'length',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'field_name': field_name,
                'field_type': input_field.get('type'),
                'test_value': test_value['value'],
                'expected_result': test_value['expected'],
                'description': test_value['description'],
                'test_data': {
                    field_name: test_value['value']
                },
                'constraints': {
                    'minlength': min_length,
                    'maxlength': max_length
                }
            })
        
        return test_cases
