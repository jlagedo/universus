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
    
    def test_get_tracked_items_count_empty(self, db):
        """Test getting tracked items count when empty."""
        count = db.get_tracked_items_count()
        assert count == 0
    
    def test_get_tracked_items_count_all(self, db):
        """Test getting total tracked items count."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(67890, "Behemoth")
        db.add_tracked_item(11111, "Excalibur")
        
        count = db.get_tracked_items_count()
        assert count == 3
    
    def test_get_tracked_items_count_by_world(self, db):
        """Test getting tracked items count filtered by world."""
        db.add_tracked_item(12345, "Behemoth")
        db.add_tracked_item(67890, "Behemoth")
        db.add_tracked_item(11111, "Excalibur")
        
        behemoth_count = db.get_tracked_items_count("Behemoth")
        excalibur_count = db.get_tracked_items_count("Excalibur")
        
        assert behemoth_count == 2
        assert excalibur_count == 1
    
    def test_datacenters_cache(self, db):
        """Test datacenter caching."""
        datacenters = [
            {'name': 'Aether', 'region': 'NA', 'worlds': [73, 79, 54]},
            {'name': 'Primal', 'region': 'NA', 'worlds': [35, 55, 64]}
        ]
        
        # Save to cache
        count = db.save_datacenters_cache(datacenters)
        assert count == 2
        
        # Retrieve from cache
        cached = db.get_datacenters_cache(max_age_hours=24)
        assert cached is not None
        assert len(cached) == 2
        assert cached[0]['name'] == 'Aether'
        assert cached[0]['region'] == 'NA'
        assert cached[0]['worlds'] == [73, 79, 54]
        assert cached[1]['name'] == 'Primal'
    
    def test_datacenters_cache_stale(self, db):
        """Test that stale cache returns None."""
        datacenters = [{'name': 'Aether', 'region': 'NA', 'worlds': [73]}]
        db.save_datacenters_cache(datacenters)
        
        # Try to get with 0 max age (should be stale)
        cached = db.get_datacenters_cache(max_age_hours=0)
        assert cached is None
    
    def test_worlds_cache(self, db):
        """Test world caching."""
        worlds = [
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'},
            {'id': 54, 'name': 'Faerie'}
        ]
        
        # Save to cache
        count = db.save_worlds_cache(worlds)
        assert count == 3
        
        # Retrieve from cache
        cached = db.get_worlds_cache(max_age_hours=24)
        assert cached is not None
        assert len(cached) == 3
        
        # Check all worlds are present (order may vary)
        cached_ids = {w['id'] for w in cached}
        cached_names = {w['name'] for w in cached}
        assert 73 in cached_ids
        assert 79 in cached_ids
        assert 54 in cached_ids
        assert 'Adamantoise' in cached_names
        assert 'Cactuar' in cached_names
        assert 'Faerie' in cached_names
    
    def test_worlds_cache_stale(self, db):
        """Test that stale world cache returns None."""
        worlds = [{'id': 73, 'name': 'Adamantoise'}]
        db.save_worlds_cache(worlds)
        
        # Try to get with 0 max age (should be stale)
        cached = db.get_worlds_cache(max_age_hours=0)
        assert cached is None
    
    def test_cache_status(self, db):
        """Test getting cache status."""
        # Initially empty
        status = db.get_cache_status()
        assert status['datacenters']['count'] == 0
        assert status['worlds']['count'] == 0
        
        # Add some data
        datacenters = [{'name': 'Aether', 'region': 'NA', 'worlds': [73]}]
        worlds = [{'id': 73, 'name': 'Adamantoise'}]
        
        db.save_datacenters_cache(datacenters)
        db.save_worlds_cache(worlds)
        
        # Check status
        status = db.get_cache_status()
        assert status['datacenters']['count'] == 1
        assert status['worlds']['count'] == 1
        assert status['datacenters']['last_updated'] is not None
        assert status['worlds']['last_updated'] is not None
    
    def test_get_current_prices_count(self, db):
        """Test counting current prices."""
        # Add tracked world
        db.add_tracked_world(73, 'Adamantoise')
        
        # Initially should be 0
        assert db.get_current_prices_count() == 0
        assert db.get_current_prices_count(73) == 0
        
        # Add some price data
        results = [
            {'itemId': 5, 'hq': {'dailySaleVelocity': {'world': {'quantity': 10.5}}, 
                                 'averageSalePrice': {'world': {'price': 1000}}}},
            {'itemId': 6, 'hq': {'dailySaleVelocity': {'world': {'quantity': 5.2}}, 
                                 'averageSalePrice': {'world': {'price': 2000}}}}
        ]
        db.save_aggregated_prices(73, results)
        
        # Check counts
        assert db.get_current_prices_count() == 2
        assert db.get_current_prices_count(73) == 2
        assert db.get_current_prices_count(999) == 0
    
    def test_get_latest_current_price_timestamp(self, db):
        """Test getting latest price timestamp."""
        # Add tracked world
        db.add_tracked_world(73, 'Adamantoise')
        
        # Initially should be None
        assert db.get_latest_current_price_timestamp() is None
        assert db.get_latest_current_price_timestamp(73) is None
        
        # Add price data
        results = [{'itemId': 5, 'hq': {}}]
        db.save_aggregated_prices(73, results)
        
        # Should have a timestamp
        timestamp = db.get_latest_current_price_timestamp()
        assert timestamp is not None
        assert db.get_latest_current_price_timestamp(73) is not None
    
    def test_get_top_items_by_hq_velocity(self, db):
        """Test getting top items by HQ velocity."""
        # Add tracked world
        db.add_tracked_world(73, 'Adamantoise')
        
        # Add items to the items table manually
        cursor = db.conn.cursor()
        cursor.execute("INSERT OR IGNORE INTO items (item_id, name) VALUES (?, ?)", (5, 'High Velocity Item'))
        cursor.execute("INSERT OR IGNORE INTO items (item_id, name) VALUES (?, ?)", (6, 'Low Velocity Item'))
        cursor.execute("INSERT OR IGNORE INTO items (item_id, name) VALUES (?, ?)", (7, 'Medium Velocity Item'))
        db.conn.commit()
        
        # Add price data with different velocities
        results = [
            {'itemId': 5, 'hq': {'dailySaleVelocity': {'world': {'quantity': 100.5}}, 
                                 'averageSalePrice': {'world': {'price': 5000}}}},
            {'itemId': 6, 'hq': {'dailySaleVelocity': {'world': {'quantity': 5.2}}, 
                                 'averageSalePrice': {'world': {'price': 2000}}}},
            {'itemId': 7, 'hq': {'dailySaleVelocity': {'world': {'quantity': 50.0}}, 
                                 'averageSalePrice': {'world': {'price': 3000}}}}
        ]
        db.save_aggregated_prices(73, results)
        
        # Get top 2 items
        top_items = db.get_top_items_by_hq_velocity(73, limit=2)
        
        assert len(top_items) == 2
        # Should be ordered by velocity descending
        assert top_items[0]['item_id'] == 5
        assert top_items[0]['hq_world_daily_velocity'] == 100.5
        assert top_items[1]['item_id'] == 7
        assert top_items[1]['hq_world_daily_velocity'] == 50.0
        
        # Check calculated gil volume
        assert top_items[0]['hq_gil_volume'] == 100.5 * 5000
        assert top_items[1]['hq_gil_volume'] == 50.0 * 3000
    
    def test_get_datacenter_gil_volume(self, db):
        """Test getting datacenter gil volume."""
        # Add tracked world
        db.add_tracked_world(73, 'Adamantoise')
        
        # Initially should be zeros
        volume = db.get_datacenter_gil_volume(73)
        assert volume['hq_volume'] == 0
        assert volume['nq_volume'] == 0
        assert volume['total_volume'] == 0
        assert volume['item_count'] == 0
        
        # Add price data - note that NQ only has region-level data in the schema
        results = [
            {'itemId': 5, 
             'hq': {'dailySaleVelocity': {'world': {'quantity': 10.0}}, 
                    'averageSalePrice': {'world': {'price': 1000}}},
             'nq': {'dailySaleVelocity': {'region': {'quantity': 20.0}}, 
                    'averageSalePrice': {'region': {'price': 500}}}},
            {'itemId': 6, 
             'hq': {'dailySaleVelocity': {'world': {'quantity': 5.0}}, 
                    'averageSalePrice': {'world': {'price': 2000}}},
             'nq': {'dailySaleVelocity': {'region': {'quantity': 15.0}}, 
                    'averageSalePrice': {'region': {'price': 800}}}}
        ]
        db.save_aggregated_prices(73, results)
        
        # Check volumes
        volume = db.get_datacenter_gil_volume(73)
        
        # HQ: (10*1000) + (5*2000) = 20,000
        assert volume['hq_volume'] == 20000
        # NQ: (20*500) + (15*800) = 22,000
        assert volume['nq_volume'] == 22000
        # Total: 42,000
        assert volume['total_volume'] == 42000
        assert volume['item_count'] == 2

    def test_save_aggregated_prices_full_response(self, db):
        """Test saving complete aggregated price data matching API response structure."""
        # Add tracked world
        db.add_tracked_world(73, 'Adamantoise')
        
        # Full response structure matching the sample JSON
        results = [{
            'itemId': 47197,
            'nq': {
                'minListing': {
                    'dc': {'price': 120000, 'worldId': 64},
                    'region': {'price': 60000, 'worldId': 63}
                },
                'recentPurchase': {
                    'world': {'price': 99993, 'timestamp': 1764457198000},
                    'dc': {'price': 100000, 'timestamp': 1764638706000, 'worldId': 35},
                    'region': {'price': 99296, 'timestamp': 1764696778000, 'worldId': 62}
                },
                'averageSalePrice': {
                    'dc': {'price': 116664},
                    'region': {'price': 139697.25}
                },
                'dailySaleVelocity': {
                    'dc': {'quantity': 0.7547735840948842},
                    'region': {'quantity': 2.0127295537351353}
                }
            },
            'hq': {
                'minListing': {
                    'world': {'price': 199868},
                    'dc': {'price': 174900, 'worldId': 95},
                    'region': {'price': 129998, 'worldId': 63}
                },
                'recentPurchase': {
                    'world': {'price': 199879, 'timestamp': 1764741789000},
                    'dc': {'price': 169900, 'timestamp': 1764792412000, 'worldId': 95},
                    'region': {'price': 247870, 'timestamp': 1764800672000, 'worldId': 41}
                },
                'averageSalePrice': {
                    'world': {'price': 219357.625},
                    'dc': {'price': 348649.62790697673},
                    'region': {'price': 353121.26928104577}
                },
                'dailySaleVelocity': {
                    'world': {'quantity': 12.076377367067643},
                    'dc': {'quantity': 54.09210686013336},
                    'region': {'quantity': 192.46726357592232}
                }
            },
            'worldUploadTimes': [
                {'worldId': 78, 'timestamp': 1764787086201},
                {'worldId': 64, 'timestamp': 1764749804882},
                {'worldId': 95, 'timestamp': 1764802094054},
                {'worldId': 63, 'timestamp': 1764801609357}
            ]
        }]
        
        db.save_aggregated_prices(73, results)
        
        # Verify the record was saved
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM current_prices WHERE item_id = 47197 AND tracked_world_id = 73")
        row = cursor.fetchone()
        
        assert row is not None
        assert row['item_id'] == 47197
        assert row['tracked_world_id'] == 73
        
        # NQ fields
        assert row['nq_dc_min_price'] == 120000
        assert row['nq_dc_min_world_id'] == 64
        assert row['nq_region_min_price'] == 60000
        assert row['nq_region_min_world_id'] == 63
        assert row['nq_world_recent_price'] == 99993
        assert row['nq_world_recent_timestamp'] == 1764457198000
        assert row['nq_dc_recent_price'] == 100000
        assert row['nq_dc_recent_timestamp'] == 1764638706000
        assert row['nq_dc_recent_world_id'] == 35
        assert row['nq_dc_avg_price'] == 116664
        assert abs(row['nq_region_avg_price'] - 139697.25) < 0.01
        assert abs(row['nq_dc_daily_velocity'] - 0.7547735840948842) < 0.0001
        assert abs(row['nq_region_daily_velocity'] - 2.0127295537351353) < 0.0001
        
        # HQ fields
        assert row['hq_world_min_price'] == 199868
        assert row['hq_dc_min_price'] == 174900
        assert row['hq_dc_min_world_id'] == 95
        assert row['hq_region_min_price'] == 129998
        assert row['hq_region_min_world_id'] == 63
        assert row['hq_world_recent_price'] == 199879
        assert row['hq_world_recent_timestamp'] == 1764741789000
        assert row['hq_dc_recent_price'] == 169900
        assert row['hq_dc_recent_timestamp'] == 1764792412000
        assert row['hq_dc_recent_world_id'] == 95
        assert abs(row['hq_world_avg_price'] - 219357.625) < 0.01
        assert abs(row['hq_dc_avg_price'] - 348649.62790697673) < 0.01
        assert abs(row['hq_world_daily_velocity'] - 12.076377367067643) < 0.0001
        assert abs(row['hq_dc_daily_velocity'] - 54.09210686013336) < 0.0001
        assert abs(row['hq_region_daily_velocity'] - 192.46726357592232) < 0.0001
        
        # Verify world upload times were saved
        price_id = row['id']
        upload_times = db.get_world_upload_times(price_id)
        assert len(upload_times) == 4
        
        # Check all upload times are present
        upload_world_ids = {ut['worldId'] for ut in upload_times}
        assert upload_world_ids == {78, 64, 95, 63}

    def test_save_aggregated_prices_skips_missing_item_id(self, db):
        """Test that records without itemId are skipped."""
        db.add_tracked_world(73, 'Adamantoise')
        
        results = [
            {'nq': {}, 'hq': {}},  # No itemId
            {'itemId': 100, 'nq': {}, 'hq': {}}
        ]
        db.save_aggregated_prices(73, results)
        
        # Only one record should be saved
        assert db.get_current_prices_count(73) == 1

    def test_world_upload_times_table_exists(self, db):
        """Test that world_upload_times table is created."""
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='world_upload_times'
        """)
        assert cursor.fetchone() is not None

    def test_get_world_upload_times_empty(self, db):
        """Test getting world upload times for non-existent record."""
        upload_times = db.get_world_upload_times(99999)
        assert upload_times == []


