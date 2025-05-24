import os
os.environ["TESTING"] = "1"
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from unittest.mock import MagicMock
from trader_app.api.market import router as market_router, get_market_data_service
from trader_app.models.market import BarModel, QuoteModel, SymbolListRequest, BarsResponse, QuotesResponse

app = FastAPI()
app.include_router(market_router)
client = TestClient(app)

# Mock MarketDataService for dependency override
def get_market_data_service_mock():
    mock = MagicMock()
    mock.get_bars_for_symbol.return_value = [
        BarModel(
            timestamp="2024-05-01T15:30:00Z",
            open="150.00",
            high="155.00",
            low="149.00",
            close="152.00",
            volume=10000
        )
    ]
    mock.get_latest_quote_for_symbol.return_value = QuoteModel(
        symbol="AAPL",
        timestamp="2024-05-01T15:30:00Z",
        ask_price="152.10",
        ask_size=200,
        bid_price="151.90",
        bid_size=180
    )
    mock.get_latest_quotes_for_symbols.return_value = [
        QuoteModel(
            symbol="AAPL",
            timestamp="2024-05-01T15:30:00Z",
            ask_price="152.10",
            ask_size=200,
            bid_price="151.90",
            bid_size=180
        ),
        QuoteModel(
            symbol="GOOG",
            timestamp="2024-05-01T15:30:00Z",
            ask_price="2720.00",
            ask_size=100,
            bid_price="2715.00",
            bid_size=90
        )
    ]
    return mock

from trader_app.api import market
app.dependency_overrides[market.get_market_data_service] = get_market_data_service_mock

def test_get_bars():
    response = client.get("/api/v1/marketdata/bars/AAPL?timeframe=1Day&limit=1")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert isinstance(data["bars"], list)
    assert data["bars"][0]["open"] == "150.00"

def test_get_latest_quote():
    response = client.get("/api/v1/marketdata/quotes/latest/AAPL")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["ask_price"] == "152.10"

def test_get_latest_quotes():
    response = client.post("/api/v1/marketdata/quotes/latest", json={"symbols": ["AAPL", "GOOG"]})
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data["quotes"], list)
    assert data["quotes"][0]["symbol"] == "AAPL"
    assert data["quotes"][1]["symbol"] == "GOOG"

def test_get_bars_not_found(monkeypatch):
    def bars_none(*args, **kwargs):
        return []
    app.dependency_overrides[market.get_market_data_service] = lambda: MagicMock(get_bars_for_symbol=bars_none)
    response = client.get("/api/v1/marketdata/bars/INVALID")
    assert response.status_code == 404
    assert "No bars found" in response.text

def test_get_bars_api_error(monkeypatch):
    def bars_error(*args, **kwargs):
        raise Exception("Alpaca error")
    app.dependency_overrides[market.get_market_data_service] = lambda: MagicMock(get_bars_for_symbol=bars_error)
    response = client.get("/api/v1/marketdata/bars/AAPL")
    assert response.status_code == 502
    assert "Alpaca error" in response.text

def test_get_latest_quote_api_error(monkeypatch):
    def quote_error(*args, **kwargs):
        raise Exception("Alpaca error")
    app.dependency_overrides[market.get_market_data_service] = lambda: MagicMock(get_latest_quote_for_symbol=quote_error)
    response = client.get("/api/v1/marketdata/quotes/latest/AAPL")
    assert response.status_code == 502
    assert "Alpaca error" in response.text

def test_get_latest_quotes_api_error(monkeypatch):
    def quotes_error(*args, **kwargs):
        raise Exception("Alpaca error")
    app.dependency_overrides[market.get_market_data_service] = lambda: MagicMock(get_latest_quotes_for_symbols=quotes_error)
    response = client.post("/api/v1/marketdata/quotes/latest", json={"symbols": ["AAPL", "GOOG"]})
    assert response.status_code == 502
    assert "Alpaca error" in response.text 