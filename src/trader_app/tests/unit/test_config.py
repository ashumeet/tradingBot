"""
Unit tests for trader_app.core.config
"""
import os
import sys
import types
import pytest
from unittest import mock

import trader_app.core.config as config

def test_mask_api_key_basic():
    """Test that mask_api_key masks all but the first and last 4 characters."""
    key = "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6"
    masked = config.mask_api_key(key)
    assert masked.startswith(key[:4])
    assert masked.endswith(key[-4:])
    assert set(masked[4:-4]) == {'*'}
    assert len(masked) == len(key)

def test_mask_api_key_short():
    """Test that short keys are masked as 'invalid-key'."""
    assert config.mask_api_key("1234567") == "invalid-key"

def test_validate_api_key_format_alpaca():
    """Test Alpaca key format validation."""
    valid, msg = config.validate_api_key_format("A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6", "ALPACA_API_KEY")
    assert valid
    invalid, msg = config.validate_api_key_format("shortkey", "ALPACA_API_KEY")
    assert not invalid
    assert "invalid format" in msg

def test_validate_api_key_format_openai():
    """Test OpenAI key format validation."""
    valid, msg = config.validate_api_key_format("sk-" + "a"*30, "OPENAI_API_KEY")
    assert valid
    invalid, msg = config.validate_api_key_format("notanopenai", "OPENAI_API_KEY")
    assert not invalid
    assert "invalid format" in msg

def test_get_config_value(monkeypatch):
    """Test get_config_value returns env value or default."""
    monkeypatch.setenv("FOO_BAR", "baz")
    assert config.get_config_value("FOO_BAR") == "baz"
    assert config.get_config_value("NOT_SET", "default") == "default"

def test_get_secure_config_summary_masking(monkeypatch):
    """Test that get_secure_config_summary masks API keys."""
    monkeypatch.setenv("ALPACA_API_KEY", "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "S1S2S3S4S5S6S7S8S9S0S1S2S3S4S5S6")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "a"*30)
    import importlib
    importlib.reload(config)
    summary = config.get_secure_config_summary()
    assert summary["ALPACA_API_KEY"].startswith("A1B2")
    assert summary["ALPACA_SECRET_KEY"].startswith("S1S2")
    assert summary["OPENAI_API_KEY"].startswith("sk-a")
    assert "*" in summary["ALPACA_API_KEY"]
    assert "*" in summary["OPENAI_API_KEY"]

def test_validate_config_missing(monkeypatch):
    """Test validate_config raises on missing required env vars."""
    # Prevent config from loading any .env file
    monkeypatch.setenv("ENV_FILE", "/dev/null")
    for var in ["ALPACA_API_KEY", "ALPACA_SECRET_KEY", "OPENAI_API_KEY", "ALPACA_API_URL", "ALPACA_DATA_API_URL"]:
        monkeypatch.delenv(var, raising=False)
    import importlib
    importlib.reload(config)
    with pytest.raises(ValueError) as exc:
        config.validate_config()
    assert "Missing required environment variables" in str(exc.value)

def test_validate_config_types(monkeypatch):
    """Test validate_config type and value checks."""
    monkeypatch.setenv("ALPACA_API_KEY", "A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6")
    monkeypatch.setenv("ALPACA_SECRET_KEY", "S1S2S3S4S5S6S7S8S9S0S1S2S3S4S5S6")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-" + "a"*30)
    monkeypatch.setenv("ALPACA_API_URL", "https://api.alpaca.markets")
    monkeypatch.setenv("ALPACA_DATA_API_URL", "https://data.alpaca.markets")
    monkeypatch.setenv("ENVIRONMENT", "invalid")
    monkeypatch.setenv("VERBOSE_LOGGING", "notabool")
    monkeypatch.setenv("MAX_CONCURRENT_TRADES", "0")
    import importlib
    importlib.reload(config)
    with pytest.raises(ValueError) as exc:
        config.validate_config()
    assert "ENVIRONMENT must be 'paper' or 'live'" in str(exc.value)
    assert "VERBOSE_LOGGING must be a boolean" in str(exc.value) or "MAX_CONCURRENT_TRADES must be a positive integer" in str(exc.value) 