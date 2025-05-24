import pytest
from fastapi.testclient import TestClient
from trader_app.api.orders import router as orders_router
from fastapi import FastAPI, status
from unittest.mock import MagicMock
from trader_app.models.order import NewOrderRequest
from trader_app.services.exceptions import OrderValidationError, AlpacaApiError, InternalServerError

from trader_app.services.exception_handlers import register_exception_handlers
app = FastAPI()
register_exception_handlers(app)
app.include_router(orders_router)
client = TestClient(app)

# Dependency override for error simulation
def get_order_service_validation_error():
    mock = MagicMock()
    mock.submit_order.side_effect = OrderValidationError("Symbol must be uppercase", details={"symbol": "aapl"})
    return mock

def get_order_service_alpaca_error():
    mock = MagicMock()
    mock.submit_order.side_effect = AlpacaApiError("Failed to submit order to Alpaca", details="API timeout")
    return mock

def get_order_service_internal_error():
    mock = MagicMock()
    mock.submit_order.side_effect = InternalServerError(details="Unexpected error")
    return mock

from trader_app.api import orders

def test_order_validation_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_validation_error
    payload = {
        "symbol": "aapl",
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 422
    data = response.json()
    # Accept both custom error and FastAPI validation error
    if "error" in data:
        assert data["error"]["code"] == "order_validation_error"
        assert "symbol" in data["error"]["details"]
    else:
        # FastAPI/Pydantic validation error
        assert "detail" in data
        assert any("symbol" in str(item.get("loc", [])) for item in data["detail"])

def test_alpaca_api_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_alpaca_error
    payload = {
        "symbol": "AAPL",
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "alpaca_api_error"
    assert "API timeout" in data["error"]["details"]

def test_internal_server_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_internal_error
    payload = {
        "symbol": "AAPL",
        "qty": 1,
        "side": "buy",
        "type": "market",
        "time_in_force": "day"
    }
    response = client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "internal_server_error"
    assert "Unexpected error" in data["error"]["details"]
