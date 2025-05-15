"""
OpenAI API integration for trading analysis.

This module provides functions to interact with OpenAI's API for trading-related
analysis, including fetching volatile stocks and analyzing portfolio data.
"""

import openai
from ..config import OPENAI_API_KEY, mask_api_key
from ..utils import common


# Configure OpenAI API with key from config
openai.api_key = OPENAI_API_KEY


def fetch_top_volatile_stocks():
    """
    Fetches the top 10 most volatile stocks from ChatGPT recommendations.

    ChatGPT is prompted to provide a comma-separated list of stock tickers
    based on historical market trends, focusing on significant intraday price fluctuations.

    Returns:
        list: A list of recommended volatile stock tickers.
    """

    common.print_log("Fetching volatile stocks from ChatGPT ...", common.LogLevel.ACTION)
    
    # Log masked API key for debugging if needed
    if common.is_debug_mode():
        common.print_log(f"Using OpenAI API key: {mask_api_key(OPENAI_API_KEY)}", common.LogLevel.DEBUG)
    
    # ChatGPT prompt for volatile stocks
    prompt = """
    You are an expert stock broker and trading expert, highly skilled in recommending volatile stocks for day trading.
    Recommend the top 10 most volatile stocks based on historical market trends (not real-time data).
    Only provide stock tickers in a comma-separated format (e.g., TSLA, AAPL, GME). 
    Ensure the stocks are:
    - Traded on major US exchanges (e.g., NYSE, NASDAQ).
    - Known for significant intraday price fluctuations.
    - Supported by Alpaca's trading platform.

    Do not include any additional explanation or text; provide only the tickers.
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
    common.print_log(f"ChatGPT recommended volatile stocks: {stocks}", common.LogLevel.SUCCESS)
    return stocks


def chatgpt_analysis(portfolio, stock_data):
    """
    Sends portfolio and stock data to ChatGPT and requests structured recommendations 
    for aggressive, minute-level trading decisions without short-selling.

    Parameters:
    - portfolio: A dictionary with keys: 'buying_power', 'positions', 'open_orders'.
    - stock_data: A dictionary with stock symbols as keys and price data as values.

    Returns:
    - A structured string response from ChatGPT, including BUY/SELL/HOLD actions 
      for high-frequency trading.
    """

    common.print_log("Doing ChatGPT analysis ...", common.LogLevel.ACTION)

    prompt = f"""
    Analyze the following portfolio and stock data, and provide trading recommendations based on:
    - Minute-by-minute trading strategies to capture short-term market trends.
    - Warren Buffett's principles of value investing and cash preservation.

    Portfolio:
    - Buying Power: ${portfolio["buying_power"]:.2f}
    - Positions: {portfolio["positions"]}
    - Open Orders: {portfolio["open_orders"]}

    Stock Data (symbol: prices):
    {stock_data}

    Guidelines:
    - Combine short-term trading strategies with a long-term, value-driven mindset:
      - Use minute-level trends to decide on aggressive BUY/SELL actions for immediate returns.
      - Apply Warren Buffett's principle: Sell underperforming or overvalued stocks and hold cash if no better opportunities exist.
    - Do not recommend selling more shares of a stock than currently held in the portfolio. For example:
      - If you own 0 shares of TSLA, do not recommend SELL actions for TSLA.
    - Prioritize high-quality stocks with strong fundamentals over speculative trades.
    - Provide recommendations in the following format:
      [ACTION]: <STOCK_SYMBOL>: <QUANTITY>: <JUSTIFICATION>
      Example:
        SELL: TSLA: 2: Overvalued and underperforming. Holding cash for better opportunities.
        BUY: AAPL: 1.5: High-quality stock with strong upward momentum.
        HOLD: MSFT: 0: Stable and fundamental value remains strong.

    - JUSTIFICATION must only highlight significant decisions or deviations from typical strategies.
    - Do not recommend speculative trades without clear justification.
    - Ensure total cost of BUY actions does not exceed available buying power (${portfolio["buying_power"]:.2f}).
    """
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a financial assistant combining minute-level trading strategies with Warren Buffett's long-term mindset."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=1000,
        temperature=0.7,  # Balanced creativity and predictability
    )
    
    return response['choices'][0]['message']['content'].strip() 