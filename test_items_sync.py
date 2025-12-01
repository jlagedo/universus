"""
Tests for items sync functionality.
"""

import pytest
from unittest.mock import Mock, patch
from database import MarketDatabase
from api_client import UniversalisAPI
from service import MarketService


class TestItemsSync:
    """Test suite for items synchronization."""
    
    @pytest.fixture
    def db(self):
        """Create in-memory database for testing."""
        db = MarketDatabase(":memory:")
        yield db
        db.close()
    
    @pytest.fixture
    def api(self):
        """Create mock API client."""
        return Mock(spec=UniversalisAPI)
    
    @pytest.fixture
    def service(self, db, api):
        """Create service with test database and mock API."""
        return MarketService(db, api)
    
    def test_sync_items_creates_table(self, db):
        """Test that items table is created during initialization."""
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='items'
        """)
        result = cursor.fetchone()
        assert result is not None
        assert result['name'] == 'items'
    
    def test_sync_items_stores_data(self, db):
        """Test that sync_items stores item data correctly."""
        test_items = {
            "12345": {"en": "Test Item 1", "de": "German Name"},
            "67890": {"en": "Test Item 2", "fr": "French Name"},
            "11111": {"en": "Test Item 3"}
        }
        
        count = db.sync_items(test_items)
        
        assert count == 3
        assert db.get_items_count() == 3
        assert db.get_item_name(12345) == "Test Item 1"
        assert db.get_item_name(67890) == "Test Item 2"
        assert db.get_item_name(11111) == "Test Item 3"
    
    def test_sync_items_replaces_existing_data(self, db):
        """Test that sync_items replaces existing data."""
        # First sync
        first_items = {
            "100": {"en": "Old Item 1"},
            "200": {"en": "Old Item 2"}
        }
        db.sync_items(first_items)
        assert db.get_items_count() == 2
        
        # Second sync with different data
        second_items = {
            "300": {"en": "New Item 1"},
            "400": {"en": "New Item 2"},
            "500": {"en": "New Item 3"}
        }
        count = db.sync_items(second_items)
        
        assert count == 3
        assert db.get_items_count() == 3
        assert db.get_item_name(100) is None  # Old items removed
        assert db.get_item_name(200) is None
        assert db.get_item_name(300) == "New Item 1"  # New items present
        assert db.get_item_name(400) == "New Item 2"
        assert db.get_item_name(500) == "New Item 3"
    
    def test_sync_items_skips_invalid_ids(self, db):
        """Test that sync_items skips items with invalid IDs."""
        test_items = {
            "12345": {"en": "Valid Item"},
            "invalid": {"en": "Invalid ID"},
            "67890": {"en": "Another Valid Item"}
        }
        
        count = db.sync_items(test_items)
        
        # Should only store items with valid integer IDs
        assert count == 2
        assert db.get_items_count() == 2
    
    def test_sync_items_skips_empty_names(self, db):
        """Test that sync_items skips items without names."""
        test_items = {
            "100": {"en": "Has Name"},
            "200": {"en": ""},  # Empty name
            "300": {"de": "No English Name"},  # No 'en' field
            "400": {"en": "Another Name"}
        }
        
        count = db.sync_items(test_items)
        
        # Should only store items with non-empty English names
        assert count == 2
        assert db.get_item_name(100) == "Has Name"
        assert db.get_item_name(200) is None
        assert db.get_item_name(300) is None
        assert db.get_item_name(400) == "Another Name"
    
    def test_get_item_name_returns_none_for_missing(self, db):
        """Test that get_item_name returns None for non-existent items."""
        assert db.get_item_name(99999) is None
    
    def test_api_fetch_teamcraft_items(self):
        """Test that API client can fetch Teamcraft items."""
        api = UniversalisAPI()
        
        with patch.object(api.session, 'get') as mock_get:
            mock_response = Mock()
            mock_response.json.return_value = {
                "1000": {"en": "Item Name 1"},
                "2000": {"en": "Item Name 2"}
            }
            mock_response.raise_for_status = Mock()
            mock_get.return_value = mock_response
            
            result = api.fetch_teamcraft_items()
            
            assert len(result) == 2
            assert result["1000"]["en"] == "Item Name 1"
            assert result["2000"]["en"] == "Item Name 2"
            
            # Verify correct URL was called
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert "ffxiv-teamcraft" in call_args[0][0]
            assert "items.json" in call_args[0][0]
    
    def test_service_sync_items_database(self, service, api, db):
        """Test service layer sync_items_database method."""
        mock_items = {
            "5000": {"en": "Service Test Item 1"},
            "6000": {"en": "Service Test Item 2"}
        }
        api.fetch_teamcraft_items.return_value = mock_items
        
        count = service.sync_items_database()
        
        assert count == 2
        assert db.get_items_count() == 2
        assert db.get_item_name(5000) == "Service Test Item 1"
        assert db.get_item_name(6000) == "Service Test Item 2"
        api.fetch_teamcraft_items.assert_called_once()


class TestItemsIntegration:
    """Integration tests for items functionality."""
    
    @pytest.fixture
    def db(self):
        """Create in-memory database."""
        db = MarketDatabase(":memory:")
        yield db
        db.close()
    
    def test_items_table_schema(self, db):
        """Test that items table has correct schema."""
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(items)")
        columns = {row['name']: row['type'] for row in cursor.fetchall()}
        
        assert 'item_id' in columns
        assert 'name' in columns
        assert 'last_synced' in columns
        assert columns['item_id'] == 'INTEGER'
        assert columns['name'] == 'TEXT'
    
    def test_items_table_primary_key(self, db):
        """Test that item_id is the primary key."""
        cursor = db.conn.cursor()
        cursor.execute("PRAGMA table_info(items)")
        for row in cursor.fetchall():
            if row['name'] == 'item_id':
                assert row['pk'] == 1  # Primary key
                break
        else:
            pytest.fail("item_id column not found")
