from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from trader_app.services.alpaca_service import AlpacaService
from trader_app.services.exceptions import OrderValidationError, AlpacaApiError, InternalServerError
from typing import Optional
from trader_app.utils.redis_schema import RedisKeyType
from trader_app.services.base_caching_service import BaseCachingService

class OrderService(BaseCachingService):
    def __init__(self, alpaca_service: Optional[AlpacaService] = None):
        super().__init__()
        self.alpaca_service = alpaca_service or AlpacaService()

    def submit_order(self, order_request: NewOrderRequest) -> OrderSubmissionResponse:
        """
        Maps the NewOrderRequest to Alpaca's order format, submits it, and returns an OrderSubmissionResponse.
        Raises HTTPException on error.
        """
        try:
            # Example validation (expand as needed)
            if not order_request.symbol.isupper():
                raise OrderValidationError("Symbol must be uppercase", details={"symbol": order_request.symbol})
            # Map NewOrderRequest to Alpaca order params
            alpaca_order = {
                "symbol": order_request.symbol,
                "qty": order_request.qty,
                "side": order_request.side,
                "type": order_request.type,
                "time_in_force": order_request.time_in_force,
            }
            if order_request.limit_price:
                alpaca_order["limit_price"] = order_request.limit_price
            if order_request.client_order_id:
                alpaca_order["client_order_id"] = order_request.client_order_id

            # Call Alpaca API
            try:
                response = self.alpaca_service.submit_order(**alpaca_order)
            except Exception as e:
                raise AlpacaApiError("Failed to submit order to Alpaca", details=str(e))

            # Map response to OrderSubmissionResponse
            return OrderSubmissionResponse(
                id=response["id"],
                client_order_id=response.get("client_order_id", ""),
                created_at=response["created_at"],
                updated_at=response.get("updated_at"),
                submitted_at=response.get("submitted_at"),
                filled_at=response.get("filled_at"),
                expired_at=response.get("expired_at"),
                canceled_at=response.get("canceled_at"),
                failed_at=response.get("failed_at"),
                asset_id=response["asset_id"],
                symbol=response["symbol"],
                asset_class=response["asset_class"],
                qty=response["qty"],
                filled_qty=response["filled_qty"],
                type=response["type"],
                side=response["side"],
                time_in_force=response["time_in_force"],
                limit_price=response.get("limit_price"),
                stop_price=response.get("stop_price"),
                status=response["status"]
            )
        except (OrderValidationError, AlpacaApiError):
            raise
        except Exception as e:
            raise InternalServerError(details=str(e))

    def get_order_by_id(self, order_id: str) -> Optional[OrderSubmissionResponse]:
        """
        Get order by ID, using Redis cache if available. Falls back to Alpaca if not cached.
        """
        params = {"order_id": order_id}
        def fetch_source():
            try:
                response = self.alpaca_service.get_order_by_id(order_id)
                return OrderSubmissionResponse(
                    id=response["id"],
                    client_order_id=response.get("client_order_id", ""),
                    created_at=response["created_at"],
                    updated_at=response.get("updated_at"),
                    submitted_at=response.get("submitted_at"),
                    filled_at=response.get("filled_at"),
                    expired_at=response.get("expired_at"),
                    canceled_at=response.get("canceled_at"),
                    failed_at=response.get("failed_at"),
                    asset_id=response["asset_id"],
                    symbol=response["symbol"],
                    asset_class=response["asset_class"],
                    qty=response["qty"],
                    filled_qty=response["filled_qty"],
                    type=response["type"],
                    side=response["side"],
                    time_in_force=response["time_in_force"],
                    limit_price=response.get("limit_price"),
                    stop_price=response.get("stop_price"),
                    status=response["status"]
                )
            except Exception as e:
                raise AlpacaApiError("Failed to fetch order by ID", details=str(e))
        return self.cache_first(
            RedisKeyType.ORDER,
            params,
            OrderSubmissionResponse,
            fetch_source,
            is_list=False
        )
