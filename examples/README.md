# Environment Configuration

This trading bot uses environment-specific configuration files to separate development (paper trading) from production (live trading) settings.

## Environment Files

The system looks for environment files in the following order:

1. **Custom environment file** specified via `ENV_FILE` environment variable or `--env-file` command-line option
2. **.env.dev** in the project root directory (development environment)
3. **.env** in the project root directory (production environment)
4. **examples/env.dev** or **examples/env.prod** if no files are found in the project root

## Setup Instructions

1. Copy the appropriate example file to your project root:
   - For development: `cp examples/env.dev .env.dev`
   - For production: `cp examples/env.prod .env`

2. Edit the file and replace placeholder values with your actual API keys.

3. Alternative ways to specify environment files:
   - Using environment variable: `ENV_FILE=/path/to/my/config.env python trade.py`
   - Using command-line option: `python trade.py --env-file=/path/to/my/config.env`

## Environment Variables

### Required Variables

- `ALPACA_API_KEY` - Your Alpaca API key
- `ALPACA_SECRET_KEY` - Your Alpaca secret key
- `OPENAI_API_KEY` - Your OpenAI API key
- `ALPACA_API_URL` - Alpaca API endpoint (different in dev vs. prod)
- `ALPACA_DATA_API_URL` - Alpaca Data API endpoint

### Optional Variables

- `ENVIRONMENT` - Either "paper" (default) or "live"
- `TARGET_INDEX_FUNDS` - Comma-separated list of index funds to track (default: "SPY,QQQ,DIA")
- `ENV_FILE` - Path to a custom environment file (can also be specified via command line)

## Benefits of Environment-Specific Configuration

1. **Safety**: Completely separate dev and prod environments
2. **Simplicity**: No conditional logic in the code based on environment
3. **Testability**: Easy to test different configurations in development
4. **Consistency**: URLs and API endpoints always match the current environment
5. **Flexibility**: Multiple ways to specify custom environment files

## Example: Testing Different Fund Lists

You can create multiple environment files for testing:

```bash
# Create a test environment file with different funds
cat > .env.test << EOF
ALPACA_API_KEY=your_dev_key_here
ALPACA_SECRET_KEY=your_dev_secret_here
OPENAI_API_KEY=your_dev_openai_key_here
ENVIRONMENT=paper
ALPACA_API_URL=https://paper-api.alpaca.markets
ALPACA_DATA_API_URL=https://data.alpaca.markets
TARGET_INDEX_FUNDS=VTI,VOO,VUG,ARKK
EOF

# Run with the test file
python trade.py --env-file=.env.test
``` 