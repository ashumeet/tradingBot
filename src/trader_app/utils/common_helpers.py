"""
Common Helpers for trader_app

This module provides generic utility functions for logging, time, and display.
All functions are stateless and reusable across the application.
"""

import os
from enum import Enum
from colorama import Fore, Style
from datetime import datetime, time as dt_time, timedelta
from typing import Any, Optional, List

class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACTION = "action"

def print_log(message: str, level: LogLevel = LogLevel.INFO) -> None:
    """
    Print a formatted log message with color based on log level.
    Args:
        message (str): The message to print
        level (LogLevel): The log level (default: INFO)
    """
    color = {
        LogLevel.DEBUG: Fore.CYAN,
        LogLevel.INFO: Fore.WHITE,
        LogLevel.SUCCESS: Fore.GREEN,
        LogLevel.WARNING: Fore.YELLOW,
        LogLevel.ERROR: Fore.RED,
        LogLevel.ACTION: Fore.MAGENTA,
    }.get(level, Fore.WHITE)
    print(f"{color}{level.value.upper():<7}{Style.RESET_ALL} {message}")

def is_debug_mode() -> bool:
    """
    Returns True if DEBUG environment variable is set to 'true'.
    """
    return os.getenv("DEBUG", "false").lower() == "true"


def display_table(headers: List[str], data: List[List[Any]], title: Optional[str] = None) -> None:
    """
    Display data as a formatted table using tabulate.
    Args:
        headers (List[str]): Column headers
        data (List[List[Any]]): Table rows
        title (Optional[str]): Optional table title
    """
    if not headers or not data:
        print_log("No data to display in table", LogLevel.WARNING)
        return
    try:
        from tabulate import tabulate
        table = tabulate(data, headers=headers, tablefmt="fancy_grid", floatfmt=".2f")
        if title:
            print(f"\n{Style.BRIGHT}{title}{Style.RESET_ALL}")
        print(table)
    except ImportError:
        print_log("tabulate library is not installed. Please add it to requirements.txt.", LogLevel.ERROR)
        for row in [headers] + data:
            print("\t".join(str(x) for x in row))


def is_market_open(
    open_time: dt_time = dt_time(9, 30),
    close_time: dt_time = dt_time(16, 0),
    tz: str = "US/Eastern",
    now: Optional[datetime] = None
) -> bool:
    """
    Determines if the market is currently open.
    Args:
        open_time (datetime.time): Market open time (default 9:30 AM)
        close_time (datetime.time): Market close time (default 4:00 PM)
        tz (str): Timezone string (default 'US/Eastern')
    Returns:
        bool: True if the market is open, False otherwise.
    """
    import pytz
    eastern = pytz.timezone(tz)
    if now is None:
        now_eastern = datetime.now(eastern)
    else:
        now_eastern = now.astimezone(eastern)
    return open_time <= now_eastern.time() <= close_time


def time_until_market_opens(
    open_time: dt_time = dt_time(9, 30),
    close_time: dt_time = dt_time(16, 0),
    tz: str = "US/Eastern",
    now: Optional[datetime] = None
) -> float:
    """
    Calculates the time remaining until the market opens.
    Args:
        open_time (datetime.time): Market open time (default 9:30 AM)
        close_time (datetime.time): Market close time (default 4:00 PM)
        tz (str): Timezone string (default 'US/Eastern')
    Returns:
        float: Seconds until the market opens.
    """
    import pytz
    eastern = pytz.timezone(tz)
    if now is None:
        now_eastern = datetime.now(eastern)
    else:
        now_eastern = now.astimezone(eastern)
    next_open = datetime.combine(now_eastern.date(), open_time, tzinfo=eastern)
    if now_eastern.time() > close_time:
        next_open += timedelta(days=1)
    return (next_open - now_eastern).total_seconds()
