# Copilot Instructions for Universus

This document provides guidance for GitHub Copilot when working with the Universus codebase.

## Project Overview

**Universus** is a Python application for tracking Final Fantasy XIV market prices using the Universalis API. It features both CLI and GUI interfaces, following a layered architecture with clean separation of concerns.

### Tech Stack

- **Language**: Python 3.7+
- **GUI Framework**: NiceGUI 1.5.13+ (web-based with Quasar components)
- **CLI Framework**: Click 8.0+
- **Database**: SQLite (built-in, thread-safe with locks)
- **Testing**: pytest 7.0+ (162+ tests, 2445+ lines)
- **Terminal UI**: Rich 13.0+ (formatted tables, colors, progress bars)
- **Charts**: Plotly, PyEcharts
- **Async Runtime**: Python asyncio with ThreadPoolExecutor for sync-to-async wrapping

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

Organize GUI code into modular components using the design system:

```python
# gui/components/my_component.py
from nicegui import ui
from ..utils.design_system import heading_classes, PROPS

class MyComponent:
    """Reusable UI component."""
    
    def __init__(self, on_action: callable):
        self.on_action = on_action
        self._build()
    
    def _build(self):
        """Build the component UI."""
        with ui.card().classes('w-full p-4'):
            ui.label('Component').classes(heading_classes(3))
            ui.button('Action', on_click=self._handle_action).props(PROPS.BUTTON_FLAT)
    
    async def _handle_action(self):
        """Handle button click."""
        await self.on_action()
```

### Card Components

Use the centralized card components from `gui/components/cards.py`:

```python
from gui.components.cards import (
    stat_card,       # Metric display with optional HQ/NQ accent
    warning_card,    # Yellow warning messages
    error_card,      # Red error messages
    info_card,       # Blue informational messages
    success_card,    # Green success messages
    filter_card,     # Filter/form container
    section_card,    # Generic section container
)

# Stat card with accent color
stat_card('Daily Velocity', '12.5/day', accent='hq')  # Teal accent
stat_card('Min Price', '50,000 gil', accent='nq')     # Gold accent
stat_card('Listings', '42', accent=None)              # No accent

# Warning/error/info cards
warning_card('No data available', 'Run price update first.')
error_card('Connection failed', 'Check your internet connection.')
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

### CSS Classes and Design System

The GUI uses a **unified design system** (`gui/utils/design_system.py`) for consistent styling:

```python
from gui.utils.design_system import (
    heading_classes, metric_classes, card_classes,
    COLORS, TYPOGRAPHY, SPACING, PROPS, TABLE_SLOTS
)
from gui.components.cards import stat_card, warning_card, filter_card

# Use heading helper for consistent typography
ui.label('Page Title').classes(heading_classes(2))  # h2 style
ui.label('Section').classes(heading_classes(3))    # h3 style

# Use card components
stat_card('Velocity', '12.5/day', accent='hq')  # HQ teal accent
stat_card('Price', '50,000 gil', accent='nq')   # NQ gold accent
warning_card('No data', 'Please select a world first.')

# Use PROPS for Quasar component consistency
ui.select(...).props(PROPS.SELECT_OUTLINED)
ui.button(...).props(PROPS.BUTTON_FLAT)

# Use TABLE_SLOTS for reusable table formatting
table.add_slot('body-cell-price', TABLE_SLOTS.PRICE_CELL)
table.add_slot('header-cell-velocity', TABLE_SLOTS.header_tooltip('velocity', 'Sales per day'))
```

**Color Palette** (WCAG AA Compliant):
- Background: `#1E1E1E` (main), `#2A2A2A` (cards)
- HQ Accent: `#00C8A2` (teal) - High Quality items
- NQ Accent: `#FFB400` (gold) - Normal Quality items  
- Interactive: `#4DA6FF` (blue) - Links, buttons
- Text: `#FFFFFF` (primary), `#B0B0B0` (secondary)
- Border: `#3A3A3A`

