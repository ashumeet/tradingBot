import os
os.environ["TESTING"] = "1"
import pytest
from fastapi.testclient import TestClient
from fastapi import FastAPI, status, Depends
from trader_app.api.orders import router as orders_router
from trader_app.api.account import router as account_router
from trader_app.services.exception_handlers import register_exception_handlers

app = FastAPI()
register_exception_handlers(app)
app.include_router(orders_router)
app.include_router(account_router)
client = TestClient(app)

def fake_auth_dependency_fail():
    from fastapi import HTTPException
    raise HTTPException(status_code=401, detail="Not authenticated")

# Patch the auth dependency for all endpoints that require it
from trader_app.api import orders, account

def test_orders_post_unauthorized():
    app.dependency_overrides[orders.get_ssh_authenticated_user] = fake_auth_dependency_fail
    response = client.post("/api/v1/orders", json={"symbol": "AAPL", "qty": 1, "side": "buy", "type": "market", "time_in_force": "day"})
    assert response.status_code == 401
    assert "Not authenticated" in response.text
    app.dependency_overrides = {}

# No get_current_user in account API, so this test is not applicable and should be removed or skipped.
