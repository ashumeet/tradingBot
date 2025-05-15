"""
Configuration Testing Module

This module provides comprehensive testing and validation for the trading bot's
configuration system. It includes both automated unit tests (TestConfigSecurity) 
and interactive validation functions.

Usage:
    # Run all tests
    python -m unittest src.tradingbot.tests.unit.test_config
    
    # Run interactive test
    python -c "from src.tradingbot.tests.unit.test_config import run_interactive_test; run_interactive_test()"
"""

import os
import sys
import unittest
import json
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Import using absolute imports
from src.markettrader.config import config


# Define some additional color formatting for better visual separation
HEADER = Fore.MAGENTA + Style.BRIGHT
SECTION = Fore.CYAN + Style.BRIGHT
SUCCESS_BRIGHT = Fore.GREEN + Style.BRIGHT
WARNING_BRIGHT = Fore.YELLOW + Style.BRIGHT
ERROR_BRIGHT = Fore.RED + Style.BRIGHT
SEPARATOR = "=" * 70


class TestConfigSecurity(unittest.TestCase):
    def setUp(self):
        # Save original environment variables
        self.original_env = {
            'ALPACA_API_KEY': os.environ.get('ALPACA_API_KEY'),
            'ALPACA_SECRET_KEY': os.environ.get('ALPACA_SECRET_KEY'),
            'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY')
        }
        
        # Clear environment variables for each test
        for key in self.original_env:
            if key in os.environ:
                del os.environ[key]
                
        # Since config.py loads env vars on import, we need to reset the module variables
        config.ALPACA_API_KEY = ""
        config.ALPACA_SECRET_KEY = ""
        config.OPENAI_API_KEY = ""
        
    def tearDown(self):
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value
                
        # Reset the module variables to reflect the restored environment
        config.ALPACA_API_KEY = os.environ.get('ALPACA_API_KEY', "")
        config.ALPACA_SECRET_KEY = os.environ.get('ALPACA_SECRET_KEY', "")
        config.OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', "")
    
    def test_missing_keys(self):
        """Test that validation fails when required keys are missing"""
        # Environment variables are already cleared in setUp
        
        with self.assertRaises(ValueError) as context:
            config.validate_config()
        error_msg = str(context.exception)
        self.assertIn("Missing required environment variables", error_msg)
        print(f"\n{WARNING_BRIGHT}Expected error for missing keys: {error_msg}")
    
    def test_invalid_key_formats(self):
        """Test that validation fails when key formats are invalid"""
        # Set invalid keys
        os.environ['ALPACA_API_KEY'] = 'short'
        os.environ['ALPACA_SECRET_KEY'] = 'test-alpaca-secret-key-12345678901234567890'
        os.environ['OPENAI_API_KEY'] = 'no-prefix-test'
        
        # Update module variables to reflect environment changes
        config.ALPACA_API_KEY = 'short'
        config.ALPACA_SECRET_KEY = 'test-alpaca-secret-key-12345678901234567890'
        config.OPENAI_API_KEY = 'no-prefix-test'
        
        with self.assertRaises(ValueError) as context:
            config.validate_config()
        error_msg = str(context.exception)
        self.assertIn("API key validation failed", error_msg)
        print(f"\n{WARNING_BRIGHT}Expected error for invalid key formats: {error_msg}")
    
    def test_openai_key_format(self):
        """Test specific validation for OpenAI key format"""
        # Set valid Alpaca keys but invalid OpenAI key
        os.environ['ALPACA_API_KEY'] = 'test-alpaca-api-key-12345678901234567890'
        os.environ['ALPACA_SECRET_KEY'] = 'test-alpaca-secret-key-12345678901234567890'
        os.environ['OPENAI_API_KEY'] = 'invalid-no-sk-prefix-but-long-enough-12345678901234567890'
        
        # Update module variables
        config.ALPACA_API_KEY = 'test-alpaca-api-key-12345678901234567890'
        config.ALPACA_SECRET_KEY = 'test-alpaca-secret-key-12345678901234567890'
        config.OPENAI_API_KEY = 'invalid-no-sk-prefix-but-long-enough-12345678901234567890'
        
        with self.assertRaises(ValueError) as context:
            config.validate_config()
        error_msg = str(context.exception)
        self.assertIn("should start with 'sk-'", error_msg)
        print(f"\n{WARNING_BRIGHT}Expected error for invalid OpenAI key format: {error_msg}")
    
    def test_alpaca_key_format(self):
        """Test specific validation for Alpaca key format"""
        # Set invalid Alpaca API key but valid others
        os.environ['ALPACA_API_KEY'] = 'ab12'  # Too short
        os.environ['ALPACA_SECRET_KEY'] = 'test-alpaca-secret-key-12345678901234567890'
        os.environ['OPENAI_API_KEY'] = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        # Update module variables
        config.ALPACA_API_KEY = 'ab12'
        config.ALPACA_SECRET_KEY = 'test-alpaca-secret-key-12345678901234567890'
        config.OPENAI_API_KEY = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        with self.assertRaises(ValueError) as context:
            config.validate_config()
        error_msg = str(context.exception)
        self.assertIn("ALPACA_API_KEY has invalid format", error_msg)
        print(f"\n{WARNING_BRIGHT}Expected error for invalid Alpaca key format: {error_msg}")
    
    def test_masking_api_keys(self):
        """Test that API keys are properly masked"""
        test_key = "abcdefghijklmnopqrstuvwxyz"
        masked = config.mask_api_key(test_key)
        # Update this to match the actual implementation in config.py
        self.assertEqual(masked, "abcd******************wxyz")
        self.assertNotIn("efghijklmnopqrstuv", masked)
        print(f"\n{SUCCESS_BRIGHT}API key masking works correctly")
        print(f"{Fore.WHITE}Original: {test_key}")
        print(f"{Fore.WHITE}Masked:   {masked}")
    
    def test_valid_config(self):
        """Test that validation passes with valid configuration"""
        # Set valid configuration
        os.environ['ALPACA_API_KEY'] = 'test-alpaca-api-key-12345678901234567890'
        os.environ['ALPACA_SECRET_KEY'] = 'test-alpaca-secret-key-12345678901234567890'
        os.environ['OPENAI_API_KEY'] = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        # Update module variables
        config.ALPACA_API_KEY = 'test-alpaca-api-key-12345678901234567890'
        config.ALPACA_SECRET_KEY = 'test-alpaca-secret-key-12345678901234567890'
        config.OPENAI_API_KEY = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        # Should not raise any exception
        config.validate_config()
        
        summary = config.get_secure_config_summary()
        self.assertIn("test", summary["ALPACA_API_KEY"])
        self.assertIn("7890", summary["ALPACA_API_KEY"])
        self.assertIn("sk-t", summary["OPENAI_API_KEY"])
        print(f"\n{SUCCESS_BRIGHT}Valid configuration accepted")
        print(f"{SECTION}Config summary: {json.dumps(summary, indent=2)}")
    
    def test_short_key_masking(self):
        """Test masking for keys that are too short"""
        short_key = "abc"
        masked = config.mask_api_key(short_key)
        self.assertEqual(masked, "invalid-key")
        print(f"\n{SUCCESS_BRIGHT}Short key masking works correctly")
        print(f"{Fore.WHITE}Original: {short_key}")
        print(f"{Fore.WHITE}Masked:   {masked}")
    
    def test_hardcoded_secrets_detection(self):
        """Test detection of hardcoded secrets"""
        suspicious_files = config.check_for_hardcoded_secrets()
        print(f"\n{SECTION}Suspicious files detected: {suspicious_files}")
        # We don't assert anything here as it depends on the state of the codebase


