import os
os.environ["TESTING"] = "1"
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status
from unittest.mock import MagicMock
from trader_app.api.account import router as account_router, get_account_service
from trader_app.services.exceptions import AlpacaApiError, InternalServerError
from trader_app.services.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(account_router)
client = TestClient(app)

def get_account_service_alpaca_error():
    mock = MagicMock()
    mock.get_account_summary.side_effect = AlpacaApiError("Failed to fetch account summary", details="API timeout")
    mock.get_all_positions.side_effect = AlpacaApiError("Failed to fetch positions", details="API timeout")
    return mock

def get_account_service_internal_error():
    mock = MagicMock()
    mock.get_account_summary.side_effect = InternalServerError(details="Unexpected error")
    mock.get_all_positions.side_effect = InternalServerError(details="Unexpected error")
    return mock

def test_account_summary_alpaca_error():
    app.dependency_overrides[get_account_service] = get_account_service_alpaca_error
    response = client.get("/api/v1/account")
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "alpaca_api_error"
    assert "API timeout" in data["error"]["details"]

def test_positions_alpaca_error():
    app.dependency_overrides[get_account_service] = get_account_service_alpaca_error
    response = client.get("/api/v1/positions")
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "alpaca_api_error"
    assert "API timeout" in data["error"]["details"]

def test_account_summary_internal_error():
    app.dependency_overrides[get_account_service] = get_account_service_internal_error
    response = client.get("/api/v1/account")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "internal_server_error"
    assert "Unexpected error" in data["error"]["details"]

def test_positions_internal_error():
    app.dependency_overrides[get_account_service] = get_account_service_internal_error
    response = client.get("/api/v1/positions")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "internal_server_error"
    assert "Unexpected error" in data["error"]["details"]
