import pytest
from pydantic import ValidationError
from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from datetime import datetime

# --- NewOrderRequest Tests ---
def test_valid_market_order():
    order = NewOrderRequest(
        symbol="AAPL",
        qty=10,
        side="buy",
        type="market",
        time_in_force="day"
    )
    assert order.symbol == "AAPL"
    assert order.qty == 10
    assert order.type == "market"

def test_valid_limit_order():
    order = NewOrderRequest(
        symbol="GOOG",
        qty=5,
        side="sell",
        type="limit",
        time_in_force="gtc",
        limit_price=1500.0
    )
    assert order.limit_price == 1500.0

def test_invalid_symbol_format():
    with pytest.raises(ValidationError):
        NewOrderRequest(
            symbol="aapl",
            qty=10,
            side="buy",
            type="market",
            time_in_force="day"
        )

def test_negative_quantity():
    with pytest.raises(ValidationError):
        NewOrderRequest(
            symbol="AAPL",
            qty=-5,
            side="buy",
            type="market",
            time_in_force="day"
        )

def test_missing_limit_price_for_limit_order():
    with pytest.raises(ValidationError):
        NewOrderRequest(
            symbol="AAPL",
            qty=10,
            side="buy",
            type="limit",
            time_in_force="day"
        )

# --- OrderSubmissionResponse Tests ---
def test_order_submission_response_parsing():
    data = {
        "id": "order123",
        "client_order_id": "client123",
        "created_at": "2024-06-01T12:00:00Z",
        "asset_id": "asset123",
        "symbol": "AAPL",
        "asset_class": "us_equity",
        "qty": 10.0,
        "filled_qty": 0.0,
        "type": "market",
        "side": "buy",
        "time_in_force": "day",
        "status": "new"
    }
    order = OrderSubmissionResponse(**data)
    assert order.id == "order123"
    assert order.symbol == "AAPL"
    assert order.qty == 10.0
    assert order.status == "new"
    assert isinstance(order.created_at, datetime)
