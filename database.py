"""
Database layer for market data storage and retrieval.
"""

import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict

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
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        logger.info(f"Initializing database at {self.db_path}")
        self.conn = sqlite3.connect(self.db_path)
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
        logger.debug(f"Saved {len(new_entries_data)} new sales entries (skipped {len(entries) - len(new_entries_data)} duplicates)")
    
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
    
    def close(self):
        """Close database connection."""
        if self.conn:
            logger.debug(f"Closing database connection to {self.db_path}")
            self.conn.close()
            self.conn = None
            logger.debug("Database connection closed")
