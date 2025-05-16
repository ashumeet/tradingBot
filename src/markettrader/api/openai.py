"""
OpenAI API integration for trading analysis.

This module provides functions to interact with OpenAI's API for trading-related
analysis, including fetching volatile stocks and analyzing portfolio data.
"""

import openai
from ..config import OPENAI_API_KEY, mask_api_key
from ..utils import common


# Configure OpenAI API with key from config and required scopes
openai.api_key = OPENAI_API_KEY
# Add the model.request scope that's required by the newer OpenAI API
openai.scope = "model.request"


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
    - Use current tickers (e.g., META instead of FB).

    Do not include any additional explanation or text; provide only the tickers.
    """
    # Using gpt-3.5-turbo instead of gpt-4 to ensure compatibility with more API keys
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial trading assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=50,
            temperature=0.7,
        )
        content = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        common.print_log(f"Error calling OpenAI API: {e}", common.LogLevel.ERROR)
        # Provide a fallback list of volatile stocks
        common.print_log("Using fallback list of volatile stocks", common.LogLevel.WARNING)
        content = "TSLA, NVDA, AMD, AAPL, MSFT, AMZN, META, GOOGL, NFLX, SNAP"
    stocks = content.split(", ")
    common.print_log(f"ChatGPT recommended volatile stocks: {stocks}", common.LogLevel.SUCCESS)
    return stocks


def analyze_technical_indicators(stock_data):
    """
    Calculate basic technical indicators from price data.
    
    Args:
        stock_data (dict): Dictionary of stock symbols with their price data
        
    Returns:
        dict: Technical indicators for each stock
    """
    indicators = {}
    for symbol, prices in stock_data.items():
        if len(prices) < 3:
            indicators[symbol] = {
                "trend": "insufficient data",
                "momentum": 0,
                "volatility": 0,
                "rsi_indication": "neutral"
            }
            continue
            
        # Simple trend detection
        trend = "neutral"
        if prices[-1] > prices[-2] > prices[-3]:
            trend = "strong uptrend"
        elif prices[-1] > prices[-2]:
            trend = "uptrend"
        elif prices[-1] < prices[-2] < prices[-3]:
            trend = "strong downtrend"
        elif prices[-1] < prices[-2]:
            trend = "downtrend"
            
        # Simple momentum calculation
        momentum = ((prices[-1] / prices[-3]) - 1) * 100 if len(prices) >= 3 else 0
        
        # Volatility estimation
        if len(prices) >= 3:
            volatility = sum([abs(prices[i] - prices[i-1]) / prices[i-1] * 100 for i in range(1, len(prices))]) / (len(prices) - 1)
        else:
            volatility = 0
            
        # Simple RSI-like indication
        up_moves = 0
        down_moves = 0
        for i in range(1, len(prices)):
            if prices[i] > prices[i-1]:
                up_moves += prices[i] - prices[i-1]
            else:
                down_moves += prices[i-1] - prices[i]
                
        if up_moves + down_moves > 0:
            rsi = 100 * (up_moves / (up_moves + down_moves))
            if rsi > 70:
                rsi_indication = "potentially overbought"
            elif rsi < 30:
                rsi_indication = "potentially oversold"
            else:
                rsi_indication = "neutral"
        else:
            rsi_indication = "neutral"
            
        indicators[symbol] = {
            "trend": trend,
            "momentum": round(momentum, 2),
            "volatility": round(volatility, 2),
            "rsi_indication": rsi_indication
        }
        
    return indicators


def print_technical_indicators(indicators):
    """
    Prints technical indicators using tabulate.
    
    Args:
        indicators (dict): Dictionary of stock symbols with their technical indicators
    """
    if not indicators:
        return
        
    headers = ["Symbol", "Trend", "Momentum", "Volatility", "RSI Indication"]
    table_data = []
    
    for symbol, data in indicators.items():
        # Format momentum with % sign and add proper color formatting later
        momentum_str = f"{data['momentum']}%" if data['momentum'] != 0 else "N/A"
        volatility_str = f"{data['volatility']}%" if data['volatility'] != 0 else "N/A"
        
        table_data.append([
            symbol, 
            data['trend'].title(), 
            momentum_str,
            volatility_str,
            data['rsi_indication'].title()
        ])
    
    common.print_log("\nTechnical Indicators:", common.LogLevel.INFO)
    common.display_table(headers, table_data)


def print_stock_data(stock_data):
    """
    Prints stock price data using tabulate.
    
    Args:
        stock_data (dict): Dictionary of stock symbols with their price data
    """
    if not stock_data:
        return
        
    headers = ["Symbol", "Latest Price", "Previous", "Change", "Period Trend"]
    table_data = []
    
    for symbol, prices in stock_data.items():
        if len(prices) >= 3:
            latest_price = prices[-1]
            prev_price = prices[-2]
            price_change = ((latest_price / prev_price) - 1) * 100
            price_change_str = f"+{price_change:.2f}%" if price_change >= 0 else f"{price_change:.2f}%"
            
            # Format the prices with appropriate decimal places
            if latest_price < 10:
                latest_price_str = f"${latest_price:.4f}"
                prev_price_str = f"${prev_price:.4f}"
            else:
                latest_price_str = f"${latest_price:.2f}"
                prev_price_str = f"${prev_price:.2f}"
                
            if len(prices) > 3:
                trend = f"{'Upward' if prices[-1] > prices[0] else 'Downward'} ({len(prices)} periods)"
            else:
                trend = "Insufficient data"
                
            table_data.append([
                symbol,
                latest_price_str,
                prev_price_str,
                price_change_str,
                trend
            ])
        else:
            table_data.append([symbol, "N/A", "N/A", "N/A", "Insufficient data"])
    
    common.print_log("\nStock Price Data:", common.LogLevel.INFO)
    common.display_table(headers, table_data)


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
    
    # Calculate technical indicators
    tech_indicators = analyze_technical_indicators(stock_data)
    
    # Display technical indicators and stock data using tabulate tables
    print_technical_indicators(tech_indicators)
    print_stock_data(stock_data)
    
    # Format technical indicators for prompt
    tech_indicators_str = ""
    for symbol, indicators in tech_indicators.items():
        tech_indicators_str += f"\n{symbol}:\n"
        tech_indicators_str += f"  - Price Trend: {indicators['trend']}\n"
        tech_indicators_str += f"  - Momentum: {indicators['momentum']}%\n"
        tech_indicators_str += f"  - Volatility: {indicators['volatility']}%\n"
        tech_indicators_str += f"  - RSI Indication: {indicators['rsi_indication']}\n"

    # Format stock data for prompt
    stock_data_str = ""
    for symbol, prices in stock_data.items():
        if len(prices) >= 3:
            price_change = ((prices[-1] / prices[-2]) - 1) * 100
            price_change_str = f"+{price_change:.2f}%" if price_change >= 0 else f"{price_change:.2f}%"
            stock_data_str += f"\n{symbol}:\n"
            stock_data_str += f"  - Latest price: ${prices[-1]:.2f} ({price_change_str} from previous)\n"
            stock_data_str += f"  - Previous prices: {', '.join([f'${p:.2f}' for p in prices[-3:-1]])}\n"
            if len(prices) > 3:
                stock_data_str += f"  - Historical trend: {'Upward' if prices[-1] > prices[0] else 'Downward'} over {len(prices)} periods\n"
        else:
            stock_data_str += f"\n{symbol}: Insufficient price data for analysis\n"

    prompt = f"""
    Analyze the following portfolio, stock data, and technical indicators to provide trading recommendations.
    
    As an expert trader combining minute-by-minute trading strategies with Warren Buffett's value investing principles, provide clear BUY/SELL/HOLD recommendations.

    PORTFOLIO:
    - Buying Power: ${portfolio["buying_power"]:.2f}
    - Current Positions: {portfolio["positions"]}
    - Open Orders: {portfolio["open_orders"]}

    PRICE DATA:
    {stock_data_str}
    
    TECHNICAL ANALYSIS:
    {tech_indicators_str}

    MARKET ANALYSIS GUIDELINES:
    1. Focus on stocks showing clear technical strength with strong fundamentals
    2. Look for momentum in uptrending stocks or reversal patterns in oversold conditions
    3. Consider volatility when sizing positions - higher volatility = smaller position size
    4. Balance short-term technical indicators with longer-term value considerations
    5. Prioritize high-quality stocks over purely speculative plays

    TRADING RULES:
    - Do NOT recommend selling more shares than currently held in the portfolio
    - Consider current market momentum and volatility in your analysis
    - For each recommendation, include a confidence level (1-10) based on the strength of signals
    - Each trade should have a clear technical or fundamental justification
    - Ensure total cost of BUY actions does not exceed available buying power (${portfolio["buying_power"]:.2f})

    FORMAT YOUR RESPONSE EXACTLY AS FOLLOWS:
    BUY: <SYMBOL>: <QUANTITY>: <CONFIDENCE 1-10>: <JUSTIFICATION>
    SELL: <SYMBOL>: <QUANTITY>: <CONFIDENCE 1-10>: <JUSTIFICATION>
    HOLD: <SYMBOL>: <CONFIDENCE 1-10>: <JUSTIFICATION>

    EXAMPLE RESPONSE:
    BUY: NVDA: 2: 8: Strong uptrend with 5.2% momentum, fundamentals support further growth
    SELL: TSLA: 1: 7: Showing bearish reversal pattern, potentially overbought at RSI 76
    HOLD: AAPL: 9: Strong fundamentals with neutral technical signals, maintain position
    
    Provide at least one BUY and one SELL recommendation if signals warrant it. Only recommend high-confidence trades (7+ rating).
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo instead of gpt-4
            messages=[
                {"role": "system", "content": "You are an expert financial analyst combining technical analysis with Warren Buffett's value investing principles."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7,  # Balanced creativity and predictability
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        common.print_log(f"Error calling OpenAI API: {e}", common.LogLevel.ERROR)
        # Return a fallback analysis
        return """
        HOLD: AAPL: 8: Market conditions uncertain. Preserving capital for better opportunities.
        BUY: AAPL: 1: 7: Strong fundamentals and growth potential.
        BUY: MSFT: 1: 7: Solid company with consistent performance.
        """ 