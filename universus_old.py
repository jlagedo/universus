#!/usr/bin/env python3
"""
Universus - A CLI for Final Fantasy XIV market prices using the Universalis API.
"""

import sys
import time
import sqlite3
import logging
from datetime import datetime, timedelta
import requests
import click
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn


# Constants
MAX_ITEMS_PER_QUERY = 200
DEFAULT_HISTORY_ENTRIES = 100
DEFAULT_TIMEOUT = 10
DEFAULT_RATE_LIMIT = 2.0  # requests per second

console = Console()
logger = logging.getLogger(__name__)


class MarketDatabase:
    """Local SQLite database for tracking market data."""
    
    def __init__(self, db_path: str = "market_data.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        cursor = self.conn.cursor()
        logger.debug("Creating database tables if not exist")
        
        # Table for tracking items we're monitoring
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                world TEXT NOT NULL,
                first_tracked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(item_id, world)
            )
        """)
        
        # Table for daily snapshots
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                world TEXT NOT NULL,
                snapshot_date DATE NOT NULL,
                average_price REAL,
                min_price INTEGER,
                max_price INTEGER,
                sale_velocity REAL,
                nq_sale_velocity REAL,
                hq_sale_velocity REAL,
                total_listings INTEGER,
                last_upload_time INTEGER,
                FOREIGN KEY (item_id) REFERENCES tracked_items(item_id),
                UNIQUE(item_id, world, snapshot_date)
            )
        """)
        
        # Table for individual sales
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                world TEXT NOT NULL,
                sale_time INTEGER NOT NULL,
                price_per_unit INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                is_hq BOOLEAN NOT NULL,
                buyer_name TEXT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (item_id) REFERENCES tracked_items(item_id)
            )
        """)
        
        # Indexes for efficient queries
        logger.debug("Creating database indexes")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_date ON daily_snapshots(snapshot_date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sales_time ON sales_history(sale_time)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracked_world ON tracked_items(world)")
        
        self.conn.commit()
        logger.info("Database initialization complete")
    
    def add_tracked_item(self, item_id: int, world: str):
        """Add an item to tracking list."""
        logger.debug(f"Adding item {item_id} to tracking list for {world}")
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO tracked_items (item_id, world)
            VALUES (?, ?)
        """, (item_id, world))
        self.conn.commit()
        logger.debug(f"Item {item_id} added successfully")
    
    def get_tracked_items(self, world: Optional[str] = None) -> List[Dict]:
        """Get all tracked items, optionally filtered by world."""
        logger.debug(f"Fetching tracked items for world: {world or 'all'}")
        cursor = self.conn.cursor()
        if world:
            cursor.execute(
                "SELECT * FROM tracked_items WHERE world = ? ORDER BY last_updated DESC",
                (world,)
            )
        else:
            cursor.execute("SELECT * FROM tracked_items ORDER BY last_updated DESC")
        results = [dict(row) for row in cursor.fetchall()]
        logger.debug(f"Found {len(results)} tracked items")
        return results
    
    def save_snapshot(self, item_id: int, world: str, data: Dict):
        """Save a daily snapshot of market data."""
        logger.debug(f"Saving snapshot for item {item_id} on {world}")
        cursor = self.conn.cursor()
        today = datetime.now().date()
        
        cursor.execute("""
            INSERT OR REPLACE INTO daily_snapshots (
                item_id, world, snapshot_date, average_price, min_price, max_price,
                sale_velocity, nq_sale_velocity, hq_sale_velocity, total_listings,
                last_upload_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            item_id, world, today,
            data.get('averagePrice'),
            data.get('minPrice'),
            data.get('maxPrice'),
            data.get('regularSaleVelocity'),
            data.get('nqSaleVelocity'),
            data.get('hqSaleVelocity'),
            len(data.get('listings', [])),
            data.get('lastUploadTime')
        ))
        
        # Update last_updated timestamp
        cursor.execute("""
            UPDATE tracked_items SET last_updated = CURRENT_TIMESTAMP
            WHERE item_id = ? AND world = ?
        """, (item_id, world))
        
        self.conn.commit()
        logger.debug(f"Snapshot saved: velocity={data.get('regularSaleVelocity')}, price={data.get('averagePrice')}")
    
    def save_sales(self, item_id: int, world: str, entries: List[Dict]):
        """Save sales history entries."""
        logger.debug(f"Saving {len(entries)} sales entries for item {item_id} on {world}")
        cursor = self.conn.cursor()
        new_entries = 0
        
        for entry in entries:
            # Check if we already have this sale
            cursor.execute("""
                SELECT id FROM sales_history
                WHERE item_id = ? AND world = ? AND sale_time = ? AND price_per_unit = ?
            """, (item_id, world, entry.get('timestamp'), entry.get('pricePerUnit')))
            
            if cursor.fetchone() is None:
                cursor.execute("""
                    INSERT INTO sales_history (
                        item_id, world, sale_time, price_per_unit, quantity, is_hq, buyer_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id, world,
                    entry.get('timestamp'),
                    entry.get('pricePerUnit'),
                    entry.get('quantity'),
                    entry.get('hq', False),
                    entry.get('buyerName')
                ))
                new_entries += 1
        
        self.conn.commit()
        logger.debug(f"Saved {new_entries} new sales entries (skipped {len(entries) - new_entries} duplicates)")
    
    def get_snapshots(self, item_id: int, world: str, days: int = 30) -> List[Dict]:
        """Get historical snapshots for an item."""
        cursor = self.conn.cursor()
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        cursor.execute("""
            SELECT * FROM daily_snapshots
            WHERE item_id = ? AND world = ? AND snapshot_date >= ?
            ORDER BY snapshot_date DESC
        """, (item_id, world, cutoff_date))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_top_volume_items(self, world: str, limit: int = 10) -> List[Dict]:
        """Get items with highest sale velocity from latest snapshots."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT ds.item_id, ds.world, ds.sale_velocity, ds.average_price,
                   ds.snapshot_date, ti.last_updated
            FROM daily_snapshots ds
            JOIN tracked_items ti ON ds.item_id = ti.item_id AND ds.world = ti.world
            WHERE ds.world = ? AND ds.snapshot_date = (
                SELECT MAX(snapshot_date) FROM daily_snapshots ds2
                WHERE ds2.item_id = ds.item_id AND ds2.world = ds.world
            )
            ORDER BY ds.sale_velocity DESC
            LIMIT ?
        """, (world, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
        return False
    
    def close(self):
        """Close database connection."""
        if self.conn:
            logger.debug(f"Closing database connection to {self.db_path}")
            self.conn.close()
            self.conn = None
            logger.debug("Database connection closed")


class RateLimiter:
    """Rate limiter to respect API limits."""
    
    def __init__(self, requests_per_second: float = DEFAULT_RATE_LIMIT):
        """Initialize rate limiter.
        
        Conservative limit of 2 requests/second based on API implementation
        showing 100ms delays between requests.
        """
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        logger.debug(f"Rate limiter initialized: {requests_per_second} req/sec (interval: {self.min_interval:.3f}s)")
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_interval:
            sleep_time = self.min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()


class UniversalisAPI:
    """Client for interacting with the Universalis API."""
    
    BASE_URL = "https://universalis.app/api"
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, rate_limiter: Optional[RateLimiter] = None):
        self.timeout = timeout
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Universus-CLI/1.0"
        })
        logger.info(f"Universalis API client initialized (timeout: {timeout}s)")
    
    def close(self):
        """Close the session."""
        if self.session:
            logger.debug("Closing API session")
            self.session.close()
            logger.debug("API session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Any:
        """Make a rate-limited request to the API."""
        logger.debug(f"Making API request: {url}" + (f" with params: {params}" if params else ""))
        self.rate_limiter.wait()
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response received: {len(str(data))} bytes")
            return data
        except requests.RequestException as e:
            logger.error(f"API request failed: {url} - {e}")
            console.print(f"[bold red]API Error:[/bold red] {e}")
            raise
    
    def get_datacenters(self) -> list:
        """Fetch all available datacenters from the API."""
        logger.info("Fetching datacenters list")
        result = self._make_request(f"{self.BASE_URL}/data-centers")
        logger.info(f"Retrieved {len(result)} datacenters")
        return result
    
    def get_most_recently_updated(self, world: str, entries: int = MAX_ITEMS_PER_QUERY) -> Dict:
        """Fetch most recently updated items for a world."""
        logger.info(f"Fetching most recently updated items for {world} (limit: {entries})")
        result = self._make_request(
            f"{self.BASE_URL}/extra/stats/most-recently-updated",
            params={"world": world, "entries": min(entries, MAX_ITEMS_PER_QUERY)}
        )
        logger.info(f"Retrieved {len(result.get('items', []))} items")
        return result
    
    def get_market_data(self, world: str, item_id: int) -> Dict:
        """Fetch current market data for an item on a world."""
        logger.debug(f"Fetching market data for item {item_id} on {world}")
        return self._make_request(f"{self.BASE_URL}/{world}/{item_id}")
    
    def get_history(self, world: str, item_id: int, entries: int = DEFAULT_HISTORY_ENTRIES) -> Dict:
        """Fetch sales history for an item on a world."""
        logger.debug(f"Fetching history for item {item_id} on {world} (limit: {entries})")
        return self._make_request(
            f"{self.BASE_URL}/history/{world}/{item_id}",
            params={"entries": entries}
        )


@click.group()
@click.version_option(version="1.0.0", prog_name="Universus")
@click.option('--db-path', default='market_data.db', help='Path to database file')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.pass_context
def cli(ctx, db_path, verbose):
    """Universus - FFXIV Market Price CLI using Universalis API."""
    ctx.ensure_object(dict)
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    logger.info(f"Starting Universus CLI (verbose: {verbose})")
    logger.debug(f"Database path: {db_path}")
    
    ctx.obj['DB_PATH'] = db_path
    ctx.obj['API'] = UniversalisAPI()
    ctx.obj['DB'] = MarketDatabase(db_path)


@cli.result_callback()
@click.pass_context
def cleanup(ctx, result, **kwargs):
    """Cleanup resources after command execution."""
    logger.debug("Starting cleanup of resources")
    if 'DB' in ctx.obj and ctx.obj['DB']:
        ctx.obj['DB'].close()
    if 'API' in ctx.obj and ctx.obj['API']:
        ctx.obj['API'].close()
    logger.info("Cleanup complete")


@cli.command()
@click.pass_context
def datacenters(ctx):
    """List all available FFXIV datacenters."""
    logger.info("Executing 'datacenters' command")
    api = ctx.obj['API']
    
    with console.status("[bold green]Fetching datacenters..."):
        try:
            dcs = api.get_datacenters()
        except Exception as e:
            logger.error(f"Failed to fetch datacenters: {e}")
            console.print(f"[bold red]Error:[/bold red] {e}")
            sys.exit(1)
    
    if not dcs:
        console.print("[yellow]No datacenters found.[/yellow]")
        return
    
    # Create a table to display the datacenters
    table = Table(title="Final Fantasy XIV Datacenters", show_header=True, header_style="bold magenta")
    table.add_column("Datacenter", style="cyan", no_wrap=True)
    table.add_column("Region", style="green")
    table.add_column("Worlds", style="yellow")
    
    # Sort datacenters by region and name
    sorted_dcs = sorted(dcs, key=lambda x: (x.get('region', ''), x.get('name', '')))
    
    for dc in sorted_dcs:
        name = dc.get('name', 'N/A')
        region = dc.get('region', 'N/A')
        worlds = dc.get('worlds', [])
        
        # Format worlds list
        worlds_str = f"{len(worlds)} worlds" if worlds else "No worlds"
        
        table.add_row(name, region, worlds_str)
    
    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(dcs)} datacenters")


