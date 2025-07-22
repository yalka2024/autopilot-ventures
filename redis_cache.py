#!/usr/bin/env python3
"""
Redis Caching System for AutoPilot Ventures Platform
Implements caching for API responses, session management, and performance optimization
"""

import os
import json
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from functools import wraps
import pickle

import redis
from redis.exceptions import RedisError

from config import config
from utils import generate_id, log

# Configure logging
logger = logging.getLogger(__name__)

# Redis Configuration
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
REDIS_DB = int(os.getenv('REDIS_DB', 0))
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', None)
REDIS_SSL = os.getenv('REDIS_SSL', 'false').lower() == 'true'

# Cache Configuration
DEFAULT_CACHE_TTL = 3600  # 1 hour
API_CACHE_TTL = 300      # 5 minutes
SESSION_CACHE_TTL = 86400 # 24 hours
AGENT_CACHE_TTL = 1800   # 30 minutes


class CacheManager:
    """Redis cache manager for performance optimization."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis connection with fallback."""
        try:
            # Create Redis connection
            self.redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                password=REDIS_PASSWORD,
                ssl=REDIS_SSL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True
            )
            
            # Test connection
            self.redis_client.ping()
            logger.info("Redis connection established successfully")
            
        except RedisError as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory fallback.")
            self.redis_client = None
    
    def _get_cache_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix."""
        return f"autopilot:{prefix}:{identifier}"
    
    def _serialize_value(self, value: Any) -> str:
        """Serialize value for Redis storage."""
        try:
            if isinstance(value, (dict, list)):
                return json.dumps(value, default=str)
            elif isinstance(value, (datetime, timedelta)):
                return json.dumps(value.isoformat())
            else:
                return str(value)
        except Exception as e:
            logger.error(f"Serialization failed: {e}")
            return str(value)
    
    def _deserialize_value(self, value: str, value_type: str = 'json') -> Any:
        """Deserialize value from Redis storage."""
        try:
            if value_type == 'json':
                return json.loads(value)
            elif value_type == 'pickle':
                return pickle.loads(value.encode('latin1'))
            else:
                return value
        except Exception as e:
            logger.error(f"Deserialization failed: {e}")
            return value
    
    def set(self, key: str, value: Any, ttl: int = DEFAULT_CACHE_TTL) -> bool:
        """Set value in cache with TTL."""
        try:
            if self.redis_client:
                serialized_value = self._serialize_value(value)
                return self.redis_client.setex(key, ttl, serialized_value)
            return False
        except RedisError as e:
            logger.error(f"Redis set failed: {e}")
            return False
    
    def get(self, key: str, value_type: str = 'json') -> Optional[Any]:
        """Get value from cache."""
        try:
            if self.redis_client:
                value = self.redis_client.get(key)
                if value:
                    return self._deserialize_value(value, value_type)
            return None
        except RedisError as e:
            logger.error(f"Redis get failed: {e}")
            return None
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            if self.redis_client:
                return bool(self.redis_client.delete(key))
            return False
        except RedisError as e:
            logger.error(f"Redis delete failed: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            if self.redis_client:
                return bool(self.redis_client.exists(key))
            return False
        except RedisError as e:
            logger.error(f"Redis exists failed: {e}")
            return False
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration for key."""
        try:
            if self.redis_client:
                return bool(self.redis_client.expire(key, ttl))
            return False
        except RedisError as e:
            logger.error(f"Redis expire failed: {e}")
            return False
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            if self.redis_client:
                keys = self.redis_client.keys(pattern)
                if keys:
                    return self.redis_client.delete(*keys)
            return 0
        except RedisError as e:
            logger.error(f"Redis clear pattern failed: {e}")
            return 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            if self.redis_client:
                info = self.redis_client.info()
                return {
                    'connected': True,
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 0),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0),
                    'uptime': info.get('uptime_in_seconds', 0)
                }
            else:
                return {
                    'connected': False,
                    'error': 'Redis not available'
                }
        except RedisError as e:
            logger.error(f"Redis stats failed: {e}")
            return {
                'connected': False,
                'error': str(e)
            }


