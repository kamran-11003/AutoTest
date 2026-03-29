"""
Test Orchestrator - Coordinates all test generators

Manages the generation of all test case types and provides
unified interface for test case generation.
"""

from typing import Dict, List, Any
import json
import re
import logging
from pathlib import Path

from .generators.bva_generator import BVAGenerator
from .generators.ecp_generator import ECPGenerator
from .generators.decision_table_generator import DecisionTableGenerator
from .generators.state_transition_generator import StateTransitionGenerator
from .generators.use_case_generator import UseCaseGenerator

logger = logging.getLogger(__name__)


class TestOrchestrator:
    """Orchestrates test case generation from crawled data"""
    
    def __init__(self):
        self.bva_generator = BVAGenerator()
        self.ecp_generator = ECPGenerator()
        self.decision_table_generator = DecisionTableGenerator()
        self.state_transition_generator = StateTransitionGenerator()
        self.use_case_generator = UseCaseGenerator()
        
        self.all_test_cases = []
    
    def _deduplicate_tests(self, tests: List[Dict], test_type: str) -> List[Dict]:
        """Remove duplicate tests based on test ID"""
        seen_ids = set()
        unique_tests = []
        duplicates = 0
        
        for test in tests:
            test_id = test.get('id')
            if test_id not in seen_ids:
                seen_ids.add(test_id)
                unique_tests.append(test)
            else:
                duplicates += 1
        
        if duplicates > 0:
            logger.info(f"  Removed {duplicates} duplicate {test_type} tests")
        
        return unique_tests
    
    def generate_all_tests(self, crawl_data_path: str) -> Dict[str, Any]:
        """
        Generate all types of test cases from crawl data
        
        Args:
            crawl_data_path: Path to crawl data JSON file
            
        Returns:
            Dictionary containing all generated test cases organized by type
        """
        logger.info(f"Loading crawl data from: {crawl_data_path}")
        
        # Load crawl data
        try:
            with open(crawl_data_path, 'r', encoding='utf-8') as f:
                crawl_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load crawl data: {e}")
            return self._empty_result()
        
        # Create node ID to metadata mapping for readable test cases
        node_map = {}
        for node in crawl_data.get('nodes', []):
            node_id = node.get('id', node.get('hash', ''))
            if node_id:
                node_map[node_id.lower()] = {
                    'url': node.get('url', 'unknown'),
                    'title': node.get('title', 'Unknown Page'),
                    'normalized_url': node.get('normalized_url', '')
                }
        
        # Extract graph and form data
        graph_data = {
            'nodes': crawl_data.get('nodes', []),
            'edges': crawl_data.get('edges', []),
            'node_map': node_map  # Add mapping for readable names
        }
        
        # Extract all forms from all nodes
        all_forms = []
        skipped_no_submit = 0
        for node in crawl_data.get('nodes', []):
            node_forms = node.get('forms', [])
            for form in node_forms:
                # Skip decorative forms with no submit button
                if not self._form_has_submit(form):
                    skipped_no_submit += 1
                    continue
                # Add URL context to form
                form['url'] = node.get('url', 'unknown')
                form['page_title'] = node.get('title', 'unknown')
                form['form_action'] = form.get('action', 'unknown')
                all_forms.append(form)

        if skipped_no_submit:
            logger.info(f"Skipped {skipped_no_submit} form(s) with no submit button (decorative)")
        
        form_data = {
            'forms': all_forms,
            'node_map': node_map  # Add mapping for readable names
        }
        
        logger.info(f"Found {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges, {len(form_data['forms'])} forms")
        
        # Generate all test types
        results = {
            'metadata': {
                'source_file': crawl_data_path,
                'total_nodes': len(graph_data['nodes']),
                'total_edges': len(graph_data['edges']),
                'total_forms': len(form_data['forms'])
            },
            'test_cases': {}
        }
        
        # 1. Boundary Value Analysis
        logger.info("Generating BVA test cases...")
        bva_tests = self.bva_generator.generate(form_data)
        # Deduplicate by test ID
        bva_tests = self._deduplicate_tests(bva_tests, "BVA")
        results['test_cases']['bva'] = bva_tests
        logger.info(f"✅ Generated {len(bva_tests)} BVA test cases")
        
        # 2. Equivalence Class Partitioning
        logger.info("Generating ECP test cases...")
        ecp_tests = self.ecp_generator.generate(form_data)
        # Deduplicate by test ID
        ecp_tests = self._deduplicate_tests(ecp_tests, "ECP")
        results['test_cases']['ecp'] = ecp_tests
        logger.info(f"✅ Generated {len(ecp_tests)} ECP test cases")
        
        # 3. Decision Table
        logger.info("Generating Decision Table test cases...")
        decision_tests = self.decision_table_generator.generate(form_data)
        results['test_cases']['decision_table'] = decision_tests
        logger.info(f"✅ Generated {len(decision_tests)} Decision Table test cases")
        
        # 4. State Transition
        logger.info("Generating State Transition test cases...")
        state_tests = self.state_transition_generator.generate(graph_data)
        results['test_cases']['state_transition'] = state_tests
        logger.info(f"✅ Generated {len(state_tests)} State Transition test cases")
        
        # 5. Use Case
        logger.info("Generating Use Case test cases...")
        usecase_tests = self.use_case_generator.generate(graph_data, form_data)
        results['test_cases']['use_case'] = usecase_tests
        logger.info(f"✅ Generated {len(usecase_tests)} Use Case test cases")

        # Enrich BVA/ECP/DecisionTable test_data with companion field values
        # so the whole form can be submitted, not just the field under test.
        logger.info("Enriching test cases with companion field data...")
        self._enrich_companion_data(results, all_forms)

        # Calculate totals
        total_tests = (
            len(bva_tests) + len(ecp_tests) + len(decision_tests) +
            len(state_tests) + len(usecase_tests)
        )

        results['summary'] = {
            'total_test_cases': total_tests,
            'bva_count': len(bva_tests),
            'ecp_count': len(ecp_tests),
            'decision_table_count': len(decision_tests),
            'state_transition_count': len(state_tests),
            'use_case_count': len(usecase_tests)
        }

        logger.info(f"🎉 Total test cases generated: {total_tests}")

        self.all_test_cases = results
        return results

    def generate_all_tests_from_dict(self, crawl_data: Dict) -> Dict[str, Any]:
        """
        Generate all types of test cases from crawl data dictionary
        
        Args:
            crawl_data: Crawl data as dictionary
            
        Returns:
            Dictionary containing all generated test cases organized by type
        """
        logger.info("Generating tests from crawl data dictionary")
        
        # Create node ID to metadata mapping for readable test cases
        node_map = {}
        for node in crawl_data.get('nodes', []):
            node_id = node.get('id', node.get('hash', ''))
            if node_id:
                node_map[node_id.lower()] = {
                    'url': node.get('url', 'unknown'),
                    'title': node.get('title', 'Unknown Page'),
                    'normalized_url': node.get('normalized_url', '')
                }
        
        # Extract graph and form data
        graph_data = {
            'nodes': crawl_data.get('nodes', []),
            'edges': crawl_data.get('edges', []),
            'node_map': node_map
        }
        
        # Extract all forms from all nodes
        all_forms = []
        skipped_no_submit = 0
        for node in crawl_data.get('nodes', []):
            node_forms = node.get('forms', [])
            for form in node_forms:
                if not self._form_has_submit(form):
                    skipped_no_submit += 1
                    continue
                form['url'] = node.get('url', 'unknown')
                form['page_title'] = node.get('title', 'unknown')
                form['form_action'] = form.get('action', 'unknown')
                all_forms.append(form)

        if skipped_no_submit:
            logger.info(f"Skipped {skipped_no_submit} form(s) with no submit button (decorative)")
        
        form_data = {
            'forms': all_forms,
            'node_map': node_map
        }
        
        logger.info(f"Found {len(graph_data['nodes'])} nodes, {len(graph_data['edges'])} edges, {len(form_data['forms'])} forms")
        
        # Generate all test types
        results = {
            'metadata': {
                'source_file': 'from_dict',
                'total_nodes': len(graph_data['nodes']),
                'total_edges': len(graph_data['edges']),
                'total_forms': len(form_data['forms'])
            },
            'test_cases': {}
        }
        
        # Generate tests (same logic as generate_all_tests)
        logger.info("Generating BVA test cases...")
        bva_tests = self.bva_generator.generate(form_data)
        bva_tests = self._deduplicate_tests(bva_tests, "BVA")
        results['test_cases']['bva'] = bva_tests
        logger.info(f"✅ Generated {len(bva_tests)} BVA test cases")
        
        logger.info("Generating ECP test cases...")
        ecp_tests = self.ecp_generator.generate(form_data)
        ecp_tests = self._deduplicate_tests(ecp_tests, "ECP")
        results['test_cases']['ecp'] = ecp_tests
        logger.info(f"✅ Generated {len(ecp_tests)} ECP test cases")
        
        logger.info("Generating Decision Table test cases...")
        decision_tests = self.decision_table_generator.generate(form_data)
        results['test_cases']['decision_table'] = decision_tests
        logger.info(f"✅ Generated {len(decision_tests)} Decision Table test cases")
        
        logger.info("Generating State Transition test cases...")
        state_tests = self.state_transition_generator.generate(graph_data)
        results['test_cases']['state_transition'] = state_tests
        logger.info(f"✅ Generated {len(state_tests)} State Transition test cases")
        
        logger.info("Generating Use Case test cases...")
        usecase_tests = self.use_case_generator.generate(graph_data, form_data)
        results['test_cases']['use_case'] = usecase_tests
        logger.info(f"✅ Generated {len(usecase_tests)} Use Case test cases")

        # Enrich BVA/ECP/DecisionTable test_data with companion field values
        logger.info("Enriching test cases with companion field data...")
        self._enrich_companion_data(results, all_forms)

        total_tests = (
            len(bva_tests) + len(ecp_tests) + len(decision_tests) +
            len(state_tests) + len(usecase_tests)
        )

        results['summary'] = {
            'total_test_cases': total_tests,
            'bva_count': len(bva_tests),
            'ecp_count': len(ecp_tests),
            'decision_table_count': len(decision_tests),
            'state_transition_count': len(state_tests),
            'use_case_count': len(usecase_tests)
        }

        logger.info(f"🎉 Total test cases generated: {total_tests}")

        self.all_test_cases = results
        return results

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of generated test cases"""
        if not self.all_test_cases:
            return self._empty_summary()
        
        return self.all_test_cases.get('summary', {})
    
    def export_tests(self, output_path: str) -> bool:
        """
        Export generated test cases to JSON file
        
        Args:
            output_path: Path to save test cases
            
        Returns:
            True if successful, False otherwise
        """
        if not self.all_test_cases:
            logger.warning("No test cases to export")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.all_test_cases, f, indent=2, ensure_ascii=False)
            
            logger.info(f"✅ Test cases exported to: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export test cases: {e}")
            return False
    
    def _empty_result(self) -> Dict[str, Any]:
        """Return empty result structure"""
        return {
            'metadata': {},
            'test_cases': {
                'bva': [],
                'ecp': [],
                'decision_table': [],
                'state_transition': [],
                'use_case': []
            },
            'summary': {
                'total_test_cases': 0,
                'bva_count': 0,
                'ecp_count': 0,
                'decision_table_count': 0,
                'state_transition_count': 0,
                'use_case_count': 0
            }
        }
    
    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary"""
        return {
            'total_test_cases': 0,
            'bva_count': 0,
            'ecp_count': 0,
            'decision_table_count': 0,
            'state_transition_count': 0,
            'use_case_count': 0
        }

    # ── Submit-button detection ────────────────────────────────────────────

    @staticmethod
    def _form_has_submit(form: Dict) -> bool:
        """Return True when *form* contains a usable submission mechanism.

        A form is considered decorative (no submit) when:
        - No ``submit_button`` key, AND
        - No ``action`` attribute pointing to an endpoint, AND
        - No input of type submit/button inside the form
        """
        # Explicit submit_button recorded by the crawler
        if form.get('submit_button'):
            return True
        # Form has an action attribute (even "#" counts as a handler target)
        action = form.get('action', '')
        if action and action not in ('', 'unknown', None):
            return True
        # Any input of type submit inside the form
        for inp in form.get('inputs', []):
            itype = (inp.get('type') or '').lower()
            if itype in ('submit', 'button'):
                return True
        return False

    # ── Companion field enrichment ─────────────────────────────────────────

    # Field types that cannot / should not be filled
    _SKIP_TYPES = {
        'submit', 'button', 'hidden', 'reset', 'image', 'file',
        'checkbox', 'radio',
    }

    def _enrich_companion_data(
        self,
        results: Dict[str, Any],
        all_forms: List[Dict],
    ) -> None:
        """
        Post-process generated test cases so that ``test_data`` contains
        valid default values for EVERY fillable field in the form, not just
        the single field under test.

        Without this, submitting a form that expects e.g. email + name + message
        would fail validation on the empty fields rather than on the boundary
        value we are actually trying to exercise.

        Only BVA, ECP, and DecisionTable test cases are enriched — State
        Transition and Use Case tests describe navigation flows, not field-level
        form filling.
        """
        # Build lookup: form_id -> list of fillable inputs
        form_lookup: Dict[str, List[Dict]] = {}
        for form in all_forms:
            fid = form.get('signature', form.get('id', ''))
            if fid:
                form_lookup[fid] = form.get('inputs', [])

        enrich_types = ['bva', 'ecp', 'decision_table']
        tc_section = results.get('test_cases', {})

        enriched_count = 0
        for tc_type in enrich_types:
            for tc in tc_section.get(tc_type, []):
                form_id = tc.get('form_id', '')
                tested_field = tc.get('field_name', '')

                if not form_id or form_id not in form_lookup:
                    continue

                companion = self._build_companion_defaults(
                    form_lookup[form_id], tested_field
                )
                if not companion:
                    continue

                # Companion data provides the baseline; the field under test
                # keeps its boundary/partition value (overrides companion).
                tc['test_data'] = {**companion, **tc.get('test_data', {})}
                enriched_count += 1

        logger.info(f"Enriched {enriched_count} test cases with companion field data")

    def _build_companion_defaults(
        self,
        form_inputs: List[Dict],
        skip_field_name: str,
    ) -> Dict[str, Any]:
        """
        Return a dict of ``{field_name: default_valid_value}`` for every
        fillable field in *form_inputs* except the one named *skip_field_name*.
        """
        companion: Dict[str, Any] = {}
        for field in form_inputs:
            ftype = (field.get('type') or 'text').lower()
            fname = field.get('name') or field.get('id') or ''

            # Skip unfillable / irrelevant field types
            if ftype in self._SKIP_TYPES:
                continue
            # Skip the field under test
            if fname == skip_field_name:
                continue
            # Skip disabled fields and fields with no usable identifier
            if field.get('disabled') or not fname:
                continue

            companion[fname] = self._generate_valid_default(field)

        return companion

    def _generate_valid_default(self, field: Dict) -> Any:
        """
        Return a realistic, valid value for *field* that will pass typical
        form validation so it does not interfere with our boundary test.
        """
        ftype = (field.get('type') or 'text').lower()
        # Combine all text identifiers for keyword matching
        fname = ' '.join(filter(None, [
            field.get('name', ''),
            field.get('id', ''),
            field.get('label', ''),
            field.get('placeholder', ''),
        ])).lower()

        # ── Typed inputs ──────────────────────────────────────────────────
        if ftype == 'email' or 'email' in fname:
            return 'tester@example.com'

        if ftype == 'password' or re.search(r'pass(word)?', fname):
            return 'Test@12345'

        if ftype == 'tel' or re.search(r'phone|mobile|cell|contact', fname):
            return '5551234567'

        if ftype == 'url' or re.search(r'url|website|web\s*site', fname):
            return 'https://example.com'

        if ftype == 'number' or ftype == 'range':
            min_v = field.get('min', field.get('minLength', 0)) or 0
            max_v = field.get('max', field.get('maxLength', 100)) or 100
            try:
                return int((float(min_v) + float(max_v)) / 2)
            except Exception:
                return 1

        if ftype == 'date':
            return '2025-06-15'

        if ftype == 'datetime-local':
            return '2025-06-15T12:00'

        if ftype == 'month':
            return '2025-06'

        if ftype == 'time':
            return '12:00'

        if ftype == 'textarea' or ftype == 'text' and re.search(
            r'message|comment|description|note|details?', fname
        ):
            return 'This is a test submission.'

        # ── Name family ───────────────────────────────────────────────────
        if re.search(r'first.?name', fname):
            return 'John'
        if re.search(r'last.?name|surname', fname):
            return 'Doe'
        if 'name' in fname:
            return 'John Doe'

        # ── Address family ────────────────────────────────────────────────
        if re.search(r'address|street', fname):
            return '123 Main Street'
        if 'city' in fname:
            return 'New York'
        if re.search(r'\bstate\b', fname):
            return 'NY'
        if re.search(r'zip|postal', fname):
            return '10001'
        if 'country' in fname:
            return 'US'

        # ── Account fields ────────────────────────────────────────────────
        if re.search(r'user.?name|login', fname):
            return 'testuser'
        if 'age' in fname:
            return 25
        if re.search(r'subject|title', fname):
            return 'Test Subject'

        # ── Generic fallback ──────────────────────────────────────────────
        return 'test'


if __name__ == '__main__':
    # Example usage
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python test_orchestrator.py <crawl_data.json> [output.json]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else 'generated_tests.json'
    
    orchestrator = TestOrchestrator()
    results = orchestrator.generate_all_tests(input_file)
    orchestrator.export_tests(output_file)
    
    print("\n" + "="*60)
    print("📊 TEST GENERATION SUMMARY")
    print("="*60)
    summary = results['summary']
    print(f"Total Test Cases: {summary['total_test_cases']}")
    print(f"  - BVA: {summary['bva_count']}")
    print(f"  - ECP: {summary['ecp_count']}")
    print(f"  - Decision Table: {summary['decision_table_count']}")
    print(f"  - State Transition: {summary['state_transition_count']}")
    print(f"  - Use Case: {summary['use_case_count']}")
    print("="*60)
