from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class PositionResponse(BaseModel):
    asset_id: str = Field(..., description="Unique identifier for the asset", example="asset123")
    symbol: str = Field(..., description="Trading symbol", example="AAPL")
    avg_entry_price: Decimal = Field(..., description="Average entry price", example="150.00")
    qty: Decimal = Field(..., description="Position quantity", example="10")
    side: str = Field(..., description="Position side (long/short)", example="long")
    market_value: Decimal = Field(..., description="Current market value", example="1500.00")
    cost_basis: Decimal = Field(..., description="Original cost basis", example="1400.00")
    unrealized_pl: Decimal = Field(..., description="Unrealized profit/loss", example="100.00")
    unrealized_plpc: Decimal = Field(..., description="Unrealized profit/loss percentage", example="0.0714")
    current_price: Decimal = Field(..., description="Current market price", example="150.00")
    # Add more fields as needed, e.g., optional fields from Alpaca's API

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}
        schema_extra = {
            "example": {
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
        }
