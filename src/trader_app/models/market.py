from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime

class StockBarResponse(BaseModel):
    """Represents a single OHLCV bar for a stock symbol."""
    timestamp: datetime = Field(..., description="Bar timestamp (UTC)", example="2024-06-01T15:30:00Z")
    open: float = Field(..., description="Opening price", ge=0, example=150.25)
    high: float = Field(..., description="Highest price", ge=0, example=151.00)
    low: float = Field(..., description="Lowest price", ge=0, example=149.80)
    close: float = Field(..., description="Closing price", ge=0, example=150.75)
    volume: int = Field(..., description="Trade volume", ge=0, example=1200000)
    vwap: Optional[float] = Field(None, description="Volume-weighted average price", ge=0, example=150.60)
    trade_count: Optional[int] = Field(None, description="Number of trades in the bar", ge=0, example=3500)

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "timestamp": "2024-06-01T15:30:00Z",
                "open": 150.25,
                "high": 151.00,
                "low": 149.80,
                "close": 150.75,
                "volume": 1200000,
                "vwap": 150.60,
                "trade_count": 3500
            }
        }
    )

class StockQuoteResponse(BaseModel):
    """Represents a real-time quote for a stock symbol."""
    symbol: str = Field(..., description="Stock symbol", example="AAPL")
    ask_price: float = Field(..., description="Current ask price", ge=0, example=150.80)
    ask_size: int = Field(..., description="Current ask size", ge=0, example=200)
    bid_price: float = Field(..., description="Current bid price", ge=0, example=150.70)
    bid_size: int = Field(..., description="Current bid size", ge=0, example=180)
    last_trade_price: float = Field(..., description="Last trade price", ge=0, example=150.75)
    timestamp: datetime = Field(..., description="Quote timestamp (UTC)", example="2024-06-01T15:30:05Z")
    conditions: Optional[List[str]] = Field(None, description="List of quote conditions (optional)", example=["R", "@"])

    model_config = ConfigDict(
        json_encoders={datetime: lambda v: v.isoformat()},
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "ask_price": 150.80,
                "ask_size": 200,
                "bid_price": 150.70,
                "bid_size": 180,
                "last_trade_price": 150.75,
                "timestamp": "2024-06-01T15:30:05Z",
                "conditions": ["R", "@"]
            }
        }
    )

class SymbolListRequest(BaseModel):
    """Request model for batch stock quote requests."""
    symbols: List[str] = Field(..., description="List of stock symbols (uppercase, alphanumeric, max 100)", example=["AAPL", "GOOG", "MSFT"])

    @field_validator('symbols')
    @classmethod
    def validate_symbols(cls, v):
        if not v or not isinstance(v, list):
            raise ValueError('symbols must be a non-empty list')
        if len(v) > 100:
            raise ValueError('Maximum 100 symbols allowed per request')
        for symbol in v:
            if not isinstance(symbol, str) or not symbol.isalnum() or not symbol.isupper():
                raise ValueError(f'Invalid symbol: {symbol}. Must be uppercase alphanumeric string.')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbols": ["AAPL", "GOOG", "MSFT"]
            }
        }
    )
