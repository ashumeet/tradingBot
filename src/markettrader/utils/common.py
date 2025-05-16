"""
Common utilities for the trading bot.

This module provides utility functions that are used across the trading bot,
including time-related functions, logging, and display formatting.
"""

import time, pytz, os
from enum import Enum
from colorama import Fore, Style
from datetime import datetime, time, timedelta


class LogLevel(Enum):
    DEBUG = "debug"  # New debug level
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACTION = "action"


def is_debug_mode():
    """
    Determines if the application is running in debug mode.
    
    Debug mode can be enabled by setting the DEBUG environment variable to "true".
    
    Returns:
        bool: True if debug mode is enabled, False otherwise.
    """
    return os.getenv("DEBUG", "false").lower() == "true"


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


def print_log(message, level=LogLevel.INFO, end="\n"):
    """
    Prints a formatted log message with a color-coded level indicator.

    Args:
        message (str): The log message to display.
        level (LogLevel): The severity level of the log (e.g., LogLevel.INFO, LogLevel.SUCCESS, 
                          LogLevel.WARNING, LogLevel.ERROR, LogLevel.ACTION). Defaults to LogLevel.INFO.
        end (str): String appended after the message, default a newline. Use "" for inline output.
    """
    # Skip DEBUG messages unless debug mode is enabled
    if level == LogLevel.DEBUG and not is_debug_mode():
        return

    colors = {
        LogLevel.DEBUG: Fore.BLUE,
        LogLevel.INFO: Fore.CYAN,
        LogLevel.SUCCESS: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.ACTION: Fore.MAGENTA,
    }
    color = colors.get(level, Fore.WHITE)
    
    # For standard log entries (with newline), include timestamp and level
    if end == "\n":
        timestamp = datetime.now().strftime('%H:%M:%S')
        print(f"{color}[{timestamp}] [{level.value.upper()}] {message}{Style.RESET_ALL}", end=end)
    else:
        # For inline content (no newline), just print the colored message without timestamp
        print(f"{color}{message}{Style.RESET_ALL}", end=end)


def print_positions(positions):
    """
    Prints detailed position information using tabulate.
    Args:
        positions (list): A list of position objects containing details like symbol, quantity, and market value.
    """
    # Prepare data for tabulate
    headers = ["Symbol", "Quantity", "Current Price", "Market Value", "Profit/Loss"]
    table_data = []
    
    for pos in positions:
        symbol = pos.symbol
        qty = float(pos.qty)
        current_price = float(pos.current_price)
        market_value = float(pos.market_value)
        unrealized_pl = float(pos.unrealized_pl)
        table_data.append([symbol, f"{qty:.2f}", f"${current_price:.2f}", f"${market_value:.2f}", f"${unrealized_pl:.2f}"])
    
    print_log("\nPositions:", LogLevel.WARNING)
    display_table(headers, table_data)


def print_open_orders(orders):
    """
    Prints detailed open order information using tabulate.
    Args:
        orders (list): A list of order objects containing details like symbol, side, quantity, and status.
    """
    # Prepare data for tabulate
    headers = ["Symbol", "Side", "Qty", "Status"]
    table_data = []
    
    for order in orders:
        symbol = order.symbol
        side = order.side.name
        qty = float(order.qty)
        status = order.status.name
        table_data.append([symbol, side, f"{qty:.2f}", status])
    
    print_log("\nOpen Orders:", LogLevel.WARNING)
    display_table(headers, table_data)


