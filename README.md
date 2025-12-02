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

## CLI Usage

### 1. List all datacenters

```bash
python universus.py datacenters
```

Use a custom config:

```bash
python universus.py --config-file ./config.toml datacenters
```

### 2. Initialize tracking for a world

Track the top 50 most actively traded items on Behemoth:

```bash
python universus.py init-tracking --world Behemoth --limit 50
```

This command:
- Fetches the most recently updated items (high activity indicator)
- Analyzes sale velocities for each item
- Creates a local database to track these items
- Respects API rate limits (20 requests/second with burst support)

### 3. Update tracked items (run daily)

```bash
python universus.py update --world Behemoth
```

This fetches current market data and sales history for all tracked items. **Schedule this command to run daily** via:

**macOS/Linux (cron)**:
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/universus && python universus.py update --world Behemoth
```

**Windows (Task Scheduler)**:
```powershell
# Create a daily task
schtasks /create /tn "FFXIV Market Update" /tr "python C:\path\to\universus.py update --world Behemoth" /sc daily /st 02:00
```

### 4. View top items by volume

```bash
python universus.py top --world Behemoth --limit 10
```

Shows the top 10 items with highest daily sales velocity.

### 5. View detailed item report

```bash
python universus.py report --world Behemoth --item-id 5594 --days 30
```

Shows 30-day historical data including:
- Daily sales velocity trends
- Price trends (average, min, max)
- Number of active listings
- Percentage changes over time period

### 6. List all tracked items

```bash
python universus.py list-tracked
```

### 7. Sync item names database

Download and sync the complete item name database from FFXIV Teamcraft:

```bash
python universus.py sync-items
```

This command:
- Fetches ~47,000 item names from the FFXIV Teamcraft data dump
- Stores them in the local database for reference
- Replaces existing data if run again (to get updates)
- Useful for looking up item names by ID in future features

**Note**: This is a one-time setup command, but can be run periodically to get updated item names from game patches.

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
- **Algorithm**: Token bucket with burst support
- **Impact**: Updating 50 items takes ~2.5 seconds

## Database Structure

The local SQLite database (`market_data.db`) contains:

- **tracked_items**: Items being monitored
- **daily_snapshots**: Daily market data snapshots
- **sales_history**: Individual sale transactions

## Example Workflow

### Using the GUI
1. Run `python run_gui.py`
2. Select your datacenter and world
3. Click "Initialize Tracking" to start monitoring items
4. Use "Update Market Data" daily to refresh data
5. View reports and statistics in the dashboard

### Using the CLI
```bash
# 1. Initialize tracking (one-time setup)
python universus.py init-tracking --world Behemoth --limit 50

# 2. Update data (run daily)
python universus.py update --world Behemoth

# 3. View top items
python universus.py top --world Behemoth

# 4. Analyze specific item
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

**Test Coverage**: 98 tests, 67% overall coverage

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

This application uses the [Universalis API](https://docs.universalis.app/) with respectful rate limiting (2 requests/second). 

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
