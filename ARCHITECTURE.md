# Architecture Documentation

## Overview

Universus follows a **layered architecture** pattern with clear separation of concerns between UI, business logic, and data access. This modular design improves maintainability, testability, and allows components to be developed and modified independently.

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         CLI Layer (universus.py)         │  ← Click commands & orchestration
├─────────────────────────────────────────┤
│       Presentation Layer (ui.py)         │  ← Rich UI components & formatting
├─────────────────────────────────────────┤
│      Business Logic (service.py)         │  ← Market operations & calculations
├─────────────────────────────────────────┤
│    API Client (api_client.py)            │  ← HTTP requests & rate limiting
│    Database (database.py)                │  ← SQLite operations & queries
└─────────────────────────────────────────┘
```

## Module Responsibilities

### 1. CLI Layer (`universus.py`)
**Purpose**: Command-line interface and application orchestration

**Responsibilities**:
- Define CLI commands using Click framework
- Parse command-line arguments
- Initialize and coordinate other layers
- Setup logging configuration
- Handle resource cleanup

**Dependencies**: All other modules

**Key Components**:
- `cli()` - Main CLI group with configuration
- `cleanup()` - Resource cleanup callback
- Command functions: `datacenters`, `init_tracking`, `update`, `top`, `report`, `list_tracked`

**Design Pattern**: Command pattern with dependency injection via Click context

---

### 2. Presentation Layer (`ui.py`)
**Purpose**: User interface and output formatting

**Responsibilities**:
- Display formatted output using Rich library
- Create tables, progress bars, and status indicators
- Format messages (success, error, warning, info)
- Handle all console output

**Dependencies**: None (pure presentation)

**Key Components**:
- `MarketUI` - Static class with display methods
- Table formatters for different data types
- Progress bar creators
- Message formatting utilities

**Design Pattern**: Static utility class (no state)

---

### 3. Business Logic Layer (`service.py`)
**Purpose**: Core market data operations and business rules

**Responsibilities**:
- Orchestrate database and API operations
- Implement business logic (tracking, updating, reporting)
- Calculate trends and metrics
- Format data for presentation
- Handle operation workflows

**Dependencies**: `database.py`, `api_client.py`

**Key Components**:
- `MarketService` - Main service class
- Data transformation methods
- Trend calculation algorithms
- Time formatting utilities

**Design Pattern**: Service layer pattern with dependency injection

**Key Methods**:
```python
get_datacenters() → List[Dict]
initialize_tracking(world, limit) → Tuple[List, int, int]
update_tracked_items(world) → Tuple[int, int, List]
get_top_items(world, limit) → List[Dict]
get_item_report(world, item_id, days) → List[Dict]
get_all_tracked_items() → Dict[str, List]
calculate_trends(snapshots) → Dict[str, float]
format_time_ago(timestamp) → str
```

---

### 4. Database Layer (`database.py`)
**Purpose**: Data persistence and retrieval

**Responsibilities**:
- Manage SQLite database connection
- Execute SQL queries
- Handle schema creation and migrations
- Implement CRUD operations
- Manage transactions

**Dependencies**: None (only sqlite3 stdlib)

**Key Components**:
- `MarketDatabase` - Database manager class
- Schema initialization
- Query methods for tracked items, snapshots, and sales
- Context manager support

**Design Pattern**: Data Access Object (DAO) pattern

**Database Schema**:
- `tracked_items` - Items being monitored
- `daily_snapshots` - Daily market snapshots
- `sales_history` - Individual sale transactions

---

### 5. API Client Layer (`api_client.py`)
**Purpose**: External API communication

**Responsibilities**:
- Make HTTP requests to Universalis API
- Implement rate limiting
- Handle request/response cycle
- Manage HTTP session
- Error handling for network issues

**Dependencies**: None (only requests library)

**Key Components**:
- `RateLimiter` - Token bucket rate limiter
- `UniversalisAPI` - HTTP client for Universalis
- Request/response handling
- Session management

**Design Pattern**: Client pattern with rate limiting decorator

**API Methods**:
```python
get_datacenters() → list
get_most_recently_updated(world, entries) → Dict
get_market_data(world, item_id) → Dict
get_history(world, item_id, entries) → Dict
```

---

## Data Flow

### Example: Update Command Flow

```
1. CLI Layer (universus.py)
   └─> parse --world argument
   └─> get database and service from context

2. Service Layer (service.py)
   └─> update_tracked_items(world)
       ├─> get tracked items from database
       │
       ├─> For each item:
       │   ├─> API: get_market_data()
       │   ├─> DB: save_snapshot()
       │   ├─> API: get_history()
       │   └─> DB: save_sales()
       │
       └─> return (successful, failed, items)

3. UI Layer (ui.py)
   └─> show_update_results(successful, failed)
```

### Data Flow Diagram

```
User Input (CLI)
    ↓
universus.py (routing)
    ↓
service.py (business logic)
    ↓           ↓
api_client.py   database.py
    ↓           ↓
Universalis     SQLite
API             Database
    ↓           ↓
service.py (aggregation)
    ↓
ui.py (formatting)
    ↓
Console Output
```

---

## Design Principles Applied

### 1. Separation of Concerns (SoC)
- Each module has a single, well-defined responsibility
- UI code doesn't access the database directly
- Business logic is independent of presentation

### 2. Dependency Inversion Principle (DIP)
- CLI depends on abstractions (service layer)
- Service layer depends on interfaces (DB and API)
- High-level modules don't depend on low-level details

### 3. Single Responsibility Principle (SRP)
- `database.py` - Only data persistence
- `api_client.py` - Only API communication
- `service.py` - Only business logic
- `ui.py` - Only presentation

### 4. Don't Repeat Yourself (DRY)
- Common UI patterns centralized in `MarketUI`
- Database queries encapsulated in methods
- Rate limiting logic in single `RateLimiter` class

### 5. Dependency Injection
- Service receives DB and API as constructor parameters
- CLI creates instances and injects via Click context
- Enables easy testing with mock objects

---

## Testing Strategy

### Unit Tests
Each layer can be tested independently:

```python
# Test database layer
def test_add_tracked_item():
    db = MarketDatabase(":memory:")
    db.add_tracked_item(12345, "Behemoth")
    items = db.get_tracked_items("Behemoth")
    assert len(items) == 1

