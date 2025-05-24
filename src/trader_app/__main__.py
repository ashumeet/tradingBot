"""
Main entry point for Trader App.
This file allows running the app via `python trade.py` or `python -m trader_app`.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from trader_app.api.orders import router as orders_router
from trader_app.api.account import router as account_router
from trader_app.api.market import router as market_router, register_market_exception_handlers
from trader_app.services.exception_handlers import register_exception_handlers
import uvicorn
import threading
import sys

app = FastAPI(title="Trader App API")
register_exception_handlers(app)

@app.get("/")
def root():
    return {"message": "Welcome to the Trader App API!"}

@app.post("/shutdown")
def shutdown(request: Request):
    """Shutdown the server (for development use only)."""
    def stopper():
        import time
        time.sleep(0.1)
        sys.exit(0)
    threading.Thread(target=stopper).start()
    return {"message": "Server shutting down..."}

app.include_router(orders_router)
app.include_router(account_router)
app.include_router(market_router)
register_market_exception_handlers(app)

def main():
    uvicorn.run(app, host="localhost", port=5638)

if __name__ == "__main__":
    main()