class TestTrackedWorlds:
    """Test suite for tracked worlds functionality."""
    
    def test_add_tracked_world(self, db):
        """Test adding a tracked world."""
        result = db.add_tracked_world(73, 'Adamantoise')
        assert result is True
        
        worlds = db.list_tracked_worlds()
        assert len(worlds) == 1
        assert worlds[0]['world_id'] == 73
        assert worlds[0]['world_name'] == 'Adamantoise'
    
    def test_add_duplicate_tracked_world(self, db):
        """Test that duplicate tracked worlds are ignored."""
        db.add_tracked_world(73, 'Adamantoise')
        result = db.add_tracked_world(73, 'Adamantoise')
        
        assert result is False
        worlds = db.list_tracked_worlds()
        assert len(worlds) == 1
    
    def test_remove_tracked_world(self, db):
        """Test removing a tracked world."""
        db.add_tracked_world(73, 'Adamantoise')
        db.add_tracked_world(79, 'Cactuar')
        
        result = db.remove_tracked_world(73)
        
        assert result is True
        worlds = db.list_tracked_worlds()
        assert len(worlds) == 1
        assert worlds[0]['world_id'] == 79
    
    def test_remove_nonexistent_tracked_world(self, db):
        """Test removing a world that doesn't exist."""
        result = db.remove_tracked_world(99999)
        
        assert result is False
    
    def test_list_tracked_worlds_sorted(self, db):
        """Test that tracked worlds are sorted by name."""
        db.add_tracked_world(79, 'Cactuar')
        db.add_tracked_world(73, 'Adamantoise')
        db.add_tracked_world(54, 'Behemoth')
        
        worlds = db.list_tracked_worlds()
        
        assert len(worlds) == 3
        assert worlds[0]['world_name'] == 'Adamantoise'
        assert worlds[1]['world_name'] == 'Behemoth'
        assert worlds[2]['world_name'] == 'Cactuar'
    
    def test_clear_tracked_worlds(self, db):
        """Test clearing all tracked worlds."""
        db.add_tracked_world(73, 'Adamantoise')
        db.add_tracked_world(79, 'Cactuar')
        
        db.clear_tracked_worlds()
        
        worlds = db.list_tracked_worlds()
        assert len(worlds) == 0
    
    def test_get_tracked_worlds_count(self, db):
        """Test getting tracked worlds count."""
        assert db.get_tracked_worlds_count() == 0
        
        db.add_tracked_world(73, 'Adamantoise')
        db.add_tracked_world(79, 'Cactuar')
        
        assert db.get_tracked_worlds_count() == 2


