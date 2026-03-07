"""
Redis Cache Manager
Distributed caching for AI detection results and site analysis
"""
import redis
import json
import hashlib
from typing import Dict, List, Optional, Any
from app.utils.logger_config import setup_logger

logger = setup_logger(__name__)


class RedisCache:
    """
    Redis-based cache for crawler data
    Provides distributed caching with TTL support
    """
    
    def __init__(
        self, 
        host: str = "127.0.0.1",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        ttl: int = 86400  # 24 hours default
    ):
        """
        Initialize Redis cache
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (if required)
            ttl: Time to live for cache entries in seconds
        """
        self.ttl = ttl
        
        try:
            self.client = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                decode_responses=True,  # Auto-decode bytes to strings
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            self.client.ping()
            logger.info(f"✅ Redis connected: {host}:{port} (db={db})")
            self.enabled = True
            
        except redis.ConnectionError as e:
            logger.info(f"ℹ️  Redis not available (using in-memory cache): {e}")
            self.client = None
            self.enabled = False
            # Fallback to in-memory dict
            self._memory_cache: Dict[str, Any] = {}
        
        except Exception as e:
            logger.error(f"❌ Redis initialization error: {e}")
            self.client = None
            self.enabled = False
            self._memory_cache: Dict[str, Any] = {}
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate Redis key with namespace"""
        # Hash long identifiers to keep keys short
        if len(identifier) > 100:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"crawler:{prefix}:{identifier}"
    
    def get(self, prefix: str, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            prefix: Cache namespace (e.g., 'ai_detection', 'site_analysis')
            key: Cache key
        
        Returns:
            Cached value or None if not found
        """
        redis_key = self._generate_key(prefix, key)
        
        if not self.enabled:
            # Use in-memory fallback
            return self._memory_cache.get(redis_key)
        
        try:
            value = self.client.get(redis_key)
            if value:
                # Deserialize JSON
                return json.loads(value)
            return None
        
        except Exception as e:
            logger.debug(f"Redis get error: {e}")
            return None
    
    def set(self, prefix: str, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            prefix: Cache namespace
            key: Cache key
            value: Value to cache (must be JSON-serializable)
            ttl: Time to live in seconds (overrides default)
        
        Returns:
            True if successful, False otherwise
        """
        redis_key = self._generate_key(prefix, key)
        cache_ttl = ttl or self.ttl
        
        if not self.enabled:
            # Use in-memory fallback
            self._memory_cache[redis_key] = value
            return True
        
        try:
            # Serialize to JSON
            serialized = json.dumps(value)
            
            # Set with TTL
            self.client.setex(redis_key, cache_ttl, serialized)
            return True
        
        except Exception as e:
            logger.debug(f"Redis set error: {e}")
            return False
    
    def exists(self, prefix: str, key: str) -> bool:
        """Check if key exists in cache"""
        redis_key = self._generate_key(prefix, key)
        
        if not self.enabled:
            return redis_key in self._memory_cache
        
        try:
            return self.client.exists(redis_key) > 0
        except Exception as e:
            logger.debug(f"Redis exists error: {e}")
            return False
    
    def delete(self, prefix: str, key: str) -> bool:
        """Delete key from cache"""
        redis_key = self._generate_key(prefix, key)
        
        if not self.enabled:
            if redis_key in self._memory_cache:
                del self._memory_cache[redis_key]
            return True
        
        try:
            self.client.delete(redis_key)
            return True
        except Exception as e:
            logger.debug(f"Redis delete error: {e}")
            return False
    
    def clear_namespace(self, prefix: str) -> int:
        """
        Clear all keys in a namespace
        
        Args:
            prefix: Cache namespace to clear
        
        Returns:
            Number of keys deleted
        """
        if not self.enabled:
            # Clear matching keys from memory cache
            pattern = f"crawler:{prefix}:"
            keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(pattern)]
            for key in keys_to_delete:
                del self._memory_cache[key]
            return len(keys_to_delete)
        
        try:
            pattern = self._generate_key(prefix, "*")
            keys = self.client.keys(pattern)
            
            if keys:
                deleted = self.client.delete(*keys)
                logger.info(f"🗑️  Cleared {deleted} keys from namespace '{prefix}'")
                return deleted
            
            return 0
        
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.enabled:
            return {
                "enabled": False,
                "backend": "memory",
                "keys_cached": len(self._memory_cache)
            }
        
        try:
            info = self.client.info("stats")
            keyspace = self.client.info("keyspace")
            
            # Count crawler keys
            crawler_keys = len(self.client.keys("crawler:*"))
            
            return {
                "enabled": True,
                "backend": "redis",
                "total_keys": crawler_keys,
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(
                    info.get("keyspace_hits", 0),
                    info.get("keyspace_misses", 0)
                ),
                "memory_used": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0)
            }
        
        except Exception as e:
            logger.debug(f"Redis stats error: {e}")
            return {
                "enabled": True,
                "backend": "redis",
                "error": str(e)
            }
    
    def _calculate_hit_rate(self, hits: int, misses: int) -> str:
        """Calculate cache hit rate percentage"""
        total = hits + misses
        if total == 0:
            return "0%"
        
        rate = (hits / total) * 100
        return f"{rate:.1f}%"
    
    def increment(self, prefix: str, key: str, amount: int = 1) -> int:
        """
        Increment a counter
        
        Args:
            prefix: Cache namespace
            key: Counter key
            amount: Amount to increment by
        
        Returns:
            New counter value
        """
        redis_key = self._generate_key(prefix, key)
        
        if not self.enabled:
            current = self._memory_cache.get(redis_key, 0)
            self._memory_cache[redis_key] = current + amount
            return self._memory_cache[redis_key]
        
        try:
            return self.client.incrby(redis_key, amount)
        except Exception as e:
            logger.debug(f"Redis increment error: {e}")
            return 0
    
    def get_counter(self, prefix: str, key: str) -> int:
        """Get counter value"""
        redis_key = self._generate_key(prefix, key)
        
        if not self.enabled:
            return self._memory_cache.get(redis_key, 0)
        
        try:
            value = self.client.get(redis_key)
            return int(value) if value else 0
        except Exception as e:
            logger.debug(f"Redis get counter error: {e}")
            return 0
    
    def close(self):
        """Close Redis connection"""
        if self.client and self.enabled:
            try:
                self.client.close()
                logger.info("✅ Redis connection closed")
            except Exception as e:
                logger.debug(f"Redis close error: {e}")


# Global cache instance
_redis_cache: Optional[RedisCache] = None


def get_redis_cache() -> RedisCache:
    """
    Get global Redis cache instance (singleton pattern)
    
    Returns:
        RedisCache instance
    """
    global _redis_cache
    
    if _redis_cache is None:
        import os
        
        # Get Redis config from environment
        host = os.getenv('REDIS_HOST', '127.0.0.1')
        port = int(os.getenv('REDIS_PORT', '6379'))
        db = int(os.getenv('REDIS_DB', '0'))
        password = os.getenv('REDIS_PASSWORD', None)
        ttl = int(os.getenv('REDIS_TTL', '86400'))  # 24 hours
        
        _redis_cache = RedisCache(
            host=host,
            port=port,
            db=db,
            password=password,
            ttl=ttl
        )
    
    return _redis_cache
