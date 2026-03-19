"""
Test Execution Cache Manager
Manages caching of test results in Redis to avoid re-running passed tests.
Stores execution history indexed by test ID for quick retrieval.
"""

import redis
import json
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class TestCacheManager:
    """
    Manages caching of test results in Redis.
    
    Cache Structure:
    - Key: test_cache:{test_id}
    - Value: {
        "status": "passed|failed|error",
        "execution_time": 2.34,
        "last_run": "2026-03-17T10:30:00",
        "crawler_version": "v1.2.3",
        "form_url": "https://app.com/form",
        "confidence": 95,
        "oracle_method": "llm|heuristic",
        "evidence": "Form submitted successfully",
        "app_state_hash": "abc123..."  # Hash of app configuration
    }
    """
    
    def __init__(self, redis_config: Optional[Dict[str, Any]] = None):
        """
        Initialize Redis connection.
        
        Args:
            redis_config: Dict with host, port, db, password, ttl
                         Falls back to environment variables
        """
        # Load from environment if not provided
        if redis_config is None:
            redis_config = {
                'host': os.getenv('REDIS_HOST', '127.0.0.1'),
                'port': int(os.getenv('REDIS_PORT', 6379)),
                'db': int(os.getenv('REDIS_DB', 0)),
                'password': os.getenv('REDIS_PASSWORD', None),
                'ttl_seconds': int(os.getenv('REDIS_TTL', 86400))  # Default 24 hours
            }
        
        self.ttl_seconds = redis_config.get('ttl_seconds', 86400)
        self.crawler_version = os.getenv('CRAWLER_VERSION', 'v1.0.0')
        
        try:
            self.redis_client = redis.Redis(
                host=redis_config['host'],
                port=redis_config['port'],
                db=redis_config['db'],
                password=redis_config['password'] if redis_config.get('password') else None,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            logger.info(f"Redis cache connected: {redis_config['host']}:{redis_config['port']}")
            self._connected = True
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {e}. Running without cache.")
            self.redis_client = None
            self._connected = False
    
    def _make_cache_key(self, test_id: str) -> str:
        """Generate Redis key for test"""
        return f"test_cache:{test_id}"
    
    def _make_stats_key(self) -> str:
        """Generate Redis key for session statistics"""
        return "test_cache:stats"
    
    def get_cached_result(self, test_id: str, app_state_hash: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve cached test result if available.
        
        Args:
            test_id: Unique test identifier
            app_state_hash: Hash of app configuration (version, URL, etc.)
                           If provided, validates that cache is still valid
        
        Returns:
            Cached result dict if found and valid, None otherwise
        """
        if not self._connected or not self.redis_client:
            return None
        
        try:
            key = self._make_cache_key(test_id)
            cached = self.redis_client.get(key)
            
            if cached is None:
                return None
            
            result = json.loads(cached)
            
            # Validate cache is still relevant
            if app_state_hash and result.get('app_state_hash') != app_state_hash:
                logger.debug(f"Cache invalidated for {test_id}: app state changed")
                return None
            
            # Only return if test passed (don't cache failures/errors)
            if result.get('status') == 'passed':
                logger.debug(f"Cache hit for {test_id}: reusing passed result")
                return result
            
            return None
        
        except Exception as e:
            logger.warning(f"Error reading cache for {test_id}: {e}")
            return None
    
    def store_result(
        self,
        test_id: str,
        status: str,  # passed, failed, error
        execution_time_ms: float,
        form_url: str,
        confidence: int = 0,
        oracle_method: str = "heuristic",
        evidence: str = "",
        app_state_hash: Optional[str] = None,
    ) -> bool:
        """
        Store test execution result in cache.
        
        Args:
            test_id: Unique test identifier
            status: Test status (passed, failed, error)
            execution_time_ms: How long the test took
            form_url: URL of the form being tested
            confidence: Confidence score (0-100)
            oracle_method: Which oracle determined the result
            evidence: Why this result was determined
            app_state_hash: Hash for cache invalidation
        
        Returns:
            True if stored, False if cache unavailable
        """
        if not self._connected or not self.redis_client:
            return False
        
        try:
            key = self._make_cache_key(test_id)
            
            result_data = {
                "status": status,
                "execution_time_ms": round(execution_time_ms, 2),
                "last_run": datetime.now().isoformat(),
                "crawler_version": self.crawler_version,
                "form_url": form_url,
                "confidence": confidence,
                "oracle_method": oracle_method,
                "evidence": evidence,
                "app_state_hash": app_state_hash or "",
            }
            
            # Store with TTL
            self.redis_client.setex(
                key,
                self.ttl_seconds,
                json.dumps(result_data)
            )
            
            # Update session statistics
            self._update_stats(status)
            
            logger.debug(f"Cached result for {test_id}: {status}")
            return True
        
        except Exception as e:
            logger.warning(f"Error storing cache for {test_id}: {e}")
            return False
    
    def _update_stats(self, status: str) -> None:
        """Update session-level statistics"""
        try:
            stats_key = self._make_stats_key()
            stats = self.redis_client.get(stats_key)
            
            if stats:
                stats = json.loads(stats)
            else:
                stats = {"total": 0, "passed": 0, "failed": 0, "error": 0}
            
            stats["total"] += 1
            stats[status] = stats.get(status, 0) + 1
            stats["last_updated"] = datetime.now().isoformat()
            
            self.redis_client.setex(
                stats_key,
                self.ttl_seconds,
                json.dumps(stats)
            )
        except Exception as e:
            logger.debug(f"Error updating cache stats: {e}")
    
    def get_session_stats(self) -> Dict:
        """Get cache statistics for current session"""
        if not self._connected or not self.redis_client:
            return {}
        
        try:
            stats_key = self._make_stats_key()
            stats = self.redis_client.get(stats_key)
            return json.loads(stats) if stats else {}
        except Exception:
            return {}
    
    def clear_cache(self, pattern: str = "test_cache:*") -> int:
        """
        Clear cache entries matching pattern.
        
        Args:
            pattern: Redis pattern (default: all test caches)
        
        Returns:
            Number of keys deleted
        """
        if not self._connected or not self.redis_client:
            return 0
        
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                deleted = self.redis_client.delete(*keys)
                logger.info(f"Cleared {deleted} cache entries matching '{pattern}'")
                return deleted
            return 0
        except Exception as e:
            logger.warning(f"Error clearing cache: {e}")
            return 0
    
    def health_check(self) -> bool:
        """Check if Redis connection is healthy"""
        if not self._connected or not self.redis_client:
            return False
        
        try:
            self.redis_client.ping()
            return True
        except Exception:
            return False
    
    def generate_app_state_hash(self, app_config: Dict) -> str:
        """
        Generate a hash representing app configuration/state.
        Used to validate if cached results are still relevant.
        
        Args:
            app_config: Dict with keys like 'base_url', 'version', etc.
        
        Returns:
            SHA256 hash of the config
        """
        config_str = json.dumps(app_config, sort_keys=True)
        return hashlib.sha256(config_str.encode()).hexdigest()[:16]
