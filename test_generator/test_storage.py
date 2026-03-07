"""
Persistent Test Storage

Saves generated tests with metadata and provides loading functionality.
Prevents redundant test generation for same crawl data.
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class TestStorage:
    """Persistent storage for generated test cases"""
    
    def __init__(self, storage_dir: str = "data/generated_tests"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "test_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load test generation index"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def _save_index(self):
        """Save test generation index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2)
    
    def _get_crawl_hash(self, crawl_data: Dict) -> str:
        """Generate unique hash for crawl data"""
        # Use nodes and edges to create hash
        crawl_str = json.dumps({
            'nodes': len(crawl_data.get('nodes', [])),
            'edges': len(crawl_data.get('edges', [])),
            'node_ids': sorted([n.get('id') for n in crawl_data.get('nodes', [])]),
        }, sort_keys=True)
        return hashlib.md5(crawl_str.encode()).hexdigest()
    
    def save_tests(self, test_results: Dict, crawl_data: Dict, metadata: Dict = None, 
                   update_existing: bool = True) -> str:
        """
        Save generated tests with metadata
        
        Args:
            test_results: Generated test cases
            crawl_data: Original crawl data
            metadata: Additional metadata
            update_existing: If True, update existing test file; if False, create new version
        
        Returns:
            Saved file path
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        crawl_hash = self._get_crawl_hash(crawl_data)
        
        # Check if tests exist for this crawl
        existing_file = None
        existing_data = {}
        if update_existing and crawl_hash in self.index:
            existing_file = self.storage_dir / self.index[crawl_hash]['filename']
            if existing_file.exists():
                # Load existing data to preserve AI refinements
                with open(existing_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                logger.info(f"Updating existing test file: {existing_file.name}")
            else:
                existing_file = None
        
        # Create storage record
        storage_record = {
            'timestamp': existing_data.get('timestamp') if existing_file else datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'crawl_hash': crawl_hash,
            'test_results': test_results,
            'metadata': metadata or {},
            'crawl_summary': {
                'total_nodes': len(crawl_data.get('nodes', [])),
                'total_edges': len(crawl_data.get('edges', [])),
                'total_forms': sum(len(n.get('forms', [])) for n in crawl_data.get('nodes', [])),
            },
            'version': existing_data.get('version', 0) + 1 if existing_file else 1,
            'ai_refined': existing_data.get('ai_refined', False) if existing_file else False,
            'refinement_history': existing_data.get('refinement_history', []) if existing_file else []
        }
        
        # Preserve AI refinements if they exist
        if existing_file and existing_data.get('ai_refined'):
            storage_record['ai_refined'] = True
            storage_record['refined_test_results'] = existing_data.get('refined_test_results', {})
            logger.info(f"Preserved AI refinements from version {existing_data.get('version', 0)}")
        
        # Save to file (update existing or create new)
        if update_existing and existing_file:
            filename = existing_file.name
            filepath = existing_file
        else:
            filename = f"tests_{timestamp}.json"
            filepath = self.storage_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(storage_record, f, indent=2, ensure_ascii=False)
        
        # Calculate total tests
        total_tests = sum(len(tests) for tests in test_results.get('test_cases', {}).values())
        
        # Update index
        self.index[crawl_hash] = {
            'filename': filename,
            'timestamp': timestamp,
            'total_tests': total_tests,
            'version': storage_record['version'],
            'ai_refined': storage_record['ai_refined'],
            'last_updated': storage_record['last_updated']
        }
        self._save_index()
        
        action = "Updated" if (update_existing and existing_file) else "Created"
        logger.info(f"{action} {total_tests} tests in {filename} (version {storage_record['version']})")
        return str(filepath)
    
    def load_tests(self, crawl_hash: str = None, filename: str = None) -> Optional[Dict]:
        """
        Load previously generated tests
        
        Args:
            crawl_hash: Hash of crawl data
            filename: Specific filename to load
        
        Returns:
            Test results or None
        """
        if filename:
            filepath = self.storage_dir / filename
        elif crawl_hash and crawl_hash in self.index:
            filename = self.index[crawl_hash]['filename']
            filepath = self.storage_dir / filename
        else:
            return None
        
        if not filepath.exists():
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def has_tests_for_crawl(self, crawl_data: Dict) -> bool:
        """Check if tests already exist for crawl data"""
        crawl_hash = self._get_crawl_hash(crawl_data)
        return crawl_hash in self.index
    
    def get_latest_tests(self) -> Optional[Dict]:
        """Get most recently generated tests"""
        if not self.index:
            return None
        
        # Find latest by timestamp
        latest_hash = max(self.index.items(), key=lambda x: x[1]['timestamp'])[0]
        return self.load_tests(crawl_hash=latest_hash)
    
    def list_all_tests(self) -> List[Dict]:
        """List all stored test generations"""
        results = []
        for crawl_hash, info in self.index.items():
            results.append({
                'crawl_hash': crawl_hash,
                'filename': info['filename'],
                'timestamp': info['timestamp'],
                'total_tests': info['total_tests'],
                'ai_refined': info.get('ai_refined', False),
            })
        return sorted(results, key=lambda x: x['timestamp'], reverse=True)
    
    def delete_tests(self, filename: str) -> bool:
        """Delete stored tests"""
        filepath = self.storage_dir / filename
        if filepath.exists():
            filepath.unlink()
            # Remove from index
            for crawl_hash, info in list(self.index.items()):
                if info['filename'] == filename:
                    del self.index[crawl_hash]
            self._save_index()
            logger.info(f"Deleted tests: {filename}")
            return True
        return False
