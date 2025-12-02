#!/usr/bin/env python3
"""
Universus - A CLI for Final Fantasy XIV market prices using the Universalis API.
"""

import sys
import logging
import click

from config import get_config
from database import MarketDatabase
from api_client import UniversalisAPI
from service import MarketService
from ui import MarketUI

# Application version - single source of truth
__version__ = "1.0.0"

logger = logging.getLogger(__name__)

# Load configuration
config = get_config()


@click.group()
@click.version_option(version=__version__, prog_name="Universus")
@click.option('--db-path', default=None, help='Path to database file')
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
@click.option('--config-file', 'config_path', default=None, help='Path to config.toml file')
@click.pass_context
def cli(ctx, db_path, verbose, config_path):
    """Universus - FFXIV Market Price CLI using Universalis API."""
    ctx.ensure_object(dict)
    
    # Load configuration (reload if custom path provided)
    if config_path:
        from config import reload_config
        reload_config(config_path)
    
    # Use config default if db_path not provided
    if db_path is None:
        db_path = config.get('database', 'default_path', 'market_data.db')
    
    # Setup logging
    log_level = logging.DEBUG if verbose else logging.INFO
    log_format = config.get('logging', 'format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    date_format = config.get('logging', 'date_format', '%Y-%m-%d %H:%M:%S')
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format
    )
    
    logger.info(f"Starting Universus CLI (verbose: {verbose})")
    logger.debug(f"Database path: {db_path}")
    
    ctx.obj['DB_PATH'] = db_path
    ctx.obj['API'] = UniversalisAPI()
    ctx.obj['DB'] = MarketDatabase(db_path)
    ctx.obj['SERVICE'] = MarketService(ctx.obj['DB'], ctx.obj['API'])


@cli.result_callback()
@click.pass_context
def cleanup(ctx, result, **kwargs):
    """Cleanup resources after command execution."""
    logger.debug("Starting cleanup of resources")
    try:
        if 'DB' in ctx.obj and ctx.obj['DB']:
            ctx.obj['DB'].close()
    except Exception as e:
        logger.error(f"Error closing database: {e}")
    finally:
        try:
            if 'API' in ctx.obj and ctx.obj['API']:
                ctx.obj['API'].close()
        except Exception as e:
            logger.error(f"Error closing API client: {e}")
        finally:
            logger.info("Cleanup complete")


@cli.command()
@click.pass_context
def datacenters(ctx):
    """List all available FFXIV datacenters."""
    logger.info("Executing 'datacenters' command")
    service = ctx.obj['SERVICE']
    
    try:
        with MarketUI.show_status("Fetching datacenters..."):
            dcs = service.get_datacenters()
        
        MarketUI.show_datacenters(dcs)
    except Exception as e:
        logger.error(f"Failed to fetch datacenters: {e}")
        MarketUI.exit_with_error(str(e))


@cli.command()
@click.option('--world', required=True, help='World name (e.g., Behemoth)')
@click.option('--limit', default=None, type=int, help='Number of top items to track')
@click.pass_context
def init_tracking(ctx, world, limit):
    """Initialize tracking for top volume items on a world."""
    if limit is None:
        limit = config.get('cli', 'default_tracking_limit', 50)
    logger.info(f"Executing 'init-tracking' command for {world} (limit: {limit})")
    service = ctx.obj['SERVICE']
    
    MarketUI.show_init_tracking_header(world, limit)
    
    try:
        # Get most recently updated items
        with MarketUI.show_status("Fetching items..."):
            pass
        
        with MarketUI.show_init_tracking_progress(limit) as progress:
            task = progress.add_task("Analyzing items...", total=limit)
            
            # Initialize tracking and get results
            top_items, total_found, items_with_sales = service.initialize_tracking(world, limit)
            
            # Update progress to complete
            progress.update(task, completed=limit)
        
        if not top_items:
            MarketUI.print_warning(f"No items with sales data found for {world}")
            return
        
        MarketUI.show_init_tracking_results(world, top_items, ctx.obj['DB_PATH'])
        
    except Exception as e:
        logger.error(f"Init tracking failed: {e}", exc_info=True)
        MarketUI.exit_with_error(str(e))


