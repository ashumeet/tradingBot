from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from decimal import Decimal

class AccountSummaryResponse(BaseModel):
    id: str = Field(..., description="Account ID")
    buying_power: Decimal = Field(..., description="Available buying power")
    cash: Decimal = Field(..., description="Cash balance")
    equity: Decimal = Field(..., description="Account equity value")
    portfolio_value: Decimal = Field(..., description="Total portfolio value")
    status: str = Field(..., description="Account status (active, inactive, etc.)")
    currency: str = Field(..., description="Base currency for the account")
    # Add more fields as needed, e.g., optional fields from Alpaca's API
    # Example:
    # last_equity: Optional[Decimal] = Field(None, description="Last equity value")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "abc123",
                "buying_power": "100000.00",
                "cash": "50000.00",
                "equity": "150000.00",
                "portfolio_value": "150000.00",
                "status": "ACTIVE",
                "currency": "USD"
            }
        },
        json_encoders={Decimal: lambda v: str(v)}
    )
