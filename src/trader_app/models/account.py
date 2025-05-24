from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal

class AccountSummaryResponse(BaseModel):
    id: str = Field(..., description="Account ID", example="abc123")
    buying_power: Decimal = Field(..., description="Available buying power", example="100000.00")
    cash: Decimal = Field(..., description="Cash balance", example="50000.00")
    equity: Decimal = Field(..., description="Account equity value", example="150000.00")
    portfolio_value: Decimal = Field(..., description="Total portfolio value", example="150000.00")
    status: str = Field(..., description="Account status (active, inactive, etc.)", example="ACTIVE")
    currency: str = Field(..., description="Base currency for the account", example="USD")
    # Add more fields as needed, e.g., optional fields from Alpaca's API
    # Example:
    # last_equity: Optional[Decimal] = Field(None, description="Last equity value", example="149000.00")

    class Config:
        json_encoders = {Decimal: lambda v: str(v)}
        schema_extra = {
            "example": {
                "id": "abc123",
                "buying_power": "100000.00",
                "cash": "50000.00",
                "equity": "150000.00",
                "portfolio_value": "150000.00",
                "status": "ACTIVE",
                "currency": "USD"
            }
        }