**Typography Rules**:
- Headings: 600-700 weight, ≥18px
- Metrics/values: 500-600 weight, ≥16px
- Labels: 400 weight, ≥14px

**Layout with Tailwind**:
```python
# Layout
ui.card().classes('w-full p-4 mb-4')
ui.row().classes('gap-4 items-center justify-between')
ui.column().classes('w-full space-y-2')
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

### Dark Mode Only

The application uses **dark mode only**. The `dark_mode` parameter is deprecated but kept for backward compatibility:

```python
# Views receive dark_mode but can ignore it
def render(state, service, dark_mode: bool = False):
    """Render the view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    """
    # Use design system - no conditional styling needed
    ui.label('Title').classes(heading_classes(2))
    
    # Use card components with consistent styling
    with ui.card().classes(card_classes()):
        ui.label('Content').classes('text-white')
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
"""My view description.

Uses the unified design system for consistent styling.
"""

from nicegui import ui
import logging
from ..utils.design_system import heading_classes, PROPS
from ..components.cards import warning_card

logger = logging.getLogger(__name__)

def render(state, service, dark_mode: bool = False):
    """Render the view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    """
    ui.label('My View').classes(heading_classes(2))
    ui.label('View description').classes('text-gray-400 mb-6')
    
    if not state.selected_world:
        warning_card('No world selected', 'Please select a world first.')
        return None, None
    
    with ui.card().classes('w-full p-4'):
        input_field = ui.input('Parameter').classes('w-full')
        results = ui.column().classes('w-full mt-4')
    
    return input_field, results

async def fetch_data(service, params, results_container, set_status):
    """Fetch and display data."""
    try:
        set_status('Fetching...')
        data = await service.get_data_async(params)
        
        with results_container:
            for item in data:
                ui.label(item['name']).classes('text-white')
        
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

## Critical Integration Patterns

### Async/Sync Bridge in GUI and Service

The service layer provides **both** sync and async methods:
- Sync methods (e.g., `get_market_data()`) for CLI and database operations
- Async methods (e.g., `get_market_data_async()`) for GUI responsiveness

```python
# In service.py - ALWAYS provide both patterns
def get_data(self, world: str) -> dict:
    """Synchronous method."""
    return self.api.fetch(world)

async def get_data_async(self, world: str) -> dict:
    """Async wrapper using ThreadPoolExecutor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, self.get_data, world)
```

**In GUI**: Always use the `_async()` version to prevent UI freezing.
**In CLI**: Use sync methods directly (blocking is acceptable for CLI).

### Configuration Access Pattern

Configuration is loaded once at startup and accessed globally:

```python
from config import get_config

config = get_config()
db_path = config.get('database', 'default_path', 'market_data.db')
timeout = config.get('api', 'timeout', 10)
```

Never create new config instances. Use the singleton pattern via `get_config()`.

### State Management in GUI

Application state is centralized in `AppState`:

```python
# gui/state.py - single source of truth for UI state
class AppState:
    selected_world: str
    selected_datacenter: str
    tracked_world_ids: set
    
# gui/app.py passes state to all views
def render(state, service, dark_mode=False):
    # Access and modify shared state
    ui.label(f'World: {state.selected_world}')
```

**Rules:**
- All UI state mutations go through AppState
- Views are functions that receive state, not classes
- Views call service methods for data operations

### Database Thread Safety

Database writes MUST be protected with locks:

```python
# In database.py
def save_price(self, item_id: int, world: str, price: int):
    with self._lock:  # Required for thread safety
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO current_prices VALUES (?)", (item_id, world, price))
        self.conn.commit()
```

The lock is initialized in `MarketDatabase.__init__()`:
```python
self._lock = threading.Lock()
```

### Rate Limiter Architecture

The RateLimiter class in `api_client.py` uses token bucket algorithm:

