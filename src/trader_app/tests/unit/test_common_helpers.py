"""
Unit tests for common_helpers.py in trader_app.utils
"""
import pytest
from trader_app.utils import common_helpers
from datetime import time as dt_time, datetime, timedelta
import pytz

# Test print_log (smoke test for all log levels)
def test_print_log_all_levels():
    for level in common_helpers.LogLevel:
        common_helpers.print_log(f"Test message for {level.value}", level)

# Test is_debug_mode

def test_is_debug_mode_true(monkeypatch):
    monkeypatch.setenv("DEBUG", "true")
    assert common_helpers.is_debug_mode() is True

def test_is_debug_mode_false(monkeypatch):
    monkeypatch.setenv("DEBUG", "false")
    assert common_helpers.is_debug_mode() is False

# Test display_table (smoke test)
def test_display_table_smoke():
    headers = ["Col1", "Col2"]
    data = [[1, 2], [3, 4]]
    common_helpers.display_table(headers, data, title="Test Table")

# Test is_market_open with injected now
def test_is_market_open_true():
    eastern = pytz.timezone("US/Eastern")
    fake_now = eastern.localize(datetime(2024, 1, 1, 10, 0, 0))
    assert common_helpers.is_market_open(now=fake_now) is True

def test_is_market_open_false():
    eastern = pytz.timezone("US/Eastern")
    fake_now = eastern.localize(datetime(2024, 1, 1, 8, 0, 0))
    assert common_helpers.is_market_open(now=fake_now) is False

# Test time_until_market_opens with injected now
def test_time_until_market_opens():
    eastern = pytz.timezone("US/Eastern")
    fake_now = eastern.localize(datetime(2024, 1, 1, 8, 0, 0))
    seconds = common_helpers.time_until_market_opens(now=fake_now)
    assert isinstance(seconds, float)
    assert seconds > 0
