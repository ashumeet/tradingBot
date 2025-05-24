import pytest
from trader_app.utils.redis_schema import RedisKeyType, get_key, get_ttl_for_key, serialize_model, deserialize_model
from trader_app.models.market import BarModel, QuoteModel
from decimal import Decimal
from datetime import datetime
import json

def test_get_key_account_summary():
    key = get_key(RedisKeyType.ACCOUNT_SUMMARY, {"user_id": "u123"})
    assert key == "cache:account_summary:user_id=u123"

def test_get_key_positions():
    key = get_key(RedisKeyType.POSITIONS, {"user_id": "u456"})
    assert key == "cache:positions:user_id=u456"

def test_get_key_stock_bars():
    key = get_key(RedisKeyType.STOCK_BARS, {"symbol": "AAPL", "timeframe": "1Day"})
    # Order of params is sorted
    assert key == "cache:stock_bars:symbol=AAPL:timeframe=1Day"

def test_get_key_stock_quote():
    key = get_key(RedisKeyType.STOCK_QUOTE, {"symbol": "GOOG"})
    assert key == "cache:stock_quote:symbol=GOOG"

def test_get_key_special_chars():
    key = get_key(RedisKeyType.STOCK_QUOTE, {"symbol": "MSFT:|!"})
    assert key == "cache:stock_quote:symbol=MSFT__!"

def test_get_key_missing_param():
    with pytest.raises(ValueError):
        get_key(RedisKeyType.STOCK_BARS, {"symbol": "AAPL"})

def test_get_key_invalid_key_type():
    with pytest.raises(ValueError):
        get_key("not_a_key_type", {"user_id": "u1"})

def test_get_ttl_for_key_all_types():
    assert get_ttl_for_key(RedisKeyType.ACCOUNT_SUMMARY) == 300
    assert get_ttl_for_key(RedisKeyType.POSITIONS) == 300
    assert get_ttl_for_key(RedisKeyType.STOCK_BARS) == 300
    assert get_ttl_for_key(RedisKeyType.STOCK_QUOTE) == 60

def test_get_ttl_for_key_invalid():
    class Dummy:
        pass
    with pytest.raises(ValueError):
        get_ttl_for_key(Dummy)

def test_serialize_deserialize_single_model():
    bar = BarModel(
        timestamp="2024-05-01T15:30:00Z",
        open="150.00",
        high="155.00",
        low="149.00",
        close="152.00",
        volume=10000
    )
    s = serialize_model(bar)
    assert isinstance(s, str)
    bar2 = deserialize_model(BarModel, s)
    assert bar2 == bar

def test_serialize_deserialize_list_of_models():
    bars = [
        BarModel(
            timestamp="2024-05-01T15:30:00Z",
            open="150.00",
            high="155.00",
            low="149.00",
            close="152.00",
            volume=10000
        ),
        BarModel(
            timestamp="2024-05-01T15:31:00Z",
            open="152.00",
            high="156.00",
            low="151.00",
            close="154.00",
            volume=12000
        )
    ]
    s = serialize_model(bars)
    assert isinstance(s, str)
    bars2 = deserialize_model(BarModel, s)
    assert bars2 == bars

def test_serialize_decimal_and_datetime():
    quote = QuoteModel(
        symbol="AAPL",
        bid_price=Decimal("150.10"),
        bid_size=100,
        ask_price=Decimal("150.20"),
        ask_size=200,
        timestamp=datetime(2024, 5, 1, 15, 30)
    )
    s = serialize_model(quote)
    d = json.loads(s)
    assert d["bid_price"] == "150.10"
    assert "T" in d["timestamp"]
    quote2 = deserialize_model(QuoteModel, s)
    assert quote2 == quote

def test_serialize_model_invalid_type():
    with pytest.raises(TypeError):
        serialize_model({"not": "a model"})

def test_deserialize_model_invalid_json():
    with pytest.raises(ValueError):
        deserialize_model(BarModel, "not a json string") 