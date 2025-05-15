#!/usr/bin/env python3
"""
Test Runner

This module provides a unified way to run all tests in the project with 
consistent output formatting. It's designed for test-driven development 
to ensure all existing tests pass as new features are added.

Usage:
    # Run all tests
    python -m src.tradingbot.tests.run_tests
    
    # Run only unit tests
    python -m src.tradingbot.tests.run_tests --unit-only
    
    # Run only integration tests
    python -m src.tradingbot.tests.run_tests --integration-only
    
    # Run with verbose output
    python -m src.tradingbot.tests.run_tests --verbose
"""

import unittest
import argparse
import sys
import os
from colorama import Fore, Style, init

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

# Constants for formatting
SEPARATOR = "=" * 70
TEST_HEADER = f"{Fore.CYAN}{Style.BRIGHT}"
TEST_SUCCESS = f"{Fore.GREEN}{Style.BRIGHT}"
TEST_FAILURE = f"{Fore.RED}{Style.BRIGHT}"
TEST_SKIPPED = f"{Fore.YELLOW}"
TEST_RUNNING = f"{Fore.BLUE}"

def setup_test_environment():
    """
    Set up the Python path to ensure tests can import the package correctly.
    This allows running the tests from the project root directory.
    """
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    # Add the project root to the Python path if not already there
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    print(f"{TEST_HEADER}Using project root: {project_root}{Style.RESET_ALL}")

def get_test_suite(unit_only=False, integration_only=False):
    """
    Build the test suite based on command line arguments.
    
    Args:
        unit_only (bool): If True, only include unit tests
        integration_only (bool): If True, only include integration tests
        
    Returns:
        unittest.TestSuite: The test suite to run
    """
    if unit_only and integration_only:
        raise ValueError("Cannot specify both unit-only and integration-only")
    
    # Determine the test directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    if unit_only:
        test_dir = os.path.join(base_dir, "unit")
        print(f"{TEST_HEADER}Running Unit Tests Only{Style.RESET_ALL}")
    elif integration_only:
        test_dir = os.path.join(base_dir, "integration")
        print(f"{TEST_HEADER}Running Integration Tests Only{Style.RESET_ALL}")
    else:
        test_dir = base_dir
        print(f"{TEST_HEADER}Running All Tests{Style.RESET_ALL}")
    
    # Discover tests
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=test_dir, pattern="test_*.py")
    
    return suite

class TradingBotTestResult(unittest.TextTestResult):
    """
    Custom test result class to provide consistent output formatting.
    """
    def startTest(self, test):
        super().startTest(test)
        if self.showAll:
            test_name = self.getDescription(test)
            self.stream.write(f"{TEST_RUNNING}Running: {test_name}... {Style.RESET_ALL}")
            self.stream.flush()
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showAll:
            self.stream.writeln(f"{TEST_SUCCESS}✓ PASS{Style.RESET_ALL}")
        else:
            self.stream.write(f"{TEST_SUCCESS}✓{Style.RESET_ALL}")
    
    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.writeln(f"{TEST_FAILURE}✗ ERROR{Style.RESET_ALL}")
        else:
            self.stream.write(f"{TEST_FAILURE}E{Style.RESET_ALL}")
    
    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.writeln(f"{TEST_FAILURE}✗ FAIL{Style.RESET_ALL}")
        else:
            self.stream.write(f"{TEST_FAILURE}F{Style.RESET_ALL}")
    
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.writeln(f"{TEST_SKIPPED}⚠ SKIPPED: {reason}{Style.RESET_ALL}")
        else:
            self.stream.write(f"{TEST_SKIPPED}s{Style.RESET_ALL}")

class TradingBotTestRunner(unittest.TextTestRunner):
    """
    Custom test runner to use our custom test result class.
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resultclass = TradingBotTestResult
    
    def run(self, test):
        """
        Run the tests with custom formatting.
        
        Args:
            test: The test suite to run
            
        Returns:
            TradingBotTestResult: The test results
        """
        print(f"\n{SEPARATOR}")
        print(f"{TEST_HEADER}RUNNING TESTS{Style.RESET_ALL}")
        print(f"{SEPARATOR}\n")
        
        result = super().run(test)
        
        print(f"\n{SEPARATOR}")
        print(f"{TEST_HEADER}TEST RESULTS SUMMARY{Style.RESET_ALL}")
        print(f"{SEPARATOR}")
        
        # Print summary with colors
        if result.wasSuccessful():
            print(f"{TEST_SUCCESS}✓ All tests passed successfully!{Style.RESET_ALL}")
        else:
            print(f"{TEST_FAILURE}✗ Tests failed: {len(result.failures) + len(result.errors)} failures/errors{Style.RESET_ALL}")
        
        print(f"\nRan {result.testsRun} tests with:")
        print(f" - {TEST_SUCCESS}{len(result.successes) if hasattr(result, 'successes') else result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)} passed{Style.RESET_ALL}")
        if result.failures:
            print(f" - {TEST_FAILURE}{len(result.failures)} failed{Style.RESET_ALL}")
        if result.errors:
            print(f" - {TEST_FAILURE}{len(result.errors)} errors{Style.RESET_ALL}")
        if result.skipped:
            print(f" - {TEST_SKIPPED}{len(result.skipped)} skipped{Style.RESET_ALL}")
        
        print(f"\n{SEPARATOR}\n")
        
        return result

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Run Trading Bot tests")
    
    # Test selection options
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--unit-only", action="store_true", help="Run only unit tests")
    group.add_argument("--integration-only", action="store_true", help="Run only integration tests")
    
    # Verbosity options
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    
    return parser.parse_args()

def main():
    """Main entry point for the test runner."""
    # Set up test environment
    setup_test_environment()
    
    # Parse command line arguments
    args = parse_args()
    
    # Create the test suite
    suite = get_test_suite(unit_only=args.unit_only, integration_only=args.integration_only)
    
    # Run the tests
    verbosity = 2 if args.verbose else 1
    runner = TradingBotTestRunner(verbosity=verbosity)
    result = runner.run(suite)
    
    # Return appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(main()) 