"""
Caching utilities for Agentic Analytics Studio.

Provides simple in-memory caching for expensive operations like
Tableau metadata requests and LLM responses.
"""

from functools import lru_cache, wraps
from typing import Any, Callable, Optional
import time
import hashlib
import json


class SimpleCache:
    """
    Simple in-memory cache with TTL support.
    
    Useful for caching API responses, database queries, and expensive computations.
    """
    
    def __init__(self, ttl: int = 300):
        """
        Initialize cache.
        
        Args:
            ttl: Time-to-live in seconds (default: 5 minutes)
        """
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache if not expired.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value or None if expired/missing
        """
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.timestamps[key] > self.ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
        """
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
        self.timestamps.clear()
    
    def size(self) -> int:
        """Return number of cached items."""
        return len(self.cache)


# Global cache instances
_tableau_cache = SimpleCache(ttl=600)  # 10 minutes for Tableau metadata
_llm_cache = SimpleCache(ttl=3600)  # 1 hour for LLM responses


def cached_tableau(func: Callable) -> Callable:
    """
    Decorator to cache Tableau API responses.
    
    Usage:
        @cached_tableau
        def get_tableau_metadata(viz_url):
            # Expensive Tableau API call
            return metadata
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key_data = {
            'func': func.__name__,
            'args': args,
            'kwargs': kwargs
        }
        key = hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()
        
        # Try cache first
        cached_value = _tableau_cache.get(key)
        if cached_value is not None:
            return cached_value
        
        # Call function and cache result
        result = func(*args, **kwargs)
        _tableau_cache.set(key, result)
        return result
    
    return wrapper


def cached_llm(func: Callable) -> Callable:
    """
    Decorator to cache LLM responses.
    
    Usage:
        @cached_llm
        def generate_rationale(prompt):
            # Expensive LLM API call
            return response
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        key_data = {
            'func': func.__name__,
            'args': args,
            'kwargs': kwargs
        }
        key = hashlib.md5(json.dumps(key_data, sort_keys=True, default=str).encode()).hexdigest()
        
        # Try cache first
        cached_value = _llm_cache.get(key)
        if cached_value is not None:
            return cached_value
        
        # Call function and cache result
        result = func(*args, **kwargs)
        _llm_cache.set(key, result)
        return result
    
    return wrapper


def clear_all_caches() -> None:
    """Clear all caches."""
    _tableau_cache.clear()
    _llm_cache.clear()


def get_cache_stats() -> dict:
    """
    Get cache statistics.
    
    Returns:
        Dictionary with cache sizes
    """
    return {
        'tableau_cache_size': _tableau_cache.size(),
        'llm_cache_size': _llm_cache.size()
    }


# Example usage
if __name__ == "__main__":
    # Test cache
    cache = SimpleCache(ttl=5)
    
    cache.set("test_key", "test_value")
    print(f"Cached: {cache.get('test_key')}")
    
    time.sleep(6)
    print(f"After TTL: {cache.get('test_key')}")  # Should be None