class TestMarketableItems:
    """Test suite for marketable items functionality."""
    
    def test_sync_marketable_items(self, db):
        """Test syncing marketable items."""
        item_ids = [5, 6, 7, 8, 9]
        count = db.sync_marketable_items(item_ids)
        
        assert count == 5
        
        # Verify items were saved
        stored = db.get_marketable_item_ids()
        assert len(stored) == 5
        assert set(stored) == set(item_ids)
    
    def test_sync_marketable_items_replaces_existing(self, db):
        """Test that syncing replaces existing items."""
        db.sync_marketable_items([1, 2, 3])
        db.sync_marketable_items([4, 5])
        
        stored = db.get_marketable_item_ids()
        assert len(stored) == 2
        assert set(stored) == {4, 5}
    
    def test_get_marketable_items_count(self, db):
        """Test getting marketable items count."""
        assert db.get_marketable_items_count() == 0
        
        db.sync_marketable_items([1, 2, 3, 4, 5])
        
        assert db.get_marketable_items_count() == 5


class TestItemsSync:
    """Test suite for items sync functionality."""
    
    def test_sync_items(self, db):
        """Test syncing items from Teamcraft data."""
        items_data = {
            '5': {'en': 'Item 5'},
            '6': {'en': 'Item 6'},
            '7': {'en': 'Item 7'}
        }
        
        count = db.sync_items(items_data)
        
        assert count == 3
    
    def test_sync_items_skips_empty_names(self, db):
        """Test that items with empty names are skipped."""
        items_data = {
            '5': {'en': 'Item 5'},
            '6': {'en': ''},  # Empty name
            '7': {}  # No 'en' key
        }
        
        count = db.sync_items(items_data)
        
        assert count == 1
    
    def test_sync_items_skips_invalid_ids(self, db):
        """Test that items with invalid IDs are skipped."""
        items_data = {
            '5': {'en': 'Item 5'},
            'invalid': {'en': 'Invalid Item'},
            '': {'en': 'Empty ID'}
        }
        
        count = db.sync_items(items_data)
        
        assert count == 1
    
    def test_get_item_name(self, db):
        """Test getting item name by ID."""
        db.sync_items({'5': {'en': 'Test Item'}})
        
        name = db.get_item_name(5)
        
        assert name == 'Test Item'
    
    def test_get_item_name_not_found(self, db):
        """Test getting item name when not found."""
        name = db.get_item_name(99999)
        
        assert name is None
    
    def test_get_items_count(self, db):
        """Test getting items count."""
        assert db.get_items_count() == 0
        
        db.sync_items({'5': {'en': 'Item 5'}, '6': {'en': 'Item 6'}})
        
        assert db.get_items_count() == 2