@cli.command()
@click.option('--world', required=True, help='World name (e.g., Behemoth)')
@click.option('--limit', default=50, help='Number of top items to track (default: 50)')
@click.pass_context
def init_tracking(ctx, world, limit):
    """Initialize tracking for top volume items on a world."""
    logger.info(f"Executing 'init-tracking' command for {world} (limit: {limit})")
    api = ctx.obj['API']
    db = ctx.obj['DB']
    
    console.print(f"[cyan]Initializing tracking for {world}...[/cyan]")
    console.print(f"[dim]Rate limit: 2 requests/second (respecting API limits)[/dim]\n")
    
    try:
        # Get most recently updated items (proxy for high volume)
        data = api.get_most_recently_updated(world, entries=limit)
        items = data.get('items', [])
        
        if not items:
            console.print(f"[yellow]No items found for {world}[/yellow]")
            return
        
        console.print(f"[green]Found {len(items)} items. Analyzing sale velocities...[/green]")
        
        # Fetch market data for each item to get sale velocity
        item_velocities = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Analyzing items...", total=len(items))
            
            for item_entry in items:
                item_id = item_entry.get('itemID')
                if not item_id:
                    progress.advance(task)
                    continue
                
                try:
                    market_data = api.get_market_data(world, item_id)
                    velocity = market_data.get('regularSaleVelocity', 0)
                    
                    if velocity > 0:  # Only track items with actual sales
                        item_velocities.append({
                            'item_id': item_id,
                            'velocity': velocity,
                            'avg_price': market_data.get('averagePrice', 0)
                        })
                        db.add_tracked_item(item_id, world)
                    
                    progress.advance(task)
                    
                except Exception as e:
                    logger.debug(f"Failed to fetch data for item {item_id}: {e}")
                    progress.advance(task)
                    continue
        
        # Sort by velocity and show top items
        item_velocities.sort(key=lambda x: x['velocity'], reverse=True)
        top_items = item_velocities[:limit]
        
        table = Table(title=f"Tracking Top {len(top_items)} Items on {world}", 
                     show_header=True, header_style="bold magenta")
        table.add_column("Item ID", style="cyan")
        table.add_column("Daily Sales", justify="right", style="green")
        table.add_column("Avg Price", justify="right", style="yellow")
        
        for item in top_items:
            table.add_row(
                str(item['item_id']),
                f"{item['velocity']:.2f}",
                f"{item['avg_price']:,.0f} gil"
            )
        
        console.print(table)
        console.print(f"\n[bold green]✓[/bold green] Initialized tracking for {len(top_items)} items on {world}")
        console.print(f"[dim]Database: {ctx.obj['DB_PATH']}[/dim]")
        logger.info(f"Successfully initialized tracking for {len(top_items)} items on {world}")
        
    except Exception as e:
        logger.error(f"Init tracking failed: {e}", exc_info=True)
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


