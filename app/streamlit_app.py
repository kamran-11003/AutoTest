"""
Streamlit Dashboard
Main UI for the Black-Box Web Crawler
"""
import streamlit as st
import asyncio
import os
import sys
import json
from pathlib import Path
import pandas as pd
from datetime import datetime
from typing import Optional, List  # NEW: Add type hints

# Windows-specific asyncio fix for Playwright
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from crawler.orchestrator import CrawlerOrchestrator
from app.components.graph_viz import GraphVisualizer
from app.utils.exporter import Exporter
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="AutoTestAI Crawler",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F77B4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stat-box {
        background-color: #F0F2F6;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1F77B4;
    }
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
</style>
""", unsafe_allow_html=True)


def transform_loaded_data(loaded_data: dict) -> dict:
    """
    Transform loaded JSON data to expected format for display_results()
    
    Converts:
        {nodes: [...], edges: [...], stats: {...}}
    To:
        {crawl_stats: {...}, graph_stats: {...}, states: [...], nodes: [...], edges: [...]}
    """
    # If already in correct format, return as-is
    if 'crawl_stats' in loaded_data and 'states' in loaded_data:
        return loaded_data
    
    # Transform nodes to states
    nodes = loaded_data.get('nodes', [])
    stats = loaded_data.get('stats', {})
    
    # FILTER OUT ORPHAN NODES: Only include nodes with valid URLs
    # Orphan nodes were created as placeholders during crawling but never filled
    valid_nodes = [node for node in nodes if node.get('url', '').strip()]
    
    if len(valid_nodes) < len(nodes):
        logger.info(f"🧹 Filtered out {len(nodes) - len(valid_nodes)} orphan nodes (no URL)")
    
    # Calculate crawl stats from valid nodes only
    total_inputs = sum(node.get('input_count', 0) for node in valid_nodes)
    total_forms = sum(node.get('form_count', 0) for node in valid_nodes)
    total_links = sum(node.get('link_count', 0) for node in valid_nodes)
    
    # Build states array (nodes contain all state info)
    states = []
    for node in valid_nodes:
        state = {
            'hash': node.get('id', node.get('hash', '')),
            'state_hash': node.get('id', node.get('hash', '')),
            'url': node.get('url', ''),
            'normalized_url': node.get('normalized_url', ''),
            'title': node.get('title', ''),
            'timestamp': node.get('timestamp', ''),
            'input_count': node.get('input_count', 0),
            'button_count': node.get('button_count', 0),
            'link_count': node.get('link_count', 0),
            'form_count': node.get('form_count', 0),
            'inputs': node.get('inputs', []),
            'buttons': node.get('buttons', []),
            'links': node.get('links', []),
            'forms': node.get('forms', [])
        }
        states.append(state)
    
    # Build transformed result (use valid_nodes for nodes field too)
    transformed = {
        'crawl_stats': {
            'pages_crawled': len(valid_nodes),
            'total_forms': total_forms,
            'total_inputs': total_inputs,
            'total_links': total_links,
            'start_url': valid_nodes[0].get('url', '') if valid_nodes else '',
            'max_depth_reached': 0,
            'unique_urls': len(valid_nodes),
            'total_states': len(valid_nodes)
        },
        'graph_stats': {
            **stats,
            'node_count': len(valid_nodes)  # Update with correct count
        },
        'ai_stats': {
            'enabled': False,
            'total_calls': 0
        },
        'states': states,
        'nodes': valid_nodes,  # Only include valid nodes
        'edges': loaded_data.get('edges', [])
    }
    
    return transformed


def run_async(coro):
    """
    Helper to run async code in Streamlit
    Handles Windows-specific event loop issues
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


