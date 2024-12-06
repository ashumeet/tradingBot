import time
import utils.common as common
import utils.alpaca as alpaca
import utils.chat_gpt as gpt
from datetime import datetime
from colorama import init

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
        recommended_stocks = gpt.fetch_top_volatile_stocks()
        all_stocks = recommended_stocks + list(portfolio["positions"].keys())
        stock_data = alpaca.fetch_stock_data(all_stocks)
        response = gpt.chatgpt_analysis(portfolio, stock_data)
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


if __name__ == "__main__":
    """
    Main entry point for the trading application. Continuously monitors the market
    and performs trading activities during open hours. When the market is closed,
    it waits until the next market opening.
    """

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
