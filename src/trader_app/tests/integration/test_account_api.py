import os
os.environ["TESTING"] = "1"
import pytest
from fastapi.testclient import TestClient
from trader_app.api.account import router as account_router
from fastapi import FastAPI, status
from unittest.mock import MagicMock
from trader_app.models.account import AccountSummaryResponse
from trader_app.models.portfolio import PositionResponse

app = FastAPI()
app.include_router(account_router)
client = TestClient(app)

# Mock AccountService for dependency override
def get_account_service_mock():
    mock = MagicMock()
    mock.get_account_summary.return_value = AccountSummaryResponse(
        id="abc123",
        buying_power="100000.00",
        cash="50000.00",
        equity="150000.00",
        portfolio_value="150000.00",
        status="ACTIVE",
        currency="USD"
    )
    mock.get_all_positions.return_value = [
        PositionResponse(
            asset_id="asset123",
            symbol="AAPL",
            avg_entry_price="150.00",
            qty="10",
            side="long",
            market_value="1500.00",
            cost_basis="1400.00",
            unrealized_pl="100.00",
            unrealized_plpc="0.0714",
            current_price="150.00"
        )
    ]
    return mock

from trader_app.api import account
app.dependency_overrides[account.get_account_service] = get_account_service_mock

def test_get_account_summary():
    response = client.get("/api/v1/account")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == "abc123"
    assert data["buying_power"] == "100000.00"
    assert data["status"] == "ACTIVE"
    assert data["currency"] == "USD"

def test_get_positions():
    response = client.get("/api/v1/positions")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["symbol"] == "AAPL"
    assert data[0]["qty"] == "10"
