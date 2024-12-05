import datetime, time
from colorama import init
from utils.common import is_market_open, time_until_market_opens, print_log
from utils.alpaca import fetch_portfolio, fetch_stock_data, execute_trades
from utils.chat_gpt import fetch_top_stocks, chatgpt_analysis

# Initialize Colorama for colored logs
init(autoreset=True)

# Analyze trends and generate buy/sell decisions using ChatGPT
def analyze_and_decide(portfolio, stock_data):
    print_log("Preparing data for ChatGPT analysis...", level="info")
    
    # Get ChatGPT response
    response = chatgpt_analysis(portfolio, stock_data)
    
    print_log("ChatGPT analysis complete. Parsing results...", level="success")
    
    # Parse ChatGPT response
    decisions = {"buy": [], "sell": [], "reasoning": []}
    lines = response.splitlines()
    for line in lines:
        if line.startswith("BUY"):
            _, stock, qty, reason = line.split(":", 3)
            decisions["buy"].append((stock.strip(), int(qty.strip())))
            decisions["reasoning"].append(f"BUY {stock.strip()}: {reason.strip()}")
        elif line.startswith("SELL"):
            _, stock, qty, reason = line.split(":", 3)
            decisions["sell"].append((stock.strip(), int(qty.strip())))
            decisions["reasoning"].append(f"SELL {stock.strip()}: {reason.strip()}")
        elif line.startswith("HOLD"):
            decisions["reasoning"].append(line.strip())
        else:
            decisions["reasoning"].append(f"UNKNOWN: {line.strip()}") 
    return decisions

# Main trading loop
def run_trading_day():
    # Track activity for the day
    day_summary = {}

    while is_market_open():
        print_log("Market is open. Running a trading cycle...", level="action")
        
        # Fetch portfolio, recommended stocks, and stock data
        portfolio = fetch_portfolio()
        recommended_stocks = fetch_top_stocks()
        all_stocks = recommended_stocks + list(portfolio["positions"].keys())
        stock_data = fetch_stock_data(all_stocks)
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
        print_log("\nBuy Decisions:", level="info")
        for stock, qty in decisions["buy"]:
            print_log(f"BUY {stock}({qty})", level="success")

        print_log("\nSell Decisions:", level="info")
        for stock, qty in decisions["sell"]:
            print_log(f"SELL {stock}({qty})", level="warning")

        print_log("\nReasoning:", level="info")
        for reason in decisions["reasoning"]:
            print_log(reason, level="action")

        # Wait for 1 minute before the next cycle
        time.sleep(60)

    return day_summary

# Modified run_trading_bot function
def run_trading_bot():
    while True:
        if is_market_open():

            print_log("Market is open. Starting trading day ...", level="success")
            day_summary = run_trading_day()
            print(day_summary)

        else:

            print_log("Market is closed. Fetching portfolio ...", level="warning")
            fetch_portfolio()

            # Wait until market opens
            print_log("Waiting for the market to open...", level="warning")
            wait_time = time_until_market_opens()
            time.sleep(wait_time)

# Run the bot
if __name__ == "__main__":
    run_trading_bot()