# Universus CLI - Quick Reference

## Commands

### Initialize Tracking
```bash
python universus.py init-tracking --world Behemoth --limit 50
```
- Discovers and tracks top volume items on a world
- Uses recently updated items as proxy for high volume
- Fetches sale velocities for ranking
- Creates local SQLite database

### Update Market Data
```bash
python universus.py update --world Behemoth
```
- Updates all tracked items for a world
- Fetches current market prices and listings
- Saves sales history
- Run daily for best results

### View Top Items
```bash
python universus.py top --world Behemoth --limit 10
```
- Shows items with highest sales velocity
- Displays from latest snapshot data

### Detailed Item Report
```bash
python universus.py report --world Behemoth --item-id 5594 --days 30
```
- Historical price and volume trends
- Shows percentage changes
- Daily snapshots for time period

### List Tracked Items
```bash
python universus.py list-tracked
```
- Shows all worlds being tracked
- Item counts per world
- Last update times

### List Datacenters
```bash
python universus.py datacenters
```
- Shows all FFXIV datacenters
- Regions and world counts

## Database Location

Default: `./market_data.db`

Custom path:
```bash
python universus.py --db-path /custom/path/data.db <command>
```

## Rate Limiting

- **2 requests per second** (500ms between requests)
- Based on API source code analysis
- Updating 50 items takes ~25 seconds

## Automation

### Linux/macOS (cron)
```bash
# Edit crontab
crontab -e

# Add line for daily update at 2 AM
0 2 * * * cd /path/to/universus && python universus.py update --world Behemoth
```

### Windows (Task Scheduler)
```powershell
schtasks /create /tn "FFXIV Market Update" /tr "python C:\path\to\universus.py update --world Behemoth" /sc daily /st 02:00
```

## Database Schema

### tracked_items
- item_id (PK)
- world
- first_tracked
- last_updated

### daily_snapshots
- item_id, world, snapshot_date (UNIQUE)
- average_price, min_price, max_price
- sale_velocity, nq_sale_velocity, hq_sale_velocity
- total_listings
- last_upload_time

### sales_history
- item_id, world
- sale_time
- price_per_unit, quantity
- is_hq, buyer_name
- recorded_at

## Tips

1. **Start Small**: Begin with 20-30 items to test
2. **Schedule Updates**: Daily updates provide best trend data
3. **Monitor Multiple Worlds**: Use separate databases or track multiple worlds
4. **Check Item IDs**: Use Universalis website to find item IDs
5. **Backup Database**: The `.db` file contains all your historical data

## Troubleshooting

**No items found:**
- Verify world name spelling (case-sensitive)
- Check if world has recent market activity

**Rate limit errors:**
- Tool automatically handles rate limiting
- Avoid running multiple instances simultaneously

**Database locked:**
- Close other connections to the database
- Only one process should write at a time

**Old data:**
- Run `update` command to refresh
- Check `last_updated` timestamp

## API Information

- **Base URL**: https://universalis.app/api
- **Documentation**: https://docs.universalis.app
- **Rate Limit**: Implemented as 2 req/sec (conservative)
- **User-Agent**: Universus-CLI/1.0
