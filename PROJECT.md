# Universus - Project Documentation

## Overview

Universus is a Python application for tracking Final Fantasy XIV market prices using the [Universalis API](https://universalis.app/). It provides both a **CLI** and a **GUI** interface for monitoring market trends and building historical databases.

## Project Structure

```
universus/
├── Core Application
│   ├── universus.py          # CLI commands & orchestration
│   ├── run_gui.py            # GUI entry point
│   ├── run_tests.py          # Test runner
│   └── validate_gui.py       # GUI validation script
│
├── Layered Architecture
│   ├── ui.py                 # Presentation layer (Rich terminal UI)
│   ├── service.py            # Business logic layer
│   ├── database.py           # Data access layer (SQLite)
│   └── api_client.py         # API communication & rate limiting
│
├── GUI (Refactored Modular Architecture)
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── app.py            # Main application coordinator
│   │   ├── state.py          # Application state management
│   │   ├── components/       # Reusable UI components
│   │   │   ├── __init__.py
│   │   │   ├── header.py     # Header with selectors
│   │   │   ├── sidebar.py    # Navigation sidebar
│   │   │   ├── footer.py     # Status footer
│   │   │   └── cards.py      # Stat & progress cards
│   │   ├── views/            # Page controllers
│   │   │   ├── __init__.py
│   │   │   ├── dashboard.py  # Dashboard view
│   │   │   ├── datacenters.py # Datacenters list
│   │   │   ├── top_items.py  # Top items view
│   │   │   ├── tracked_items.py # Tracked items
│   │   │   ├── tracking.py   # Init & update tracking
│   │   │   ├── reports.py    # Item reports & charts
│   │   │   └── settings.py   # Sync & settings
│   │   └── utils/            # GUI utilities
│   │       ├── __init__.py
│   │       ├── formatters.py # Gil, velocity formatting
│   │       └── theme.py      # Theme management
│
├── Configuration
│   ├── config.py             # Configuration loader
│   └── config.toml           # Settings file
│
├── Tests (174 tests, 2560+ lines)
│   ├── test_cli.py           # CLI commands
│   ├── test_gui.py           # GUI components
│   ├── test_ui.py            # Terminal UI
│   ├── test_service.py       # Business logic
│   ├── test_database.py      # Database operations
│   ├── test_api_client.py    # API client
│   └── test_items_sync.py    # Item synchronization
│
└── Documentation
    ├── README.md             # User guide
    ├── PROJECT.md            # This file
    ├── GUI_REFACTORING.md    # GUI refactoring details
    └── LLM_INSTRUCTIONS.md   # AI assistant guide
```

## Architecture

### Layered Design Pattern

```
┌─────────────────────────────────────────┐
│  CLI (universus.py) + GUI (gui.py)      │  ← User interfaces
├─────────────────────────────────────────┤
│  Presentation (ui.py)                    │  ← Terminal formatting
├─────────────────────────────────────────┤
│  Business Logic (service.py)             │  ← Market operations
├─────────────────────────────────────────┤
│  API Client (api_client.py)              │  ← HTTP + rate limiting
│  Database (database.py)                  │  ← SQLite persistence
│  Configuration (config.py)               │  ← TOML settings
└─────────────────────────────────────────┘
```

### Module Responsibilities

**CLI Layer** (`universus.py`)
- Click command definitions
- Argument parsing
- Component initialization
- Resource cleanup

**GUI Layer** (`gui/`)
- Modular NiceGUI web interface
- Component-based architecture
- State management via `AppState`
- Async operations with ThreadPoolExecutor
- Responsive UI during long operations
- Real-time progress feedback
- Theme management (dark/light mode)

**Presentation Layer** (`ui.py`)
- Rich terminal formatting
- Tables, progress bars
- Status messages

**Business Logic** (`service.py`)
- Market data operations
- Trend calculations
- Data transformations
- Orchestrates API + Database

**Database Layer** (`database.py`)
- SQLite operations
- Thread-safe with locking
- Schema management
- CRUD operations

**API Client** (`api_client.py`)
- HTTP communication
- Rate limiting (2 req/sec)
- Async operations for GUI
- Error handling & retries

**Configuration** (`config.py`)
- TOML file loading
- Default values
- Settings validation

## Database Schema

### tracked_items
Stores items being monitored.
```sql
CREATE TABLE tracked_items (
    item_id INTEGER,
    world TEXT,
    first_tracked DATETIME,
    last_updated DATETIME,
    PRIMARY KEY (item_id, world)
)
```

### daily_snapshots
Historical market data snapshots.
```sql
CREATE TABLE daily_snapshots (
    item_id INTEGER,
    world TEXT,
    snapshot_date DATE,
    average_price REAL,
    min_price INTEGER,
    max_price INTEGER,
    sale_velocity REAL,
    nq_sale_velocity REAL,
    hq_sale_velocity REAL,
    total_listings INTEGER,
    last_upload_time DATETIME,
    UNIQUE(item_id, world, snapshot_date)
)
```

### sales_history
Individual sale transactions.
```sql
CREATE TABLE sales_history (
    item_id INTEGER,
    world TEXT,
    sale_time DATETIME,
    price_per_unit INTEGER,
    quantity INTEGER,
    is_hq BOOLEAN,
    buyer_name TEXT,
    recorded_at DATETIME
)
```

### items
Item name database (from FFXIV Teamcraft).
```sql
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
)
```

### marketable_items
List of all marketable item IDs from Universalis.
```sql
CREATE TABLE marketable_items (
    item_id INTEGER PRIMARY KEY
)
```

### tracked_worlds
Configuration of worlds to track for current prices.
```sql
CREATE TABLE tracked_worlds (
    id INTEGER,
    name TEXT,
    PRIMARY KEY (id)
)
```

### current_prices
Current aggregated prices per world.
```sql
CREATE TABLE current_prices (
    item_id INTEGER,
    world_id INTEGER,
    min_price INTEGER,
    max_price INTEGER,
    average_price REAL,
    last_update DATETIME,
    PRIMARY KEY (item_id, world_id)
)
```

### datacenters_cache
Cached datacenter data from API.
```sql
CREATE TABLE datacenters_cache (
    name TEXT PRIMARY KEY,
    region TEXT,
    worlds TEXT,
    cached_at DATETIME
)
```

### worlds_cache
Cached world data from API.
```sql
CREATE TABLE worlds_cache (
    id INTEGER PRIMARY KEY,
    name TEXT,
    cached_at DATETIME
)
```

## Key Features

### 1. Rate Limiting
- 20 requests/second (80% of 25 req/s API limit)
- Token bucket algorithm with burst support (40 tokens)
- Respects official Universalis API limits (25 req/s sustained, 50 req/s burst)
- Provides safety margin while maximizing performance

### 2. Async Operations (GUI)
- ThreadPoolExecutor with 3 workers
- Non-blocking API calls
- Responsive UI during long operations
- Proper error handling

### 3. Thread Safety (Database)
- `check_same_thread=False` for cross-thread access
- `threading.Lock()` protects write operations
- 30-second timeout on locks
- Safe concurrent access

### 4. Configuration
- Centralized `config.toml`
- Environment-specific overrides
- Sensible defaults
- All settings documented

### 5. Logging
- Hierarchical logger structure
- Module-specific loggers
- DEBUG mode available (`--verbose`)
- File and console output

## Design Principles

**Separation of Concerns**
- Each module has single responsibility
- Clear boundaries between layers
- UI independent of business logic

**Dependency Inversion**
- High-level modules depend on abstractions
- Service layer receives DB and API via constructor
- Easy to mock for testing

**Don't Repeat Yourself**
- Common patterns centralized
- Reusable components
- Shared utilities

**Dependency Injection**
- Components receive dependencies as parameters
- Enables testing with mocks
- Configured via Click context (CLI) or initialization (GUI)

## Testing Strategy

### Test Coverage
- **Total Tests**: 174
- **Test Files**: 7 modules
- **Lines of Test Code**: 2560+
- **Framework**: pytest 7.0+

### Test Structure
```
test_api_client.py   35+ tests - API client & rate limiting
test_database.py     31+ tests - Database operations
test_service.py      20+ tests - Business logic
test_ui.py           28+ tests - Terminal UI formatting
test_cli.py          24+ tests - CLI commands
test_gui.py          26+ tests - GUI components & state
test_items_sync.py   10+ tests - Item synchronization
```

### Testing Patterns

**Fixtures for Setup**
```python
@pytest.fixture
def db():
    database = MarketDatabase(":memory:")
    yield database
    database.close()
```

**Mocking External Dependencies**
```python
@pytest.fixture
def mock_api():
    return Mock()
```

**In-Memory Database**
```python
db = MarketDatabase(":memory:")  # No file I/O
```

### Running Tests
```bash
# All tests
pytest

# With coverage
pytest --cov=. --cov-report=html

# Specific test file
pytest test_database.py

# Using test runner
python run_tests.py --coverage --verbose
```

## CLI Commands

### Initialize Tracking
```bash
python universus.py init-tracking --world Behemoth --limit 50
```
Discovers and tracks top volume items.

### Update Market Data
```bash
python universus.py update --world Behemoth
```
Updates all tracked items (run daily).

### View Top Items
```bash
python universus.py top --world Behemoth --limit 10
```
Shows highest sales velocity items.

### Detailed Report
```bash
python universus.py report --world Behemoth --item-id 5594 --days 30
```
Historical analysis for specific item.

### List Tracked Items
```bash
python universus.py list-tracked
```
Shows all tracked items by world.

### Sync Item Names
```bash
python universus.py sync-items
```
Downloads ~47,000 item names from FFXIV Teamcraft.

### List Datacenters
```bash
python universus.py datacenters
```
Shows all FFXIV datacenters and worlds.

### Sync Marketable Items
```bash
python universus.py sync-marketable
```
Downloads all marketable item IDs from Universalis API.

### Manage Tracked Worlds
```bash
# List tracked worlds
python universus.py tracked-worlds list

# Add a world
python universus.py tracked-worlds add --world Behemoth

# Remove a world
python universus.py tracked-worlds remove --world-id 99

# Clear all tracked worlds
python universus.py tracked-worlds clear
```

### Refresh Cache
```bash
python universus.py refresh-cache
```
Manually refresh cached datacenter and world data.

### Update Current Prices
```bash
python universus.py update-current-prices
```
Updates current aggregated prices for all marketable items on tracked worlds.

## GUI Interface

### Running the GUI
```bash
python run_gui.py
```
Starts web interface on http://localhost:8080

### Features
- All CLI commands available
- Real-time progress feedback
- Responsive during operations
- Datacenter/world selection
- Dashboard with statistics
- Interactive data tables
- Dark/light theme toggle
- Modular component-based UI
- Multiple views (dashboard, tracking, reports, settings)

### Technical Implementation
- Built with NiceGUI
- Modular architecture with separation of concerns
- Component-based UI (header, sidebar, footer, cards)
- State management via `AppState` class
- Theme management via `ThemeManager` class
- Async operations using ThreadPoolExecutor
- Thread-safe database access
- Automatic error handling
- Clean shutdown handling

## Configuration

### config.toml
```toml
[database]
default_path = "market_data.db"

[api]
base_url = "https://universalis.app/api"
timeout = 10
rate_limit = 2.0
max_items_per_query = 200
default_history_entries = 100

[teamcraft]
items_url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json"
timeout = 30

[cli]
default_tracking_limit = 50
default_top_limit = 10
default_report_days = 30

[logging]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"
```

## Automation

### Linux/macOS (cron)
```bash
# Edit crontab
crontab -e

# Add daily update at 2 AM
0 2 * * * cd /path/to/universus && python universus.py update --world Behemoth
```

### Windows (Task Scheduler)
```powershell
schtasks /create /tn "FFXIV Market Update" /tr "python C:\path\to\universus.py update --world Behemoth" /sc daily /st 02:00
```

## Dependencies

### Runtime
- **click** - CLI framework
- **requests** - HTTP client
- **rich** - Terminal formatting
- **nicegui** - Web GUI framework
- **tomli** - TOML parsing (Python < 3.11)

### Testing
- **pytest** - Test framework
- **pytest-cov** - Coverage reporting
- **pytest-mock** - Mocking utilities

### Installation
```bash
pip install -r requirements.txt
```

## Performance Metrics

- **Init tracking (50 items)**: ~2.5 seconds (rate limited at 20 req/s)
- **Daily update (50 items)**: ~2.5 seconds (rate limited at 20 req/s)
- **Database growth**: ~1MB per week per 50 items
- **Query speed**: <10ms for most operations
- **GUI response time**: <100ms (async operations)

## API Integration

**Base URL**: https://universalis.app/api

**Rate Limit**: 2 requests/second (conservative)

**Endpoints Used**:
- `GET /api/data-centers` - List datacenters
- `GET /v2/worlds` - List all worlds
- `GET /extra/stats/most-recently-updated` - Active items
- `GET /{world}/{item_id}` - Current market data
- `GET /history/{world}/{item_id}` - Sales history

**Documentation**: https://docs.universalis.app/

## Error Handling

### Layered Strategy
1. **API Layer**: Catches `requests.RequestException`, logs and re-raises
2. **Database Layer**: Catches `sqlite3.Error`, logs and re-raises
3. **Service Layer**: Catches specific exceptions, logs with context
4. **UI Layer**: Displays user-friendly messages
5. **CLI/GUI Layer**: Ensures cleanup, exits gracefully

### Example Flow
```python
# API client
try:
    response = self.session.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API request failed: {url} - {e}")
    raise

# Service layer
try:
    data = self.api.get_market_data(world, item_id)
except Exception as e:
    logger.debug(f"Failed to update item {item_id}: {e}")
    failed += 1
    continue

# CLI layer
try:
    items = service.get_top_items(world, limit)
except Exception as e:
    logger.error(f"Failed to fetch top items: {e}")
    MarketUI.exit_with_error(str(e))
```

## Best Practices

### Adding New Features

1. **Determine Layer**
   - API communication? → `api_client.py`
   - Business logic? → `service.py`
   - Display formatting? → `ui.py`
   - Database operations? → `database.py`

2. **Add Tests First**
   ```python
   def test_new_feature():
       # Arrange
       # Act
       # Assert
   ```

3. **Implement Synchronous Version**
   ```python
   def new_operation(self, params):
       # Implementation
   ```

4. **Add Async Wrapper (if needed for GUI)**
   ```python
   async def new_operation_async(self, params):
       loop = asyncio.get_event_loop()
       return await loop.run_in_executor(
           _executor,
           self.new_operation,
           params
       )
   ```

5. **Update CLI Command**
   ```python
   @cli.command()
   def new_command():
       service.new_operation()
   ```

6. **Update GUI View (if applicable)**
   ```python
   async def render_new_view(self):
       result = await service.new_operation_async()
   ```

### Code Style

- **Type Hints**: Use where beneficial
- **Docstrings**: For public methods
- **Logging**: Use module-specific loggers
- **Error Messages**: User-friendly, informative
- **Comments**: Explain "why", not "what"

### Git Workflow

```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and test
pytest

# Commit with descriptive message
git commit -m "Add feature: description"

# Push and create PR
git push origin feature/new-feature
```

## Troubleshooting

### Common Issues

**Database Locked**
- Only one process should write at a time
- Check for other running instances
- Solution: Close other connections

**API Rate Limit**
- Tool handles rate limiting automatically
- Avoid multiple simultaneous instances
- Check logs for retry attempts

**Thread Safety Errors**
- Database has `check_same_thread=False`
- Write operations use locks
- Read operations are safe

**GUI Freezing**
- Ensure using async methods (`*_async`)
- Check `await` is used properly
- Verify ThreadPoolExecutor is initialized

**Import Errors**
- Install all dependencies: `pip install -r requirements.txt`
- Check Python version: 3.7+
- Verify virtual environment activation

## Future Enhancements

### Potential Features
- [ ] Multi-world comparison
- [ ] Price alert notifications
- [ ] Export to CSV/JSON
- [ ] Profit margin calculator
- [ ] WebSocket support for real-time updates
- [ ] Caching layer for API responses
- [ ] User preference persistence
- [ ] Dark/light theme toggle

### Technical Improvements
- [ ] Async HTTP client (`aiohttp`)
- [ ] Async database operations (`aiosqlite`)
- [ ] Dynamic thread pool sizing
- [ ] Operation cancellation
- [ ] Streaming results
- [ ] Progressive loading

## Resources

- [Universalis API Docs](https://docs.universalis.app/)
- [FFXIV Teamcraft](https://ffxivteamcraft.com/)
- [Click Documentation](https://click.palletsprojects.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [NiceGUI Documentation](https://nicegui.io/)
- [pytest Documentation](https://docs.pytest.org/)

## License

MIT

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Write tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

---

**Last Updated**: December 2, 2025
**Status**: Production Ready
**Version**: 1.0.0