@cli.command()
@click.option('--world', required=True, help='World name to update')
@click.pass_context
def update(ctx, world):
    """Update market data for all tracked items on a world."""
    logger.info(f"Executing 'update' command for {world}")
    api = ctx.obj['API']
    db = ctx.obj['DB']
    
    tracked_items = db.get_tracked_items(world)
    
    if not tracked_items:
        console.print(f"[yellow]No items being tracked for {world}. Run 'init-tracking' first.[/yellow]")
        return
    
    console.print(f"[cyan]Updating {len(tracked_items)} items on {world}...[/cyan]")
    console.print(f"[dim]Rate limit: 2 requests/second • This will take ~{len(tracked_items)} seconds[/dim]\n")
    
    successful = 0
    failed = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Fetching market data...", total=len(tracked_items))
        
        for item in tracked_items:
            item_id = item['item_id']
            
            try:
                # Fetch current market data
                market_data = api.get_market_data(world, item_id)
                db.save_snapshot(item_id, world, market_data)
                
                # Fetch and save recent sales history
                history_data = api.get_history(world, item_id, entries=100)
                if 'entries' in history_data:
                    db.save_sales(item_id, world, history_data['entries'])
                
                successful += 1
                progress.advance(task)
                
            except Exception as e:
                logger.debug(f"Failed to update item {item_id}: {e}")
                failed += 1
                progress.advance(task)
                continue
    
    console.print(f"\n[bold green]✓[/bold green] Updated {successful} items")
    if failed > 0:
        console.print(f"[yellow]⚠[/yellow] Failed to update {failed} items")
    
    logger.info(f"Update complete: {successful} successful, {failed} failed")
    console.print(f"[dim]Tip: Schedule this command daily via cron/Task Scheduler[/dim]")


