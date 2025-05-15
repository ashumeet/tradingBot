"""
Redis Schema Module

This module defines the Redis key naming conventions and TTL policies
for different data types stored in Redis.
"""

import enum
from typing import Dict, Any, List

# Key prefixes for different data categories
class KeyPrefix:
    SETTINGS = "settings"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    TRADE = "trade"
    CACHE = "cache"
    AI_OUTPUT = "ai_output"
    LOG = "log"
    SESSION = "session"


# Default TTL (Time To Live) values in seconds
class TTL:
    # No expiration
    NONE = -1
    
    # Short-lived cache (1 minute)
    VERY_SHORT = 60
    
    # Standard cache (10 minutes)
    SHORT = 600
    
    # Medium cache (1 hour)
    MEDIUM = 3600
    
    # Long cache (8 hours)
    LONG = 28800
    
    # Daily data (24 hours)
    DAILY = 86400
    
    # Weekly data (7 days)
    WEEKLY = 604800
    
    # Monthly data (30 days)
    MONTHLY = 2592000


# TTL policies for different key types
TTL_POLICIES = {
    # Settings do not expire
    f"{KeyPrefix.SETTINGS}:*": TTL.NONE,
    
    # Market data with different time frames
    f"{KeyPrefix.MARKET_DATA}:ticker:*": TTL.SHORT,         # Ticker data
    f"{KeyPrefix.MARKET_DATA}:bars:1min:*": TTL.DAILY,      # 1-minute bars
    f"{KeyPrefix.MARKET_DATA}:bars:5min:*": TTL.DAILY,      # 5-minute bars
    f"{KeyPrefix.MARKET_DATA}:bars:15min:*": TTL.DAILY,     # 15-minute bars
    f"{KeyPrefix.MARKET_DATA}:bars:1hour:*": TTL.WEEKLY,    # 1-hour bars
    f"{KeyPrefix.MARKET_DATA}:bars:1day:*": TTL.MONTHLY,    # Daily bars
    
    # Portfolio data
    f"{KeyPrefix.PORTFOLIO}:current:*": TTL.MEDIUM,         # Current portfolio
    f"{KeyPrefix.PORTFOLIO}:history:*": TTL.WEEKLY,         # Portfolio history
    
    # Trade data
    f"{KeyPrefix.TRADE}:logs:*": TTL.WEEKLY,                # Trade logs
    f"{KeyPrefix.TRADE}:orders:*": TTL.DAILY,               # Order history
    
    # Cache data
    f"{KeyPrefix.CACHE}:api:*": TTL.SHORT,                  # API response cache
    f"{KeyPrefix.CACHE}:computed:*": TTL.MEDIUM,            # Computed results
    
    # AI model outputs
    f"{KeyPrefix.AI_OUTPUT}:prediction:*": TTL.MEDIUM,      # AI predictions
    f"{KeyPrefix.AI_OUTPUT}:analysis:*": TTL.LONG,          # AI analysis
    
    # Logs and debug info
    f"{KeyPrefix.LOG}:error:*": TTL.WEEKLY,                 # Error logs
    f"{KeyPrefix.LOG}:access:*": TTL.DAILY,                 # Access logs
    
    # Session data
    f"{KeyPrefix.SESSION}:*": TTL.MEDIUM,                   # User session data
}


def get_key(category: str, key_type: str, identifier: str = None) -> str:
    """
    Generate a Redis key with proper structure and namespacing.
    
    Args:
        category: The main category (use KeyPrefix constants)
        key_type: The key type within the category
        identifier: Optional identifier such as asset name, date, etc.
        
    Returns:
        str: The properly formatted Redis key
    """
    if identifier:
        return f"{category}:{key_type}:{identifier}"
    return f"{category}:{key_type}"


def get_ttl_for_key(key: str) -> int:
    """
    Get the TTL for a given key based on TTL policies.
    
    Args:
        key: The Redis key
        
    Returns:
        int: TTL in seconds, or -1 for no expiration
    """
    # Try exact match first
    if key in TTL_POLICIES:
        return TTL_POLICIES[key]
    
    # Check pattern matches
    for pattern, ttl in TTL_POLICIES.items():
        if pattern.endswith('*'):
            prefix = pattern[:-1]  # Remove the * at the end
            if key.startswith(prefix):
                return ttl
    
    # Default to no expiration if no match found
    return TTL.NONE


# Schema definitions for JSON structures
SCHEMA_DEFINITIONS = {
    # Settings schema
    f"{KeyPrefix.SETTINGS}": {
        "type": "hash",
        "fields": {
            "app_version": "string",
            "trading_enabled": "boolean",
            "max_position_size": "integer",
            "risk_level": "float",
            "active_strategies": "json"
        }
    },
    
    # Market data schema
    f"{KeyPrefix.MARKET_DATA}:ticker": {
        "type": "hash",
        "fields": {
            "symbol": "string",
            "bid": "float",
            "ask": "float",
            "last_price": "float",
            "volume": "integer",
            "timestamp": "integer"
        }
    },
    
    f"{KeyPrefix.MARKET_DATA}:bars": {
        "type": "sorted_set",
        "score": "timestamp",
        "value": "json",
        "value_schema": {
            "open": "float",
            "high": "float",
            "low": "float",
            "close": "float",
            "volume": "integer",
            "timestamp": "integer"
        }
    },
    
    # Portfolio schema
    f"{KeyPrefix.PORTFOLIO}:current": {
        "type": "hash",
        "fields": {
            "cash": "float",
            "positions": "json",
            "equity": "float",
            "last_updated": "integer"
        }
    },
    
    # Trade logs schema
    f"{KeyPrefix.TRADE}:logs": {
        "type": "list",
        "max_length": 1000,
        "value_schema": {
            "symbol": "string",
            "side": "string",
            "quantity": "float",
            "price": "float",
            "timestamp": "integer",
            "strategy": "string",
            "reason": "string",
            "order_id": "string"
        }
    },
    
    # AI output schema
    f"{KeyPrefix.AI_OUTPUT}:prediction": {
        "type": "hash",
        "fields": {
            "symbol": "string",
            "prediction": "float",
            "confidence": "float",
            "timestamp": "integer",
            "model_version": "string",
            "features_used": "json"
        }
    }
}


def get_key_schema(key_pattern: str) -> Dict[str, Any]:
    """
    Get the schema definition for a key pattern.
    
    Args:
        key_pattern: Key pattern to lookup in schema definitions
        
    Returns:
        Dict: Schema definition or empty dict if not found
    """
    # Try exact match
    if key_pattern in SCHEMA_DEFINITIONS:
        return SCHEMA_DEFINITIONS[key_pattern]
    
    # Try to find the best match by prefix
    for schema_key, schema in SCHEMA_DEFINITIONS.items():
        if key_pattern.startswith(schema_key):
            return schema
    
    return {} 