import pytest
from decimal import Decimal
from datetime import datetime
from trader_app.models.market import (
    BarModel, QuoteModel, SymbolListRequest, BarsResponse, QuotesResponse
)

def test_bar_model_valid():
    bar = BarModel(
        timestamp="2024-05-01T15:30:00Z",
        open="150.00",
        high="155.00",
        low="149.00",
        close="152.00",
        volume=10000
    )
    assert bar.open == Decimal("150.00")
    assert bar.volume == 10000
    assert isinstance(bar.timestamp, datetime)

def test_bar_model_negative_price():
    with pytest.raises(ValueError):
        BarModel(
            timestamp="2024-05-01T15:30:00Z",
            open="-1.00",
            high="155.00",
            low="149.00",
            close="152.00",
            volume=10000
        )

def test_bar_model_negative_volume():
    with pytest.raises(ValueError):
        BarModel(
            timestamp="2024-05-01T15:30:00Z",
            open="150.00",
            high="155.00",
            low="149.00",
            close="152.00",
            volume=-1
        )

def test_quote_model_valid():
    quote = QuoteModel(
        symbol="AAPL",
        timestamp="2024-05-01T15:30:00Z",
        ask_price="152.10",
        ask_size=200,
        bid_price="151.90",
        bid_size=180
    )
    assert quote.symbol == "AAPL"
    assert quote.ask_price == Decimal("152.10")
    assert quote.bid_size == 180

def test_quote_model_negative_price():
    with pytest.raises(ValueError):
        QuoteModel(
            symbol="AAPL",
            timestamp="2024-05-01T15:30:00Z",
            ask_price="-1.00",
            ask_size=200,
            bid_price="151.90",
            bid_size=180
        )

def test_quote_model_negative_size():
    with pytest.raises(ValueError):
        QuoteModel(
            symbol="AAPL",
            timestamp="2024-05-01T15:30:00Z",
            ask_price="152.10",
            ask_size=-1,
            bid_price="151.90",
            bid_size=180
        )

def test_symbol_list_request_valid():
    req = SymbolListRequest(symbols=["AAPL", "GOOG"])
    assert req.symbols == ["AAPL", "GOOG"]

def test_symbol_list_request_empty():
    with pytest.raises(ValueError):
        SymbolListRequest(symbols=[])

def test_symbol_list_request_invalid_symbol():
    with pytest.raises(ValueError):
        SymbolListRequest(symbols=[""])

def test_bars_response_valid():
    bar = BarModel(
        timestamp="2024-05-01T15:30:00Z",
        open="150.00",
        high="155.00",
        low="149.00",
        close="152.00",
        volume=10000
    )
    resp = BarsResponse(symbol="AAPL", bars=[bar])
    assert resp.symbol == "AAPL"
    assert resp.bars[0].open == Decimal("150.00")

def test_quotes_response_valid():
    quote = QuoteModel(
        symbol="AAPL",
        timestamp="2024-05-01T15:30:00Z",
        ask_price="152.10",
        ask_size=200,
        bid_price="151.90",
        bid_size=180
    )
    resp = QuotesResponse(quotes=[quote])
    assert resp.quotes[0].symbol == "AAPL"
    assert resp.quotes[0].ask_price == Decimal("152.10")

def test_openapi_examples():
    # BarModel example
    bar = BarModel(**BarModel.model_config["json_schema_extra"]["example"])
    assert bar.open == Decimal("150.00")
    # QuoteModel example
    quote = QuoteModel(**QuoteModel.model_config["json_schema_extra"]["example"])
    assert quote.ask_price == Decimal("152.10")
    # SymbolListRequest example
    req = SymbolListRequest(**SymbolListRequest.model_config["json_schema_extra"]["example"])
    assert req.symbols == ["AAPL", "GOOG", "MSFT"]
    # BarsResponse example
    bars_resp = BarsResponse(
        symbol="AAPL",
        bars=[BarModel(**BarModel.model_config["json_schema_extra"]["example"])]
    )
    assert bars_resp.symbol == "AAPL"
    # QuotesResponse example
    quotes_resp = QuotesResponse(
        quotes=[QuoteModel(**QuoteModel.model_config["json_schema_extra"]["example"])]
    )
    assert quotes_resp.quotes[0].symbol == "AAPL" 