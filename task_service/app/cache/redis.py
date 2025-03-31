import json
import redis
from typing import Any, Dict, List, Optional, Union
from app.core.config import settings

# Redis client
redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)

def get_cache_key(key_type: str, *args) -> str:
    """Generate a cache key with proper namespacing"""
    return f"task_service:{key_type}:{':'.join(str(arg) for arg in args)}"

async def get_from_cache(key: str) -> Optional[Dict[str, Any]]:
    """Get data from Redis cache"""
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

async def set_in_cache(key: str, data: Dict[str, Any], ttl: int) -> None:
    """Store data in Redis cache with TTL"""
    redis_client.setex(key, ttl, json.dumps(data))

async def delete_from_cache(key: str) -> None:
    """Delete data from Redis cache"""
    redis_client.delete(key)

async def invalidate_user_task_cache(user_id: str) -> None:
    """Invalidate all cache keys for a specific user's tasks"""
    pattern = get_cache_key("tasks", user_id, "*")
    keys = redis_client.keys(pattern)
    if keys:
        redis_client.delete(*keys)

async def cache_task(user_id: str, task_id: str, task_data: Dict[str, Any]) -> None:
    """Cache a single task"""
    key = get_cache_key("tasks", user_id, "task", task_id)
    await set_in_cache(key, task_data, settings.REDIS_TTL_TASKS)

async def cache_task_list(user_id: str, filters: Dict[str, Any], tasks_data: Dict[str, Any]) -> None:
    """Cache a task list with filters"""
    # Create a deterministic key based on filters
    filter_str = json.dumps(filters, sort_keys=True)
    key = get_cache_key("tasks", user_id, "list", hash(filter_str))
    await set_in_cache(key, tasks_data, settings.REDIS_TTL_TASK_LIST)

async def get_cached_task(user_id: str, task_id: str) -> Optional[Dict[str, Any]]:
    """Get a cached task"""
    key = get_cache_key("tasks", user_id, "task", task_id)
    return await get_from_cache(key)

async def get_cached_task_list(user_id: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Get a cached task list based on filters"""
    filter_str = json.dumps(filters, sort_keys=True)
    key = get_cache_key("tasks", user_id, "list", hash(filter_str))
    return await get_from_cache(key)
