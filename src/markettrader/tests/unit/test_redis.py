"""
Tests for the Redis client and schema modules.

These tests verify the functionality of the Redis client connection,
operations, and schema definitions.
"""

import unittest
import fakeredis
import json
import time
from unittest.mock import patch, MagicMock

from src.markettrader.utils.redis_client import RedisClient, redis_client
from src.markettrader.utils.redis_schema import (
    KeyPrefix, TTL, get_key, get_ttl_for_key, get_key_schema
)
from redis.exceptions import ConnectionError


class TestRedisSchema(unittest.TestCase):
    """Test cases for Redis schema module."""
    
    def test_key_generation(self):
        """Test key generation with different parameters."""
        # Test with two parts
        key = get_key(KeyPrefix.MARKET_DATA, "ticker")
        self.assertEqual(key, "market_data:ticker")
        
        # Test with identifier
        key = get_key(KeyPrefix.MARKET_DATA, "ticker", "AAPL")
        self.assertEqual(key, "market_data:ticker:AAPL")
    
    def test_ttl_lookup(self):
        """Test TTL lookup for different key patterns."""
        # Test exact match
        ttl = get_ttl_for_key("settings:app")
        self.assertEqual(ttl, TTL.NONE)
        
        # Test pattern match
        ttl = get_ttl_for_key("market_data:ticker:AAPL")
        self.assertEqual(ttl, TTL.SHORT)
        
        # Test no match
        ttl = get_ttl_for_key("unknown:key")
        self.assertEqual(ttl, TTL.NONE)  # Default to no expiration
    
    def test_schema_lookup(self):
        """Test schema lookup for different key patterns."""
        # Test exact match
        schema = get_key_schema("settings")
        self.assertEqual(schema["type"], "hash")
        self.assertIn("fields", schema)
        
        # Test prefix match
        schema = get_key_schema("market_data:ticker")
        self.assertEqual(schema["type"], "hash")
        self.assertIn("fields", schema)
        
        # Test no match
        schema = get_key_schema("unknown:key")
        self.assertEqual(schema, {})


