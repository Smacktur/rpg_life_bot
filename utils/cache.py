import json
import logging
from typing import Any, Dict, Optional, TypeVar, Generic, Union, Callable
import redis.asyncio as redis
from functools import wraps
import inspect
import asyncio

from config import REDIS_HOST, REDIS_PORT

T = TypeVar('T')

# Initialize Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    decode_responses=True,  # Auto-decode bytes to string
    socket_timeout=5,        # Timeout for socket operations
)

class Cache:
    """Redis-based caching utility"""
    
    @staticmethod
    async def get(key: str) -> Optional[str]:
        """Get value from cache by key"""
        try:
            value = await redis_client.get(key)
            return value
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: Union[str, Dict, list], 
                  expire: int = 3600) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to store (string, dict, or list)
            expire: Expiration time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert complex types to JSON
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
                
            await redis_client.set(key, value, ex=expire)
            return True
        except Exception as e:
            logging.error(f"Redis set error: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            await redis_client.delete(key)
            return True
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
            return False
    
    @staticmethod
    async def exists(key: str) -> bool:
        """Check if key exists in cache"""
        try:
            return bool(await redis_client.exists(key))
        except Exception as e:
            logging.error(f"Redis exists error: {e}")
            return False

# Cache decorator for async functions
def cached(key_prefix: str, ttl: int = 3600):
    """
    Cache decorator for async functions.
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        
    Usage:
        @cached("user:{telegram_id}", 300)
        async def get_user_data(telegram_id: str):
            # Function logic...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get the signature of the function
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Format the key with args and kwargs
            key = key_prefix
            for name, value in bound_args.arguments.items():
                # Only replace the placeholders that exist in the key_prefix
                if f"{{{name}}}" in key:
                    key = key.replace(f"{{{name}}}", str(value))
            
            # Try to get from cache
            cached_value = await Cache.get(key)
            if cached_value:
                try:
                    return json.loads(cached_value)
                except json.JSONDecodeError:
                    return cached_value
            
            # Call the function if not in cache
            result = await func(*args, **kwargs)
            
            # Cache the result
            await Cache.set(key, result, expire=ttl)
            
            return result
        return wrapper
    return decorator 