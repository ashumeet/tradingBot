"""
API integrations for the trading bot.

This module provides integration with external APIs like Alpaca and OpenAI.
"""

from .alpaca import (
    fetch_portfolio,
    fetch_stock_data,
    execute_trades
)

from .openai import (
    fetch_top_volatile_stocks,
    chatgpt_analysis
)

__all__ = [
    'fetch_portfolio',
    'fetch_stock_data',
    'execute_trades',
    'fetch_top_volatile_stocks',
    'chatgpt_analysis'
] 