"""Redis caching layer for Risk Intelligence Agent.

This module provides caching functionality to reduce latency for repeated
evaluations of the same MSME.

**Validates Requirements**: 15.1, 15.2, 15.3, 15.4, 15.5, 15.6, 15.7, 15.8, 15.9
"""

import hashlib
import json
from typing import Optional, Any
from datetime import datetime


def generate_cache_key(gstin: str, pan: str, data_timestamps: dict) -> str:
    """Generate SHA-256 cache key from input identifiers.
    
    Args:
        gstin: GSTIN identifier
        pan: PAN identifier
        data_timestamps: Dictionary of data source timestamps
        
    Returns:
        SHA-256 hash string as cache key
    """
    # Create canonical string for hashing
    canonical = f"{gstin}|{pan}|{json.dumps(data_timestamps, sort_keys=True)}"
    
    # Generate SHA-256 hash
    hash_obj = hashlib.sha256(canonical.encode('utf-8'))
    return hash_obj.hexdigest()


class RiskCache:
    """Redis-based caching for risk assessment components.
    
    Caches validated data, feature vectors, and predictions with
    appropriate TTLs for each data source type.
    """
    
    def __init__(self, redis_client: Optional[Any] = None):
        """Initialize cache with Redis client.
        
        Args:
            redis_client: Redis client instance (optional, uses mock if None)
        """
        self.redis_client = redis_client
        self.memory_cache = {}  # Fallback in-memory cache
        self.use_redis = redis_client is not None
        
        # Cache hit/miss tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.total_requests = 0
    
    def _get_from_storage(self, key: str) -> Optional[str]:
        """Get value from storage backend.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value as JSON string, or None if not found
        """
        try:
            if self.use_redis:
                return self.redis_client.get(key)
            else:
                return self.memory_cache.get(key)
        except Exception as e:
            print(f"Cache retrieval failed: {e}")
            return None
    
    def _set_in_storage(self, key: str, value: str, ttl_seconds: int) -> bool:
        """Set value in storage backend with TTL.
        
        Args:
            key: Cache key
            value: Value to cache (JSON string)
            ttl_seconds: Time-to-live in seconds
            
        Returns:
            True if set successfully, False otherwise
        """
        try:
            if self.use_redis:
                self.redis_client.setex(key, ttl_seconds, value)
            else:
                # Simple in-memory cache (no TTL enforcement)
                self.memory_cache[key] = value
            return True
        except Exception as e:
            print(f"Cache write failed: {e}")
            return False
    
    def cache_validated_data(self, cache_key: str, validated_data: Any) -> bool:
        """Cache validated data with 24h TTL.
        
        Args:
            cache_key: Cache key
            validated_data: ValidatedData object
            
        Returns:
            True if cached successfully
        """
        ttl_seconds = 24 * 60 * 60  # 24 hours
        
        try:
            # Convert to JSON
            value = validated_data.json() if hasattr(validated_data, 'json') else json.dumps(validated_data)
            return self._set_in_storage(f"validated:{cache_key}", value, ttl_seconds)
        except Exception as e:
            print(f"Failed to cache validated data: {e}")
            return False
    
    def get_cached_validated_data(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached validated data.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Validated data dict or None
        """
        self.total_requests += 1
        
        value = self._get_from_storage(f"validated:{cache_key}")
        if value:
            self.cache_hits += 1
            try:
                return json.loads(value) if isinstance(value, str) else value
            except Exception as e:
                print(f"Failed to deserialize cached data: {e}")
                return None
        else:
            self.cache_misses += 1
            return None
    
    def cache_feature_vector(self, cache_key: str, feature_vector: Any) -> bool:
        """Cache feature vector with 1h TTL.
        
        Args:
            cache_key: Cache key
            feature_vector: FeatureVector object
            
        Returns:
            True if cached successfully
        """
        ttl_seconds = 60 * 60  # 1 hour
        
        try:
            value = feature_vector.json() if hasattr(feature_vector, 'json') else json.dumps(feature_vector)
            return self._set_in_storage(f"features:{cache_key}", value, ttl_seconds)
        except Exception as e:
            print(f"Failed to cache feature vector: {e}")
            return False
    
    def get_cached_feature_vector(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached feature vector.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Feature vector dict or None
        """
        self.total_requests += 1
        
        value = self._get_from_storage(f"features:{cache_key}")
        if value:
            self.cache_hits += 1
            try:
                return json.loads(value) if isinstance(value, str) else value
            except Exception as e:
                print(f"Failed to deserialize cached features: {e}")
                return None
        else:
            self.cache_misses += 1
            return None
    
    def cache_prediction(self, cache_key: str, prediction: Any) -> bool:
        """Cache risk prediction with 1h TTL.
        
        Args:
            cache_key: Cache key
            prediction: RiskPrediction object
            
        Returns:
            True if cached successfully
        """
        ttl_seconds = 60 * 60  # 1 hour
        
        try:
            value = prediction.json() if hasattr(prediction, 'json') else json.dumps(prediction)
            return self._set_in_storage(f"prediction:{cache_key}", value, ttl_seconds)
        except Exception as e:
            print(f"Failed to cache prediction: {e}")
            return False
    
    def get_cached_prediction(self, cache_key: str) -> Optional[dict]:
        """Retrieve cached prediction.
        
        Args:
            cache_key: Cache key
            
        Returns:
            Prediction dict or None
        """
        self.total_requests += 1
        
        value = self._get_from_storage(f"prediction:{cache_key}")
        if value:
            self.cache_hits += 1
            try:
                return json.loads(value) if isinstance(value, str) else value
            except Exception as e:
                print(f"Failed to deserialize cached prediction: {e}")
                return None
        else:
            self.cache_misses += 1
            return None
    
    def get_cache_metrics(self) -> dict:
        """Get cache performance metrics.
        
        Returns:
            Dictionary with hit rate, total requests, and cache size
        """
        hit_rate = (self.cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0.0
        
        return {
            "hit_rate_percentage": round(hit_rate, 2),
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "total_requests": self.total_requests,
            "cache_size": len(self.memory_cache) if not self.use_redis else "N/A (Redis)"
        }
    
    def log_cache_metrics(self) -> None:
        """Log cache metrics (called hourly)."""
        metrics = self.get_cache_metrics()
        print(f"Cache Metrics: {json.dumps(metrics)}")


# Global cache instance
_cache: Optional[RiskCache] = None


def get_cache() -> RiskCache:
    """Get global cache instance.
    
    Returns:
        RiskCache instance
    """
    global _cache
    if _cache is None:
        _cache = RiskCache()
    return _cache


def initialize_cache(redis_client: Optional[Any] = None) -> RiskCache:
    """Initialize cache with Redis client.
    
    Args:
        redis_client: Redis client instance
        
    Returns:
        Initialized RiskCache
    """
    global _cache
    _cache = RiskCache(redis_client)
    return _cache
