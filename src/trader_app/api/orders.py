import os
from fastapi import APIRouter, Depends, status, Request
from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from trader_app.services.order_service import OrderService
from trader_app.services.alpaca_service import AlpacaService
from trader_app.utils.logging import get_logger
import time
from src.trader_app.security.dependencies import get_ssh_authenticated_user

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
logger = get_logger()

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
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    auth=Depends(get_ssh_authenticated_user)
):
    """
    Place a new order. Accepts a validated NewOrderRequest and returns an OrderSubmissionResponse on success.
    """
    start_time = time.time()
    logger.info("Order request received", extra={
        "method": request.method,
        "path": request.url.path,
        "body": order.model_dump(),
        "user_id": "ssh-key"
    })
    try:
        response = order_service.submit_order(order)
        logger.info("Order response", extra={
            "status": 201,
            "response": response.model_dump(),
            "elapsed_ms": int((time.time() - start_time) * 1000),
            "user_id": "ssh-key"
        })
        return response
    except Exception as e:
        from fastapi import HTTPException
        if isinstance(e, HTTPException):
            raise  # Let FastAPI handle HTTPExceptions (like 401/403)
        logger.error("Order error", extra={
            "error": str(e),
            "elapsed_ms": int((time.time() - start_time) * 1000),
            "user_id": "ssh-key"
        })
        raise
