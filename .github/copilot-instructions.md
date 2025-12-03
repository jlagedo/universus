# Copilot Instructions for Universus

This document provides guidance for GitHub Copilot when working with the Universus codebase.

## Project Overview

**Universus** is a Python application for tracking Final Fantasy XIV market prices using the Universalis API. It features both CLI and GUI interfaces, following a layered architecture with clean separation of concerns.

### Tech Stack

- **Language**: Python 3.7+
- **GUI Framework**: NiceGUI 1.5.13+
- **CLI Framework**: Click 8.0+
- **Database**: SQLite (built-in)
- **Testing**: pytest 7.0+
- **Terminal UI**: Rich 13.0+
- **Charts**: Plotly, PyEcharts

---

## Python Best Practices

### Code Style

- Follow **PEP 8** style guidelines
- Use **snake_case** for functions and variables
- Use **PascalCase** for classes
- Use **UPPER_SNAKE_CASE** for constants
- Use **_leading_underscore** for private methods/attributes

### Type Hints

Use type hints for function signatures to improve readability and IDE support:

```python
# Good
def get_market_data(world: str, item_id: int, days: int = 30) -> dict:
    """Fetch market data for an item."""
    ...

# Avoid
def get_market_data(world, item_id, days=30):
    ...
```

### Docstrings

Use Google-style docstrings for all public functions and classes:

```python
def calculate_velocity(sales: list[dict], days: int) -> float:
    """Calculate the daily sales velocity for an item.
    
    Args:
        sales: List of sale records with 'quantity' and 'timestamp' keys.
        days: Number of days to calculate velocity over.
    
    Returns:
        The average number of sales per day.
    
    Raises:
        ValueError: If days is less than 1.
    """
    ...
```

### Imports

Organize imports in this order, separated by blank lines:

```python
# 1. Standard library
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 2. Third-party packages
import click
import requests
from nicegui import ui
from rich.console import Console

# 3. Local modules
from database import MarketDatabase
from api_client import UniversalisAPI
from service import MarketService
```

### Error Handling

Use specific exception types and meaningful error messages:

```python
# Good
try:
    response = self.session.get(url, timeout=self.timeout)
    response.raise_for_status()
except requests.Timeout as e:
    logger.error(f"Request timeout for {url}: {e}")
    raise
except requests.HTTPError as e:
    logger.error(f"HTTP error {e.response.status_code} for {url}")
    raise

# Avoid
try:
    response = self.session.get(url)
except Exception:
    pass  # Never silently swallow exceptions
```

### Logging

Use module-specific loggers with appropriate levels:

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debugging info")      # Development
logger.info("Normal operation messages")     # Production
logger.warning("Unexpected but handled")     # Potential issues
logger.error("Errors with context", exc_info=True)  # Failures
```

### Context Managers

Use context managers for resource management:

```python
# Good
with open(file_path, 'r') as f:
    content = f.read()

# For database connections
with self._lock:
    cursor.execute(query, params)
    self.conn.commit()
```

### List Comprehensions

Prefer list comprehensions for simple transformations:

```python
# Good
item_ids = [item['id'] for item in items if item['tradeable']]

# Avoid for complex logic - use regular loops instead
result = []
for item in items:
    if complex_condition(item):
        transformed = complex_transformation(item)
        result.append(transformed)
```

---

## NiceGUI Best Practices

### Component Structure

Organize GUI code into modular components:

```python
# gui/components/my_component.py
from nicegui import ui

class MyComponent:
    """Reusable UI component."""
    
    def __init__(self, on_action: callable, dark_mode: bool = False):
        self.on_action = on_action
        self.dark_mode = dark_mode
        self._build()
    
    def _build(self):
        """Build the component UI."""
        with ui.card().classes('w-full'):
            self.label = ui.label('Component')
            ui.button('Action', on_click=self._handle_action)
    
    async def _handle_action(self):
        """Handle button click."""
        await self.on_action()
```

### Async Operations

**Always** use async methods for long-running operations to keep the GUI responsive:

```python
# Good - GUI stays responsive
async def fetch_data():
    ui.notify('Fetching data...')
    result = await service.get_data_async()
    ui.notify('Done!', type='positive')

# Bad - Freezes the GUI
def fetch_data():
    result = service.get_data()  # Blocks the event loop!