```python
class RateLimiter:
    """Token bucket: 20 req/s sustained, 40 req/s burst."""
    
    def __init__(self, requests_per_second=20.0, burst_size=40):
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.tokens = float(burst_size)  # Start full
    
    def wait(self):
        """Block if necessary to respect limit."""
        # Refill tokens, then consume one
```

Never call API methods without going through the rate limiter. All API requests in `UniversalisAPI` methods call `self.rate_limiter.wait()`.

### Shared Executor Pattern

A single `ThreadPoolExecutor` is shared across the application to avoid resource waste:

```python
# In executor.py - singleton pattern
from concurrent.futures import ThreadPoolExecutor
from config import get_config

config = get_config()
_max_workers = config.get('api', 'executor_workers', 3)
executor = ThreadPoolExecutor(max_workers=_max_workers)

# Use throughout the codebase
from executor import executor

async def get_data_async(self) -> dict:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, self.get_data)
```

**Why:** Prevents creating multiple thread pools, which wastes resources. The executor is automatically cleaned up on application exit via `atexit` registration.

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
|--------------|-----------|
| CLI command | `universus.py` |
| Business logic | `service.py` |
| Database operations | `database.py` |
| API communication | `api_client.py` |
| Terminal formatting | `ui.py` |
| GUI view | `gui/views/` |
| GUI component | `gui/components/` |
| GUI utilities | `gui/utils/` |
| Design tokens/helpers | `gui/utils/design_system.py` |
| Theme/CSS | `gui/utils/theme.py` |
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

## Virtual Environment

**IMPORTANT**: This project uses a Python virtual environment. Always use the venv when executing Python commands.

### Python Executable Path

**Windows:**
```cmd
# Use this path for all Python commands:
e:\dev\universus\.venv\Scripts\python.exe

# Examples:
e:\dev\universus\.venv\Scripts\python.exe universus.py --help
e:\dev\universus\.venv\Scripts\python.exe -m pytest -v
e:\dev\universus\.venv\Scripts\python.exe run_gui.py
```

**macOS/Linux:**
```bash
/Users/jlagedo/Developer/python/universus/.venv/bin/python
```

### Why Use the venv?

- Ensures all project dependencies are available
- Avoids conflicts with system Python
- Uses the correct Python version (3.7+, currently 3.14+)
- Required for pytest, NiceGUI, and other packages

---

## Quick Reference

### Running the Application

**Windows:**
```cmd
REM GUI
e:\dev\universus\.venv\Scripts\python.exe run_gui.py

REM CLI
e:\dev\universus\.venv\Scripts\python.exe universus.py --help
e:\dev\universus\.venv\Scripts\python.exe universus.py top --world Behemoth

REM Tests
e:\dev\universus\.venv\Scripts\python.exe -m pytest
e:\dev\universus\.venv\Scripts\python.exe run_tests.py --coverage --verbose
```

**macOS/Linux:**
```bash
# GUI
/Users/jlagedo/Developer/python/universus/.venv/bin/python run_gui.py

# CLI
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py --help
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py top --world Behemoth

# Tests
/Users/jlagedo/Developer/python/universus/.venv/bin/python -m pytest
/Users/jlagedo/Developer/python/universus/.venv/bin/python run_tests.py --coverage --verbose
```

### Common Commands

```bash
# Import static data (items + marketable items)
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py isd

# Add a world to track
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py tw a --world Behemoth

# Update current prices (run daily)
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py ucp

# View reports
/Users/jlagedo/Developer/python/universus/.venv/bin/python universus.py report --world Behemoth --item-id 5594 --days 30
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
- [ ] Use design system helpers (`heading_classes`, `PROPS`, etc.)
- [ ] Use card components (`warning_card`, `stat_card`, etc.)
- [ ] Follow WCAG AA contrast guidelines
- [ ] Write tests for new functionality
- [ ] Keep documentation updated

---

*Last Updated: December 2025*
