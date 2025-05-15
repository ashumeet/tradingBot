"""
Redis Client Module

This module provides the RedisClient class for connecting to and interacting with Redis.
It implements connection pooling, error handling, and a singleton pattern.
"""

import json
import time
import redis
from redis.exceptions import (
    ConnectionError,
    TimeoutError,
    RedisError
)
from typing import Any, Dict, Optional, Union, TypeVar, List
import logging
from ..config import config

# Type variable for generic return types
T = TypeVar('T')

# Setup logging
logger = logging.getLogger(__name__)

class RedisClient:
    """
    Redis client with connection pooling and error handling.
    
    This class implements the singleton pattern to ensure only one instance
    of the Redis client is created across the application.
    """
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        """
        Implement singleton pattern to ensure only one Redis client instance.
        """
        if cls._instance is None:
            cls._instance = super(RedisClient, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, host: str = None, port: int = None, 
                 password: str = None, db: int = 0,
                 max_connections: int = 10, 
                 socket_timeout: int = 5,
                 socket_connect_timeout: int = 5,
                 retry_on_timeout: bool = True,
                 max_retries: int = 3):
        """
        Initialize the Redis client with connection parameters.
        
        Args:
            host: Redis server host (default: from config)
            port: Redis server port (default: from config)
            password: Redis server password (default: from config)
            db: Redis database number (default: 0)
            max_connections: Maximum connections in the connection pool (default: 10)
            socket_timeout: Socket timeout in seconds (default: 5)
            socket_connect_timeout: Socket connection timeout in seconds (default: 5)
            retry_on_timeout: Whether to retry on timeout (default: True)
            max_retries: Maximum number of retry attempts (default: 3)
        """
        # Skip re-initialization if already initialized (singleton pattern)
        if self._initialized:
            return
        
        # Use provided parameters or load from config
        self.host = host or config.REDIS_HOST
        self.port = port or config.REDIS_PORT
        self.password = password or config.REDIS_PASSWORD
        self.db = db
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.max_retries = max_retries
        
        # Connection pool and client instance
        self._connection_pool = None
        self._client = None
        self._backoff_factor = 0.5  # Initial backoff in seconds
        self._max_backoff = 30      # Maximum backoff in seconds
        
        # Initialize the connection
        self._create_connection_pool()
        self._initialized = True
    
    def _create_connection_pool(self) -> None:
        """
        Create a Redis connection pool with configured parameters.
        """
        try:
            self._connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout,
                decode_responses=True  # Always decode responses to strings
            )
            logger.info(f"Redis connection pool created for {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {str(e)}")
            raise
    
    def _get_client(self) -> redis.Redis:
        """
        Get a Redis client from the connection pool.
        
        Returns:
            redis.Redis: Connected Redis client
        """
        if not self._client:
            try:
                self._client = redis.Redis(connection_pool=self._connection_pool)
                # Test the connection
                self._client.ping()
                logger.debug("Redis client connected successfully")
            except (ConnectionError, TimeoutError) as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                self._client = None
                raise
        return self._client
    
    def _handle_connection_error(self, operation: str, retry_count: int) -> float:
        """
        Handle connection errors with exponential backoff.
        
        Args:
            operation: The operation that failed
            retry_count: Current retry attempt
            
        Returns:
            float: Time to wait before retrying (in seconds)
        """
        # Calculate backoff with exponential increase and jitter
        backoff = min(self._max_backoff, self._backoff_factor * (2 ** retry_count))
        jitter = backoff * 0.1  # 10% jitter
        wait_time = backoff + (jitter * (2 * (time.time() % 1) - 1))
        
        logger.warning(
            f"Redis {operation} failed. Retrying in {wait_time:.2f}s "
            f"(attempt {retry_count}/{self.max_retries})"
        )
        return wait_time
    
    def _execute_with_retry(self, operation_name: str, operation: callable, *args, **kwargs) -> Any:
        """
        Execute a Redis operation with retry logic.
        
        Args:
            operation_name: Name of the operation for logging
            operation: The function to execute
            *args: Arguments to pass to the operation
            **kwargs: Keyword arguments to pass to the operation
            
        Returns:
            Any: Result of the operation
        
        Raises:
            RedisError: If the operation fails after all retries
        """
        retry_count = 0
        last_error = None
        
        while retry_count <= self.max_retries:
            try:
                client = self._get_client()
                return operation(client, *args, **kwargs)
                
            except (ConnectionError, TimeoutError) as e:
                last_error = e
                retry_count += 1
                
                if retry_count > self.max_retries:
                    break
                
                # Reset client on connection errors
                self._client = None
                
                # Wait before retrying
                wait_time = self._handle_connection_error(operation_name, retry_count)
                time.sleep(wait_time)
                
            except RedisError as e:
                logger.error(f"Redis {operation_name} operation failed: {str(e)}")
                last_error = e
                break
        
        logger.error(f"Redis {operation_name} failed after {retry_count} retries: {str(last_error)}")
        raise last_error or RedisError(f"Redis {operation_name} operation failed")
    
    # Basic Redis operations with error handling and retry logic
    
    def ping(self) -> bool:
        """
        Ping the Redis server to check connectivity.
        
        Returns:
            bool: True if successful, raises an exception otherwise
        """
        try:
            result = self._execute_with_retry("ping", lambda client: client.ping())
            return result
        except Exception:
            return False
    
    def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """
        Set a key-value pair in Redis.
        
        Args:
            key: The key to set
            value: The value to set
            ex: Optional expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        return self._execute_with_retry(
            "set",
            lambda client: client.set(key, value, ex=ex)
        )
    
    def get(self, key: str) -> Optional[str]:
        """
        Get a value from Redis by key.
        
        Args:
            key: The key to retrieve
            
        Returns:
            Optional[str]: The value or None if key doesn't exist
        """
        return self._execute_with_retry(
            "get",
            lambda client: client.get(key)
        )
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from Redis.
        
        Args:
            key: The key to delete
            
        Returns:
            bool: True if deleted, False if key doesn't exist
        """
        result = self._execute_with_retry(
            "delete",
            lambda client: client.delete(key)
        )
        return result > 0
    
    def exists(self, key: str) -> bool:
        """
        Check if a key exists in Redis.
        
        Args:
            key: The key to check
            
        Returns:
            bool: True if key exists, False otherwise
        """
        result = self._execute_with_retry(
            "exists", 
            lambda client: client.exists(key)
        )
        return result > 0
    
    def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration time on a key.
        
        Args:
            key: The key to set expiration on
            seconds: Expiration time in seconds
            
        Returns:
            bool: True if successful, False if key doesn't exist
        """
        return self._execute_with_retry(
            "expire",
            lambda client: client.expire(key, seconds)
        )
    
    def ttl(self, key: str) -> int:
        """
        Get the time-to-live for a key.
        
        Args:
            key: The key to check
            
        Returns:
            int: TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        return self._execute_with_retry(
            "ttl",
            lambda client: client.ttl(key)
        )
    
    # JSON operations
    
    def set_json(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """
        Set a JSON-serializable object in Redis.
        
        Args:
            key: The key to set
            value: JSON-serializable object
            ex: Optional expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            json_value = json.dumps(value)
            return self.set(key, json_value, ex)
        except (TypeError, ValueError) as e:
            logger.error(f"Failed to serialize object for key {key}: {str(e)}")
            raise
    
    def get_json(self, key: str, default: Optional[T] = None) -> Union[Dict, List, T]:
        """
        Get a JSON object from Redis by key.
        
        Args:
            key: The key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            Union[Dict, List, T]: Deserialized JSON object or default
        """
        value = self.get(key)
        if value is None:
            return default
        
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to deserialize value for key {key}: {str(e)}")
            return default
    
    # Hash operations
    
    def hset(self, name: str, key: str, value: str) -> bool:
        """
        Set a hash field to a value.
        
        Args:
            name: Hash name
            key: Field name
            value: Field value
            
        Returns:
            bool: True if successful
        """
        return self._execute_with_retry(
            "hset",
            lambda client: client.hset(name, key, value)
        ) > 0
    
    def hget(self, name: str, key: str) -> Optional[str]:
        """
        Get the value of a hash field.
        
        Args:
            name: Hash name
            key: Field name
            
        Returns:
            Optional[str]: Field value or None if doesn't exist
        """
        return self._execute_with_retry(
            "hget",
            lambda client: client.hget(name, key)
        )
    
    def hgetall(self, name: str) -> Dict[str, str]:
        """
        Get all fields and values in a hash.
        
        Args:
            name: Hash name
            
        Returns:
            Dict[str, str]: Dictionary of field-value pairs
        """
        return self._execute_with_retry(
            "hgetall",
            lambda client: client.hgetall(name)
        )
    
    def hdel(self, name: str, *keys: str) -> int:
        """
        Delete one or more hash fields.
        
        Args:
            name: Hash name
            *keys: Field names to delete
            
        Returns:
            int: Number of fields that were deleted
        """
        return self._execute_with_retry(
            "hdel",
            lambda client: client.hdel(name, *keys)
        )
    
    # List operations
    
    def lpush(self, name: str, *values: str) -> int:
        """
        Prepend values to a list.
        
        Args:
            name: List name
            *values: Values to prepend
            
        Returns:
            int: Length of the list after operation
        """
        return self._execute_with_retry(
            "lpush",
            lambda client: client.lpush(name, *values)
        )
    
    def rpush(self, name: str, *values: str) -> int:
        """
        Append values to a list.
        
        Args:
            name: List name
            *values: Values to append
            
        Returns:
            int: Length of the list after operation
        """
        return self._execute_with_retry(
            "rpush",
            lambda client: client.rpush(name, *values)
        )
    
    def lrange(self, name: str, start: int, end: int) -> List[str]:
        """
        Get a range of elements from a list.
        
        Args:
            name: List name
            start: Start index
            end: End index
            
        Returns:
            List[str]: List of values
        """
        return self._execute_with_retry(
            "lrange",
            lambda client: client.lrange(name, start, end)
        )
    
    def ltrim(self, name: str, start: int, end: int) -> bool:
        """
        Trim a list to the specified range.
        
        Args:
            name: List name
            start: Start index
            end: End index
            
        Returns:
            bool: True if successful
        """
        return self._execute_with_retry(
            "ltrim",
            lambda client: client.ltrim(name, start, end)
        )
    
    def llen(self, name: str) -> int:
        """
        Get the length of a list.
        
        Args:
            name: List name
            
        Returns:
            int: Length of the list
        """
        return self._execute_with_retry(
            "llen",
            lambda client: client.llen(name)
        )
    
    # Utility methods
    
    def add_to_list_limited(self, name: str, value: str, max_items: int = 100) -> int:
        """
        Add an item to a list and limit its size.
        
        Args:
            name: List name
            value: Value to add
            max_items: Maximum number of items to keep
            
        Returns:
            int: Length of the list after operation
        """
        pipeline = self._execute_with_retry(
            "pipeline",
            lambda client: client.pipeline()
        )
        
        try:
            pipeline.lpush(name, value)
            pipeline.ltrim(name, 0, max_items - 1)
            results = pipeline.execute()
            return results[0]  # Return list length
        except RedisError as e:
            logger.error(f"Failed to add item to limited list {name}: {str(e)}")
            raise
    
    def clear_cache(self, pattern: str = "*") -> int:
        """
        Clear cache entries matching a pattern.
        
        Args:
            pattern: Pattern to match keys (default: "*" to match all keys)
            
        Returns:
            int: Number of keys deleted
        """
        keys = self._execute_with_retry(
            "keys",
            lambda client: client.keys(pattern)
        )
        
        if not keys:
            return 0
        
        return self._execute_with_retry(
            "delete",
            lambda client: client.delete(*keys)
        )

# Create a default Redis client instance
# This can be imported and used directly: from utils.redis_client import redis_client
redis_client = RedisClient()

def get_redis_client() -> RedisClient:
    """
    Get the singleton Redis client instance.
    
    Returns:
        RedisClient: The Redis client instance
    """
    return redis_client 