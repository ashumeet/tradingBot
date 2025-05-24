"""
Main entry point for Trader App.
This file allows running the app via `python trade.py` or `python -m trader_app`.
"""

from fastapi import FastAPI, Request
from trader_app.api.orders import router as orders_router
import uvicorn
import threading
import sys

app = FastAPI(title="Trader App API")

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

def main():
    uvicorn.run(app, host="localhost", port=5638)

if __name__ == "__main__":
    main()
