from trader_app.models.market import BarModel, QuoteModel
from trader_app.services.alpaca_service import AlpacaService, AlpacaServiceException
from typing import List, Optional
from decimal import Decimal
from datetime import datetime
from trader_app.services.exceptions import InvalidSymbolError, MarketDataValidationError, AlpacaApiError
from trader_app.utils.redis_schema import RedisKeyType
from trader_app.services.base_caching_service import BaseCachingService

class MarketDataService(BaseCachingService):
    def __init__(self, alpaca_service: Optional[AlpacaService] = None):
        super().__init__()
        self.alpaca_service = alpaca_service or AlpacaService()

    def get_bars_for_symbol(self, symbol: str, timeframe: str, start: Optional[str] = None, end: Optional[str] = None, limit: int = 100) -> List[BarModel]:
        """
        Fetch historical bars for a symbol from Alpaca and map to BarModel list.
        Uses Redis cache if available.
        Raises InvalidSymbolError, MarketDataValidationError, AlpacaApiError.
        """
        params = {"symbol": symbol, "timeframe": timeframe}
        def fetch_source():
            try:
                bars = self.alpaca_service.get_bars(symbol, timeframe, start, end, limit)
                if bars is None:
                    raise InvalidSymbolError(f"Symbol not found: {symbol}")
                bar_models = []
                for bar in bars:
                    try:
                        bar_models.append(BarModel(
                            timestamp=bar.t,
                            open=bar.o,
                            high=bar.h,
                            low=bar.l,
                            close=bar.c,
                            volume=bar.v
                        ))
                    except Exception as e:
                        raise MarketDataValidationError(f"Invalid bar data for {symbol}", details=str(e))
                return bar_models
            except InvalidSymbolError:
                raise
            except MarketDataValidationError:
                raise
            except Exception as e:
                raise AlpacaApiError(f"Failed to fetch bars for {symbol}", details=str(e))
        return self.cache_first(
            RedisKeyType.STOCK_BARS,
            params,
            BarModel,
            fetch_source,
            is_list=True
        )

    def get_latest_quote_for_symbol(self, symbol: str) -> QuoteModel:
        """
        Fetch the latest quote for a symbol from Alpaca and map to QuoteModel.
        Uses Redis cache if available.
        Raises InvalidSymbolError, AlpacaApiError.
        """
        params = {"symbol": symbol}
        def fetch_source():
            try:
                quote = self.alpaca_service.get_latest_quote(symbol)
                if quote is None:
                    raise InvalidSymbolError(f"Symbol not found: {symbol}")
                try:
                    model = QuoteModel(
                        symbol=symbol,
                        timestamp=quote.t,
                        ask_price=quote.ap,
                        ask_size=quote.asize,
                        bid_price=quote.bp,
                        bid_size=quote.bsize
                    )
                except Exception as e:
                    raise MarketDataValidationError(f"Invalid quote data for {symbol}", details=str(e))
                return model
            except InvalidSymbolError:
                raise
            except MarketDataValidationError:
                raise
            except Exception as e:
                raise AlpacaApiError(f"Failed to fetch quote for {symbol}", details=str(e))
        return self.cache_first(
            RedisKeyType.STOCK_QUOTE,
            params,
            QuoteModel,
            fetch_source,
            is_list=False
        )

    def get_latest_quotes_for_symbols(self, symbols: List[str]) -> List[QuoteModel]:
        """
        Fetch latest quotes for multiple symbols from Alpaca and map to QuoteModel list.
        Uses Redis cache if available for each symbol.
        Raises InvalidSymbolError, AlpacaApiError.
        """
        results = []
        missing = []
        for symbol in symbols:
            params = {"symbol": symbol}
            cached = self.get_from_cache(RedisKeyType.STOCK_QUOTE, params, QuoteModel)
            if cached:
                results.append(cached)
            else:
                missing.append(symbol)
        # Fetch missing from API
        if missing:
            try:
                quotes = self.alpaca_service.get_latest_quotes(missing)
                if quotes is None:
                    raise InvalidSymbolError(f"No quotes found for symbols: {missing}")
                for symbol, quote in quotes.items():
                    if quote is None:
                        continue
                    try:
                        model = QuoteModel(
                            symbol=symbol,
                            timestamp=quote.t,
                            ask_price=quote.ap,
                            ask_size=quote.asize,
                            bid_price=quote.bp,
                            bid_size=quote.bsize
                        )
                        results.append(model)
                        params = {"symbol": symbol}
                        self.set_cache(RedisKeyType.STOCK_QUOTE, params, model)
                    except Exception as e:
                        raise MarketDataValidationError(f"Invalid quote data for {symbol}", details=str(e))
            except InvalidSymbolError:
                raise
            except MarketDataValidationError:
                raise
            except Exception as e:
                raise AlpacaApiError(f"Failed to fetch quotes for {missing}", details=str(e))
        if not results:
            raise InvalidSymbolError(f"No valid quotes found for symbols: {symbols}")
        return results

    # TODO: Add cache key generation methods (generate_bars_cache_key, generate_quote_cache_key)
    # TODO: Add placeholder methods for caching integration
    # TODO: Add logging throughout the service

    def generate_bars_cache_key(self, symbol, timeframe, start, end, limit):
        # Implementation of generate_bars_cache_key method
        pass

    def generate_quote_cache_key(self, symbol):
        # Implementation of generate_quote_cache_key method
        pass

    def generate_bars_cache_key(self, symbol, timeframe, start, end, limit):
        # Implementation of generate_bars_cache_key method
        pass

    def generate_quote_cache_key(self, symbol):
        # Implementation of generate_quote_cache_key method
        pass 