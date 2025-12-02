# LLM Instructions for Working with Universus

This document provides guidance for AI assistants working with the Universus codebase.

## Project Overview

Universus is a Python application for tracking Final Fantasy XIV market prices with both CLI and GUI interfaces. The codebase follows a **layered architecture** pattern with clear separation of concerns.

## Quick Context

- **Language**: Python 3.7+
- **Architecture**: Layered (CLI/GUI → UI → Service → API/Database)
- **Testing**: pytest (98 tests, 67% coverage)
- **Database**: SQLite with thread-safety
- **GUI**: NiceGUI with async operations
- **API**: Universalis API with rate limiting (2 req/sec)

## File Structure & Responsibilities

### Entry Points
- `universus.py` - CLI application (Click framework)
- `gui.py` - Web GUI (NiceGUI framework)
- `run_gui.py` - GUI launcher
- `run_tests.py` - Test runner

### Core Layers
- `ui.py` - Terminal formatting (Rich library)
- `service.py` - Business logic & orchestration
- `database.py` - SQLite operations (thread-safe)
- `api_client.py` - HTTP client with rate limiting
- `config.py` - TOML configuration loader

### Testing
- `test_*.py` - Unit tests for each module
- `pytest.ini` - Test configuration
- All tests use in-memory database (`:memory:`)
- Mocks used for external dependencies

### Configuration
- `config.toml` - Application settings
- `requirements.txt` - Python dependencies

## Architectural Patterns

### 1. Layered Architecture

```
CLI/GUI → UI → Service → API/Database
```

