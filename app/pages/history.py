"""Historical crawl results viewer"""
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import pandas as pd
import os

# Import from app components
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.components.graph_viz import GraphVisualizer
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)

def load_crawl_results():
    """Load all available crawl result files"""
    crawl_dir = Path("data/crawled_graphs")
    if not crawl_dir.exists():
        return []
    
    results = []
    for json_file in crawl_dir.glob("crawl_*.json"):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Extract metadata
                metadata = data.get('metadata', {})
                timestamp = metadata.get('timestamp', '')
                
                # If no timestamp in metadata, use file modification time
                if not timestamp:
                    timestamp = datetime.fromtimestamp(json_file.stat().st_mtime).isoformat()
                
                # Parse timestamp for display
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    display_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    display_time = timestamp
                
                results.append({
                    'file': json_file.name,
                    'path': str(json_file),
                    'timestamp': timestamp,
                    'display_time': display_time,
                    'nodes': len(data.get('nodes', [])),
                    'edges': len(data.get('edges', [])),
                    'start_url': metadata.get('start_url', 'Unknown'),
                    'max_depth': metadata.get('max_depth', 'N/A'),
                    'max_pages': metadata.get('max_pages', 'N/A')
                })
        except Exception as e:
            logger.warning(f"Could not load {json_file.name}: {e}")
    
    return sorted(results, key=lambda x: x['timestamp'], reverse=True)

def render_graph(graph_data, crawl_name):
    """Render the crawl graph visualization using GraphVisualizer"""
    try:
        visualizer = GraphVisualizer()
        
        # Create unique filename for this crawl
        graph_file = f"data/temp_history_{crawl_name}.html"
        
        st.info(f"📊 Graph: {len(graph_data.get('nodes', []))} nodes, {len(graph_data.get('edges', []))} edges")
        
        html_file = visualizer.create_interactive_graph(graph_data, graph_file)
        
        # Display graph
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.components.v1.html(html_content, height=800, scrolling=True)
    
    except Exception as e:
        st.error(f"Error displaying graph: {e}")
        logger.error(f"Graph display error: {e}", exc_info=True)

