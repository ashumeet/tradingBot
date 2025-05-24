"""
Configuration Module for trader_app

This module manages secure configuration for the trading bot, handling API keys
and sensitive information. It loads configuration from environment variables,
provides validation, and implements security best practices.

Features:
- Environment variable loading via python-dotenv
- API key validation and format checking
- Secret masking for secure logging
- Hardcoded secret detection in codebase
- New parameters: VERBOSE_LOGGING, MAX_CONCURRENT_TRADES

Usage:
    from trader_app.core import validate_config, ALPACA_API_KEY
    # Or when imported within the package:
    from .config import validate_config, ALPACA_API_KEY
    
    # Validate configuration
    validate_config()
    
    # Access configuration variables directly
    api_key = ALPACA_API_KEY
    verbose = VERBOSE_LOGGING
    max_trades = MAX_CONCURRENT_TRADES
"""

import os
import re
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment configuration with the following priority:
# 1. Custom environment file specified via ENV_FILE environment variable
# 2. .env.dev in current directory (development environment)
# 3. .env in current directory (production environment)
# 4. Look in examples directory for env.dev or env.prod if nothing found

custom_env_path = os.environ.get('ENV_FILE')
if custom_env_path and Path(custom_env_path).exists():
    print(f"Loading configuration from custom env file: {custom_env_path}")
    load_dotenv(dotenv_path=custom_env_path)
    loaded_env_file = custom_env_path
elif Path('.env.dev').exists():
    print("Loading development environment (.env.dev)")
    load_dotenv(dotenv_path='.env.dev')
    loaded_env_file = '.env.dev'
elif Path('.env').exists():
    print("Loading production environment (.env)")
    load_dotenv(dotenv_path='.env')
    loaded_env_file = '.env'
else:
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    example_dev = project_root / 'examples' / 'env.dev'
    example_prod = project_root / 'examples' / 'env.prod'
    if example_dev.exists():
        print(f"Loading example development environment from: {example_dev}")
        load_dotenv(dotenv_path=example_dev)
        loaded_env_file = str(example_dev)
    elif example_prod.exists():
        print(f"Loading example production environment from: {example_prod}")
        load_dotenv(dotenv_path=example_prod)
        loaded_env_file = str(example_prod)
    else:
        print("No environment file found. Using default environment variables.")
        load_dotenv()
        loaded_env_file = None

# API Keys and Credentials
ALPACA_API_KEY = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Redis configuration
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_DB = int(os.getenv("REDIS_DB", "0"))
REDIS_USE_SSL = os.getenv("REDIS_USE_SSL", "false").lower() == "true"

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "paper").lower()

# Alpaca API endpoints
ALPACA_API_URL = os.getenv("ALPACA_API_URL", "")
ALPACA_DATA_API_URL = os.getenv("ALPACA_DATA_API_URL", "")

# Trading configuration
TARGET_INDEX_FUNDS = os.getenv("TARGET_INDEX_FUNDS", "SPY,QQQ,DIA").split(",")

# New configuration parameters for trader_app
# Example: Enable verbose logging (default: False)
VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
# Example: Maximum number of concurrent trades (default: 5)
MAX_CONCURRENT_TRADES = int(os.getenv("MAX_CONCURRENT_TRADES", "5"))

# Store the loaded environment file path for reference
ENV_FILE_PATH = loaded_env_file

def get_config_value(key, default=None):
    """Get a configuration value by key with optional default."""
    return os.getenv(key, default)

# ... (rest of the config.py logic will be copied in next chunk) ...

def mask_api_key(api_key, visible_chars=4):
    """
    Masks an API key for secure display in logs.
    Returns the first few and last few characters, with everything in between replaced by asterisks.
    Args:
        api_key (str): The API key to mask
        visible_chars (int): The number of characters to show at the beginning and end.
    Returns:
        str: The masked API key or "invalid-key" if too short
    """
    if not api_key or len(api_key) < 8:
        return "invalid-key"
    if len(api_key) <= visible_chars * 2:
        masked_part = '*' * (len(api_key) - 2)
        return f"{api_key[:1]}{masked_part}{api_key[-1:]}"
    masked_part = '*' * (len(api_key) - (visible_chars * 2))
    return f"{api_key[:visible_chars]}{masked_part}{api_key[-visible_chars:]}"

def validate_api_key_format(key, name):
    """
    Validates that an API key meets basic format requirements.
    Args:
        key (str): The API key to validate
        name (str): The name of the API key for error messages
    Returns:
        tuple: (is_valid, error_message) where is_valid is a boolean and error_message is a string (empty if valid)
    """
    if not key:
        return False, f"{name} is missing"
    # Alpaca keys: 20+ alphanumeric chars
    if name.upper().startswith("ALPACA") and (len(key) < 20 or not key.replace("-", "").isalnum()):
        return False, f"{name} has invalid format (should be alphanumeric and at least 20 characters)"
    # OpenAI keys: start with 'sk-' and at least 30 chars
    if name == "OPENAI_API_KEY" and (not key.startswith("sk-") or len(key) < 30):
        return False, f"{name} has invalid format (should start with 'sk-' and be at least 30 characters)"
    return True, ""