def main():
    """Main Streamlit application"""
    
    # Initialize session state
    if 'crawl_results' not in st.session_state:
        st.session_state.crawl_results = None
    if 'crawl_running' not in st.session_state:
        st.session_state.crawl_running = False
    if 'selected_node' not in st.session_state:
        st.session_state.selected_node = None
    
    # Header
    st.markdown('<div class="main-header">🕸️ AutoTestAI Black-Box Crawler</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar - Configuration
    with st.sidebar:
        st.header("⚙️ Crawl Configuration")
        
        # Add button to load previous crawls
        st.markdown("---")
        st.subheader("📂 Load Previous Crawl")
        
        # Get list of saved crawls
        crawls_dir = Path("data/crawled_graphs")
        if crawls_dir.exists():
            # All JSON files in crawled_graphs – sorted newest first
            saved_crawls = sorted(
                [f.stem for f in crawls_dir.glob("*.json")],
                reverse=True
            )
            if saved_crawls:
                selected_crawl = st.selectbox(
                    "Select a crawl:",
                    [""] + saved_crawls,
                    key="crawl_selector"
                )
                
                if st.button("Load Selected Crawl", disabled=(not selected_crawl)):
                    try:
                        from test_generator.test_storage import TestStorage
                        from test_generator.file_linking import file_linking
                        from test_generator.constraint_storage import constraint_storage
                        
                        crawl_file = crawls_dir / f"{selected_crawl}.json"
                        with open(crawl_file, 'r', encoding='utf-8') as f:
                            loaded_data = json.load(f)
                        
                        # Transform loaded data to expected format
                        transformed_data = transform_loaded_data(loaded_data)
                        
                        # Load corresponding test cases for this crawl
                        storage = TestStorage()
                        crawl_hash = storage._get_crawl_hash(transformed_data)
                        
                        # Register crawl in file linking system
                        file_linking.register_crawl(
                            crawl_file=f"{selected_crawl}.json",
                            crawl_hash=crawl_hash,
                            metadata={
                                'url': transformed_data.get('nodes', [{}])[0].get('url', '') if transformed_data.get('nodes') else '',
                                'timestamp': datetime.now().isoformat()
                            }
                        )
                        
                        # Load constraints for this crawl
                        if constraint_storage.has_constraints(crawl_hash):
                            constraints = constraint_storage.load_constraints(crawl_hash)
                            st.session_state.loaded_constraints = constraints
                        else:
                            st.session_state.loaded_constraints = None
                        
                        # Use file linking to get correct test file
                        test_file = file_linking.get_test_file(crawl_hash)
                        
                        if test_file or storage.has_tests_for_crawl(transformed_data):
                            stored_data = storage.load_tests(crawl_hash=crawl_hash)
                            if stored_data:
                                test_results = stored_data['test_results']
                                
                                # Link test file if not already linked
                                if not test_file:
                                    test_filename = storage.index[crawl_hash]['filename']
                                    version = storage.index[crawl_hash].get('version', 1)
                                    file_linking.link_tests(crawl_hash, test_filename, version)
                                
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
                                
                                st.session_state.generated_tests = test_results
                                st.success(f"✅ Loaded crawl: {selected_crawl} with {total_tests} test cases")
                            else:
                                st.session_state.generated_tests = None
                                st.success(f"✅ Loaded crawl: {selected_crawl} (no test cases generated yet)")
                        else:
                            st.session_state.generated_tests = None
                            st.success(f"✅ Loaded crawl: {selected_crawl} (no test cases generated yet)")
                        
                        st.session_state.crawl_results = transformed_data
                        st.session_state['selected_crawl'] = selected_crawl
                        st.session_state.selected_node = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to load crawl: {str(e)}")
            else:
                st.info("No saved crawls found")
        else:
            st.info("No crawls directory found")
        
        st.markdown("---")
        
        # Basic settings
        start_url = st.text_input(
            "🎯 Start URL",
            value="https://demoqa.com",
            help="The URL where crawling will begin"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            max_depth = st.slider(
                "📊 Max Depth",
                min_value=1,
                max_value=10,
                value=5,
                help="Maximum navigation depth"
            )
        with col2:
            max_pages = st.slider(
                "📄 Max Pages",
                min_value=10,
                max_value=200,
                value=50,
                help="Maximum pages to crawl"
            )
        
        headless = st.checkbox(
            "🚀 Headless Mode",
            value=False,
            help="Run browser in headless mode (no UI)"
        )
        
        st.markdown("---")
        
        # Advanced settings
        st.header("🔧 Advanced Options")
        
        enable_ai = st.checkbox(
            "🤖 Use Gemini AI Enrichment",
            value=True,
            help="Use AI to detect non-semantic elements"
        )
        
        enable_normalization = st.checkbox(
            "🔗 Enable URL Normalization",
            value=True,
            help="Merge dynamic routes (/product/:id)"
        )
        
        # NEW: Seed URLs
        st.markdown("---")
        st.subheader("🌱 Seed URLs (Optional)")
        seed_urls_text = st.text_area(
            "Additional URLs to crawl",
            value="",
            height=100,
            placeholder="/products\n/category/electronics\n/about",
            help="One URL per line (relative or absolute). These will be added to the crawl queue."
        )
        
        st.markdown("---")
        
        # Session management
        st.header("🔐 Session")
        
        session_exists = Path("auth_session.json").exists()
        if session_exists:
            st.success("✅ Saved session found")
            if st.button("🔄 Clear Session"):
                os.remove("auth_session.json")
                st.rerun()
        else:
            st.info("ℹ️ Manual login will be required")
        
        st.markdown("---")
        
        # Start crawl button
        if not st.session_state.crawl_running:
            if st.button("▶️ Start Crawl", type="primary"):
                st.session_state.crawl_running = True
                st.rerun()
        else:
            st.warning("⏳ Crawl in progress...")
    
    # Parse seed URLs
    seed_urls = None
    if seed_urls_text.strip():
        seed_urls = [url.strip() for url in seed_urls_text.strip().split('\n') if url.strip()]
    
    # Main content area
    if st.session_state.crawl_running:
        run_crawl(
            start_url,
            max_depth,
            max_pages,
            headless,
            enable_ai,
            enable_normalization,
            seed_urls  # NEW parameter
        )
    elif st.session_state.crawl_results:
        display_results(st.session_state.crawl_results)
    else:
        display_welcome()


def display_welcome():
    """Display welcome screen"""
    st.markdown("## 👋 Welcome to AutoTestAI Crawler")
    
    st.markdown("""
    ### 🎯 Features
    - ✅ **Universal Detection**: Works with React, Vue, Angular, and plain HTML
    - ✅ **SPA Support**: Detects client-side navigation without URL changes
    - ✅ **AI-Powered**: Gemini API detects non-semantic interactive elements
    - ✅ **URL Normalization**: Merges dynamic routes like `/product/:id`
    - ✅ **Interactive Graphs**: Visualize your application's state machine
    - ✅ **Multiple Export Formats**: JSON, CSV, GraphML, and more
    
    ### 🚀 Quick Start
    1. Configure your crawl in the sidebar
    2. Click **"Start Crawl"**
    3. Log in manually when prompted (if required)
    4. Wait for the crawl to complete
    5. View and export results
    
    ### 📖 Documentation
    See `ENHANCED_PRD_v2.md` for full documentation.
    """)
    
    # Example sites
    st.markdown("### 🧪 Try These Demo Sites")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**DemoQA**")
        st.code("https://demoqa.com")
        st.caption("Forms, tables, interactions")
    
    with col2:
        st.markdown("**Sauce Demo**")
        st.code("https://www.saucedemo.com")
        st.caption("E-commerce demo (login: standard_user / secret_sauce)")
    
    with col3:
        st.markdown("**The Internet**")
        st.code("https://the-internet.herokuapp.com")
        st.caption("Various test scenarios")


def run_crawl(
    start_url: str,
    max_depth: int,
    max_pages: int,
    headless: bool,
    enable_ai: bool,
    enable_normalization: bool,
    seed_urls: Optional[List[str]] = None  # NEW parameter
):
    """Execute the crawl"""
    st.markdown("## 🔄 Crawl in Progress")
    
    progress_placeholder = st.empty()
    log_placeholder = st.empty()
    
    try:
        # Update config (simplified - would need proper config management)
        orchestrator = CrawlerOrchestrator()
        
        # Override config
        orchestrator.config['crawler']['headless'] = headless
        orchestrator.config['ai_enrichment']['enabled'] = enable_ai
        orchestrator.config['url_normalization']['enabled'] = enable_normalization
        # Note: submit_forms is always False for safety (wizard auto-fills forms)
        orchestrator.config['interaction']['submit_forms'] = False
        
        progress_placeholder.info("🚀 Starting crawler...")
        
        # Run crawl using our helper to avoid event loop conflicts
        results = run_async(
            orchestrator.start_crawl(
                start_url=start_url,
                manual_login=not Path("auth_session.json").exists(),
                max_depth=max_depth,
                max_pages=max_pages,
                seed_urls=seed_urls  # NEW: Pass seed URLs
            )
        )
        
        # Export results
        orchestrator.export_results()
        
        # Store results in session state
        st.session_state.crawl_results = results
        st.session_state.crawl_running = False
        
        # Debug: Show what we got
        logger.info(f"Crawl results structure: {list(results.keys())}")
        if 'states' in results:
            logger.info(f"Found {len(results['states'])} states")
        if 'nodes' in results:
            logger.info(f"Found {len(results['nodes'])} nodes")
        
        progress_placeholder.success("✅ Crawl completed successfully!")
        st.rerun()
    
    except Exception as e:
        st.session_state.crawl_running = False
        st.error(f"❌ Crawl failed: {e}")
        logger.error(f"Crawl error: {e}")


def display_results(results: dict):
    """Display crawl results"""
    st.markdown("## 📊 Crawl Results")
    
    # Statistics
    stats = results.get('crawl_stats', {})
    graph_stats = results.get('graph_stats', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('pages_crawled', 0)}</div>
            <div class="stat-label">Pages Crawled</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('total_forms', 0)}</div>
            <div class="stat-label">Forms Found</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{stats.get('total_inputs', 0)}</div>
            <div class="stat-label">Input Fields</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-box">
            <div class="stat-value">{graph_stats.get('node_count', 0)}</div>
            <div class="stat-label">Unique States</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📈 Graph", "📋 Pages", "🔍 Elements", "🧪 Test Cases", "💾 Export", "🚀 Execute Tests"])
    
    with tab1:
        display_graph(results)
    
    with tab2:
        display_pages_table(results)
    
    with tab3:
        display_elements_table(results)
    
    with tab4:
        display_test_cases(results)
    
    with tab5:
        display_export_options(results)
    
    with tab6:
        display_execute_tests(results)


def display_graph(results: dict):
    """Display interactive graph"""
    st.markdown("### 🕸️ Interactive State Graph")
    
    try:
        # Create visualizer
        visualizer = GraphVisualizer()
        
        # Generate graph HTML
        graph_file = "data/temp_graph.html"
        
        # Get graph data from results (check different possible structures)
        graph_data = None
        
        # Option 1: Direct graph data
        if 'nodes' in results and 'edges' in results:
            graph_data = results
        
        # Option 2: Load from exported files
        else:
            try:
                from pathlib import Path
                
                # Find latest graph JSON
                graph_dir = Path("data/crawled_graphs")
                if graph_dir.exists():
                    json_files = list(graph_dir.glob("*.json"))
                    if json_files:
                        latest_file = max(json_files, key=lambda p: p.stat().st_mtime)
                        with open(latest_file, 'r') as f:
                            graph_data = json.load(f)
                        st.info(f"📂 Loaded graph from: {latest_file.name}")
            except Exception as e:
                logger.error(f"Error loading graph file: {e}")
        
        # Option 3: Build graph from states
        if not graph_data:
            st.warning("⚠️ Building graph from states (edges may be incomplete)")
            graph_data = {
                'nodes': [],
                'edges': []
            }
            
            states = results.get('states', [])
            for state in states:
                graph_data['nodes'].append({
                    'id': state.get('hash') or state.get('state_hash'),
                    'url': state.get('url'),
                    'normalized_url': state.get('normalized_url'),
                    'title': state.get('title', 'Untitled'),
                    'form_count': state.get('form_count', 0),
                    'input_count': state.get('input_count', 0),
                    'link_count': state.get('link_count', 0)
                })
        
        # Show stats
        st.info(f"📊 Graph: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
        
        if not graph_data.get('nodes'):
            st.error("❌ No nodes found in graph data")
            st.json(results)  # Debug: show raw results
            return
        
        html_file = visualizer.create_interactive_graph(graph_data, graph_file)
        
        # Display graph
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
        
        # Node selection and component display
        st.markdown("---")
        st.markdown("### 🔍 Node Details")
        
        # Get list of nodes for selection
        nodes = graph_data.get('nodes', [])
        if nodes:
            node_options = {f"{node.get('title', 'Untitled')} ({node.get('url', 'N/A')})": node for node in nodes}
            selected_node_label = st.selectbox(
                "Select a node to view its components:",
                [""] + list(node_options.keys()),
                key="node_selector"
            )
            
            if selected_node_label:
                selected_node = node_options[selected_node_label]
                st.session_state.selected_node = selected_node
                
                # Display node components
                display_node_components(selected_node, results)
        else:
            st.info("No nodes available")
    
    except Exception as e:
        st.error(f"Error displaying graph: {e}")
        logger.error(f"Graph display error: {e}", exc_info=True)
        st.json(results)  # Debug output


def display_node_components(node: dict, results: dict):
    """Display components of a selected node"""
    st.markdown(f"#### 📄 {node.get('title', 'Untitled')}")
    st.markdown(f"**URL:** `{node.get('url', 'N/A')}`")
    
    # Create tabs for different component types
    comp_tab1, comp_tab2, comp_tab3, comp_tab4 = st.tabs(["📝 Forms", "🔗 Links", "⌨️ Inputs", "🔘 Buttons"])
    
    # Find the state data for this node
    node_id = node.get('id')
    state_data = None
    
    # Search in both 'states' and 'nodes' (for backward compatibility)
    states = results.get('states', []) or results.get('nodes', [])
    for state in states:
        state_hash = state.get('hash') or state.get('state_hash') or state.get('id')
        if state_hash == node_id:
            state_data = state
            break
    
    if not state_data:
        st.warning("⚠️ No detailed component data available for this node")
        return
    
    with comp_tab1:
        forms = state_data.get('forms', [])
        if forms:
            st.markdown(f"**Found {len(forms)} form(s)**")
            for i, form in enumerate(forms, 1):
                # Get form metadata
                form_action = form.get('action') or 'No action'
                form_method = form.get('method', 'GET').upper()
                form_selector = form.get('selector', 'Unknown')
                detection_method = form.get('detection_method', 'code')
                
                # Create expander title
                expander_title = f"Form {i}: {form_method} → {form_action}"
                if detection_method == 'ai_vision':
                    expander_title += " 🤖 (AI Detected)"
                
                with st.expander(expander_title, expanded=(i == 1)):
                    # Form metadata
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.markdown(f"**Method:** `{form_method}`")
                    with col2:
                        st.markdown(f"**Detection:** `{detection_method}`")
                    with col3:
                        st.markdown(f"**Selector:** `{form_selector}`")
                    
                    if form.get('submit_button'):
                        st.markdown(f"**Submit Button:** `{form['submit_button']}`")
                    
                    st.markdown("---")
                    
                    # Form inputs table
                    inputs = form.get('inputs', [])
                    if inputs:
                        st.markdown(f"**Input Fields ({len(inputs)})**")
                        
                        inputs_data = []
                        for inp in inputs:
                            inputs_data.append({
                                'Type': inp.get('type', 'N/A'),
                                'Name': inp.get('name', 'N/A'),
                                'Label': inp.get('label', 'N/A'),
                                'Placeholder': inp.get('placeholder', 'N/A'),
                                'Required': '✅' if inp.get('required') else '❌',
                                'Disabled': '🚫' if inp.get('disabled') else '✅',
                                'Selector': inp.get('selector', 'N/A')
                            })
                        
                        df_form_inputs = pd.DataFrame(inputs_data)
                        st.dataframe(df_form_inputs, use_container_width=True, height=min(300, len(inputs) * 35 + 38))
                    else:
                        st.info("No input fields detected in this form")
        else:
            st.info("No forms found on this page")
    
    with comp_tab2:
        links = state_data.get('links', [])
        if links:
            st.markdown(f"**Found {len(links)} link(s)**")
            
            # Handle both string URLs and object formats
            links_data = []
            for link in links[:50]:  # Limit to first 50
                if isinstance(link, str):
                    # Simple URL string
                    links_data.append({
                        'URL': link,
                        'Text': 'N/A',
                        'Type': 'N/A'
                    })
                else:
                    # Object with text, url, type
                    links_data.append({
                        'URL': link.get('url', 'N/A'),
                        'Text': link.get('text', 'N/A'),
                        'Type': link.get('type', 'N/A')
                    })
            
            df_links = pd.DataFrame(links_data)
            st.dataframe(df_links, use_container_width=True, height=300)
            if len(links) > 50:
                st.info(f"Showing first 50 of {len(links)} links")
        else:
            st.info("No links found on this page")
    
    with comp_tab3:
        inputs = state_data.get('inputs', [])
        if inputs:
            st.markdown(f"**Found {len(inputs)} input(s)**")
            df_inputs = pd.DataFrame([
                {
                    'Name': inp.get('name', 'N/A'),
                    'Type': inp.get('type', 'N/A'),
                    'ID': inp.get('id', 'N/A'),
                    'Required': inp.get('required', False)
                }
                for inp in inputs
            ])
            st.dataframe(df_inputs, use_container_width=True, height=300)
        else:
            st.info("No input fields found on this page")
    
    with comp_tab4:
        buttons = state_data.get('buttons', [])
        if buttons:
            st.markdown(f"**Found {len(buttons)} button(s)**")
            df_buttons = pd.DataFrame([
                {
                    'Text': btn.get('text', 'N/A'),
                    'Type': btn.get('type', 'N/A'),
                    'ID': btn.get('id', 'N/A')
                }
                for btn in buttons
            ])
            st.dataframe(df_buttons, use_container_width=True, height=300)
        else:
            st.info("No buttons found on this page")


def display_pages_table(results: dict):
    """Display pages table"""
    st.markdown("### 📄 Discovered Pages")
    
    states = results.get('states', [])
    
    if states:
        # Filter out states with empty URLs and build dataframe
        pages_data = []
        for s in states:
            url = s.get('url', '').strip()
            title = s.get('title', '').strip()
            
            # Only include states with valid URL
            if url:
                pages_data.append({
                    'URL': url,
                    'Title': title if title else 'Untitled',
                    'Forms': s.get('form_count', 0),
                    'Inputs': s.get('input_count', 0),
                    'Links': s.get('link_count', 0)
                })
        
        if pages_data:
            df = pd.DataFrame(pages_data)
            st.dataframe(df, use_container_width=True, height=400)
            st.caption(f"📊 Total: {len(pages_data)} unique pages discovered")
        else:
            st.info("No pages found")
    else:
        st.info("No pages found")


def display_elements_table(results: dict):
    """Display forms and input elements tables"""
    st.markdown("### 🔍 Forms & Input Elements")
    
    # Create tabs for forms and inputs
    elem_tab1, elem_tab2 = st.tabs(["📝 All Forms", "⌨️ All Inputs"])
    
    states = results.get('states', [])
    
    with elem_tab1:
        st.markdown("#### 📋 Forms Across All Pages")
        
        # Collect all forms from all states
        all_forms = []
        for state in states:
            page_url = state.get('url', 'Unknown')
            page_title = state.get('title', 'Untitled')
            
            for form in state.get('forms', []):
                method = form.get('method') or 'GET'
                all_forms.append({
                    'Page URL': page_url,
                    'Page Title': page_title,
                    'Method': method.upper() if method else 'GET',
                    'Action': form.get('action', 'No action') or 'No action',
                    'Submit Button': form.get('submit_button', 'N/A') or 'N/A',
                    'Inputs': len(form.get('inputs', [])),
                    'Detection': form.get('detection_method', 'code') or 'code',
                    'Selector': form.get('selector', 'Unknown') or 'Unknown'
                })
        
        if all_forms:
            st.info(f"📊 Total: {len(all_forms)} forms found across {len(states)} pages")
            
            # Add filter by detection method
            detection_filter = st.multiselect(
                "Filter by detection method:",
                options=['code', 'ai_vision', 'semantic', 'container', 'event_driven'],
                default=None,
                key="form_detection_filter"
            )
            
            # Apply filter
            filtered_forms = all_forms
            if detection_filter:
                filtered_forms = [f for f in all_forms if f['Detection'] in detection_filter]
            
            df_forms = pd.DataFrame(filtered_forms)
            st.dataframe(df_forms, use_container_width=True, height=400)
            
            # Show statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                ai_forms = len([f for f in all_forms if f['Detection'] == 'ai_vision'])
                st.metric("🤖 AI Detected", ai_forms)
            with col2:
                code_forms = len([f for f in all_forms if f['Detection'] != 'ai_vision'])
                st.metric("💻 Code Detected", code_forms)
            with col3:
                avg_inputs = sum(f['Inputs'] for f in all_forms) / len(all_forms) if all_forms else 0
                st.metric("📊 Avg Inputs/Form", f"{avg_inputs:.1f}")
        else:
            st.info("No forms found in crawl results")
    
    with elem_tab2:
        st.markdown("#### ⌨️ Input Elements Across All Pages")
        
        elements = []
        for state in states:
            page_url = state.get('url', 'Unknown')
            
            for inp in state.get('inputs', []):
                elements.append({
                    'Page': page_url,
                    'Type': inp.get('type', 'N/A'),
                    'Name': inp.get('name', 'N/A'),
                    'Label': inp.get('label', 'N/A'),
                    'Required': '✅' if inp.get('required') else '❌',
                    'Disabled': '🚫' if inp.get('disabled') else '✅',
                    'Form': inp.get('parent_form', 'N/A')
                })
        
        if elements:
            st.info(f"📊 Total: {len(elements)} input elements found")
            
            # Filter by type
            input_types = list(set(e['Type'] for e in elements))
            type_filter = st.multiselect(
                "Filter by input type:",
                options=sorted(input_types),
                default=None,
                key="input_type_filter"
            )
            
            # Apply filter
            filtered_elements = elements
            if type_filter:
                filtered_elements = [e for e in elements if e['Type'] in type_filter]
            
            df_elements = pd.DataFrame(filtered_elements)
            st.dataframe(df_elements, use_container_width=True, height=400)
        else:
            st.info("No input elements found in crawl results")


def display_test_cases(results: dict):
    """Display test case generation and results"""
    st.markdown("### 🧪 Test Case Generation")
    
    st.info("""
    Generate automated test cases from crawled data using multiple testing strategies:
    - **BVA (Boundary Value Analysis)**: Test input boundaries
    - **ECP (Equivalence Class Partitioning)**: Test representative values
    - **Decision Table**: Test input combinations
    - **State Transition**: Test navigation flows
    - **Use Case**: Test end-to-end scenarios
    
    💡 **New:** Use Constraint Manager if fields lack min/max/length constraints!
    """)
    
    # Check if we have generated tests in session state
    if 'generated_tests' not in st.session_state:
        st.session_state.generated_tests = None
    
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        # Button to generate tests
        if st.button("🚀 Generate Test Cases", type="primary"):
            with st.spinner("Generating test cases..."):
                try:
                    from test_generator.test_orchestrator import TestOrchestrator
                    from test_generator.test_storage import TestStorage
                    import tempfile
                    
                    storage = TestStorage()
                    
                    # Always regenerate — delete any existing tests for this crawl first
                    crawl_hash = storage._get_crawl_hash(results)
                    if crawl_hash in storage.index:
                        old_file = storage.storage_dir / storage.index[crawl_hash]['filename']
                        if old_file.exists():
                            old_file.unlink()
                        del storage.index[crawl_hash]
                        storage._save_index()
                    
                    # Save results to temporary file for test generator
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as tmp:
                        json.dump(results, tmp, indent=2)
                        tmp_path = tmp.name
                    
                    # Generate tests
                    orchestrator = TestOrchestrator()
                    test_results = orchestrator.generate_all_tests(tmp_path)
                    
                    # Clean up temp file
                    os.unlink(tmp_path)
                    
                    # Save to persistent storage
                    storage.save_tests(test_results, results, metadata={'ai_refined': False})
                    
                    # Store in session state
                    st.session_state.generated_tests = test_results
                    st.success("✅ Test cases generated and saved!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error generating tests: {str(e)}")
                    logger.error(f"Test generation error: {e}", exc_info=True)
    
    with col2:
        # AI Refinement button
        if st.session_state.generated_tests:
            if st.button("✨ Refine with AI", type="secondary"):
                with st.spinner("Refining tests with Gemini AI..."):
                    try:
                        from test_generator.ai_refiner import GeminiTestRefiner
                        from test_generator.test_storage import TestStorage
                        
                        refiner = GeminiTestRefiner()
                        storage = TestStorage()
                        
                        # Refine tests
                        test_cases = st.session_state.generated_tests.get('test_cases', {})
                        refined_cases = refiner.refine_tests(test_cases, results)
                        
                        # CRITICAL: Recalculate summary with new test counts
                        # Map test_case keys (bva, ecp) to summary keys (bva_count, ecp_count)
                        total_tests = 0
                        summary = {'by_type': {}}
                        
                        # Count tests by actual dictionary keys
                        bva_count = len(refined_cases.get('bva', []))
                        ecp_count = len(refined_cases.get('ecp', []))
                        dt_count = len(refined_cases.get('decision_table', []))
                        st_count = len(refined_cases.get('state_transition', []))
                        uc_count = len(refined_cases.get('use_case', []))
                        
                        total_tests = bva_count + ecp_count + dt_count + st_count + uc_count
                        
                        summary = {
                            'total_test_cases': total_tests,
                            'bva_count': bva_count,
                            'ecp_count': ecp_count,
                            'decision_table_count': dt_count,
                            'state_transition_count': st_count,
                            'use_case_count': uc_count,
                            'by_type': {
                                'bva': bva_count,
                                'ecp': ecp_count,
                                'decision_table': dt_count,
                                'state_transition': st_count,
                                'use_case': uc_count
                            }
                        }
                        
                        # Update session state with refined tests AND new summary
                        st.session_state.generated_tests['test_cases'] = refined_cases
                        st.session_state.generated_tests['summary'] = summary
                        
                        print(f"\n[UPDATED] Total tests after refinement: {total_tests}")
                        
                        # Save refined version
                        storage.save_tests(st.session_state.generated_tests, results, 
                                         metadata={'ai_refined': True})
                        
                        st.success(f"✨ Tests refined with AI! Total: {total_tests}")
                        st.rerun()
                        
                    except Exception as e:
                        st.error(f"❌ Error refining tests: {str(e)}")
                        logger.error(f"AI refinement error: {e}", exc_info=True)
    
    with col3:
        if st.session_state.generated_tests:
            summary = st.session_state.generated_tests.get('summary', {})
            st.metric("Total Tests", summary.get('total_test_cases', 0))
    
    # Display generated tests if available
    if st.session_state.generated_tests:
        st.markdown("---")
        
        # Summary metrics
        summary = st.session_state.generated_tests.get('summary', {})
        
        st.markdown("### 📊 Test Summary")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("BVA", summary.get('bva_count', 0))
        with col2:
            st.metric("ECP", summary.get('ecp_count', 0))
        with col3:
            st.metric("Decision Table", summary.get('decision_table_count', 0))
        with col4:
            st.metric("State Transition", summary.get('state_transition_count', 0))
        with col5:
            st.metric("Use Case", summary.get('use_case_count', 0))
        
        st.markdown("---")
        
        # Performance warning for large test suites
        total_tests = summary.get('total_test_cases', 0)
        if total_tests > 500:
            st.info(f"💡 **Performance Tip**: {total_tests} tests loaded. Use pagination in each tab for better responsiveness.")
        
        # Test case tabs
        test_cases = st.session_state.generated_tests.get('test_cases', {})
        
        test_tabs = st.tabs(["🔢 BVA", "📦 ECP", "🔀 Decision Table", "🔄 State Transition", "📝 Use Case", "⚙️ Constraints"])
        
        # BVA Tab
        with test_tabs[0]:
            display_bva_tests(test_cases.get('bva', []))
        
        # ECP Tab
        with test_tabs[1]:
            display_ecp_tests(test_cases.get('ecp', []))
        
        # Decision Table Tab
        with test_tabs[2]:
            display_decision_table_tests(test_cases.get('decision_table', []))
        
        # State Transition Tab
        with test_tabs[3]:
            # Create node mapping from results or load from source
            node_map = {}
            
            # Try to get from results (crawl data)
            if 'nodes' in results:
                for node in results.get('nodes', []):
                    node_id = node.get('id', node.get('hash', ''))
                    if node_id:
                        node_map[node_id.lower()] = {
                            'url': node.get('url', 'unknown'),
                            'title': node.get('title', 'Unknown Page')
                        }
            else:
                # Try to load from source file in metadata
                source_file = st.session_state.generated_tests.get('metadata', {}).get('source_file', '')
                if source_file and os.path.exists(source_file):
                    try:
                        with open(source_file, 'r', encoding='utf-8') as f:
                            crawl_data = json.load(f)
                            for node in crawl_data.get('nodes', []):
                                node_id = node.get('id', node.get('hash', ''))
                                if node_id:
                                    node_map[node_id.lower()] = {
                                        'url': node.get('url', 'unknown'),
                                        'title': node.get('title', 'Unknown Page')
                                    }
                    except Exception as e:
                        logger.warning(f"Could not load node map from source file: {e}")
            
            display_state_transition_tests(test_cases.get('state_transition', []), node_map)
        
        # Use Case Tab
        with test_tabs[4]:
            display_use_case_tests(test_cases.get('use_case', []))
        
        # Constraint Manager Tab
        with test_tabs[5]:
            from app.components.constraint_editor_v2 import display_constraint_editor
            
            # Extract form data from results
            form_data = {'forms': []}
            for node in results.get('nodes', []):
                for form in node.get('forms', []):
                    form['url'] = node.get('url', 'unknown')
                    form['page_title'] = node.get('title', 'Unknown Page')
                    form_data['forms'].append(form)
            
            display_constraint_editor(form_data, results)
        
        # Export generated tests
        st.markdown("---")
        st.markdown("### 💾 Export Test Cases")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Export Tests (JSON)"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                # Export to dedicated test directory, not crawled_graphs
                test_dir = Path("data/exported_tests")
                test_dir.mkdir(parents=True, exist_ok=True)
                filepath = test_dir / f"tests_{timestamp}.json"
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(st.session_state.generated_tests, f, indent=2)
                st.success(f"✅ Exported: {filepath}")
        
        with col2:
            if st.button("📊 Export Tests (CSV)"):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                all_tests = []
                for test_type, tests in test_cases.items():
                    for test in tests:
                        all_tests.append({
                            'type': test_type,
                            'id': test.get('id', ''),
                            'description': test.get('description', ''),
                            'expected_result': test.get('expected_result', '')
                        })
                
                if all_tests:
                    df = pd.DataFrame(all_tests)
                    # Export to dedicated test directory, not crawled_graphs
                    test_dir = Path("data/exported_tests")
                    test_dir.mkdir(parents=True, exist_ok=True)
                    filepath = test_dir / f"tests_{timestamp}.csv"
                    df.to_csv(filepath, index=False)
                    st.success(f"✅ Exported: {filepath}")


def display_bva_tests(tests: List[dict]):
    """Display BVA test cases with pagination for performance"""
    if not tests:
        st.info("No BVA test cases generated")
        return
    
    st.markdown(f"### 📊 Boundary Value Analysis: {len(tests)} Tests")
    
    # Performance optimization: Show summary + pagination for large test sets
    if len(tests) > 50:
        st.warning(f"⚡ Large test set ({len(tests)} tests). Using pagination for better performance.")
        
        # Pagination controls
        tests_per_page = 50
        total_pages = (len(tests) + tests_per_page - 1) // tests_per_page
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                "Page", 
                min_value=1, 
                max_value=total_pages, 
                value=1,
                key="bva_page"
            )
        
        start_idx = (page - 1) * tests_per_page
        end_idx = min(start_idx + tests_per_page, len(tests))
        
        st.caption(f"Showing tests {start_idx + 1}-{end_idx} of {len(tests)}")
        tests = tests[start_idx:end_idx]
    
    # Group by form URL for better organization
    forms = {}
    for test in tests:
        form_url = test.get('form_url', 'Unknown Form')
        if form_url not in forms:
            forms[form_url] = []
        forms[form_url].append(test)
    
    for form_url, form_tests in forms.items():
        # Extract page title from first test
        page_title = form_tests[0].get('page_title', 'Unknown Page')
        
        with st.expander(f"📄 {page_title} - {form_url.split('/')[-1] or 'home'} ({len(form_tests)} tests)", expanded=len(forms)==1):
            # Group by field for cleaner display
            fields = {}
            for test in form_tests:
                # Get field identifier - use ID from test_id if available
                test_id = test.get('id', '')
                field_id = test_id.split('_')[3] if len(test_id.split('_')) > 3 else 'unknown'
                
                if field_id not in fields:
                    fields[field_id] = []
                fields[field_id].append(test)
            
            for field_id, field_tests in fields.items():
                field_label = field_tests[0].get('field_label', '')
                field_name = field_tests[0].get('field_name', '')
                field_type = field_tests[0].get('field_type', 'unknown')
                
                # Create readable field display name
                if field_label and field_label.strip():
                    field_display = f"{field_label} ({field_id})"
                elif field_name and field_name.strip():
                    field_display = f"{field_name} ({field_id})"
                else:
                    field_display = field_id
                
                st.markdown(f"#### 📝 Field: {field_display}")
                st.caption(f"Type: `{field_type}` | {len(field_tests)} boundary tests")
                
                # Display tests in a compact table
                for idx, test in enumerate(field_tests, 1):
                    subtype = test.get('subtype', 'numeric').upper()
                    test_value = test.get('test_value', 'N/A')
                    expected = test.get('expected_result', 'N/A')
                    description = test.get('description', 'N/A')
                    
                    # Color code the expected result
                    if expected == 'success':
                        result_emoji = "✅"
                    elif expected == 'error':
                        result_emoji = "❌"
                    else:
                        result_emoji = "⚠️"
                    
                    col1, col2, col3 = st.columns([1, 2, 3])
                    with col1:
                        st.markdown(f"{result_emoji} **Test {idx}**")
                    with col2:
                        st.code(str(test_value), language=None)
                    with col3:
                        # Extract just the boundary description part
                        if ':' in description:
                            desc_parts = description.split(':')
                            st.caption(desc_parts[-1].strip())
                        else:
                            st.caption(description)
                
                # Show constraints if available
                if 'constraints' in field_tests[0]:
                    constraints = field_tests[0]['constraints']
                    # Handle both numeric (min/max/step) and length (minlength/maxlength) constraints
                    if 'minlength' in constraints or 'maxlength' in constraints:
                        st.caption(f"⚙️ **Constraints:** minlength={constraints.get('minlength')}, maxlength={constraints.get('maxlength')}")
                    else:
                        st.caption(f"⚙️ **Constraints:** min={constraints.get('min')}, max={constraints.get('max')}, step={constraints.get('step')}")
                
                st.markdown("---")


def display_ecp_tests(tests: List[dict]):
    """Display ECP test cases with pagination for performance"""
    if not tests:
        st.info("No ECP test cases generated")
        return
    
    st.markdown(f"### 📦 Equivalence Class Partitioning: {len(tests)} Tests")
    
    # Performance optimization: Pagination for large test sets
    if len(tests) > 50:
        st.warning(f"⚡ Large test set ({len(tests)} tests). Using pagination for better performance.")
        
        tests_per_page = 50
        total_pages = (len(tests) + tests_per_page - 1) // tests_per_page
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                "Page", 
                min_value=1, 
                max_value=total_pages, 
                value=1,
                key="ecp_page"
            )
        
        start_idx = (page - 1) * tests_per_page
        end_idx = min(start_idx + tests_per_page, len(tests))
        
        st.caption(f"Showing tests {start_idx + 1}-{end_idx} of {len(tests)}")
        tests = tests[start_idx:end_idx]
    
    # Group by form URL
    forms = {}
    for test in tests:
        form_url = test.get('form_url', 'Unknown Form')
        if form_url not in forms:
            forms[form_url] = []
        forms[form_url].append(test)
    
    for form_url, form_tests in forms.items():
        page_title = form_tests[0].get('page_title', 'Unknown Page')
        page_name = form_url.split('/')[-1] or 'home'
        
        with st.expander(f"📄 {page_title} - {page_name} ({len(form_tests)} tests)", expanded=len(forms)==1):
            # Group by field
            fields = {}
            for test in form_tests:
                test_id = test.get('id', '')
                field_id = test_id.split('_')[3] if len(test_id.split('_')) > 3 else 'unknown'
                
                if field_id not in fields:
                    fields[field_id] = []
                fields[field_id].append(test)
            
            for field_id, field_tests in fields.items():
                field_label = field_tests[0].get('field_label', '')
                field_name = field_tests[0].get('field_name', '')
                field_type = field_tests[0].get('field_type', 'unknown')
                
                # Create readable field display
                if field_label and field_label.strip():
                    field_display = f"{field_label} ({field_id})"
                elif field_name and field_name.strip():
                    field_display = f"{field_name} ({field_id})"
                else:
                    field_display = field_id
                
                st.markdown(f"#### 📝 Field: {field_display}")
                st.caption(f"Type: `{field_type}` | {len(field_tests)} equivalence class tests")
                
                # Display tests in organized manner
                for test in field_tests:
                    eq_class = test.get('equivalence_class', 'unknown')
                    test_value = test.get('test_value', 'N/A')
                    expected = test.get('expected_result', 'N/A')
                    description = test.get('description', 'N/A')
                    
                    # Format the value for display
                    if isinstance(test_value, str) and len(test_value) > 50:
                        display_value = test_value[:50] + "..."
                    else:
                        display_value = test_value
                    
                    # Color code
                    if expected == 'success':
                        result_emoji = "✅"
                        result_color = "green"
                    elif expected == 'error':
                        result_emoji = "❌"
                        result_color = "red"
                    else:
                        result_emoji = "⚠️"
                        result_color = "orange"
                    
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.markdown(f"{result_emoji} **{eq_class.replace('_', ' ').title()}**")
                    with col2:
                        if isinstance(test_value, str):
                            st.code(display_value, language=None)
                        else:
                            st.write(f"`{display_value}`")
                        st.caption(description)
                
                st.markdown("---")


