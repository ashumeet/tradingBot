"""
Main Trading Bot Module

This module serves as the entry point for the trading bot application.
It manages the trading cycles, market monitoring, and overall execution flow.
"""

import time
from datetime import datetime
from colorama import init

from .utils import common
from .api import alpaca, openai
from .config import validate_config, get_secure_config_summary, check_for_hardcoded_secrets

init(autoreset=True)


def trading_day():
    """
    Executes trading cycles throughout the day while the market is open.

    Fetches portfolio, analyzes volatile stocks, gathers stock data, and makes 
    trading decisions in a loop until the market closes. Summarizes trading 
    activities for the day.

    Returns:
        dict: A summary of the day's trading decisions, including buy and sell orders.
    """

    day_summary = {}
    common.print_log("Market is open ...", common.LogLevel.ACTION)
    while common.is_market_open():

        common.print_log("Running a trading cycle ...\n", common.LogLevel.ACTION)
        portfolio = alpaca.fetch_portfolio()
        recommended_stocks = openai.fetch_top_volatile_stocks()
        all_stocks = recommended_stocks + list(portfolio["positions"].keys())
        stock_data = alpaca.fetch_stock_data(all_stocks)
        response = openai.chatgpt_analysis(portfolio, stock_data)
        decisions = common.decode_chat_gpt_response(response)
        common.print_decisions(decisions)

        day_summary[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = {
            "buy_decisions": decisions["buy"],
            "sell_decisions": decisions["sell"],
            "reasoning": decisions["reasoning"],
        }

        alpaca.execute_trades(decisions)

        common.print_log("\nSleeping for 1 mins ...\n", common.LogLevel.ACTION)
        time.sleep(60)

    return day_summary


def main():
    """
    Main entry point for the trading application. Continuously monitors the market
    and performs trading activities during open hours. When the market is closed,
    it waits until the next market opening.
    """
    try:
        # Validate configuration before starting
        validate_config()
        common.print_log("Configuration validated successfully.", common.LogLevel.INFO)
        
        # Display secure configuration summary
        config_summary = get_secure_config_summary()
        common.print_log(f"Current configuration: {config_summary}", common.LogLevel.INFO)
        
        # Check for hardcoded secrets
        suspicious_files = check_for_hardcoded_secrets()
        if suspicious_files:
            common.print_log(f"WARNING: Potential hardcoded secrets found in: {', '.join(suspicious_files)}", 
                             common.LogLevel.WARNING)
            common.print_log("It's recommended to move these to environment variables or .env file.", 
                             common.LogLevel.WARNING)
        
        while True:
            if common.is_market_open():
                day_summary = trading_day()
                print(day_summary)
            else:
                common.print_log("Market is closed ...", common.LogLevel.WARNING)
                alpaca.fetch_portfolio()

                common.print_log("Waiting for the market to open ...", common.LogLevel.WARNING)
                wait_time = common.time_until_market_opens()
                time.sleep(wait_time)
    except ValueError as e:
        common.print_log(f"Configuration error: {str(e)}", common.LogLevel.ERROR)
        exit(1)
    except Exception as e:
        common.print_log(f"An unexpected error occurred: {str(e)}", common.LogLevel.ERROR)
        exit(1)


if __name__ == "__main__":
    main() 