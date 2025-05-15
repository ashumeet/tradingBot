"""
Command-line interface for the trading bot.

This module provides the command-line entry point for running the trading bot.
"""

import sys
import argparse
import json
import warnings
import os
from pathlib import Path
from .trading_bot import main as run_bot
from .config import validate_config, get_secure_config_summary, ENVIRONMENT, ENV_FILE_PATH

# Suppress specific urllib3 warnings about OpenSSL
warnings.filterwarnings('ignore', category=Warning, module='urllib3')

# ANSI colors for terminal output
BLUE = '\033[0;34m'
GREEN = '\033[0;32m'
YELLOW = '\033[1;33m'
CYAN = '\033[0;36m'
MAGENTA = '\033[0;35m'
RED = '\033[0;31m'
BOLD = '\033[1m'
NC = '\033[0m'  # No Color


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Trading Bot CLI")
    parser.add_argument(
        "--check-config", 
        action="store_true", 
        help="Check configuration and exit"
    )
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="Enable debug mode"
    )
    parser.add_argument(
        "--env-file",
        help="Specify a custom environment file to use"
    )
    return parser.parse_args()


def format_config_summary(config):
    """Format configuration summary in a readable way with colors."""
    header = f"{BLUE}=== Market Trader Configuration ==={NC}"
    footer = f"{BLUE}==================================={NC}"
    
    env_status = f"{GREEN}PAPER TRADING{NC}" if config['ENVIRONMENT'] == 'paper' else f"{RED}LIVE TRADING{NC}"
    
    # Get information about the environment file
    env_file = config.get('ENV_FILE_PATH', 'None')
    env_file_status = f"{GREEN}Found{NC}" if env_file else f"{YELLOW}Using defaults{NC}"
    
    formatted = [
        header,
        f"{CYAN}• Environment:{NC} {env_status}",
        f"{CYAN}• Config File:{NC} {env_file} ({env_file_status})",
        f"{CYAN}• Alpaca API Key:{NC} {YELLOW}{config['ALPACA_API_KEY']}{NC}",
        f"{CYAN}• Alpaca Secret Key:{NC} {YELLOW}{config['ALPACA_SECRET_KEY']}{NC}",
        f"{CYAN}• OpenAI API Key:{NC} {YELLOW}{config['OPENAI_API_KEY']}{NC}",
        f"{CYAN}• Alpaca API URL:{NC} {GREEN}{config['ALPACA_API_URL']}{NC}",
        f"{CYAN}• Alpaca Data API URL:{NC} {GREEN}{config['ALPACA_DATA_API_URL']}{NC}",
        f"{CYAN}• Target Index Funds:{NC} {MAGENTA}{', '.join(config['TARGET_INDEX_FUNDS'])}{NC}",
        footer
    ]
    
    return "\n".join(formatted)


def main():
    """Main entry point for the CLI."""
    # Suppress all warnings in non-debug mode
    if not any('--debug' in arg for arg in sys.argv):
        warnings.filterwarnings('ignore')
        os.environ['PYTHONWARNINGS'] = 'ignore'
    
    args = parse_args()
    
    # If a custom environment file is specified, set it as an environment variable
    # This needs to be done before importing config module
    if args.env_file:
        os.environ['ENV_FILE'] = args.env_file
        print(f"{YELLOW}Using custom environment file: {args.env_file}{NC}")
    
    if args.debug:
        # Re-enable warnings in debug mode
        warnings.resetwarnings()
        os.environ["DEBUG"] = "true"
    
    if args.check_config:
        try:
            validate_config()
            config = get_secure_config_summary()
            print(f"{GREEN}✅ Configuration is valid!{NC}")
            print(format_config_summary(config))
            return 0
        except ValueError as e:
            print(f"{RED}❌ Configuration error: {e}{NC}")
            return 1
    
    # Run the main bot loop
    try:
        run_bot()
        return 0
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Trading bot stopped by user.{NC}")
        return 0
    except Exception as e:
        print(f"{RED}Error: {e}{NC}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 