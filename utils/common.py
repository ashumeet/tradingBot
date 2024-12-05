import time, pytz
from colorama import Fore, Style
from datetime import datetime, time, timedelta


def is_market_open():
    # Define market open and close times in Eastern Time (ET)
    market_open = time(9, 30)  # 9:30 AM ET
    market_close = time(16, 0)  # 4:00 PM ET

    # Get the current time in Eastern Time
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)

    # Check if the current time is within market hours
    return market_open <= now_eastern.time() <= market_close

# Function to calculate time until the market opens
def time_until_market_opens():
    eastern = pytz.timezone("US/Eastern")
    now_eastern = datetime.now(eastern)

    # Calculate the next market open time (9:30 AM ET)
    next_open = datetime.combine(now_eastern.date(), time(9, 30), tzinfo=eastern)
    if now_eastern.time() > time(16, 0):  # If past market close, set to next day
        next_open += timedelta(days=1)

    return (next_open - now_eastern).total_seconds()

# Function to print logs with colors
def print_log(message, level="info"):
    colors = {
        "info": Fore.CYAN,
        "success": Fore.GREEN,
        "warning": Fore.YELLOW,
        "error": Fore.RED,
        "action": Fore.MAGENTA,
    }
    color = colors.get(level, Fore.WHITE)
    print(f"{color}{message}{Style.RESET_ALL}")
