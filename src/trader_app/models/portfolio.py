from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class PositionResponse(BaseModel):
    asset_id: str = Field(..., description="Unique identifier for the asset")
    symbol: str = Field(..., description="Trading symbol")
    avg_entry_price: Decimal = Field(..., description="Average entry price")
    qty: Decimal = Field(..., description="Position quantity")
    side: str = Field(..., description="Position side (long/short)")
    market_value: Decimal = Field(..., description="Current market value")
    cost_basis: Decimal = Field(..., description="Original cost basis")
    unrealized_pl: Decimal = Field(..., description="Unrealized profit/loss")
    unrealized_plpc: Decimal = Field(..., description="Unrealized profit/loss percentage")
    current_price: Decimal = Field(..., description="Current market price")
    # Add more fields as needed, e.g., optional fields from Alpaca's API

    model_config = ConfigDict(
        json_schema_extra={
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
        },
        json_encoders={Decimal: lambda v: str(v)}
    )
