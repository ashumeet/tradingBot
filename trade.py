#!/usr/bin/env python3
"""
Simple script to start the trading platform from the root directory.
This provides a more convenient way to run the trading platform compared to
using the module syntax.

Usage:
    python3 trade.py                        # Start trading with default config
    python3 trade.py --debug                # Run with debug mode
    python3 trade.py --check-config         # Validate configuration and exit
    python3 trade.py --env-file=config.env  # Use a specific environment file
"""

# Suppress all warnings before any imports
import warnings
warnings.filterwarnings('ignore')

import sys
import os

# Add the current directory to the path so we can import src
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function from the module
from src.trader_app.__main__ import main

if __name__ == "__main__":
    # Call the main function with the command line arguments
    main() 