from fastapi import APIRouter, Depends, status, HTTPException
from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from trader_app.services.order_service import OrderService
from trader_app.services.alpaca_service import AlpacaService
import os

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])

# Dependency for OrderService
def get_order_service():
    api_key = os.getenv("ALPACA_API_KEY", "demo")
    secret_key = os.getenv("ALPACA_SECRET_KEY", "demo")
    api_url = os.getenv("ALPACA_API_URL", "https://paper-api.alpaca.markets")
    alpaca_service = AlpacaService(api_key, secret_key, api_url)
    return OrderService(alpaca_service=alpaca_service)

@router.post("/", response_model=OrderSubmissionResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order: NewOrderRequest,
    order_service: OrderService = Depends(get_order_service)
):
    """
    Place a new order. Accepts a validated NewOrderRequest and returns an OrderSubmissionResponse on success.
    """
    try:
        return order_service.submit_order(order)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {e}")
