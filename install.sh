#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Function to display the header
show_header() {
    echo -e "${BLUE}==================================${NC}"
    echo -e "${BLUE}  Trader App Installation Script  ${NC}"
    echo -e "${BLUE}==================================${NC}"
}

# Function to display uninstall header
show_uninstall_header() {
    echo -e "${RED}==================================${NC}"
    echo -e "${RED}  Trader App Uninstall Process    ${NC}"
    echo -e "${RED}==================================${NC}"
}

# Function to uninstall/reset the environment
uninstall() {
    show_uninstall_header
    
    if [ "$1" != "--force" ]; then
        # Ask for confirmation
        echo -e "${RED}WARNING: This will delete your virtual environment and reset the project.${NC}"
        echo -e "${RED}Any customizations you've made to the venv will be lost.${NC}"
        echo -e "${YELLOW}Your code and .env file will be preserved.${NC}"
        read -p "Are you sure you want to continue? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${GREEN}Uninstall cancelled.${NC}"
            exit 0
        fi
    fi

    # Stop and remove Docker containers if Docker is available
    if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Stopping and removing Docker containers...${NC}"
        docker-compose down -v || echo -e "${RED}Failed to stop Docker containers. Continuing...${NC}"
        echo -e "${GREEN}Docker containers removed.${NC}"
    fi

    # Remove virtual environment
    echo -e "${YELLOW}Removing virtual environment...${NC}"
    rm -rf .venv
    echo -e "${GREEN}Virtual environment removed.${NC}"

    # Remove any pth files or other configuration
    echo -e "${YELLOW}Removing any Python configuration files...${NC}"
    rm -f *.pth
    echo -e "${GREEN}Configuration files removed.${NC}"

    # Remove __pycache__ directories to clean up
    echo -e "${YELLOW}Removing Python cache files...${NC}"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
    find . -type f -name "*.pyc" -delete 2>/dev/null
    echo -e "${GREEN}Python cache files removed.${NC}"
    
    echo -e "${BLUE}==================================${NC}"
    echo -e "${GREEN}Environment Reset Complete!${NC}"
    echo -e "${BLUE}==================================${NC}"
    echo 
    echo -e "${CYAN}To reinstall the Trader App:${NC}"
    echo -e "  ${BOLD}./install.sh${NC}"
    echo
    echo -e "${CYAN}Or to run without installation:${NC}"
    echo -e "  ${BOLD}./trade.py${NC}"
    echo
    
    exit 0
}

# Parse command line options
while getopts "uhU" opt; do
  case $opt in
    u|U)
      uninstall
      ;;
    h)
      echo -e "${CYAN}Usage:${NC}"
      echo -e "  ${BOLD}./install.sh${NC}         : Install the Market Trader"
      echo -e "  ${BOLD}./install.sh -u${NC}      : Uninstall/reset the environment"
      echo -e "  ${BOLD}./install.sh -h${NC}      : Show this help message"
      exit 0
      ;;
    \?)
      echo "Invalid option: -$OPTARG" >&2
      exit 1
      ;;
  esac
done

# Display the header
show_header

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    echo "Please install Python 3.8 or higher before continuing."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
required_version="3.8"
if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo -e "${RED}Error: Python $python_version is installed but Python $required_version or higher is required${NC}"
    exit 1
fi

echo -e "${GREEN}Python $python_version detected${NC}"

# Check for Docker and Docker Compose
if command -v docker &> /dev/null; then
    echo -e "${GREEN}Docker is installed${NC}"
    docker_installed=true
else
    echo -e "${YELLOW}Docker is not installed. Redis will not be available as a container.${NC}"
    docker_installed=false
fi

if command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}Docker Compose is installed${NC}"
    docker_compose_installed=true
else
    echo -e "${YELLOW}Docker Compose is not installed. Redis will not be available as a container.${NC}"
    docker_compose_installed=false
fi

# Remove any existing virtual environment before creating a new one
echo -e "${YELLOW}Removing any existing virtual environment (venv or .venv)...${NC}"
rm -rf venv .venv

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment${NC}"
        exit 1
    fi
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${YELLOW}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source .venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated${NC}"

# Set PYTHONPATH to include src for proper imports
echo -e "${YELLOW}Setting PYTHONPATH to include src directory...${NC}"
export PYTHONPATH="${PWD}/src:$PYTHONPATH"
echo -e "${GREEN}PYTHONPATH set to: $PYTHONPATH${NC}"

