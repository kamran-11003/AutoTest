"""
State Transition Testing Generator

Generates test cases for testing state transitions and navigation flows
(e.g., cart states, multi-step forms, wizards).
"""

from typing import Dict, List, Any, Set, Tuple
import logging

logger = logging.getLogger(__name__)


class StateTransitionGenerator:
    """Generate State Transition test cases"""
    
    def __init__(self):
        self.test_cases = []
        self.node_map = {}
    
    def generate(self, graph_data: Dict) -> List[Dict[str, Any]]:
        """
        Generate state transition test cases from UI graph data
        
        Args:
            graph_data: Dictionary containing nodes and edges from crawler
            
        Returns:
            List of test case dictionaries
        """
        self.test_cases = []
        
        if not graph_data:
            logger.warning("No graph data provided")
            return []
        
        nodes = graph_data.get('nodes', [])
        edges = graph_data.get('edges', [])
        
        # Build node map for ID to URL/title resolution
        self.node_map = {}
        for node in nodes:
            node_id = node.get('id', node.get('hash', ''))
            if node_id:
                self.node_map[node_id.lower()] = {
                    'url': node.get('url', ''),
                    'title': node.get('title', ''),
                    'normalized_url': node.get('normalized_url', '')
                }
        
        if not nodes or not edges:
            logger.warning("Graph has no nodes or edges")
            return []
        
        # Generate test cases for different flow types
        self.test_cases.extend(self._generate_linear_flows(nodes, edges))
        self.test_cases.extend(self._generate_circular_flows(nodes, edges))
        self.test_cases.extend(self._generate_branching_flows(nodes, edges))
        
        logger.info(f"Generated {len(self.test_cases)} State Transition test cases")
        return self.test_cases
    
    def _generate_linear_flows(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate test cases for linear flows (A → B → C → D)"""
        test_cases = []
        
        # Build adjacency list
        graph = {}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            action = edge.get('action', 'navigate')
            
            if source not in graph:
                graph[source] = []
            graph[source].append({'target': target, 'action': action})
        
        # Find paths of length 3+ (meaningful flows)
        paths = self._find_paths(graph, min_length=3, max_length=6)
        
        for idx, path in enumerate(paths[:20]):  # Limit to 20 paths
            steps = []
            for i in range(len(path) - 1):
                source_url = path[i]
                target_url = path[i + 1]
                
                # Find the action for this transition
                action = 'navigate'
                for edge in edges:
                    if edge.get('source') == source_url and edge.get('target') == target_url:
                        action = edge.get('action', 'navigate')
                        break
                
                steps.append({
                    'step': i + 1,
                    'action': action,
                    'from_url': source_url,
                    'to_url': target_url,
                    'description': f'Navigate from {self._get_page_name(source_url)} to {self._get_page_name(target_url)}'
                })
            
            test_cases.append({
                'id': f"state_linear_{idx}",
                'type': 'State Transition',
                'subtype': 'linear_flow',
                'path_length': len(path),
                'start_url': path[0],
                'end_url': path[-1],
                'steps': steps,
                'expected_result': 'success',
                'description': f'Linear flow: {self._get_page_name(path[0])} → {self._get_page_name(path[-1])} ({len(path)} steps)',
                'flow_description': ' → '.join([self._get_page_name(url) for url in path])
            })
        
        return test_cases
    
    def _generate_circular_flows(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate test cases for circular flows (A → B → C → A)"""
        test_cases = []
        
        # Build adjacency list
        graph = {}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source not in graph:
                graph[source] = []
            graph[source].append(target)
        
        # Find circular paths
        circles = self._find_circles(graph, max_length=5)
        
        for idx, circle in enumerate(circles[:10]):  # Limit to 10 circles
            steps = []
            for i in range(len(circle)):
                source_url = circle[i]
                target_url = circle[(i + 1) % len(circle)]
                
                steps.append({
                    'step': i + 1,
                    'action': 'navigate',
                    'from_url': source_url,
                    'to_url': target_url,
                    'description': f'Navigate from {self._get_page_name(source_url)} to {self._get_page_name(target_url)}'
                })
            
            test_cases.append({
                'id': f"state_circular_{idx}",
                'type': 'State Transition',
                'subtype': 'circular_flow',
                'path_length': len(circle),
                'start_url': circle[0],
                'end_url': circle[0],  # Returns to start
                'steps': steps,
                'expected_result': 'success',
                'description': f'Circular flow: Returns to {self._get_page_name(circle[0])} after {len(circle)} steps',
                'flow_description': ' → '.join([self._get_page_name(url) for url in circle]) + f' → {self._get_page_name(circle[0])}'
            })
        
        return test_cases
    
    def _generate_branching_flows(self, nodes: List[Dict], edges: List[Dict]) -> List[Dict]:
        """Generate test cases for branching flows (decision points)"""
        test_cases = []
        
        # Build adjacency list with action details
        graph = {}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            action = edge.get('action', {})
            
            if source not in graph:
                graph[source] = []
            graph[source].append({'target': target, 'action': action})
        
        # Find nodes with multiple outgoing edges (decision points)
        decision_points = {url: targets for url, targets in graph.items() if len(targets) > 1}
        
        for idx, (decision_url, branches) in enumerate(decision_points.items()):
            if idx >= 15:  # Limit to 15 decision points
                break
            
            # Create test case for each branch
            for branch_idx, branch in enumerate(branches):
                target_url = branch['target']
                action = branch.get('action', 'navigate')
                
                test_cases.append({
                    'id': f"state_branch_{idx}_{branch_idx}",
                    'type': 'State Transition',
                    'subtype': 'branching_flow',
                    'decision_point': decision_url,
                    'branch_taken': target_url,
                    'total_branches': len(branches),
                    'steps': [
                        {
                            'step': 1,
                            'action': 'navigate',
                            'from_url': 'start',
                            'to_url': decision_url,
                            'description': f'Navigate to decision point: {self._get_page_name(decision_url)}'
                        },
                        {
                            'step': 2,
                            'action': action,
                            'from_url': decision_url,
                            'to_url': target_url,
                            'description': f'Take branch {branch_idx + 1}/{len(branches)}: {self._get_page_name(target_url)}'
                        }
                    ],
                    'expected_result': 'success',
                    'description': f'Branch {branch_idx + 1} from {self._get_page_name(decision_url)}: → {self._get_page_name(target_url)}',
                    'flow_description': f'{self._get_page_name(decision_url)} → {self._get_page_name(target_url)} (Branch {branch_idx + 1}/{len(branches)})'
                })
        
        return test_cases
    
    def _find_paths(self, graph: Dict, min_length: int = 3, max_length: int = 6) -> List[List[str]]:
        """Find all paths between min and max length using DFS"""
        paths = []
        
        def dfs(node: str, current_path: List[str], visited: Set[str]):
            if len(current_path) >= min_length and len(current_path) <= max_length:
                paths.append(current_path[:])
            
            if len(current_path) >= max_length:
                return
            
            if node in graph:
                for neighbor_info in graph[node]:
                    neighbor = neighbor_info.get('target', neighbor_info) if isinstance(neighbor_info, dict) else neighbor_info
                    if neighbor not in visited:
                        visited.add(neighbor)
                        current_path.append(neighbor)
                        dfs(neighbor, current_path, visited)
                        current_path.pop()
                        visited.remove(neighbor)
        
        # Start DFS from each node
        for start_node in list(graph.keys())[:10]:  # Limit starting points
            visited = {start_node}
            dfs(start_node, [start_node], visited)
        
        return paths
    
    def _find_circles(self, graph: Dict, max_length: int = 5) -> List[List[str]]:
        """Find circular paths (cycles) in the graph"""
        circles = []
        
        def dfs_circle(node: str, start: str, current_path: List[str], visited: Set[str]):
            if len(current_path) > 1 and len(current_path) <= max_length:
                if node in graph:
                    for neighbor in graph[node]:
                        if neighbor == start:
                            circles.append(current_path[:])
                        elif neighbor not in visited and len(current_path) < max_length:
                            visited.add(neighbor)
                            current_path.append(neighbor)
                            dfs_circle(neighbor, start, current_path, visited)
                            current_path.pop()
                            visited.remove(neighbor)
        
        # Try to find circles starting from each node
        for start_node in list(graph.keys())[:10]:  # Limit starting points
            visited = {start_node}
            dfs_circle(start_node, start_node, [start_node], visited)
        
        return circles
    
    def _get_page_name(self, node_id_or_url: str) -> str:
        """
        Extract readable page name from node ID or URL
        
        Args:
            node_id_or_url: Either a node hash ID or a full URL
            
        Returns:
            Readable page name
        """
        if not node_id_or_url:
            return 'Unknown'
        
        # First check if this is a node ID that needs resolution
        node_info = self.node_map.get(node_id_or_url.lower(), {})
        if node_info:
            url = node_info.get('url', node_id_or_url)
            title = node_info.get('title', '')
        else:
            # It's already a URL
            url = node_id_or_url
            title = ''
        
        # Extract path from URL
        if '://' in url:
            path = url.split('://', 1)[1]
        else:
            path = url
        
        # Remove domain
        if '/' in path:
            path = '/' + '/'.join(path.split('/')[1:])
        
        # Clean up
        path = path.strip('/')
        if not path:
            return title if title and title.upper() != title else 'Home'  # Use title unless it's all caps
        
        # Make readable from URL path
        name = path.split('/')[-1] or path.split('/')[-2] if len(path.split('/')) > 1 else path
        name = name.replace('-', ' ').replace('_', ' ').title()
        
        # Only use title if it's different and meaningful (not generic all-caps)
        if title and title.upper() != title and title.lower() != name.lower():
            return f"{name} ({title})"[:50]
        
        return name[:50]  # Limit length
