from pydantic import BaseModel, Field, PositiveFloat, field_validator, model_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime

class NewOrderRequest(BaseModel):
    symbol: str = Field(
        ..., 
        pattern=r'^[A-Z]{1,5}$', 
        description="Stock symbol (1-5 uppercase letters)"
    )
    qty: PositiveFloat = Field(
        ..., 
        description="Order quantity (must be positive)"
    )
    side: Literal['buy', 'sell'] = Field(
        ..., 
        description="Order side: 'buy' or 'sell'"
    )
    type: Literal['market', 'limit', 'stop', 'stop_limit'] = Field(
        ..., 
        description="Order type"
    )
    time_in_force: Literal['day', 'gtc', 'opg', 'cls', 'ioc', 'fok'] = Field(
        ..., 
        description="Time in force"
    )
    limit_price: Optional[float] = Field(
        None, 
        description="Limit price (required for limit orders)"
    )
    client_order_id: Optional[str] = Field(
        None, 
        description="Optional client order ID"
    )

    @field_validator('symbol')
    @classmethod
    def symbol_must_be_uppercase(cls, v):
        if not v.isupper():
            raise ValueError('Symbol must be uppercase')
        return v

    @field_validator('qty')
    @classmethod
    def qty_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be positive')
        return v

    @model_validator(mode="after")
    def check_conditional_fields(self):
        if self.type in ('limit', 'stop_limit') and self.limit_price is None:
            raise ValueError('limit_price is required for limit and stop_limit orders')
        return self

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "qty": 10,
                "side": "buy",
                "type": "limit",
                "time_in_force": "day",
                "limit_price": 150.0,
                "client_order_id": "my-order-123"
            }
        }
    )

class OrderSubmissionResponse(BaseModel):
    id: str = Field(..., description="Order ID")
    client_order_id: str = Field(..., description="Client order ID")
    created_at: datetime = Field(..., description="Order creation time")
    updated_at: Optional[datetime] = Field(None, description="Order update time")
    submitted_at: Optional[datetime] = Field(None, description="Order submission time")
    filled_at: Optional[datetime] = Field(None, description="Order fill time")
    expired_at: Optional[datetime] = Field(None, description="Order expiration time")
    canceled_at: Optional[datetime] = Field(None, description="Order cancel time")
    failed_at: Optional[datetime] = Field(None, description="Order failure time")
    asset_id: str = Field(..., description="Asset ID")
    symbol: str = Field(..., description="Stock symbol")
    asset_class: str = Field(..., description="Asset class")
    qty: float = Field(..., description="Order quantity")
    filled_qty: float = Field(..., description="Filled quantity")
    type: str = Field(..., description="Order type")
    side: str = Field(..., description="Order side")
    time_in_force: str = Field(..., description="Time in force")
    limit_price: Optional[float] = Field(None, description="Limit price")
    stop_price: Optional[float] = Field(None, description="Stop price")
    status: str = Field(..., description="Order status")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "order123",
                "client_order_id": "client123",
                "created_at": "2024-06-01T12:00:00Z",
                "updated_at": "2024-06-01T12:05:00Z",
                "submitted_at": "2024-06-01T12:00:01Z",
                "filled_at": None,
                "expired_at": None,
                "canceled_at": None,
                "failed_at": None,
                "asset_id": "asset123",
                "symbol": "AAPL",
                "asset_class": "us_equity",
                "qty": 10.0,
                "filled_qty": 0.0,
                "type": "market",
                "side": "buy",
                "time_in_force": "day",
                "limit_price": 150.0,
                "stop_price": None,
                "status": "new"
            }
        },
        validate_by_name=True,
        from_attributes=True
    )
