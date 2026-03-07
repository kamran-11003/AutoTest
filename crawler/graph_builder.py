"""
Graph Builder
Builds NetworkX directed graph representing UI state machine
"""
import networkx as nx
from typing import Dict, List, Optional
from datetime import datetime
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class GraphBuilder:
    """Builds and manages the crawl state graph"""
    
    def __init__(self):
        """Initialize graph builder"""
        self.graph = nx.DiGraph()
        logger.info("GraphBuilder initialized")
    
    def add_node(
        self,
        state_hash: str,
        url: str,
        normalized_url: str,
        title: str,
        inputs: List[Dict],
        buttons: List[str],
        links: List[str],
        forms: List[Dict],
        metadata: Optional[Dict] = None
    ):
        """
        Add a node (page state) to the graph
        
        Args:
            state_hash: Unique state identifier
            url: Page URL
            normalized_url: Normalized URL template
            title: Page title
            inputs: List of input elements
            buttons: List of button texts
            links: List of link URLs
            forms: List of form structures
            metadata: Additional metadata
        """
        node_data = {
            'hash': state_hash,
            'url': url,
            'normalized_url': normalized_url,
            'title': title,
            'input_count': len(inputs),
            'button_count': len(buttons),
            'link_count': len(links),
            'form_count': len(forms),
            'inputs': inputs,
            'buttons': buttons,
            'links': links,
            'forms': forms,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.graph.add_node(state_hash, **node_data)
        logger.debug(f"Added node: {state_hash} ({normalized_url})")
    
    def add_edge(
        self,
        from_hash: str,
        to_hash: str,
        action: str,
        element: str,
        label: Optional[str] = None,
        allow_pending: bool = False
    ):
        """
        Add an edge (transition) between states
        
        Args:
            from_hash: Source state hash
            to_hash: Target state hash (can be URL if allow_pending=True)
            action: Action type (click, submit, hover, etc.)
            element: Element selector that triggered transition
            label: Human-readable edge label
            allow_pending: If True, allow edges to non-existent nodes (for later fixing)
        """
        if from_hash not in self.graph:
            logger.warning(f"Source node {from_hash} not in graph")
            return
        
        if not allow_pending and to_hash not in self.graph:
            logger.warning(f"Target node {to_hash} not in graph")
            return
        
        edge_data = {
            'action': action,
            'element': element,
            'label': label or f"{action}: {element}",
            'timestamp': datetime.now().isoformat()
        }
        
        self.graph.add_edge(from_hash, to_hash, **edge_data)
        if allow_pending:
            logger.debug(f"Added pending edge: {from_hash} -> {to_hash[:40]}... ({action})")
        else:
            logger.debug(f"Added edge: {from_hash} -> {to_hash} ({action})")
    
    def get_node_data(self, state_hash: str) -> Optional[Dict]:
        """Get data for a specific node"""
        if state_hash in self.graph:
            return dict(self.graph.nodes[state_hash])
        return None
    
    def get_neighbors(self, state_hash: str) -> List[str]:
        """Get all neighbor nodes (outgoing edges)"""
        if state_hash in self.graph:
            return list(self.graph.successors(state_hash))
        return []
    
    def get_stats(self) -> Dict:
        """Get graph statistics"""
        stats = {
            'node_count': self.graph.number_of_nodes(),
            'edge_count': self.graph.number_of_edges(),
            'isolated_nodes': len(list(nx.isolates(self.graph))),
            'is_connected': nx.is_weakly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False
        }
        
        # Calculate depth (from first node)
        if self.graph.number_of_nodes() > 0:
            nodes = list(self.graph.nodes())
            first_node = nodes[0]
            try:
                depths = nx.single_source_shortest_path_length(self.graph, first_node)
                stats['max_depth'] = max(depths.values()) if depths else 0
                stats['avg_depth'] = sum(depths.values()) / len(depths) if depths else 0
            except:
                stats['max_depth'] = 0
                stats['avg_depth'] = 0
        else:
            stats['max_depth'] = 0
            stats['avg_depth'] = 0
        
        return stats
    
    def to_dict(self) -> Dict:
        """Export graph to dictionary format"""
        return {
            'nodes': [
                {
                    'id': node,
                    **self.graph.nodes[node]
                }
                for node in self.graph.nodes()
            ],
            'edges': [
                {
                    'from_hash': edge[0],
                    'to_hash': edge[1],
                    'source': edge[0],  # Alias for visualization compatibility
                    'target': edge[1],  # Alias for visualization compatibility
                    **self.graph.edges[edge]
                }
                for edge in self.graph.edges()
            ],
            'stats': self.get_stats()
        }
    
    def to_graphml(self, filepath: str):
        """Export graph to GraphML format"""
        try:
            # Create a clean copy without complex types
            clean_graph = nx.DiGraph()
            
            for node in self.graph.nodes():
                # Only include simple types for GraphML
                clean_data = {
                    'url': str(self.graph.nodes[node].get('url', '')),
                    'title': str(self.graph.nodes[node].get('title', '')),
                    'input_count': int(self.graph.nodes[node].get('input_count', 0)),
                    'form_count': int(self.graph.nodes[node].get('form_count', 0)),
                    'link_count': int(self.graph.nodes[node].get('link_count', 0))
                }
                clean_graph.add_node(node, **clean_data)
            
            for edge in self.graph.edges():
                clean_edge_data = {
                    'action': str(self.graph.edges[edge].get('action', '')),
                    'label': str(self.graph.edges[edge].get('label', ''))
                }
                clean_graph.add_edge(edge[0], edge[1], **clean_edge_data)
            
            nx.write_graphml(clean_graph, filepath)
            logger.info(f"💾 Graph exported to GraphML: {filepath}")
        except Exception as e:
            logger.error(f"Error exporting to GraphML: {e}")
    
    def to_json(self, filepath: str):
        """Export graph to JSON format"""
        import json
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"💾 Graph exported to JSON: {filepath}")
        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
    
    def find_cycles(self) -> List[List[str]]:
        """Find cyclic paths in the graph"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def get_all_paths(self, start_hash: str, end_hash: str, max_length: int = 10) -> List[List[str]]:
        """Get all paths between two nodes"""
        try:
            paths = list(nx.all_simple_paths(
                self.graph,
                start_hash,
                end_hash,
                cutoff=max_length
            ))
            return paths
        except:
            return []
