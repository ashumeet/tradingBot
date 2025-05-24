from decimal import Decimal
from trader_app.models.account import AccountSummaryResponse
from trader_app.models.portfolio import PositionResponse

def test_account_summary_response_instantiation():
    data = {
        "id": "abc123",
        "buying_power": "100000.00",
        "cash": "50000.00",
        "equity": "150000.00",
        "portfolio_value": "150000.00",
        "status": "ACTIVE",
        "currency": "USD"
    }
    model = AccountSummaryResponse(**data)
    assert model.id == "abc123"
    assert model.buying_power == Decimal("100000.00")
    assert model.cash == Decimal("50000.00")
    assert model.equity == Decimal("150000.00")
    assert model.portfolio_value == Decimal("150000.00")
    assert model.status == "ACTIVE"
    assert model.currency == "USD"
    # Test serialization
    json_data = model.model_dump_json()
    assert '100000.00' in json_data

def test_position_response_instantiation():
    data = {
        "asset_id": "asset123",
        "symbol": "AAPL",
        "avg_entry_price": "150.00",
        "qty": "10",
        "side": "long",
        "market_value": "1500.00",
        "cost_basis": "1400.00",
        "unrealized_pl": "100.00",
        "unrealized_plpc": "0.0714",
        "current_price": "150.00"
    }
    model = PositionResponse(**data)
    assert model.asset_id == "asset123"
    assert model.symbol == "AAPL"
    assert model.avg_entry_price == Decimal("150.00")
    assert model.qty == Decimal("10")
    assert model.side == "long"
    assert model.market_value == Decimal("1500.00")
    assert model.cost_basis == Decimal("1400.00")
    assert model.unrealized_pl == Decimal("100.00")
    assert model.unrealized_plpc == Decimal("0.0714")
    assert model.current_price == Decimal("150.00")
    # Test serialization
    json_data = model.model_dump_json()
    assert '1500.00' in json_data
