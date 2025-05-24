from typing import Any, Callable, Optional, Type, TypeVar, Generic
from trader_app.utils.redis_client import RedisClient
from trader_app.utils import redis_schema
from pydantic import BaseModel
import logging

T = TypeVar('T', bound=BaseModel)

class BaseCachingService(Generic[T]):
    """
    Base class for cache-first service logic using Redis and Pydantic models.
    Subclasses should specify the model type and use cache_first for cache-backed fetches.
    
    Args:
        redis_client (RedisClient, optional): Custom Redis client for testing or advanced use.
    """
    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis_client = redis_client or RedisClient()

    def get_from_cache(
        self,
        key_type: redis_schema.RedisKeyType,
        params: dict,
        model: Type[T],
        is_list: bool = False
    ) -> Optional[Any]:
        """
        Attempt to fetch and deserialize a value from Redis cache.
        Returns None if not found or on error.
        """
        key = redis_schema.get_key(key_type, params)
        try:
            value = self.redis_client.get_client().get(key)
            if value is None:
                return None
            return redis_schema.deserialize_model(model, value)
        except Exception as e:
            logging.warning(f"Redis cache get failed for key {key}: {e}")
            return None

    def set_cache(
        self,
        key_type: redis_schema.RedisKeyType,
        params: dict,
        value: Any,
        is_list: bool = False
    ) -> None:
        """
        Serialize and store a value in Redis with appropriate TTL.
        Logs and skips on error.
        """
        key = redis_schema.get_key(key_type, params)
        ttl = redis_schema.get_ttl_for_key(key_type)
        try:
            serialized = redis_schema.serialize_model(value)
            self.redis_client.get_client().setex(key, ttl, serialized)
        except Exception as e:
            logging.warning(f"Redis cache set failed for key {key}: {e}")

    def cache_first(
        self,
        key_type: redis_schema.RedisKeyType,
        params: dict,
        model: Type[T],
        fetch_source: Callable[[], Any],
        is_list: bool = False
    ) -> Any:
        """
        Implements the cache-first pattern: check cache, else fetch from source and cache.
        Args:
            key_type: RedisKeyType for key generation
            params: dict of key parameters
            model: Pydantic model class for deserialization
            fetch_source: Callable that fetches data from the source (e.g., API)
            is_list: If True, expects a list of models
        Returns:
            The cached or freshly fetched data, or None if not found
        """
        cached = self.get_from_cache(key_type, params, model, is_list)
        if cached is not None:
            return cached
        data = fetch_source()
        if data is not None:
            self.set_cache(key_type, params, data, is_list)
        return data 