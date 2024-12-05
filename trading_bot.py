import time
import utils.common as common
import utils.alpaca as alpaca
import utils.chat_gpt as gpt
from datetime import datetime
from colorama import init

# Initialize Colorama for colored logs
init(autoreset=True)

# Analyze trends and generate buy/sell decisions using ChatGPT
def analyze_and_decide(portfolio, stock_data):

    common.print_log("Preparing data for ChatGPT analysis ...", level="info")
    
    # Get ChatGPT response
    response = gpt.chatgpt_analysis(portfolio, stock_data)
    
    common.print_log("ChatGPT analysis complete. Parsing results ...", level="success")
    
    return common.decode_chat_gpt_response(response)

# Main trading loop
def run_trading_day():
    # Track activity for the day
    day_summary = {}

    common.print_log("Market is open ...", level="action")
    while common.is_market_open():
        common.print_log("Running a trading cycle ...\n", level="action")
        
        # Fetch portfolio, recommended stocks, and stock data
        portfolio = alpaca.fetch_portfolio()
        recommended_stocks = gpt.fetch_top_volatile_stocks()
        all_stocks = recommended_stocks + list(portfolio["positions"].keys())
        stock_data = alpaca.fetch_stock_data(all_stocks)
        decisions = analyze_and_decide(portfolio, stock_data)

        # Get the current timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Log decisions under the timestamp
        day_summary[current_time] = {
            "buy_decisions": decisions["buy"],
            "sell_decisions": decisions["sell"],
            "reasoning": decisions["reasoning"],
        }

        # Print decisions and reasoning
        common.print_decisions(decisions)

        # Execute the trade
        alpaca.execute_trades(decisions)

        # Wait for 1 minute before the next cycle
        common.print_log("\nSleeping for 1 mins ...\n", level="action")
        time.sleep(60)

    return day_summary

# Modified run_trading_bot function
def run_trading_bot():
    while True:
        if common.is_market_open():

            common.print_log("Market is open. Starting trading day ...", level="success")
            day_summary = run_trading_day()
            print(day_summary)

        else:

            common.print_log("Market is closed. Fetching portfolio ...", level="warning")
            alpaca.fetch_portfolio()

            # Wait until market opens
            common.print_log("Waiting for the market to open ...", level="warning")
            wait_time = common.time_until_market_opens()
            time.sleep(wait_time)

# Run the bot
if __name__ == "__main__":
    run_trading_bot()