class TestRedisClient(unittest.TestCase):
    """Test cases for Redis client module using fakeredis."""
    
    def setUp(self):
        """Set up fake Redis server for testing."""
        # Patch redis.Redis with fakeredis.FakeRedis
        self.patcher = patch('redis.Redis', fakeredis.FakeRedis)
        self.patcher.start()
        
        # Reset singleton instance
        RedisClient._instance = None
        self.redis_client = RedisClient(
            host="localhost",
            port=6379,
            password="",
            db=0
        )
    
    def tearDown(self):
        """Clean up after tests."""
        self.patcher.stop()
    
    def test_singleton_pattern(self):
        """Test that RedisClient implements singleton pattern."""
        client1 = RedisClient()
        client2 = RedisClient()
        
        # Both instances should be the same object
        self.assertIs(client1, client2)
    
    def test_basic_operations(self):
        """Test basic Redis operations (get, set, exists, delete)."""
        # Test set and get
        self.redis_client.set("test_key", "test_value")
        value = self.redis_client.get("test_key")
        # Redis returns bytes, decode for comparison
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        self.assertEqual(value, "test_value")
        
        # Test exists
        exists = self.redis_client.exists("test_key")
        self.assertTrue(exists)
        
        # Test delete
        deleted = self.redis_client.delete("test_key")
        self.assertTrue(deleted)
        
        # Verify key is gone
        exists = self.redis_client.exists("test_key")
        self.assertFalse(exists)
    
    def test_json_operations(self):
        """Test JSON serialization and deserialization."""
        test_data = {
            "name": "AAPL",
            "price": 150.5,
            "metrics": {
                "pe_ratio": 25.3,
                "market_cap": 2.5e12
            },
            "tags": ["tech", "consumer"]
        }
        
        # Test set_json and get_json
        self.redis_client.set_json("json_key", test_data)
        result = self.redis_client.get_json("json_key")
        
        self.assertEqual(result, test_data)
        self.assertEqual(result["name"], "AAPL")
        self.assertEqual(result["metrics"]["pe_ratio"], 25.3)
        
        # Test default value when key doesn't exist
        default_result = self.redis_client.get_json("non_existent_key", {"default": True})
        self.assertEqual(default_result, {"default": True})
    
    def test_hash_operations(self):
        """Test hash operations (hset, hget, hgetall, hdel)."""
        # Set multiple fields
        self.redis_client.hset("hash_key", "field1", "value1")
        self.redis_client.hset("hash_key", "field2", "value2")
        
        # Get individual fields
        field1 = self.redis_client.hget("hash_key", "field1") 
        if isinstance(field1, bytes):
            field1 = field1.decode('utf-8')
        self.assertEqual(field1, "value1")
        
        # Get all fields
        raw_fields = self.redis_client.hgetall("hash_key")
        all_fields = {}
        for k, v in raw_fields.items():
            if isinstance(k, bytes):
                k = k.decode('utf-8')
            if isinstance(v, bytes):
                v = v.decode('utf-8')
            all_fields[k] = v
        
        self.assertEqual(all_fields, {"field1": "value1", "field2": "value2"})
        
        # Delete a field
        deleted = self.redis_client.hdel("hash_key", "field1")
        self.assertEqual(deleted, 1)
        
        # Verify field is gone
        raw_fields = self.redis_client.hgetall("hash_key")
        all_fields = {}
        for k, v in raw_fields.items():
            if isinstance(k, bytes):
                k = k.decode('utf-8')
            if isinstance(v, bytes):
                v = v.decode('utf-8')
            all_fields[k] = v
        
        self.assertEqual(all_fields, {"field2": "value2"})
    
    def test_list_operations(self):
        """Test list operations (lpush, rpush, lrange, ltrim, llen)."""
        # Push items to list from left
        length = self.redis_client.lpush("list_key", "item3", "item2", "item1")
        self.assertEqual(length, 3)
        
        # Push items to list from right
        length = self.redis_client.rpush("list_key", "item4", "item5")
        self.assertEqual(length, 5)
        
        # Get range of items - Redis returns bytes, decode for comparison
        raw_items = self.redis_client.lrange("list_key", 0, -1)
        items = [item.decode('utf-8') if isinstance(item, bytes) else item for item in raw_items]
        self.assertEqual(items, ["item1", "item2", "item3", "item4", "item5"])
        
        # Trim list
        self.redis_client.ltrim("list_key", 1, 3)
        raw_items = self.redis_client.lrange("list_key", 0, -1)
        items = [item.decode('utf-8') if isinstance(item, bytes) else item for item in raw_items]
        self.assertEqual(items, ["item2", "item3", "item4"])
        
        # Get list length
        length = self.redis_client.llen("list_key")
        self.assertEqual(length, 3)
    
    def test_limited_list(self):
        """Test add_to_list_limited utility."""
        # Add items to limited list
        for i in range(12):
            self.redis_client.add_to_list_limited("limited_list", f"item{i}", max_items=10)
        
        # Should only have 10 items
        length = self.redis_client.llen("limited_list")
        self.assertEqual(length, 10)
        
        # First two items should be trimmed
        raw_items = self.redis_client.lrange("limited_list", 0, -1)
        items = [item.decode('utf-8') if isinstance(item, bytes) else item for item in raw_items]
        self.assertEqual(items[0], "item11")
        self.assertEqual(items[9], "item2")
    
    def test_retry_mechanism(self):
        """Test retry mechanism on connection errors."""
        # Create a counter to track calls to _get_client
        call_count = 0
        
        # Store the original methods
        original_get_client = self.redis_client._get_client
        original_handle = self.redis_client._handle_connection_error
        
        # Mock the _get_client method to simulate connection failures
        def mock_get_client():
            nonlocal call_count
            call_count += 1
            
            # First two calls fail with ConnectionError
            if call_count <= 2:
                raise ConnectionError("Connection refused")
            
            # Third call succeeds
            return original_get_client()
            
        # Replace the methods
        self.redis_client._get_client = mock_get_client
        self.redis_client._handle_connection_error = lambda op, retry: 0  # No sleep between retries
        
        try:
            # Call ping, which should internally retry on connection errors
            result = self.redis_client.ping()
            
            # Verify the method was called the expected number of times
            self.assertEqual(call_count, 3)
            
            # The final result should be True
            self.assertTrue(result)
            
        finally:
            # Restore the original methods
            self.redis_client._get_client = original_get_client
            self.redis_client._handle_connection_error = original_handle


if __name__ == '__main__':
    unittest.main() 