def print_decisions(decisions):
    """
    Prints the buy and sell decisions along with reasoning using tabulate.
    """
    # Prepare data for buy decisions table
    if decisions["buy"]:
        buy_headers = ["Symbol", "Quantity", "Reasoning"]
        buy_data = []
        
        for i, (stock, qty) in enumerate(decisions["buy"]):
            if qty > 0:
                # Find the matching reasoning entry
                reasoning = "No justification provided"
                for reason in decisions["reasoning"]:
                    if reason.startswith(f"BUY {stock}"):
                        reasoning = reason.replace(f"BUY {stock} ", "")
                        break
                
                buy_data.append([stock, qty, reasoning])
        
        print_log("\nBuy Decisions:", LogLevel.SUCCESS)
        display_table(buy_headers, buy_data)
    else:
        print_log("\nNothing To Buy", LogLevel.WARNING)

    # Prepare data for sell decisions table
    if decisions["sell"]:
        sell_headers = ["Symbol", "Quantity", "Reasoning"]
        sell_data = []
        
        for i, (stock, qty) in enumerate(decisions["sell"]):
            if qty > 0:
                # Find the matching reasoning entry
                reasoning = "No justification provided"
                for reason in decisions["reasoning"]:
                    if reason.startswith(f"SELL {stock}"):
                        reasoning = reason.replace(f"SELL {stock} ", "")
                        break
                
                sell_data.append([stock, qty, reasoning])
        
        print_log("\nSell Decisions:", LogLevel.WARNING)
        display_table(sell_headers, sell_data)
    else:
        print_log("\nNothing To Sell", LogLevel.WARNING)

    # Display other reasoning that isn't buy or sell
    other_reasoning = [reason for reason in decisions["reasoning"]
                       if not (reason.startswith("BUY") or reason.startswith("SELL"))]
    
    if other_reasoning:
        print_log("\nReasoning for Significant Events:", LogLevel.INFO)
        for reason in other_reasoning:
            print_log(reason, LogLevel.ACTION)


def decode_chat_gpt_response(response):
    """
    Decodes the structured ChatGPT response into buy/sell decisions and reasoning.
    
    Format expected:
    BUY: <SYMBOL>: <QUANTITY>: <CONFIDENCE 1-10>: <JUSTIFICATION>
    SELL: <SYMBOL>: <QUANTITY>: <CONFIDENCE 1-10>: <JUSTIFICATION>
    HOLD: <SYMBOL>: <CONFIDENCE 1-10>: <JUSTIFICATION>
    
    Returns:
        dict: A dictionary with "buy", "sell", and "reasoning" keys
    """

    print_log("Parsing ChatGPT response ...", LogLevel.ACTION)
    decisions = {"buy": [], "sell": [], "reasoning": []}
    lines = response.splitlines()
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("BUY:"):
            try:
                parts = line.split(":", 4)
                if len(parts) >= 4:
                    symbol = parts[1].strip()
                    quantity = float(parts[2].strip())
                    confidence = int(parts[3].strip()) if parts[3].strip().isdigit() else 5
                    justification = parts[4].strip() if len(parts) > 4 else "No justification provided"
                    
                    # Only add trades with confidence of 7 or higher
                    if confidence >= 7:
                        decisions["buy"].append((symbol, quantity))
                        decisions["reasoning"].append(f"BUY {symbol} (quantity: {quantity}, confidence: {confidence}/10): {justification}")
                    else:
                        print_log(f"Skipping low-confidence BUY for {symbol} (confidence: {confidence}/10)", LogLevel.WARNING)
            except (ValueError, IndexError) as e:
                print_log(f"Error parsing BUY line: {line} - {str(e)}", LogLevel.ERROR)
                
        elif line.startswith("SELL:"):
            try:
                parts = line.split(":", 4)
                if len(parts) >= 4:
                    symbol = parts[1].strip()
                    quantity = float(parts[2].strip())
                    confidence = int(parts[3].strip()) if parts[3].strip().isdigit() else 5
                    justification = parts[4].strip() if len(parts) > 4 else "No justification provided"
                    
                    # Only add trades with confidence of 7 or higher
                    if confidence >= 7:
                        decisions["sell"].append((symbol, quantity))
                        decisions["reasoning"].append(f"SELL {symbol} (quantity: {quantity}, confidence: {confidence}/10): {justification}")
                    else:
                        print_log(f"Skipping low-confidence SELL for {symbol} (confidence: {confidence}/10)", LogLevel.WARNING)
            except (ValueError, IndexError) as e:
                print_log(f"Error parsing SELL line: {line} - {str(e)}", LogLevel.ERROR)
                
        elif line.startswith("HOLD:"):
            try:
                parts = line.split(":", 3)
                if len(parts) >= 3:
                    symbol = parts[1].strip()
                    confidence = int(parts[2].strip()) if parts[2].strip().isdigit() else 5
                    justification = parts[3].strip() if len(parts) > 3 else "No justification provided"
                    
                    decisions["reasoning"].append(f"HOLD {symbol} (confidence: {confidence}/10): {justification}")
            except (ValueError, IndexError) as e:
                print_log(f"Error parsing HOLD line: {line} - {str(e)}", LogLevel.ERROR)
        
        # If it's part of a reasoning or other text, just add it as is
        elif not any(line.startswith(prefix) for prefix in ["BUY:", "SELL:", "HOLD:"]) and len(line) > 5:
            decisions["reasoning"].append(line)

    return decisions 


