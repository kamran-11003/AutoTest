"""
Exporter
Handles export of crawl results to various formats
"""
import json
import pandas as pd
from pathlib import Path
from typing import Dict, List
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class Exporter:
    """Export crawl results to multiple formats"""
    
    def __init__(self, output_dir: str = "data/crawled_graphs"):
        """
        Initialize exporter
        
        Args:
            output_dir: Base directory for exports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Exporter initialized: {output_dir}")
    
    def export_json(self, data: Dict, filename: str) -> str:
        """Export data to JSON"""
        filepath = self.output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Exported JSON: {filepath}")
        return str(filepath)
    
    def export_csv(self, states: List[Dict], filename: str) -> str:
        """Export states to CSV"""
        filepath = self.output_dir / filename
        
        # Flatten state data for CSV
        flattened = []
        for state in states:
            row = {
                'hash': state.get('hash'),
                'url': state.get('url'),
                'normalized_url': state.get('normalized_url'),
                'title': state.get('title'),
                'input_count': state.get('input_count', 0),
                'button_count': state.get('button_count', 0),
                'link_count': state.get('link_count', 0),
                'form_count': state.get('form_count', 0),
                'timestamp': state.get('timestamp')
            }
            flattened.append(row)
        
        df = pd.DataFrame(flattened)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"💾 Exported CSV: {filepath}")
        return str(filepath)
    
    def export_elements_csv(self, states: List[Dict], filename: str) -> str:
        """Export detailed element list to CSV"""
        filepath = self.output_dir / filename
        
        # Extract all inputs across all pages
        elements = []
        for state in states:
            page_url = state.get('url')
            for inp in state.get('inputs', []):
                elements.append({
                    'page_url': page_url,
                    'page_title': state.get('title'),
                    'element_type': inp.get('type'),
                    'name': inp.get('name'),
                    'id': inp.get('id'),
                    'label': inp.get('label'),
                    'placeholder': inp.get('placeholder'),
                    'required': inp.get('required'),
                    'visible': inp.get('visible')
                })
        
        df = pd.DataFrame(elements)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"💾 Exported elements CSV: {filepath}")
        return str(filepath)
    
    def export_markdown_report(self, crawl_results: Dict, filename: str) -> str:
        """Export human-readable markdown report"""
        filepath = self.output_dir / filename
        
        stats = crawl_results.get('crawl_stats', {})
        graph_stats = crawl_results.get('graph_stats', {})
        
        md_content = f"""# Crawl Report

## Summary
- **Start URL**: {stats.get('start_url')}
- **Pages Crawled**: {stats.get('pages_crawled')}
- **Unique States**: {stats.get('total_states')}
- **Total Inputs**: {stats.get('total_inputs')}
- **Total Forms**: {stats.get('total_forms')}
- **Total Links**: {stats.get('total_links')}

## Graph Statistics
- **Nodes**: {graph_stats.get('node_count')}
- **Edges**: {graph_stats.get('edge_count')}
- **Max Depth**: {graph_stats.get('max_depth')}
- **Avg Depth**: {graph_stats.get('avg_depth', 0):.2f}
- **Isolated Nodes**: {graph_stats.get('isolated_nodes')}

## Discovered Pages

| URL | Title | Inputs | Forms | Links |
|-----|-------|--------|-------|-------|
"""
        
        for state in crawl_results.get('states', [])[:50]:  # First 50 pages
            md_content += f"| {state.get('url')} | {state.get('title')} | {state.get('input_count')} | {state.get('form_count')} | {state.get('link_count')} |\n"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        logger.info(f"💾 Exported markdown report: {filepath}")
        return str(filepath)
