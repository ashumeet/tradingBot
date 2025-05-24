"""
AlpacaService: Provides a clean, reusable interface to Alpaca API functionality.

- Initializes TradingClient and StockHistoricalDataClient using configuration
- Stateless: no mutable instance state
- Handles API errors and logs operations

Usage:
    from trader_app.services.alpaca_service import AlpacaService
    from trader_app.core import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_API_URL

    service = AlpacaService(
        api_key=ALPACA_API_KEY,
        secret_key=ALPACA_SECRET_KEY,
        api_url=ALPACA_API_URL
    )
    account = service.get_account()
"""

from alpaca.trading.client import TradingClient
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.common.exceptions import APIError
from trader_app.core import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_API_URL
import logging
import time

class AlpacaServiceException(Exception):
    """Custom exception for AlpacaService errors."""
    pass

class AlpacaService:
    """
    Service for interacting with Alpaca Trading and Market Data APIs.
    Stateless: all configuration is passed at initialization.
    """
    def __init__(self, api_key: str, secret_key: str, api_url: str = None):
        self.trading_client = TradingClient(api_key, secret_key, paper=("paper" in (api_url or "").lower()))
        self.data_client = StockHistoricalDataClient(api_key, secret_key)
        self.api_url = api_url
        self.logger = logging.getLogger("AlpacaService")
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s %(name)s: %(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def health_check(self) -> bool:
        """Check if the Alpaca API is reachable and credentials are valid."""
        try:
            account = self.trading_client.get_account()
            self.logger.info("Alpaca account loaded: %s", account.id)
            return True
        except APIError as e:
            self.logger.error("Alpaca health check failed: %s", e)
            return False
        except Exception as e:
            self.logger.error("Unexpected error during Alpaca health check: %s", e)
            return False

    def get_account(self):
        """Retrieve Alpaca account information."""
        try:
            account = self.trading_client.get_account()
            self.logger.info("Fetched Alpaca account info.")
            return account
        except APIError as e:
            self.logger.error("Failed to fetch account info: %s", e)
            raise

    def get_stock_bars(self, symbol: str, timeframe: str = "1Day", start: str = None, end: str = None, limit: int = 100):
        """Retrieve historical price bars for a stock symbol."""
        try:
            bars = self.data_client.get_stock_bars(symbol, timeframe, start=start, end=end, limit=limit)
            self.logger.info("Fetched bars for %s", symbol)
            return bars
        except APIError as e:
            self.logger.error("Failed to fetch bars for %s: %s", symbol, e)
            raise

    def get_latest_trade(self, symbol: str):
        """Get the latest trade for a symbol."""
        try:
            trade = self.data_client.get_latest_trade(symbol)
            self.logger.info("Fetched latest trade for %s", symbol)
            return trade
        except APIError as e:
            self.logger.error("Failed to fetch latest trade for %s: %s", symbol, e)
            raise

    def get_latest_quote(self, symbol: str):
        """Get the latest quote for a symbol."""
        try:
            quote = self.data_client.get_latest_quote(symbol)
            self.logger.info("Fetched latest quote for %s", symbol)
            return quote
        except APIError as e:
            self.logger.error("Failed to fetch latest quote for %s: %s", symbol, e)
            raise

    def get_positions(self):
        """Retrieve current positions."""
        try:
            positions = self.trading_client.get_all_positions()
            self.logger.info("Fetched positions.")
            return positions
        except APIError as e:
            self.logger.error("Failed to fetch positions: %s", e)
            raise

    def get_clock(self):
        """Get market clock information."""
        try:
            clock = self.trading_client.get_clock()
            self.logger.info("Fetched market clock.")
            return clock
        except APIError as e:
            self.logger.error("Failed to fetch market clock: %s", e)
            raise

    def submit_order(self, symbol: str, qty: int, side: str, type_: str, time_in_force: str, **kwargs):
        """Submit a new order to Alpaca."""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                order = self.trading_client.submit_order(
                    symbol=symbol,
                    qty=qty,
                    side=side,
                    type=type_,
                    time_in_force=time_in_force,
                    **kwargs
                )
                self.logger.info("Submitted order: %s %d %s (%s)", side, qty, symbol, type_)
                return order
            except APIError as e:
                if 'rate limit' in str(e).lower() and attempt < max_retries - 1:
                    self.logger.warning("Rate limit hit, retrying (%d/%d)...", attempt + 1, max_retries)
                    time.sleep(2 ** attempt)
                    continue
                self.logger.error("Failed to submit order for %s: %s", symbol, e)
                raise AlpacaServiceException(f"Order submission failed: {e}")
            except Exception as e:
                self.logger.error("Unexpected error submitting order for %s: %s", symbol, e)
                raise AlpacaServiceException(f"Unexpected error: {e}")

    def get_orders(self, status: str = "open"):
        """Retrieve open or filled orders."""
        try:
            orders = self.trading_client.get_orders(status=status)
            self.logger.info("Fetched %s orders.", status)
            return orders
        except APIError as e:
            self.logger.error("Failed to fetch orders: %s", e)
            raise

    def get_order_by_id(self, order_id: str):
        """Retrieve a specific order by ID."""
        try:
            order = self.trading_client.get_order_by_id(order_id)
            self.logger.info("Fetched order by ID: %s", order_id)
            return order
        except APIError as e:
            self.logger.error("Failed to fetch order %s: %s", order_id, e)
            raise

    def cancel_order(self, order_id: str):
        """Cancel an existing order by ID."""
        try:
            result = self.trading_client.cancel_order(order_id)
            self.logger.info("Cancelled order: %s", order_id)
            return result
        except APIError as e:
            self.logger.error("Failed to cancel order %s: %s", order_id, e)
            raise

    def replace_order(self, order_id: str, **kwargs):
        """Replace (modify) an existing order by ID."""
        try:
            order = self.trading_client.replace_order(order_id, **kwargs)
            self.logger.info("Replaced order: %s", order_id)
            return order
        except APIError as e:
            self.logger.error("Failed to replace order %s: %s", order_id, e)
            raise
