"""
Unit tests for the service layer (business logic).
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from service import MarketService


class TestMarketService:
    """Test suite for MarketService class."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return Mock()
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API client."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_db, mock_api):
        """Create service with mocked dependencies."""
        return MarketService(mock_db, mock_api)
    
    def test_initialization(self, mock_db, mock_api):
        """Test service initialization."""
        service = MarketService(mock_db, mock_api)
        assert service.db == mock_db
        assert service.api == mock_api
    
    def test_get_datacenters(self, service, mock_db, mock_api):
        """Test getting datacenters with cache."""
        expected_dcs = [
            {'name': 'Crystal', 'region': 'NA'},
            {'name': 'Light', 'region': 'EU'}
        ]
        
        # Test with empty cache (should fetch from API)
        mock_db.get_datacenters_cache.return_value = None
        mock_api.get_datacenters.return_value = expected_dcs
        
        result = service.get_datacenters()
        
        assert result == expected_dcs
        mock_api.get_datacenters.assert_called_once()
        mock_db.save_datacenters_cache.assert_called_once_with(expected_dcs)
        
        # Test with valid cache (should use cache, not API)
        mock_db.get_datacenters_cache.return_value = expected_dcs
        mock_api.reset_mock()
        mock_db.reset_mock()
        
        result = service.get_datacenters()
        
        assert result == expected_dcs
        mock_api.get_datacenters.assert_not_called()
        mock_db.save_datacenters_cache.assert_not_called()
        
        # Test with use_cache=False (should always fetch from API)
        mock_api.reset_mock()
        mock_db.reset_mock()
        
        result = service.get_datacenters(use_cache=False)
        
        assert result == expected_dcs
        mock_api.get_datacenters.assert_called_once()
        mock_db.save_datacenters_cache.assert_called_once()
    
    def test_initialize_tracking_success(self, service, mock_db, mock_api):
        """Test successful tracking initialization."""
        # Mock API responses
        mock_api.get_most_recently_updated.return_value = {
            'items': [
                {'itemID': 12345},
                {'itemID': 67890},
                {'itemID': 11111}
            ]
        }
        
        mock_api.get_market_data.side_effect = [
            {'regularSaleVelocity': 10.0, 'averagePrice': 1000},
            {'regularSaleVelocity': 5.0, 'averagePrice': 2000},
            {'regularSaleVelocity': 15.0, 'averagePrice': 500}
        ]
        
        top_items, total_found, items_with_sales = service.initialize_tracking('Behemoth', limit=50)
        
        # Verify results
        assert len(top_items) == 3
        assert total_found == 3
        assert items_with_sales == 3
        
        # Check items are sorted by velocity (descending)
        assert top_items[0]['item_id'] == 11111  # velocity 15.0
        assert top_items[1]['item_id'] == 12345  # velocity 10.0
        assert top_items[2]['item_id'] == 67890  # velocity 5.0
        
        # Verify database calls
        assert mock_db.add_tracked_item.call_count == 3
        mock_db.add_tracked_item.assert_any_call(12345, 'Behemoth')
        mock_db.add_tracked_item.assert_any_call(67890, 'Behemoth')
        mock_db.add_tracked_item.assert_any_call(11111, 'Behemoth')
    
    def test_initialize_tracking_no_items(self, service, mock_api):
        """Test initialization when no items found."""
        mock_api.get_most_recently_updated.return_value = {'items': []}
        
        top_items, total_found, items_with_sales = service.initialize_tracking('Behemoth', limit=50)
        
        assert top_items == []
        assert total_found == 0
        assert items_with_sales == 0
    
    def test_initialize_tracking_filters_zero_velocity(self, service, mock_db, mock_api):
        """Test that items with zero velocity are filtered out."""
        mock_api.get_most_recently_updated.return_value = {
            'items': [
                {'itemID': 12345},
                {'itemID': 67890}
            ]
        }
        
        mock_api.get_market_data.side_effect = [
            {'regularSaleVelocity': 10.0, 'averagePrice': 1000},
            {'regularSaleVelocity': 0, 'averagePrice': 2000}  # Zero velocity
        ]
        
        top_items, total_found, items_with_sales = service.initialize_tracking('Behemoth', limit=50)
        
        assert len(top_items) == 1
        assert top_items[0]['item_id'] == 12345
        assert mock_db.add_tracked_item.call_count == 1
    
    def test_initialize_tracking_handles_api_errors(self, service, mock_db, mock_api):
        """Test that API errors are handled gracefully."""
        import requests
        mock_api.get_most_recently_updated.return_value = {
            'items': [
                {'itemID': 12345},
                {'itemID': 67890}
            ]
        }
        
        # First call succeeds, second fails with network error
        mock_api.get_market_data.side_effect = [
            {'regularSaleVelocity': 10.0, 'averagePrice': 1000},
            requests.ConnectionError("Connection Error")
        ]
        
        top_items, total_found, items_with_sales = service.initialize_tracking('Behemoth', limit=50)
        
        # Should continue despite error
        assert len(top_items) == 1
        assert top_items[0]['item_id'] == 12345
    
    def test_update_tracked_items_success(self, service, mock_db, mock_api):
        """Test successful update of tracked items."""
        # Mock tracked items
        mock_db.get_tracked_items.return_value = [
            {'item_id': 12345, 'world': 'Behemoth'},
            {'item_id': 67890, 'world': 'Behemoth'}
        ]
        
        # Mock API responses
        market_data_1 = {'regularSaleVelocity': 10.0, 'averagePrice': 1000}
        market_data_2 = {'regularSaleVelocity': 5.0, 'averagePrice': 2000}
        mock_api.get_market_data.side_effect = [market_data_1, market_data_2]
        
        mock_api.get_history.side_effect = [
            {'entries': [{'timestamp': 123, 'pricePerUnit': 1000}]},
            {'entries': [{'timestamp': 456, 'pricePerUnit': 2000}]}
        ]
        
        successful, failed, tracked_items = service.update_tracked_items('Behemoth')
        
        assert successful == 2
        assert failed == 0
        assert len(tracked_items) == 2
        
        # Verify calls
        mock_db.save_snapshot.assert_any_call(12345, 'Behemoth', market_data_1)
        mock_db.save_sales.assert_called()
    
    def test_update_tracked_items_no_items(self, service, mock_db):
        """Test update when no items are tracked."""
        mock_db.get_tracked_items.return_value = []
        
        successful, failed, tracked_items = service.update_tracked_items('Behemoth')
        
        assert successful == 0
        assert failed == 0
        assert tracked_items == []
    
    def test_update_tracked_items_partial_failure(self, service, mock_db, mock_api):
        """Test update with some failures."""
        import requests
        mock_db.get_tracked_items.return_value = [
            {'item_id': 12345, 'world': 'Behemoth'},
            {'item_id': 67890, 'world': 'Behemoth'}
        ]
        
        # First succeeds, second fails with network error
        mock_api.get_market_data.side_effect = [
            {'regularSaleVelocity': 10.0, 'averagePrice': 1000},
            requests.ConnectionError("Connection Error")
        ]
        
        mock_api.get_history.return_value = {'entries': []}
        
        successful, failed, tracked_items = service.update_tracked_items('Behemoth')
        
        assert successful == 1
        assert failed == 1
    
    def test_update_tracked_items_no_history_entries(self, service, mock_db, mock_api):
        """Test update when history has no entries."""
        mock_db.get_tracked_items.return_value = [
            {'item_id': 12345, 'world': 'Behemoth'}
        ]
        
        mock_api.get_market_data.return_value = {'regularSaleVelocity': 10.0}
        mock_api.get_history.return_value = {}  # No 'entries' key
        
        successful, failed, tracked_items = service.update_tracked_items('Behemoth')
        
        assert successful == 1
        # save_sales should not be called
        mock_db.save_sales.assert_not_called()
    
    def test_get_top_items(self, service, mock_db):
        """Test getting top items."""
        expected_items = [
            {'item_id': 12345, 'velocity': 10.0},
            {'item_id': 67890, 'velocity': 5.0}
        ]
        mock_db.get_top_volume_items.return_value = expected_items
        
        result = service.get_top_items('Behemoth', limit=10)
        
        assert result == expected_items
        mock_db.get_top_volume_items.assert_called_once_with('Behemoth', 10)
    
    def test_get_item_report(self, service, mock_db):
        """Test getting item report."""
        expected_snapshots = [
            {'snapshot_date': '2025-12-01', 'sale_velocity': 10.0},
            {'snapshot_date': '2025-11-30', 'sale_velocity': 9.0}
        ]
        mock_db.get_snapshots.return_value = expected_snapshots
        
        result = service.get_item_report('Behemoth', 12345, days=30)
        
        assert result == expected_snapshots
        mock_db.get_snapshots.assert_called_once_with(12345, 'Behemoth', 30)
    
    def test_get_all_tracked_items(self, service, mock_db):
        """Test getting all tracked items grouped by world."""
        mock_db.get_tracked_items.return_value = [
            {'item_id': 12345, 'world': 'Behemoth'},
            {'item_id': 67890, 'world': 'Behemoth'},
            {'item_id': 11111, 'world': 'Excalibur'}
        ]
        
        result = service.get_all_tracked_items()
        
        assert 'Behemoth' in result
        assert 'Excalibur' in result
        assert len(result['Behemoth']) == 2
        assert len(result['Excalibur']) == 1
    
    def test_get_all_tracked_items_empty(self, service, mock_db):
        """Test getting tracked items when none exist."""
        mock_db.get_tracked_items.return_value = []
        
        result = service.get_all_tracked_items()
        
        assert result == {}
    
    def test_calculate_trends_with_data(self, service):
        """Test trend calculation with valid data."""
        snapshots = [
            {'sale_velocity': 10.0, 'average_price': 1000},  # Latest
            {'sale_velocity': 8.0, 'average_price': 900}     # Oldest
        ]
        
        trends = service.calculate_trends(snapshots)
        
        assert 'velocity_change' in trends
        assert 'price_change' in trends
        assert trends['velocity_change'] == pytest.approx(25.0)  # (10-8)/8 * 100
        assert trends['price_change'] == pytest.approx(11.111, rel=0.01)  # (1000-900)/900 * 100
    
    def test_calculate_trends_single_snapshot(self, service):
        """Test trend calculation with only one snapshot."""
        snapshots = [
            {'sale_velocity': 10.0, 'average_price': 1000}
        ]
        
        trends = service.calculate_trends(snapshots)
        
        assert trends == {}
    
    def test_calculate_trends_no_data(self, service):
        """Test trend calculation with empty data."""
        trends = service.calculate_trends([])
        assert trends == {}
    
    def test_calculate_trends_null_values(self, service):
        """Test trend calculation with null values."""
        snapshots = [
            {'sale_velocity': None, 'average_price': 1000},
            {'sale_velocity': 8.0, 'average_price': None}
        ]
        
        trends = service.calculate_trends(snapshots)
        
        # Should return empty dict when values are None
        assert 'velocity_change' not in trends
        assert 'price_change' not in trends
    
    def test_format_time_ago_days(self, service):
        """Test formatting time for days ago."""
        from datetime import timedelta
        timestamp_str = (datetime.now() - timedelta(days=3)).isoformat()
        
        result = service.format_time_ago(timestamp_str)
        
        assert 'd ago' in result
    
    def test_format_time_ago_hours(self, service):
        """Test formatting time for hours ago."""
        from datetime import timedelta
        timestamp_str = (datetime.now() - timedelta(hours=5)).isoformat()
        
        result = service.format_time_ago(timestamp_str)
        
        assert 'h ago' in result
    
    def test_format_time_ago_minutes(self, service):
        """Test formatting time for minutes ago."""
        from datetime import timedelta
        timestamp_str = (datetime.now() - timedelta(minutes=30)).isoformat()
        
        result = service.format_time_ago(timestamp_str)
        
        assert 'm ago' in result
    
    def test_format_time_ago_invalid(self, service):
        """Test formatting invalid timestamp."""
        result = service.format_time_ago("invalid")
        assert result == "Unknown"
    
    def test_format_time_ago_none(self, service):
        """Test formatting None timestamp."""
        result = service.format_time_ago(None)
        assert result == "Unknown"
    
    def test_get_available_worlds_with_cache(self, service, mock_db, mock_api):
        """Test getting worlds with cache."""
        expected_worlds = [
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'}
        ]
        
        # Test with empty cache
        mock_db.get_worlds_cache.return_value = None
        mock_api.get_worlds.return_value = expected_worlds
        
        result = service.get_available_worlds()
        
        assert result == expected_worlds
        mock_api.get_worlds.assert_called_once()
        mock_db.save_worlds_cache.assert_called_once_with(expected_worlds)
    
    def test_refresh_cache(self, service, mock_db, mock_api):
        """Test manual cache refresh."""
        datacenters = [{'name': 'Aether', 'region': 'NA'}]
        worlds = [{'id': 73, 'name': 'Adamantoise'}]
        
        mock_api.get_datacenters.return_value = datacenters
        mock_api.get_worlds.return_value = worlds
        mock_db.save_datacenters_cache.return_value = 1
        mock_db.save_worlds_cache.return_value = 1
        
        result = service.refresh_cache()
        
        assert result == {'datacenters': 1, 'worlds': 1}
        mock_api.get_datacenters.assert_called_once()
        mock_api.get_worlds.assert_called_once()
        mock_db.save_datacenters_cache.assert_called_once()
        mock_db.save_worlds_cache.assert_called_once()
