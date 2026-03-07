"""
URL Normalizer
Converts dynamic URLs to templates (/product/123 -> /product/:id)
"""
import re
from typing import Dict, List
from urllib.parse import urlparse, parse_qs
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class URLNormalizer:
    """Normalize dynamic URLs to prevent duplicate state detection"""
    
    def __init__(self, patterns: List[Dict[str, str]] = None):
        """
        Initialize URL normalizer with custom patterns
        
        Args:
            patterns: List of dicts with 'pattern' (regex) and 'replacement' keys
        """
        self.patterns = patterns or [
            # Only normalize pure numeric IDs (e.g., /product/123 -> /product/:id)
            {'pattern': r'/\d+', 'replacement': '/:id'},
            # UUID pattern (e.g., /user/a1b2c3d4-e5f6-... -> /user/:uuid)
            {'pattern': r'/[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}', 'replacement': '/:uuid'},
            # Very long alphanumeric slugs (30+ chars to avoid matching legitimate path names)
            # NOTE: Disabled for sites like DemoQA with descriptive URLs (e.g., /automation-practice-form)
            # {'pattern': r'/[a-zA-Z0-9-]{30,}', 'replacement': '/:slug'},
        ]
        
        logger.debug(f"Initialized URLNormalizer with {len(self.patterns)} patterns")
    
    def normalize(self, url: str) -> str:
        """
        Normalize a URL by replacing dynamic segments with placeholders
        
        Args:
            url: Full URL to normalize
        
        Returns:
            Normalized URL with placeholders
        
        Examples:
            /product/123 -> /product/:id
            /blog/my-article-title -> /blog/:slug
            /user/a1b2c3d4-e5f6-7890 -> /user/:uuid
        """
        try:
            parsed = urlparse(url)
            path = parsed.path
            
            # Remove trailing slash
            path = path.rstrip('/')
            
            # Apply normalization patterns in order
            for pattern_dict in self.patterns:
                pattern = pattern_dict['pattern']
                replacement = pattern_dict['replacement']
                
                # Replace each segment separately to avoid over-matching
                segments = path.split('/')
                normalized_segments = []
                
                for segment in segments:
                    if segment and re.fullmatch(pattern.strip('/'), segment):
                        normalized_segments.append(replacement.strip('/'))
                    else:
                        normalized_segments.append(segment)
                
                path = '/'.join(normalized_segments)
            
            # Reconstruct normalized URL (path only, no query params for hashing)
            normalized = path or '/'
            
            if normalized != parsed.path.rstrip('/'):
                logger.debug(f"Normalized: {parsed.path} -> {normalized}")
            
            return normalized
        
        except Exception as e:
            logger.error(f"Error normalizing URL {url}: {e}")
            return url
    
    def get_base_pattern(self, url: str) -> str:
        """
        Get the base pattern for a URL (useful for grouping)
        
        Args:
            url: URL to get pattern for
        
        Returns:
            Base pattern (e.g., /product/:id)
        """
        return self.normalize(url)
    
    def are_equivalent(self, url1: str, url2: str) -> bool:
        """
        Check if two URLs are equivalent after normalization
        
        Args:
            url1: First URL
            url2: Second URL
        
        Returns:
            True if URLs normalize to same pattern
        """
        return self.normalize(url1) == self.normalize(url2)


# Singleton instance
_normalizer_instance = None

def get_normalizer(patterns: List[Dict[str, str]] = None) -> URLNormalizer:
    """Get or create URLNormalizer singleton"""
    global _normalizer_instance
    if _normalizer_instance is None:
        _normalizer_instance = URLNormalizer(patterns)
    return _normalizer_instance