def display_decision_table_tests(tests: List[dict]):
    """Display Decision Table test cases with pagination"""
    if not tests:
        st.info("No Decision Table test cases generated")
        return
    
    st.markdown(f"**Total Decision Table Tests:** {len(tests)}")
    
    # Pagination for large sets
    if len(tests) > 20:
        st.warning(f"⚡ Showing paginated view ({len(tests)} tests)")
        
        tests_per_page = 20
        total_pages = (len(tests) + tests_per_page - 1) // tests_per_page
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            page = st.number_input(
                "Page", 
                min_value=1, 
                max_value=total_pages, 
                value=1,
                key="dt_page"
            )
        
        start_idx = (page - 1) * tests_per_page
        end_idx = min(start_idx + tests_per_page, len(tests))
        
        st.caption(f"Showing tests {start_idx + 1}-{end_idx} of {len(tests)}")
        tests = tests[start_idx:end_idx]
    
    for test in tests:
        with st.expander(f"🔀 {test.get('description', 'Test')}"):
            page_title = test.get('page_title', 'Unknown Page')
            form_url = test.get('form_url', 'N/A')
            form_action = test.get('form_action', 'N/A')
            
            st.markdown(f"**📄 Page:** {page_title}")
            st.markdown(f"**🔗 URL:** `{form_url}`")
            st.markdown(f"**⚡ Form Action:** `{form_action}`")
            st.markdown(f"**🆔 Form ID:** `{test.get('form_id', 'N/A')}`")
            
            # Display test data with field labels
            test_data = test.get('test_data', {})
            if test_data:
                st.markdown("**📝 Input Values:**")
                for field, value in test_data.items():
                    # Get field label if available
                    field_labels = test.get('field_labels', {})
                    field_label = field_labels.get(field, field)
                    
                    # Format boolean values
                    if isinstance(value, bool):
                        value_display = "✓ Yes" if value else "✗ No"
                    else:
                        value_display = str(value)
                    
                    st.markdown(f"  - **{field_label}:** `{value_display}`")
            
            st.markdown(f"**✅ Expected Result:** `{test.get('expected_result', 'N/A')}`")


