import requests, config
from utils.common import print_log


# Use keys from the config file
ALPACA_API_KEY = config.ALPACA_API_KEY
ALPACA_SECRET_KEY = config.ALPACA_SECRET_KEY
ALPACA_BASE_URL = "https://api.alpaca.markets"

# Fetch Alpaca portfolio and open orders
def fetch_portfolio():
    print_log("Fetching portfolio details and open orders...\n", level="info")
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    }

    # Fetch account and positions
    account_info = requests.get(f"{ALPACA_BASE_URL}/v2/account", headers=headers).json()
    positions = requests.get(f"{ALPACA_BASE_URL}/v2/positions", headers=headers).json()
    open_orders = requests.get(f"{ALPACA_BASE_URL}/v2/orders", headers=headers).json()

    # Extract relevant account details
    portfolio_value = float(account_info.get("portfolio_value", 0))
    buying_power = float(account_info.get("buying_power", 0))

    print_log(f"Portfolio Value: ${portfolio_value:.2f}", level="success")
    print_log(f"Buying Power: ${buying_power:.2f}\n", level="success")

    # Extract detailed position information
    if positions:
        print_log("\nPositions:\n", level="warning")
        print_log(f"{'Symbol':<10}{'Quantity':<10}{'Current Price':<15}{'Market Value':<15}{'Profit/Loss ($)':<20}")
        print_log("-" * 70, level="info")
        for pos in positions:
            symbol = pos["symbol"]
            qty = float(pos["qty"])
            current_price = float(pos["current_price"])
            market_value = float(pos["market_value"])
            unrealized_pl = float(pos["unrealized_pl"])
            print_log(f"{symbol:<10}{qty:<10.2f}{current_price:<15.2f}{market_value:<15.2f}{unrealized_pl:<20.2f}")
        print_log("-" * 70 + "\n", level="info")
    else:
        print_log("No positions found in the portfolio.", level="warning")

    # Extract and display open orders
    if open_orders:
        print_log("\nOpen Orders:\n", level="warning")
        print_log(f"{'Symbol':<10}{'Side':<10}{'Qty':<10}{'Status':<15}")
        print_log("-" * 40, level="info")
        for order in open_orders:
            symbol = order["symbol"]
            side = order["side"]
            qty = float(order["qty"])
            status = order["status"]
            print_log(f"{symbol:<10}{side:<10}{qty:<10.2f}{status:<15}")
        print_log("-" * 40 + "\n", level="info")
    else:
        print_log("No open orders found.\n", level="warning")

    # Return the portfolio data with open orders and updated values
    portfolio = {
        "buying_power": buying_power,
        "positions": {pos["symbol"]: float(pos["qty"]) for pos in positions},
        "open_orders": [
            {
                "symbol": order["symbol"],
                "side": order["side"],
                "qty": float(order["qty"]),
                "status": order["status"],
                "current_price": float(requests.get(f"{ALPACA_BASE_URL}/v2/assets/{order['symbol']}/quote", headers=headers).json().get("last", 0)),  # Latest price
                "total_value": float(order["qty"]) * float(requests.get(f"{ALPACA_BASE_URL}/v2/assets/{order['symbol']}/quote", headers=headers).json().get("last", 0)),  # Price * Qty
            }
            for order in open_orders
        ]
    }
    return portfolio

# Fetch stock data for the portfolio and recommended stocks
def fetch_stock_data(stocks):
    print_log("Fetching stock data...", level="info")
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    }
    data = {}
    failed_stocks = []

    # Fetch data for each stock
    for stock in stocks:
        url = f"{ALPACA_BASE_URL}/v2/stocks/{stock}/bars?timeframe=1Min&limit=10"
        print_log(f"Requesting URL: {url}", level="info")  # Debugging the API URL
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            try:
                response_json = response.json()
                bars = response_json.get("bars", None)
                if isinstance(bars, list) and bars:
                    data[stock] = [bar["c"] for bar in bars]  # Extract closing prices
                else:
                    print_log(f"No valid data for {stock}. Bars: {bars}", level="warning")
                    failed_stocks.append(stock)
            except Exception as e:
                print_log(f"Error processing data for {stock}: {e}", level="error")
                failed_stocks.append(stock)
        elif response.status_code == 404:
            print_log(f"Failed to fetch data for {stock}. Status: {response.status_code}. Response: Not Found.", level="warning")
            failed_stocks.append(stock)
        else:
            print_log(f"Failed to fetch data for {stock}. Status: {response.status_code}. Response: {response.text}", level="warning")
            failed_stocks.append(stock)

    # Log successes and failures
    print_log("Stock data fetching completed.", level="success")
    if failed_stocks:
        print_log(f"Failed to fetch data for: {', '.join(failed_stocks)}", level="warning")

    # Represent the stock data
    if data:
        print_log("Stock data summary:", level="info")
        for stock, prices in data.items():
            print(f"Stock: {stock}")
            print(f"  Closing Prices (last {len(prices)} minutes): {prices}")
            print(f"  Latest Price: {prices[-1]}")
            print(f"  Average Price: {sum(prices) / len(prices):.2f}")
            print("-" * 40)

    return data

# Execute trades based on decisions
def execute_trades(decisions):
    print_log("Executing trades instantly...", level="action")
    headers = {
        "APCA-API-KEY-ID": ALPACA_API_KEY,
        "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
    }
    # Execute buy orders immediately
    for stock, qty in decisions["buy"]:
        response = requests.post(f"{ALPACA_BASE_URL}/v2/orders", headers=headers, json={
            "symbol": stock,
            "qty": qty,
            "side": "buy",
            "type": "market",
            "time_in_force": "day",
        })
        print_log(f"Bought {qty} of {stock}. Response: {response.status_code}", level="success")

    # Execute sell orders immediately
    for stock, qty in decisions["sell"]:
        response = requests.post(f"{ALPACA_BASE_URL}/v2/orders", headers=headers, json={
            "symbol": stock,
            "qty": qty,
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
        })
        print_log(f"Sold {qty} of {stock}. Response: {response.status_code}", level="success")