@cli.command()
@click.option('--world', required=True, help='World name to update')
@click.pass_context
def update(ctx, world):
    """Update market data for all tracked items on a world."""
    logger.info(f"Executing 'update' command for {world}")
    service = ctx.obj['SERVICE']
    db = ctx.obj['DB']
    
    # Get tracked items count for display
    tracked_count = db.get_tracked_items_count(world)
    
    if tracked_count == 0:
        MarketUI.print_warning(f"No items being tracked for {world}. Run 'init-tracking' first.")
        return
    
    MarketUI.show_update_header(world, tracked_count)
    
    with MarketUI.show_update_progress(tracked_count) as progress:
        task = progress.add_task("Fetching market data...", total=tracked_count)
        
        # Update items (service handles the actual query)
        successful, failed, _ = service.update_tracked_items(world)
        
        # Update progress to complete
        progress.update(task, completed=tracked_count)
    
    MarketUI.show_update_results(successful, failed)


@cli.command()
@click.option('--world', required=True, help='World name')
@click.option('--limit', default=None, type=int, help='Number of top items to show')
@click.pass_context
def top(ctx, world, limit):
    """Show top selling items by volume on a world."""
    if limit is None:
        limit = config.get('cli', 'default_top_limit', 10)
    logger.info(f"Executing 'top' command for {world} (limit: {limit})")
    service = ctx.obj['SERVICE']
    
    top_items = service.get_top_items(world, limit)
    MarketUI.show_top_items(world, top_items, service.format_time_ago)


@cli.command()
@click.option('--world', required=True, help='World name')
@click.option('--item-id', required=True, type=int, help='Item ID to report on')
@click.option('--days', default=None, type=int, help='Number of days to show')
@click.pass_context
def report(ctx, world, item_id, days):
    """Show detailed historical report for a specific item."""
    if days is None:
        days = config.get('cli', 'default_report_days', 30)
    logger.info(f"Executing 'report' command for item {item_id} on {world} ({days} days)")
    service = ctx.obj['SERVICE']
    
    snapshots = service.get_item_report(world, item_id, days)
    
    if not snapshots:
        MarketUI.print_warning(f"No data available for item {item_id} on {world}")
        return
    
    MarketUI.show_item_report_header(world, item_id, len(snapshots))
    MarketUI.show_item_report_table(snapshots)
    
    # Calculate and show trends
    trends = service.calculate_trends(snapshots)
    if trends:
        MarketUI.show_trends(trends)


@cli.command()
@click.pass_context
def list_tracked(ctx):
    """List all tracked items across all worlds."""
    logger.info("Executing 'list-tracked' command")
    service = ctx.obj['SERVICE']
    
    by_world = service.get_all_tracked_items()
    MarketUI.show_tracked_summary(by_world)


@cli.command()
@click.pass_context
def sync_items(ctx):
    """Sync item names from FFXIV Teamcraft data dump.
    
    This command fetches the latest item database from FFXIV Teamcraft
    and updates the local database. Any existing items will be replaced.
    """
    logger.info("Executing 'sync-items' command")
    service = ctx.obj['SERVICE']
    
    try:
        with MarketUI.show_status("Fetching items from FFXIV Teamcraft (this may take a moment)..."):
            count = service.sync_items_database()
        
        MarketUI.print_success(f"Successfully synced {count:,} items to local database")
    except Exception as e:
        logger.error(f"Failed to sync items: {e}")
        MarketUI.exit_with_error(f"Failed to sync items: {str(e)}")


@cli.command()
@click.pass_context
def sync_marketable(ctx):
    """Sync marketable items from Universalis API.
    
    This command downloads all marketable item IDs from the Universalis API
    and stores them in the local database. Any existing marketable items data
    will be cleared first.
    """
    logger.info("Executing 'sync-marketable' command")
    service = ctx.obj['SERVICE']
    
    try:
        with MarketUI.show_status("Downloading marketable items from Universalis API..."):
            count = service.sync_marketable_items()
        
        MarketUI.print_success(f"Successfully synced {count:,} marketable items to local database")
    except Exception as e:
        logger.error(f"Failed to sync marketable items: {e}")
        MarketUI.exit_with_error(f"Failed to sync marketable items: {str(e)}")


@cli.group(name='tracked-worlds')
@click.pass_context
def tracked_worlds_group(ctx):
    """Manage tracked worlds configuration (CRUD)."""
    pass


@tracked_worlds_group.command('list')
@click.pass_context
def tracked_worlds_list(ctx):
    """List all tracked worlds."""
    logger.info("Executing 'tracked-worlds list' command")
    service = ctx.obj['SERVICE']
    worlds = service.list_tracked_worlds()
    MarketUI.show_tracked_worlds(worlds)


