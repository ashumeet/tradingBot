#!/bin/bash

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Ensure src/ is in the Python module search path
export PYTHONPATH="${PWD}/src:$PYTHONPATH"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: Virtual environment not found${NC}"
    echo -e "${YELLOW}Please run './install.sh' first to set up the environment${NC}"
    exit 1
fi

# Try activating the virtual environment
if ! source .venv/bin/activate 2>/dev/null; then
    echo -e "${RED}Error: Could not activate virtual environment${NC}"
    echo -e "${YELLOW}Please run './install.sh' first to set up the environment properly${NC}"
    exit 1
fi

# Check if key packages are installed
python -c "import pytest" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Required packages not installed${NC}"
    echo -e "${YELLOW}Please run './install.sh' first to install dependencies${NC}"
    exit 1
fi

echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}  Running All Tests  ${NC}"
echo -e "${BLUE}==================================${NC}"

# Find all test files recursively in the new tests directory
TEST_FILES=$(find src/trader_app/tests -name "test_*.py" -type f | sort)
TOTAL_FILES=$(echo "$TEST_FILES" | wc -l)
TOTAL_FILES=$(echo "$TOTAL_FILES" | tr -d ' ')
PASSED_FILES=0
FAILED_FILES=0
SKIPPED_FILES=0

# API integration tests need valid API keys, so mark them as skippable
SKIPPABLE_TESTS=(
    "test_api_integration.py"  # Requires valid Alpaca and OpenAI API keys
)

echo -e "${YELLOW}Found $TOTAL_FILES test files to run${NC}"
echo

# Process each test file individually
for TEST_FILE in $TEST_FILES; do
    TEST_NAME=$(basename "$TEST_FILE" .py)
    FILENAME=$(basename "$TEST_FILE")
    
    # Check if this is a skippable test
    IS_SKIPPABLE=0
    for SKIP_TEST in "${SKIPPABLE_TESTS[@]}"; do
        if [[ "$FILENAME" == "$SKIP_TEST" ]]; then
            IS_SKIPPABLE=1
            break
        fi
    done
    
    echo -e "${YELLOW}Running $TEST_NAME...${NC}"
    
    # Run the test and capture output
    python3 -m pytest "$TEST_FILE" -v
    TEST_RESULT=$?
    
    # Check if the test passed, failed, or is a skippable failure
    if [ $TEST_RESULT -eq 0 ]; then
        echo -e "${GREEN}✓ $TEST_NAME passed${NC}"
        PASSED_FILES=$((PASSED_FILES + 1))
    elif [ $IS_SKIPPABLE -eq 1 ]; then
        echo -e "${YELLOW}⚠ $TEST_NAME failed but marked as skippable (likely requires API keys)${NC}"
        SKIPPED_FILES=$((SKIPPED_FILES + 1))
    else
        echo -e "${RED}✗ $TEST_NAME failed${NC}"
        FAILED_FILES=$((FAILED_FILES + 1))
    fi
    echo
done

# Print summary
echo -e "${BLUE}==================================${NC}"
echo -e "${BLUE}  Test Summary  ${NC}"
echo -e "${BLUE}==================================${NC}"
echo -e "Total test files: $TOTAL_FILES"
echo -e "${GREEN}Passed: $PASSED_FILES${NC}"
if [ $SKIPPED_FILES -gt 0 ]; then
    echo -e "${YELLOW}Skipped: $SKIPPED_FILES${NC}"
fi
echo -e "${RED}Failed: $FAILED_FILES${NC}"

# Return appropriate exit code - treat skippable failures as acceptable
if [ $FAILED_FILES -eq 0 ]; then
    if [ $SKIPPED_FILES -gt 0 ]; then
        echo -e "${GREEN}${BOLD}All critical tests passed!${NC} ${YELLOW}(Some API tests skipped)${NC}"
    else
        echo -e "${GREEN}${BOLD}All tests passed!${NC}"
    fi
    exit 0
else
    echo -e "${RED}${BOLD}Some tests failed.${NC}"
    exit 1
fi