# Test service layer with mocks
def test_initialize_tracking():
    mock_db = Mock(MarketDatabase)
    mock_api = Mock(UniversalisAPI)
    service = MarketService(mock_db, mock_api)
    # ... test logic

# Test UI layer
def test_show_datacenters(capsys):
    MarketUI.show_datacenters([{"name": "Crystal", "region": "NA"}])
    output = capsys.readouterr()
    assert "Crystal" in output.out
```

### Integration Tests
Test layer interactions:

```python
def test_update_flow():
    db = MarketDatabase(":memory:")
    api = UniversalisAPI()
    service = MarketService(db, api)
    
    # Add tracked item
    db.add_tracked_item(12345, "Behemoth")
    
    # Update items
    successful, failed, _ = service.update_tracked_items("Behemoth")
    
    assert successful > 0
```

---

## Benefits of This Architecture

### 1. Maintainability
- Changes to UI don't affect business logic
- Database schema changes isolated to one module
- API changes contained in client layer

### 2. Testability
- Each layer can be tested independently
- Easy to mock dependencies
- Unit tests don't require network or database

### 3. Reusability
- `MarketService` can be used in other interfaces (web, GUI)
- `MarketDatabase` can be reused in other tools
- `UniversalisAPI` client is standalone

### 4. Scalability
- Easy to add new commands without changing existing code
- Can swap SQLite for PostgreSQL by changing only `database.py`
- Can add caching layer without modifying service logic

### 5. Readability
- Clear module boundaries
- Easy to understand each component's purpose
- New developers can contribute to specific layers

---

## File Structure

```
universus/
├── universus.py          # CLI commands & orchestration (182 lines)
├── database.py           # Database operations (217 lines)
├── api_client.py         # API client & rate limiting (123 lines)
├── service.py            # Business logic (177 lines)
├── ui.py                 # UI presentation (213 lines)
├── requirements.txt      # Dependencies
├── README.md             # Usage documentation
├── QUICK_REFERENCE.md    # Command reference
├── IMPLEMENTATION.md     # Technical details
├── LOGGING.md            # Logging documentation
└── ARCHITECTURE.md       # This file
```

**Total**: ~912 lines (down from 670 lines in monolithic version, but with better organization)

---

## Migration Notes

### From Monolithic to Modular

**Before**: Single `universus.py` file with ~670 lines containing all code

**After**: 5 separate modules with clear responsibilities

**Breaking Changes**: None - CLI interface remains identical

**Compatibility**: Existing databases work without migration

---

## Future Enhancements

### 1. Add Caching Layer
```python
# cache.py
class CacheService:
    def get_or_fetch(self, key, fetch_func, ttl=300):
        # Implementation
```

### 2. Add Configuration Module
```python
# config.py
class Config:
    def load_from_file(self, path):
        # Read .universusrc
```

### 3. Add Export Service
```python
# export.py
class ExportService:
    def export_to_csv(self, data, path):
        # CSV export logic
```

### 4. Add Web Interface
```python
# web.py (Flask/FastAPI)
app = FastAPI()

@app.get("/api/top/{world}")
def get_top_items(world: str):
    service = MarketService(db, api)
    return service.get_top_items(world, 10)
```

All can be added without modifying existing modules!

---

## Logging Integration

Each module has its own logger:

```python
# In each file
import logging
logger = logging.getLogger(__name__)

# Results in hierarchical logging:
__main__         # universus.py
database         # database.py
api_client       # api_client.py
service          # service.py
```

This allows fine-grained control over log levels per module.

---

## Error Handling Strategy

### Layered Error Handling

1. **API Layer**: Catches `requests.RequestException`, logs and re-raises
2. **Database Layer**: Catches `sqlite3.Error`, logs and re-raises
3. **Service Layer**: Catches specific exceptions, logs with context
4. **UI Layer**: Displays user-friendly error messages
5. **CLI Layer**: Catches all exceptions, ensures cleanup, exits gracefully

### Example

```python
# api_client.py
try:
    response = self.session.get(url)
    response.raise_for_status()
except requests.RequestException as e:
    logger.error(f"API request failed: {url} - {e}")
    raise  # Re-raise for service layer

# service.py
try:
    market_data = self.api.get_market_data(world, item_id)
except Exception as e:
    logger.debug(f"Failed to update item {item_id}: {e}")
    failed += 1
    continue  # Continue with next item

# universus.py (CLI)
try:
    dcs = service.get_datacenters()
except Exception as e:
    logger.error(f"Failed to fetch datacenters: {e}")
    MarketUI.exit_with_error(str(e))
```

---

## Performance Considerations

### Database
- Indexes on frequently queried columns
- Batch inserts where possible
- Connection reuse via context manager

### API
- Rate limiting prevents throttling
- Session reuse (connection pooling)
- Minimal data transformation

### Memory
- Streaming large result sets (if needed)
- No global state (only in Click context)
- Proper resource cleanup

---

## Summary

The modular architecture provides:
- ✅ Clear separation between UI, logic, and data
- ✅ Independent, testable components
- ✅ Easy to extend and modify
- ✅ Maintainable codebase
- ✅ Production-ready design

Each layer can evolve independently while maintaining a stable interface to other layers.