@tracked_worlds_group.command('add')
@click.option('--world', required=False, help='World name (e.g., Behemoth)')
@click.option('--world-id', required=False, type=int, help='World ID')
@click.pass_context
def tracked_worlds_add(ctx, world, world_id):
    """Add a world to tracked worlds configuration."""
    logger.info("Executing 'tracked-worlds add' command")
    service = ctx.obj['SERVICE']
    try:
        with MarketUI.show_status("Resolving world..."):
            info = service.add_tracked_world(world=world, world_id=world_id)
        MarketUI.print_success(f"Added tracked world: {info['name'] or info['id']} (ID {info['id']})")
    except Exception as e:
        logger.error(f"Failed to add tracked world: {e}")
        MarketUI.exit_with_error(str(e))


@tracked_worlds_group.command('remove')
@click.option('--world', required=False, help='World name (e.g., Behemoth)')
@click.option('--world-id', required=False, type=int, help='World ID')
@click.pass_context
def tracked_worlds_remove(ctx, world, world_id):
    """Remove a world from tracked worlds configuration."""
    logger.info("Executing 'tracked-worlds remove' command")
    service = ctx.obj['SERVICE']
    try:
        with MarketUI.show_status("Removing world..."):
            deleted = service.remove_tracked_world(world=world, world_id=world_id)
        if deleted:
            MarketUI.print_success("Removed tracked world")
        else:
            MarketUI.print_warning("World not found in tracked configuration")
    except Exception as e:
        logger.error(f"Failed to remove tracked world: {e}")
        MarketUI.exit_with_error(str(e))


@tracked_worlds_group.command('clear')
@click.pass_context
def tracked_worlds_clear(ctx):
    """Clear all tracked worlds configuration."""
    logger.info("Executing 'tracked-worlds clear' command")
    service = ctx.obj['SERVICE']
    try:
        with MarketUI.show_status("Clearing tracked worlds..."):
            service.clear_tracked_worlds()
        MarketUI.print_success("Cleared tracked worlds configuration")
    except Exception as e:
        logger.error(f"Failed to clear tracked worlds: {e}")
        MarketUI.exit_with_error(str(e))


@cli.command(name='refresh-cache')
@click.pass_context
def refresh_cache(ctx):
    """Refresh cached datacenter and world data.
    
    This command updates the local cache of datacenter and world information
    from the Universalis API. The cache is automatically used and refreshed
    daily, but this command allows manual refresh if needed.
    """
    logger.info("Executing 'refresh-cache' command")
    service = ctx.obj['SERVICE']
    
    try:
        with MarketUI.show_status("Refreshing datacenter and world cache..."):
            result = service.refresh_cache()
        
        MarketUI.print_success(
            f"Cache refreshed: {result['datacenters']} datacenters, {result['worlds']} worlds"
        )
        
        # Show cache status
        db = ctx.obj['DB']
        status = db.get_cache_status()
        MarketUI.print_info(f"Datacenters cached: {status['datacenters']['count']} (last updated: {status['datacenters']['last_updated']})")
        MarketUI.print_info(f"Worlds cached: {status['worlds']['count']} (last updated: {status['worlds']['last_updated']})")
    except Exception as e:
        logger.error(f"Failed to refresh cache: {e}")
        MarketUI.exit_with_error(str(e))


@cli.command(name='update-current-prices')
@click.pass_context
def update_current_prices(ctx):
    """Update current aggregated prices for all marketable items on tracked worlds.
    
    - Reads marketable item IDs from `marketable_items` table
    - Reads tracked worlds from `tracked_worlds` table
    - Calls Universalis aggregated API in batches of 100 per world
    - Stores results in `current_prices` table with timestamp and tracked world id
    - Skips items already updated today per world
    """
    logger.info("Executing 'update-current-prices' command")
    service = ctx.obj['SERVICE']
    try:
        with MarketUI.show_status("Updating aggregated prices (batched)..."):
            summary = service.update_current_item_prices()
        MarketUI.print_success(
            f"Updated {summary['updated']:,} entries across {summary['worlds']} worlds (skipped {summary['skipped']:,}; total items {summary['items']:,})"
        )
    except Exception as e:
        logger.error(f"Failed to update current prices: {e}")
        MarketUI.exit_with_error(str(e))


if __name__ == "__main__":
    cli(obj={})