@cli.command()
@click.option('--world', required=True, help='World name')
@click.option('--limit', default=10, help='Number of top items to show')
@click.pass_context
def top(ctx, world, limit):
    """Show top selling items by volume on a world."""
    logger.info(f"Executing 'top' command for {world} (limit: {limit})")
    db = ctx.obj['DB']
    
    top_items = db.get_top_volume_items(world, limit)
    
    if not top_items:
        console.print(f"[yellow]No data available for {world}. Run 'update' first.[/yellow]")
        return
    
    table = Table(title=f"Top {len(top_items)} Items by Sales Volume on {world}",
                 show_header=True, header_style="bold magenta")
    table.add_column("Rank", style="cyan", width=6)
    table.add_column("Item ID", style="yellow")
    table.add_column("Daily Sales", justify="right", style="green")
    table.add_column("Avg Price", justify="right", style="magenta")
    table.add_column("Last Updated", style="dim")
    
    for idx, item in enumerate(top_items, 1):
        try:
            last_updated = datetime.fromisoformat(item['last_updated'])
            time_ago = datetime.now() - last_updated
        except (ValueError, TypeError):
            time_str = "Unknown"
        else:
        
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds // 3600}h ago"
            else:
                time_str = f"{time_ago.seconds // 60}m ago"
        
        table.add_row(
            str(idx),
            str(item['item_id']),
            f"{item['sale_velocity']:.2f}" if item['sale_velocity'] else "N/A",
            f"{item['average_price']:,.0f} gil" if item['average_price'] else "N/A",
            time_str
        )
    
    console.print(table)
    console.print(f"\n[dim]Snapshot date: {top_items[0]['snapshot_date']}[/dim]")