def display_decision_table_tests_old(tests: List[dict]):
    """Display Decision Table test cases"""
    if not tests:
        st.info("No Decision Table test cases generated")
        return
    
    st.markdown(f"**Total Decision Table Tests:** {len(tests)}")
    
    for test in tests:
        with st.expander(f"🔀 {test.get('description', 'Test')}"):
            page_title = test.get('page_title', 'Unknown Page')
            form_url = test.get('form_url', 'N/A')
            form_action = test.get('form_action', 'N/A')
            
            st.markdown(f"**📄 Page:** {page_title}")
            st.markdown(f"**🔗 URL:** `{form_url}`")
            st.markdown(f"**⚡ Form Action:** `{form_action}`")
            st.markdown(f"**🆔 Form ID:** `{test.get('form_id', 'N/A')}`")
            
            # Display test data with field labels
            test_data = test.get('test_data', {})
            if test_data:
                st.markdown("**📝 Input Values:**")
                for field, value in test_data.items():
                    # Try to get field label from field_labels dict if available
                    field_labels = test.get('field_labels', {})
                    field_label = field_labels.get(field, field)
                    st.markdown(f"- **{field_label}** (`{field}`): `{value}`")
            
            st.markdown(f"**✅ Expected:** `{test.get('expected_result', 'N/A')}`")


