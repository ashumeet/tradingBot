from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.trading.requests import GetOrdersRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import config
import utils.common as common

# Initialize the Alpaca Trading and Data API clients
trading_client = TradingClient(config.ALPACA_API_KEY, config.ALPACA_SECRET_KEY, paper=False)
data_client = StockHistoricalDataClient(api_key=config.ALPACA_API_KEY, secret_key=config.ALPACA_SECRET_KEY)

# Fetch Alpaca portfolio and open orders
def fetch_portfolio():
    common.print_log("Fetching portfolio details and open orders...\n", level="info")

    # Fetch account and positions
    account = trading_client.get_account()
    positions = trading_client.get_all_positions()

    # Fetch open orders using the correct request model
    order_request = GetOrdersRequest(status="open")
    orders = trading_client.get_orders(filter=order_request)

    # Extract relevant account details
    portfolio_value = float(account.portfolio_value)
    buying_power = float(account.buying_power)

    common.print_log(f"Portfolio Value: ${portfolio_value:.2f}", level="success")
    common.print_log(f"Buying Power: ${buying_power:.2f}\n", level="success")

    # Extract detailed position information
    if positions:
        common.print_log("\nPositions:\n", level="warning")
        common.print_log(f"{'Symbol':<10}{'Quantity':<10}{'Current Price':<15}{'Market Value':<15}{'Profit/Loss ($)':<20}")
        common.print_log("-" * 70, level="info")
        for pos in positions:
            symbol = pos.symbol
            qty = float(pos.qty)
            current_price = float(pos.current_price)
            market_value = float(pos.market_value)
            unrealized_pl = float(pos.unrealized_pl)
            common.print_log(f"{symbol:<10}{qty:<10.2f}{current_price:<15.2f}{market_value:<15.2f}{unrealized_pl:<20.2f}")
        common.print_log("-" * 70 + "\n", level="info")
    else:
        common.print_log("No positions found in the portfolio.", level="warning")

    # Extract and display open orders
    if orders:
        common.print_log("\nOpen Orders:\n", level="warning")
        common.print_log(f"{'Symbol':<10}{'Side':<10}{'Qty':<10}{'Status':<15}")
        common.print_log("-" * 40, level="info")
        for order in orders:
            symbol = order.symbol
            side = order.side
            qty = float(order.qty)
            status = order.status
            common.print_log(f"{symbol:<10}{side:<10}{qty:<10.2f}{status:<15}")
        common.print_log("-" * 40 + "\n", level="info")
    else:
        common.print_log("No open orders found.\n", level="warning")

    # Return the portfolio data with open orders and updated values
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

# Fetch stock data for the portfolio and recommended stocks
def fetch_stock_data(stocks):
    common.print_log("Fetching stock data...", level="info")
    data = {}
    failed_stocks = []

    # Fetch data for each stock
    for stock in stocks:
        try:
            request_params = StockBarsRequest(
                symbol_or_symbols=stock,
                timeframe=TimeFrame.Minute,
                start=datetime.now() - timedelta(minutes=10)  # Get data from the last 10 minutes
            )
            bars = data_client.get_stock_bars(request_params)
            if bars.df is not None and not bars.df.empty:
                closing_prices = bars.df["close"].tolist()
                data[stock] = closing_prices
            else:
                common.print_log(f"No valid data for {stock}.", level="warning")
                failed_stocks.append(stock)
        except Exception as e:
            common.print_log(f"Error fetching data for {stock}: {e}", level="error")
            failed_stocks.append(stock)

    # Log successes and failures
    common.print_log("Stock data fetching completed.", level="success")
    if failed_stocks:
        common.print_log(f"Failed to fetch data for: {', '.join(failed_stocks)}", level="warning")

    # Represent the stock data
    if data:
        common.print_log("Stock data summary:", level="info")
        for stock, prices in data.items():
            print(f"Stock: {stock}")
            print(f"  Closing Prices (last {len(prices)} minutes): {prices}")
            print(f"  Latest Price: {prices[-1]}")
            print(f"  Average Price: {sum(prices) / len(prices):.2f}")
            print("-" * 40)

    return data

# Execute trades based on decisions
def execute_trades(decisions):
    common.print_log("Executing trades instantly...", level="action")

    # Execute buy orders immediately
    for stock, qty in decisions["buy"]:
        market_order_data = MarketOrderRequest(
            symbol=stock,
            qty=qty,
            side=OrderSide.BUY,
            time_in_force=TimeInForce.DAY
        )
        trading_client.submit_order(order_data=market_order_data)
        common.print_log(f"Bought {qty} of {stock}.", level="success")

    # Execute sell orders immediately
    for stock, qty in decisions["sell"]:
        market_order_data = MarketOrderRequest(
            symbol=stock,
            qty=qty,
            side=OrderSide.SELL,
            time_in_force=TimeInForce.DAY
        )
        trading_client.submit_order(order_data=market_order_data)
        common.print_log(f"Sold {qty} of {stock}.", level="success")
