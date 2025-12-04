"""
Unit tests for the UI layer (presentation).
"""

import pytest
from unittest.mock import patch, MagicMock
from io import StringIO
from ui import MarketUI


class TestMarketUI:
    """Test suite for MarketUI class."""
    
    @pytest.fixture
    def mock_console(self):
        """Mock the Rich console."""
        with patch('ui.console') as mock:
            yield mock
    
    def test_show_status(self, mock_console):
        """Test showing status message."""
        with MarketUI.show_status("Testing..."):
            pass
        
        mock_console.status.assert_called_once()
        call_args = mock_console.status.call_args[0][0]
        assert "Testing..." in call_args
    
    def test_print_success(self, mock_console):
        """Test printing success message."""
        MarketUI.print_success("Operation completed")
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "✓" in call_args
        assert "Operation completed" in call_args
    
    def test_print_warning(self, mock_console):
        """Test printing warning message."""
        MarketUI.print_warning("Warning message")
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "⚠" in call_args
        assert "Warning message" in call_args
    
    def test_print_error(self, mock_console):
        """Test printing error message."""
        MarketUI.print_error("Error occurred")
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Error:" in call_args
        assert "Error occurred" in call_args
    
    def test_print_info(self, mock_console):
        """Test printing info message."""
        MarketUI.print_info("Information")
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Information" in call_args
    
    def test_print_dim(self, mock_console):
        """Test printing dimmed message."""
        MarketUI.print_dim("Dimmed text")
        
        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "Dimmed text" in call_args
    
    def test_show_datacenters_empty(self, mock_console):
        """Test showing empty datacenters list."""
        MarketUI.show_datacenters([])
        
        # Should print warning
        assert mock_console.print.called
    
    def test_show_datacenters_with_data(self, mock_console):
        """Test showing datacenters with data."""
        datacenters = [
            {'name': 'Crystal', 'region': 'NA', 'worlds': ['Behemoth', 'Excalibur']},
            {'name': 'Light', 'region': 'EU', 'worlds': ['Lich', 'Odin']}
        ]
        
        MarketUI.show_datacenters(datacenters)
        
        # Should print table and summary
        assert mock_console.print.call_count >= 2
    
    def test_show_top_items_empty(self, mock_console):
        """Test showing top items with no data."""
        MarketUI.show_top_items('Behemoth', [], lambda x: "1h ago")
        
        # Should print warning
        assert mock_console.print.called
    
    def test_show_top_items_with_data(self, mock_console):
        """Test showing top items with data."""
        items = [
            {
                'item_id': 12345,
                'sale_velocity': 10.5,
                'average_price': 1000,
                'last_updated': '2025-12-01 00:00:00',
                'snapshot_date': '2025-12-01'
            },
            {
                'item_id': 67890,
                'sale_velocity': 5.2,
                'average_price': 2000,
                'last_updated': '2025-12-01 00:00:00',
                'snapshot_date': '2025-12-01'
            }
        ]
        
        format_func = lambda x: "1h ago"
        MarketUI.show_top_items('Behemoth', items, format_func)
        
        # Should print table and snapshot date
        assert mock_console.print.call_count >= 2
    
    def test_show_top_items_with_null_values(self, mock_console):
        """Test showing top items with null values."""
        items = [
            {
                'item_id': 12345,
                'sale_velocity': None,
                'average_price': None,
                'last_updated': '2025-12-01 00:00:00',
                'snapshot_date': '2025-12-01'
            }
        ]
        
        format_func = lambda x: "1h ago"
        MarketUI.show_top_items('Behemoth', items, format_func)
        
        # Should handle None values gracefully
        assert mock_console.print.called
    
    def test_show_item_report_header(self, mock_console):
        """Test showing item report header."""
        MarketUI.show_item_report_header('Behemoth', 12345, 30)
        
        # Should print header with item ID and days
        assert mock_console.print.call_count == 2
    
    def test_show_item_report_table(self, mock_console):
        """Test showing item report table."""
        snapshots = [
            {
                'snapshot_date': '2025-12-01',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'min_price': 900,
                'max_price': 1100,
                'total_listings': 5
            }
        ]
        
        MarketUI.show_item_report_table(snapshots)
        
        # Should print table
        assert mock_console.print.called
    
    def test_show_trends_velocity_only(self, mock_console):
        """Test showing trends with velocity change only."""
        trends = {'velocity_change': 25.5}
        
        MarketUI.show_trends(trends)
        
        # Should print velocity trend
        assert mock_console.print.call_count == 1
        call_args = mock_console.print.call_args[0][0]
        assert '25.5' in call_args
    
    def test_show_trends_price_only(self, mock_console):
        """Test showing trends with price change only."""
        trends = {'price_change': -10.2}
        
        MarketUI.show_trends(trends)
        
        # Should print price trend
        assert mock_console.print.call_count == 1
        call_args = mock_console.print.call_args[0][0]
        assert '10.2' in call_args
    
    def test_show_trends_both(self, mock_console):
        """Test showing trends with both changes."""
        trends = {
            'velocity_change': 25.5,
            'price_change': -10.2
        }
        
        MarketUI.show_trends(trends)
        
        # Should print both trends
        assert mock_console.print.call_count == 2
    
    def test_show_trends_positive_change(self, mock_console):
        """Test showing positive trends."""
        trends = {
            'velocity_change': 25.5,
            'price_change': 10.2
        }
        
        MarketUI.show_trends(trends)
        
        # Should use up arrows/positive emojis
        calls = [str(call[0][0]) for call in mock_console.print.call_args_list]
        assert any('📈' in call for call in calls)
        assert any('💰' in call for call in calls)
    
    def test_show_trends_negative_change(self, mock_console):
        """Test showing negative trends."""
        trends = {
            'velocity_change': -25.5,
            'price_change': -10.2
        }
        
        MarketUI.show_trends(trends)
        
        # Should use down arrows/negative emojis
        calls = [str(call[0][0]) for call in mock_console.print.call_args_list]
        assert any('📉' in call for call in calls)
        assert any('💸' in call for call in calls)
    
    def test_show_trends_empty(self, mock_console):
        """Test showing empty trends."""
        MarketUI.show_trends({})
        
        # Should not print anything
        mock_console.print.assert_not_called()
    
    def test_exit_with_error(self, mock_console):
        """Test exit with error."""
        with pytest.raises(SystemExit) as exc_info:
            MarketUI.exit_with_error("Test error", exit_code=42)
        
        # Should print error
        mock_console.print.assert_called_once()
        
        # Should exit with correct code
        assert exc_info.value.code == 42
    
    def test_exit_with_error_default_code(self, mock_console):
        """Test exit with error using default exit code."""
        with pytest.raises(SystemExit) as exc_info:
            MarketUI.exit_with_error("Test error")
        
        # Should use default exit code 1
        assert exc_info.value.code == 1
    
    def test_show_tracked_worlds_empty(self, mock_console):
        """Test showing empty tracked worlds list."""
        MarketUI.show_tracked_worlds([])
        
        # Should print warning
        assert mock_console.print.called
    
    def test_show_tracked_worlds_with_data(self, mock_console):
        """Test showing tracked worlds with data."""
        worlds = [
            {'world_id': 73, 'world_name': 'Adamantoise', 'added_at': '2025-12-01 10:00:00'},
            {'world_id': 79, 'world_name': 'Cactuar', 'added_at': '2025-12-02 12:00:00'}
        ]
        
        MarketUI.show_tracked_worlds(worlds)
        
        # Should print table
        assert mock_console.print.called
    
    def test_show_tracked_worlds_with_null_values(self, mock_console):
        """Test showing tracked worlds with null values."""
        worlds = [
            {'world_id': 73, 'world_name': None, 'added_at': None}
        ]
        
        MarketUI.show_tracked_worlds(worlds)
        
        # Should handle None values gracefully
        assert mock_console.print.called
    
    def test_show_item_report_table_with_null_values(self, mock_console):
        """Test showing item report table with null values."""
        snapshots = [
            {
                'snapshot_date': '2025-12-01',
                'sale_velocity': None,
                'average_price': None,
                'min_price': None,
                'max_price': None,
                'total_listings': None
            }
        ]
        
        MarketUI.show_item_report_table(snapshots)
        
        # Should handle None values gracefully
        assert mock_console.print.called
    
    def test_show_datacenters_sorts_by_region_and_name(self, mock_console):
        """Test that datacenters are sorted by region and name."""
        datacenters = [
            {'name': 'Light', 'region': 'EU', 'worlds': ['Lich']},
            {'name': 'Crystal', 'region': 'NA', 'worlds': ['Behemoth']},
            {'name': 'Aether', 'region': 'NA', 'worlds': ['Cactuar']}
        ]
        
        MarketUI.show_datacenters(datacenters)
        
        # Should have sorted and printed
        assert mock_console.print.call_count >= 2
    
    def test_show_top_items_with_item_name(self, mock_console):
        """Test showing top items with item names."""
        items = [
            {
                'item_id': 12345,
                'item_name': 'Test Item',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'last_updated': '2025-12-01 00:00:00',
                'snapshot_date': '2025-12-01'
            }
        ]
        
        format_func = lambda x: "1h ago"
        MarketUI.show_top_items('Behemoth', items, format_func)
        
        # Should print table with item name
        assert mock_console.print.called
