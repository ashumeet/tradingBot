from fastapi import APIRouter, Depends, status, Query, HTTPException, Request
from trader_app.models.market import BarModel, QuoteModel, SymbolListRequest, BarsResponse, QuotesResponse
from trader_app.services.market_data_service import MarketDataService
from trader_app.services.exceptions import InvalidSymbolError, MarketDataValidationError, AlpacaApiError
from typing import List, Optional
from fastapi.responses import JSONResponse
from src.trader_app.security.dependencies import get_ssh_authenticated_user

router = APIRouter(prefix="/api/v1/marketdata", tags=["marketdata"])

def get_market_data_service() -> MarketDataService:
    return MarketDataService()

def register_market_exception_handlers(app):
    @app.exception_handler(InvalidSymbolError)
    async def invalid_symbol_exception_handler(request: Request, exc: InvalidSymbolError):
        return JSONResponse(
            status_code=404,
            content={"code": exc.code, "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(MarketDataValidationError)
    async def market_data_validation_exception_handler(request: Request, exc: MarketDataValidationError):
        return JSONResponse(
            status_code=422,
            content={"code": exc.code, "message": exc.message, "details": exc.details}
        )

    @app.exception_handler(AlpacaApiError)
    async def alpaca_api_error_handler(request: Request, exc: AlpacaApiError):
        return JSONResponse(
            status_code=502,
            content={"code": exc.code, "message": exc.message, "details": exc.details}
        )

@router.get(
    "/bars/{symbol}",
    response_model=BarsResponse,
    summary="Get historical bars for a symbol",
    description="Returns historical OHLCV bars for a given symbol.",
    responses={
        200: {"description": "Bars returned successfully."},
        404: {"description": "Symbol not found."},
        422: {"description": "Invalid parameters."},
        502: {"description": "Alpaca API error."}
    }
)
def get_bars(
    symbol: str,
    timeframe: str = Query("1Day", description="Timeframe, e.g., 1Day, 1Min, etc."),
    start: Optional[str] = Query(None, description="Start date (ISO format)"),
    end: Optional[str] = Query(None, description="End date (ISO format)"),
    limit: int = Query(100, gt=0, le=1000, description="Max number of bars to return (1-1000)"),
    service: MarketDataService = Depends(get_market_data_service),
    auth=Depends(get_ssh_authenticated_user)
):
    try:
        bars = service.get_bars_for_symbol(symbol, timeframe, start, end, limit)
        if not bars:
            raise HTTPException(status_code=404, detail="No bars found for symbol.")
        return BarsResponse(symbol=symbol, bars=bars)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.get(
    "/quotes/latest/{symbol}",
    response_model=QuoteModel,
    summary="Get latest quote for a symbol",
    description="Returns the latest quote for a given symbol.",
    responses={
        200: {"description": "Quote returned successfully."},
        404: {"description": "Symbol not found."},
        502: {"description": "Alpaca API error."}
    }
)
def get_latest_quote(symbol: str, service: MarketDataService = Depends(get_market_data_service), auth=Depends(get_ssh_authenticated_user)):
    try:
        quote = service.get_latest_quote_for_symbol(symbol)
        return quote
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@router.post(
    "/quotes/latest",
    response_model=QuotesResponse,
    summary="Get latest quotes for multiple symbols",
    description="Returns the latest quotes for a list of symbols.",
    responses={
        200: {"description": "Quotes returned successfully."},
        422: {"description": "Invalid request body."},
        502: {"description": "Alpaca API error."}
    }
)
def get_latest_quotes(request: SymbolListRequest, service: MarketDataService = Depends(get_market_data_service), auth=Depends(get_ssh_authenticated_user)):
    try:
        quotes = service.get_latest_quotes_for_symbols(request.symbols)
        return QuotesResponse(quotes=quotes)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) 