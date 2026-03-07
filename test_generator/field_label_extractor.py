"""
Generic Field Label Extractor

Extracts meaningful field labels from any website structure using:
- Direct attributes (label, placeholder, id, name)
- Contextual clues (parent headings, aria-label, title)
- Semantic analysis (nearby text, form structure)
"""

from typing import Dict, Optional
import re


def extract_field_label(field: Dict, form_context: Dict = None) -> str:
    """
    Extract the most meaningful label for a field using multiple strategies.
    Works generically for any website structure.
    
    Args:
        field: Field dictionary with attributes
        form_context: Optional context about parent form
    
    Returns:
        Best available label for the field
    """
    # Strategy 1: Direct label attribute
    label = field.get('label') or ''
    if isinstance(label, str):
        label = label.strip()
        if label and len(label) > 0:
            return clean_label(label)
    
    # Strategy 2: Placeholder as label
    placeholder = field.get('placeholder') or ''
    if isinstance(placeholder, str):
        placeholder = placeholder.strip()
        if placeholder and len(placeholder) > 0:
            return clean_label(placeholder)
    
    # Strategy 3: ID attribute (convert to readable)
    field_id = field.get('id') or ''
    if isinstance(field_id, str):
        field_id = field_id.strip()
        if field_id and len(field_id) > 0:
            return id_to_label(field_id)
    
    # Strategy 4: Name attribute (convert to readable)
    field_name = field.get('name') or ''
    if isinstance(field_name, str):
        field_name = field_name.strip()
        if field_name and len(field_name) > 0:
            return id_to_label(field_name)
    
    # Strategy 5: Aria-label (accessibility attribute)
    aria_label = field.get('aria-label') or ''
    if isinstance(aria_label, str):
        aria_label = aria_label.strip()
        if aria_label and len(aria_label) > 0:
            return clean_label(aria_label)
    
    # Strategy 6: Title attribute
    title = field.get('title') or ''
    if isinstance(title, str):
        title = title.strip()
        if title and len(title) > 0:
            return clean_label(title)
    
    # Strategy 7: Parent form context
    if form_context:
        page_title = form_context.get('title') or ''
        if isinstance(page_title, str):
            page_title = page_title.strip()
            if page_title and page_title != 'Unknown Page':
                # Use page title + field type as fallback
                field_type = (field.get('type') or 'field')
                if isinstance(field_type, str):
                    field_type = field_type.title()
                    return f"{page_title} {field_type}"
    
    # Strategy 8: Field type with context
    field_type = field.get('type') or 'unknown'
    if isinstance(field_type, str):
        field_type = field_type.title()
    return f"{field_type} Field"


def clean_label(text: str) -> str:
    """Clean and normalize a label text"""
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Remove common suffixes
    text = re.sub(r'\s*[:\-\*]+\s*$', '', text)
    
    # Capitalize first letter if all lowercase
    if text.islower():
        text = text.capitalize()
    
    return text[:100]  # Limit length


def id_to_label(identifier: str) -> str:
    """
    Convert ID/name to readable label.
    Examples:
        firstName -> First Name
        user_email -> User Email
        phone-number -> Phone Number
        txtPassword -> Password
    """
    # Remove common prefixes
    identifier = re.sub(r'^(txt|input|field|select|chk|rad|btn)', '', identifier, flags=re.IGNORECASE)
    
    # Split by camelCase
    identifier = re.sub(r'([a-z])([A-Z])', r'\1 \2', identifier)
    
    # Split by underscores and hyphens
    identifier = identifier.replace('_', ' ').replace('-', ' ')
    
    # Clean up multiple spaces
    identifier = ' '.join(identifier.split())
    
    # Title case
    return identifier.title()


def get_field_context(field: Dict) -> Dict[str, str]:
    """
    Extract all available context for a field.
    Useful for AI refinement.
    """
    return {
        'id': field.get('id', ''),
        'name': field.get('name', ''),
        'type': field.get('type', ''),
        'label': field.get('label', ''),
        'placeholder': field.get('placeholder', ''),
        'aria_label': field.get('aria-label', ''),
        'title': field.get('title', ''),
        'pattern': field.get('pattern', ''),
        'required': field.get('required', False),
        'parent_form': field.get('parent_form', ''),
        'selector': field.get('selector', ''),
    }
