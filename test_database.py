"""
Unit tests for the database layer.
"""

import pytest
import sqlite3
from datetime import datetime, timedelta
from database import MarketDatabase


@pytest.fixture
def db():
    """Create an in-memory database for testing."""
    database = MarketDatabase(":memory:")
    yield database
    database.close()


class TestMarketDatabase:
    """Test suite for MarketDatabase class."""
    
    def test_database_initialization(self, db):
        """Test that database schema is created correctly."""
        cursor = db.conn.cursor()
        
        # Check tracked_items table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='tracked_items'
        """)
        assert cursor.fetchone() is not None
        
        # Check daily_snapshots table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='daily_snapshots'
        """)
        assert cursor.fetchone() is not None
        
        # Check sales_history table exists
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='sales_history'
        """)
        assert cursor.fetchone() is not None
    
    def test_add_tracked_item(self, db):
        """Test adding an item to tracking list."""
        db.add_tracked_item(12345, "Behemoth")
        
        items = db.get_tracked_items("Behemoth")
        assert len(items) == 1
        assert items[0]['item_id'] == 12345
        assert items[0]['world'] == "Behemoth"
    
    def test_add_duplicate_tracked_item(self, db):
        """Test that duplicate items are ignored."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(12345, "Behemoth")
        
        items = db.get_tracked_items("Behemoth")
        assert len(items) == 1
    
    def test_add_same_item_different_worlds(self, db):
        """Test tracking same item on different worlds."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(12345, "Excalibur")
        
        behemoth_items = db.get_tracked_items("Behemoth")
        excalibur_items = db.get_tracked_items("Excalibur")
        
        assert len(behemoth_items) == 1
        assert len(excalibur_items) == 1
    
    def test_get_tracked_items_all_worlds(self, db):
        """Test getting tracked items from all worlds."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(67890, "Excalibur")
        
        all_items = db.get_tracked_items()
        assert len(all_items) == 2
    
    def test_get_tracked_items_specific_world(self, db):
        """Test filtering tracked items by world."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(67890, "Excalibur")
        
        behemoth_items = db.get_tracked_items("Behemoth")
        assert len(behemoth_items) == 1
        assert behemoth_items[0]['world'] == "Behemoth"
    
    def test_save_snapshot(self, db):
        """Test saving a market data snapshot."""
        db.add_tracked_item(12345, "Behemoth")
        
        market_data = {
            'averagePrice': 1000.5,
            'minPrice': 800,
            'maxPrice': 1200,
            'regularSaleVelocity': 5.5,
            'nqSaleVelocity': 3.0,
            'hqSaleVelocity': 2.5,
            'listings': [1, 2, 3],
            'lastUploadTime': 1234567890
        }
        
        db.save_snapshot(12345, "Behemoth", market_data)
        
        # Verify snapshot was saved
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM daily_snapshots 
            WHERE item_id = ? AND world = ?
        """, (12345, "Behemoth"))
        
        snapshot = cursor.fetchone()
        assert snapshot is not None
        assert snapshot['average_price'] == 1000.5
        assert snapshot['sale_velocity'] == 5.5
        assert snapshot['total_listings'] == 3
    
    def test_save_snapshot_updates_last_updated(self, db):
        """Test that saving snapshot updates last_updated timestamp."""
        db.add_tracked_item(12345, "Behemoth")
        
        # Get original timestamp
        items = db.get_tracked_items("Behemoth")
        original_timestamp = items[0]['last_updated']
        
        # Save snapshot
        market_data = {'averagePrice': 1000, 'regularSaleVelocity': 5.0, 'listings': []}
        db.save_snapshot(12345, "Behemoth", market_data)
        
        # Check timestamp was updated
        items = db.get_tracked_items("Behemoth")
        new_timestamp = items[0]['last_updated']
        assert new_timestamp >= original_timestamp
    
    def test_save_sales(self, db):
        """Test saving sales history entries."""
        db.add_tracked_item(12345, "Behemoth")
        
        sales_entries = [
            {
                'timestamp': 1234567890,
                'pricePerUnit': 1000,
                'quantity': 2,
                'hq': False,
                'buyerName': 'Buyer One'
            },
            {
                'timestamp': 1234567900,
                'pricePerUnit': 1200,
                'quantity': 1,
                'hq': True,
                'buyerName': 'Buyer Two'
            }
        ]
        
        db.save_sales(12345, "Behemoth", sales_entries)
        
        # Verify sales were saved
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT * FROM sales_history 
            WHERE item_id = ? AND world = ?
            ORDER BY sale_time
        """, (12345, "Behemoth"))
        
        sales = cursor.fetchall()
        assert len(sales) == 2
        assert sales[0]['price_per_unit'] == 1000
        assert sales[1]['price_per_unit'] == 1200
    
    def test_save_duplicate_sales(self, db):
        """Test that duplicate sales are not saved."""
        db.add_tracked_item(12345, "Behemoth")
        
        sales_entry = [{
            'timestamp': 1234567890,
            'pricePerUnit': 1000,
            'quantity': 2,
            'hq': False,
            'buyerName': 'Buyer'
        }]
        
        db.save_sales(12345, "Behemoth", sales_entry)
        db.save_sales(12345, "Behemoth", sales_entry)
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) as count FROM sales_history 
            WHERE item_id = ? AND world = ?
        """, (12345, "Behemoth"))
        
        count = cursor.fetchone()['count']
        assert count == 1
    
    def test_get_snapshots(self, db):
        """Test retrieving historical snapshots."""
        db.add_tracked_item(12345, "Behemoth")
        
        # Create snapshots for multiple days
        for i in range(5):
            market_data = {
                'averagePrice': 1000 + i * 100,
                'regularSaleVelocity': 5.0 + i,
                'listings': []
            }
            db.save_snapshot(12345, "Behemoth", market_data)
        
        snapshots = db.get_snapshots(12345, "Behemoth", days=30)
        assert len(snapshots) >= 1  # At least today's snapshot
    
    def test_get_snapshots_with_date_filter(self, db):
        """Test that get_snapshots respects date filter."""
        db.add_tracked_item(12345, "Behemoth")
        
        market_data = {'averagePrice': 1000, 'regularSaleVelocity': 5.0, 'listings': []}
        db.save_snapshot(12345, "Behemoth", market_data)
        
        # Get snapshots from last 0 days (should return empty or today only)
        snapshots = db.get_snapshots(12345, "Behemoth", days=0)
        assert len(snapshots) <= 1
    
    def test_get_top_volume_items(self, db):
        """Test getting top items by sale velocity."""
        # Add multiple items with different velocities
        items = [
            (12345, 10.0, 1000),
            (67890, 20.0, 2000),
            (11111, 5.0, 500)
        ]
        
        for item_id, velocity, price in items:
            db.add_tracked_item(item_id, "Behemoth")
            market_data = {
                'averagePrice': price,
                'regularSaleVelocity': velocity,
                'listings': []
            }
            db.save_snapshot(item_id, "Behemoth", market_data)
        
        top_items = db.get_top_volume_items("Behemoth", limit=2)
        
        assert len(top_items) == 2
        assert top_items[0]['item_id'] == 67890  # Highest velocity
        assert top_items[1]['item_id'] == 12345  # Second highest
    
    def test_get_top_volume_items_empty(self, db):
        """Test getting top items when no data exists."""
        top_items = db.get_top_volume_items("Behemoth", limit=10)
        assert len(top_items) == 0
    
    def test_context_manager(self):
        """Test database context manager."""
        with MarketDatabase(":memory:") as db:
            db.add_tracked_item(12345, "Behemoth")
            items = db.get_tracked_items()
            assert len(items) == 1
        
        # Connection should be closed after context
        assert db.conn is None
    
    def test_close(self, db):
        """Test closing database connection."""
        assert db.conn is not None
        db.close()
        assert db.conn is None
    
    def test_close_idempotent(self, db):
        """Test that closing twice doesn't cause errors."""
        db.close()
        db.close()  # Should not raise exception
        assert db.conn is None
