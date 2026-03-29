"""
Gemini API Key Rotator
Automatically switches between multiple API keys when rate limits are hit
"""
import os
import re
import time
from typing import List, Optional
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class GeminiKeyRotator:
    """Manages multiple Gemini API keys with automatic rotation on rate limits"""
    
    def __init__(self):
        """Initialize key rotator with API keys from environment"""
        self.api_keys = self._load_api_keys()
        self.current_index = 0
        self.rate_limit_counts = {}  # Track rate limit hits per key
        self.suspended_keys = set()  # Track permanently suspended keys
        self.last_switch_time = time.time()
        
        if self.api_keys:
            logger.info(f"🔑 Loaded {len(self.api_keys)} Gemini API keys for rotation")
        else:
            logger.warning("⚠️  No Gemini API keys found")
    
    def _load_api_keys(self) -> List[str]:
        """
        Load API keys from environment variables
        Supports:
        - GEMINI_API_KEY (single key)
        - GEMINI_API_KEYS (comma-separated list)
        - GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.
        """
        keys = []
        
        # Method 1: Comma-separated list
        keys_str = os.getenv('GEMINI_API_KEYS', '')
        if keys_str:
            keys.extend([k.strip() for k in keys_str.split(',') if k.strip()])
        
        # Method 2: Individual keys (GEMINI_API_KEY_1, GEMINI_API_KEY_2, etc.)
        for i in range(1, 11):  # Support up to 10 keys
            key = os.getenv(f'GEMINI_API_KEY_{i}', '')
            if key:
                keys.append(key.strip())
        
        # Method 3: Single key fallback
        if not keys:
            single_key = os.getenv('GEMINI_API_KEY', '')
            if single_key:
                keys.append(single_key.strip())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keys = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        return unique_keys
    
    def get_current_key(self) -> Optional[str]:
        """Get the current active API key (skipping suspended keys)"""
        if not self.api_keys:
            return None
        
        # Skip suspended keys
        attempts = 0
        while attempts < len(self.api_keys):
            current_key = self.api_keys[self.current_index]
            if current_key not in self.suspended_keys:
                return current_key
            # This key is suspended, move to next
            self.current_index = (self.current_index + 1) % len(self.api_keys)
            attempts += 1
        
        # All keys are suspended
        logger.error("❌ All API keys are suspended!")
        return None
    
    def rotate_key(self, reason: str = "rate_limit") -> Optional[str]:
        """
        Rotate to the next API key
        
        Args:
            reason: Reason for rotation (rate_limit, error, manual)
            
        Returns:
            New API key or None if no keys available
        """
        if not self.api_keys:
            return None
        
        if len(self.api_keys) == 1:
            logger.warning("⚠️  Only 1 API key available, cannot rotate")
            return self.api_keys[0]
        
        # Track rate limit hit for current key
        current_key_preview = self.api_keys[self.current_index][-8:]
        if reason == "rate_limit":
            self.rate_limit_counts[self.current_index] = \
                self.rate_limit_counts.get(self.current_index, 0) + 1
        
        # Move to next key
        old_index = self.current_index
        self.current_index = (self.current_index + 1) % len(self.api_keys)
        self.last_switch_time = time.time()
        
        new_key_preview = self.api_keys[self.current_index][-8:]
        logger.info(f"🔄 Rotated API key: ...{current_key_preview} → ...{new_key_preview} (reason: {reason})")
        
        return self.api_keys[self.current_index]
    
    def extract_retry_delay(self, error_message: str) -> Optional[float]:
        """Extract retry delay from Gemini error message"""
        try:
            # Look for "Please retry in X.XXXXs"
            match = re.search(r'Please retry in ([\d.]+)s', str(error_message))
            if match:
                return float(match.group(1))
            
            # Look for retry_delay { seconds: X }
            match = re.search(r'retry_delay\s*\{\s*seconds:\s*(\d+)', str(error_message))
            if match:
                return float(match.group(1))
            
            return None
        except:
            return None
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error"""
        error_str = str(error).lower()
        return '429' in error_str or 'quota' in error_str or 'rate limit' in error_str or 'resource has been exhausted' in error_str
    
    def is_suspended_error(self, error: Exception) -> bool:
        """Check if error indicates suspended key"""
        error_str = str(error).lower()
        return 'consumer_suspended' in error_str or 'has been suspended' in error_str or 'permission denied' in error_str
    
    def mark_key_suspended(self, key: str):
        """Mark a key as permanently suspended"""
        if key not in self.suspended_keys:
            self.suspended_keys.add(key)
            key_preview = key[-8:] if len(key) > 8 else '***'
            logger.warning(f"🚫 Marked key as SUSPENDED: ...{key_preview}")
            logger.warning(f"   Remaining active keys: {len(self.api_keys) - len(self.suspended_keys)}/{len(self.api_keys)}")

    def mark_success(self):
        """No-op hook for successful API calls (kept for interface compatibility)."""
        pass
    
    def get_stats(self) -> dict:
        """Get rotation statistics"""
        return {
            'total_keys': len(self.api_keys),
            'current_index': self.current_index,
            'current_key_preview': f"...{self.api_keys[self.current_index][-8:]}" if self.api_keys else None,
            'rate_limit_hits': self.rate_limit_counts,
            'time_since_last_switch': time.time() - self.last_switch_time
        }
    
    def reset(self):
        """Reset to first key"""
        self.current_index = 0
        self.rate_limit_counts = {}
        logger.info("🔄 Key rotation reset to first key")