def main():
    st.set_page_config(page_title="Crawl History", page_icon="📜", layout="wide")
    
    st.title("📜 Crawl History")
    st.markdown("View and analyze previous crawl results from stored JSON files")
    
    # Load available crawls
    crawls = load_crawl_results()
    
    if not crawls:
        st.warning("⚠️ No crawl history found. Run a crawl first!")
        st.info("💡 Crawl results are automatically saved to `data/crawled_graphs/` after each crawl.")
        return
    
    st.success(f"✅ Found {len(crawls)} saved crawl(s)")
    
    # Create selection interface in sidebar
    st.sidebar.header("📂 Select Crawl")
    
    # Show list of crawls with details
    selected_idx = st.sidebar.selectbox(
        "Choose a crawl to view:",
        range(len(crawls)),
        format_func=lambda i: f"{crawls[i]['display_time']} ({crawls[i]['nodes']} pages)"
    )
    
    selected_crawl = crawls[selected_idx]
    
    # Show comparison if multiple crawls
    if len(crawls) > 1:
        with st.sidebar.expander("📊 Compare All Crawls"):
            comparison_df = pd.DataFrame([{
                'Date': c['display_time'].split()[0],
                'Time': c['display_time'].split()[1] if len(c['display_time'].split()) > 1 else '',
                'Pages': c['nodes'],
                'Edges': c['edges']
            } for c in crawls])
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    
    # Display metadata
    st.markdown(f"### 📁 {selected_crawl['file']}")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("📄 Pages", selected_crawl['nodes'])
    col2.metric("🔗 Edges", selected_crawl['edges'])
    col3.metric("📊 Max Depth", selected_crawl.get('max_depth', 'N/A'))
    col4.metric("🎯 Max Pages", selected_crawl.get('max_pages', 'N/A'))
    col5.metric("🕒 Crawled", selected_crawl['display_time'].split()[0])
    
    # Show start URL
    st.info(f"🌐 Start URL: **{selected_crawl['start_url']}**")
    
    # Load full data
    with open(selected_crawl['path'], 'r', encoding='utf-8') as f:
        graph_data = json.load(f)
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📊 Graph Visualization", "📋 Pages List", "🔍 Details"])
    
    with tab1:
        st.subheader("🕸️ Graph Visualization")
        render_graph(graph_data, selected_crawl['file'].replace('.json', ''))
    
    with tab2:
        st.subheader("📄 Discovered Pages")
        pages_data = []
        for node in graph_data.get('nodes', []):
            # Handle both integer and list types for counts
            form_count = node.get('form_count', 0)
            if isinstance(form_count, list):
                form_count = len(form_count)
            elif isinstance(node.get('forms'), list):
                form_count = len(node.get('forms', []))
            
            input_count = node.get('input_count', 0)
            if isinstance(input_count, list):
                input_count = len(input_count)
            elif isinstance(node.get('inputs'), list):
                input_count = len(node.get('inputs', []))
            
            button_count = node.get('button_count', 0)
            if isinstance(button_count, list):
                button_count = len(button_count)
            elif isinstance(node.get('buttons'), list):
                button_count = len(node.get('buttons', []))
            
            pages_data.append({
                'URL': node.get('url', ''),
                'Title': node.get('title', 'Untitled'),
                'Forms': form_count,
                'Inputs': input_count,
                'Buttons': button_count,
                'Links': node.get('link_count', 0),
                'Depth': node.get('depth', 0)
            })
        
        pages_df = pd.DataFrame(pages_data)
        
        # Add filters
        col1, col2 = st.columns(2)
        with col1:
            filter_forms = st.checkbox("Only pages with forms", value=False)
        with col2:
            filter_inputs = st.checkbox("Only pages with inputs", value=False)
        
        # Apply filters
        if filter_forms:
            pages_df = pages_df[pages_df['Forms'] > 0]
        if filter_inputs:
            pages_df = pages_df[pages_df['Inputs'] > 0]
        
        st.dataframe(pages_df, use_container_width=True, hide_index=True, height=400)
        
        # Download button
        csv = pages_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Pages as CSV",
            data=csv,
            file_name=f"pages_{selected_crawl['file'].replace('.json', '.csv')}",
            mime="text/csv"
        )
    
    with tab3:
        st.subheader("📋 Crawl Details & Statistics")
        metadata = graph_data.get('metadata', {})
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🔧 Configuration")
            st.json({
                "Start URL": metadata.get('start_url', 'Unknown'),
                "Timestamp": metadata.get('timestamp', 'Unknown'),
                "Max Depth": metadata.get('max_depth', 'N/A'),
                "Max Pages": metadata.get('max_pages', 'N/A'),
                "Headless": metadata.get('headless', 'N/A'),
                "AI Enabled": metadata.get('ai_enabled', 'N/A')
            })
        
        with col2:
            st.markdown("##### 📊 Statistics")
            
            # Calculate stats safely
            total_forms = 0
            total_inputs = 0
            total_buttons = 0
            
            for node in nodes:
                # Handle forms
                form_count = node.get('form_count', 0)
                if isinstance(form_count, list):
                    form_count = len(form_count)
                elif isinstance(node.get('forms'), list):
                    form_count = len(node.get('forms', []))
                total_forms += form_count
                
                # Handle inputs
                input_count = node.get('input_count', 0)
                if isinstance(input_count, list):
                    input_count = len(input_count)
                elif isinstance(node.get('inputs'), list):
                    input_count = len(node.get('inputs', []))
                total_inputs += input_count
                
                # Handle buttons
                button_count = node.get('button_count', 0)
                if isinstance(button_count, list):
                    button_count = len(button_count)
                elif isinstance(node.get('buttons'), list):
                    button_count = len(node.get('buttons', []))
                total_buttons += button_count
            
            node_count = len(nodes)
            
            st.json({
                "Total Nodes": node_count,
                "Total Edges": len(edges),
                "Total Forms": total_forms,
                "Total Inputs": total_inputs,
                "Total Buttons": total_buttons,
                "Avg Forms/Page": round(total_forms / max(node_count, 1), 2),
                "Avg Inputs/Page": round(total_inputs / max(node_count, 1), 2)
            })
        
        # Edge details
        st.markdown("##### 🔗 Edge Information")
        if edges:
            st.info(f"Found {len(edges)} connections between pages")
            
            # Sample edges
            with st.expander("🔍 View Sample Edges (first 10)"):
                edge_samples = []
                for i, edge in enumerate(edges[:10]):
                    source = edge.get('source') or edge.get('from') or edge.get('from_hash')
                    target = edge.get('target') or edge.get('to') or edge.get('to_hash')
                    action = edge.get('action', 'unknown')
                    label = edge.get('label', 'No label')
                    
                    edge_samples.append({
                        '#': i + 1,
                        'Action': action,
                        'Label': label,
                        'From': source[:20] + '...' if len(str(source)) > 20 else source,
                        'To': target[:20] + '...' if len(str(target)) > 20 else target
                    })
                
                st.dataframe(pd.DataFrame(edge_samples), use_container_width=True, hide_index=True)
        else:
            st.warning("⚠️ No edges found in this crawl")
        
        # Download raw JSON
        st.markdown("---")
        st.markdown("##### 💾 Download Raw Data")
        json_str = json.dumps(graph_data, indent=2)
        st.download_button(
            label="📥 Download Full JSON",
            data=json_str,
            file_name=selected_crawl['file'],
            mime="application/json"
        )

if __name__ == "__main__":
    main()
