import pytest
from unittest.mock import MagicMock, patch
from trader_app.services.market_data_service import MarketDataService
from trader_app.models.market import BarModel, QuoteModel
from trader_app.services.exceptions import AlpacaApiError, InvalidSymbolError
from decimal import Decimal
from datetime import datetime

@pytest.fixture
def mock_alpaca_service():
    mock = MagicMock()
    # Mock bar object
    bar_obj = MagicMock()
    bar_obj.t = datetime(2024, 5, 1, 15, 30)
    bar_obj.o = 150.0
    bar_obj.h = 155.0
    bar_obj.l = 149.0
    bar_obj.c = 152.0
    bar_obj.v = 10000
    mock.get_bars.return_value = [bar_obj]
    # Mock quote object
    quote_obj = MagicMock()
    quote_obj.t = datetime(2024, 5, 1, 15, 30)
    quote_obj.ap = 152.10
    quote_obj.asize = 200
    quote_obj.bp = 151.90
    quote_obj.bsize = 180
    mock.get_latest_quote.return_value = quote_obj
    # Mock get_latest_quotes returns dict
    mock.get_latest_quotes.return_value = {
        "AAPL": quote_obj,
        "GOOG": quote_obj
    }
    return mock

def test_get_bars_for_symbol_success(mock_alpaca_service):
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    bars = service.get_bars_for_symbol("AAPL", "1Day")
    assert isinstance(bars, list)
    assert isinstance(bars[0], BarModel)
    assert bars[0].open == Decimal("150.0")
    assert bars[0].volume == 10000

def test_get_bars_for_symbol_error(mock_alpaca_service):
    mock_alpaca_service.get_bars.side_effect = Exception("fail")
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    with pytest.raises(AlpacaApiError):
        service.get_bars_for_symbol("AAPL", "1Day")

def test_get_latest_quote_for_symbol_success(mock_alpaca_service):
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    quote = service.get_latest_quote_for_symbol("AAPL")
    assert isinstance(quote, QuoteModel)
    assert quote.symbol == "AAPL"
    assert quote.ask_price == Decimal("152.10")
    assert quote.bid_size == 180

def test_get_latest_quote_for_symbol_error(mock_alpaca_service):
    mock_alpaca_service.get_latest_quote.side_effect = Exception("fail")
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    with pytest.raises(AlpacaApiError):
        service.get_latest_quote_for_symbol("AAPL")

def test_get_latest_quotes_for_symbols_success(mock_alpaca_service):
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    quotes = service.get_latest_quotes_for_symbols(["AAPL", "GOOG"])
    assert isinstance(quotes, list)
    assert all(isinstance(q, QuoteModel) for q in quotes)
    assert quotes[0].symbol == "AAPL"

def test_get_latest_quotes_for_symbols_partial_failure(mock_alpaca_service):
    # Simulate partial failure: AAPL fails, GOOG succeeds
    quote_obj = MagicMock()
    quote_obj.t = datetime(2024, 5, 1, 15, 30)
    quote_obj.ap = 152.10
    quote_obj.asize = 200
    quote_obj.bp = 151.90
    quote_obj.bsize = 180
    mock_alpaca_service.get_latest_quotes.return_value = {
        "AAPL": None,
        "GOOG": quote_obj
    }
    service = MarketDataService(alpaca_service=mock_alpaca_service)
    quotes = service.get_latest_quotes_for_symbols(["AAPL", "GOOG"])
    assert len(quotes) == 1
    assert quotes[0].symbol == "GOOG"

# Patch RedisClient in base_caching_service for cache tests
def make_service_with_redis_mock(mock_redis, mock_alpaca_service):
    from trader_app.services.base_caching_service import BaseCachingService
    class TestMarketDataService(MarketDataService):
        def __init__(self, alpaca_service):
            super().__init__(alpaca_service=alpaca_service)
            self.redis_client = mock_redis
    return TestMarketDataService

def test_get_bars_for_symbol_cache_hit(mock_alpaca_service):
    bar = BarModel(
        timestamp="2024-05-01T15:30:00Z",
        open="150.00",
        high="155.00",
        low="149.00",
        close="152.00",
        volume=10000
    )
    mock_redis = MagicMock()
    # Simulate cache hit: return serialized list
    mock_redis.get_client.return_value.get.return_value = '[{"timestamp": "2024-05-01T15:30:00Z", "open": "150.00", "high": "155.00", "low": "149.00", "close": "152.00", "volume": 10000}]'
    TestService = make_service_with_redis_mock(mock_redis, mock_alpaca_service)
    service = TestService(alpaca_service=mock_alpaca_service)
    bars = service.get_bars_for_symbol("AAPL", "1Day")
    assert isinstance(bars, list)
    assert bars[0] == bar
    mock_alpaca_service.get_bars.assert_not_called()

def test_get_bars_for_symbol_cache_miss(mock_alpaca_service):
    mock_redis = MagicMock()
    # Simulate cache miss: return None
    mock_redis.get_client.return_value.get.return_value = None
    TestService = make_service_with_redis_mock(mock_redis, mock_alpaca_service)
    service = TestService(alpaca_service=mock_alpaca_service)
    bars = service.get_bars_for_symbol("AAPL", "1Day")
    assert isinstance(bars, list)
    mock_alpaca_service.get_bars.assert_called_once()

def test_get_latest_quote_for_symbol_cache_hit(mock_alpaca_service):
    quote = QuoteModel(
        symbol="AAPL",
        bid_price=Decimal("151.90"),
        bid_size=180,
        ask_price=Decimal("152.10"),
        ask_size=200,
        timestamp=datetime(2024, 5, 1, 15, 30)
    )
    mock_redis = MagicMock()
    # Simulate cache hit: return serialized model
    mock_redis.get_client.return_value.get.return_value = '{"symbol": "AAPL", "bid_price": "151.90", "bid_size": 180, "ask_price": "152.10", "ask_size": 200, "timestamp": "2024-05-01T15:30:00"}'
    TestService = make_service_with_redis_mock(mock_redis, mock_alpaca_service)
    service = TestService(alpaca_service=mock_alpaca_service)
    result = service.get_latest_quote_for_symbol("AAPL")
    assert result == quote
    mock_alpaca_service.get_latest_quote.assert_not_called()

def test_get_latest_quote_for_symbol_cache_miss(mock_alpaca_service):
    mock_redis = MagicMock()
    # Simulate cache miss: return None
    mock_redis.get_client.return_value.get.return_value = None
    TestService = make_service_with_redis_mock(mock_redis, mock_alpaca_service)
    service = TestService(alpaca_service=mock_alpaca_service)
    result = service.get_latest_quote_for_symbol("AAPL")
    assert isinstance(result, QuoteModel)
    mock_alpaca_service.get_latest_quote.assert_called_once() 