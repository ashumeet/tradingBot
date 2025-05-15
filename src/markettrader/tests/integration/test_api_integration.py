"""
Integration tests for API modules.

These tests verify that the API modules can communicate with external services.
They require valid API keys to be configured in the environment.
"""

import unittest
import os
from unittest import skipIf

# Use absolute imports
from src.tradingbot.config import ALPACA_API_KEY, OPENAI_API_KEY
from src.tradingbot.api import (
    fetch_portfolio,
    fetch_stock_data,
    fetch_top_volatile_stocks
)


@skipIf(not ALPACA_API_KEY, "Alpaca API key not configured")
class TestAlpacaIntegration(unittest.TestCase):
    """Integration tests for Alpaca API."""

    def test_fetch_portfolio(self):
        """Test that we can fetch portfolio data from Alpaca."""
        portfolio = fetch_portfolio()
        self.assertIsInstance(portfolio, dict)
        self.assertIn("buying_power", portfolio)
        self.assertIn("positions", portfolio)
        self.assertIn("open_orders", portfolio)
        self.assertIsInstance(portfolio["buying_power"], float)

    def test_fetch_stock_data(self):
        """Test that we can fetch stock data from Alpaca."""
        stocks = ["AAPL", "MSFT"]
        data = fetch_stock_data(stocks)
        self.assertIsInstance(data, dict)
        # At least one stock should have returned data
        self.assertTrue(any(stock in data for stock in stocks))


@skipIf(not OPENAI_API_KEY, "OpenAI API key not configured")
class TestOpenAIIntegration(unittest.TestCase):
    """Integration tests for OpenAI API."""

    def test_fetch_volatile_stocks(self):
        """Test that we can fetch volatile stock recommendations."""
        stocks = fetch_top_volatile_stocks()
        self.assertIsInstance(stocks, list)
        self.assertGreater(len(stocks), 0)
        # Stock symbols should be uppercase and contain only letters
        for stock in stocks:
            self.assertTrue(stock.isupper())


if __name__ == "__main__":
    unittest.main() 