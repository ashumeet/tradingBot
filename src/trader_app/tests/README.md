# tests

This directory contains all test modules for the trading application, including unit and integration tests.

## Directory Structure

- `unit/` — Unit tests for individual modules and functions. Each test file should be named `test_*.py` and focus on isolated logic.
- `integration/` — Integration tests that cover interactions between multiple modules or external services.
- `conftest.py` — Shared pytest fixtures and hooks for all tests.
- `test_utils.py` (optional) — Common test helper functions (to be created if needed).

## Adding New Tests

- Place new unit tests in `unit/` and integration tests in `integration/`.
- Name test files as `test_<module>.py` and test functions as `test_<functionality>()`.
- Use descriptive docstrings for test functions.
- Use fixtures from `conftest.py` for setup/teardown logic.

## Running Tests

- Use the provided `run_tests.sh` script or run `pytest` from the project root.
- All tests in both subdirectories will be discovered automatically.

## Best Practices

- Keep tests isolated and independent.
- Mock external dependencies in unit tests.
- Use fixtures for reusable setup logic.
- Add clear assertions and error messages.
- Document any non-obvious test logic in comments or docstrings.

## Example Test File

```python
# src/trader_app/tests/unit/test_example.py

def test_addition():
    """Test that addition works as expected."""
    assert 1 + 1 == 2
```