def run_interactive_test():
    """
    Run an interactive test to verify configuration manually.
    
    Returns:
        bool: True if configuration is valid, False otherwise
    """
    print(f"\n{HEADER}{SEPARATOR}")
    print(f"{HEADER} Interactive Configuration Test ")
    print(f"{HEADER}{SEPARATOR}")
    print("This will test your current environment configuration.")
    
    try:
        config.validate_config()
        print(f"\n{SUCCESS_BRIGHT}✓ Configuration is valid!")
        
        print(f"\n{SECTION}Secure configuration summary:")
        summary = config.get_secure_config_summary()
        for key, value in summary.items():
            print(f"  {key}: {value}")
        
        print(f"\n{SECTION}Checking for hardcoded secrets...")
        suspicious_files = config.check_for_hardcoded_secrets()
        if suspicious_files:
            print(f"\n{WARNING_BRIGHT}⚠ Potential hardcoded secrets found in these files:")
            for file in suspicious_files:
                print(f"  - {file}")
            print(f"{Fore.YELLOW}Consider moving these secrets to environment variables.")
        else:
            print(f"\n{SUCCESS_BRIGHT}✓ No hardcoded secrets detected in Python files.")
        
    except ValueError as e:
        print(f"\n{ERROR_BRIGHT}✗ Configuration error: {str(e)}")
        print(f"\n{Fore.WHITE}To fix this error:")
        print(f"{Fore.WHITE}1. Set your API keys as environment variables:")
        print(f"{Fore.WHITE}   export ALPACA_API_KEY=your-api-key")
        print(f"{Fore.WHITE}   export ALPACA_SECRET_KEY=your-secret-key")
        print(f"{Fore.WHITE}   export OPENAI_API_KEY=your-openai-key")
        print(f"{Fore.WHITE}2. Or create a .env file in the project root with these variables")
        return False
    
    return True


