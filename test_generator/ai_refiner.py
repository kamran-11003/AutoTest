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
import re
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
            self.model = genai.GenerativeModel('gemini-3.1-flash-lite-preview')
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
        
        # Configure generation for reliable JSON output
        # Very low temperature for consistent, deterministic JSON
        generation_config = {
            "temperature": 0.1,  # Very low for consistent JSON
            "top_p": 0.8,
            "max_output_tokens": 8192,
        }
        
        response = self.model.generate_content(
            prompt,
            generation_config=generation_config
        )
        refined_batch = self._parse_ai_response(response.text, batch)
        
        return refined_batch
    
    def _build_refinement_prompt(self, batch: List[Dict], test_type: str, crawl_data: Dict = None) -> str:
        """Build simple, direct prompt for test refinement"""
        
        # Extract field names from crawl data
        fields_list = []
        if crawl_data:
            nodes = crawl_data.get('nodes', [])
            for node in nodes:
                for form in node.get('forms', []):
                    for inp in form.get('inputs', []):
                        label = inp.get('label') or inp.get('name') or inp.get('id')
                        if label:
                            fields_list.append(label)
            fields_list = list(set(fields_list))[:20]  # Unique, max 20
        
        fields_str = ", ".join(fields_list) if fields_list else "See test cases for field names"
        
        # Create example showing ALL fields must be preserved
        example_in = batch[0] if batch else {"id": "example", "type": "text", "test_value": "value"}
        example_out = dict(example_in)
        example_out["action"] = "kept"
        example_out["description"] = "Updated description if needed"
        
        prompt = f"""Refine these test cases. CRITICAL: Preserve ALL original fields!

ORIGINAL TEST STRUCTURE (preserve all these fields):
{json.dumps(example_in, indent=2)}

FIELDS IN SYSTEM: {fields_str}

TEST CASES TO REFINE:
{json.dumps(batch, indent=2)}

INSTRUCTIONS:
1. For each test, return ALL original fields UNCHANGED (id, type, test_value, expected_result, etc.)
2. Only update: field_label (use actual field names), description (make more specific)
3. Add action field: kept, updated, or added
4. Add new tests only if you identify missing scenarios
5. Never remove or change original fields like test_value, type, expected_result

EXAMPLE OUTPUT (shows ALL fields preserved from input):
{json.dumps(example_out, indent=2)}

CRITICAL REQUIREMENTS:
- Every returned test must have ALL its original fields
- If action=updated, only field_label and description should change
- If action=added, generate complete new test with all required fields
- Return ONLY a JSON array
- Start with [ and end with ]"""
        
        return prompt
    
    def _repair_json(self, json_text: str) -> str:
        """Aggressively repair common JSON issues"""
        
        # Remove control characters
        json_text = re.sub(r'[\x00-\x1f\x7f]', ' ', json_text)
        
        # Fix missing commas between objects in array
        json_text = re.sub(r'}\s*{', '}, {', json_text)
        json_text = re.sub(r']\s*{', '], {', json_text)
        json_text = re.sub(r'}\s*\[', '}, [', json_text)
        
        # Remove trailing commas before ] or }
        json_text = re.sub(r',(\s*[}\]])', r'\1', json_text)
        
        # Fix common quote issues
        # Don't try to fix internal quotes - too risky
        # Just ensure outer structure is valid
        
        # Ensure arrays start and end properly
        json_text = json_text.strip()
        if not json_text.startswith('['):
            # Find first [
            first_bracket = json_text.find('[')
            if first_bracket >= 0:
                json_text = json_text[first_bracket:]
        
        if not json_text.endswith(']'):
            # Find last ]
            last_bracket = json_text.rfind(']')
            if last_bracket >= 0:
                json_text = json_text[:last_bracket + 1]
        
        return json_text
    
    def _parse_ai_response(self, response_text: str, original_batch: List[Dict]) -> List[Dict]:
        """Parse AI response with robust error handling"""
        try:
            # Remove markdown code blocks
            response_text = response_text.replace('```json', '').replace('```', '').strip()
            
            # Try to extract JSON array
            json_start = response_text.find('[')
            json_end = response_text.rfind(']') + 1
            
            if json_start < 0 or json_end <= json_start:
                print(f"    ⚠️  No JSON array found - keeping originals")
                return original_batch
            
            json_text = response_text[json_start:json_end].strip()
            
            # Attempt to repair JSON
            json_text = self._repair_json(json_text)
            
            # Try to parse repaired JSON
            try:
                ai_tests = json.loads(json_text)
            except json.JSONDecodeError as e:
                # If repair didn't help, try to extract individual objects
                print(f"    ⚠️  JSON parse failed ({str(e)[:30]}), extracting individual tests...")
                
                # Find all { } pairs that might be test objects
                ai_tests = []
                depth = 0
                current_obj = []
                in_string = False
                escape_next = False
                
                for i, char in enumerate(json_text):
                    if escape_next:
                        escape_next = False
                        current_obj.append(char)
                        continue
                    
                    if char == '\\\\':
                        escape_next = True
                        current_obj.append(char)
                        continue
                    
                    if char == '"' and depth > 0:
                        in_string = not in_string
                    
                    if char == '{' and not in_string:
                        depth += 1
                        current_obj = [char]
                    elif char == '}' and not in_string:
                        current_obj.append(char)
                        depth -= 1
                        if depth == 0 and current_obj:
                            try:
                                obj_str = ''.join(current_obj)
                                test_obj = json.loads(obj_str)
                                ai_tests.append(test_obj)
                            except:
                                pass
                            current_obj = []
                    elif depth > 0:
                        current_obj.append(char)
                
                if not ai_tests:
                    print(f"    ❌ Could not extract any tests - keeping originals")
                    return original_batch
            
            # Process extracted tests
            stats = {'kept': 0, 'updated': 0, 'added': 0, 'deleted': 0}
            refined_tests = []
            
            # Create a map of original tests by ID for field restoration
            original_map = {test.get('id'): test for test in original_batch}
            
            for test in ai_tests:
                if not isinstance(test, dict):
                    continue
                
                test_id = test.get('id')
                action = test.get('action', 'kept')
                stats[action] = stats.get(action, 0) + 1
                
                # If this test was in the original batch, restore any missing critical fields
                if test_id in original_map and action in ['kept', 'updated']:
                    original = original_map[test_id]
                    # Restore critical fields that should never be lost
                    for critical_field in ['type', 'test_value', 'expected_result', 'page', 'form_name']:
                        if critical_field not in test and critical_field in original:
                            test[critical_field] = original[critical_field]
                
                # Add metadata
                test['ai_enhanced'] = True
                test['enhanced_at'] = datetime.now().isoformat()
                
                # Skip deleted tests
                if action == 'delete':
                    print(f"    ❌ Deleted: {test_id}")
                    continue
                
                # Log updates and additions
                if action == 'updated':
                    print(f"    ✏️ Updated: {test_id}")
                elif action == 'added':
                    print(f"    ➕ Added: {test_id}")
                
                # Validate test has critical fields before adding
                # Must have: id, test_value (or we use original)
                if test_id in original_map and action in ['kept', 'updated']:
                    # If AI didn't get critical fields, use the original instead
                    if not test.get('test_value'):
                        test = dict(original_map[test_id])
                        test['action'] = action
                        test['ai_enhanced'] = True
                        test['enhanced_at'] = datetime.now().isoformat()
                        test['ai_notes'] = 'Kept original due to incomplete refinement'
                
                # Only add if test has test_value and id
                if test.get('id') and test.get('test_value') is not None:
                    refined_tests.append(test)
                elif test.get('id'):
                    # Has ID but missing test_value - use original
                    if test_id in original_map:
                        orig = dict(original_map[test_id])
                        orig['action'] = action
                        orig['ai_enhanced'] = True
                        refined_tests.append(orig)
            
            # Print summary
            print(f"\n    >> Refinement Stats: {stats['kept']} kept, {stats['updated']} updated, {stats['added']} added, {stats['deleted']} deleted")
            print(f"    >> Total: {len(original_batch)} → {len(refined_tests)} ({len(refined_tests) - len(original_batch):+d})")
            
            return refined_tests if refined_tests else original_batch
        
        except Exception as e:
            print(f"    ❌ Error: {str(e)[:40]} - keeping originals")
            logger.error(f"Error parsing AI response: {e}")
            return original_batch