def display_state_transition_tests(tests: List[dict], node_map: dict = None):
    """Display State Transition test cases with resolved node names"""
    if not tests:
        st.info("No State Transition test cases generated")
        return
    
    if node_map is None:
        node_map = {}
    
    def resolve_node(node_id: str) -> str:
        """Resolve node ID to readable format using URL path parsing"""
        if not node_id:
            return "Unknown"
        
        # Check if it's a node ID that needs resolution
        node_info = node_map.get(node_id.lower(), {})
        if node_info:
            url = node_info.get('url', '')
            title = node_info.get('title', '')
        else:
            # Might already be a URL
            url = node_id if '://' in node_id else ''
            title = ''
        
        # Parse URL to get readable name
        if url and url != 'unknown':
            # Extract path from URL
            if '://' in url:
                path = url.split('://', 1)[1]
            else:
                path = url
            
            # Remove domain
            if '/' in path:
                path = '/' + '/'.join(path.split('/')[1:])
            
            # Clean up path
            path = path.strip('/')
            if not path:
                # Root page - use title if not generic
                if title and title.upper() != title:
                    return title
                return 'Home'
            
            # Make readable from URL path
            name = path.split('/')[-1] if path.split('/')[-1] else path
            name = name.replace('-', ' ').replace('_', ' ').title()
            
            return name
        
        # Fallback to title or node ID
        if title and title != 'Unknown Page':
            return title
        return node_id[:8]
    
    st.markdown(f"**Total State Transition Tests:** {len(tests)}")
    
    # Group by subtype
    subtypes = {}
    for test in tests:
        subtype = test.get('subtype', 'other')
        if subtype not in subtypes:
            subtypes[subtype] = []
        subtypes[subtype].append(test)
    
    for subtype, subtype_tests in subtypes.items():
        with st.expander(f"🔄 {subtype.replace('_', ' ').title()} ({len(subtype_tests)} tests)"):
            for test in subtype_tests:
                st.markdown(f"**Test ID:** `{test.get('id', 'N/A')}`")
                
                # Resolve path nodes to readable names
                path = test.get('path', [])
                if path:
                    resolved_path = " → ".join([resolve_node(node) for node in path])
                    st.markdown(f"**Flow Path:** {resolved_path}")
                
                st.markdown(f"**Description:** {test.get('description', 'N/A')}")
                
                # Display steps with resolved names
                steps = test.get('steps', [])
                if steps:
                    st.markdown("**Steps:**")
                    for step in steps:
                        step_desc = step.get('description', 'N/A')
                        # Try to resolve node IDs in the description
                        from_node = step.get('from', '')
                        to_node = step.get('to', '')
                        if from_node and to_node:
                            step_desc = f"Navigate from **{resolve_node(from_node)}** to **{resolve_node(to_node)}**"
                        st.markdown(f"{step.get('step', 'N/A')}. {step_desc}")
                
                st.divider()


