import pytest
from fastapi.testclient import TestClient
from trader_app.__main__ import main
from trader_app.models.order import OrderSubmissionResponse, NewOrderRequest
from trader_app.api.orders import router as orders_router
from fastapi import FastAPI, status
from unittest.mock import MagicMock

# Create a FastAPI TestClient instance
app = FastAPI()
app.include_router(orders_router)
client = TestClient(app)

# Mock OrderService for dependency override
def mock_submit_order(order_request: NewOrderRequest):
    return OrderSubmissionResponse(
        id="order123",
        client_order_id=order_request.client_order_id or "client123",
        created_at="2024-06-01T15:30:00Z",
        asset_id="asset123",
        symbol=order_request.symbol,
        asset_class="us_equity",
        qty=order_request.qty,
        filled_qty=0,
        type=order_request.type,
        side=order_request.side,
        time_in_force=order_request.time_in_force,
        status="accepted"
    )

from trader_app.api import orders
app.dependency_overrides[orders.get_order_service] = lambda: MagicMock(submit_order=mock_submit_order)

def test_post_order_valid_market():
    payload = {
        "symbol": "AAPL",
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["qty"] == 1
    assert data["status"] == "accepted"

def test_post_order_invalid_symbol():
    payload = {
        "symbol": "aapl",  # not uppercase
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 422
    assert "symbol" in response.text

def test_post_order_missing_required():
    payload = {
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 422
    assert "symbol" in response.text
