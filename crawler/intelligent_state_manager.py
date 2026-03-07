"""
Intelligent State Manager
Uses full rendered HTML comparison (document.body.innerHTML) instead of URL+DOM hashing
Treats SPAs correctly by comparing actual visual state
"""
import hashlib
import re
from difflib import SequenceMatcher
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


@dataclass
class PageState:
    """Represents a unique UI state"""
    state_id: str
    url: str
    normalized_url: str
    rendered_html: str
    rendered_html_hash: str
    input_elements: List = field(default_factory=list)
    form_structures: List = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict = field(default_factory=dict)


class IntelligentStateManager:
    """
    Manages UI states using full rendered HTML comparison
    No URL+DOM hashing - pure visual state comparison
    """
    
    def __init__(self, similarity_threshold: float = 0.95):
        """
        Initialize state manager
        
        Args:
            similarity_threshold: Threshold for considering states similar (0.0-1.0)
        """
        self.states: Dict[str, PageState] = {}
        self.state_by_url: Dict[str, List[str]] = {}  # URL -> [state_ids]
        self.similarity_threshold = similarity_threshold
        
        logger.info(f"IntelligentStateManager initialized (similarity={similarity_threshold})")
    
    def get_rendered_html(self, page) -> str:
        """
        Get full rendered HTML from page (document.body.innerHTML)
        This captures the complete visual state of SPAs
        
        Args:
            page: Playwright page object
        
        Returns:
            Rendered HTML string
        """
        js_code = """
        () => {
            // Get full rendered HTML
            const html = document.body.innerHTML;
            
            // Clean dynamic content that changes but doesn't affect state
            let cleaned = html;
            
            // Remove timestamps
            cleaned = cleaned.replace(/\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/g, 'TIMESTAMP');
            
            // Remove random IDs
            cleaned = cleaned.replace(/id="[a-z0-9-]{20,}"/gi, 'id="RANDOM_ID"');
            
            // Remove counters
            cleaned = cleaned.replace(/\d+ (items?|results?|pages?)/gi, 'N items');
            
            // Remove cache busters
            cleaned = cleaned.replace(/\?v=\d+/g, '?v=VERSION');
            cleaned = cleaned.replace(/\?_=\d+/g, '?_=CACHE');
            
            return cleaned;
        }
        """
        
        try:
            html = page.evaluate(js_code)
            return html
        except Exception as e:
            logger.error(f"Error getting rendered HTML: {e}")
            return ""
    
    def clean_html_for_comparison(self, html: str) -> str:
        """
        Clean HTML for comparison
        Remove whitespace, normalize formatting
        
        Args:
            html: Raw HTML string
        
        Returns:
            Cleaned HTML
        """
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', html)
        
        # Remove comments
        cleaned = re.sub(r'<!--.*?-->', '', cleaned)
        
        # Lowercase for case-insensitive comparison
        cleaned = cleaned.lower()
        
        return cleaned.strip()
    
    def calculate_similarity(self, html1: str, html2: str) -> float:
        """
        Calculate similarity between two HTML strings
        
        Args:
            html1: First HTML string
            html2: Second HTML string
        
        Returns:
            Similarity score (0.0 to 1.0)
        """
        clean1 = self.clean_html_for_comparison(html1)
        clean2 = self.clean_html_for_comparison(html2)
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, clean1, clean2).ratio()
    
    def hash_html(self, html: str) -> str:
        """
        Generate hash from rendered HTML
        
        Args:
            html: HTML string
        
        Returns:
            8-character hash
        """
        cleaned = self.clean_html_for_comparison(html)
        full_hash = hashlib.sha256(cleaned.encode()).hexdigest()
        return full_hash[:8]
    
    def is_new_state(self, url: str, rendered_html: str, normalized_url: str = None) -> bool:
        """
        Check if this is a new unique state
        
        Args:
            url: Current URL
            rendered_html: Full rendered HTML
            normalized_url: Normalized URL pattern
        
        Returns:
            True if new state, False if duplicate
        """
        if normalized_url is None:
            normalized_url = url
        
        # Get existing states for this URL pattern
        existing_state_ids = self.state_by_url.get(normalized_url, [])
        
        if not existing_state_ids:
            # No states for this URL pattern - definitely new
            return True
        
        # Compare with existing states
        for state_id in existing_state_ids:
            existing_state = self.states.get(state_id)
            if not existing_state:
                continue
            
            # Calculate similarity
            similarity = self.calculate_similarity(rendered_html, existing_state.rendered_html)
            
            if similarity >= self.similarity_threshold:
                logger.debug(f"Duplicate state detected (similarity={similarity:.2f})")
                return False
        
        # No similar state found - this is new
        return True
    
    def add_state(
        self,
        url: str,
        normalized_url: str,
        rendered_html: str,
        input_elements: List = None,
        form_structures: List = None,
        metadata: Dict = None
    ) -> PageState:
        """
        Add new state to manager
        
        Args:
            url: Current URL
            normalized_url: Normalized URL pattern
            rendered_html: Full rendered HTML
            input_elements: List of input elements
            form_structures: List of form structures
            metadata: Additional metadata
        
        Returns:
            Created PageState object
        """
        # Generate hash from HTML
        html_hash = self.hash_html(rendered_html)
        
        # Create state
        state = PageState(
            state_id=html_hash,
            url=url,
            normalized_url=normalized_url,
            rendered_html=rendered_html,
            rendered_html_hash=html_hash,
            input_elements=input_elements or [],
            form_structures=form_structures or [],
            metadata=metadata or {}
        )
        
        # Store state
        self.states[html_hash] = state
        
        # Update URL mapping
        if normalized_url not in self.state_by_url:
            self.state_by_url[normalized_url] = []
        self.state_by_url[normalized_url].append(html_hash)
        
        logger.info(f"✅ New state: {html_hash} | {normalized_url} | {len(input_elements or [])} inputs")
        
        return state
    
    def get_state(self, state_id: str) -> Optional[PageState]:
        """Get state by ID"""
        return self.states.get(state_id)
    
    def get_all_states(self) -> List[PageState]:
        """Get all tracked states"""
        return list(self.states.values())
    
    def get_stats(self) -> Dict:
        """Get statistics"""
        return {
            'total_states': len(self.states),
            'total_urls': len(self.state_by_url),
            'avg_states_per_url': len(self.states) / len(self.state_by_url) if self.state_by_url else 0
        }
