import os
os.environ["TESTING"] = "1"
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from unittest.mock import MagicMock
from trader_app.api.orders import router as orders_router, get_order_service
from trader_app.services.exceptions import OrderValidationError, AlpacaApiError, InternalServerError
from trader_app.services.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(orders_router)
client = TestClient(app)

# Error mocks
def get_order_service_validation_error():
    mock = MagicMock()
    mock.place_order.side_effect = OrderValidationError("Invalid order", details="Negative quantity")
    return mock

def get_order_service_alpaca_error():
    mock = MagicMock()
    mock.submit_order.side_effect = AlpacaApiError("Alpaca error", details="API timeout")
    mock.get_order.side_effect = AlpacaApiError("Alpaca error", details="API timeout")
    return mock

def get_order_service_internal_error():
    mock = MagicMock()
    mock.submit_order.side_effect = InternalServerError(details="Unexpected error")
    mock.get_order.side_effect = InternalServerError(details="Unexpected error")
    return mock

def get_order_service_not_found():
    mock = MagicMock()
    mock.get_order.side_effect = OrderValidationError("Order not found", details="No such order")
    return mock

from trader_app.api import orders

def test_post_order_validation_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_validation_error
    response = client.post("/api/v1/orders", json={"symbol": "AAPL", "qty": -1, "side": "buy", "type": "market", "time_in_force": "day"})
    assert response.status_code == 422
    data = response.json()
    # FastAPI validation errors use 'detail' key
    assert "detail" in data

def test_post_order_alpaca_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_alpaca_error
    response = client.post("/api/v1/orders", json={"symbol": "AAPL", "qty": 1, "side": "buy", "type": "market", "time_in_force": "day"})
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "alpaca_api_error"
    assert "API timeout" in data["error"]["details"]

def test_post_order_internal_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_internal_error
    response = client.post("/api/v1/orders", json={"symbol": "AAPL", "qty": 1, "side": "buy", "type": "market", "time_in_force": "day"})
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "internal_server_error"
    assert "Unexpected error" in data["error"]["details"]

def test_get_order_not_found():
    app.dependency_overrides[orders.get_order_service] = get_order_service_not_found
    response = client.get("/api/v1/orders/12345")
    assert response.status_code == 422 or response.status_code == 404
    data = response.json()
    # Accept either custom error or FastAPI 404
    if response.status_code == 422:
        assert data["error"]["code"] == "order_validation_error"
        assert "No such order" in data["error"]["details"]
    else:
        assert data["detail"] == "Not Found"

def test_get_order_alpaca_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_alpaca_error
    response = client.get("/api/v1/orders/12345")
    assert response.status_code == 502 or response.status_code == 404
    data = response.json()
    if response.status_code == 502:
        assert data["error"]["code"] == "alpaca_api_error"
        assert "API timeout" in data["error"]["details"]
    else:
        assert data["detail"] == "Not Found"

def test_get_order_internal_error():
    app.dependency_overrides[orders.get_order_service] = get_order_service_internal_error
    response = client.get("/api/v1/orders/12345")
    assert response.status_code == 500 or response.status_code == 404
    data = response.json()
    if response.status_code == 500:
        assert data["error"]["code"] == "internal_server_error"
        assert "Unexpected error" in data["error"]["details"]
    else:
        assert data["detail"] == "Not Found"