# Ensure pip is up to date in the virtual environment
echo -e "${YELLOW}Updating pip...${NC}"
python -m ensurepip --upgrade || curl https://bootstrap.pypa.io/get-pip.py | python
echo -e "${GREEN}Pip is installed/updated${NC}"

# Now upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}Pip is up to date${NC}"

# Install requirements first
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install requirements${NC}"
    exit 1
fi
echo -e "${GREEN}Requirements installed successfully${NC}"

# Install package in development mode using a different approach
echo -e "${YELLOW}Installing the Trader App package...${NC}"
# Create a minimal .pth file to make the package available
mkdir -p .venv/lib/python${python_version}/site-packages/
cat > .venv/lib/python${python_version}/site-packages/trader_app.pth << EOF
${PWD}/src/trader_app
EOF
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install package${NC}"
    exit 1
fi
echo -e "${GREEN}Package installed successfully using .pth file${NC}"

# Check if environment files exist
if [ ! -f ".env.dev" ] && [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating sample environment files...${NC}"
    
    # Create development environment file (.env.dev)
    echo -e "${YELLOW}Creating development environment file (.env.dev)...${NC}"
    cat > .env.dev << EOF
# Development Environment (Paper Trading)
# API Keys
ALPACA_API_KEY=your_dev_alpaca_api_key_here
ALPACA_SECRET_KEY=your_dev_alpaca_secret_key_here
OPENAI_API_KEY=your_dev_openai_api_key_here

# Environment setting
ENVIRONMENT=paper

# API Endpoints
ALPACA_API_URL=https://paper-api.alpaca.markets
ALPACA_DATA_API_URL=https://data.alpaca.markets

# Trading Configuration
TARGET_INDEX_FUNDS=SPY,QQQ,DIA

# Debug mode
DEBUG=true

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=dev_password_here
REDIS_DB=0
REDIS_USE_SSL=false
EOF
    echo -e "${GREEN}Sample .env.dev file created${NC}"
    
    # Create production environment file (.env)
    echo -e "${YELLOW}Creating production environment file (.env)...${NC}"
    cat > .env << EOF
# Production Environment (Live Trading)
# API Keys
ALPACA_API_KEY=your_prod_alpaca_api_key_here
ALPACA_SECRET_KEY=your_prod_alpaca_secret_key_here
OPENAI_API_KEY=your_prod_openai_api_key_here

# Environment setting
ENVIRONMENT=live

# API Endpoints
ALPACA_API_URL=https://api.alpaca.markets
ALPACA_DATA_API_URL=https://data.alpaca.markets

# Trading Configuration
TARGET_INDEX_FUNDS=SPY,QQQ,DIA

# Debug mode
DEBUG=false

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=your_secure_password_here
REDIS_DB=0
REDIS_USE_SSL=false
EOF
    echo -e "${GREEN}Sample .env file created${NC}"
    echo -e "${YELLOW}Please edit these files with your actual API keys${NC}"
    echo -e "${YELLOW}Use .env.dev for development/paper trading and .env for production/live trading${NC}"
else
    if [ -f ".env.dev" ]; then
        echo -e "${YELLOW}A .env.dev file already exists${NC}"
    fi
    if [ -f ".env" ]; then
        echo -e "${YELLOW}A .env file already exists${NC}"
    fi
    echo -e "${GREEN}Environment files are already configured${NC}"
fi

# Start Docker Redis container if Docker is available
if [ "$docker_installed" = true ] && [ "$docker_compose_installed" = true ]; then
    echo -e "${YELLOW}Setting up Redis using Docker...${NC}"
    if [ -f "docker-compose.yml" ]; then
        echo -e "${YELLOW}Starting Redis container...${NC}"
        docker-compose up -d redis
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to start Redis container${NC}"
            echo -e "${YELLOW}You can start it manually with: docker-compose up -d redis${NC}"
        else
            echo -e "${GREEN}Redis container started successfully${NC}"
        fi
    else
        echo -e "${RED}docker-compose.yml not found${NC}"
        echo -e "${YELLOW}Please create a docker-compose.yml file to use Redis with Docker${NC}"
    fi
else
    echo -e "${YELLOW}Docker and/or Docker Compose not installed. Skipping Redis container setup.${NC}"
    echo -e "${YELLOW}Please install Redis manually or use Docker for containerized Redis.${NC}"
fi

# Create a shell alias file for easier execution
echo -e "${YELLOW}Creating command shortcut...${NC}"
cat > ${PWD}/trader_app-alias.sh << EOF
#!/bin/sh
# Add this to your .bashrc or .zshrc with:
# source /path/to/trader_app-alias.sh

# Trader App activation
trader_app_activate() {
  . "${PWD}/.venv/bin/activate"
  echo "Trader App environment activated"
}

# Run the Trader App
trader_app() {
  if [ "\$VIRTUAL_ENV" = "" ]; then
    . "${PWD}/.venv/bin/activate"
  fi
  python -m trader_app "\$@"
}
EOF
chmod +x ${PWD}/trader_app-alias.sh
echo -e "${GREEN}Created ${PWD}/trader_app-alias.sh${NC}"
echo -e "${YELLOW}Add to your shell configuration with: source ${PWD}/trader_app-alias.sh${NC}"

# Make trade.py executable
if [ -f "trade.py" ]; then
    echo -e "${YELLOW}Making trade.py executable...${NC}"
    chmod +x trade.py
    echo -e "${GREEN}trade.py is now executable${NC}"
fi

# Verify installation by running a check
echo -e "${YELLOW}Verifying installation...${NC}"
python -c "import sys; sys.path.insert(0, '${PWD}'); import trader_app; print('✅ Package can be imported successfully')"
if [ $? -ne 0 ]; then
    echo -e "${RED}Warning: Package import verification failed${NC}"
    echo -e "${YELLOW}You may still be able to run the trader using ./trade.py${NC}"
else
    echo -e "${GREEN}Installation verified successfully${NC}"
fi

# Make sure test runner script is executable
if [ -f "run_tests.sh" ]; then
    echo -e "${YELLOW}Making test runner script executable...${NC}"
    chmod +x run_tests.sh
    echo -e "${GREEN}Test runner script is now executable${NC}"
else
    echo -e "${RED}Error: run_tests.sh not found${NC}"
    echo -e "${YELLOW}Please make sure the run_tests.sh file exists in the project root${NC}"
fi

# Run tests after installation if user wants to
echo -e "${YELLOW}Would you like to run tests now to verify installation? (y/n)${NC}"
read -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running tests...${NC}"
    ${PWD}/run_tests.sh
    if [ $? -ne 0 ]; then
        echo -e "${RED}Some tests failed, but installation is still complete.${NC}"
        echo -e "${YELLOW}You may want to check the test failures before using the application.${NC}"
    else
        echo -e "${GREEN}All tests passed!${NC}"
    fi
fi

echo -e "${BLUE}==================================${NC}"
echo -e "${GREEN}${BOLD}Installation Complete!${NC}"
echo -e "${BLUE}==================================${NC}"
echo 
echo -e "${CYAN}To run the Trader App:${NC}"
echo -e "  ${BOLD}- Simply run: ./trade.py${NC}"
echo
echo -e "${CYAN}For checking configuration:${NC}"
echo -e "  ${BOLD}./trade.py --check-config${NC}"
echo
echo -e "${CYAN}For custom environment file:${NC}"
echo -e "  ${BOLD}./trade.py --env-file=path/to/custom/config.env${NC}"
echo
echo -e "${CYAN}Environment Configuration:${NC}"
echo -e "  ${BOLD}- .env.dev${NC} for development/paper trading"
echo -e "  ${BOLD}- .env${NC} for production/live trading"
echo
echo -e "${CYAN}For debug mode:${NC}"
echo -e "  ${BOLD}./trade.py --debug${NC}"
echo
echo -e "${CYAN}Redis Docker Container:${NC}"
echo -e "  ${BOLD}- Start: docker-compose up -d redis${NC}"
echo -e "  ${BOLD}- Stop: docker-compose down${NC}"
echo
echo -e "${CYAN}To run all tests:${NC}"
echo -e "  ${BOLD}./run_tests.sh${NC}"
echo
echo -e "${CYAN}To uninstall/reset the environment:${NC}"
echo -e "  ${BOLD}./install.sh -u${NC}"
echo
echo -e "${GREEN}${BOLD}Happy trading with Trader App!${NC}" 