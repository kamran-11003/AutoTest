"""
State Manager
Handles state hashing, duplicate detection, and visited state tracking
"""
import hashlib
import json
from typing import Dict, Set, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from crawler.url_normalizer import get_normalizer
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class PageState:
    """Represents a unique page state"""
    hash: str
    url: str
    normalized_url: str
    title: str
    timestamp: str
    input_count: int
    button_count: int
    link_count: int
    form_count: int
    inputs: List[Dict]
    buttons: List[str]
    links: List[str]
    forms: List[Dict]
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


class StateManager:
    """Manages page states and duplicate detection using hybrid hashing"""
    
    def __init__(self, enable_normalization: bool = True):
        """
        Initialize state manager
        
        Args:
            enable_normalization: Whether to use URL normalization in hashing
        """
        self.visited_hashes: Set[str] = set()
        self.visited_urls: Set[str] = set()
        self.states: Dict[str, PageState] = {}
        self.url_to_hash: Dict[str, str] = {}
        self.enable_normalization = enable_normalization
        self.normalizer = get_normalizer()
        
        # Session management
        self.authenticated = False
        self.auth_actions: List[str] = []
        self.logout_patterns = ['logout', 'log out', 'sign out', 'signout']
        
        logger.info(f"StateManager initialized (normalization={'ON' if enable_normalization else 'OFF'})")
    
    def generate_hash(
        self,
        url: str,
        interactive_elements: List[Dict],
        use_normalization: bool = None
    ) -> str:
        """
        Generate hybrid hash from URL + interactive elements
        
        Args:
            url: Page URL
            interactive_elements: List of inputs, buttons, links
            use_normalization: Override default normalization setting
        
        Returns:
            8-character hash string
        """
        use_norm = use_normalization if use_normalization is not None else self.enable_normalization
        
        # Always include URL path for uniqueness
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        url_path = parsed_url.path.rstrip('/')  # e.g., "/elements", "/widgets"
        
        # Normalize URL if enabled (for element comparison)
        url_component = self.normalizer.normalize(url) if use_norm else url
        
        # Create element signature (sorted for consistency)
        element_signatures = []
        for elem in interactive_elements:
            tag = elem.get('tag', 'unknown')
            elem_type = elem.get('type', '')
            name = elem.get('name', '')
            signature = f"{tag}:{elem_type}:{name}"
            element_signatures.append(signature)
        
        element_signatures.sort()
        element_component = '|'.join(element_signatures)
        
        # Combine components with URL path for uniqueness
        combined = f"{url_path}::{url_component}::{element_component}"
        
        # Generate SHA256 hash and take first 8 characters
        full_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        short_hash = full_hash[:8]
        
        logger.debug(f"Generated hash {short_hash} for {url_path} ({url_component})")
        
        return short_hash
    
    def is_visited(self, state_hash: str) -> bool:
        """Check if state hash has been visited"""
        return state_hash in self.visited_hashes
    
    def is_url_visited(self, url: str) -> bool:
        """Check if URL has been visited"""
        return url in self.visited_urls
    
    def add_state(
        self,
        url: str,
        title: str,
        inputs: List[Dict],
        buttons: List[str],
        links: List[str],
        forms: List[Dict]
    ) -> tuple[str, bool]:
        """
        Add a new page state
        
        Args:
            url: Page URL
            title: Page title
            inputs: List of input elements
            buttons: List of button texts
            links: List of link URLs
            forms: List of form structures
        
        Returns:
            Tuple of (state_hash, is_new)
        """
        # Prepare interactive elements for hashing
        interactive_elements = []
        
        for inp in inputs:
            interactive_elements.append({
                'tag': 'input',
                'type': inp.get('type', 'text'),
                'name': inp.get('name', '')
            })
        
        for btn in buttons:
            interactive_elements.append({
                'tag': 'button',
                'type': 'button',
                'name': btn
            })
        
        # Generate hash
        state_hash = self.generate_hash(url, interactive_elements)
        
        # Check if already visited
        if state_hash in self.visited_hashes:
            logger.debug(f"State {state_hash} already visited (duplicate content)")
            return state_hash, False
        
        # Create normalized URL
        normalized_url = self.normalizer.normalize(url) if self.enable_normalization else url
        
        # Create state object
        state = PageState(
            hash=state_hash,
            url=url,
            normalized_url=normalized_url,
            title=title,
            timestamp=datetime.now().isoformat(),
            input_count=len(inputs),
            button_count=len(buttons),
            link_count=len(links),
            form_count=len(forms),
            inputs=inputs,
            buttons=buttons,
            links=links,
            forms=forms
        )
        
        # Store state
        self.visited_hashes.add(state_hash)
        self.visited_urls.add(url)
        self.states[state_hash] = state
        self.url_to_hash[url] = state_hash
        
        logger.info(f"✅ New state: {state_hash} | {normalized_url} | {len(inputs)} inputs, {len(forms)} forms")
        
        return state_hash, True
    
    def get_state(self, state_hash: str) -> Optional[PageState]:
        """Get state by hash"""
        return self.states.get(state_hash)
    
    def get_all_states(self) -> List[PageState]:
        """Get all discovered states"""
        return list(self.states.values())
    
    def get_stats(self) -> Dict:
        """Get crawl statistics"""
        total_inputs = sum(s.input_count for s in self.states.values())
        total_forms = sum(s.form_count for s in self.states.values())
        total_links = sum(s.link_count for s in self.states.values())
        
        return {
            'total_states': len(self.states),
            'unique_urls': len(self.visited_urls),
            'total_inputs': total_inputs,
            'total_forms': total_forms,
            'total_links': total_links,
            'avg_inputs_per_page': total_inputs / len(self.states) if self.states else 0,
            'avg_forms_per_page': total_forms / len(self.states) if self.states else 0
        }
    
    def save_checkpoint(self, filepath: str):
        """Save current state to checkpoint file"""
        checkpoint = {
            'visited_hashes': list(self.visited_hashes),
            'visited_urls': list(self.visited_urls),
            'states': {h: s.to_dict() for h, s in self.states.items()},
            'url_to_hash': self.url_to_hash,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Checkpoint saved: {filepath}")
    
    def load_checkpoint(self, filepath: str):
        """Load state from checkpoint file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            
            self.visited_hashes = set(checkpoint['visited_hashes'])
            self.visited_urls = set(checkpoint['visited_urls'])
            self.url_to_hash = checkpoint['url_to_hash']
            
            # Reconstruct PageState objects
            self.states = {}
            for hash_val, state_dict in checkpoint['states'].items():
                self.states[hash_val] = PageState(**state_dict)
            
            logger.info(f"📂 Checkpoint loaded: {len(self.states)} states restored")
            return True
        
        except Exception as e:
            logger.error(f"Error loading checkpoint: {e}")
            return False
    
    def mark_authenticated(self, action: str):
        """Mark that authentication occurred"""
        self.authenticated = True
        self.auth_actions.append(action)
        logger.info(f"🔐 Session authenticated via: {action}")
    
    def is_logout_action(self, element_text: str, element_attrs: Dict) -> bool:
        """Detect if an action is a logout action"""
        text = element_text.lower().strip()
        href = element_attrs.get('href', '').lower()
        onclick = element_attrs.get('onclick', '').lower()
        
        # Check text, href, and onclick attributes
        for pattern in self.logout_patterns:
            if pattern in text or pattern in href or pattern in onclick:
                return True
        
        return False
    
    def should_skip_action(self, element_text: str, element_attrs: Dict) -> bool:
        """Determine if action should be skipped to preserve session"""
        if self.authenticated and self.is_logout_action(element_text, element_attrs):
            logger.warning(f"⚠️ SKIPPING logout action: '{element_text}' (preserving authenticated session)")
            return True
        return False
