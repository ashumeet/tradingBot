"""
Redis Client Module for trader_app

Provides a singleton RedisClient with connection pooling and error handling.
Configuration is loaded from trader_app.core.config.
"""

import json
import time
import redis
from redis.exceptions import ConnectionError, TimeoutError, RedisError
from typing import Any, Dict, Optional, Union, TypeVar, List
import logging
from trader_app.core import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_DB

T = TypeVar('T')
logger = logging.getLogger("trader_app.utils.redis_client")

class RedisClient:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    def __init__(self, host: str = None, port: int = None, password: str = None, db: int = None,
                 max_connections: int = 10, socket_timeout: int = 5, socket_connect_timeout: int = 5,
                 retry_on_timeout: bool = True, max_retries: int = 3):
        if self._initialized:
            return
        self.host = host or REDIS_HOST
        self.port = port or REDIS_PORT
        self.password = password or REDIS_PASSWORD
        self.db = db if db is not None else REDIS_DB
        self.max_connections = max_connections
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.retry_on_timeout = retry_on_timeout
        self.max_retries = max_retries
        self._connection_pool = None
        self._client = None
        self._backoff_factor = 0.5
        self._max_backoff = 30
        self._create_connection_pool()
        self._initialized = True
    def _create_connection_pool(self) -> None:
        try:
            self._connection_pool = redis.ConnectionPool(
                host=self.host,
                port=self.port,
                password=self.password,
                db=self.db,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout,
                retry_on_timeout=self.retry_on_timeout
            )
            self._client = redis.Redis(connection_pool=self._connection_pool)
        except Exception as e:
            logger.error(f"Failed to create Redis connection pool: {e}")
            raise
    def get_client(self):
        return self._client
    # Add more methods as needed for get/set/delete, with retry and error handling
