import pytest
from unittest.mock import MagicMock, patch
from trader_app.services.account_service import AccountService
from trader_app.models.account import AccountSummaryResponse
from trader_app.models.portfolio import PositionResponse
from trader_app.services.exceptions import AlpacaApiError
from decimal import Decimal

@pytest.fixture
def mock_alpaca_service():
    mock = MagicMock()
    # Account data mock
    mock.get_account.return_value = {
        "id": "abc123",
        "buying_power": "100000.00",
        "cash": "50000.00",
        "equity": "150000.00",
        "portfolio_value": "150000.00",
        "status": "ACTIVE",
        "currency": "USD"
    }
    # Positions data mock
    mock.get_positions.return_value = [
        {
            "asset_id": "asset123",
            "symbol": "AAPL",
            "avg_entry_price": "150.00",
            "qty": "10",
            "side": "long",
            "market_value": "1500.00",
            "cost_basis": "1400.00",
            "unrealized_pl": "100.00",
            "unrealized_plpc": "0.0714",
            "current_price": "150.00"
        }
    ]
    return mock

def test_get_account_summary_success(mock_alpaca_service):
    service = AccountService(alpaca_service=mock_alpaca_service)
    result = service.get_account_summary()
    assert isinstance(result, AccountSummaryResponse)
    assert result.id == "abc123"
    assert result.buying_power == Decimal("100000.00")
    assert result.status == "ACTIVE"
    assert result.currency == "USD"

def test_get_account_summary_error(mock_alpaca_service):
    mock_alpaca_service.get_account.side_effect = Exception("fail")
    service = AccountService(alpaca_service=mock_alpaca_service)
    with pytest.raises(AlpacaApiError) as exc:
        service.get_account_summary()
    assert "Failed to fetch account summary" in str(exc.value)

def test_get_all_positions_success(mock_alpaca_service):
    service = AccountService(alpaca_service=mock_alpaca_service)
    results = service.get_all_positions()
    assert isinstance(results, list)
    assert len(results) == 1
    pos = results[0]
    assert isinstance(pos, PositionResponse)
    assert pos.symbol == "AAPL"
    assert pos.qty == Decimal("10")
    assert pos.side == "long"

def test_get_all_positions_error(mock_alpaca_service):
    mock_alpaca_service.get_positions.side_effect = Exception("fail")
    service = AccountService(alpaca_service=mock_alpaca_service)
    with pytest.raises(AlpacaApiError) as exc:
        service.get_all_positions()
    assert "Failed to fetch positions" in str(exc.value)

def test_get_account_summary_cache_hit(mock_alpaca_service):
    summary = AccountSummaryResponse(
        id="abc123",
        buying_power=Decimal("100000.00"),
        cash=Decimal("50000.00"),
        equity=Decimal("150000.00"),
        portfolio_value=Decimal("150000.00"),
        status="ACTIVE",
        currency="USD"
    )
    with patch("trader_app.services.base_caching_service.RedisClient") as MockRedis, \
         patch("trader_app.utils.redis_schema.deserialize_model") as mock_deserialize:
        mock_redis = MockRedis.return_value
        mock_redis.get.return_value = '{"id": "abc123", "buying_power": "100000.00", "cash": "50000.00", "equity": "150000.00", "portfolio_value": "150000.00", "status": "ACTIVE", "currency": "USD"}'
        mock_deserialize.return_value = summary
        service = AccountService(alpaca_service=mock_alpaca_service)
        result = service.get_account_summary()
        assert result == summary
        mock_alpaca_service.get_account.assert_not_called()

def test_get_account_summary_cache_miss(mock_alpaca_service):
    with patch("trader_app.services.base_caching_service.RedisClient") as MockRedis:
        mock_redis = MockRedis.return_value
        mock_redis.get.return_value = None
        service = AccountService(alpaca_service=mock_alpaca_service)
        result = service.get_account_summary()
        assert isinstance(result, AccountSummaryResponse)
        mock_alpaca_service.get_account.assert_called_once()

def test_get_all_positions_cache_hit(mock_alpaca_service):
    pos = PositionResponse(
        asset_id="asset123",
        symbol="AAPL",
        avg_entry_price=Decimal("150.00"),
        qty=Decimal("10"),
        side="long",
        market_value=Decimal("1500.00"),
        cost_basis=Decimal("1400.00"),
        unrealized_pl=Decimal("100.00"),
        unrealized_plpc=Decimal("0.0714"),
        current_price=Decimal("150.00")
    )
    with patch("trader_app.services.base_caching_service.RedisClient") as MockRedis, \
         patch("trader_app.utils.redis_schema.deserialize_model") as mock_deserialize:
        mock_redis = MockRedis.return_value
        mock_redis.get.return_value = '[{"asset_id": "asset123", "symbol": "AAPL", "avg_entry_price": "150.00", "qty": "10", "side": "long", "market_value": "1500.00", "cost_basis": "1400.00", "unrealized_pl": "100.00", "unrealized_plpc": "0.0714", "current_price": "150.00"}]'
        mock_deserialize.return_value = [pos]
        service = AccountService(alpaca_service=mock_alpaca_service)
        results = service.get_all_positions()
        assert isinstance(results, list)
        assert results[0] == pos
        mock_alpaca_service.get_positions.assert_not_called()

def test_get_all_positions_cache_miss(mock_alpaca_service):
    with patch("trader_app.services.base_caching_service.RedisClient") as MockRedis:
        mock_redis = MockRedis.return_value
        mock_redis.get.return_value = None
        service = AccountService(alpaca_service=mock_alpaca_service)
        results = service.get_all_positions()
        assert isinstance(results, list)
        mock_alpaca_service.get_positions.assert_called_once() 