def display_use_case_tests(tests: List[dict]):
    """Display Use Case test cases"""
    if not tests:
        st.info("No Use Case test cases generated")
        return
    
    st.markdown(f"**Total Use Case Tests:** {len(tests)}")
    
    # Group by subtype
    subtypes = {}
    for test in tests:
        subtype = test.get('subtype', 'other')
        if subtype not in subtypes:
            subtypes[subtype] = []
        subtypes[subtype].append(test)
    
    for subtype, subtype_tests in subtypes.items():
        with st.expander(f"📝 {subtype.replace('_', ' ').title()} ({len(subtype_tests)} tests)"):
            for test in subtype_tests:
                st.markdown(f"### {test.get('scenario_name', 'Scenario')}")
                st.markdown(f"**Test ID:** `{test.get('id', 'N/A')}`")
                st.markdown(f"**Description:** {test.get('description', 'N/A')}")
                
                # Display preconditions
                preconditions = test.get('preconditions', [])
                if preconditions:
                    st.markdown("**Preconditions:**")
                    for pre in preconditions:
                        st.markdown(f"- {pre}")
                
                # Display steps
                steps = test.get('steps', [])
                if steps:
                    st.markdown("**Steps:**")
                    for step in steps:
                        st.markdown(f"""
                        **Step {step.get('step', 'N/A')}:** {step.get('action', 'N/A')}  
                        - Description: {step.get('description', 'N/A')}  
                        - Verification: {step.get('verification', 'N/A')}
                        """)
                
                # Display postconditions
                postconditions = test.get('postconditions', [])
                if postconditions:
                    st.markdown("**Postconditions:**")
                    for post in postconditions:
                        st.markdown(f"- {post}")
                
                st.markdown(f"**Expected Result:** `{test.get('expected_result', 'N/A')}`")
                st.divider()


