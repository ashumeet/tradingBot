from fastapi import APIRouter, Depends, status, Request
from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from trader_app.services.order_service import OrderService
from trader_app.services.alpaca_service import AlpacaService
from trader_app.utils.logging import get_logger
import time

router = APIRouter(prefix="/api/v1/orders", tags=["orders"])
logger = get_logger()

# Dependency for OrderService
def get_order_service():
    api_key = os.getenv("ALPACA_API_KEY", "demo")
    secret_key = os.getenv("ALPACA_SECRET_KEY", "demo")
    api_url = os.getenv("ALPACA_API_URL", "https://paper-api.alpaca.markets")
    alpaca_service = AlpacaService(api_key, secret_key, api_url)
    return OrderService(alpaca_service=alpaca_service)

# Placeholder for authentication dependency
def get_current_user():
    # In the future, extract user info from JWT or session
    return None

@router.post("/", response_model=OrderSubmissionResponse, status_code=status.HTTP_201_CREATED)
def place_order(
    order: NewOrderRequest,
    request: Request,
    order_service: OrderService = Depends(get_order_service),
    user_id: str = Depends(get_current_user)
):
    """
    Place a new order. Accepts a validated NewOrderRequest and returns an OrderSubmissionResponse on success.
    """
    start_time = time.time()
    logger.info("Order request received", extra={
        "method": request.method,
        "path": request.url.path,
        "body": order.model_dump(),
        "user_id": user_id
    })
    try:
        response = order_service.submit_order(order)
        logger.info("Order response", extra={
            "status": 201,
            "response": response.model_dump(),
            "elapsed_ms": int((time.time() - start_time) * 1000),
            "user_id": user_id
        })
        return response
    except Exception as e:
        logger.error("Order error", extra={
            "error": str(e),
            "elapsed_ms": int((time.time() - start_time) * 1000),
            "user_id": user_id
        })
        raise
