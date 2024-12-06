import time, pytz
from enum import Enum
from colorama import Fore, Style
from datetime import datetime, time, timedelta


class LogLevel(Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACTION = "action"


def is_market_open():
    """
    Determines if the US stock market is currently open.

    The market is considered open if the current time in Eastern Time (ET) is between
    9:30 AM ET and 4:00 PM ET on a trading day.

    Returns:
        bool: True if the market is open, False otherwise.
    """

    market_open = time(9, 30)
    market_close = time(16, 0)
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)
    return market_open <= now_eastern.time() <= market_close


def time_until_market_opens():
    """
    Calculates the time remaining until the US stock market opens (9:30 AM ET).

    The US stock market operates on Eastern Time (ET). If the current time is 
    after the market close (4:00 PM ET), the function calculates the time 
    until the next day's market open.

    Returns:
        float: The number of seconds until the market opens.
    """

    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)
    next_open = datetime.combine(now_eastern.date(), time(9, 30), tzinfo=eastern)
    if now_eastern.time() > time(16, 0):  # If past market close, set to next day
        next_open += timedelta(days=1)
    return (next_open - now_eastern).total_seconds()


def print_log(message, level=LogLevel.INFO):
    """
    Prints a formatted log message with a color-coded level indicator.

    Args:
        message (str): The log message to display.
        level (LogLevel): The severity level of the log (e.g., LogLevel.INFO, LogLevel.SUCCESS, 
                          LogLevel.WARNING, LogLevel.ERROR, LogLevel.ACTION). Defaults to LogLevel.INFO.

    """

    colors = {
        LogLevel.INFO: Fore.CYAN,
        LogLevel.SUCCESS: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.ACTION: Fore.MAGENTA,
    }
    color = colors.get(level, Fore.WHITE)
    print(f"{color}{message}{Style.RESET_ALL}")


def print_positions(positions):
    """
    Prints detailed position information.
    Args:
        positions (list): A list of position objects containing details like symbol, quantity, and market value.
    """

    print_log("\nPositions:\n", LogLevel.WARNING)
    print_log(f"{'Symbol':<10}{'Quantity':<10}{'Current Price':<15}{'Market Value':<15}{'Profit/Loss':<20}")
    print_log("-" * 62)
    for pos in positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        current_price = float(pos.current_price)
        market_value = float(pos.market_value)
        unrealized_pl = float(pos.unrealized_pl)
        print_log(f"{symbol:<10}{qty:<10.2f}{current_price:<15.2f}{market_value:<15.2f}{unrealized_pl:<20.2f}")
    print_log("-" * 62 + "\n")


def print_open_orders(orders):
    """
    Prints detailed open order information.
    Args:
        orders (list): A list of order objects containing details like symbol, side, quantity, and status.
    """

    print_log("\nOpen Orders:\n", LogLevel.WARNING)
    print_log(f"{'Symbol':<10}{'Side':<10}{'Qty':<10}{'Status':<15}")
    print_log("-" * 40)
    for order in orders:
        symbol = order.symbol
        side = order.side.name
        qty = float(order.qty)
        status = order.status.name
        print_log(f"{symbol:<10}{side:<10}{qty:<10.2f}{status:<15}")
    print_log("-" * 40 + "\n")


def print_decisions(decisions):
    """
    Prints the buy and sell decisions along with reasoning for significant events.
    """

    if decisions["buy"]:
        print_log("\nBuy Decisions:")
        for stock, qty in decisions["buy"]:
            if qty > 0:
                print_log(f"BUY {stock} ({qty})", LogLevel.SUCCESS)
    else:
        print_log("\nNothing To Buy", LogLevel.WARNING)


    if decisions["sell"]:
        print_log("\nSell Decisions:")
        for stock, qty in decisions["sell"]:
            if qty > 0:
                print_log(f"SELL {stock} ({qty})", LogLevel.SUCCESS)
    else:
        print_log("\nNothing To Sell", LogLevel.WARNING)

    if decisions["reasoning"]:
        print_log("\nReasoning for Significant Events:")
        for reason in decisions["reasoning"]:
            print_log(reason, LogLevel.ACTION)


def decode_chat_gpt_response(response):
    """
    Decodes the structured ChatGPT response into buy/sell decisions and reasoning.
    """

    print_log("Parsing ChatGPT response ...", LogLevel.ACTION)
    decisions = {"buy": [], "sell": [], "reasoning": []}
    lines = response.splitlines()
    for line in lines:
        line = line.strip()
        if line.startswith("BUY"):
            _, stock, qty, reason = line.split(":", 3)
            decisions["buy"].append((stock.strip(), float(qty.strip())))
            decisions["reasoning"].append(f"BUY {stock.strip()}: {reason.strip()}")
        elif line.startswith("SELL"):
            _, stock, qty, reason = line.split(":", 3)
            decisions["sell"].append((stock.strip(), float(qty.strip())))
            decisions["reasoning"].append(f"SELL {stock.strip()}: {reason.strip()}")
        elif line.startswith("HOLD"):
            if "significant" in line.lower():
                decisions["reasoning"].append(line.strip())
        else:
            decisions["reasoning"].append(f"{line.strip()}")

    return decisions