def display_table(headers, data, title=None):
    """
    Display data as a formatted table using the tabulate library with fancy formatting and colors.
    
    Args:
        headers (list): List of column headers
        data (list): List of rows, where each row is a list of values matching the headers
        title (str, optional): Optional title for the table
            
    Returns:
        None: Prints formatted table to console
    """
    if not headers or not data:
        print_log("No data to display in table", LogLevel.WARNING)
        return
    
    try:
        from tabulate import tabulate
        from colorama import Fore, Style
        
        # Print title if provided
        if title:
            print_log(title, LogLevel.SUCCESS)
        
        # Process data to add colors where appropriate
        colored_data = []
        for row in data:
            colored_row = []
            for i, cell in enumerate(row):
                cell_str = str(cell)
                
                # Add colors based on content
                if "+" in cell_str and "%" in cell_str:  # Positive percentage
                    colored_row.append(f"{Fore.GREEN}{cell_str}{Style.RESET_ALL}")
                elif "-" in cell_str and "%" in cell_str:  # Negative percentage
                    colored_row.append(f"{Fore.RED}{cell_str}{Style.RESET_ALL}")
                elif "Up" in cell_str or "▲" in cell_str or "↗" in cell_str:  # Uptrend
                    colored_row.append(f"{Fore.GREEN}{cell_str}{Style.RESET_ALL}")
                elif "Down" in cell_str or "▼" in cell_str or "↘" in cell_str:  # Downtrend
                    colored_row.append(f"{Fore.RED}{cell_str}{Style.RESET_ALL}")
                elif "Neutral" in cell_str or "→" in cell_str:  # Neutral trend
                    colored_row.append(f"{Fore.CYAN}{cell_str}{Style.RESET_ALL}")
                elif "BUY" in cell_str:  # Buy side
                    colored_row.append(f"{Fore.GREEN}{cell_str}{Style.RESET_ALL}")
                elif "SELL" in cell_str:  # Sell side
                    colored_row.append(f"{Fore.RED}{cell_str}{Style.RESET_ALL}")
                else:
                    colored_row.append(cell_str)
            
            colored_data.append(colored_row)
            
        # Use grid format for nice table structure
        table = tabulate(colored_data, headers=headers, tablefmt="heavy_outline")
        print(table)
        
    except ImportError:
        # Instead of just a warning, also suggest installing the package with pip
        print_log("Tabulate library not installed. Run: pip install tabulate", LogLevel.ERROR)
        
        # Fallback to simple text table if tabulate is not available
        if title:
            print_log(title, LogLevel.SUCCESS)
        
        # Print headers
        header_str = "  ".join(str(h) for h in headers)
        print_log(header_str, LogLevel.INFO)
        print_log("-" * len(header_str), LogLevel.INFO)
        
        # Print rows
        for row in data:
            row_str = "  ".join(str(cell) for cell in row)
            print_log(row_str, LogLevel.INFO) 