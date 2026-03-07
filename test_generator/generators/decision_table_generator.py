"""
Decision Table Testing Generator

Generates test cases for combinations of inputs and conditions
using decision table technique.
"""

from typing import Dict, List, Any
import itertools
import logging

logger = logging.getLogger(__name__)


class DecisionTableGenerator:
    """Generate Decision Table test cases"""
    
    def __init__(self):
        self.test_cases = []
    
    def generate(self, form_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate decision table test cases from form input data
        
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
            
            # Find boolean/select fields that can be combined
            combinable_fields = self._find_combinable_fields(form.get('inputs', []))
            
            if len(combinable_fields) >= 2:
                test_cases = self._generate_combinations(combinable_fields, form_context)
                self.test_cases.extend(test_cases)
        
        logger.info(f"Generated {len(self.test_cases)} Decision Table test cases")
        return self.test_cases
    
    def _find_combinable_fields(self, inputs: List[Dict]) -> List[Dict]:
        """Find fields that can be used in decision table (boolean, select with few options)"""
        combinable = []
        
        # Group radio buttons by name
        radio_groups = {}
        checkbox_fields = []
        
        for input_field in inputs:
            field_type = (input_field.get('type') or '').lower()
            
            # Group radio buttons by name
            if field_type == 'radio':
                field_name = input_field.get('name', input_field.get('id', 'unknown'))
                if field_name not in radio_groups:
                    radio_groups[field_name] = []
                radio_groups[field_name].append(input_field)
            
            # Checkboxes are individual boolean fields
            elif field_type == 'checkbox':
                checkbox_fields.append(input_field)
            
            # Select with few options (max 5 for reasonable combinations)
            elif field_type == 'select':
                options = input_field.get('options', [])
                if 0 < len(options) <= 5:
                    combinable.append({
                        'field': input_field,
                        'name': input_field.get('name') or input_field.get('id', 'unknown'),
                        'label': input_field.get('label') or input_field.get('name') or input_field.get('id', 'Field'),
                        'values': options,
                        'field_type': 'select'
                    })
        
        # Add radio groups as single combinable fields with all their options
        for group_name, radios in radio_groups.items():
            if radios:
                # Get generic label from group (use first radio's context or name)
                group_label = None
                for radio in radios:
                    parent_label = radio.get('parent_label') or radio.get('group_label')
                    if parent_label:
                        group_label = parent_label
                        break
                
                if not group_label:
                    # Try to derive from name or use name itself
                    group_label = group_name.replace('_', ' ').replace('-', ' ').title()
                
                # Get all option labels
                option_labels = [r.get('label') or r.get('value') or r.get('id', f'Option{i}') 
                                for i, r in enumerate(radios, 1)]
                
                combinable.append({
                    'field': radios[0],  # Representative field
                    'name': group_name,
                    'label': group_label,
                    'values': option_labels,
                    'field_type': 'radio',
                    'radio_group': radios  # Store all radios in group
                })
        
        # Add checkboxes as individual boolean fields
        for checkbox in checkbox_fields:
            combinable.append({
                'field': checkbox,
                'name': checkbox.get('name') or checkbox.get('id', 'unknown'),
                'label': checkbox.get('label') or checkbox.get('placeholder') or checkbox.get('id', 'Checkbox'),
                'values': [True, False],
                'field_type': 'checkbox'
            })
        
        return combinable
    
    def _generate_combinations(self, combinable_fields: List[Dict], form_context: Dict) -> List[Dict]:
        """Generate all combinations of field values"""
        test_cases = []
        
        # Limit to first 3 fields to avoid combinatorial explosion
        fields_to_combine = combinable_fields[:3]
        
        if not fields_to_combine:
            return []
        
        # Get field names, labels, and their possible values
        field_names = [f['field'].get('name') or f['field'].get('id', 'unknown') for f in fields_to_combine]
        field_labels = {(f['field'].get('name') or f['field'].get('id', 'unknown')): f['field'].get('label', f['field'].get('name') or f['field'].get('id', 'Field')) for f in fields_to_combine}
        value_sets = [f['values'] for f in fields_to_combine]
        
        # Generate all combinations
        all_combinations = list(itertools.product(*value_sets))
        
        # Create test case for each combination
        for idx, combination in enumerate(all_combinations):
            test_data = {}
            description_parts = []
            
            for field_idx, (field_name, value) in enumerate(zip(field_names, combination)):
                test_data[field_name] = value
                
                # Build description using field label
                field_label = field_labels.get(field_name, field_name.replace('_', ' ').title())
                if isinstance(value, bool):
                    value_str = 'Yes' if value else 'No'
                else:
                    value_str = str(value)
                
                description_parts.append(f"{field_label}={value_str}")
            
            description = 'Combination {}: {}'.format(idx + 1, ', '.join(description_parts))
            
            test_cases.append({
                'id': f"decision_table_{form_context['id']}_{idx}",
                'type': 'Decision Table',
                'form_url': form_context['url'],
                'form_id': form_context['id'],
                'form_action': form_context['action'],
                'page_title': form_context['title'],
                'combination_index': idx,
                'test_data': test_data,
                'field_labels': field_labels,
                'expected_result': 'success',  # Would need business rules to determine
                'description': description,
                'fields_combined': field_names
            })
        
        return test_cases
