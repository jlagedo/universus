# Universus

A Python application for tracking Final Fantasy XIV market prices using the [Universalis API](https://universalis.app/). Build a local historical database to monitor the most traded items and track price trends over time.

## Features

- 📊 Track top selling items by volume on any world
- 💾 Local SQLite database for historical data storage
- 📈 Daily snapshots of market data and price trends
- 🔄 Automated data fetching with rate limiting
- 🖥️ **CLI** with beautiful terminal UI (Rich formatting)
- 🌐 **Web GUI** with responsive interface (NiceGUI)
- ⚡ Respects API rate limits (20 requests/second, 80% of API capacity)
- 🔧 Centralized configuration via `config.toml`

## Quick Start

### Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

### Running the Application

**Web GUI** (Recommended for beginners):
```bash
python run_gui.py
```
Then open http://localhost:8080 in your browser.

**CLI** (For automation and scripting):
```bash
python universus.py --help
```

### Configuration

(Optional) Create a config file:

```toml
# config.toml
[database]
default_path = "market_data.db"
cache_max_age_hours = 24

[api]
base_url = "https://universalis.app/api"
timeout = 10
rate_limit = 20.0          # 80% of API limit (25 req/s)
burst_size = 40            # Token bucket burst capacity
max_items_per_query = 200
default_history_entries = 100
batch_size = 100           # Items per batch for price updates
executor_workers = 3       # Thread pool workers for async ops

[teamcraft]
items_url = "https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json"
timeout = 30
max_retries = 3

[cli]
default_tracking_limit = 50
default_top_limit = 10
default_report_days = 30

[logging]
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
date_format = "%Y-%m-%d %H:%M:%S"

[gui]
theme = "dark"             # 'light' or 'dark'
port = 8080
```

## CLI Usage

### 1. List all datacenters

```bash
python universus.py datacenters
```

Use a custom config:

```bash
python universus.py --config-file ./config.toml datacenters
```

### 2. Import static data (item names and marketable items)

Download item names and marketable item IDs:

```bash
python universus.py import-static-data
# or use short alias:
python universus.py isd
```

This command:
- Fetches ~47,000 item names from FFXIV Teamcraft
- Fetches ~30,000 marketable item IDs from Universalis API
- Stores them in the local database
- Any existing data will be replaced

### 3. Manage tracked worlds

Add worlds to track for price updates:

```bash
# List tracked worlds
python universus.py tracked-worlds list

# Add a world
python universus.py tracked-worlds add --world Behemoth

# Remove a world
python universus.py tracked-worlds remove --world Behemoth

# Clear all
python universus.py tracked-worlds clear
```

### 4. Update current prices (run periodically)

```bash
python universus.py update-current-prices
```

This fetches current aggregated prices for all marketable items on tracked worlds. **Schedule this command to run daily** via:

**macOS/Linux (cron)**:
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/universus && python universus.py update-current-prices
```

**Windows (Task Scheduler)**:
```powershell
# Create a daily task
schtasks /create /tn "FFXIV Market Update" /tr "python C:\path\to\universus.py update-current-prices" /sc daily /st 02:00
```

### 5. View top items by volume

```bash
python universus.py top --world Behemoth --limit 10
```

Shows the top 10 items with highest daily sales velocity.

### 6. View detailed item report

```bash
python universus.py report --world Behemoth --item-id 5594 --days 30
```

Shows 30-day historical data including:
- Daily sales velocity trends
- Price trends (average, min, max)
- Number of active listings
- Percentage changes over time period

### 7. Refresh cache

Manually refresh cached datacenter and world data:

```bash
python universus.py refresh-cache
```

## Configuration

The application reads defaults from `config.toml`. You can override per-run using CLI flags, or point to another config with `--config-file`.

- `database.default_path`: SQLite file location
- `api.*`: Base URL, timeouts, rate limits, query limits
- `teamcraft.*`: Items dump URL and timeout
- `cli.*`: Command defaults for limits and days
- `logging.*`: Log formatting

## API Rate Limiting

This tool implements respectful rate limiting based on official Universalis API limits:

- **API Limit**: 25 requests/second sustained (50 req/s burst)
- **Our Rate**: 20 requests/second (80% of limit for safety)
- **Algorithm**: Token bucket with burst support (40 tokens)
- **Retry Logic**: Exponential backoff for transient errors
- **Impact**: Updating current prices is batched at 100 items per request

## Database Structure

The local SQLite database (`market_data.db`) contains:

- **tracked_items**: Items being monitored per world
- **daily_snapshots**: Daily market data snapshots
- **sales_history**: Individual sale transactions
- **items**: Item names database (~47k items from FFXIV Teamcraft)
- **marketable_items**: List of all marketable item IDs (~30k from Universalis)
- **tracked_worlds**: Configuration of worlds to track for price updates
- **current_prices**: Current aggregated prices per tracked world (NQ/HQ at world, DC, region levels)
- **cached_datacenters**: Cached datacenter data from API (refreshed daily)
- **cached_worlds**: Cached world data from API (refreshed daily)

## Example Workflow

### Using the GUI
1. Run `python run_gui.py`
2. Select your datacenter and world from the header
3. Go to Settings > Import Static Data to download item names and marketable items
4. Go to Settings > Tracked Worlds to add worlds to track
5. Run `python universus.py update-current-prices` via CLI to fetch prices
6. View dashboard for market analysis and top items by HQ velocity
7. Use Reports views for detailed item analysis and sell volume charts

### Using the CLI
```bash
# 1. Import static data (one-time or periodic for updates)
python universus.py import-static-data

# 2. Add worlds to track
python universus.py tracked-worlds add --world Behemoth

# 3. Update prices (run daily)
python universus.py update-current-prices

# 4. View top items
python universus.py top --world Behemoth

# 5. Analyze specific item
python universus.py report --world Behemoth --item-id 36112 --days 30
```

## Documentation

- **[README.md](README.md)** (this file) - User guide and quick start
- **[PROJECT.md](PROJECT.md)** - Comprehensive project documentation (architecture, testing, development)
- **[LLM_INSTRUCTIONS.md](LLM_INSTRUCTIONS.md)** - Instructions for AI assistants working with the code

## For Developers

### Testing

Run the comprehensive test suite:
```bash
pytest
# or
python run_tests.py --coverage --verbose
```

**Test Coverage**: 162 tests across 7 test modules, 2445+ lines of test code

### Architecture

Universus follows a layered architecture with clear separation of concerns:
- **CLI/GUI Layer** - User interfaces
- **Presentation Layer** - Terminal formatting
- **Business Logic** - Market operations
- **Data Access** - Database and API communication

See **[PROJECT.md](PROJECT.md)** for detailed technical documentation.

## Requirements

- **Python 3.7+**
- Dependencies listed in `requirements.txt`

All dependencies install automatically with:
```bash
pip install -r requirements.txt
```

## About the API

This application uses the [Universalis API](https://docs.universalis.app/) with respectful rate limiting (20 requests/second, 80% of API limit). 

## Database File

By default, the database is stored as `market_data.db` in the current directory. You can specify a custom path:

```bash
python universus.py --db-path /path/to/custom.db <command>
```

Or define in `config.toml` and pass `--config-file`:

```bash
python universus.py --config-file ./config.toml top --world Behemoth
```

## Tips

- Run updates during off-peak hours to minimize impact
- Start with 30-50 items to keep update times reasonable
- Use the `report` command to identify trending items
- The database grows ~1MB per week per 50 items tracked

## License

MIT

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.
