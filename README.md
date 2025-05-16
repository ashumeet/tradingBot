# Market Trader

A Python-based algorithmic trading platform that uses OpenAI's GPT for market analysis and Alpaca API for trading execution.

## Technologies Used
* OpenAI GPT-4 API for trading analysis
* Alpaca API for portfolio management and trading
* Python 3.8+ with modern package structure

## Features
* Automated minute-by-minute trading
* Volatile stock recommendation via GPT
* Portfolio management and tracking
* Real-time market data analysis
* Secure configuration management
* Comprehensive testing framework

## Project Structure
```
marketTrader/
├── src/
│   └── markettrader/                          # Main package
│       ├── __init__.py                        # Package initialization
│       ├── __main__.py                        # CLI entry point
│       ├── market_trader.py                   # Main application logic
│       ├── config/                            # Configuration module
│       │   ├── __init__.py
│       │   └── config.py                      # Configuration management
│       ├── api/                               # API integrations
│       │   ├── __init__.py
│       │   ├── alpaca.py                      # Alpaca API integration
│       │   └── openai.py                      # OpenAI API integration
│       ├── utils/                             # Utility functions
│       │   ├── __init__.py
│       │   └── common.py                      # Common utilities
│       └── tests/                             # Test modules
│           ├── __init__.py
│           ├── run_tests.py                   # Test runner script
│           ├── unit/                          # Unit tests
│           │   ├── __init__.py
│           │   └── test_config.py
│           └── integration/                   # Integration tests
│               ├── __init__.py
│               └── test_api_integration.py
├── trade.py                                  # Convenience script to run the platform
├── install.sh                                # Installation/uninstallation script
├── .env                                      # Environment variables (not committed)
├── requirements.txt                          # Dependencies
├── setup.py                                  # Package setup
└── README.md                                 # This file
```

## Setup and Configuration

### Prerequisites
- Python 3.8 or higher
- Alpaca trading account
- OpenAI API key

### Installation

#### Option 1: Using the Installation Script (Recommended)
```bash
# Clone the repository
git clone https://github.com/yourusername/marketTrader.git
cd marketTrader

# Run the installation script
chmod +x install.sh
./install.sh
```

#### Option 2: Manual Installation
1. Clone this repository
   ```bash
   git clone https://github.com/yourusername/marketTrader.git
   cd marketTrader
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Add project to Python path:
   ```bash
   # Create a .pth file for development
   echo "$(pwd)/src" > venv/lib/python3.*/site-packages/markettrader.pth
   ```

### Configuration
This trading platform uses environment variables for secure configuration management with multiple loading options:

1. **Environment Hierarchy**:
   - Custom file specified via `ENV_FILE` environment variable or `--env-file` command-line option
   - `.env.dev` in project root (for development/paper trading)
   - `.env` in project root (for production/live trading)
   - Example files in `examples/` as fallback

2. **Development vs. Production**:
   - Use `.env.dev` for paper trading (development) - example: `cp examples/env.dev .env.dev`
   - Use `.env` for live trading (production) - example: `cp examples/env.prod .env`

3. **Required Variables**:
   ```
   # API Keys
   ALPACA_API_KEY=your_alpaca_api_key
   ALPACA_SECRET_KEY=your_alpaca_secret_key
   OPENAI_API_KEY=your_openai_api_key
   
   # API Endpoints (environment-specific)
   ALPACA_API_URL=https://paper-api.alpaca.markets  # For dev
   ALPACA_DATA_API_URL=https://data.alpaca.markets
   
   # Environment setting
   ENVIRONMENT=paper  # Use 'paper' for development or 'live' for production
   
   # Trading Configuration
   TARGET_INDEX_FUNDS=SPY,QQQ,DIA  # Comma-separated list of funds to track
   ```

4. **Command-Line Options**:
   ```bash
   # Run with a specific environment file
   ./trade.py --env-file=path/to/custom/config.env
   
   # Check your configuration
   ./trade.py --check-config
   ```

5. See detailed documentation in `examples/README.md`

### Debug Mode
The application includes a debug mode that provides additional logging information:

```bash
# Using the command line flag
./trade.py --debug

# Using environment variable
export DEBUG=true
./trade.py
```

## Usage

### Running the Market Trader

```bash
# Run the platform
./trade.py

# Check configuration
./trade.py --check-config

# Enable debug mode
./trade.py --debug
```

### Using as a Python Module
```python
from src.markettrader.market_trader import main as run_trader

# Run the platform
run_trader()
```

## Testing

The project follows a test-driven development approach with a comprehensive test suite.

### Test Structure
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components and external services

### Running Tests

#### Using the Test Runner (Recommended)
The project includes a custom test runner that provides consistent, colored output and a clear summary of test results:

```bash
# Run all tests with formatted output
python -m src.markettrader.tests.run_tests

# Run only unit tests
python -m src.markettrader.tests.run_tests --unit-only

# Run only integration tests
python -m src.markettrader.tests.run_tests --integration-only

# Run tests with verbose output
python -m src.markettrader.tests.run_tests --verbose
```

#### Using unittest directly
You can also use Python's unittest framework directly:

```bash
# Run all tests
python -m unittest discover src/markettrader/tests

# Run unit tests only
python -m unittest discover src/markettrader/tests/unit

# Run integration tests only
python -m unittest discover src/markettrader/tests/integration

# Run a specific test file
python -m unittest src.markettrader.tests.unit.test_config
```

#### Checking Configuration
To test your configuration specifically:

```bash
# Run the configuration check
./trade.py --check-config
```

### Creating New Tests
When adding new features, create corresponding test files in the appropriate directories:

- For unit tests: `src/markettrader/tests/unit/`
- For integration tests: `src/markettrader/tests/integration/`

#### Test Naming Conventions
- Test files should be named with the prefix `test_`
- Test classes should inherit from `unittest.TestCase`
- Test methods should start with `test_`

#### Example Test Structure
```python
import unittest

class TestMyFeature(unittest.TestCase):
    def setUp(self):
        # Set up test environment
        pass
        
    def test_specific_functionality(self):
        # Test something specific
        result = my_function()
        self.assertEqual(result, expected_value)
        
    def tearDown(self):
        # Clean up after test
        pass
```

## Troubleshooting

### Common Issues

#### Installation Failed with pip/setup.py Errors
If the installation is failing with pip-related errors:

1. Try using the convenience script directly without installation:
   ```bash
   ./trade.py
   ```

2. Reset the environment and try again:
   ```bash
   ./install.sh -u
   ./install.sh
   ```

#### ModuleNotFoundError
If you see an error like `ModuleNotFoundError: No module named 'src'`:

1. Make sure you're in the project root directory when running the command
2. Use the script `./trade.py` which adds the project root to the Python path

### Resetting the Environment
If you encounter persistent issues, you can reset the entire environment:

1. Run the uninstall option:
   ```bash
   ./install.sh -u
   ```

2. This will:
   - Remove the virtual environment
   - Clear Python cache files
   - Remove any .pth files

3. After resetting, run the installation script again:
   ```bash
   ./install.sh
   ```

### Installation Script Options
The installation script provides several options:

```bash
./install.sh         # Install the Market Trader
./install.sh -u      # Uninstall/reset the environment
./install.sh -h      # Show help information
```

## License
MIT
