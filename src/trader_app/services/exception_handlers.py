from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .exceptions import OrderValidationError, AlpacaApiError, InternalServerError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(OrderValidationError)
    def order_validation_exception_handler(request: Request, exc: OrderValidationError):
        return JSONResponse(
            status_code=422,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
        )

    @app.exception_handler(AlpacaApiError)
    def alpaca_api_exception_handler(request: Request, exc: AlpacaApiError):
        return JSONResponse(
            status_code=502,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
        )

    @app.exception_handler(InternalServerError)
    def internal_server_exception_handler(request: Request, exc: InternalServerError):
        return JSONResponse(
            status_code=500,
            content={"error": {"code": exc.code, "message": exc.message, "details": exc.details}}
        )
