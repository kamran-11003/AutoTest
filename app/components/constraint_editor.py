"""
Constraint Editor UI Component

Provides interactive UI for:
1. Viewing constraint coverage analysis
2. Manually editing constraints
3. Regenerating tests with new constraints
4. Using AI to refine constraints
"""

import streamlit as st
from typing import Dict, List, Any
import json
from datetime import datetime
from test_generator.constraint_manager import constraint_manager
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


def display_constraint_editor(form_data: Dict, results: Dict):
    """
    Display constraint editor UI
    
    Args:
        form_data: Form data with inputs
        results: Crawl results for context
    """
    st.markdown("### ⚙️ Constraint Manager")
    
    st.info("""
    **Edit field constraints and regenerate tests for specific fields while preserving all AI refinements.**
    """)
    
    # Regenerate button at top
    if st.button("🔄 Regenerate Tests with Updated Constraints", 
                 width='stretch',
                 type="primary",
                 disabled=not st.session_state.get('constraints_updated', False)):
        with st.spinner("Regenerating ALL tests with updated constraints..."):
            from test_generator.test_orchestrator import TestOrchestrator
            from test_generator.test_storage import TestStorage
            import tempfile
            import json
            import os
            
            storage = TestStorage()
            
            # Get updated form data
            updated_form_data = st.session_state.get('updated_form_data', form_data)
            
            # Get the edited field info from session
            edited_field_info = st.session_state.get('edited_field_info', {})
            
            if not edited_field_info:
                st.error("No field was edited. Please edit a field's constraints first.")
            else:
                field_id = edited_field_info.get('field_id')
                form_index = edited_field_info.get('form_index')
                field_index = edited_field_info.get('field_index')
                
                # CRITICAL: Update the ACTUAL field in results with new constraints
                updated_crawl = results.copy()
                
                # Find and update the specific field in all nodes
                form_counter = 0
                for node in updated_crawl.get('nodes', []):
                    for form in node.get('forms', []):
                        if form_counter == form_index:
                            # Found the form, update the field
                            if field_index < len(form.get('inputs', [])):
                                # Get the updated field data
                                updated_field = edited_field_info.get('field_data')
                                form['inputs'][field_index] = updated_field
                                logger.info(f"Updated field {field_id} with constraints: {updated_field.get('minlength')}-{updated_field.get('maxlength')}")
                        form_counter += 1
                
                # Save updated crawl to temp file
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                    json.dump(updated_crawl, tmp, indent=2)
                    tmp_path = tmp.name
                
                try:
                    # Regenerate ALL tests with updated constraints
                    orchestrator = TestOrchestrator()
                    test_results = orchestrator.generate_all_tests(tmp_path)
                    
                    # Recalculate summary
                    test_cases = test_results.get('test_cases', {})
                    bva_count = len(test_cases.get('bva', []))
                    ecp_count = len(test_cases.get('ecp', []))
                    dt_count = len(test_cases.get('decision_table', []))
                    st_count = len(test_cases.get('state_transition', []))
                    uc_count = len(test_cases.get('use_case', []))
                    
                    total_tests = bva_count + ecp_count + dt_count + st_count + uc_count
                    
                    test_results['summary'] = {
                        'total_test_cases': total_tests,
                        'bva_count': bva_count,
                        'ecp_count': ecp_count,
                        'decision_table_count': dt_count,
                        'state_transition_count': st_count,
                        'use_case_count': uc_count
                    }
                    
                    # Save to storage
                    storage.save_tests(test_results, updated_crawl, 
                                     metadata={
                                         'ai_refined': False,  # Full regeneration loses AI refinements
                                         'constraints_updated': True
                                     })
                    
                    # Update session state
                    st.session_state.generated_tests = test_results
                    st.session_state.crawl_results = updated_crawl  # Update crawl results too!
                    st.session_state.constraints_updated = False
                    st.session_state.pop('updated_form_data', None)
                    st.session_state.pop('edited_field_info', None)
                    
                    # CRITICAL: Save updated crawl to disk so constraints persist
                    # Find the most recent crawl file and update it
                    from pathlib import Path
                    crawls_dir = Path("data/crawled_graphs")
                    if crawls_dir.exists():
                        crawl_files = sorted(crawls_dir.glob("crawl_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
                        if crawl_files:
                            # Update the most recent crawl file (assume it's the current one)
                            latest_crawl = crawl_files[0]
                            with open(latest_crawl, 'w', encoding='utf-8') as f:
                                json.dump(updated_crawl, f, indent=2, ensure_ascii=False)
                            logger.info(f"Updated crawl file with new constraints: {latest_crawl}")
                    
                    # Show summary
                    st.success(f"✅ Tests regenerated with updated constraints for field '{field_id}'!")
                    st.info(f"Total: {total_tests} tests (BVA: {bva_count}, ECP: {ecp_count}, DT: {dt_count}, ST: {st_count}, UC: {uc_count})")
                    st.warning("⚠️ Note: Full regeneration was performed. AI refinements were not preserved.")
                    
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                
                st.rerun()
    
    # Manual Constraint Editor
    st.markdown("---")
    st.markdown("#### ✏️ Manual Constraint Editor")
    
    # Get all forms
    all_forms = form_data.get('forms', [])
    
    if not all_forms:
        st.warning("No forms found in crawl data")
        return
    
    # Form selector
    form_options = [f"{i+1}. {form.get('url', 'Unknown')} - {len(form.get('inputs', []))} fields" 
                   for i, form in enumerate(all_forms)]
    
    selected_form_idx = st.selectbox(
        "Select Form to Edit",
        range(len(all_forms)),
        format_func=lambda x: form_options[x]
    )
    
    if selected_form_idx is not None:
        selected_form = all_forms[selected_form_idx]
        form_inputs = selected_form.get('inputs', [])
        
        # Filter out non-editable fields
        editable_inputs = [
            inp for inp in form_inputs 
            if inp.get('type', '').lower() not in ['submit', 'button', 'hidden', 'reset', 'image']
        ]
        
        if not editable_inputs:
            st.info("No editable fields in this form")
            return
        
        st.markdown(f"**Form:** `{selected_form.get('url', 'Unknown')}`")
        st.markdown(f"**Editable Fields:** {len(editable_inputs)}")
        
        # Field editor
        for idx, field in enumerate(editable_inputs):
            field_name = field.get('name') or field.get('id', f'field_{idx}')
            field_type = field.get('type', 'text')
            field_label = field.get('label', '') or field.get('placeholder', '') or field_name
            
            with st.expander(f"📝 {field_label} ({field_type})", expanded=False):
                st.markdown(f"**Field Name:** `{field_name}`")
                st.markdown(f"**Field Type:** `{field_type}`")
                
                # Current constraints
                current_constraints = constraint_manager.get_constraints_for_field(field)
                
                st.markdown("**Current Constraints:**")
                if current_constraints:
                    st.json(current_constraints)
                else:
                    st.caption("_No constraints defined_")
                
                # Edit constraints based on field type
                st.markdown("**Edit Constraints:**")
                
                if field_type in ['number', 'range']:
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        new_min = st.number_input(
                            "Min",
                            value=current_constraints.get('min', 0),
                            key=f"min_{selected_form_idx}_{idx}"
                        )
                    with col2:
                        new_max = st.number_input(
                            "Max",
                            value=current_constraints.get('max', 100),
                            key=f"max_{selected_form_idx}_{idx}"
                        )
                    with col3:
                        new_step = st.number_input(
                            "Step",
                            value=current_constraints.get('step', 1),
                            min_value=0.01,
                            key=f"step_{selected_form_idx}_{idx}"
                        )
                    
                    if st.button(f"Update Numeric Constraints", key=f"update_num_{selected_form_idx}_{idx}"):
                        # Update field in place
                        field['min'] = new_min
                        field['max'] = new_max
                        field['step'] = new_step
                        
                        # Update in form_data structure
                        all_forms[selected_form_idx]['inputs'][idx] = field
                        form_data['forms'] = all_forms
                        
                        # Store updated form data
                        st.session_state['updated_form_data'] = form_data
                        
                        # Store edited field info for regeneration
                        st.session_state['edited_field_info'] = {
                            'field_id': field_name,
                            'form_url': selected_form.get('url', 'Unknown'),
                            'field_data': field.copy(),  # Copy to preserve values
                            'form_index': selected_form_idx,
                            'field_index': idx
                        }
                        
                        st.success(f"✅ Updated {field_label} constraints")
                        st.session_state.constraints_updated = True
                
                elif field_type in ['text', 'email', 'tel', 'url', 'password', 'search', 'textarea']:
                    # Check if this field was recently updated
                    updated_form_data = st.session_state.get('updated_form_data', {})
                    if updated_form_data and 'forms' in updated_form_data:
                        if selected_form_idx < len(updated_form_data['forms']):
                            updated_form = updated_form_data['forms'][selected_form_idx]
                            if idx < len(updated_form.get('inputs', [])):
                                updated_field = updated_form['inputs'][idx]
                                if updated_field.get('name') == field_name:
                                    # Use updated constraints
                                    current_constraints = constraint_manager.get_constraints_for_field(updated_field)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        new_minlength = st.number_input(
                            "Min Length",
                            value=current_constraints.get('minlength', 0),
                            min_value=0,
                            key=f"minlen_{selected_form_idx}_{idx}"
                        )
                    with col2:
                        new_maxlength = st.number_input(
                            "Max Length",
                            value=current_constraints.get('maxlength', 255),
                            min_value=1,
                            key=f"maxlen_{selected_form_idx}_{idx}"
                        )
                    
                    new_pattern = st.text_input(
                        "Pattern (regex)",
                        value=current_constraints.get('pattern', ''),
                        key=f"pattern_{selected_form_idx}_{idx}",
                        help="Optional regex pattern for validation"
                    )
                    
                    if st.button(f"Update Text Constraints", key=f"update_text_{selected_form_idx}_{idx}"):
                        # Update field in place
                        field['minlength'] = new_minlength
                        field['maxlength'] = new_maxlength
                        if new_pattern:
                            field['pattern'] = new_pattern
                        
                        # Update in form_data structure
                        all_forms[selected_form_idx]['inputs'][idx] = field
                        form_data['forms'] = all_forms
                        
                        # Store updated form data
                        st.session_state['updated_form_data'] = form_data
                        
                        # Store edited field info for regeneration
                        st.session_state['edited_field_info'] = {
                            'field_id': field_name,
                            'form_url': selected_form.get('url', 'Unknown'),
                            'field_data': field.copy(),  # Copy to preserve values
                            'form_index': selected_form_idx,
                            'field_index': idx
                        }
                        
                        st.success(f"✅ Updated {field_label} constraints")
                        st.session_state.constraints_updated = True
                
                elif field_type in ['date', 'datetime-local', 'month', 'week', 'time']:
                    col1, col2 = st.columns(2)
                    with col1:
                        new_min_date = st.text_input(
                            "Min Date",
                            value=current_constraints.get('min', '2000-01-01'),
                            key=f"mindate_{selected_form_idx}_{idx}",
                            help="Format: YYYY-MM-DD"
                        )
                    with col2:
                        new_max_date = st.text_input(
                            "Max Date",
                            value=current_constraints.get('max', '2099-12-31'),
                            key=f"maxdate_{selected_form_idx}_{idx}",
                            help="Format: YYYY-MM-DD"
                        )
                    
                    if st.button(f"Update Date Constraints", key=f"update_date_{selected_form_idx}_{idx}"):
                        field['min'] = new_min_date
                        field['max'] = new_max_date
                        st.success(f"✅ Updated {field_label} constraints")
                        st.session_state.constraints_updated = True
                
                else:
                    st.caption(f"_Constraint editing not available for type '{field_type}'_")


def display_constraint_summary():
    """Display constraint update status in sidebar"""
    if st.session_state.get('constraints_updated', False):
        st.sidebar.warning("⚠️ Constraints updated! Regenerate tests to apply changes.")
        if st.sidebar.button("🔄 Regenerate Now"):
            st.switch_page("app/streamlit_app.py")
