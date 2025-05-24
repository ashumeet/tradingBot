# Confirmed: All models in this file use Pydantic v2 ConfigDict and json_schema_extra (no changes needed)
from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List
from decimal import Decimal
from datetime import datetime

class BarModel(BaseModel):
    timestamp: datetime = Field(..., description="Bar timestamp (UTC)")
    open: Decimal = Field(..., description="Open price")
    high: Decimal = Field(..., description="High price")
    low: Decimal = Field(..., description="Low price")
    close: Decimal = Field(..., description="Close price")
    volume: int = Field(..., description="Trade volume")

    @field_validator("open", "high", "low", "close")
    def price_positive(cls, v):
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("volume")
    def volume_positive(cls, v):
        if v < 0:
            raise ValueError("Volume must be non-negative")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "timestamp": "2024-05-01T15:30:00Z",
                "open": "150.00",
                "high": "155.00",
                "low": "149.00",
                "close": "152.00",
                "volume": 10000
            }
        }
    )

class QuoteModel(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    timestamp: datetime = Field(..., description="Quote timestamp (UTC)")
    ask_price: Decimal = Field(..., description="Ask price")
    ask_size: int = Field(..., description="Ask size")
    bid_price: Decimal = Field(..., description="Bid price")
    bid_size: int = Field(..., description="Bid size")

    @field_validator("ask_price", "bid_price")
    def price_positive(cls, v):
        if v < 0:
            raise ValueError("Price must be non-negative")
        return v

    @field_validator("ask_size", "bid_size")
    def size_positive(cls, v):
        if v < 0:
            raise ValueError("Size must be non-negative")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "timestamp": "2024-05-01T15:30:00Z",
                "ask_price": "152.10",
                "ask_size": 200,
                "bid_price": "151.90",
                "bid_size": 180
            }
        }
    )

class SymbolListRequest(BaseModel):
    symbols: List[str] = Field(..., description="List of stock symbols")

    @field_validator("symbols")
    def symbols_not_empty(cls, v):
        if not v or not isinstance(v, list):
            raise ValueError("Symbols list must not be empty")
        for symbol in v:
            if not symbol or not isinstance(symbol, str):
                raise ValueError("Each symbol must be a non-empty string")
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbols": ["AAPL", "GOOG", "MSFT"]
            }
        }
    )

class BarsResponse(BaseModel):
    symbol: str = Field(..., description="Stock symbol")
    bars: List[BarModel] = Field(..., description="List of historical bars")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "bars": [BarModel.model_config["json_schema_extra"]["example"]]
            }
        }
    )

class QuotesResponse(BaseModel):
    quotes: List[QuoteModel] = Field(..., description="List of latest quotes")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "quotes": [QuoteModel.model_config["json_schema_extra"]["example"]]
            }
        }
    )
