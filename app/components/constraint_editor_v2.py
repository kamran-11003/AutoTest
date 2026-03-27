"""
Updated Constraint Editor with New Architecture

Changes:
1. Constraints stored in separate file (constraint_storage.py)
2. File linking system (file_linking.py) tracks relationships
3. Updates existing test file instead of creating new one
4. Preserves AI refinements during regeneration
"""

import streamlit as st
from typing import Dict, List, Any
import json
from datetime import datetime
from pathlib import Path

# New imports
from test_generator.constraint_manager import constraint_manager
from test_generator.constraint_storage import constraint_storage
from test_generator.file_linking import file_linking
from test_generator.test_storage import TestStorage
from test_generator.test_orchestrator import TestOrchestrator
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


def display_constraint_editor(form_data: Dict, results: Dict):
    """
    Display constraint editor UI with new architecture
    
    Args:
        form_data: Form data with inputs
        results: Crawl results for context
    """
    st.markdown("### ⚙️ Constraint Manager")
    
    st.info("""
    **Edit field constraints and regenerate tests. All changes are tracked and AI refinements are preserved!**
    
    - **Constraints**: Stored separately from crawl files
    - **Versioning**: Each regeneration creates a new version
    - **AI Refinements**: Automatically preserved across regenerations
    """)
    
    # Get crawl hash and check file linking
    storage = TestStorage()
    crawl_hash = storage._get_crawl_hash(results)
    
    # Display current file links
    with st.expander("📎 File Links", expanded=False):
        links = file_linking.get_all_links_for_crawl(crawl_hash)
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption("**Crawl File:**")
            crawl_info = links.get('crawl_info', {})
            if crawl_info:
                st.code(crawl_info.get('crawl_file', 'N/A'))
            else:
                st.code("Not registered")
        
        with col2:
            st.caption("**Test File:**")
            test_file = links.get('test_file')
            if test_file:
                st.code(test_file)
            else:
                st.code("No tests generated")
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.caption("**Constraint File:**")
            constraint_file = links.get('constraint_file')
            if constraint_file:
                st.code(constraint_file)
            else:
                st.code("Using defaults")
        
        with col4:
            st.caption("**Version History:**")
            history = links.get('version_history', [])
            if history:
                latest = history[-1]
                st.code(f"v{latest['version']} ({len(history)} total)")
            else:
                st.code("v1")
    
    # Regenerate button at top
    if st.button("🔄 Regenerate Tests with Updated Constraints", 
                 type="primary",
                 disabled=not st.session_state.get('constraints_updated', False)):
        with st.spinner("Regenerating tests with updated constraints (preserving AI refinements)..."):
            
            # Get the edited field info from session
            edited_field_info = st.session_state.get('edited_field_info', {})
            
            if not edited_field_info:
                st.error("No field was edited. Please edit a field's constraints first.")
            else:
                field_id = edited_field_info.get('field_id')
                
                # Get current constraints from session
                updated_constraints = st.session_state.get('updated_constraints', {})
                
                # Save constraints to separate file
                constraint_storage.save_constraints(crawl_hash, updated_constraints)
                
                # Link constraint file
                constraint_file = f"constraints_{crawl_hash}.json"
                file_linking.link_constraints(crawl_hash, constraint_file)
                
                # Apply constraints to form data for regeneration
                updated_results = _apply_constraints_to_results(results, updated_constraints)
                
                # Regenerate tests (this will UPDATE existing file, preserving AI refinements)
                orchestrator = TestOrchestrator()
                test_results = orchestrator.generate_all_tests_from_dict(updated_results)
                
                # Recalculate summary
                test_cases = test_results.get('test_cases', {})
                summary = {
                    'total_test_cases': sum(len(tests) for tests in test_cases.values()),
                    'bva_count': len(test_cases.get('bva', [])),
                    'ecp_count': len(test_cases.get('ecp', [])),
                    'decision_table_count': len(test_cases.get('decision_table', [])),
                    'state_transition_count': len(test_cases.get('state_transition', [])),
                    'use_case_count': len(test_cases.get('use_case', []))
                }
                test_results['summary'] = summary
                
                # Save to storage (UPDATE existing file, preserve AI refinements)
                test_file = storage.save_tests(
                    test_results, 
                    updated_results,
                    metadata={'constraints_updated': True},
                    update_existing=True  # This is the key!
                )
                
                # Update file linking
                test_filename = Path(test_file).name
                version = storage.index[crawl_hash]['version']
                file_linking.link_tests(crawl_hash, test_filename, version)
                
                # Update session state
                st.session_state.generated_tests = test_results
                st.session_state.crawl_results = updated_results
                st.session_state.constraints_updated = False
                st.session_state.pop('edited_field_info', None)
                
                # Show summary
                st.success(f"✅ Tests updated with new constraints for field '{field_id}'!")
                st.info(f"**Version {version}** | Total: {summary['total_test_cases']} tests | AI refinements preserved ✨")
                
                st.rerun()
    
    # Manual Constraint Editor
    st.markdown("---")
    st.markdown("#### ✏️ Manual Constraint Editor")
    
    # Get all forms
    all_forms = []
    for node in results.get('nodes', []):
        for form in node.get('forms', []):
            all_forms.append({
                'form': form,
                'node_url': node.get('url', 'Unknown')
            })
    
    if not all_forms:
        st.warning("No forms found in crawl results")
        return
    
    # Form selector
    form_options = [f"Form {i+1} ({f['node_url']})" for i, f in enumerate(all_forms)]
    selected_form_idx = st.selectbox(
        "Select Form",
        range(len(form_options)),
        format_func=lambda x: form_options[x]
    )
    
    selected_form = all_forms[selected_form_idx]['form']
    form_inputs = selected_form.get('inputs', [])
    
    if not form_inputs:
        st.warning("No input fields found in this form")
        return
    
    # Field selector
    field_options = []
    for i, field in enumerate(form_inputs):
        field_type = field.get('type', 'unknown')
        field_id = field.get('id') or field.get('name') or f"field_{i}"
        field_label = field.get('label') or field.get('placeholder') or field_id
        field_options.append(f"{field_label} ({field_type})")
    
    selected_field_idx = st.selectbox(
        "Select Field to Edit",
        range(len(field_options)),
        format_func=lambda x: field_options[x],
        key="field_selector"
    )
    
    selected_field = form_inputs[selected_field_idx]
    field_id = selected_field.get('id') or selected_field.get('name') or f"field_{selected_field_idx}"
    field_type = selected_field.get('type', 'text')
    
    # Load existing constraints (from constraint_storage or session or defaults)
    if constraint_storage.has_constraints(crawl_hash):
        saved_constraints = constraint_storage.load_constraints(crawl_hash) or {}
        current_field_constraints = saved_constraints.get(field_id, {})
    else:
        current_field_constraints = {}
    
    # Check session state for recent updates
    updated_constraints = st.session_state.get('updated_constraints', {})
    if field_id in updated_constraints:
        current_field_constraints = updated_constraints[field_id]
    
    # If no constraints, get from constraint_manager defaults
    if not current_field_constraints:
        current_field_constraints = constraint_manager.get_constraints_for_field(selected_field)
    
    # Display current field info
    st.markdown(f"**Editing:** `{field_id}` ({field_type})")
    
    # Edit constraints based on field type
    if field_type in ['text', 'textarea', 'email', 'tel', 'url', 'search']:
        st.markdown("##### Text Constraints")
        
        col1, col2 = st.columns(2)
        with col1:
            new_minlength = st.number_input(
                "Min Length",
                value=current_field_constraints.get('minlength', 0),
                min_value=0,
                max_value=10000,
                key=f"minlen_{field_id}"
            )
        
        with col2:
            new_maxlength = st.number_input(
                "Max Length",
                value=current_field_constraints.get('maxlength', 255),
                min_value=1,
                max_value=10000,
                key=f"maxlen_{field_id}"
            )
        
        if st.button("💾 Update Text Constraints", key=f"update_text_{field_id}"):
            # Store in session
            if 'updated_constraints' not in st.session_state:
                st.session_state.updated_constraints = {}
            
            st.session_state.updated_constraints[field_id] = {
                'minlength': new_minlength,
                'maxlength': new_maxlength,
                'type': field_type
            }
            
            # Update field data
            selected_field['minlength'] = new_minlength
            selected_field['maxlength'] = new_maxlength
            
            # Store field info for regeneration
            st.session_state.edited_field_info = {
                'field_id': field_id,
                'form_index': selected_form_idx,
                'field_index': selected_field_idx,
                'field_data': selected_field
            }
            
            st.session_state.constraints_updated = True
            st.success(f"✅ Constraints updated! Click 'Regenerate' to apply changes.")
            st.rerun()
    
    elif field_type in ['number', 'range']:
        st.markdown("##### Numeric Constraints")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            new_min = st.number_input(
                "Min Value",
                value=float(current_field_constraints.get('min', 0)),
                key=f"min_{field_id}"
            )
        
        with col2:
            new_max = st.number_input(
                "Max Value",
                value=float(current_field_constraints.get('max', 999999)),
                key=f"max_{field_id}"
            )
        
        with col3:
            new_step = st.number_input(
                "Step",
                value=float(current_field_constraints.get('step', 1)),
                min_value=0.01,
                key=f"step_{field_id}"
            )
        
        if st.button("💾 Update Numeric Constraints", key=f"update_num_{field_id}"):
            if 'updated_constraints' not in st.session_state:
                st.session_state.updated_constraints = {}
            
            st.session_state.updated_constraints[field_id] = {
                'min': new_min,
                'max': new_max,
                'step': new_step,
                'type': field_type
            }
            
            selected_field['min'] = new_min
            selected_field['max'] = new_max
            selected_field['step'] = new_step
            
            st.session_state.edited_field_info = {
                'field_id': field_id,
                'form_index': selected_form_idx,
                'field_index': selected_field_idx,
                'field_data': selected_field
            }
            
            st.session_state.constraints_updated = True
            st.success(f"✅ Constraints updated! Click 'Regenerate' to apply changes.")
            st.rerun()


def _apply_constraints_to_results(results: Dict, constraints: Dict) -> Dict:
    """
    Apply constraint dictionary to results
    
    Args:
        results: Crawl results
        constraints: field_id -> constraints mapping
        
    Returns:
        Updated results with constraints applied
    """
    updated = results.copy()
    
    for node in updated.get('nodes', []):
        for form in node.get('forms', []):
            for field in form.get('inputs', []):
                field_id = field.get('id') or field.get('name')
                if field_id and field_id in constraints:
                    field_constraints = constraints[field_id]
                    # Apply constraints to field
                    for key, value in field_constraints.items():
                        if key != 'type':  # Don't overwrite type
                            field[key] = value
    
    return updated