```

### Async Wrapper Pattern

Create async wrappers for synchronous operations:

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor(max_workers=3)

# Synchronous method
def get_data(self, world: str) -> dict:
    """Fetch data synchronously."""
    return self.api.fetch(world)

# Async wrapper for GUI
async def get_data_async(self, world: str) -> dict:
    """Fetch data asynchronously for GUI use."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        _executor,
        self.get_data,
        world
    )
```

### Notifications

Use appropriate notification types for user feedback:

```python
ui.notify('Operation successful', type='positive')  # Green
ui.notify('Please check your input', type='warning')  # Yellow
ui.notify('Error: Connection failed', type='negative')  # Red
ui.notify('Processing...', type='info')  # Blue
```

### CSS Classes

Use Tailwind CSS classes for styling (built into NiceGUI):

```python
# Layout
ui.card().classes('w-full p-4 mb-4')
ui.row().classes('gap-4 items-center justify-between')
ui.column().classes('w-full space-y-2')

# Typography
ui.label('Title').classes('text-2xl font-bold')
ui.label('Subtitle').classes('text-gray-600')

# Colors
ui.label('Success').classes('text-green-600')
ui.label('Warning').classes('text-yellow-600')
ui.label('Error').classes('text-red-600')
```

### Icons

Use the centralized `GameIcons` class for Material Icons:

```python
from gui.utils.icons import GameIcons

# Good - Use centralized icon constants
ui.button('Dashboard', icon=GameIcons.DASHBOARD)
ui.button('Sync', icon=GameIcons.SYNC)
ui.icon(GameIcons.SUCCESS).classes('text-green-500')

# Avoid - Hardcoded icon strings
ui.button('Dashboard', icon='dashboard')  # Don't do this
```

### Theme Support

Always consider dark/light mode in components:

```python
def render(self, dark_mode: bool = False):
    bg_class = 'bg-gray-800' if dark_mode else 'bg-white'
    text_class = 'text-gray-100' if dark_mode else 'text-gray-900'
    
    with ui.card().classes(f'{bg_class} {text_class}'):
        ui.label('Content')
```

### State Management

Use the `AppState` class for centralized state:

```python
# Good - Centralized state
class AppState:
    def __init__(self):
        self.selected_world = None
        self.selected_datacenter = None
        self.current_view = 'dashboard'
    
    def change_world(self, world: str):
        self.selected_world = world

# Usage in views
def render(state: AppState):
    ui.label(f'World: {state.selected_world}')
```

### View Pattern

Follow the established view pattern for new views:

```python
# gui/views/my_view.py
from nicegui import ui
import logging

logger = logging.getLogger(__name__)

def render(state, service, dark_mode: bool = False):
    """Render the view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is enabled
    """
    with ui.card().classes('w-full'):
        ui.label('My View').classes('text-2xl font-bold')
        
        # Return inputs/containers for event handlers
        input_field = ui.input('Parameter')
        results = ui.column()
        
        return input_field, results

async def fetch_data(service, params, results_container, set_status):
    """Fetch and display data."""
    try:
        set_status('Fetching...')
        data = await service.get_data_async(params)
        
        with results_container:
            for item in data:
                ui.label(item['name'])
        
        set_status('Ready')
    except Exception as e:
        logger.error(f'Error fetching data: {e}')
        ui.notify(f'Error: {e}', type='negative')
        set_status('Error')
```

---

## Architecture Guidelines

### Layered Architecture

Respect the layer boundaries:

```
┌─────────────────────────────────────────┐
│  CLI (universus.py) + GUI (gui/)        │  ← User interfaces
├─────────────────────────────────────────┤
│  Presentation (ui.py)                   │  ← Terminal formatting
├─────────────────────────────────────────┤
│  Business Logic (service.py)            │  ← Market operations
├─────────────────────────────────────────┤
│  API Client (api_client.py)             │  ← HTTP + rate limiting
│  Database (database.py)                 │  ← SQLite persistence
└─────────────────────────────────────────┘
```

**Rules:**
- Never bypass layers (CLI → Service → Database, not CLI → Database)
- UI layer is pure presentation (no business logic)
- Service layer orchestrates API and Database

### Dependency Injection

Always inject dependencies rather than creating them:

```python
# Good - Dependencies injected
class MarketService:
    def __init__(self, database: MarketDatabase, api_client: UniversalisAPI):
        self.db = database
        self.api = api_client

# Bad - Hard-coded dependencies
class MarketService:
    def __init__(self):
        self.db = MarketDatabase()  # Can't mock for testing!
```

### Thread Safety

Protect database writes with locks:

```python
# Good - Thread-safe write
def save_data(self, data: dict):
    with self._lock:
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO table VALUES (?)", (data,))
        self.conn.commit()

# Bad - Race condition possible
def save_data(self, data: dict):
    cursor = self.conn.cursor()
    cursor.execute("INSERT INTO table VALUES (?)", (data,))
    self.conn.commit()  # Another thread might interfere!
```

### Rate Limiting

**Never** bypass rate limiting. The API requires respect:

```python
# The rate limiter is already configured in api_client.py
# Always use the API client methods, never raw requests

# Good
data = await self.api.get_market_data_async(world, item_id)

# Bad - Bypasses rate limiter
response = requests.get(f"{base_url}/{world}/{item_id}")
```

---

## Testing Best Practices

### Test Structure

Follow the Arrange-Act-Assert pattern:

```python
def test_get_top_items(mock_api, db):
    # Arrange
    service = MarketService(db, mock_api)
    mock_api.get_market_data.return_value = {'items': [{'id': 1}]}
    
    # Act
    result = service.get_top_items('Behemoth', limit=10)
    
    # Assert
    assert len(result) <= 10
    mock_api.get_market_data.assert_called_once()
```

### Fixtures

Use pytest fixtures for setup:

```python
@pytest.fixture
def db():
    """Create in-memory database for testing."""
    database = MarketDatabase(":memory:")
    yield database
    database.close()

@pytest.fixture
def mock_api():
    """Create mock API client."""
    api = Mock()
    api.get_data.return_value = {'status': 'ok'}
    return api
```

### Async Tests

Mark async tests appropriately:

```python
@pytest.mark.asyncio
async def test_async_operation(service):
    result = await service.get_data_async()
    assert result is not None
```

### Test Coverage

Aim for high coverage but focus on meaningful tests:

```bash
# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest test_database.py::TestDatabase::test_insert -v
```

---

## File Placement Guide

When adding new features, place code in the appropriate module:

| Feature Type | Location |
|--------------|----------|
| CLI command | `universus.py` |
| Business logic | `service.py` |
| Database operations | `database.py` |
| API communication | `api_client.py` |
| Terminal formatting | `ui.py` |
| GUI view | `gui/views/` |
| GUI component | `gui/components/` |
| GUI utilities | `gui/utils/` |
| Configuration | `config.py` |

---

## Common Patterns

### Adding a CLI Command

```python
@cli.command()
@click.option('--world', required=True, help='World name')
@click.option('--limit', default=10, help='Number of items')
@pass_context
def new_command(ctx, world: str, limit: int):
    """Command description for --help."""
    db = ctx.obj['database']
    service = ctx.obj['service']
    
    try:
        result = service.new_operation(world, limit)
        MarketUI.show_result(result)
    except Exception as e:
        logger.error(f"Command failed: {e}")
        MarketUI.exit_with_error(str(e))
```

### Adding a GUI View

```python
# 1. Create gui/views/new_view.py
# 2. Import in gui/views/__init__.py
# 3. Add to sidebar navigation in gui/components/sidebar.py
# 4. Register in gui/app.py show_view() method
```

### Adding a Database Table

```python
# In database.py _init_database()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS new_table (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
""")

# Add index for common queries
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_new_table_name
    ON new_table(name)
""")
```

---

## Quick Reference

### Running the Application

```bash
# GUI
python run_gui.py

# CLI
python universus.py --help
python universus.py top --world Behemoth

# Tests
pytest
python run_tests.py --coverage --verbose
```

### Common Commands

```bash
# Initialize tracking
python universus.py init-tracking --world Behemoth --limit 50

# Update data (run daily)
python universus.py update --world Behemoth

# View reports
python universus.py report --world Behemoth --item-id 5594 --days 30
```

### Database Inspection

```bash
sqlite3 market_data.db
.tables
.schema tracked_items
SELECT * FROM tracked_items LIMIT 10;
```

---

## Summary Checklist

When writing code for this project:

- [ ] Follow PEP 8 style guidelines
- [ ] Add type hints to function signatures
- [ ] Write docstrings for public functions
- [ ] Use appropriate logging levels
- [ ] Handle exceptions with specific types
- [ ] Respect the layered architecture
- [ ] Inject dependencies (don't hard-code them)
- [ ] Use async wrappers for GUI operations
- [ ] Protect database writes with locks
- [ ] Never bypass rate limiting
- [ ] Use `GameIcons` class for icons
- [ ] Support dark/light themes
- [ ] Write tests for new functionality
- [ ] Keep documentation updated

---

*Last Updated: December 2025*