def display_export_options(results: dict):
    """Display export options"""
    st.markdown("### 💾 Export Results")
    
    exporter = Exporter()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Include the crawled URL in the manual export filename too
    _start_url = results.get('crawl_stats', {}).get('start_url', '') or ''
    if _start_url:
        import re as _re
        from urllib.parse import urlparse as _up
        _p = _up(_start_url)
        _host = _p.netloc.replace(':', '_').replace('.', '_')
        _path = _re.sub(r'[^a-zA-Z0-9_\-]', '_', _p.path.strip('/'))
        _slug = f"{_host}_{_path}_{timestamp}" if _path else f"{_host}_{timestamp}"
    else:
        _slug = f"crawl_{timestamp}"
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📄 Export JSON"):
            filepath = exporter.export_json(results, f"{_slug}.json")
            st.success(f"✅ Exported: {filepath}")
    
    with col2:
        if st.button("📊 Export CSV"):
            filepath = exporter.export_csv(results.get('states', []), f"{_slug}.csv")
            st.success(f"✅ Exported: {filepath}")
    
    col3, col4 = st.columns(2)
    
    with col3:
        if st.button("📝 Export Elements CSV"):
            filepath = exporter.export_elements_csv(results.get('states', []), f"{_slug}_elements.csv")
            st.success(f"✅ Exported: {filepath}")
    
    with col4:
        if st.button("📋 Export Forms CSV"):
            # Export all forms to CSV
            states = results.get('states', [])
            forms_data = []
            
            for state in states:
                page_url = state.get('url', 'Unknown')
                page_title = state.get('title', 'Untitled')
                
                for form in state.get('forms', []):
                    forms_data.append({
                        'page_url': page_url,
                        'page_title': page_title,
                        'form_action': form.get('action', 'No action'),
                        'form_method': form.get('method', 'GET'),
                        'submit_button': form.get('submit_button', 'N/A'),
                        'input_count': len(form.get('inputs', [])),
                        'detection_method': form.get('detection_method', 'code'),
                        'selector': form.get('selector', 'Unknown')
                    })
            
            if forms_data:
                import pandas as pd
                df = pd.DataFrame(forms_data)
                # Export to dedicated exports directory, not crawled_graphs
                export_dir = Path("data/exported_data")
                export_dir.mkdir(parents=True, exist_ok=True)
                filepath = export_dir / f"forms_{timestamp}.csv"
                df.to_csv(filepath, index=False)
                st.success(f"✅ Exported: {filepath}")
            else:
                st.warning("⚠️ No forms to export")
        if st.button("📋 Export Report"):
            filepath = exporter.export_markdown_report(results, f"report_{timestamp}.md")
            st.success(f"✅ Exported: {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# EXECUTE TESTS TAB
# ─────────────────────────────────────────────────────────────────────────────

def display_execute_tests(results: dict):
    """Execute Tests tab — runs generated test cases against the live application."""
    st.markdown("### 🚀 Execute Tests")

    # Check that test cases are loaded
    generated_tests = st.session_state.get("generated_tests")
    if not generated_tests:
        st.info(
            "ℹ️ No test suite loaded.  "
            "Go to the **🧪 Test Cases** tab and generate or load tests first."
        )
        return

    test_cases = generated_tests.get("test_cases", {})
    total_tc = sum(len(v) for v in test_cases.values() if isinstance(v, list))
    st.success(f"✅ Test suite loaded — **{total_tc} test cases** ready to execute")

    st.markdown("---")

    # ── Test Type Selection ────────────────────────────────────────────────
    st.subheader("🎯 Select Test Types to Execute")
    
    # Count tests by type
    type_counts = {}
    for test_type, cases in test_cases.items():
        if isinstance(cases, list):
            type_counts[test_type] = len(cases)
    
    if type_counts:
        # Display test type counts in columns
        type_cols = st.columns(len(type_counts))
        for idx, (test_type, count) in enumerate(sorted(type_counts.items())):
            with type_cols[idx]:
                st.metric(test_type, count)
        
        st.markdown("---")
        
        # Multi-select for test types
        selected_types = st.multiselect(
            "Choose test types to execute:",
            options=sorted(type_counts.keys()),
            default=sorted(type_counts.keys()),
            help="Select one or more test types. Only selected types will be executed."
        )
        
        if not selected_types:
            st.warning("⚠️ Please select at least one test type to execute")
            return
        
        # Filter test cases by selected types
        filtered_tests = {}
        for test_type in selected_types:
            if test_type in test_cases:
                filtered_tests[test_type] = test_cases[test_type]
        
        filtered_count = sum(len(v) for v in filtered_tests.values() if isinstance(v, list))
        st.info(f"📌 **{filtered_count} test cases** selected from **{len(selected_types)} type(s)** for execution")
        
        # Create filtered test suite
        filtered_test_suite = generated_tests.copy()
        filtered_test_suite["test_cases"] = filtered_tests
    else:
        filtered_test_suite = generated_tests
        filtered_count = total_tc

    st.markdown("---")

    # ── Configuration ──────────────────────────────────────────────────────
    st.subheader("⚙️ Execution Configuration")
    col1, col2, col3 = st.columns(3)

    with col1:
        rl_mode = st.toggle(
            "🤖 Adaptive RL Mode",
            value=True,
            help="Uses the DQN agent to decide when to call the LLM oracle vs trust free heuristics."
        )

    with col2:
        api_budget = st.slider(
            "💸 API Budget (LLM calls)",
            min_value=5, max_value=100, value=30, step=5,
            help="Max number of Gemini Vision calls. Each call costs ~$0.002."
        )
        st.caption(f"Estimated max cost: **${api_budget * 0.002:.2f}**")

    with col3:
        time_limit = st.slider(
            "⏱️ Time Limit (minutes)",
            min_value=2, max_value=60, value=10, step=2
        )
        headless = st.checkbox("Headless browser", value=True)

    st.markdown("---")

    # ── Run button ─────────────────────────────────────────────────────────
    run_col, status_col = st.columns([1, 3])
    with run_col:
        run_clicked = st.button("▶️ Run Tests", type="primary")

    if "exec_report" in st.session_state:
        with status_col:
            rep = st.session_state["exec_report"]
            st.success(
                f"Last run: {rep['passed']}/{rep['total']} passed  "
                f"| {rep['api_calls_used']} LLM calls (${rep['api_cost_usd']:.3f})  "
                f"| {rep['duration_s']}s  "
                f"| stop: {rep['stop_reason']}"
            )

    if run_clicked:
        # Safety: require test suite
        if filtered_count == 0:
            st.error("No test cases to run.")
            return

        crawl_id = st.session_state.get("selected_crawl", "unknown")

        progress_bar  = st.progress(0)
        status_text   = st.empty()
        metric_cols   = st.columns(4)
        passed_metric = metric_cols[0].empty()
        failed_metric = metric_cols[1].empty()
        api_metric    = metric_cols[2].empty()
        cost_metric   = metric_cols[3].empty()

        # Shared counters (updated via callback)
        counters = {"done": 0, "passed": 0, "failed": 0, "api": 0, "cost": 0.0}

        def sync_progress(current, total, result):
            counters["done"] = current
            if hasattr(result, 'status'):
                if result.status.value == "passed":
                    counters["passed"] += 1
                elif result.status.value == "failed":
                    counters["failed"] += 1
            progress_bar.progress(current / max(total, 1))
            status_text.markdown(
                f"Running test **{current}/{total}**: `{result.test_id}` "
                f"→ {result.status.value if hasattr(result.status,'value') else result.status}"
            )
            passed_metric.metric("✅ Passed", counters["passed"])
            failed_metric.metric("❌ Failed", counters["failed"])

        # Async progress wrapper (Streamlit runs sync; we patch callback)
        import queue as _queue
        _q: _queue.Queue = _queue.Queue()

        async def _async_progress(current, total, result):
            sync_progress(current, total, result)

        # ── Execute ────────────────────────────────────────────────────
        with st.spinner(f"Executing {filtered_count} tests …"):
            try:
                sys.path.insert(0, str(Path(".").resolve()))
                from execution.adaptive_runner import AdaptiveRunner

                runner = AdaptiveRunner(
                    api_budget   = api_budget,
                    time_limit_s = time_limit * 60,
                    rl_mode      = rl_mode,
                    headless     = headless,
                    progress_cb  = _async_progress,
                )

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                report = loop.run_until_complete(
                    runner.execute(filtered_test_suite, crawl_id=crawl_id)
                )
                loop.close()

                report_dict = report.to_dict()
                st.session_state["exec_report"] = report_dict

            except Exception as e:
                st.error(f"Execution failed: {e}")
                logger.error(f"Execute tab error: {e}", exc_info=True)
                return

        # ── Results summary ────────────────────────────────────────────
        progress_bar.progress(1.0)
        status_text.success("Execution complete!")

        r = report_dict
        st.markdown("#### 📊 Results")
        c1, c2, c3, c4, c5, c6, c7 = st.columns(7)
        c1.metric("Total",    r["total"])
        c2.metric("✅ Passed", r["passed"])
        c3.metric("❌ Failed", r["failed"])
        c4.metric("⚠️ Errors", r["errors"])
        c5.metric("🤖 LLM calls", r["api_calls_used"])
        c6.metric("💸 Cost",   f"${r['api_cost_usd']:.3f}")
        c7.metric("⏱ Duration", f"{r['duration_s']}s")

        st.caption(
            f"Stop reason: **{r['stop_reason']}**  |  "
            f"RL decisions — heuristic: {r['heuristic_decisions']}, "
            f"LLM: {r['llm_decisions']}, stop: {r['stop_decisions']}"
        )

    # ── Show previous report if available ─────────────────────────────────
    if "exec_report" in st.session_state and not run_clicked:
        st.markdown("#### 📋 Previous Run Results")

    # ── Load & display latest HTML report ─────────────────────────────────
    results_dir = Path("data/test_results")
    html_reports = sorted(results_dir.glob("report_*.html"), reverse=True) if results_dir.exists() else []

    if html_reports:
        latest_report = html_reports[0]
        st.markdown(f"**Latest report:** `{latest_report.name}`")
        with open(latest_report, "r", encoding="utf-8") as f:
            html_content = f.read()
        st.components.v1.html(html_content, height=900, scrolling=True)
        st.download_button(
            label="⬇️ Download HTML Report",
            data=html_content,
            file_name=latest_report.name,
            mime="text/html",
        )
    elif "exec_report" not in st.session_state:
        st.info("No reports yet — run tests above to generate one.")


if __name__ == "__main__":
    main()
