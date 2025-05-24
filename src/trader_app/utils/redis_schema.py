"""
Redis Schema Module for trader_app

Defines key naming conventions and TTL policies for Redis data.
"""
from typing import Optional, Dict, Any, Type, TypeVar, List, Union
from enum import Enum
import json
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime

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

class RedisKeyType(str, Enum):
    ACCOUNT_SUMMARY = "account_summary"
    POSITIONS = "positions"
    STOCK_BARS = "stock_bars"
    STOCK_QUOTE = "stock_quote"

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

# TTLs in seconds
KEY_TTLS = {
    RedisKeyType.ACCOUNT_SUMMARY: 300,  # 5 minutes
    RedisKeyType.POSITIONS: 300,        # 5 minutes
    RedisKeyType.STOCK_BARS: 300,       # 5 minutes
    RedisKeyType.STOCK_QUOTE: 60,       # 1 minute
}

T = TypeVar("T", bound=BaseModel)

def serialize_model(model: Union[BaseModel, List[BaseModel]]) -> str:
    """
    Serialize a Pydantic model or list of models to a JSON string for Redis storage.
    Handles Decimal and datetime types.
    Args:
        model: A Pydantic BaseModel instance or list of BaseModel
    Returns:
        str: JSON string
    Raises:
        TypeError: if input is not a BaseModel or list of BaseModel
    """
    def default(obj):
        if isinstance(obj, Decimal):
            return str(obj)
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")
    if isinstance(model, list):
        return json.dumps([m.model_dump() for m in model], default=default)
    elif isinstance(model, BaseModel):
        return json.dumps(model.model_dump(), default=default)
    else:
        raise TypeError("serialize_model expects a BaseModel or list of BaseModel")

def deserialize_model(model_cls: Type[T], data: str) -> Union[T, List[T]]:
    """
    Deserialize a JSON string from Redis to a Pydantic model or list of models.
    Args:
        model_cls: The Pydantic model class
        data: JSON string
    Returns:
        BaseModel instance or list of BaseModel
    Raises:
        ValueError: if JSON is invalid or cannot be parsed
    """
    try:
        obj = json.loads(data)
        if isinstance(obj, list):
            return [model_cls.model_validate(item) for item in obj]
        return model_cls.model_validate(obj)
    except Exception as e:
        raise ValueError(f"Failed to deserialize model: {e}")

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

def get_key(key_type: RedisKeyType, params: Dict[str, Any]) -> str:
    """
    Generate a standardized Redis cache key string.
    Args:
        key_type: RedisKeyType enum value
        params: dict of parameters (e.g., symbol, timeframe, user_id)
    Returns:
        str: Standardized cache key
    Raises:
        ValueError: if required params are missing or key_type is invalid
    """
    if not isinstance(key_type, RedisKeyType):
        raise ValueError(f"Invalid key_type: {key_type}")
    # Required params for each key type
    required = {
        RedisKeyType.ACCOUNT_SUMMARY: ["user_id"],
        RedisKeyType.POSITIONS: ["user_id"],
        RedisKeyType.STOCK_BARS: ["symbol", "timeframe"],
        RedisKeyType.STOCK_QUOTE: ["symbol"],
    }
    req = required[key_type]
    for r in req:
        if r not in params or params[r] is None:
            raise ValueError(f"Missing required param '{r}' for key_type '{key_type}'")
    # Key format: prefix:key_type:param1=value1:param2=value2
    parts = ["cache", key_type.value]
    for k in sorted(params):
        v = str(params[k]).replace(":", "_").replace("|", "_")
        parts.append(f"{k}={v}")
    return ":".join(parts)

def get_ttl_for_key(key_type: RedisKeyType) -> int:
    """
    Get the TTL (in seconds) for a given key type.
    Args:
        key_type: RedisKeyType enum value
    Returns:
        int: TTL in seconds
    Raises:
        ValueError: if key_type is invalid
    """
    if key_type not in KEY_TTLS:
        raise ValueError(f"No TTL defined for key_type: {key_type}")
    return KEY_TTLS[key_type]
