# Testing Documentation

## Overview

Universus includes a comprehensive test suite following Python testing standards using **pytest** framework. The tests are organized by layer and provide excellent coverage of all critical functionality.

## Test Statistics

- **Total Tests**: 88
- **Test Files**: 4
- **Coverage**: 66% overall, 100% for tested modules
- **Framework**: pytest 7.0+

## Test Structure

```
universus/
├── test_database.py      # Database layer tests (17 tests)
├── test_api_client.py    # API client tests (20 tests)
├── test_service.py       # Service layer tests (23 tests)
├── test_ui.py            # UI layer tests (28 tests)
└── pytest.ini            # Pytest configuration
```

## Running Tests

### Install Test Dependencies

```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
pytest test_database.py
pytest test_api_client.py
pytest test_service.py
pytest test_ui.py
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Coverage Report

```bash
pytest --cov=. --cov-report=term-missing
```

### Run Specific Test Class

```bash
pytest test_database.py::TestMarketDatabase
```

### Run Specific Test Method

```bash
pytest test_database.py::TestMarketDatabase::test_add_tracked_item
```

## Test Coverage by Module

### Database Layer (test_database.py)
**Coverage: 100%** | **17 tests**

Tests for SQLite database operations:

- ✅ Database initialization and schema creation
- ✅ Adding tracked items (single, duplicate, multiple worlds)
- ✅ Retrieving tracked items (all, filtered by world)
- ✅ Saving market snapshots
- ✅ Saving sales history (with duplicate detection)
- ✅ Retrieving historical snapshots
- ✅ Getting top volume items
- ✅ Context manager functionality
- ✅ Connection cleanup

**Key Test Cases:**
```python
def test_add_tracked_item(db)
def test_add_duplicate_tracked_item(db)
def test_save_snapshot(db)
def test_save_duplicate_sales(db)
def test_get_top_volume_items(db)
```

### API Client Layer (test_api_client.py)
**Coverage: 100%** | **20 tests**

Tests for HTTP client and rate limiting:

- ✅ Rate limiter initialization and behavior
- ✅ Rate limiting enforcement
- ✅ API client initialization
- ✅ HTTP request/response handling
- ✅ Error handling (HTTP errors, timeouts, connection errors)
- ✅ All API methods (datacenters, market data, history)
- ✅ Request parameters and URL construction
- ✅ Session management
- ✅ Context manager functionality

**Key Test Cases:**
```python
def test_rate_limiting_enforced()
def test_make_request_success(api, mock_session)
def test_make_request_http_error(api, mock_session)
def test_get_market_data(api, mock_session)
def test_rate_limiting_integration(api, mock_session)
```

### Service Layer (test_service.py)
**Coverage: 99%** | **23 tests**

Tests for business logic:

- ✅ Service initialization with dependencies
- ✅ Tracking initialization workflow
- ✅ Item filtering by velocity
- ✅ Update operations (success, partial failure, errors)
- ✅ Top items retrieval
- ✅ Historical reporting
- ✅ Trend calculations
- ✅ Time formatting utilities
- ✅ Error handling in workflows

**Key Test Cases:**
```python
def test_initialize_tracking_success(service, mock_db, mock_api)
def test_update_tracked_items_success(service, mock_db, mock_api)
def test_calculate_trends_with_data(service)
def test_initialize_tracking_handles_api_errors(service, mock_db, mock_api)
```

### UI Layer (test_ui.py)
**Coverage: 98%** | **28 tests**

Tests for presentation and formatting:

- ✅ Status messages (success, error, warning, info)
- ✅ Table formatting (datacenters, items, reports)
- ✅ Progress indicators
- ✅ Trend display (positive/negative)
- ✅ Empty state handling
- ✅ Null value handling
- ✅ Exit error handling

**Key Test Cases:**
```python
def test_show_datacenters_with_data(mock_console)
def test_show_top_items_with_null_values(mock_console)
def test_show_trends_positive_change(mock_console)
def test_exit_with_error(mock_console)
```

## Testing Patterns Used

### 1. Fixtures for Test Setup

```python
@pytest.fixture
def db():
    """Create an in-memory database for testing."""
    database = MarketDatabase(":memory:")
    yield database
    database.close()

@pytest.fixture
def service(mock_db, mock_api):
    """Create service with mocked dependencies."""
    return MarketService(mock_db, mock_api)
```

### 2. Mocking External Dependencies

```python
@pytest.fixture
def mock_api(self):
    """Create a mock API client."""
    return Mock()

# Usage
mock_api.get_market_data.return_value = {'price': 1000}
```

### 3. In-Memory Database for Tests

```python
# No file I/O during tests
db = MarketDatabase(":memory:")
```

### 4. Parameterized Testing (When Needed)

```python
@pytest.mark.parametrize("velocity,expected", [
    (10.0, True),
    (0.0, False),
    (-5.0, False)
])
def test_velocity_filter(velocity, expected):
    assert is_valid_velocity(velocity) == expected
```

### 5. Testing Error Conditions

```python
def test_make_request_timeout(api, mock_session):
    mock_session.get.side_effect = requests.Timeout("Request timeout")
    
    with pytest.raises(requests.Timeout):
        api._make_request("https://test.com/api")