class APICache:
    """API response caching system."""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize API cache."""
        self.cache_manager = cache_manager
    
    def cache_response(self, ttl: int = API_CACHE_TTL):
        """Decorator to cache API responses."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Generate cache key from function name and arguments
                cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_response = self.cache_manager.get(cache_key)
                if cached_response:
                    logger.debug(f"Cache hit for {func.__name__}")
                    return cached_response
                
                # Execute function and cache result
                result = await func(*args, **kwargs)
                self.cache_manager.set(cache_key, result, ttl)
                
                logger.debug(f"Cache miss for {func.__name__}, cached result")
                return result
            
            return wrapper
        return decorator
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function name and arguments."""
        # Create a hash of the arguments
        args_str = str(args) + str(sorted(kwargs.items()))
        args_hash = hashlib.md5(args_str.encode()).hexdigest()
        
        return self.cache_manager._get_cache_key('api', f"{func_name}:{args_hash}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern."""
        return self.cache_manager.clear_pattern(f"autopilot:api:{pattern}")


class SessionCache:
    """Session management with Redis."""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize session cache."""
        self.cache_manager = cache_manager
    
    def store_session(self, session_id: str, session_data: Dict[str, Any]) -> bool:
        """Store session data."""
        key = self.cache_manager._get_cache_key('session', session_id)
        return self.cache_manager.set(key, session_data, SESSION_CACHE_TTL)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        key = self.cache_manager._get_cache_key('session', session_id)
        return self.cache_manager.get(key)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete session data."""
        key = self.cache_manager._get_cache_key('session', session_id)
        return self.cache_manager.delete(key)
    
    def refresh_session(self, session_id: str) -> bool:
        """Refresh session TTL."""
        key = self.cache_manager._get_cache_key('session', session_id)
        return self.cache_manager.expire(key, SESSION_CACHE_TTL)


class AgentCache:
    """Agent-specific caching system."""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize agent cache."""
        self.cache_manager = cache_manager
    
    def cache_agent_result(self, agent_id: str, task_id: str, result: Any) -> bool:
        """Cache agent execution result."""
        key = self.cache_manager._get_cache_key('agent_result', f"{agent_id}:{task_id}")
        return self.cache_manager.set(key, result, AGENT_CACHE_TTL)
    
    def get_agent_result(self, agent_id: str, task_id: str) -> Optional[Any]:
        """Get cached agent result."""
        key = self.cache_manager._get_cache_key('agent_result', f"{agent_id}:{task_id}")
        return self.cache_manager.get(key)
    
    def cache_agent_context(self, agent_id: str, context: Dict[str, Any]) -> bool:
        """Cache agent context for reuse."""
        key = self.cache_manager._get_cache_key('agent_context', agent_id)
        return self.cache_manager.set(key, context, AGENT_CACHE_TTL)
    
    def get_agent_context(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get cached agent context."""
        key = self.cache_manager._get_cache_key('agent_context', agent_id)
        return self.cache_manager.get(key)
    
    def invalidate_agent_cache(self, agent_id: str) -> int:
        """Invalidate all cache entries for an agent."""
        pattern = f"autopilot:agent_*:{agent_id}*"
        return self.cache_manager.clear_pattern(pattern)


