import json
from trader_app.models.market import StockBarResponse, StockQuoteResponse, SymbolListRequest
from datetime import datetime
import pytest

def test_stock_bar_response_instantiation():
    data = {
        "timestamp": "2024-06-01T15:30:00Z",
        "open": 150.25,
        "high": 151.00,
        "low": 149.80,
        "close": 150.75,
        "volume": 1200000,
        "vwap": 150.60,
        "trade_count": 3500
    }
    model = StockBarResponse(**data)
    assert model.open == 150.25
    assert model.timestamp == datetime.fromisoformat("2024-06-01T15:30:00+00:00") or model.timestamp.isoformat().startswith("2024-06-01T15:30:00")
    assert model.vwap == 150.60
    assert model.trade_count == 3500
    # Test serialization
    json_data = model.model_dump_json()
    assert '150.25' in json_data

def test_stock_quote_response_instantiation():
    data = {
        "symbol": "AAPL",
        "ask_price": 150.80,
        "ask_size": 200,
        "bid_price": 150.70,
        "bid_size": 180,
        "last_trade_price": 150.75,
        "timestamp": "2024-06-01T15:30:05Z",
        "conditions": ["R", "@"]
    }
    model = StockQuoteResponse(**data)
    assert model.symbol == "AAPL"
    assert model.ask_price == 150.80
    assert model.conditions == ["R", "@"]
    # Test serialization: parse JSON and check numeric value
    json_data = model.model_dump_json()
    parsed = json.loads(json_data)
    assert parsed["ask_price"] == 150.8

def test_symbol_list_request_valid():
    req = SymbolListRequest(symbols=["AAPL", "GOOG", "MSFT"])
    assert req.symbols == ["AAPL", "GOOG", "MSFT"]

def test_symbol_list_request_invalid():
    with pytest.raises(ValueError):
        SymbolListRequest(symbols=[])
    with pytest.raises(ValueError):
        SymbolListRequest(symbols=["aapl"])  # not uppercase
    with pytest.raises(ValueError):
        SymbolListRequest(symbols=["AAPL"] * 101)  # too many symbols
