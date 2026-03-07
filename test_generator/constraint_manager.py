"""
Constraint Manager - Handle missing constraints with smart defaults

Addresses real-world scenario where crawled forms lack explicit constraints:
- Auto-applies sensible defaults based on field type and context
- Allows manual constraint editing
- Supports constraint-based test regeneration
"""

from typing import Dict, List, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ConstraintManager:
    """Manage field constraints with smart defaults"""
    
    # Default constraints based on common patterns
    DEFAULT_CONSTRAINTS = {
        # Text fields
        'text': {'minlength': 1, 'maxlength': 255},
        'textarea': {'minlength': 1, 'maxlength': 5000},
        
        # Name fields
        'firstname': {'minlength': 2, 'maxlength': 50},
        'lastname': {'minlength': 2, 'maxlength': 50},
        'name': {'minlength': 2, 'maxlength': 100},
        'username': {'minlength': 3, 'maxlength': 30},
        
        # Contact fields
        'email': {'minlength': 5, 'maxlength': 254},
        'phone': {'minlength': 10, 'maxlength': 15},
        'tel': {'minlength': 10, 'maxlength': 15},
        
        # Password fields
        'password': {'minlength': 8, 'maxlength': 128},
        
        # Numeric fields
        'number': {'min': 0, 'max': 999999, 'step': 1},
        'range': {'min': 0, 'max': 100, 'step': 1},
        'age': {'min': 1, 'max': 120, 'step': 1},
        'quantity': {'min': 1, 'max': 999, 'step': 1},
        'price': {'min': 0.01, 'max': 999999.99, 'step': 0.01},
        'amount': {'min': 0, 'max': 999999.99, 'step': 0.01},
        
        # Date fields
        'date': {'min': '1900-01-01', 'max': '2099-12-31'},
        'datetime-local': {'min': '1900-01-01T00:00', 'max': '2099-12-31T23:59'},
        
        # Postal/Zip
        'zip': {'minlength': 5, 'maxlength': 10},
        'zipcode': {'minlength': 5, 'maxlength': 10},
        'postal': {'minlength': 5, 'maxlength': 10},
        'postalcode': {'minlength': 5, 'maxlength': 10},
        
        # Address
        'address': {'minlength': 5, 'maxlength': 200},
        'street': {'minlength': 3, 'maxlength': 100},
        'city': {'minlength': 2, 'maxlength': 100},
        'state': {'minlength': 2, 'maxlength': 50},
        'country': {'minlength': 2, 'maxlength': 100},
        
        # Other
        'url': {'minlength': 10, 'maxlength': 2048},
        'search': {'minlength': 1, 'maxlength': 200},
        'comment': {'minlength': 1, 'maxlength': 1000},
        'message': {'minlength': 1, 'maxlength': 5000},
        'description': {'minlength': 10, 'maxlength': 2000},
    }
    
    def __init__(self):
        self.custom_constraints = {}  # User-defined constraints
    
    def apply_smart_defaults(self, field: Dict) -> Dict:
        """
        Apply smart default constraints if field lacks them
        
        Args:
            field: Input field dictionary
            
        Returns:
            Field with constraints applied
        """
        field = field.copy()  # Don't modify original

        # Normalise camelCase keys written by the crawler to lowercase so
        # the rest of the generator code (which uses lowercase lookups) can
        # find them.  Prefer the camelCase value over a pre-existing lowercase
        # value because the camelCase one came directly from the HTML attribute.
        for camel, lower in [('minLength', 'minlength'), ('maxLength', 'maxlength')]:
            if field.get(camel) is not None:
                field[lower] = field[camel]

        # Check if field already has constraints
        has_constraints = self._has_constraints(field)
        if has_constraints:
            return field  # Use existing constraints
        
        # Get field identifiers for matching
        field_type = (field.get('type') or 'text').lower()
        field_name = (field.get('name') or '').lower()
        field_id = (field.get('id') or '').lower()
        field_label = (field.get('label') or '').lower()
        field_placeholder = (field.get('placeholder') or '').lower()
        
        # Strategy 1: Match by field type
        if field_type in self.DEFAULT_CONSTRAINTS:
            constraints = self.DEFAULT_CONSTRAINTS[field_type]
            field.update(constraints)
            logger.info(f"Applied default constraints for type '{field_type}': {constraints}")
            return field
        
        # Strategy 2: Match by field name/id/label keywords
        search_text = f"{field_name} {field_id} {field_label} {field_placeholder}"
        
        for keyword, constraints in self.DEFAULT_CONSTRAINTS.items():
            if keyword in search_text:
                field.update(constraints)
                logger.info(f"Applied default constraints for keyword '{keyword}': {constraints}")
                return field
        
        # Strategy 3: Check for semantic patterns
        # Names (firstName, lastName, fullName, etc.)
        if re.search(r'(first|last|full|middle|sur)?name', search_text, re.IGNORECASE):
            field.update(self.DEFAULT_CONSTRAINTS['name'])
            logger.info(f"Applied name field constraints")
            return field
        
        # Phone numbers
        if re.search(r'phone|mobile|cell|contact', search_text, re.IGNORECASE):
            field.update(self.DEFAULT_CONSTRAINTS['phone'])
            logger.info(f"Applied phone field constraints")
            return field
        
        # Addresses
        if re.search(r'address|street|location', search_text, re.IGNORECASE):
            field.update(self.DEFAULT_CONSTRAINTS['address'])
            logger.info(f"Applied address field constraints")
            return field
        
        # Strategy 4: Generic fallback based on field type category
        if field_type in ['text', 'search', 'url', 'tel', 'email']:
            # Text-like field
            field.update({'minlength': 1, 'maxlength': 255})
            logger.info(f"Applied generic text constraints")
        elif field_type in ['number', 'range']:
            # Numeric field
            field.update({'min': 0, 'max': 999999, 'step': 1})
            logger.info(f"Applied generic numeric constraints")
        elif field_type == 'textarea':
            field.update({'minlength': 1, 'maxlength': 5000})
            logger.info(f"Applied generic textarea constraints")
        else:
            logger.warning(f"No default constraints found for field: {field_name or field_id or 'unknown'}")
        
        return field
    
    def _has_constraints(self, field: Dict) -> bool:
        """Check if field already has constraints.

        The crawler serialises HTML attributes in camelCase (``minLength``,
        ``maxLength``) while the rest of the generator code uses lowercase
        keys (``minlength``, ``maxlength``).  Check both variants so that
        real crawled constraints are not silently discarded.
        """
        # Numeric constraints
        if any(k in field for k in ['min', 'max', 'step']):
            # Make sure the value is actually set (not None)
            if any(field.get(k) is not None for k in ['min', 'max', 'step']):
                return True

        # Length constraints – lowercase (generator-internal) and camelCase (crawler)
        length_keys = ['minlength', 'maxlength', 'minLength', 'maxLength']
        if any(field.get(k) is not None for k in length_keys):
            return True
        
        # Pattern constraint
        if field.get('pattern'):
            return True
        
        return False
    
    def update_constraint(self, field: Dict, constraint_type: str, value: Any) -> Dict:
        """
        Manually update a constraint value
        
        Args:
            field: Input field dictionary
            constraint_type: Type of constraint (min, max, minlength, maxlength, step, pattern)
            value: New constraint value
            
        Returns:
            Updated field
        """
        field = field.copy()
        field[constraint_type] = value
        
        # Store in custom constraints
        field_key = field.get('name') or field.get('id') or 'unknown'
        if field_key not in self.custom_constraints:
            self.custom_constraints[field_key] = {}
        self.custom_constraints[field_key][constraint_type] = value
        
        logger.info(f"Updated constraint for {field_key}: {constraint_type}={value}")
        return field
    
    def get_constraints_for_field(self, field: Dict) -> Dict[str, Any]:
        """Extract all constraints from a field"""
        constraints = {}
        
        # Numeric constraints
        if 'min' in field:
            constraints['min'] = field['min']
        if 'max' in field:
            constraints['max'] = field['max']
        if 'step' in field:
            constraints['step'] = field['step']
        
        # Length constraints
        if 'minlength' in field:
            constraints['minlength'] = field['minlength']
        if 'maxlength' in field:
            constraints['maxlength'] = field['maxlength']
        
        # Pattern constraint
        if 'pattern' in field:
            constraints['pattern'] = field['pattern']
        
        # Required
        if 'required' in field:
            constraints['required'] = field['required']
        
        return constraints
    
    def analyze_form_constraints(self, form_data: Dict) -> Dict[str, Any]:
        """
        Analyze a form and report constraint coverage
        
        Args:
            form_data: Form data dictionary with forms and inputs
            
        Returns:
            Analysis report
        """
        report = {
            'total_fields': 0,
            'fields_with_constraints': 0,
            'fields_without_constraints': 0,
            'missing_constraint_fields': [],
            'constraint_coverage_percent': 0
        }
        
        for form in form_data.get('forms', []):
            for field in form.get('inputs', []):
                field_type = (field.get('type') or '').lower()
                
                # Skip non-input types
                if field_type in ['submit', 'button', 'hidden', 'reset', 'image']:
                    continue
                
                report['total_fields'] += 1
                
                if self._has_constraints(field):
                    report['fields_with_constraints'] += 1
                else:
                    report['fields_without_constraints'] += 1
                    report['missing_constraint_fields'].append({
                        'form_url': form.get('url', 'unknown'),
                        'field_name': field.get('name') or field.get('id', 'unknown'),
                        'field_type': field_type,
                        'field_label': field.get('label', ''),
                        'suggested_defaults': self._suggest_defaults(field)
                    })
        
        if report['total_fields'] > 0:
            report['constraint_coverage_percent'] = round(
                (report['fields_with_constraints'] / report['total_fields']) * 100, 2
            )
        
        return report
    
    def _suggest_defaults(self, field: Dict) -> Dict[str, Any]:
        """Suggest default constraints for a field"""
        temp_field = self.apply_smart_defaults(field)
        return self.get_constraints_for_field(temp_field)
    
    def apply_constraints_to_form_data(self, form_data: Dict, auto_apply: bool = True) -> Dict:
        """
        Apply smart defaults to all fields in form data
        
        Args:
            form_data: Form data dictionary
            auto_apply: If True, automatically apply defaults; if False, just analyze
            
        Returns:
            Updated form data (if auto_apply=True) or analysis report
        """
        if not auto_apply:
            return self.analyze_form_constraints(form_data)
        
        updated_data = form_data.copy()
        applied_count = 0
        
        for form in updated_data.get('forms', []):
            for i, field in enumerate(form.get('inputs', [])):
                field_type = (field.get('type') or '').lower()
                
                # Skip non-input types
                if field_type in ['submit', 'button', 'hidden', 'reset', 'image']:
                    continue
                
                if not self._has_constraints(field):
                    form['inputs'][i] = self.apply_smart_defaults(field)
                    applied_count += 1
        
        logger.info(f"Applied smart defaults to {applied_count} fields")
        return updated_data


# Global instance
constraint_manager = ConstraintManager()