```

## Test Categories

### Unit Tests
All tests are unit tests that test individual components in isolation:

```bash
# Run all unit tests
pytest -m unit
```

### Integration Tests
Can be added with marker:

```python
@pytest.mark.integration
def test_full_update_workflow():
    # Test multiple components together
    pass
```

### Slow Tests
Long-running tests can be marked:

```python
@pytest.mark.slow
def test_large_dataset():
    # Test with large data
    pass
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v2
```

## Coverage Reports

### Terminal Report

```bash
pytest --cov=. --cov-report=term-missing
```

Output:
```
Name               Stmts   Miss  Cover   Missing
------------------------------------------------
database.py           79      0   100%
api_client.py         69      0   100%
service.py           100      1    99%   49
ui.py                130      2    98%   81, 118
------------------------------------------------
TOTAL                378      3    99%
```

### HTML Report

```bash
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### XML Report (for CI)

```bash
pytest --cov=. --cov-report=xml
```

## Writing New Tests

### Test File Template

```python
"""
Unit tests for [module_name].
"""

import pytest
from unittest.mock import Mock, patch
from [module_name] import [ClassName]


class Test[ClassName]:
    """Test suite for [ClassName] class."""
    
    @pytest.fixture
    def instance(self):
        """Create instance for testing."""
        return [ClassName]()
    
    def test_basic_functionality(self, instance):
        """Test basic functionality."""
        result = instance.method()
        assert result is not None
    
    def test_error_condition(self, instance):
        """Test error handling."""
        with pytest.raises(ValueError):
            instance.method_that_raises()
```

### Test Naming Convention

- **File**: `test_<module_name>.py`
- **Class**: `Test<ClassName>`
- **Method**: `test_<what_it_tests>`

### Assertion Guidelines

```python
# Equality
assert actual == expected

# Containment
assert item in collection
assert "text" in string

# Exceptions
with pytest.raises(ValueError):
    function_that_raises()

# Approximate (for floats)
assert actual == pytest.approx(expected, rel=0.01)

# Boolean
assert condition is True
assert condition is False

# None
assert value is None
assert value is not None
```

## Best Practices

### 1. ✅ Test Isolation
Each test should be independent and not rely on other tests.

### 2. ✅ Use Fixtures
Reuse setup code with pytest fixtures.

### 3. ✅ Mock External Calls
Never make real HTTP requests or database connections in unit tests.

### 4. ✅ Test Edge Cases
Test empty inputs, null values, boundary conditions.

### 5. ✅ Clear Test Names
Test names should describe what they test.

### 6. ✅ One Assertion Per Test
Each test should verify one specific behavior.

### 7. ✅ Fast Tests
Unit tests should run in milliseconds, not seconds.

### 8. ✅ Descriptive Docstrings
Each test should have a docstring explaining what it tests.

## Common Testing Patterns

### Testing Database Operations

```python
def test_database_operation(db):
    # Arrange
    db.add_item(123, "World")
    
    # Act
    items = db.get_items()
    
    # Assert
    assert len(items) == 1
    assert items[0]['id'] == 123
```

### Testing API Calls

```python
def test_api_call(api, mock_session):
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = {'data': 'value'}
    mock_session.get.return_value = mock_response
    
    # Act
    result = api.get_data()
    
    # Assert
    assert result['data'] == 'value'
    mock_session.get.assert_called_once()
```

### Testing Business Logic

```python
def test_service_logic(service, mock_db, mock_api):
    # Arrange
    mock_api.get_data.return_value = {'value': 10}
    mock_db.save.return_value = True
    
    # Act
    result = service.process()
    
    # Assert
    assert result is True
    mock_api.get_data.assert_called_once()
    mock_db.save.assert_called_once()
```

## Troubleshooting Tests

### Tests Not Found

```bash
# Verify test discovery
pytest --collect-only
```

### Import Errors

```bash
# Run from project root
cd /path/to/universus
pytest
```

### Mock Not Working

```python
# Ensure correct import path
with patch('module_name.ClassName') as mock:
    # Not 'other_module.ClassName'
```

### Fixture Not Found

```python
# Check fixture scope and location
@pytest.fixture  # Add decorator
def my_fixture():
    return value
```

## Test Maintenance

### Updating Tests After Changes

1. **Schema Changes**: Update database test fixtures
2. **API Changes**: Update mock responses in API tests
3. **Business Logic**: Update service test assertions
4. **UI Changes**: Update UI test expectations

### Keeping Tests Fast

- Use in-memory database (`:memory:`)
- Mock all I/O operations
- Avoid `time.sleep()` in tests
- Use smaller test datasets

### Handling Deprecation Warnings

```python
# Suppress specific warnings in tests
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
```

## Summary

The test suite provides comprehensive coverage of all application layers:

- ✅ **88 tests** covering critical functionality
- ✅ **100% coverage** of database, API client
- ✅ **99% coverage** of service layer
- ✅ **98% coverage** of UI layer
- ✅ **Fast execution** (~1 second for all tests)
- ✅ **Isolated tests** with proper mocking
- ✅ **Clear organization** by architectural layer

The tests ensure code quality, prevent regressions, and document expected behavior through executable examples.
