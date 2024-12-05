import openai, config
from utils.common import print_log


# Use keys from the config file
openai.api_key = config.OPENAI_API_KEY

# Fetch top stocks from ChatGPT
def fetch_top_stocks():
    print_log("Fetching top recommended stocks from ChatGPT...", level="info")
    prompt = """
    You are an expert stock broker and trading expert, highly skilled in recommending stocks for buying or selling based on historic data (not real time data).
    While you lack access to real-time data, you excel at analyzing general market trends to identify opportunities. 
    Based on historical insights, recommend the top 10 stocks to watch for trading right now. 
    Provide only the stock tickers in a comma-separated format (e.g., AAPL, MSFT, TSLA).
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial trading assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=50,
        temperature=0.7,
    )
    stocks = response['choices'][0]['message']['content'].strip().split(", ")
    print_log(f"ChatGPT recommended stocks: {stocks}", level="success")
    return stocks

# ChatGPT interaction
def chatgpt_analysis(portfolio, stock_data):

    # Prepare a single prompt for all stocks
    prompt = f"""
    Analyze the following portfolio and stock data, and provide buy/sell/hold recommendations:
    
    Portfolio:
    - Buying Power: ${portfolio["buying_power"]:.2f}
    - Positions: {portfolio["positions"]}
    - Open Orders: {portfolio["open_orders"]}
    
    Stock Data (symbol: prices):
    {stock_data}
    
    Guidelines:
    - For each stock, provide a clear recommendation (BUY, SELL, HOLD).
    - Justify each decision based on the provided stock data and portfolio constraints.
    - Avoid suggesting actions for stocks already in open orders.
    """

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial trading assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,
    )
    return response['choices'][0]['message']['content'].strip()
