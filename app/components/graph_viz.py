"""Graph Visualization Component"""
from typing import Dict
from pyvis.network import Network
from pathlib import Path
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class GraphVisualizer:
    """Production-ready graph visualizer"""
    
    def __init__(self, width: str = "100%", height: str = "800px"):
        self.width = width
        self.height = height
        logger.info("GraphVisualizer initialized")
    
    def create_interactive_graph(self, graph_data: Dict, output_file: str = "graph.html") -> str:
        """Create interactive graph visualization"""
        try:
            net = Network(
                height=self.height,
                width=self.width,
                directed=True,
                bgcolor='#ffffff',
                font_color='#000000',
                notebook=False
            )
            
            net.toggle_physics(True)
            net.show_buttons(filter_=['physics'])
            
            # Process nodes
            nodes_by_id = {}
            for node in graph_data.get('nodes', []):
                node_id = node.get('id')
                url = node.get('url')
                
                if not node_id or not url:
                    continue
                
                nodes_by_id[node_id] = node
                
                # Get counts safely
                form_count = len(node.get('forms', [])) if isinstance(node.get('forms'), list) else node.get('form_count', 0)
                input_count = len(node.get('inputs', [])) if isinstance(node.get('inputs'), list) else node.get('input_count', 0)
                link_count = len(node.get('links', [])) if isinstance(node.get('links'), list) else node.get('link_count', 0)
                
                color = '#FF6B6B' if form_count > 0 else '#FFA500' if input_count > 0 else '#4ECDC4'
                size = max(25, 20 + (link_count * 2))
                label = node.get('normalized_url', url).strip('/').split('/')[-1] or 'home'
                title = f"<b>{node.get('title', 'Untitled')}</b><br>URL: {url}<br>Forms: {form_count} | Inputs: {input_count}"
                
                net.add_node(node_id, label=label, title=title, color=color, size=size, shape='dot')
            
            logger.info(f"✅ Added {len(nodes_by_id)} nodes")
            
            # Process edges
            edge_count = 0
            for edge in graph_data.get('edges', []):
                source = edge.get('source') or edge.get('from') or edge.get('from_hash')
                target = edge.get('target') or edge.get('to') or edge.get('to_hash')
                
                if source in nodes_by_id and target in nodes_by_id:
                    net.add_edge(source, target, color='#888888', width=1)
                    edge_count += 1
            
            logger.info(f"✅ Graph: {len(nodes_by_id)} nodes, {edge_count} edges")
            
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            net.save_graph(str(output_path))
            
            self._inject_click_handler(output_path, nodes_by_id)
            
            logger.info(f"📊 Saved: {output_path}")
            return str(output_path)
        
        except Exception as e:
            logger.error(f"❌ Graph error: {e}", exc_info=True)
            raise
    
    def _inject_click_handler(self, html_path: Path, nodes_data: Dict):
        """Inject node click handler"""
        try:
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import json
            nodes_json = json.dumps({k: {
                'url': v.get('url', ''),
                'title': v.get('title', 'Untitled'),
                'forms': len(v.get('forms', [])) if isinstance(v.get('forms'), list) else v.get('form_count', 0),
                'inputs': len(v.get('inputs', [])) if isinstance(v.get('inputs'), list) else v.get('input_count', 0),
                'buttons': len(v.get('buttons', [])) if isinstance(v.get('buttons'), list) else v.get('button_count', 0),
                'links': len(v.get('links', [])) if isinstance(v.get('links'), list) else v.get('link_count', 0)
            } for k, v in nodes_data.items()})
            
            js = f"""
<div id="node-details" style="margin-top:20px;padding:15px;background:#f8f9fa;border-radius:5px;display:none;"></div>
<script>
const nodes = {nodes_json};
setTimeout(() => {{
  if (typeof network !== 'undefined') {{
    network.on("click", (params) => {{
      if (params.nodes[0]) {{
        const n = nodes[params.nodes[0]];
        document.getElementById('node-details').innerHTML = n ? `
          <b>📄 ${{n.title}}</b><br>
          <a href="${{n.url}}" target="_blank">${{n.url}}</a><br>
          Forms: ${{n.forms}} | Inputs: ${{n.inputs}} | Buttons: ${{n.buttons}} | Links: ${{n.links}}
        ` : 'No data';
        document.getElementById('node-details').style.display = 'block';
      }}
    }});
  }}
}}, 500);
</script>
</body>"""
            
            content = content.replace('</body>', js)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
        except Exception as e:
            logger.warning(f"Click handler skip: {e}")
    

