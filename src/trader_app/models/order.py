from pydantic import BaseModel, Field, PositiveFloat, field_validator, model_validator
from typing import Optional, Literal
from datetime import datetime

class NewOrderRequest(BaseModel):
    symbol: str = Field(
        ..., 
        pattern=r'^[A-Z]{1,5}$', 
        description="Stock symbol (1-5 uppercase letters)",
        example="AAPL"
    )
    qty: PositiveFloat = Field(
        ..., 
        description="Order quantity (must be positive)",
        example=10
    )
    side: Literal['buy', 'sell'] = Field(
        ..., 
        description="Order side: 'buy' or 'sell'",
        example="buy"
    )
    type: Literal['market', 'limit', 'stop', 'stop_limit'] = Field(
        ..., 
        description="Order type",
        example="limit"
    )
    time_in_force: Literal['day', 'gtc', 'opg', 'cls', 'ioc', 'fok'] = Field(
        ..., 
        description="Time in force",
        example="day"
    )
    limit_price: Optional[float] = Field(
        None, 
        description="Limit price (required for limit orders)",
        example=150.0
    )
    client_order_id: Optional[str] = Field(
        None, 
        description="Optional client order ID",
        example="my-order-123"
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

class OrderSubmissionResponse(BaseModel):
    id: str = Field(..., description="Order ID", example="order123")
    client_order_id: str = Field(..., description="Client order ID", example="client123")
    created_at: datetime = Field(..., description="Order creation time", example="2024-06-01T12:00:00Z")
    updated_at: Optional[datetime] = Field(None, description="Order update time", example="2024-06-01T12:05:00Z")
    submitted_at: Optional[datetime] = Field(None, description="Order submission time", example="2024-06-01T12:00:01Z")
    filled_at: Optional[datetime] = Field(None, description="Order fill time", example="2024-06-01T12:01:00Z")
    expired_at: Optional[datetime] = Field(None, description="Order expiration time", example=None)
    canceled_at: Optional[datetime] = Field(None, description="Order cancel time", example=None)
    failed_at: Optional[datetime] = Field(None, description="Order failure time", example=None)
    asset_id: str = Field(..., description="Asset ID", example="asset123")
    symbol: str = Field(..., description="Stock symbol", example="AAPL")
    asset_class: str = Field(..., description="Asset class", example="us_equity")
    qty: float = Field(..., description="Order quantity", example=10.0)
    filled_qty: float = Field(..., description="Filled quantity", example=0.0)
    type: str = Field(..., description="Order type", example="market")
    side: str = Field(..., description="Order side", example="buy")
    time_in_force: str = Field(..., description="Time in force", example="day")
    limit_price: Optional[float] = Field(None, description="Limit price", example=150.0)
    stop_price: Optional[float] = Field(None, description="Stop price", example=None)
    status: str = Field(..., description="Order status", example="new")

    class Config:
        allow_population_by_field_name = True
        orm_mode = True