**Rules**:
- Never bypass layers (e.g., CLI shouldn't call Database directly)
- Each layer depends only on the layer below
- Service layer orchestrates API and Database
- UI layer is pure presentation (no business logic)

### 2. Dependency Injection

Components receive dependencies via constructor:

```python
# Good
service = MarketService(database, api_client)

# Bad
class MarketService:
    def __init__(self):
        self.db = MarketDatabase()  # Hard-coded dependency
```

### 3. Sync + Async Pattern

**CLI**: Uses synchronous methods
```python
result = service.initialize_tracking(world, limit)
```

**GUI**: Uses async wrappers
```python
result = await service.initialize_tracking_async(world, limit)
```

**Implementation**:
```python
# Sync method (original)
def operation(self, params):
    # Blocking implementation
    pass

# Async wrapper for GUI
async def operation_async(self, params):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        self.operation,
        params
    )
```

### 4. Thread Safety (Database)

**SQLite Configuration**:
```python
sqlite3.connect(
    path,
    check_same_thread=False,  # Allow cross-thread access
    timeout=30.0              # Wait for lock
)
```

**Write Protection**:
```python
with self._lock:  # threading.Lock()
    cursor.execute(...)
    self.conn.commit()
```

**Read Operations**: No lock needed (SQLite handles it)

## Code Conventions

### Naming
- **Functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

### Imports
```python
# Standard library
import os
import sqlite3

# Third-party
import click
import requests

# Local
from database import MarketDatabase
from api_client import UniversalisAPI
```

### Logging
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Operation started")
logger.debug("Detailed info")
logger.error("Error occurred", exc_info=True)
```

### Error Handling
```python
try:
    result = operation()
except SpecificException as e:
    logger.error(f"Operation failed: {e}")
    raise  # Re-raise for upper layers
```

## Common Tasks

### Adding a New CLI Command

1. **Define command in `universus.py`**:
```python
@cli.command()
@click.option('--param', help='Description')
@pass_context
def new_command(ctx, param):
    """Command description."""
    db = ctx.obj['database']
    service = ctx.obj['service']
    
    try:
        result = service.new_operation(param)
        MarketUI.show_success(f"Done: {result}")
    except Exception as e:
        logger.error(f"Command failed: {e}")
        MarketUI.exit_with_error(str(e))
```

2. **Add business logic to `service.py`**:
```python
def new_operation(self, param):
    """Business logic for operation."""
    # Implementation
    return result
```

3. **Add database method if needed** (`database.py`):
```python
def save_new_data(self, data):
    """Save data to database."""
    with self._lock:  # If writing
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO table ...", data)
        self.conn.commit()
```

4. **Add UI display method** (`ui.py`):
```python
@staticmethod
def show_new_data(data):
    """Display data in terminal."""
    table = Table(title="New Data")
    # Build table
    console.print(table)
```

### Adding a GUI View

1. **Add view method to `gui.py`**:
```python
def render_new_view(self):
    """Render new view."""
    with ui.card():
        ui.label('New Feature')
        
        async def on_action():
            try:
                result = await service.operation_async(params)
                ui.notify('Success!', type='positive')
            except Exception as e:
                ui.notify(f'Error: {e}', type='negative')
        
        ui.button('Action', on_click=on_action)
```

2. **Add to navigation** (if needed):
```python
def render_sidebar(self):
    with ui.column():
        ui.button('New View', on_click=self.render_new_view)
```

### Adding Tests

1. **Create test file** (`test_new_module.py`):
```python
import pytest
from unittest.mock import Mock
from new_module import NewClass

class TestNewClass:
    @pytest.fixture
    def instance(self):
        return NewClass()
    
    def test_basic_functionality(self, instance):
        result = instance.method()
        assert result is not None
```

2. **Run tests**:
```bash
pytest test_new_module.py -v
```

### Adding Database Table

1. **Add to schema in `database.py`**:
```python
def _init_database(self):
    cursor = self.conn.cursor()
    
    # Existing tables...
    
    # New table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS new_table (
            id INTEGER PRIMARY KEY,
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_new_table_created
        ON new_table(created_at)
    """)
```

2. **Add CRUD methods**:
```python
def add_to_new_table(self, data):
    with self._lock:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO new_table (data) VALUES (?)",
            (data,)
        )
        self.conn.commit()

def get_from_new_table(self, id):
    cursor = self.conn.cursor()
    cursor.execute("SELECT * FROM new_table WHERE id = ?", (id,))
    return cursor.fetchone()
```

## Important Constraints

### Rate Limiting
**NEVER** remove or bypass rate limiting. The API requires respect:
```python
# In api_client.py
self.rate_limiter = RateLimiter(requests_per_second=2.0)
```

### Thread Safety
**ALWAYS** use locks for database writes:
```python
# Good
with self._lock:
    cursor.execute("INSERT ...")
    self.conn.commit()

# Bad
cursor.execute("INSERT ...")  # Race condition!
self.conn.commit()
```

### Async Operations (GUI)
**ALWAYS** use async wrappers for long operations in GUI:
```python
# Good - GUI stays responsive
result = await service.operation_async()

# Bad - GUI freezes
result = service.operation()  # Blocks event loop!
```

### Layer Violations
**NEVER** bypass architectural layers:
```python
# Good
service.get_data()  # Service calls database

# Bad
cli_command() -> database.query()  # Skips service layer!
```

## Testing Guidelines

### Fixtures
```python
@pytest.fixture
def db():
    """In-memory database for testing."""
    database = MarketDatabase(":memory:")
    yield database
    database.close()

@pytest.fixture
def mock_api():
    """Mock API client."""
    api = Mock()
    api.get_data.return_value = {'key': 'value'}
    return api
```

### Async Tests
```python
@pytest.mark.asyncio
async def test_async_operation():
    result = await service.operation_async()
    assert result is not None
```

### Mocking
```python
def test_with_mock(mock_api):
    service = MarketService(db, mock_api)
    service.operation()
    
    # Verify mock was called
    mock_api.get_data.assert_called_once()
```

## Common Pitfalls

### 1. Forgetting Await in GUI
```python
# Wrong - GUI will freeze
async def handler():
    result = service.long_operation()  # Missing await!

# Right
async def handler():
    result = await service.long_operation_async()
```

### 2. Database Lock Forgetting
```python
# Wrong - Not thread-safe
def save_data(self, data):
    cursor = self.conn.cursor()
    cursor.execute("INSERT ...")  # No lock!
    self.conn.commit()

# Right
def save_data(self, data):
    with self._lock:
        cursor = self.conn.cursor()
        cursor.execute("INSERT ...")
        self.conn.commit()
```

### 3. Layer Bypass
```python
# Wrong - CLI accessing database directly
@cli.command()
def command():
    items = database.get_tracked_items()  # Bypass service!

# Right
@cli.command()
def command():
    items = service.get_tracked_items()  # Through service
```

### 4. Hard-coded Dependencies
```python
# Wrong
class Service:
    def __init__(self):
        self.db = MarketDatabase()  # Can't mock!

# Right
class Service:
    def __init__(self, database, api_client):
        self.db = database  # Injected, can mock
        self.api = api_client
```

### 5. Missing Rate Limiting
```python
# Wrong - Bypasses rate limiter
response = requests.get(url)

# Right - Uses rate-limited client
response = self.api.get_data()
```

## Debugging Tips

### Enable Verbose Logging
```bash
python universus.py --verbose command
```

### Check Thread Issues
```python
import threading
print(f"Thread: {threading.current_thread().name}")
print(f"Active threads: {threading.active_count()}")
```

### Database Inspection
```bash
sqlite3 market_data.db
.tables
.schema table_name
SELECT * FROM table_name LIMIT 10;
```

### Test Specific File
```bash
pytest test_database.py -v
pytest test_database.py::TestClass::test_method -v
```

## Quick Reference

### Running Application
```bash
# CLI
python universus.py --help
python universus.py top --world Behemoth

# GUI
python run_gui.py

# Tests
pytest
python run_tests.py --coverage
```

### Common Patterns

**Service Method**:
```python
def operation(self, params):
    data = self.api.fetch(params)
    processed = self.process(data)
    self.db.save(processed)
    return processed
```

**GUI Handler**:
```python
async def on_button_click():
    try:
        result = await service.operation_async(params)
        ui.notify('Success', type='positive')
    except Exception as e:
        ui.notify(f'Error: {e}', type='negative')
```

**Database Write**:
```python
def save_data(self, data):
    with self._lock:
        cursor = self.conn.cursor()
        cursor.execute("INSERT ...", data)
        self.conn.commit()
```

**Test Case**:
```python
def test_operation(mock_api):
    service = MarketService(db, mock_api)
    mock_api.fetch.return_value = {'data': 'value'}
    
    result = service.operation()
    
    assert result == expected
    mock_api.fetch.assert_called_once()
```

## When Making Changes

1. **Identify the layer** - Which file should this change go in?
2. **Follow patterns** - Look at existing similar code
3. **Write tests first** - Test-driven development
4. **Check thread safety** - Database writes need locks
5. **Add async wrapper** - If operation is for GUI
6. **Update documentation** - Keep PROJECT.md current
7. **Run all tests** - `pytest` before committing

## Resources

- **PROJECT.md** - Comprehensive project documentation
- **README.md** - User-facing guide
- `pytest.ini` - Test configuration
- `config.toml` - Application settings
- Test files - Examples of usage patterns

## Summary

When working with this codebase:

✅ Respect the layered architecture
✅ Use dependency injection
✅ Add async wrappers for GUI operations
✅ Protect database writes with locks
✅ Never bypass rate limiting
✅ Write tests for new functionality
✅ Follow existing patterns
✅ Keep documentation updated

The codebase is well-structured and testable. Follow the established patterns and you'll have a smooth experience!

---

**Last Updated**: December 1, 2025
**For**: AI Assistants and LLMs
**Status**: Production Ready