@cli.command()
@click.option('--world', required=True, help='World name')
@click.option('--item-id', required=True, type=int, help='Item ID to report on')
@click.option('--days', default=30, help='Number of days to show (default: 30)')
@click.pass_context
def report(ctx, world, item_id, days):
    """Show detailed historical report for a specific item."""
    logger.info(f"Executing 'report' command for item {item_id} on {world} ({days} days)")
    db = ctx.obj['DB']
    
    snapshots = db.get_snapshots(item_id, world, days)
    
    if not snapshots:
        console.print(f"[yellow]No data available for item {item_id} on {world}[/yellow]")
        return
    
    console.print(f"\n[bold cyan]Item {item_id} on {world}[/bold cyan]")
    console.print(f"[dim]Historical data for the last {len(snapshots)} days[/dim]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Date", style="cyan")
    table.add_column("Daily Sales", justify="right", style="green")
    table.add_column("Avg Price", justify="right", style="yellow")
    table.add_column("Min Price", justify="right")
    table.add_column("Max Price", justify="right")
    table.add_column("Listings", justify="right")
    
    for snapshot in reversed(snapshots):  # Show oldest to newest
        table.add_row(
            snapshot['snapshot_date'],
            f"{snapshot['sale_velocity']:.2f}" if snapshot['sale_velocity'] else "N/A",
            f"{snapshot['average_price']:,.0f}" if snapshot['average_price'] else "N/A",
            f"{snapshot['min_price']:,}" if snapshot['min_price'] else "N/A",
            f"{snapshot['max_price']:,}" if snapshot['max_price'] else "N/A",
            str(snapshot['total_listings']) if snapshot['total_listings'] else "0"
        )
    
    console.print(table)
    
    # Calculate trends
    if len(snapshots) >= 2:
        latest = snapshots[0]
        oldest = snapshots[-1]
        
        if latest['sale_velocity'] and oldest['sale_velocity']:
            velocity_change = ((latest['sale_velocity'] - oldest['sale_velocity']) / 
                             oldest['sale_velocity'] * 100)
            velocity_emoji = "📈" if velocity_change > 0 else "📉"
            console.print(f"\n{velocity_emoji} Sales velocity trend: {velocity_change:+.1f}%")
        
        if latest['average_price'] and oldest['average_price']:
            price_change = ((latest['average_price'] - oldest['average_price']) / 
                          oldest['average_price'] * 100)
            price_emoji = "💰" if price_change > 0 else "💸"
            console.print(f"{price_emoji} Price trend: {price_change:+.1f}%")


@cli.command()
@click.pass_context
def list_tracked(ctx):
    """List all tracked items across all worlds."""
    logger.info("Executing 'list-tracked' command")
    db = ctx.obj['DB']
    
    tracked = db.get_tracked_items()
    
    if not tracked:
        console.print("[yellow]No items being tracked. Run 'init-tracking' first.[/yellow]")
        return
    
    # Group by world
    by_world = {}
    for item in tracked:
        world = item['world']
        if world not in by_world:
            by_world[world] = []
        by_world[world].append(item)
    
    console.print(f"\n[bold cyan]Tracked Items Summary[/bold cyan]\n")
    
    for world, items in sorted(by_world.items()):
        console.print(f"[bold]{world}[/bold]: {len(items)} items")
        console.print(f"[dim]Last updated: {items[0]['last_updated']}[/dim]\n")


if __name__ == "__main__":
    cli(obj={})
