"""
Unit tests for RedisClient and Redis schema utilities in trader_app
"""
import pytest
from unittest.mock import patch, MagicMock
from trader_app.utils import redis_client, redis_schema

# Utility to reset the RedisClient singleton between tests

def reset_redis_singleton():
    redis_client.RedisClient._instance = None

# Test RedisClient singleton and connection

def test_redis_client_singleton():
    reset_redis_singleton()
    client1 = redis_client.RedisClient()
    client2 = redis_client.RedisClient()
    assert client1 is client2

@patch('trader_app.utils.redis_client.redis.ConnectionPool')
@patch('trader_app.utils.redis_client.redis.Redis')
def test_redis_client_connection(mock_redis, mock_pool):
    reset_redis_singleton()
    mock_pool.return_value = MagicMock()
    mock_instance = MagicMock()
    mock_redis.return_value = mock_instance
    client = redis_client.RedisClient(host='localhost', port=6379, db=0)
    redis_conn = client.get_client()
    assert redis_conn == mock_instance  # Use ==, not is

# Test Redis schema key generation

def test_get_key_with_identifier():
    key = redis_schema.get_key(redis_schema.KeyPrefix.MARKET_DATA, 'ticker', 'AAPL')
    assert key == 'market_data:ticker:AAPL'

def test_get_key_without_identifier():
    key = redis_schema.get_key(redis_schema.KeyPrefix.SESSION, 'active')
    assert key == 'session:active'

# Test TTL policies

def test_ttl_policies_for_market_data():
    ttl = redis_schema.TTL_POLICIES['market_data:ticker:*']
    assert ttl == redis_schema.TTL.SHORT

def test_ttl_policies_for_portfolio_history():
    ttl = redis_schema.TTL_POLICIES['portfolio:history:*']
    assert ttl == redis_schema.TTL.WEEKLY

# Test error handling in RedisClient (simulate connection error)
@patch('trader_app.utils.redis_client.redis.ConnectionPool')
def test_redis_client_connection_error(mock_pool):
    reset_redis_singleton()
    mock_pool.side_effect = Exception('Connection failed')
    with pytest.raises(Exception):
        redis_client.RedisClient(host='badhost', port=9999, db=0, max_retries=0)
# ... continued from previous chunk ...
