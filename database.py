"""
Database layer for market data storage and retrieval.
"""

import sqlite3
import logging
import threading
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from config import get_config

logger = logging.getLogger(__name__)

# Load configuration
config = get_config()


class MarketDatabase:
    """Local SQLite database for tracking market data."""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = config.get('database', 'default_path', 'market_data.db')
        self.db_path = db_path
        self.conn = None
        self._lock = threading.Lock()  # Thread-safe lock for database operations
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        # check_same_thread=False allows connection to be used across threads
        # This is safe with SQLite's default locking mechanism
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False, timeout=30.0)
        self.conn.row_factory = sqlite3.Row
        # Enable foreign key enforcement
        self.conn.execute("PRAGMA foreign_keys = ON")
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
                UNIQUE(item_id, world, snapshot_date)
            )
        """)
        
        # Table for item names
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS items (
                item_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for tracked worlds configuration
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracked_worlds (
                world_id INTEGER PRIMARY KEY,
                world_name TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for marketable items
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS marketable_items (
                item_id INTEGER PRIMARY KEY,
                last_synced TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for cached datacenters
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_datacenters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                region TEXT NOT NULL,
                worlds TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for cached worlds
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cached_worlds (
                world_id INTEGER PRIMARY KEY,
                world_name TEXT NOT NULL,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for current aggregated prices per tracked world
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS current_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tracked_world_id INTEGER NOT NULL,
                item_id INTEGER NOT NULL,
                fetched_at TIMESTAMP NOT NULL,
                nq_world_min_price INTEGER,
                nq_dc_min_price INTEGER,
                nq_dc_min_world_id INTEGER,
                nq_region_min_price INTEGER,
                nq_region_min_world_id INTEGER,
                nq_world_recent_price INTEGER,
                nq_world_recent_timestamp INTEGER,
                nq_dc_recent_price INTEGER,
                nq_dc_recent_timestamp INTEGER,
                nq_dc_recent_world_id INTEGER,
                nq_region_recent_price INTEGER,
                nq_region_recent_timestamp INTEGER,
                nq_region_recent_world_id INTEGER,
                nq_region_avg_price REAL,
                nq_region_daily_velocity REAL,
                hq_world_min_price INTEGER,
                hq_dc_min_price INTEGER,
                hq_dc_min_world_id INTEGER,
                hq_region_min_price INTEGER,
                hq_region_min_world_id INTEGER,
                hq_world_recent_price INTEGER,
                hq_world_recent_timestamp INTEGER,
                hq_dc_recent_price INTEGER,
                hq_dc_recent_timestamp INTEGER,
                hq_dc_recent_world_id INTEGER,
                hq_region_recent_price INTEGER,
                hq_region_recent_timestamp INTEGER,
                hq_region_recent_world_id INTEGER,
                hq_world_avg_price REAL,
                hq_dc_avg_price REAL,
                hq_region_avg_price REAL,
                hq_world_daily_velocity REAL,
                hq_dc_daily_velocity REAL,
                hq_region_daily_velocity REAL
            )
        """)
        # Unique index for same-day entries
        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_current_prices_unique_day
            ON current_prices(tracked_world_id, item_id, strftime('%Y-%m-%d', fetched_at))
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
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        with self._lock:
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
                """
                SELECT ti.*, it.name AS item_name
                FROM tracked_items ti
                LEFT JOIN items it ON it.item_id = ti.item_id
                WHERE ti.world = ?
                ORDER BY ti.last_updated DESC
                """,
                (world,)
            )
        else:
            cursor.execute(
                """
                SELECT ti.*, it.name AS item_name
                FROM tracked_items ti
                LEFT JOIN items it ON it.item_id = ti.item_id
                ORDER BY ti.last_updated DESC
                """
            )
        results = [dict(row) for row in cursor.fetchall()]
        logger.debug(f"Found {len(results)} tracked items")
        return results
    
    def save_snapshot(self, item_id: int, world: str, data: Dict):
        """Save a daily snapshot of market data."""
        logger.debug(f"Saving snapshot for item {item_id} on {world}")
        with self._lock:
            cursor = self.conn.cursor()
            today = datetime.now().date().isoformat()  # Convert to ISO format string
            
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
        with self._lock:
            cursor = self.conn.cursor()
            
            # Get existing sale keys to filter duplicates in memory
            cursor.execute("""
                SELECT sale_time, price_per_unit FROM sales_history
                WHERE item_id = ? AND world = ?
            """, (item_id, world))
            existing_keys = {(row[0], row[1]) for row in cursor.fetchall()}
            
            # Filter new entries and prepare for bulk insert
            new_entries_data = []
            for entry in entries:
                sale_key = (entry.get('timestamp'), entry.get('pricePerUnit'))
                if sale_key not in existing_keys:
                    new_entries_data.append((
                        item_id, world,
                        entry.get('timestamp'),
                        entry.get('pricePerUnit'),
                        entry.get('quantity'),
                        entry.get('hq', False),
                        entry.get('buyerName')
                    ))
            
            # Bulk insert new entries
            if new_entries_data:
                cursor.executemany("""
                    INSERT INTO sales_history (
                        item_id, world, sale_time, price_per_unit, quantity, is_hq, buyer_name
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """, new_entries_data)
            
            self.conn.commit()
        logger.debug(f"Saved {len(new_entries_data) if 'new_entries_data' in locals() else 0} new sales entries")
    
    def get_snapshots(self, item_id: int, world: str, days: int = 30) -> List[Dict]:
        """Get historical snapshots for an item."""
        cursor = self.conn.cursor()
        cutoff_date = (datetime.now().date() - timedelta(days=days)).isoformat()
        cursor.execute(
            """
            SELECT * FROM daily_snapshots
            WHERE item_id = ? AND world = ? AND snapshot_date >= ?
            ORDER BY snapshot_date DESC
            """,
            (item_id, world, cutoff_date)
        )
        return [dict(row) for row in cursor.fetchall()]

    def get_top_volume_items(self, world: str, limit: int = 10) -> List[Dict]:
        """Get items with highest sale velocity from latest snapshots."""
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT ds.item_id,
                   it.name AS item_name,
                   ds.world,
                   ds.sale_velocity,
                   ds.average_price,
                   ds.snapshot_date,
                   ti.last_updated
            FROM daily_snapshots ds
            JOIN tracked_items ti
              ON ds.item_id = ti.item_id AND ds.world = ti.world
            LEFT JOIN items it
              ON it.item_id = ds.item_id
            WHERE ds.world = ?
              AND ds.snapshot_date = (
                SELECT MAX(snapshot_date)
                FROM daily_snapshots ds2
                WHERE ds2.item_id = ds.item_id AND ds2.world = ds.world
              )
            ORDER BY ds.sale_velocity DESC
            LIMIT ?
            """,
            (world, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensures connection is closed."""
        self.close()
        return False
    
    def sync_items(self, items_data: Dict[str, Dict]) -> int:
        """Sync item names from Teamcraft data dump.
        
        Args:
            items_data: Dictionary mapping item_id (as string) to item data with 'en' field
            
        Returns:
            Number of items synced
        """
        logger.info(f"Syncing {len(items_data)} items to database")
        with self._lock:
            cursor = self.conn.cursor()
            
            # Clear existing items
            logger.debug("Clearing existing items table")
            cursor.execute("DELETE FROM items")
            
            # Insert all items
            count = 0
            for item_id_str, item_data in items_data.items():
                try:
                    item_id = int(item_id_str)
                    name = item_data.get('en', '')
                    if name:  # Only insert items with names
                        cursor.execute(
                            "INSERT INTO items (item_id, name) VALUES (?, ?)",
                            (item_id, name)
                        )
                        count += 1
                except (ValueError, TypeError) as e:
                    logger.warning(f"Skipping invalid item {item_id_str}: {e}")
                    continue
            
            self.conn.commit()
        logger.info(f"Successfully synced {count} items")
        return count
    
    def get_item_name(self, item_id: int) -> Optional[str]:
        """Get item name by ID."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT name FROM items WHERE item_id = ?", (item_id,))
        row = cursor.fetchone()
        return row['name'] if row else None
    
    def get_items_count(self) -> int:
        """Get total count of items in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM items")
        return cursor.fetchone()['count']
    
    def get_marketable_item_ids(self) -> List[int]:
        """Get all marketable item IDs."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT item_id FROM marketable_items")
        return [row[0] for row in cursor.fetchall()]
    
    def get_tracked_items_count(self, world: str = None) -> int:
        """Get count of tracked items, optionally filtered by world."""
        cursor = self.conn.cursor()
        if world:
            cursor.execute(
                "SELECT COUNT(*) as count FROM tracked_items WHERE world = ?",
                (world,)
            )
        else:
            cursor.execute("SELECT COUNT(*) as count FROM tracked_items")
        return cursor.fetchone()['count']
    
    def add_tracked_world(self, world_id: int, world_name: Optional[str] = None) -> bool:
        """Add a world to tracked worlds configuration.
        
        Returns True if inserted, False if already present.
        """
        logger.debug(f"Adding tracked world: id={world_id}, name={world_name}")
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO tracked_worlds (world_id, world_name) VALUES (?, ?)",
                (world_id, world_name)
            )
            self.conn.commit()
            inserted = cursor.rowcount > 0
        logger.debug(f"Tracked world {'inserted' if inserted else 'already exists'}: {world_id}")
        return inserted
    
    def remove_tracked_world(self, world_id: int) -> bool:
        """Remove a world from tracked worlds configuration.
        
        Returns True if a row was deleted.
        """
        logger.debug(f"Removing tracked world: id={world_id}")
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tracked_worlds WHERE world_id = ?", (world_id,))
            self.conn.commit()
            deleted = cursor.rowcount > 0
        logger.debug(f"Tracked world {'deleted' if deleted else 'not found'}: {world_id}")
        return deleted
    
    def list_tracked_worlds(self) -> List[Dict]:
        """List all tracked worlds."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT world_id, world_name, added_at FROM tracked_worlds ORDER BY world_name COLLATE NOCASE ASC"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def clear_tracked_worlds(self):
        """Clear all tracked worlds configuration."""
        logger.debug("Clearing tracked_worlds table")
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM tracked_worlds")
            self.conn.commit()
        logger.info("Tracked worlds cleared")
    
    def get_tracked_worlds_count(self) -> int:
        """Get count of tracked worlds."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM tracked_worlds")
        return cursor.fetchone()['count']
    
    def save_aggregated_prices(self, tracked_world_id: int, results: List[Dict]):
        """Save aggregated prices results for a tracked world.
        
        Skips inserts that already exist for the same day due to UNIQUE constraint.
        """
        def get_nested(d, *keys):
            """Safely get nested dictionary values."""
            try:
                for k in keys:
                    d = d.get(k, {})
                return d
            except AttributeError:
                return {}
        
        with self._lock:
            cursor = self.conn.cursor()
            now = datetime.now().isoformat(sep=' ')
            for item in results:
                item_id = item.get('itemId')
                nq = item.get('nq', {})
                hq = item.get('hq', {})
                cursor.execute(
                    """
                    INSERT OR IGNORE INTO current_prices (
                        tracked_world_id, item_id, fetched_at,
                        nq_world_min_price, nq_dc_min_price, nq_dc_min_world_id, nq_region_min_price, nq_region_min_world_id,
                        nq_world_recent_price, nq_world_recent_timestamp,
                        nq_dc_recent_price, nq_dc_recent_timestamp, nq_dc_recent_world_id,
                        nq_region_recent_price, nq_region_recent_timestamp, nq_region_recent_world_id,
                        nq_region_avg_price, nq_region_daily_velocity,
                        hq_world_min_price, hq_dc_min_price, hq_dc_min_world_id, hq_region_min_price, hq_region_min_world_id,
                        hq_world_recent_price, hq_world_recent_timestamp,
                        hq_dc_recent_price, hq_dc_recent_timestamp, hq_dc_recent_world_id,
                        hq_region_recent_price, hq_region_recent_timestamp, hq_region_recent_world_id,
                        hq_world_avg_price, hq_dc_avg_price, hq_region_avg_price,
                        hq_world_daily_velocity, hq_dc_daily_velocity, hq_region_daily_velocity
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        tracked_world_id, item_id, now,
                        nq.get('minListing', {}).get('world', {}).get('price'),
                        nq.get('minListing', {}).get('dc', {}).get('price'),
                        nq.get('minListing', {}).get('dc', {}).get('worldId'),
                        nq.get('minListing', {}).get('region', {}).get('price'),
                        nq.get('minListing', {}).get('region', {}).get('worldId'),
                        nq.get('recentPurchase', {}).get('world', {}).get('price'),
                        nq.get('recentPurchase', {}).get('world', {}).get('timestamp'),
                        nq.get('recentPurchase', {}).get('dc', {}).get('price'),
                        nq.get('recentPurchase', {}).get('dc', {}).get('timestamp'),
                        nq.get('recentPurchase', {}).get('dc', {}).get('worldId'),
                        nq.get('recentPurchase', {}).get('region', {}).get('price'),
                        nq.get('recentPurchase', {}).get('region', {}).get('timestamp'),
                        nq.get('recentPurchase', {}).get('region', {}).get('worldId'),
                        get_nested(nq, 'averageSalePrice', 'region').get('price'),
                        get_nested(nq, 'dailySaleVelocity', 'region').get('quantity'),
                        hq.get('minListing', {}).get('world', {}).get('price'),
                        hq.get('minListing', {}).get('dc', {}).get('price'),
                        hq.get('minListing', {}).get('dc', {}).get('worldId'),
                        hq.get('minListing', {}).get('region', {}).get('price'),
                        hq.get('minListing', {}).get('region', {}).get('worldId'),
                        hq.get('recentPurchase', {}).get('world', {}).get('price'),
                        hq.get('recentPurchase', {}).get('world', {}).get('timestamp'),
                        hq.get('recentPurchase', {}).get('dc', {}).get('price'),
                        hq.get('recentPurchase', {}).get('dc', {}).get('timestamp'),
                        hq.get('recentPurchase', {}).get('dc', {}).get('worldId'),
                        hq.get('recentPurchase', {}).get('region', {}).get('price'),
                        hq.get('recentPurchase', {}).get('region', {}).get('timestamp'),
                        hq.get('recentPurchase', {}).get('region', {}).get('worldId'),
                        get_nested(hq, 'averageSalePrice', 'world').get('price'),
                        get_nested(hq, 'averageSalePrice', 'dc').get('price'),
                        get_nested(hq, 'averageSalePrice', 'region').get('price'),
                        get_nested(hq, 'dailySaleVelocity', 'world').get('quantity'),
                        get_nested(hq, 'dailySaleVelocity', 'dc').get('quantity'),
                        get_nested(hq, 'dailySaleVelocity', 'region').get('quantity'),
                    )
                )
            self.conn.commit()
    
    def get_items_updated_today(self, tracked_world_id: int) -> set:
        """Return a set of item_ids already updated today for the tracked world."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT item_id FROM current_prices WHERE tracked_world_id = ? AND strftime('%Y-%m-%d', fetched_at) = strftime('%Y-%m-%d', 'now', 'localtime')",
            (tracked_world_id,)
        )
        return {row[0] for row in cursor.fetchall()}
    
    def sync_marketable_items(self, item_ids: List[int]) -> int:
        """Sync marketable item IDs to database.
        
        Args:
            item_ids: List of marketable item IDs
            
        Returns:
            Number of items synced
        """
        logger.info(f"Syncing {len(item_ids)} marketable items to database")
        with self._lock:
            cursor = self.conn.cursor()
            
            # Clear existing marketable items
            logger.debug("Clearing existing marketable_items table")
            cursor.execute("DELETE FROM marketable_items")
            
            # Bulk insert all marketable items
            count = 0
            for item_id in item_ids:
                try:
                    cursor.execute(
                        "INSERT INTO marketable_items (item_id) VALUES (?)",
                        (item_id,)
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to insert marketable item {item_id}: {e}")
                    continue
            
            self.conn.commit()
        logger.info(f"Successfully synced {count} marketable items")
        return count
    
    def get_marketable_items_count(self) -> int:
        """Get total count of marketable items in database."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM marketable_items")
        return cursor.fetchone()['count']
    
    def save_datacenters_cache(self, datacenters: List[Dict]) -> int:
        """Save datacenters to cache.
        
        Args:
            datacenters: List of datacenter dicts with 'name', 'region', 'worlds' keys
            
        Returns:
            Number of datacenters cached
        """
        logger.info(f"Caching {len(datacenters)} datacenters")
        with self._lock:
            cursor = self.conn.cursor()
            
            # Clear existing cache
            cursor.execute("DELETE FROM cached_datacenters")
            
            # Insert all datacenters
            count = 0
            for dc in datacenters:
                try:
                    # Convert worlds list to JSON string
                    worlds_json = json.dumps(dc.get('worlds', []))
                    
                    cursor.execute(
                        """INSERT INTO cached_datacenters (name, region, worlds, last_updated)
                           VALUES (?, ?, ?, CURRENT_TIMESTAMP)""",
                        (dc.get('name'), dc.get('region'), worlds_json)
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to cache datacenter {dc.get('name')}: {e}")
                    continue
            
            self.conn.commit()
        logger.info(f"Successfully cached {count} datacenters")
        return count
    
    def get_datacenters_cache(self, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """Get cached datacenters if not stale.
        
        Args:
            max_age_hours: Maximum age of cache in hours (default 24)
            
        Returns:
            List of datacenters or None if cache is stale/empty
        """
        cursor = self.conn.cursor()
        
        # Check if cache exists and is fresh
        cursor.execute(
            """SELECT name, region, worlds, last_updated 
               FROM cached_datacenters 
               WHERE datetime(last_updated) > datetime('now', '-' || ? || ' hours')""",
            (max_age_hours,)
        )
        
        rows = cursor.fetchall()
        if not rows:
            logger.debug("Datacenter cache is empty or stale")
            return None
        
        # Convert back to list of dicts
        datacenters = []
        for row in rows:
            datacenters.append({
                'name': row['name'],
                'region': row['region'],
                'worlds': json.loads(row['worlds'])
            })
        
        logger.info(f"Retrieved {len(datacenters)} datacenters from cache")
        return datacenters
    
    def save_worlds_cache(self, worlds: List[Dict]) -> int:
        """Save worlds to cache.
        
        Args:
            worlds: List of world dicts with 'id' and 'name' keys
            
        Returns:
            Number of worlds cached
        """
        logger.info(f"Caching {len(worlds)} worlds")
        with self._lock:
            cursor = self.conn.cursor()
            
            # Clear existing cache
            cursor.execute("DELETE FROM cached_worlds")
            
            # Insert all worlds
            count = 0
            for world in worlds:
                try:
                    cursor.execute(
                        """INSERT INTO cached_worlds (world_id, world_name, last_updated)
                           VALUES (?, ?, CURRENT_TIMESTAMP)""",
                        (world.get('id'), world.get('name'))
                    )
                    count += 1
                except Exception as e:
                    logger.warning(f"Failed to cache world {world.get('name')}: {e}")
                    continue
            
            self.conn.commit()
        logger.info(f"Successfully cached {count} worlds")
        return count
    
    def get_worlds_cache(self, max_age_hours: int = 24) -> Optional[List[Dict]]:
        """Get cached worlds if not stale.
        
        Args:
            max_age_hours: Maximum age of cache in hours (default 24)
            
        Returns:
            List of worlds or None if cache is stale/empty
        """
        cursor = self.conn.cursor()
        
        # Check if cache exists and is fresh
        cursor.execute(
            """SELECT world_id, world_name, last_updated 
               FROM cached_worlds 
               WHERE datetime(last_updated) > datetime('now', '-' || ? || ' hours')""",
            (max_age_hours,)
        )
        
        rows = cursor.fetchall()
        if not rows:
            logger.debug("Worlds cache is empty or stale")
            return None
        
        # Convert back to list of dicts
        worlds = []
        for row in rows:
            worlds.append({
                'id': row['world_id'],
                'name': row['world_name']
            })
        
        logger.info(f"Retrieved {len(worlds)} worlds from cache")
        return worlds
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get status of all caches.
        
        Returns:
            Dict with cache counts and last update times
        """
        cursor = self.conn.cursor()
        
        # Datacenter cache status
        cursor.execute("SELECT COUNT(*) as count, MAX(last_updated) as last_updated FROM cached_datacenters")
        dc_row = cursor.fetchone()
        
        # Worlds cache status
        cursor.execute("SELECT COUNT(*) as count, MAX(last_updated) as last_updated FROM cached_worlds")
        worlds_row = cursor.fetchone()
        
        return {
            'datacenters': {
                'count': dc_row['count'],
                'last_updated': dc_row['last_updated']
            },
            'worlds': {
                'count': worlds_row['count'],
                'last_updated': worlds_row['last_updated']
            }
        }
    
    def get_current_prices_count(self, world_id: int = None) -> int:
        """Get count of current prices, optionally filtered by world.
        
        Args:
            world_id: Optional world ID to filter by
            
        Returns:
            Count of current price records
        """
        cursor = self.conn.cursor()
        if world_id:
            cursor.execute(
                "SELECT COUNT(*) as count FROM current_prices WHERE tracked_world_id = ?",
                (world_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) as count FROM current_prices")
        return cursor.fetchone()['count']
    
    def get_latest_current_price_timestamp(self, world_id: int = None) -> str:
        """Get the most recent fetched_at timestamp from current_prices.
        
        Args:
            world_id: Optional world ID to filter by
            
        Returns:
            ISO timestamp string or None if no data
        """
        cursor = self.conn.cursor()
        if world_id:
            cursor.execute(
                "SELECT MAX(fetched_at) as latest FROM current_prices WHERE tracked_world_id = ?",
                (world_id,)
            )
        else:
            cursor.execute("SELECT MAX(fetched_at) as latest FROM current_prices")
        row = cursor.fetchone()
        return row['latest'] if row else None
    
    def get_top_items_by_hq_velocity(self, world_id: int, limit: int = 10) -> List[Dict]:
        """Get top items by HQ daily sale velocity for a world.
        
        Args:
            world_id: World ID to query
            limit: Maximum number of items to return
            
        Returns:
            List of items with velocity and price data, ordered by HQ velocity desc
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                cp.item_id,
                i.name as item_name,
                cp.hq_world_daily_velocity,
                cp.hq_world_avg_price,
                cp.nq_region_daily_velocity,
                cp.nq_region_avg_price,
                cp.fetched_at,
                (cp.hq_world_daily_velocity * cp.hq_world_avg_price) as hq_gil_volume,
                (cp.nq_region_daily_velocity * cp.nq_region_avg_price) as nq_gil_volume
            FROM current_prices cp
            LEFT JOIN items i ON cp.item_id = i.item_id
            WHERE cp.tracked_world_id = ?
            AND strftime('%Y-%m-%d', cp.fetched_at) = strftime('%Y-%m-%d', 'now', 'localtime')
            AND cp.hq_world_daily_velocity IS NOT NULL
            ORDER BY cp.hq_world_daily_velocity DESC
            LIMIT ?
            """,
            (world_id, limit)
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def get_datacenter_gil_volume(self, world_id: int) -> Dict[str, Any]:
        """Get total gil volume for a datacenter (sum of all items for today).
        
        Args:
            world_id: World ID to query
            
        Returns:
            Dict with hq_volume, nq_volume, total_volume, item_count
        """
        cursor = self.conn.cursor()
        cursor.execute(
            """
            SELECT 
                SUM(hq_world_daily_velocity * hq_world_avg_price) as hq_volume,
                SUM(nq_region_daily_velocity * nq_region_avg_price) as nq_volume,
                COUNT(*) as item_count
            FROM current_prices
            WHERE tracked_world_id = ?
            AND strftime('%Y-%m-%d', fetched_at) = strftime('%Y-%m-%d', 'now', 'localtime')
            """,
            (world_id,)
        )
        row = cursor.fetchone()
        if row:
            hq = row['hq_volume'] or 0
            nq = row['nq_volume'] or 0
            return {
                'hq_volume': hq,
                'nq_volume': nq,
                'total_volume': hq + nq,
                'item_count': row['item_count']
            }
        return {'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0}

    def close(self):
        """Close database connection."""
        if self.conn:
            logger.debug(f"Closing database connection to {self.db_path}")
            self.conn.close()
            self.conn = None
            logger.debug("Database connection closed")
