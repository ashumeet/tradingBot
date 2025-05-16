"""
Configuration module for the trading bot.

This module provides configuration loading, validation, and secure handling.
"""

from .config import (
    ALPACA_API_KEY,
    ALPACA_SECRET_KEY,
    OPENAI_API_KEY,
    ENVIRONMENT,
    ALPACA_API_URL,
    ALPACA_DATA_API_URL,
    TARGET_INDEX_FUNDS,
    validate_config,
    get_secure_config_summary,
    mask_api_key,
    check_for_hardcoded_secrets,
    ENV_FILE_PATH,
    get_config_value
)

__all__ = [
    'ALPACA_API_KEY',
    'ALPACA_SECRET_KEY',
    'OPENAI_API_KEY',
    'ENVIRONMENT',
    'ALPACA_API_URL',
    'ALPACA_DATA_API_URL',
    'TARGET_INDEX_FUNDS',
    'validate_config',
    'get_secure_config_summary',
    'mask_api_key',
    'check_for_hardcoded_secrets',
    'ENV_FILE_PATH',
    'get_config_value'
] 