def demonstrate_bad_config():
    """
    Demonstrate what happens with invalid configuration.
    
    Shows examples of:
    - Missing API keys
    - Invalid API key formats
    - Incorrect key prefixes
    """
    print(f"\n{HEADER}{SEPARATOR}")
    print(f"{HEADER} Bad Configuration Examples ")
    print(f"{HEADER}{SEPARATOR}")
    
    # Save original environment and module variables
    original_env = {
        'ALPACA_API_KEY': os.environ.get('ALPACA_API_KEY'),
        'ALPACA_SECRET_KEY': os.environ.get('ALPACA_SECRET_KEY'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY')
    }
    
    original_values = {
        'ALPACA_API_KEY': config.ALPACA_API_KEY,
        'ALPACA_SECRET_KEY': config.ALPACA_SECRET_KEY,
        'OPENAI_API_KEY': config.OPENAI_API_KEY
    }
    
    try:
        # Example 1: Missing keys
        print(f"\n{SECTION}Example 1: Missing API keys{Style.RESET_ALL}")
        for key in original_env:
            if key in os.environ:
                del os.environ[key]
        
        # Reset module variables
        config.ALPACA_API_KEY = ""
        config.ALPACA_SECRET_KEY = ""
        config.OPENAI_API_KEY = ""
        
        try:
            config.validate_config()
            print(f"{SUCCESS_BRIGHT}✓ Validation passed (unexpected)")
        except ValueError as e:
            print(f"{ERROR_BRIGHT}✗ Error: {str(e)}")
        
        # Example 2: Invalid OpenAI key format
        print(f"\n{SECTION}Example 2: Invalid OpenAI key format{Style.RESET_ALL}")
        os.environ['ALPACA_API_KEY'] = 'test-alpaca-api-key-12345678901234567890'
        os.environ['ALPACA_SECRET_KEY'] = 'test-alpaca-secret-key-12345678901234567890'
        os.environ['OPENAI_API_KEY'] = 'no-sk-prefix-but-long-enough'
        
        # Update module variables
        config.ALPACA_API_KEY = 'test-alpaca-api-key-12345678901234567890'
        config.ALPACA_SECRET_KEY = 'test-alpaca-secret-key-12345678901234567890'
        config.OPENAI_API_KEY = 'no-sk-prefix-but-long-enough'
        
        try:
            config.validate_config()
            print(f"{SUCCESS_BRIGHT}✓ Validation passed (unexpected)")
        except ValueError as e:
            print(f"{ERROR_BRIGHT}✗ Error: {str(e)}")
        
        # Example 3: Short Alpaca key
        print(f"\n{SECTION}Example 3: Alpaca key too short{Style.RESET_ALL}")
        os.environ['ALPACA_API_KEY'] = 'too-short'
        os.environ['OPENAI_API_KEY'] = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        # Update module variables
        config.ALPACA_API_KEY = 'too-short'
        config.OPENAI_API_KEY = 'sk-testtesttesttesttesttesttesttesttesttest'
        
        try:
            config.validate_config()
            print(f"{SUCCESS_BRIGHT}✓ Validation passed (unexpected)")
        except ValueError as e:
            print(f"{ERROR_BRIGHT}✗ Error: {str(e)}")
            
    finally:
        # Restore original environment
        for key, value in original_env.items():
            if value is None:
                if key in os.environ:
                    del os.environ[key]
            else:
                os.environ[key] = value
        
        # Restore original module variables
        config.ALPACA_API_KEY = original_values['ALPACA_API_KEY']
        config.ALPACA_SECRET_KEY = original_values['ALPACA_SECRET_KEY']
        config.OPENAI_API_KEY = original_values['OPENAI_API_KEY']


def print_usage_instructions():
    """Print instructions for using the config test module"""
    print(f"\n{HEADER}{SEPARATOR}")
    print(f"{HEADER} Configuration Testing Usage ")
    print(f"{HEADER}{SEPARATOR}")
    print("This module provides several ways to test your configuration:")
    
    print(f"\n{SECTION}1. Run automated tests:")
    print(f"{Fore.WHITE}   python -m unittest src.tradingbot.tests.unit.test_config")
    
    print(f"\n{SECTION}2. Test your current configuration:")
    print(f"{Fore.WHITE}   python -c \"from src.tradingbot.tests.unit.test_config import run_interactive_test; run_interactive_test()\"")
    
    print(f"\n{SECTION}3. Demonstrate bad configuration examples:")
    print(f"{Fore.WHITE}   python -c \"from src.tradingbot.tests.unit.test_config import demonstrate_bad_config; demonstrate_bad_config()\"")
    
    print(f"\n{SECTION}4. Run manually from command line:")
    print(f"{Fore.WHITE}   export ALPACA_API_KEY=test-alpaca-api-key-12345678901234567890")
    print(f"{Fore.WHITE}   export ALPACA_SECRET_KEY=test-alpaca-secret-key-12345678901234567890")
    print(f"{Fore.WHITE}   export OPENAI_API_KEY=sk-testtesttesttesttesttesttesttesttesttest")
    print(f"{Fore.WHITE}   python -c \"from src.tradingbot.config import get_secure_config_summary; import json; print(json.dumps(get_secure_config_summary(), indent=2))\"")
    
    print(f"\n{SECTION}5. Check what keys you have set currently:")
    print(f"{Fore.WHITE}   python -c \"from src.tradingbot.config import ALPACA_API_KEY, mask_api_key; print(f'ALPACA_API_KEY: {{mask_api_key(ALPACA_API_KEY)}}')\"")
    print(f"{Fore.WHITE}   python -c \"from src.tradingbot.config import OPENAI_API_KEY, mask_api_key; print(f'OPENAI_API_KEY: {{mask_api_key(OPENAI_API_KEY)}}')\"")


if __name__ == '__main__':
    print_usage_instructions()
    
    # If arguments are provided, process them
    if len(sys.argv) > 1:
        if sys.argv[1] == "test":
            run_interactive_test()
        elif sys.argv[1] == "demo":
            demonstrate_bad_config()
        elif sys.argv[1] == "unittest":
            unittest.main(argv=['first-arg-is-ignored'])
        else:
            print(f"\n{WARNING_BRIGHT}Unknown argument: {sys.argv[1]}")
            print(f"{Fore.YELLOW}Valid arguments: test, demo, unittest")
    else:
        # If no arguments, run everything
        print("\nRunning interactive test...")
        run_interactive_test()
        
        print("\nDemonstrating bad configuration examples...")
        demonstrate_bad_config()
        
        print("\nRunning automated tests...")
        unittest.main(argv=['first-arg-is-ignored'], exit=False) 