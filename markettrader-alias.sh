#!/bin/bash
# Add this to your .bashrc or .zshrc with:
# source /path/to/markettrader-alias.sh

# Market Trader activation
markettrader_activate() {
  source "/Users/ashu/Documents/Workspace/tradingBot/venv/bin/activate"
  echo "Market Trader environment activated"
}

# Run the Market Trader
markettrader() {
  if [[ $VIRTUAL_ENV != *"marketTrader"* ]]; then
    source "/Users/ashu/Documents/Workspace/tradingBot/venv/bin/activate"
  fi
  python -m src.markettrader.__main__ $@
}
