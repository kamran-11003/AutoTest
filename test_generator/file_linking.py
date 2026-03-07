"""
File Linking System - Track relationships between crawls, constraints, and tests

Establishes clear links:
- crawl_42 → constraints_HASH.json
- crawl_42 → tests_TIMESTAMP.json
- crawl_42 → refined_tests (stored in same file with version tracking)

This allows:
- Loading correct tests for each crawl
- Preserving AI refinements
- Version history
- Independent constraint management
"""

import json
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FileLinkingSystem:
    """Track relationships between crawls, constraints, and test files"""
    
    def __init__(self, storage_dir: str = "data"):
        self.storage_dir = Path(storage_dir)
        self.link_file = self.storage_dir / "file_links.json"
        self._load_links()
    
    def _load_links(self):
        """Load file linking index"""
        if self.link_file.exists():
            with open(self.link_file, 'r', encoding='utf-8') as f:
                self.links = json.load(f)
        else:
            self.links = {
                'crawl_to_tests': {},      # crawl_hash -> test_filename
                'crawl_to_constraints': {}, # crawl_hash -> constraint_filename
                'crawl_metadata': {},       # crawl_hash -> {crawl_file, url, timestamp}
                'version_history': {}       # crawl_hash -> [list of versions]
            }
    
    def _save_links(self):
        """Save file linking index"""
        with open(self.link_file, 'w', encoding='utf-8') as f:
            json.dump(self.links, f, indent=2, ensure_ascii=False)
    
    def register_crawl(self, crawl_file: str, crawl_hash: str, metadata: Dict = None):
        """
        Register a crawl file in the linking system
        
        Args:
            crawl_file: Path to crawl file (e.g., 'crawl_42.json')
            crawl_hash: Unique hash for the crawl
            metadata: Additional metadata (url, timestamp, etc.)
        """
        self.links['crawl_metadata'][crawl_hash] = {
            'crawl_file': crawl_file,
            'registered_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        self._save_links()
        logger.info(f"Registered crawl {crawl_file} with hash {crawl_hash}")
    
    def link_tests(self, crawl_hash: str, test_file: str, version: int = 1):
        """
        Link test file to crawl
        
        Args:
            crawl_hash: Hash of the crawl
            test_file: Test filename (e.g., 'tests_20251129_220205.json')
            version: Version number of tests
        """
        self.links['crawl_to_tests'][crawl_hash] = test_file
        
        # Track version history
        if crawl_hash not in self.links['version_history']:
            self.links['version_history'][crawl_hash] = []
        
        self.links['version_history'][crawl_hash].append({
            'test_file': test_file,
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
        
        self._save_links()
        logger.info(f"Linked tests {test_file} (v{version}) to crawl {crawl_hash}")
    
    def link_constraints(self, crawl_hash: str, constraint_file: str):
        """
        Link constraint file to crawl
        
        Args:
            crawl_hash: Hash of the crawl
            constraint_file: Constraint filename
        """
        self.links['crawl_to_constraints'][crawl_hash] = constraint_file
        self._save_links()
        logger.info(f"Linked constraints {constraint_file} to crawl {crawl_hash}")
    
    def get_test_file(self, crawl_hash: str) -> Optional[str]:
        """Get test file for a crawl"""
        return self.links['crawl_to_tests'].get(crawl_hash)
    
    def get_constraint_file(self, crawl_hash: str) -> Optional[str]:
        """Get constraint file for a crawl"""
        return self.links['crawl_to_constraints'].get(crawl_hash)
    
    def get_crawl_info(self, crawl_hash: str) -> Optional[Dict]:
        """Get full crawl information"""
        return self.links['crawl_metadata'].get(crawl_hash)
    
    def get_version_history(self, crawl_hash: str) -> List[Dict]:
        """Get version history for a crawl's tests"""
        return self.links['version_history'].get(crawl_hash, [])
    
    def get_all_links_for_crawl(self, crawl_hash: str) -> Dict:
        """
        Get all linked files for a crawl
        
        Returns:
            Dictionary with test_file, constraint_file, crawl_info, and version_history
        """
        return {
            'crawl_hash': crawl_hash,
            'crawl_info': self.get_crawl_info(crawl_hash),
            'test_file': self.get_test_file(crawl_hash),
            'constraint_file': self.get_constraint_file(crawl_hash),
            'version_history': self.get_version_history(crawl_hash)
        }
    
    def find_crawl_by_file(self, crawl_file: str) -> Optional[str]:
        """Find crawl_hash by crawl filename"""
        for crawl_hash, metadata in self.links['crawl_metadata'].items():
            if metadata['crawl_file'] == crawl_file:
                return crawl_hash
        return None
    
    def delete_crawl_links(self, crawl_hash: str):
        """Delete all links for a crawl"""
        if crawl_hash in self.links['crawl_to_tests']:
            del self.links['crawl_to_tests'][crawl_hash]
        if crawl_hash in self.links['crawl_to_constraints']:
            del self.links['crawl_to_constraints'][crawl_hash]
        if crawl_hash in self.links['crawl_metadata']:
            del self.links['crawl_metadata'][crawl_hash]
        if crawl_hash in self.links['version_history']:
            del self.links['version_history'][crawl_hash]
        self._save_links()
        logger.info(f"Deleted all links for crawl {crawl_hash}")


# Singleton instance
file_linking = FileLinkingSystem()
