"""
Equivalence Class Partitioning (ECP) Test Generator

Generates test cases by dividing input domains into equivalence classes
and testing representative values from each class.
"""

from typing import Dict, List, Any
import re
import logging
from test_generator.field_label_extractor import extract_field_label

logger = logging.getLogger(__name__)


class ECPGenerator:
    """Generate Equivalence Class Partitioning test cases"""
    
    def __init__(self):
        self.test_cases = []
    
    def _get_unique_field_id(self, input_field: Dict) -> str:
        """Generate unique field identifier using id and name attributes"""
        field_id = input_field.get('id', '')
        field_name = input_field.get('name', '')
        # Use field id if available, otherwise use name, or fallback to 'unknown'
        if field_id:
            return field_id
        elif field_name:
            return field_name
        else:
            # Use selector as last resort for uniqueness
            selector = input_field.get('selector', 'unknown')
            return selector.replace('[', '_').replace(']', '_').replace('"', '').replace(' ', '_')
    
    def generate(self, form_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate ECP test cases from form input data
        
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
            form_action = form.get('form_action', form.get('action', 'N/A'))
            page_title = form.get('page_title', 'Unknown Page')
            
            # Create context dictionary
            form_context = {
                'url': form_url,
                'id': form_id,
                'action': form_action,
                'title': page_title
            }
            
            for input_field in form.get('inputs', []):
                test_cases = self._generate_for_input(input_field, form_context)
                self.test_cases.extend(test_cases)
        
        logger.info(f"Generated {len(self.test_cases)} ECP test cases")
        return self.test_cases
    
    def _generate_for_input(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for a single input field - GENERIC for all types"""
        field_type = (input_field.get('type') or 'text').lower()
        field_name = input_field.get('name') or 'unknown'
        field_unique_id = self._get_unique_field_id(input_field)
        pattern = input_field.get('pattern')
        
        test_cases = []
        
        # Email inputs
        if field_type == 'email':
            test_cases = self._generate_email_ecp(input_field, form_context)
        
        # URL inputs
        elif field_type == 'url':
            test_cases = self._generate_url_ecp(input_field, form_context)
        
        # Phone inputs
        elif field_type == 'tel':
            test_cases = self._generate_phone_ecp(input_field, form_context)
        
        # Date/Time inputs (HTML5)
        elif field_type in ['date', 'datetime-local', 'month', 'week', 'time']:
            test_cases = self._generate_datetime_ecp(input_field, form_context)
        
        # Number/Range inputs
        elif field_type in ['number', 'range']:
            test_cases = self._generate_numeric_ecp(input_field, form_context)
        
        # Color inputs
        elif field_type == 'color':
            test_cases = self._generate_color_ecp(input_field, form_context)
        
        # Text with pattern
        elif pattern and pattern != 'null':
            test_cases = self._generate_pattern_ecp(input_field, form_context)
        
        # Select/dropdown
        elif field_type in ['select', 'select-one', 'select-multiple']:
            test_cases = self._generate_select_ecp(input_field, form_context)
        
        # Checkbox/Radio
        elif field_type in ['checkbox', 'radio']:
            test_cases = self._generate_boolean_ecp(input_field, form_context)
        
        # File upload
        elif field_type == 'file':
            test_cases = self._generate_file_ecp(input_field, form_context)
        
        # Generic text fields (FALLBACK for any unknown type)
        elif field_type not in ['submit', 'button', 'hidden', 'reset', 'image']:
            test_cases = self._generate_text_ecp(input_field, form_context)
        
        return test_cases
    
    def _generate_email_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for email inputs"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        
        # Equivalence classes for email
        test_classes = [
            # Valid classes
            {
                'class': 'valid_standard',
                'values': ['user@example.com', 'test@domain.co.uk'],
                'expected': 'success',
                'description': 'Valid standard email format'
            },
            {
                'class': 'valid_with_plus',
                'values': ['user+tag@example.com', 'test+filter@domain.com'],
                'expected': 'success',
                'description': 'Valid email with plus addressing'
            },
            {
                'class': 'valid_with_dots',
                'values': ['first.last@example.com', 'user.name@domain.org'],
                'expected': 'success',
                'description': 'Valid email with dots in local part'
            },
            {
                'class': 'valid_subdomain',
                'values': ['user@mail.example.com', 'test@subdomain.domain.com'],
                'expected': 'success',
                'description': 'Valid email with subdomain'
            },
            # Invalid classes
            {
                'class': 'invalid_missing_at',
                'values': ['userexample.com', 'test.domain.com'],
                'expected': 'error',
                'description': 'Missing @ symbol'
            },
            {
                'class': 'invalid_missing_domain',
                'values': ['user@', 'test@.com'],
                'expected': 'error',
                'description': 'Missing or invalid domain'
            },
            {
                'class': 'invalid_special_chars',
                'values': ['user..name@example.com', '.user@example.com'],
                'expected': 'error',
                'description': 'Invalid format: consecutive dots / leading dot (rejected by HTML5)'
            },
            {
                'class': 'invalid_empty',
                'values': ['', '   '],
                'expected': 'error',
                'description': 'Empty or whitespace only'
            },
            {
                'class': 'invalid_spaces',
                'values': ['user name@example.com', 'test @domain.com'],
                'expected': 'error',
                'description': 'Contains spaces'
            }
        ]
        
        test_cases = []
        for test_class in test_classes:
            for idx, value in enumerate(test_class['values']):
                test_cases.append({
                    'id': f"ecp_email_{form_context['id']}_{field_unique_id}_{test_class['class']}_{idx}",
                    'type': 'ECP',
                    'subtype': 'email',
                    'form_url': form_context['url'],
                    'form_id': form_context['id'],
                    'field_name': field_name,
                    'field_type': 'email',
                    'equivalence_class': test_class['class'],
                    'test_value': value,
                    'expected_result': test_class['expected'],
                    'description': test_class['description'],
                    'test_data': {
                        field_name: value
                    }
                })
        
        return test_cases
    
    def _generate_url_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for URL inputs"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        
        test_classes = [
            # Valid classes
            {
                'class': 'valid_http',
                'values': ['http://example.com', 'http://www.example.com'],
                'expected': 'success',
                'description': 'Valid HTTP URL'
            },
            {
                'class': 'valid_https',
                'values': ['https://example.com', 'https://secure.domain.com'],
                'expected': 'success',
                'description': 'Valid HTTPS URL'
            },
            {
                'class': 'valid_with_path',
                'values': ['https://example.com/path/to/page', 'http://domain.com/api/v1'],
                'expected': 'success',
                'description': 'Valid URL with path'
            },
            {
                'class': 'valid_with_query',
                'values': ['https://example.com?key=value', 'http://domain.com?id=123&name=test'],
                'expected': 'success',
                'description': 'Valid URL with query parameters'
            },
            # Invalid classes
            {
                'class': 'invalid_no_protocol',
                'values': ['example.com', 'www.domain.com'],
                'expected': 'error',
                'description': 'Missing protocol (http/https)'
            },
            {
                'class': 'invalid_format',
                'values': ['not-a-url', 'http:/invalid'],
                'expected': 'error',
                'description': 'Invalid URL format'
            },
            {
                'class': 'invalid_empty',
                'values': ['', '   '],
                'expected': 'error',
                'description': 'Empty or whitespace only'
            }
        ]
        
        test_cases = []
        for test_class in test_classes:
            for idx, value in enumerate(test_class['values']):
                test_cases.append({
                    'id': f"ecp_url_{form_context['id']}_{field_unique_id}_{test_class['class']}_{idx}",
                    'type': 'ECP',
                    'subtype': 'url',
                    'form_url': form_context['url'],
                    'form_id': form_context['id'],
                    'field_name': field_name,
                    'field_type': 'url',
                    'equivalence_class': test_class['class'],
                    'test_value': value,
                    'expected_result': test_class['expected'],
                    'description': test_class['description'],
                    'test_data': {
                        field_name: value
                    }
                })
        
        return test_cases
    
    def _generate_phone_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for phone inputs"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        
        test_classes = [
            # Valid classes
            {
                'class': 'valid_us_format',
                'values': ['555-123-4567', '(555) 123-4567'],
                'expected': 'success',
                'description': 'Valid US phone format'
            },
            {
                'class': 'valid_international',
                'values': ['+1-555-123-4567', '+44 20 7946 0958'],
                'expected': 'success',
                'description': 'Valid international format'
            },
            {
                'class': 'valid_digits_only',
                'values': ['5551234567', '15551234567'],
                'expected': 'success',
                'description': 'Valid digits only format'
            },
            # Invalid classes
            {
                'class': 'invalid_too_short',
                'values': ['123', '55512'],
                'expected': 'error',
                'description': 'Too few digits'
            },
            {
                'class': 'invalid_letters',
                'values': ['555-CALL-NOW', 'ABC-1234567'],
                'expected': 'error',
                'description': 'Contains letters'
            },
            {
                'class': 'invalid_empty',
                'values': ['', '   '],
                'expected': 'error',
                'description': 'Empty or whitespace only'
            }
        ]
        
        test_cases = []
        for test_class in test_classes:
            for idx, value in enumerate(test_class['values']):
                test_cases.append({
                    'id': f"ecp_phone_{form_context['id']}_{field_unique_id}_{test_class['class']}_{idx}",
                    'type': 'ECP',
                    'subtype': 'phone',
                    'form_url': form_context['url'],
                    'form_id': form_context['id'],
                    'field_name': field_name,
                    'field_type': 'tel',
                    'equivalence_class': test_class['class'],
                    'test_value': value,
                    'expected_result': test_class['expected'],
                    'description': test_class['description'],
                    'test_data': {
                        field_name: value
                    }
                })
        
        return test_cases
    
    def _generate_pattern_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for inputs with pattern attribute"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        pattern = input_field.get('pattern', '')
        
        # Try to determine what the pattern validates
        test_cases = []
        
        # Zipcode pattern
        if re.search(r'\\d\{5\}', pattern) or 'zip' in field_name.lower():
            test_classes = [
                {
                    'class': 'valid_zipcode',
                    'values': ['12345', '90210', '10001'],
                    'expected': 'success',
                    'description': 'Valid 5-digit zipcode'
                },
                {
                    'class': 'invalid_too_short',
                    'values': ['1234', '123'],
                    'expected': 'error',
                    'description': 'Less than 5 digits'
                },
                {
                    'class': 'invalid_too_long',
                    'values': ['123456', '1234567'],
                    'expected': 'error',
                    'description': 'More than 5 digits'
                },
                {
                    'class': 'invalid_letters',
                    'values': ['ABCDE', '12A45'],
                    'expected': 'error',
                    'description': 'Contains letters'
                }
            ]
        else:
            # Generic pattern testing
            test_classes = [
                {
                    'class': 'valid_pattern',
                    'values': ['validInput123'],
                    'expected': 'success',
                    'description': 'Matches pattern'
                },
                {
                    'class': 'invalid_pattern',
                    'values': ['<invalid>', '!@#$%'],
                    'expected': 'error',
                    'description': 'Does not match pattern'
                }
            ]
        
        for test_class in test_classes:
            for idx, value in enumerate(test_class['values']):
                test_cases.append({
                    'id': f"ecp_pattern_{form_context['id']}_{field_unique_id}_{test_class['class']}_{idx}",
                    'type': 'ECP',
                    'subtype': 'pattern',
                    'form_url': form_context['url'],
                    'form_id': form_context['id'],
                    'field_name': field_name,
                    'field_type': input_field.get('type'),
                    'equivalence_class': test_class['class'],
                    'test_value': value,
                    'expected_result': test_class['expected'],
                    'description': test_class['description'],
                    'test_data': {
                        field_name: value
                    },
                    'pattern': pattern
                })
        
        return test_cases
    
    def _generate_select_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for select/dropdown inputs"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        options = input_field.get('options', [])
        
        test_cases = []
        
        if not options:
            return test_cases
        
        # Test first, middle, and last options
        if len(options) > 0:
            test_cases.append({
                'id': f"ecp_select_{form_context['id']}_{field_unique_id}_first",
                'type': 'ECP',
                'subtype': 'select',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'field_name': field_name,
                'field_type': 'select',
                'equivalence_class': 'valid_first_option',
                'test_value': options[0],
                'expected_result': 'success',
                'description': 'Select first option',
                'test_data': {
                    field_name: options[0]
                }
            })
        
        if len(options) > 2:
            mid_idx = len(options) // 2
            test_cases.append({
                'id': f"ecp_select_{form_context['id']}_{field_unique_id}_middle",
                'type': 'ECP',
                'subtype': 'select',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'field_name': field_name,
                'field_type': 'select',
                'equivalence_class': 'valid_middle_option',
                'test_value': options[mid_idx],
                'expected_result': 'success',
                'description': 'Select middle option',
                'test_data': {
                    field_name: options[mid_idx]
                }
            })
        
        if len(options) > 1:
            test_cases.append({
                'id': f"ecp_select_{form_context['id']}_{field_unique_id}_last",
                'type': 'ECP',
                'subtype': 'select',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'field_name': field_name,
                'field_type': 'select',
                'equivalence_class': 'valid_last_option',
                'test_value': options[-1],
                'expected_result': 'success',
                'description': 'Select last option',
                'test_data': {
                    field_name: options[-1]
                }
            })
        
        return test_cases
    
    def _generate_boolean_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for checkbox/radio inputs"""
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_type = input_field.get('type')
        # Use generic field label extraction
        field_label = extract_field_label(input_field, form_context)
        field_id = input_field.get('id', '')
        
        # For radio buttons with labels (Male, Female, Other), use the label as the value
        if field_type == 'radio' and field_label and field_label.strip():
            test_value = field_label
            test_description = f'Select "{field_label}" option for {field_name}'
        else:
            test_value = True
            test_description = f'{field_type.capitalize()} checked/selected for {field_label or field_name}'
        
        test_cases = [
            {
                'id': f"ecp_boolean_{form_context['id']}_{field_unique_id}_{field_id}",
                'type': 'ECP',
                'subtype': 'boolean',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'form_action': form_context['action'],
                'page_title': form_context['title'],
                'field_name': field_name,
                'field_label': field_label,
                'field_type': field_type,
                'equivalence_class': 'selected' if field_type == 'radio' else 'checked',
                'test_value': test_value,
                'expected_result': 'success',
                'description': test_description,
                'test_data': {
                    field_name: test_value
                }
            }
        ]
        
        # For checkboxes, also test unchecked state
        if field_type == 'checkbox':
            test_cases.append({
                'id': f"ecp_boolean_{form_context['id']}_{field_unique_id}_{field_id}_unchecked",
                'type': 'ECP',
                'subtype': 'boolean',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'form_action': form_context['action'],
                'page_title': form_context['title'],
                'field_name': field_name,
                'field_label': field_label,
                'field_type': field_type,
                'equivalence_class': 'unchecked',
                'test_value': False,
                'expected_result': 'success',
                'description': f'Checkbox not checked',
                'test_data': {
                    field_name: False
                }
            })
        
        return test_cases
    
    def _generate_text_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP test cases for generic text/password inputs"""
        field_name = input_field.get('name', input_field.get('id', 'unknown'))
        field_unique_id = self._get_unique_field_id(input_field)
        field_type = input_field.get('type')
        required = input_field.get('required', False)
        # Use proper fallback chain for label
        field_label = extract_field_label(input_field, form_context)
        
        test_cases = []
        
        # Valid: Normal text input
        test_cases.append({
            'id': f"ecp_text_{form_context['id']}_{field_unique_id}_valid",
            'type': 'ECP',
            'subtype': 'text',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'form_action': form_context['action'],
            'page_title': form_context['title'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'valid_text',
            'test_value': 'ValidInput123',
            'expected_result': 'success',
            'description': f'Valid text input for {field_label}',
            'test_data': {
                field_name: 'ValidInput123'
            }
        })
        
        # Invalid: Empty (if required)
        if required:
            test_cases.append({
                'id': f"ecp_text_{form_context['id']}_{field_unique_id}_empty",
                'type': 'ECP',
                'subtype': 'text',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'form_action': form_context['action'],
                'page_title': form_context['title'],
                'field_label': field_label,
                'field_name': field_name,
                'field_type': field_type,
                'equivalence_class': 'empty_required',
                'test_value': '',
                'expected_result': 'error',
                'description': f'Empty value for required field {field_label}',
                'test_data': {
                    field_name: ''
                }
            })
        
        # Invalid: Special characters (potential XSS)
        test_cases.append({
            'id': f"ecp_text_{form_context['id']}_{field_unique_id}_special",
            'type': 'ECP',
            'subtype': 'text',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'form_action': form_context['action'],
            'page_title': form_context['title'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'special_characters',
            'test_value': '<script>alert("XSS")</script>',
            'expected_result': 'error',
            'description': f'Special characters/XSS attempt in {field_label}',
            'test_data': {
                field_name: '<script>alert("XSS")</script>'
            }
        })
        
        # Invalid: Very long text (server should reject input exceeding maxlength)
        test_cases.append({
            'id': f"ecp_text_{form_context['id']}_{field_unique_id}_long",
            'type': 'ECP',
            'subtype': 'text',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'form_action': form_context['action'],
            'page_title': form_context['title'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'long_text',
            'test_value': 'A' * 500,
            'expected_result': 'error',
            'description': f'Very long text input (500 chars) for {field_label} — should exceed server maxlength',
            'test_data': {
                field_name: 'A' * 500
            }
        })
        
        # Valid: Unicode characters
        # Build a unicode value that safely exceeds the field's minlength so it
        # is accepted by the server (server-side minlength may differ from the
        # HTML attribute, e.g. BUG-1 style mismatches).  We use at least 10
        # chars, or minlength+4 if larger, staying well inside any reasonable
        # maxlength (typically ≥15).
        _unicode_base = '测试数据🎉!'   # 6 distinct unicode/emoji chars
        _minlength = int(input_field.get('minlength') or 0)
        _needed = max(_minlength + 4, 10)
        unicode_val = (_unicode_base * ((_needed // len(_unicode_base)) + 1))[:_needed]
        test_cases.append({
            'id': f"ecp_text_{form_context['id']}_{field_unique_id}_unicode",
            'type': 'ECP',
            'subtype': 'text',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'form_action': form_context['action'],
            'page_title': form_context['title'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'unicode',
            'test_value': unicode_val,
            'expected_result': 'success',
            'description': f'Unicode characters in {field_label}',
            'test_data': {
                field_name: unicode_val
            }
        })
        
        return test_cases
    
    def _generate_datetime_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP for date/time inputs"""
        from test_generator.field_label_extractor import extract_field_label
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_label = extract_field_label(input_field, form_context)
        field_type = input_field.get('type', 'date')
        
        test_cases = []
        formats = {
            'date': '2024-01-15',
            'datetime-local': '2024-01-15T14:30',
            'month': '2024-01',
            'week': '2024-W03',
            'time': '14:30'
        }
        
        valid_value = formats.get(field_type, '2024-01-15')
        
        # Valid date
        test_cases.append({
            'id': f"ecp_{field_type}_{form_context['id']}_{field_unique_id}_valid",
            'type': 'ECP',
            'subtype': field_type,
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'valid',
            'test_value': valid_value,
            'expected_result': 'success',
            'description': f'Valid {field_type} format for {field_label}',
            'test_data': {field_name: valid_value}
        })
        
        # Invalid format
        test_cases.append({
            'id': f"ecp_{field_type}_{form_context['id']}_{field_unique_id}_invalid",
            'type': 'ECP',
            'subtype': field_type,
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'invalid_format',
            'test_value': 'invalid-date',
            'expected_result': 'error',
            'description': f'Invalid format for {field_label}',
            'test_data': {field_name: 'invalid-date'}
        })
        
        return test_cases
    
    def _generate_numeric_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP for number/range inputs"""
        from test_generator.field_label_extractor import extract_field_label
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_label = extract_field_label(input_field, form_context)
        field_type = input_field.get('type', 'number')
        
        min_val = input_field.get('min', 0)
        max_val = input_field.get('max', 100)
        
        test_cases = []
        
        # Valid number in range
        try:
            valid_val = int((int(min_val) + int(max_val)) / 2) if min_val and max_val else 50
        except:
            valid_val = 50
            
        test_cases.append({
            'id': f"ecp_number_{form_context['id']}_{field_unique_id}_valid",
            'type': 'ECP',
            'subtype': 'number',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'valid_range',
            'test_value': valid_val,
            'expected_result': 'success',
            'description': f'Valid number in range for {field_label}',
            'test_data': {field_name: valid_val}
        })
        
        # Non-numeric
        test_cases.append({
            'id': f"ecp_number_{form_context['id']}_{field_unique_id}_invalid",
            'type': 'ECP',
            'subtype': 'number',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': field_type,
            'equivalence_class': 'non_numeric',
            'test_value': 'abc',
            'expected_result': 'error',
            'description': f'Non-numeric value for {field_label}',
            'test_data': {field_name: 'abc'}
        })
        
        return test_cases
    
    def _generate_color_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP for color inputs"""
        from test_generator.field_label_extractor import extract_field_label
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_label = extract_field_label(input_field, form_context)
        
        test_cases = []
        
        # Valid hex color
        test_cases.append({
            'id': f"ecp_color_{form_context['id']}_{field_unique_id}_valid",
            'type': 'ECP',
            'subtype': 'color',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': 'color',
            'equivalence_class': 'valid_hex',
            'test_value': '#FF5733',
            'expected_result': 'success',
            'description': f'Valid hex color for {field_label}',
            'test_data': {field_name: '#FF5733'}
        })
        
        # Invalid color
        test_cases.append({
            'id': f"ecp_color_{form_context['id']}_{field_unique_id}_invalid",
            'type': 'ECP',
            'subtype': 'color',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': 'color',
            'equivalence_class': 'invalid_format',
            'test_value': 'notacolor',
            'expected_result': 'error',
            'description': f'Invalid color format for {field_label}',
            'test_data': {field_name: 'notacolor'}
        })
        
        return test_cases
    
    def _generate_file_ecp(self, input_field: Dict, form_context: Dict) -> List[Dict]:
        """Generate ECP for file inputs"""
        from test_generator.field_label_extractor import extract_field_label
        field_name = input_field.get('name', 'unknown')
        field_unique_id = self._get_unique_field_id(input_field)
        field_label = extract_field_label(input_field, form_context)
        accept = input_field.get('accept', '*/*')
        
        test_cases = []
        
        # Valid file type
        test_cases.append({
            'id': f"ecp_file_{form_context['id']}_{field_unique_id}_valid",
            'type': 'ECP',
            'subtype': 'file',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': 'file',
            'equivalence_class': 'valid_file',
            'test_value': 'document.pdf',
            'expected_result': 'success',
            'description': f'Valid file upload for {field_label} (accepts: {accept})',
            'test_data': {field_name: 'document.pdf'}
        })
        
        # Large file
        test_cases.append({
            'id': f"ecp_file_{form_context['id']}_{field_unique_id}_large",
            'type': 'ECP',
            'subtype': 'file',
            'form_url': form_context['url'],
            'form_id': form_context['id'],
            'field_label': field_label,
            'field_name': field_name,
            'field_type': 'file',
            'equivalence_class': 'large_file',
            'test_value': 'large_file_10MB.zip',
            'expected_result': 'error_or_success',
            'description': f'Large file upload (10MB) for {field_label}',
            'test_data': {field_name: 'large_file_10MB.zip'}
        })
        
        return test_cases