class TestItemsUpdatedToday:
    """Test suite for items updated today functionality."""
    
    def test_get_items_updated_today_empty(self, db):
        """Test getting items updated today when none exist."""
        db.add_tracked_world(73, 'Adamantoise')
        
        updated = db.get_items_updated_today(73)
        
        assert updated == set()
    
    def test_get_items_updated_today(self, db):
        """Test getting items updated today."""
        db.add_tracked_world(73, 'Adamantoise')
        
        # Add some price data
        results = [
            {'itemId': 5, 'hq': {}, 'nq': {}},
            {'itemId': 6, 'hq': {}, 'nq': {}}
        ]
        db.save_aggregated_prices(73, results)
        
        updated = db.get_items_updated_today(73)
        
        assert updated == {5, 6}


class TestDatabaseEdgeCases:
    """Test edge cases in database operations."""
    
    def test_save_snapshot_with_empty_data(self, db):
        """Test saving snapshot with empty data."""
        db.add_tracked_item(12345, "Behemoth")
        
        # Empty data dict
        db.save_snapshot(12345, "Behemoth", {})
        
        # Should not raise error
        snapshots = db.get_snapshots(12345, "Behemoth", days=1)
        assert len(snapshots) == 1
    
    def test_save_sales_empty_list(self, db):
        """Test saving empty sales list."""
        db.add_tracked_item(12345, "Behemoth")
        
        db.save_sales(12345, "Behemoth", [])
        
        # Should not raise error
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM sales_history")
        count = cursor.fetchone()['count']
        assert count == 0
    
    def test_get_snapshots_no_data(self, db):
        """Test getting snapshots when no data exists."""
        snapshots = db.get_snapshots(99999, "NonExistentWorld", days=30)
        
        assert snapshots == []
    
    def test_save_aggregated_prices_empty_nested(self, db):
        """Test saving aggregated prices with empty nested objects."""
        db.add_tracked_world(73, 'Adamantoise')
        
        results = [{
            'itemId': 100,
            'hq': {},
            'nq': {}
        }]
        
        db.save_aggregated_prices(73, results)
        
        # Should save with null values
        assert db.get_current_prices_count(73) == 1