class StartupCache:
    """Startup-specific caching system."""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize startup cache."""
        self.cache_manager = cache_manager
    
    def cache_startup_data(self, startup_id: str, data: Dict[str, Any]) -> bool:
        """Cache startup data."""
        key = self.cache_manager._get_cache_key('startup', startup_id)
        return self.cache_manager.set(key, data, DEFAULT_CACHE_TTL)
    
    def get_startup_data(self, startup_id: str) -> Optional[Dict[str, Any]]:
        """Get cached startup data."""
        key = self.cache_manager._get_cache_key('startup', startup_id)
        return self.cache_manager.get(key)
    
    def cache_startup_metrics(self, startup_id: str, metrics: Dict[str, Any]) -> bool:
        """Cache startup metrics."""
        key = self.cache_manager._get_cache_key('startup_metrics', startup_id)
        return self.cache_manager.set(key, metrics, DEFAULT_CACHE_TTL)
    
    def get_startup_metrics(self, startup_id: str) -> Optional[Dict[str, Any]]:
        """Get cached startup metrics."""
        key = self.cache_manager._get_cache_key('startup_metrics', startup_id)
        return self.cache_manager.get(key)
    
    def invalidate_startup_cache(self, startup_id: str) -> int:
        """Invalidate all cache entries for a startup."""
        pattern = f"autopilot:startup*:{startup_id}*"
        return self.cache_manager.clear_pattern(pattern)


class PerformanceCache:
    """Performance optimization caching."""
    
    def __init__(self, cache_manager: CacheManager):
        """Initialize performance cache."""
        self.cache_manager = cache_manager
    
    def cache_api_response(self, endpoint: str, params: Dict[str, Any], response: Any) -> bool:
        """Cache API response."""
        # Create hash of endpoint and parameters
        params_str = json.dumps(params, sort_keys=True)
        cache_key = hashlib.md5(f"{endpoint}:{params_str}".encode()).hexdigest()
        key = self.cache_manager._get_cache_key('api_response', cache_key)
        
        return self.cache_manager.set(key, response, API_CACHE_TTL)
    
    def get_cached_response(self, endpoint: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached API response."""
        params_str = json.dumps(params, sort_keys=True)
        cache_key = hashlib.md5(f"{endpoint}:{params_str}".encode()).hexdigest()
        key = self.cache_manager._get_cache_key('api_response', cache_key)
        
        return self.cache_manager.get(key)
    
    def cache_database_query(self, query_hash: str, result: Any) -> bool:
        """Cache database query result."""
        key = self.cache_manager._get_cache_key('db_query', query_hash)
        return self.cache_manager.set(key, result, DEFAULT_CACHE_TTL)
    
    def get_cached_query(self, query_hash: str) -> Optional[Any]:
        """Get cached database query result."""
        key = self.cache_manager._get_cache_key('db_query', query_hash)
        return self.cache_manager.get(key)
    
    def cache_external_api(self, api_name: str, params: Dict[str, Any], response: Any) -> bool:
        """Cache external API responses."""
        params_str = json.dumps(params, sort_keys=True)
        cache_key = hashlib.md5(f"{api_name}:{params_str}".encode()).hexdigest()
        key = self.cache_manager._get_cache_key('external_api', cache_key)
        
        return self.cache_manager.set(key, response, API_CACHE_TTL)
    
    def get_cached_external_api(self, api_name: str, params: Dict[str, Any]) -> Optional[Any]:
        """Get cached external API response."""
        params_str = json.dumps(params, sort_keys=True)
        cache_key = hashlib.md5(f"{api_name}:{params_str}".encode()).hexdigest()
        key = self.cache_manager._get_cache_key('external_api', cache_key)
        
        return self.cache_manager.get(key)


# Global cache manager instance
cache_manager = CacheManager()

# Specialized cache instances
api_cache = APICache(cache_manager)
session_cache = SessionCache(cache_manager)
agent_cache = AgentCache(cache_manager)
startup_cache = StartupCache(cache_manager)
performance_cache = PerformanceCache(cache_manager)


# Cache decorators for easy use
def cache_api_response(ttl: int = API_CACHE_TTL):
    """Decorator to cache API responses."""
    return api_cache.cache_response(ttl)


def cache_agent_result(agent_id: str, task_id: str):
    """Decorator to cache agent results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get from cache first
            cached_result = agent_cache.get_agent_result(agent_id, task_id)
            if cached_result:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            agent_cache.cache_agent_result(agent_id, task_id, result)
            
            return result
        return wrapper
    return decorator


def cache_startup_data(startup_id: str):
    """Decorator to cache startup data."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Try to get from cache first
            cached_data = startup_cache.get_startup_data(startup_id)
            if cached_data:
                return cached_data
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            startup_cache.cache_startup_data(startup_id, result)
            
            return result
        return wrapper
    return decorator


# Cache management functions
def clear_all_caches() -> Dict[str, int]:
    """Clear all caches and return counts."""
    patterns = [
        "autopilot:api:*",
        "autopilot:session:*",
        "autopilot:agent_*:*",
        "autopilot:startup*:*",
        "autopilot:db_query:*",
        "autopilot:external_api:*"
    ]
    
    results = {}
    for pattern in patterns:
        count = cache_manager.clear_pattern(pattern)
        results[pattern] = count
    
    return results


def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    redis_stats = cache_manager.get_stats()
    
    return {
        'redis': redis_stats,
        'cache_types': {
            'api_cache': 'API response caching',
            'session_cache': 'User session management',
            'agent_cache': 'Agent result caching',
            'startup_cache': 'Startup data caching',
            'performance_cache': 'Performance optimization'
        },
        'ttl_settings': {
            'default': DEFAULT_CACHE_TTL,
            'api': API_CACHE_TTL,
            'session': SESSION_CACHE_TTL,
            'agent': AGENT_CACHE_TTL
        }
    } 