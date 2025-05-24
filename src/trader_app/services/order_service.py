from trader_app.models.order import NewOrderRequest, OrderSubmissionResponse
from trader_app.services.alpaca_service import AlpacaService
from fastapi import HTTPException
from typing import Optional

class OrderService:
    def __init__(self, alpaca_service: Optional[AlpacaService] = None):
        self.alpaca_service = alpaca_service or AlpacaService()

    def submit_order(self, order_request: NewOrderRequest) -> OrderSubmissionResponse:
        """
        Maps the NewOrderRequest to Alpaca's order format, submits it, and returns an OrderSubmissionResponse.
        Raises HTTPException on error.
        """
        try:
            # Map NewOrderRequest to Alpaca order params
            alpaca_order = {
                "symbol": order_request.symbol,
                "qty": order_request.qty,
                "side": order_request.side,
                "type": order_request.type,
                "time_in_force": order_request.time_in_force,
            }
            if order_request.limit_price is not None:
                alpaca_order["limit_price"] = order_request.limit_price
            if order_request.client_order_id:
                alpaca_order["client_order_id"] = order_request.client_order_id

            # Submit order to Alpaca
            alpaca_response = self.alpaca_service.submit_order(**alpaca_order)

            # Map Alpaca response to OrderSubmissionResponse
            return OrderSubmissionResponse(
                id=alpaca_response["id"],
                client_order_id=alpaca_response.get("client_order_id", ""),
                created_at=alpaca_response["created_at"],
                updated_at=alpaca_response.get("updated_at"),
                submitted_at=alpaca_response.get("submitted_at"),
                filled_at=alpaca_response.get("filled_at"),
                expired_at=alpaca_response.get("expired_at"),
                canceled_at=alpaca_response.get("canceled_at"),
                failed_at=alpaca_response.get("failed_at"),
                asset_id=alpaca_response["asset_id"],
                symbol=alpaca_response["symbol"],
                asset_class=alpaca_response["asset_class"],
                qty=alpaca_response["qty"],
                filled_qty=alpaca_response["filled_qty"],
                type=alpaca_response["type"],
                side=alpaca_response["side"],
                time_in_force=alpaca_response["time_in_force"],
                limit_price=alpaca_response.get("limit_price"),
                stop_price=alpaca_response.get("stop_price"),
                status=alpaca_response["status"]
            )
        except Exception as e:
            # Map known Alpaca errors to HTTP 400/502, else 500
            raise HTTPException(status_code=502, detail=f"Order submission failed: {e}")
