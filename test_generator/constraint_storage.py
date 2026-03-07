"""
Constraint Storage - Separate storage for field constraints

Keeps constraints separate from crawl files to maintain clean data architecture.
Provides versioning and linking to test cases.
"""

import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConstraintStorage:
    """Persistent storage for field constraints"""
    
    def __init__(self, storage_dir: str = "data/constraints"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = self.storage_dir / "constraint_index.json"
        self._load_index()
    
    def _load_index(self):
        """Load constraint index"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                self.index = json.load(f)
        else:
            self.index = {}
    
    def _save_index(self):
        """Save constraint index"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def save_constraints(self, crawl_hash: str, constraints: Dict) -> str:
        """
        Save constraints for a specific crawl
        
        Args:
            crawl_hash: Hash identifying the crawl
            constraints: Dictionary of field_id -> constraints mapping
            
        Returns:
            Filename where constraints were saved
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"constraints_{crawl_hash}.json"
        filepath = self.storage_dir / filename
        
        # Create constraint record
        constraint_record = {
            'crawl_hash': crawl_hash,
            'timestamp': datetime.now().isoformat(),
            'last_modified': timestamp,
            'constraints': constraints,
            'version': self.index.get(crawl_hash, {}).get('version', 0) + 1
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(constraint_record, f, indent=2, ensure_ascii=False)
        
        # Update index
        self.index[crawl_hash] = {
            'filename': filename,
            'last_modified': timestamp,
            'version': constraint_record['version']
        }
        self._save_index()
        
        logger.info(f"Saved constraints for crawl {crawl_hash} (version {constraint_record['version']})")
        return filename
    
    def load_constraints(self, crawl_hash: str) -> Optional[Dict]:
        """
        Load constraints for a specific crawl
        
        Args:
            crawl_hash: Hash identifying the crawl
            
        Returns:
            Constraints dictionary or None if not found
        """
        if crawl_hash not in self.index:
            logger.info(f"No constraints found for crawl {crawl_hash}")
            return None
        
        filename = self.index[crawl_hash]['filename']
        filepath = self.storage_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Constraint file {filename} not found")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            constraint_record = json.load(f)
        
        logger.info(f"Loaded constraints for crawl {crawl_hash} (version {constraint_record['version']})")
        return constraint_record['constraints']
    
    def has_constraints(self, crawl_hash: str) -> bool:
        """Check if constraints exist for a crawl"""
        return crawl_hash in self.index
    
    def get_field_constraint(self, crawl_hash: str, field_id: str) -> Optional[Dict]:
        """Get constraints for a specific field"""
        constraints = self.load_constraints(crawl_hash)
        if not constraints:
            return None
        return constraints.get(field_id)
    
    def update_field_constraint(self, crawl_hash: str, field_id: str, 
                               field_constraint: Dict) -> bool:
        """
        Update constraint for a single field
        
        Args:
            crawl_hash: Hash identifying the crawl
            field_id: Field identifier
            field_constraint: New constraint values
            
        Returns:
            True if successful, False otherwise
        """
        # Load existing constraints
        constraints = self.load_constraints(crawl_hash) or {}
        
        # Update specific field
        constraints[field_id] = {
            **field_constraint,
            'last_updated': datetime.now().isoformat()
        }
        
        # Save back
        self.save_constraints(crawl_hash, constraints)
        logger.info(f"Updated constraint for field {field_id} in crawl {crawl_hash}")
        return True
    
    def delete_constraints(self, crawl_hash: str) -> bool:
        """Delete constraints for a crawl"""
        if crawl_hash not in self.index:
            return False
        
        filename = self.index[crawl_hash]['filename']
        filepath = self.storage_dir / filename
        
        if filepath.exists():
            filepath.unlink()
        
        del self.index[crawl_hash]
        self._save_index()
        
        logger.info(f"Deleted constraints for crawl {crawl_hash}")
        return True


# Singleton instance
constraint_storage = ConstraintStorage()
