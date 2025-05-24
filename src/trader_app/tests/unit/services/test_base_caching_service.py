import pytest
from unittest.mock import MagicMock, patch
from pydantic import BaseModel
from trader_app.services.base_caching_service import BaseCachingService
from trader_app.utils import redis_schema

class DummyModel(BaseModel):
    x: int

class DummyService(BaseCachingService[DummyModel]):
    pass

def make_service(redis_mock=None):
    if redis_mock is None:
        redis_mock = MagicMock()
    client = MagicMock()
    client.get_client.return_value = redis_mock
    service = DummyService(redis_client=client)
    return service, redis_mock

@patch('trader_app.utils.redis_schema.deserialize_model')
def test_get_from_cache_hit(mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.return_value = b'data'
    mock_deserialize.return_value = DummyModel(x=1)
    result = service.get_from_cache(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel)
    assert isinstance(result, DummyModel)
    assert result.x == 1
    redis_mock.get.assert_called_once()
    mock_deserialize.assert_called_once()

@patch('trader_app.utils.redis_schema.deserialize_model')
def test_get_from_cache_miss(mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.return_value = None
    result = service.get_from_cache(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel)
    assert result is None
    redis_mock.get.assert_called_once()
    mock_deserialize.assert_not_called()

@patch('trader_app.utils.redis_schema.deserialize_model')
def test_get_from_cache_redis_error(mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.side_effect = Exception('fail')
    result = service.get_from_cache(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel)
    assert result is None
    redis_mock.get.assert_called_once()
    mock_deserialize.assert_not_called()

@patch('trader_app.utils.redis_schema.serialize_model')
def test_set_cache_success(mock_serialize):
    service, redis_mock = make_service()
    mock_serialize.return_value = b'serialized'
    with patch('trader_app.utils.redis_schema.get_ttl_for_key', return_value=123):
        service.set_cache(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel(x=2))
    redis_mock.setex.assert_called_once_with(
        redis_schema.get_key(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}),
        123,
        b'serialized',
    )
    mock_serialize.assert_called_once()

@patch('trader_app.utils.redis_schema.serialize_model')
def test_set_cache_redis_error(mock_serialize):
    service, redis_mock = make_service()
    mock_serialize.return_value = b'serialized'
    redis_mock.setex.side_effect = Exception('fail')
    with patch('trader_app.utils.redis_schema.get_ttl_for_key', return_value=123):
        service.set_cache(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel(x=2))
    redis_mock.setex.assert_called_once()
    mock_serialize.assert_called_once()

@patch('trader_app.utils.redis_schema.deserialize_model')
@patch('trader_app.utils.redis_schema.serialize_model')
def test_cache_first_cache_hit(mock_serialize, mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.return_value = b'data'
    mock_deserialize.return_value = DummyModel(x=3)
    fetch_source = MagicMock()
    result = service.cache_first(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel, fetch_source)
    assert isinstance(result, DummyModel)
    assert result.x == 3
    fetch_source.assert_not_called()
    mock_deserialize.assert_called_once()

@patch('trader_app.utils.redis_schema.deserialize_model')
@patch('trader_app.utils.redis_schema.serialize_model')
def test_cache_first_cache_miss(mock_serialize, mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.return_value = None
    fetch_source = MagicMock(return_value=DummyModel(x=4))
    mock_serialize.return_value = b'serialized'
    with patch('trader_app.utils.redis_schema.get_ttl_for_key', return_value=123):
        result = service.cache_first(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel, fetch_source)
    assert isinstance(result, DummyModel)
    assert result.x == 4
    fetch_source.assert_called_once()
    mock_serialize.assert_called_once()
    redis_mock.setex.assert_called_once()

@patch('trader_app.utils.redis_schema.deserialize_model')
@patch('trader_app.utils.redis_schema.serialize_model')
def test_cache_first_source_returns_none(mock_serialize, mock_deserialize):
    service, redis_mock = make_service()
    redis_mock.get.return_value = None
    fetch_source = MagicMock(return_value=None)
    result = service.cache_first(redis_schema.RedisKeyType.ACCOUNT_SUMMARY, {'user_id': 'abc'}, DummyModel, fetch_source)
    assert result is None
    fetch_source.assert_called_once()
    mock_serialize.assert_not_called()
    redis_mock.setex.assert_not_called()

# Test extensibility: subclass can override methods
class CustomService(BaseCachingService[DummyModel]):
    def get_from_cache(self, *args, **kwargs):
        return 'custom-cache'

def test_subclass_override():
    service = CustomService(redis_client=MagicMock())
    assert service.get_from_cache(None, None, None) == 'custom-cache' 