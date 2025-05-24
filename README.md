# Trader App

A modular, maintainable personal trading bot project built with Python, FastAPI, and Alpaca.

## Project Overview
Trader App is a modern trading bot framework designed for flexibility, maintainability, and ease of use. It provides a clean architecture for integrating trading APIs, managing strategies, and running both manual and automated trading workflows.

**Main Features:**
- Modular codebase for easy extension
- REST API for trading operations (FastAPI)
- Alpaca API integration for live and paper trading
- Redis support for caching and state
- Pydantic models for robust data validation
- Colorful CLI output and tabular data display
- Comprehensive test suite with pytest

## Directory Structure
```
src/trader_app/
  api/         # REST API endpoints and logic
  services/    # Business logic and integrations
  models/      # Data models and schemas
  utils/       # Utility functions and helpers
  core/        # Core logic and foundational components
  tests/       # Unit and integration tests
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- (Optional) Docker & Docker Compose for Redis

### Quick Start
```sh
# Clone the repository
$ git clone <your-repo-url>
$ cd tradingBot

# Run the install script (creates venv, installs dependencies, sets up aliases)
$ ./install.sh
```

### Manual Setup (if needed)
```sh
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Environment Variables
- Copy `.env.dev` and `.env` as needed and fill in your API keys and configuration.

## Usage
- Activate the environment: `source venv/bin/activate`
- Run the app: `python -m trader_app`
- Use the provided shell aliases for convenience (see `trader_app-alias.sh`)

## Testing
- Run all tests: `./run_tests.sh` or `pytest src/trader_app/tests`
- Add new tests in `src/trader_app/tests/unit/` or `integration/`

## Contributing
Pull requests are welcome! Please add tests for new features and follow the project structure.

## License
MIT

## Setup and Installation

### Prerequisites
- Python 3.8 or higher
- (Optional) Docker & Docker Compose for Redis

### Installation Steps
1. **Clone the repository:**
   ```sh
   git clone <your-repo-url>
   cd tradingBot
   ```
2. **Run the install script:**
   ```sh
   ./install.sh
   ```
   This will create a virtual environment, install dependencies, and set up shell aliases.
3. **Manual setup (if needed):**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   pip install -r requirements.txt
   ```
4. **Configure environment variables:**
   - Copy `.env.dev` and `.env` as needed and fill in your API keys and configuration.

### Troubleshooting
- If you encounter issues with dependencies, ensure you are using a supported Python version.
- For Redis, either use Docker or install Redis locally.
- For further help, open an issue or check the project discussions.

## Usage
- Activate the environment: `source venv/bin/activate`
- Run the app: `python -m trader_app`
- Use the provided shell aliases for convenience (see `trader_app-alias.sh`)

## Testing
- Run all tests: `./run_tests.sh` or `pytest src/trader_app/tests`
- Add new tests in `src/trader_app/tests/unit/` or `integration/`

## Contributing
Pull requests are welcome! Please add tests for new features and follow the project structure.

## License
MIT
