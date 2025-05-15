"""
Configuration Module

This module manages secure configuration for the trading bot, handling API keys
and sensitive information. It loads configuration from environment variables,
provides validation, and implements security best practices.

Features:
- Environment variable loading via python-dotenv
- API key validation and format checking
- Secret masking for secure logging
- Hardcoded secret detection in codebase

Usage:
    from src.tradingbot.config import validate_config, ALPACA_API_KEY
    # Or when imported within the package:
    from ..config import validate_config, ALPACA_API_KEY
    
    # Validate configuration
    validate_config()
    
    # Access configuration variables directly
    api_key = ALPACA_API_KEY
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

# If ENV_FILE is specified, use that (option 1)
custom_env_path = os.environ.get('ENV_FILE')
if custom_env_path and Path(custom_env_path).exists():
    print(f"Loading configuration from custom env file: {custom_env_path}")
    load_dotenv(dotenv_path=custom_env_path)
    loaded_env_file = custom_env_path
# Try dev environment (option 2)
elif Path('.env.dev').exists():
    print("Loading development environment (.env.dev)")
    load_dotenv(dotenv_path='.env.dev')
    loaded_env_file = '.env.dev'
# Try production environment (option 3)
elif Path('.env').exists():
    print("Loading production environment (.env)")
    load_dotenv(dotenv_path='.env')
    loaded_env_file = '.env'
# Try examples directory (option 4)
else:
    # Get the project root directory to find the examples folder
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
# Load from environment variables with empty string as fallback
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
ENVIRONMENT = os.getenv("ENVIRONMENT", "paper").lower()  # Default to paper trading

# Alpaca API endpoints - directly use the URLs from environment variables
ALPACA_API_URL = os.getenv("ALPACA_API_URL", "")
ALPACA_DATA_API_URL = os.getenv("ALPACA_DATA_API_URL", "")

# Trading configuration
TARGET_INDEX_FUNDS = os.getenv("TARGET_INDEX_FUNDS", "SPY,QQQ,DIA").split(",")

# Store the loaded environment file path for reference
ENV_FILE_PATH = loaded_env_file

def mask_api_key(api_key):
    """
    Masks an API key for secure display in logs.
    Returns the first 4 and last 4 characters, with everything in between replaced by asterisks.
    
    Args:
        api_key (str): The API key to mask
        
    Returns:
        str: The masked API key or "invalid-key" if too short
    """
    if not api_key or len(api_key) < 8:
        return "invalid-key"
    
    return f"{api_key[:4]}{'*' * (len(api_key) - 8)}{api_key[-4:]}"

def validate_api_key_format(key, name):
    """
    Validates that an API key meets basic format requirements.
    Different services have different formats, so this is a general check.
    
    Args:
        key (str): The API key to validate
        name (str): The name of the API key for error messages
        
    Returns:
        tuple: (is_valid, error_message) where is_valid is a boolean and
               error_message is a string (empty if valid)
    """
    if not key:
        return False, f"{name} is missing"
    
    # Alpaca keys are typically alphanumeric and at least 20 chars
    if name.startswith("ALPACA") and (len(key) < 20 or not key.replace("-", "").isalnum()):
        return False, f"{name} has invalid format (should be alphanumeric and at least 20 characters)"
    
    # OpenAI keys typically start with "sk-" and are at least 30 chars
    if name == "OPENAI_API_KEY" and (not key.startswith("sk-") or len(key) < 30):
        return False, f"{name} has invalid format (should start with 'sk-' and be at least 30 characters)"
    
    return True, ""

def validate_config():
    """
    Validates that all required environment variables are set and have proper formats.
    Raises ValueError with a message if any validation fails.
    
    Raises:
        ValueError: If any required configuration is missing or invalid
    """
    required_vars = {
        "ALPACA_API_KEY": ALPACA_API_KEY,
        "ALPACA_SECRET_KEY": ALPACA_SECRET_KEY,
        "OPENAI_API_KEY": OPENAI_API_KEY,
        "ALPACA_API_URL": ALPACA_API_URL,
        "ALPACA_DATA_API_URL": ALPACA_DATA_API_URL
    }
    
    # Redis is not critical for basic operation, but log warning if missing
    if not REDIS_HOST or not REDIS_PORT:
        print("Warning: Redis configuration is incomplete. Redis features will not be available.")
    
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
    
    if validation_errors:
        error_list = ", ".join(validation_errors)
        raise ValueError(f"API key validation failed: {error_list}")

def check_for_hardcoded_secrets():
    """
    Scans Python files in the project for potentially hardcoded API keys.
    This is a basic security check to ensure secrets aren't committed to version control.
    
    Returns:
        list: A list of files with potential hardcoded secrets
    """
    suspicious_files = []
    
    # Common patterns for API keys
    patterns = [
        r'sk-[a-zA-Z0-9]{30,}',  # OpenAI API key pattern
        r'api[_-]?key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',  # Generic API key assignment
        r'secret[_-]?key\s*=\s*["\'][a-zA-Z0-9]{20,}["\']',  # Generic secret key assignment
    ]
    
    # Directories to exclude
    exclude_dirs = ['venv', 'env', '.git', '__pycache__', 'node_modules']
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
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
                    # Skip files that can't be read
                    pass
    
    return suspicious_files

def get_secure_config_summary():
    """
    Returns a safe summary of the current configuration with masked API keys.
    This is useful for logging the current config without exposing secrets.
    
    Returns:
        dict: A dictionary with masked configuration values
    """
    return {
        "ALPACA_API_KEY": mask_api_key(ALPACA_API_KEY),
        "ALPACA_SECRET_KEY": mask_api_key(ALPACA_SECRET_KEY),
        "OPENAI_API_KEY": mask_api_key(OPENAI_API_KEY),
        "ENVIRONMENT": ENVIRONMENT,
        "ALPACA_API_URL": ALPACA_API_URL,
        "ALPACA_DATA_API_URL": ALPACA_DATA_API_URL,
        "TARGET_INDEX_FUNDS": TARGET_INDEX_FUNDS,
        "ENV_FILE_PATH": ENV_FILE_PATH
    } 