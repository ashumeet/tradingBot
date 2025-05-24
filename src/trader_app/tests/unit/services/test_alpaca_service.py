"""
Unit tests for AlpacaService in trader_app.services.alpaca_service
"""
import pytest
from unittest.mock import patch, MagicMock
from trader_app.services.alpaca_service import AlpacaService, AlpacaServiceException

API_KEY = "test_key"
SECRET_KEY = "test_secret"
API_URL = "https://paper-api.alpaca.markets"

@patch("trader_app.services.alpaca_service.TradingClient")
@patch("trader_app.services.alpaca_service.StockHistoricalDataClient")
def test_alpaca_service_init(mock_data_client, mock_trading_client):
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.trading_client == mock_trading_client.return_value
    assert service.data_client == mock_data_client.return_value
    assert service.api_url == API_URL

@patch("trader_app.services.alpaca_service.TradingClient")
def test_health_check_success(mock_trading_client):
    mock_instance = mock_trading_client.return_value
    mock_instance.get_account.return_value = MagicMock(id="abc123")
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.health_check() is True

@patch("trader_app.services.alpaca_service.TradingClient")
def test_health_check_api_error(mock_trading_client):
    from alpaca.common.exceptions import APIError
    mock_instance = mock_trading_client.return_value
    mock_instance.get_account.side_effect = APIError("fail")
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.health_check() is False

@patch("trader_app.services.alpaca_service.TradingClient")
def test_health_check_unexpected_error(mock_trading_client):
    mock_instance = mock_trading_client.return_value
    mock_instance.get_account.side_effect = Exception("fail")
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.health_check() is False

@patch("trader_app.services.alpaca_service.TradingClient")
def test_get_account_success(mock_trading_client):
    mock_instance = mock_trading_client.return_value
    mock_instance.get_account.return_value = MagicMock()
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.get_account() == mock_instance.get_account.return_value

@patch("trader_app.services.alpaca_service.TradingClient")
def test_get_account_api_error(mock_trading_client):
    from alpaca.common.exceptions import APIError
    mock_instance = mock_trading_client.return_value
    mock_instance.get_account.side_effect = APIError("fail")
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    with pytest.raises(APIError):
        service.get_account()

@patch("trader_app.services.alpaca_service.StockHistoricalDataClient")
def test_get_stock_bars_success(mock_data_client):
    mock_instance = mock_data_client.return_value
    mock_instance.get_stock_bars.return_value = [MagicMock()]
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    result = service.get_stock_bars("AAPL")
    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], MagicMock)

@patch("trader_app.services.alpaca_service.StockHistoricalDataClient")
def test_get_latest_trade_success(mock_data_client):
    mock_instance = mock_data_client.return_value
    mock_instance.get_latest_trade.return_value = MagicMock()
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.get_latest_trade("AAPL") == mock_instance.get_latest_trade.return_value

@patch("trader_app.services.alpaca_service.StockHistoricalDataClient")
def test_get_latest_quote_success(mock_data_client):
    mock_instance = mock_data_client.return_value
    mock_instance.get_latest_quote.return_value = MagicMock()
    service = AlpacaService(API_KEY, SECRET_KEY, API_URL)
    assert service.get_latest_quote("AAPL") == mock_instance.get_latest_quote.return_value
