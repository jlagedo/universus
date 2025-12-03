"""
Business logic layer for market data operations.
"""

import logging
import asyncio
from typing import List, Dict, Tuple
from datetime import datetime

import requests

from config import get_config
from database import MarketDatabase
from api_client import UniversalisAPI
from executor import executor

logger = logging.getLogger(__name__)

# Load configuration
config = get_config()


class MarketService:
    """Service layer for market data operations."""
    
    def __init__(self, db: MarketDatabase, api: UniversalisAPI):
        self.db = db
        self.api = api
    
    def get_datacenters(self, use_cache: bool = True, max_age_hours: int = 24) -> List[Dict]:
        """Fetch and return all datacenters, using cache when possible.
        
        Args:
            use_cache: Whether to use cached data (default True)
            max_age_hours: Maximum age of cache in hours (default 24)
            
        Returns:
            List of datacenter dictionaries
        """
        if use_cache:
            cached = self.db.get_datacenters_cache(max_age_hours)
            if cached:
                logger.info("Using cached datacenters")
                return cached
        
        # Fetch from API and cache
        logger.info("Fetching datacenters from API")
        datacenters = self.api.get_datacenters()
        self.db.save_datacenters_cache(datacenters)
        return datacenters
    
    def get_available_worlds(self, use_cache: bool = True, max_age_hours: int = 24) -> List[Dict]:
        """Fetch and return all available worlds, using cache when possible.
        
        Args:
            use_cache: Whether to use cached data (default True)
            max_age_hours: Maximum age of cache in hours (default 24)
            
        Returns:
            List of world dictionaries with 'id' and 'name' keys
        """
        if use_cache:
            cached = self.db.get_worlds_cache(max_age_hours)
            if cached:
                logger.info("Using cached worlds")
                return cached
        
        # Fetch from API and cache
        logger.info("Fetching worlds from API")
        worlds = self.api.get_worlds()
        self.db.save_worlds_cache(worlds)
        return worlds
    
    def refresh_cache(self) -> Dict[str, int]:
        """Manually refresh all caches.
        
        Returns:
            Dict with counts of cached items
        """
        logger.info("Manually refreshing caches")
        
        datacenters = self.api.get_datacenters()
        dc_count = self.db.save_datacenters_cache(datacenters)
        
        worlds = self.api.get_worlds()
        worlds_count = self.db.save_worlds_cache(worlds)
        
        return {
            'datacenters': dc_count,
            'worlds': worlds_count
        }
    
    async def refresh_cache_async(self) -> Dict[str, int]:
        """Async version: Manually refresh all caches.
        
        Returns:
            Dict with counts of cached items
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.refresh_cache
        )
    
    def initialize_tracking(self, world: str, limit: int) -> Tuple[List[Dict], int, int]:
        """
        Initialize tracking for top volume items on a world.
        
        Returns:
            Tuple of (top_items, total_found, items_with_sales)
        """
        logger.info(f"Initializing tracking for {world} with limit {limit}")
        
        # Get most recently updated items
        data = self.api.get_most_recently_updated(world, entries=limit)
        items = data.get('items', [])
        
        if not items:
            logger.warning(f"No items found for {world}")
            return [], 0, 0
        
        # Fetch market data for each item to get sale velocity
        item_velocities = []
        
        for item_entry in items:
            item_id = item_entry.get('itemID')
            if not item_id:
                continue
            
            try:
                market_data = self.api.get_market_data(world, item_id)
                velocity = market_data.get('regularSaleVelocity', 0)
                
                if velocity > 0:  # Only track items with actual sales
                    item_velocities.append({
                        'item_id': item_id,
                        'velocity': velocity,
                        'avg_price': market_data.get('averagePrice', 0)
                    })
                    self.db.add_tracked_item(item_id, world)
                
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                logger.warning(f"Failed to fetch data for item {item_id}: {e}")
                continue
        
        # Sort by velocity and return top items
        item_velocities.sort(key=lambda x: x['velocity'], reverse=True)
        top_items = item_velocities[:limit]
        
        logger.info(f"Initialized tracking for {len(top_items)} items with sales data")
        return top_items, len(items), len(item_velocities)
    
    async def initialize_tracking_async(self, world: str, limit: int) -> Tuple[List[Dict], int, int]:
        """Async version: Initialize tracking for top volume items on a world.
        
        Non-blocking version that runs in executor.
        
        Returns:
            Tuple of (top_items, total_found, items_with_sales)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.initialize_tracking,
            world,
            limit
        )
    
    def update_tracked_items(self, world: str) -> Tuple[int, int, List[Dict]]:
        """
        Update market data for all tracked items on a world.
        
        Returns:
            Tuple of (successful_count, failed_count, tracked_items)
        """
        logger.info(f"Updating tracked items for {world}")
        tracked_items = self.db.get_tracked_items(world)
        
        if not tracked_items:
            logger.warning(f"No tracked items found for {world}")
            return 0, 0, []
        
        successful = 0
        failed = 0
        
        for item in tracked_items:
            item_id = item['item_id']
            
            try:
                # Fetch current market data
                market_data = self.api.get_market_data(world, item_id)
                self.db.save_snapshot(item_id, world, market_data)
                
                # Fetch and save recent sales history
                history_data = self.api.get_history(world, item_id)
                if 'entries' in history_data:
                    self.db.save_sales(item_id, world, history_data['entries'])
                
                successful += 1
                
            except (requests.RequestException, ConnectionError, TimeoutError) as e:
                logger.warning(f"Failed to update item {item_id}: {e}")
                failed += 1
                continue
        
        logger.info(f"Update complete: {successful} successful, {failed} failed")
        return successful, failed, tracked_items
    
    async def update_tracked_items_async(self, world: str) -> Tuple[int, int, List[Dict]]:
        """Async version: Update market data for all tracked items on a world.
        
        Non-blocking version that runs in executor.
        
        Returns:
            Tuple of (successful_count, failed_count, tracked_items)
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.update_tracked_items,
            world
        )
    
    def get_top_items(self, world: str, limit: int) -> List[Dict]:
        """Get top selling items by volume on a world."""
        logger.debug(f"Fetching top {limit} items for {world}")
        return self.db.get_top_volume_items(world, limit)
    
    def get_item_report(self, world: str, item_id: int, days: int) -> List[Dict]:
        """Get historical report for a specific item."""
        logger.debug(f"Fetching report for item {item_id} on {world} ({days} days)")
        return self.db.get_snapshots(item_id, world, days)
    
    def get_all_tracked_items(self) -> Dict[str, List[Dict]]:
        """Get all tracked items grouped by world."""
        logger.debug("Fetching all tracked items")
        tracked = self.db.get_tracked_items()
        
        # Group by world
        by_world = {}
        for item in tracked:
            world = item['world']
            if world not in by_world:
                by_world[world] = []
            by_world[world].append(item)
        
        return by_world
    
    def calculate_trends(self, snapshots: List[Dict]) -> Dict[str, float]:
        """
        Calculate trends from snapshot data.
        
        Returns:
            Dict with 'velocity_change' and 'price_change' percentages
        """
        if len(snapshots) < 2:
            return {}
        
        latest = snapshots[0]
        oldest = snapshots[-1]
        trends = {}
        
        if latest['sale_velocity'] and oldest['sale_velocity'] and oldest['sale_velocity'] != 0:
            velocity_change = ((latest['sale_velocity'] - oldest['sale_velocity']) / 
                             oldest['sale_velocity'] * 100)
            trends['velocity_change'] = velocity_change
        
        if latest['average_price'] and oldest['average_price'] and oldest['average_price'] != 0:
            price_change = ((latest['average_price'] - oldest['average_price']) / 
                          oldest['average_price'] * 100)
            trends['price_change'] = price_change
        
        return trends
    
    def format_time_ago(self, timestamp_str: str) -> str:
        """Format a timestamp as relative time (e.g., '2h ago')."""
        try:
            last_updated = datetime.fromisoformat(timestamp_str)
            time_ago = datetime.now() - last_updated
        except (ValueError, TypeError):
            return "Unknown"
        
        if time_ago.days > 0:
            return f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            return f"{time_ago.seconds // 3600}h ago"
        else:
            return f"{time_ago.seconds // 60}m ago"
    
    def sync_items_database(self) -> int:
        """Sync item names from FFXIV Teamcraft data dump.
        
        Returns:
            Number of items synced
        """
        logger.info("Starting items database sync")
        items_data = self.api.fetch_teamcraft_items()
        count = self.db.sync_items(items_data)
        logger.info(f"Items sync complete: {count} items")
        return count
    
    async def sync_items_database_async(self) -> int:
        """Async version: Sync item names from FFXIV Teamcraft data dump.
        
        Non-blocking version that runs in executor.
        
        Returns:
            Number of items synced
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.sync_items_database
        )
    
    def sync_marketable_items(self) -> int:
        """Sync marketable item IDs from Universalis API to local database.
        
        This will clear existing marketable items and download fresh data from the API.
        
        Returns:
            Number of items synced
        """
        logger.info("Starting marketable items sync")
        item_ids = self.api.get_marketable_items()
        count = self.db.sync_marketable_items(item_ids)
        logger.info(f"Marketable items sync complete: {count} items")
        return count
    
    async def sync_marketable_items_async(self) -> int:
        """Async version: Sync marketable item IDs from Universalis API.
        
        Non-blocking version that runs in executor.
        
        Returns:
            Number of items synced
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self.sync_marketable_items
        )

    def add_tracked_world(self, world: str = None, world_id: int = None) -> Dict:
        """Add a world to the tracked worlds configuration.
        
        Accepts either a `world` name or `world_id`. When only name is provided,
        it is resolved via the Universalis worlds API.
        
        Returns:
            Dict with keys `id` and `name` for the inserted world.
        """
        logger.info("Adding tracked world configuration")
        if world_id is None and not world:
            raise ValueError("Either world name or world_id must be provided")
        
        resolved_id = world_id
        resolved_name = world
        
        if resolved_id is None:
            worlds = self.api.get_worlds()
            match = next((w for w in worlds if w.get('name') == world), None)
            if not match:
                raise ValueError(f"World not found: {world}")
            resolved_id = match.get('id')
            resolved_name = match.get('name')
        else:
            if resolved_name is None:
                worlds = self.api.get_worlds()
                match = next((w for w in worlds if w.get('id') == world_id), None)
                resolved_name = match.get('name') if match else None
        
        inserted = self.db.add_tracked_world(int(resolved_id), resolved_name)
        if not inserted:
            logger.info("World already present in tracked configuration")
        return {"id": int(resolved_id), "name": resolved_name}

    def remove_tracked_world(self, world: str = None, world_id: int = None) -> bool:
        """Remove a world from the tracked worlds configuration."""
        logger.info("Removing tracked world configuration")
        if world_id is None and not world:
            raise ValueError("Either world name or world_id must be provided")
        
        resolved_id = world_id
        if resolved_id is None:
            worlds = self.api.get_worlds()
            match = next((w for w in worlds if w.get('name') == world), None)
            if not match:
                raise ValueError(f"World not found: {world}")
            resolved_id = match.get('id')
        return self.db.remove_tracked_world(int(resolved_id))

    def list_tracked_worlds(self) -> List[Dict]:
        """List all tracked worlds from the database."""
        return self.db.list_tracked_worlds()

    def clear_tracked_worlds(self):
        """Clear all tracked worlds from the database."""
        self.db.clear_tracked_worlds()

    def update_current_item_prices(self) -> Dict[str, int]:
        """Fetch aggregated prices for all marketable items across tracked worlds.
        
        - Gets all tracked worlds (id+name)
        - Gets all marketable item IDs
        - Skips items already updated today per world
        - Queries Universalis aggregated API in batches of 100 per world
        - Saves results to `current_prices`
        Returns a summary dict with counts.
        """
        tracked_worlds = self.db.list_tracked_worlds()
        if not tracked_worlds:
            return {"worlds": 0, "items": 0, "updated": 0, "skipped": 0}
        item_ids = self.db.get_marketable_item_ids()
        if not item_ids:
            return {"worlds": len(tracked_worlds), "items": 0, "updated": 0, "skipped": 0}
        total_updated = 0
        total_skipped = 0
        for tw in tracked_worlds:
            world_id = tw.get('world_id')
            world_name = tw.get('world_name')
            if not world_name:
                # Resolve world name from API if missing
                try:
                    worlds = self.api.get_worlds()
                    match = next((w for w in worlds if w.get('id') == world_id), None)
                    world_name = match.get('name') if match else str(world_id)
                except Exception:
                    world_name = str(world_id)
            updated_today = self.db.get_items_updated_today(world_id)
            # Batch into groups, skipping already updated ones
            batch_size = config.get('api', 'batch_size', 100)
            batch = []
            for iid in item_ids:
                if iid in updated_today:
                    total_skipped += 1
                    continue
                batch.append(iid)
                if len(batch) == batch_size:
                    data = self.api.get_aggregated_prices(world_name, batch)
                    results = data.get('results', [])
                    self.db.save_aggregated_prices(world_id, results)
                    total_updated += len(results)
                    batch = []
            if batch:
                data = self.api.get_aggregated_prices(world_name, batch)
                results = data.get('results', [])
                self.db.save_aggregated_prices(world_id, results)
                total_updated += len(results)
        return {"worlds": len(tracked_worlds), "items": len(item_ids), "updated": total_updated, "skipped": total_skipped}
