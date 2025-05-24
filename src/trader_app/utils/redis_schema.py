"""
Redis Schema Module for trader_app

Defines key naming conventions and TTL policies for Redis data.
"""
from typing import Optional

class KeyPrefix:
    SETTINGS = "settings"
    MARKET_DATA = "market_data"
    PORTFOLIO = "portfolio"
    TRADE = "trade"
    CACHE = "cache"
    AI_OUTPUT = "ai_output"
    LOG = "log"
    SESSION = "session"

class TTL:
    NONE = -1
    VERY_SHORT = 60
    SHORT = 600
    MEDIUM = 3600
    LONG = 28800
    DAILY = 86400
    WEEKLY = 604800
    MONTHLY = 2592000

TTL_POLICIES = {
    f"{KeyPrefix.SETTINGS}:*": TTL.NONE,
    f"{KeyPrefix.MARKET_DATA}:ticker:*": TTL.SHORT,
    f"{KeyPrefix.MARKET_DATA}:bars:1min:*": TTL.DAILY,
    f"{KeyPrefix.MARKET_DATA}:bars:5min:*": TTL.DAILY,
    f"{KeyPrefix.MARKET_DATA}:bars:15min:*": TTL.DAILY,
    f"{KeyPrefix.MARKET_DATA}:bars:1hour:*": TTL.WEEKLY,
    f"{KeyPrefix.MARKET_DATA}:bars:1day:*": TTL.MONTHLY,
    f"{KeyPrefix.PORTFOLIO}:current:*": TTL.MEDIUM,
    f"{KeyPrefix.PORTFOLIO}:history:*": TTL.WEEKLY,
    f"{KeyPrefix.TRADE}:logs:*": TTL.WEEKLY,
    f"{KeyPrefix.TRADE}:orders:*": TTL.DAILY,
    f"{KeyPrefix.CACHE}:api:*": TTL.SHORT,
    f"{KeyPrefix.CACHE}:computed:*": TTL.MEDIUM,
    f"{KeyPrefix.AI_OUTPUT}:prediction:*": TTL.MEDIUM,
    f"{KeyPrefix.AI_OUTPUT}:analysis:*": TTL.LONG,
    f"{KeyPrefix.LOG}:error:*": TTL.WEEKLY,
    f"{KeyPrefix.LOG}:access:*": TTL.DAILY,
    f"{KeyPrefix.SESSION}:*": TTL.MEDIUM,
}

def get_key(category: str, key_type: str, identifier: Optional[str] = None) -> str:
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
