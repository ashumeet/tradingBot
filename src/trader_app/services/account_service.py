from trader_app.models.account import AccountSummaryResponse
from trader_app.models.portfolio import PositionResponse
from trader_app.services.alpaca_service import AlpacaService
from trader_app.services.exceptions import AlpacaApiError, InternalServerError
from typing import List, Optional
from decimal import Decimal
from trader_app.utils.redis_schema import RedisKeyType
from trader_app.services.base_caching_service import BaseCachingService

class AccountService(BaseCachingService):
    def __init__(self, alpaca_service: Optional[AlpacaService] = None):
        super().__init__()
        self.alpaca_service = alpaca_service or AlpacaService()

    def get_account_summary(self) -> AccountSummaryResponse:
        """
        Get account summary, using Redis cache if available.
        Raises AlpacaApiError on failure.
        """
        params = {"user_id": "default"}  # TODO: Replace with real user_id if available
        def fetch_source():
            try:
                data = self.alpaca_service.get_account()
                return AccountSummaryResponse(
                    id=data["id"],
                    buying_power=Decimal(data["buying_power"]),
                    cash=Decimal(data["cash"]),
                    equity=Decimal(data["equity"]),
                    portfolio_value=Decimal(data["portfolio_value"]),
                    status=data["status"],
                    currency=data["currency"]
                )
            except Exception as e:
                raise AlpacaApiError("Failed to fetch account summary", details=str(e))
        return self.cache_first(
            RedisKeyType.ACCOUNT_SUMMARY,
            params,
            AccountSummaryResponse,
            fetch_source,
            is_list=False
        )

    def get_all_positions(self) -> List[PositionResponse]:
        """
        Get all positions, using Redis cache if available.
        Raises AlpacaApiError on failure.
        """
        params = {"user_id": "default"}  # TODO: Replace with real user_id if available
        def fetch_source():
            try:
                positions = self.alpaca_service.get_positions()
                return [
                    PositionResponse(
                        asset_id=p["asset_id"],
                        symbol=p["symbol"],
                        avg_entry_price=Decimal(p["avg_entry_price"]),
                        qty=Decimal(p["qty"]),
                        side=p["side"],
                        market_value=Decimal(p["market_value"]),
                        cost_basis=Decimal(p["cost_basis"]),
                        unrealized_pl=Decimal(p["unrealized_pl"]),
                        unrealized_plpc=Decimal(p["unrealized_plpc"]),
                        current_price=Decimal(p["current_price"])
                    ) for p in positions
                ]
            except Exception as e:
                raise AlpacaApiError("Failed to fetch positions", details=str(e))
        return self.cache_first(
            RedisKeyType.POSITIONS,
            params,
            PositionResponse,
            fetch_source,
            is_list=True
        )

    # TODO: Add caching integration in the future
