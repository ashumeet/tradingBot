"""
Alpaca API integration module.

This module provides functions for interacting with the Alpaca trading platform,
including fetching portfolio data, stock data, and executing trades.
"""

from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.trading.requests import GetOrdersRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta

from ..config import (
    ALPACA_API_KEY, 
    ALPACA_SECRET_KEY, 
    ENVIRONMENT,
    ALPACA_API_URL,
    mask_api_key
)
from ..utils import common


# Log masked API key for debugging if needed
if common.is_debug_mode():
    common.print_log(f"Using Alpaca API key: {mask_api_key(ALPACA_API_KEY)}", common.LogLevel.DEBUG)
    common.print_log(f"Environment: {ENVIRONMENT}", common.LogLevel.DEBUG)
    common.print_log(f"Using Alpaca endpoint: {ALPACA_API_URL}", common.LogLevel.DEBUG)

# Initialize Alpaca clients - paper=True for paper trading, paper=False for live trading
trading_client = TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=(ENVIRONMENT == 'paper'))
data_client = StockHistoricalDataClient(api_key=ALPACA_API_KEY, secret_key=ALPACA_SECRET_KEY)


def fetch_portfolio():
    """
    Fetches Alpaca portfolio and open orders, and prints their details.
    Returns:
        dict: A dictionary containing buying power, positions, and open orders.
    """

    common.print_log("Fetching portfolio details and open orders ...\n", common.LogLevel.ACTION)
    account = trading_client.get_account()
    positions = trading_client.get_all_positions()
    order_request = GetOrdersRequest(status="open")
    orders = trading_client.get_orders(filter=order_request)

    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)

    common.print_log(f"Portfolio Value: ${portfolio_value:.2f}", common.LogLevel.SUCCESS)
    common.print_log(f"Buying Power: ${buying_power:.2f}\n", common.LogLevel.SUCCESS)

    if positions:
        common.print_positions(positions)
    else:
        common.print_log("No positions found in the portfolio.", common.LogLevel.WARNING)

    if orders:
        common.print_open_orders(orders)
    else:
        common.print_log("No open orders found.\n", common.LogLevel.WARNING)

    portfolio = {
        "buying_power": buying_power,
        "positions": {pos.symbol: float(pos.qty) for pos in positions},
        "open_orders": [
            {
                "symbol": order.symbol,
                "side": order.side,
                "qty": float(order.qty),
                "status": order.status,
            }
            for order in orders
        ]
    }
    return portfolio


def fetch_stock_data(stocks):
    """
    Fetches historical stock data for the given list of stocks.

    Args:
        stocks (list): A list of stock symbols to fetch data for.

    Returns:
        data: A dictionary mapping stock symbols to their closing prices.
    """

    common.print_log("Fetching stock data ...", common.LogLevel.ACTION)
    data = {}
    failed_stocks = []

    for stock in stocks:
        try:
            # Use a fixed time window in the past to ensure data availability
            end = datetime.now() - timedelta(days=1)  # Use yesterday to ensure market was open
            start = end - timedelta(days=5)  # Get 5 days of data
            
            request_params = StockBarsRequest(
                symbol_or_symbols=stock,
                timeframe=TimeFrame.Day,  # Switch to daily data which is more reliable
                start=start,
                end=end,
                limit=10
            )
            bars = data_client.get_stock_bars(request_params)
            if bars.df is not None and not bars.df.empty:
                closing_prices = bars.df["close"].tolist()
                data[stock] = closing_prices
            else:
                common.print_log(f"No valid data for {stock}.", common.LogLevel.WARNING)
                failed_stocks.append(stock)
        except Exception as e:
            common.print_log(f"Error fetching data for {stock}: {e}", common.LogLevel.ERROR)
            failed_stocks.append(stock)

    common.print_log("Stock data fetching completed.", common.LogLevel.SUCCESS)
    if failed_stocks:
        common.print_log(f"Failed to fetch data for: {', '.join(failed_stocks)}", common.LogLevel.WARNING)

    if data:
        common.print_log("Stock data summary:", common.LogLevel.SUCCESS)
        for stock, prices in data.items():
            print(f"Stock: {stock}")
            print(f"  Closing Prices (last {len(prices)} minutes): {prices}")
            print(f"  Latest Price: {prices[-1]}")
            print(f"  Average Price: {sum(prices) / len(prices):.2f}")
            print("-" * 40)

    return data


def execute_trades(decisions):
    """
    Executes buy and sell orders based on the provided decisions.

    Args:
        decisions (dict): A dictionary with "buy" and "sell" keys, each containing a list of tuples.
                          Each tuple includes a stock symbol (str) and a quantity (int).

    """

    common.print_log("\nExecuting trades ...", common.LogLevel.ACTION)

    for stock, qty in decisions["sell"]:
        if qty == 0:
            continue
        try:
            market_order_data = MarketOrderRequest(
                symbol=stock,
                qty=qty,
                side=OrderSide.SELL,
                time_in_force=TimeInForce.DAY
            )
            trading_client.submit_order(order_data=market_order_data)
            common.print_log(f"Sold {qty} of {stock}.", common.LogLevel.SUCCESS)
        except Exception as e:
            common.print_log(f"Failed to sell {qty} of {stock}. Error: {e}", common.LogLevel.ERROR)

    for stock, qty in decisions["buy"]:
        if qty == 0:
            continue
        try:
            market_order_data = MarketOrderRequest(
                symbol=stock,
                qty=qty,
                side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY
            )
            trading_client.submit_order(order_data=market_order_data)
            common.print_log(f"Bought {qty} of {stock}.", common.LogLevel.SUCCESS)
        except Exception as e:
            common.print_log(f"Failed to buy {qty} of {stock}. Error: {e}", common.LogLevel.ERROR) 