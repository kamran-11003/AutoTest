"""
AI Test Refinement using Gemini with Key Rotation

Enhances test cases by:
- Filling missing field labels
- Improving test descriptions
- Suggesting edge cases
- Adding business logic validation
"""

import os
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiTestRefiner:
    """Refine test cases using Gemini AI with key rotation"""
    
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.model = None
        self._initialize_model()
    
    def _load_api_keys(self) -> List[str]:
        """
        Load Gemini API keys from environment
        Supports:
        - GEMINI_API_KEY (single key)
        - GEMINI_API_KEYS (comma-separated list)
        - GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
        """
        keys = []
        
        # Method 1: Comma-separated list (same as crawler)
        keys_str = os.getenv('GEMINI_API_KEYS', '')
        if keys_str:
            keys.extend([k.strip() for k in keys_str.split(',') if k.strip()])
        
        # Method 2: Single key
        single_key = os.getenv('GEMINI_API_KEY')
        if single_key and single_key not in keys:
            keys.append(single_key)
        
        # Method 3: Individual keys (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.)
        for i in range(1, 11):  # Support up to 10 keys
            key = os.getenv(f'GEMINI_API_KEY_{i}')
            if key and key not in keys:
                keys.append(key)
        
        if not keys:
            logger.warning("No Gemini API keys found in environment variables")
            logger.warning("Set GEMINI_API_KEY, GEMINI_API_KEYS, or GEMINI_API_KEY_1, etc.")
        else:
            logger.info(f"Loaded {len(keys)} Gemini API key(s)")
        
        return keys
    
    def _initialize_model(self):
        """Initialize Gemini model with current API key"""
        if not self.api_keys:
            return
        
        try:
            key = self.api_keys[self.current_key_index]
            genai.configure(api_key=key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info(f"Initialized Gemini model with key #{self.current_key_index + 1}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            self.model = None
    
    def _rotate_key(self):
        """Rotate to next API key"""
        if len(self.api_keys) <= 1:
            return False
        
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        logger.info(f"Rotating to API key #{self.current_key_index + 1}")
        self._initialize_model()
        return True
    
    def refine_tests(self, test_cases: Dict[str, List[Dict]], crawl_data: Dict = None) -> Dict[str, List[Dict]]:
        """
        Refine all test cases using AI
        
        Args:
            test_cases: Dictionary of test cases by type
            crawl_data: Optional crawl data for context
        
        Returns:
            Enhanced test cases
        """
        if not self.model:
            print("⚠️  Gemini model not initialized - skipping refinement")
            logger.warning("Gemini model not initialized - skipping refinement")
            return test_cases
        
        print("\n" + "="*60)
        print("AI STARTING AI TEST REFINEMENT WITH GEMINI")
        print("="*60)
        logger.info("Starting AI test refinement...")
        
        if crawl_data:
            print(f">> Crawl Context: {len(crawl_data.get('nodes', []))} pages, {len(crawl_data.get('edges', []))} transitions")
        
        refined_tests = {}
        
        for test_type, tests in test_cases.items():
            if isinstance(tests, list):
                print(f"\n-> Refining {len(tests)} {test_type} tests...")
                logger.info(f"Refining {len(tests)} {test_type} tests...")
                refined_tests[test_type] = self._refine_test_batch(tests, test_type, crawl_data)
                print(f"OK Completed {test_type} refinement")
            else:
                # Handle non-list formats (e.g., use cases might be dict)
                print(f"\n⚠️  Skipping {test_type} - not in list format")
                refined_tests[test_type] = tests
        
        print("\n" + "="*60)
        print("✨ AI REFINEMENT COMPLETE!")
        print("="*60 + "\n")
        logger.info("AI refinement complete!")
        return refined_tests
    
    def _refine_test_batch(self, tests: List[Dict], test_type: str, crawl_data: Dict = None) -> List[Dict]:
        """Refine a batch of tests"""
        refined = []
        batch_size = 10  # Process in smaller batches
        total_batches = (len(tests) + batch_size - 1) // batch_size
        
        for batch_num, i in enumerate(range(0, len(tests), batch_size), 1):
            batch = tests[i:i+batch_size]
            print(f"  BATCH Processing batch {batch_num}/{total_batches} ({len(batch)} tests)...", end=" ")
            
            try:
                refined_batch = self._refine_batch_with_ai(batch, test_type, crawl_data)
                refined.extend(refined_batch)
                print("OK")
            except Exception as e:
                print(f"FAIL Error: {str(e)[:50]}...")
                logger.error(f"Error refining batch: {e}")
                # Try rotating key
                print(f"  -> Rotating to next API key...", end=" ")
                if self._rotate_key():
                    try:
                        refined_batch = self._refine_batch_with_ai(batch, test_type, crawl_data)
                        refined.extend(refined_batch)
                        print("OK Retry successful")
                    except Exception as e2:
                        print(f"FAIL Retry failed: {str(e2)[:30]}...")
                        logger.error(f"Error after key rotation: {e2}")
                        # Keep original tests
                        refined.extend(batch)
                else:
                    print("FAIL No more keys available")
                    # Keep original tests
                    refined.extend(batch)
        
        return refined
    
    def _refine_batch_with_ai(self, batch: List[Dict], test_type: str, crawl_data: Dict = None) -> List[Dict]:
        """Use AI to refine a batch of tests"""
        prompt = self._build_refinement_prompt(batch, test_type, crawl_data)
        
        # Configure generation for JSON output
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "max_output_tokens": 8192,
        }
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        refined_batch = self._parse_ai_response(response.text, batch)
        
        return refined_batch
    
    def _build_refinement_prompt(self, batch: List[Dict], test_type: str, crawl_data: Dict = None) -> str:
        """Build comprehensive prompt with full crawl context for intelligent test refinement"""
        
        # Extract DETAILED website context from crawl data
        website_context = ""
        forms_detail = ""
        fields_detail = ""
        
        if crawl_data:
            nodes = crawl_data.get('nodes', [])
            edges = crawl_data.get('edges', [])
            
            # Get ALL forms with their fields
            all_forms = []
            for node in nodes:
                page_url = node.get('url', '')
                page_title = node.get('title', 'Untitled')
                for form in node.get('forms', []):
                    form_info = {
                        'page': page_title,
                        'url': page_url,
                        'action': form.get('action', ''),
                        'method': form.get('method', 'GET'),
                        'inputs': []
                    }
                    for inp in form.get('inputs', []):
                        form_info['inputs'].append({
                            'type': inp.get('type', ''),
                            'name': inp.get('name', ''),
                            'id': inp.get('id', ''),
                            'label': inp.get('label', ''),
                            'placeholder': inp.get('placeholder', ''),
                            'required': inp.get('required', False)
                        })
                    all_forms.append(form_info)
            
            # Build detailed forms context
            if all_forms:
                forms_detail = "\nFORMS DISCOVERED:\n"
                for i, form in enumerate(all_forms[:10], 1):  # First 10 forms
                    forms_detail += f"\nForm {i} on '{form['page']}':\n"
                    forms_detail += f"  Action: {form['action']}\n"
                    forms_detail += f"  Fields: {len(form['inputs'])}\n"
                    for inp in form['inputs'][:5]:  # First 5 fields per form
                        field_desc = f"    - {inp['type']}"
                        if inp['label']:
                            field_desc += f" | Label: {inp['label']}"
                        if inp['name']:
                            field_desc += f" | Name: {inp['name']}"
                        if inp['placeholder']:
                            field_desc += f" | Placeholder: {inp['placeholder']}"
                        if inp['required']:
                            field_desc += " | REQUIRED"
                        forms_detail += field_desc + "\n"
            
            # Get page navigation structure
            pages_detail = "\nPAGE STRUCTURE:\n"
            for node in nodes[:10]:  # First 10 pages
                pages_detail += f"- {node.get('title', 'Untitled')} @ {node.get('url', '')}\n"
                pages_detail += f"  Forms: {len(node.get('forms', []))}, Inputs: {len(node.get('inputs', []))}, Links: {len(node.get('links', []))}\n"
            
            website_context = f"""
CRAWLED WEBSITE DATA (Use this to understand ACTUAL fields and context):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Total Pages: {len(nodes)}
• Total Transitions: {len(edges)}
• Total Forms: {len(all_forms)}
• Total Input Fields: {sum(len(f['inputs']) for f in all_forms)}
{pages_detail}
{forms_detail}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        prompt = f"""You are an expert QA engineer performing COMPREHENSIVE test case refinement.

{website_context}

CURRENT TEST CASES ({test_type}):
{json.dumps(batch, indent=2)}

YOUR MISSION - PERFORM ALL 4 ACTIONS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 🔍 ANALYZE EXISTING TESTS:
   - Review each test for completeness and accuracy
   - Check if field_label matches actual fields from crawl data
   - Verify test values are appropriate for field types
   - Check if descriptions are clear and specific

2. UPD️ UPDATE/FIX EXISTING TESTS:
   - Replace "Unknown Field", generic labels with ACTUAL field names from crawl data
   - Update test_value if it doesn't match field type (e.g., number for text field)
   - Improve descriptions to be specific: "Verify [FieldName] accepts [value] and [expected behavior]"
   - Fix expected_result if incorrect
   - Mark updated tests with "action": "updated"

3. ➕ ADD NEW MISSING TEST CASES:
   - Identify fields from crawl data that aren't being tested
   - Generate NEW test cases for untested scenarios:
     * Missing boundary values
     * Missing equivalence partitions
     * Untested form fields
     * Missing negative tests
     * Security tests (SQL injection, XSS for text fields)
   - Mark new tests with "action": "added"

4. DEL️ MARK REDUNDANT/INVALID TESTS FOR DELETION:
   - Duplicate tests (same field, same test type, same values)
   - Tests for non-existent fields
   - Invalid test configurations
   - Mark with "action": "delete", "delete_reason": "explanation"

RESPONSE FORMAT (JSON array with ALL tests):
[
  {{
    "action": "kept|updated|added|delete",
    "delete_reason": "reason if action=delete",
    ...all_original_test_fields...,
    "description": "Enhanced specific description",
    "field_label": "Actual field name from crawl data",
    "test_value": "Updated if needed",
    "expected_result": "Updated if needed",
    "ai_notes": "What was changed and why",
    "validation_rules": ["Rule 1", "Rule 2"],
    "edge_cases_covered": ["Scenario 1", "Scenario 2"]
  }}
]

CRITICAL RULES:
✓ Return COMPLETE test objects (all original fields + enhancements)
✓ Use ACTUAL field names/labels from the crawl data above
✓ Generate 20-30% MORE tests than provided (add missing scenarios)
✓ Mark action as "updated", "added", "delete", or "kept"
✓ Return ONLY valid JSON array, no markdown, no code blocks, no explanation
✓ Be aggressive about adding missing test coverage
✓ Start response with [ and end with ] - PURE JSON ONLY

EXAMPLE OUTPUT (DO NOT INCLUDE THIS TEXT, ONLY JSON):
[{{"action":"updated","id":"BVA_001",...}},{{"action":"added","id":"BVA_003",...}}]

Now return the refined test cases as a pure JSON array:"""
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, original_batch: List[Dict]) -> List[Dict]:
        """Parse AI response - handle updated, new, and deleted tests"""
        try:
            # Remove markdown code blocks if present
            response_text = response_text.replace('```json', '').replace('```', '')
            
            # Try to extract JSON from response
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_text = response_text[json_start:json_end]
                
                # Clean up common JSON issues
                json_text = json_text.strip()
                
                ai_tests = json.loads(json_text)
                
                # Track statistics
                stats = {'kept': 0, 'updated': 0, 'added': 0, 'deleted': 0}
                
                # Filter out deleted tests and count actions
                refined_tests = []
                for test in ai_tests:
                    action = test.get('action', 'kept')
                    stats[action] = stats.get(action, 0) + 1
                    
                    # Add metadata
                    test['ai_enhanced'] = True
                    test['enhanced_at'] = datetime.now().isoformat()
                    
                    # Skip deleted tests
                    if action == 'delete':
                        print(f"    DEL️  Deleted: {test.get('id', 'unknown')} - {test.get('delete_reason', 'no reason')}")
                        continue
                    
                    # Log updates and additions
                    if action == 'updated':
                        print(f"    UPD️  Updated: {test.get('id', 'unknown')} - {test.get('field_label', '')}")
                    elif action == 'added':
                        print(f"    ➕ Added: {test.get('id', 'NEW')} - {test.get('description', '')[:60]}")
                    
                    refined_tests.append(test)
                
                # Print summary
                print(f"\n    >> Refinement Stats: {stats['kept']} kept, {stats['updated']} updated, {stats['added']} added, {stats['deleted']} deleted")
                print(f"    >> Total: {len(original_batch)} → {len(refined_tests)} ({len(refined_tests) - len(original_batch):+d})")
                
                return refined_tests
            else:
                print("    ⚠️  Could not parse JSON from AI response - keeping originals")
                logger.warning("Could not parse JSON from AI response")
                return original_batch
        
        except Exception as e:
            print(f"    FAIL Parse error: {str(e)[:50]} - keeping originals")
            logger.error(f"Error parsing AI response: {e}")
            return original_batch
