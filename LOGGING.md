# Logging Documentation

## Overview

Universus now includes comprehensive logging throughout the application to provide visibility into operations, debugging information, and error tracking.

## Logging Levels

### INFO Level (Default)
INFO level is always enabled and shows:
- Application startup and configuration
- Command execution start
- Major operations (database initialization, API client creation)
- Operation results and summaries
- Resource cleanup

**Example INFO output:**
```
2025-12-01 01:01:44 - __main__ - INFO - Starting Universus CLI (verbose: False)
2025-12-01 01:01:44 - __main__ - INFO - Universalis API client initialized (timeout: 10s)
2025-12-01 01:01:44 - __main__ - INFO - Executing 'top' command for Behemoth (limit: 3)
2025-12-01 01:01:44 - __main__ - INFO - Cleanup complete
```

### DEBUG Level (--verbose flag)
DEBUG level provides detailed operational information:
- Database path and configuration
- Rate limiter initialization and wait times
- All API requests with URLs and parameters
- HTTP response status codes and sizes
- Database operations (inserts, queries, updates)
- Item-by-item processing details
- Duplicate detection in sales data
- Connection lifecycle events

**Enable with:**
```bash
python universus.py --verbose <command>
```

**Example DEBUG output:**
```
2025-12-01 01:01:27 - __main__ - DEBUG - Database path: market_data.db
2025-12-01 01:01:27 - __main__ - DEBUG - Rate limiter initialized: 2.0 req/sec (interval: 0.500s)
2025-12-01 01:01:27 - __main__ - DEBUG - Fetching tracked items for world: Behemoth
2025-12-01 01:01:27 - __main__ - DEBUG - Found 9 tracked items
2025-12-01 01:01:27 - __main__ - DEBUG - Making API request: https://universalis.app/api/Behemoth/32230
2025-12-01 01:01:28 - __main__ - DEBUG - Response status: 200
2025-12-01 01:01:28 - __main__ - DEBUG - Response received: 1376 bytes
2025-12-01 01:01:28 - __main__ - DEBUG - Saving snapshot for item 32230 on Behemoth
2025-12-01 01:01:28 - __main__ - DEBUG - Snapshot saved: velocity=0.71428573, price=8998.6
2025-12-01 01:01:28 - __main__ - DEBUG - Rate limiting: sleeping for 0.249s
```

## Logging Categories

### Application Lifecycle
- CLI initialization with configuration
- Resource setup (database, API client)
- Resource cleanup and connection closure

### Database Operations
- Database file path and initialization
- Table and index creation
- Item tracking additions
- Snapshot saves with key metrics
- Sales history insertion with duplicate detection
- Query operations with result counts
- Connection close events

### API Operations
- Rate limiter initialization with intervals
- Rate limiting delays (when enforced)
- HTTP request URLs and parameters
- Response status codes
- Response payload sizes
- API method calls (datacenters, market data, history)
- Session lifecycle events

### Command Execution
- Command name and parameters logged at start
- Processing progress for batch operations
- Success/failure counts
- Error details with stack traces (on ERROR level)

## Log Format

```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

**Components:**
- **Timestamp**: ISO 8601 format with date and time
- **Logger Name**: `__main__` for application code, `urllib3.connectionpool` for HTTP details
- **Level**: INFO, DEBUG, ERROR, etc.
- **Message**: Human-readable description

## Use Cases

### 1. Debugging API Issues
Enable verbose logging to see exact API requests and responses:
```bash
python universus.py --verbose update --world Behemoth
```

Look for:
- Request URLs and parameters
- Response status codes (should be 200)
- Response sizes (unusually small might indicate missing data)
- Rate limiting delays

### 2. Monitoring Database Performance
Check database operations:
- Table initialization time
- Query execution and result counts
- Duplicate detection in sales data
- Connection lifecycle

### 3. Tracking Update Progress
During long update operations:
- Item-by-item processing logs
- Success/failure counts
- Error messages for specific items

### 4. Troubleshooting Rate Limiting
Verify rate limiting behavior:
- Rate limiter initialization parameters
- Actual sleep times applied
- Request timing patterns

### 5. Production Monitoring
Without verbose flag for cleaner logs:
- Command executions
- Major operation completions
- Error summaries
- Resource cleanup confirmation

## Error Logging

All errors are logged with ERROR level, including:
- API request failures with full URL and exception details
- Database operation errors
- Command execution failures with stack traces (when verbose)

**Example:**
```
2025-12-01 01:01:27 - __main__ - ERROR - API request failed: https://universalis.app/api/... - Connection timeout
2025-12-01 01:01:27 - __main__ - ERROR - Init tracking failed: ...
```

## Best Practices

### For Development
Always use `--verbose` for debugging:
```bash
python universus.py --verbose init-tracking --world Behemoth --limit 10
```

### For Production/Scheduled Tasks
Use INFO level (default) and redirect to log file:
```bash
python universus.py update --world Behemoth >> /var/log/universus.log 2>&1
```

### For Troubleshooting Specific Issues
Combine verbose with output filtering:
```bash
# See only rate limiting
python universus.py --verbose update --world Behemoth 2>&1 | grep "Rate limiting"

# See only API requests
python universus.py --verbose update --world Behemoth 2>&1 | grep "Making API request"

# See only errors
python universus.py update --world Behemoth 2>&1 | grep ERROR
```

## Log Rotation Recommendation

For scheduled daily updates, use logrotate or similar:

```bash
# /etc/logrotate.d/universus
/var/log/universus.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
}
```

## Performance Impact

- **INFO level**: Negligible impact, suitable for production
- **DEBUG level**: Minimal impact, safe for all operations
- HTTP connection pool logs from urllib3 included automatically at DEBUG level

## Third-Party Library Logs

When verbose mode is enabled, you'll also see:
- **urllib3**: HTTP connection pool details, request/response details
- **requests**: HTTP session management (if enabled in requests library)

These provide additional insight into network operations and connection reuse.