def validate_config():
    """
    Validates that all required environment variables are set and have proper formats.
    Raises ValueError with a message if any validation fails.
    Also checks types and value ranges for critical parameters.
    """
    required_vars = {
        "ALPACA_API_KEY": ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ALPACA_API_URL": ALPACA_API_URL,
        "ALPACA_DATA_API_URL": ALPACA_DATA_API_URL
    }
    # Redis is not critical for basic operation, but log warning if missing
    if not REDIS_HOST or not isinstance(REDIS_PORT, int) or REDIS_PORT <= 0:
        print("Warning: Redis configuration is incomplete or invalid. Redis features will not be available.")
    # Check for missing variables
    missing_vars = [var_name for var_name, var_value in required_vars.items() if not var_value]
    if missing_vars:
        missing_list = ", ".join(missing_vars)
        raise ValueError(f"Missing required environment variables: {missing_list}. "
                         f"Please set them in your environment or .env file.")
    # Check key formats
    validation_errors = []
    for var_name, var_value in required_vars.items():
        if var_name.endswith("_API_KEY") or var_name.endswith("_SECRET_KEY"):
            is_valid, error_message = validate_api_key_format(var_value, var_name)
            if not is_valid:
                validation_errors.append(error_message)
    # Check environment value
    if ENVIRONMENT not in ("paper", "live"):
        validation_errors.append(f"ENVIRONMENT must be 'paper' or 'live', got '{ENVIRONMENT}'")
    # Check target index funds
    if not isinstance(TARGET_INDEX_FUNDS, list) or not all(isinstance(f, str) and f for f in TARGET_INDEX_FUNDS):
        validation_errors.append("TARGET_INDEX_FUNDS must be a comma-separated list of symbols (e.g., 'SPY,QQQ,DIA')")
    # Check new parameters
    if not isinstance(VERBOSE_LOGGING, bool):
        validation_errors.append("VERBOSE_LOGGING must be a boolean (true/false)")
    if not isinstance(MAX_CONCURRENT_TRADES, int) or MAX_CONCURRENT_TRADES < 1:
        validation_errors.append("MAX_CONCURRENT_TRADES must be a positive integer")
    if validation_errors:
        error_list = ", ".join(validation_errors)
        raise ValueError(f"Configuration validation failed: {error_list}")

def check_for_hardcoded_secrets():
    """
    Scans Python files in the project for potentially hardcoded API keys.
    Returns:
        list: A list of files with potential hardcoded secrets
    """
    suspicious_files = []
    patterns = [
        r'sk-[a-zA-Z0-9]{30,}',  # OpenAI API key pattern
        r'api[_-]?key\s*=\s*["\"][a-zA-Z0-9]{20,}["\"]',  # Generic API key assignment
        r'secret[_-]?key\s*=\s*["\"][a-zA-Z0-9]{20,}["\"]',  # Generic secret key assignment
    ]
    exclude_dirs = ['venv', 'env', '.git', '__pycache__', 'node_modules']
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and file != 'config_template.py':
                file_path = os.path.join(root, file)
                try:
                    with open(file_path, 'r') as f:
                        content = f.read()
                        for pattern in patterns:
                            if re.search(pattern, content):
                                suspicious_files.append(file_path)
                                break
                except Exception:
                    pass
    return suspicious_files

def get_secure_config_summary():
    """
    Returns a safe summary of the current configuration with masked API keys.
    This is useful for logging the current config without exposing secrets.
    Returns:
        dict: A summary of the configuration with sensitive values masked
    """
    return {
        "ALPACA_API_KEY": mask_api_key(ALPACA_API_KEY),
        "ALPACA_SECRET_KEY": mask_api_key(ALPACA_SECRET_KEY),
        "OPENAI_API_KEY": mask_api_key(OPENAI_API_KEY),
        "ENVIRONMENT": ENVIRONMENT,
        "ALPACA_API_URL": ALPACA_API_URL,
        "ALPACA_DATA_API_URL": ALPACA_DATA_API_URL,
        "TARGET_INDEX_FUNDS": TARGET_INDEX_FUNDS,
        "REDIS_HOST": REDIS_HOST,
        "REDIS_PORT": REDIS_PORT,
        "REDIS_DB": REDIS_DB,
        "REDIS_USE_SSL": REDIS_USE_SSL,
        "ENV_FILE_PATH": ENV_FILE_PATH,
        "VERBOSE_LOGGING": VERBOSE_LOGGING,
        "MAX_CONCURRENT_TRADES": MAX_CONCURRENT_TRADES
    }
# All sensitive values are masked; do not log or print raw API keys or secrets.
