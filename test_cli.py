"""
Unit tests for the CLI layer (universus.py).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
from universus import cli, __version__


class TestCLI:
    """Test suite for CLI commands."""
    
    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner."""
        return CliRunner()
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        db = Mock()
        db.get_tracked_items.return_value = []
        db.get_tracked_items_count.return_value = 0
        return db
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API client."""
        return Mock()
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        return Mock()
    
    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert 'Universus' in result.output
    
    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'FFXIV Market Price CLI' in result.output
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_datacenters_command(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test datacenters command."""
        mock_service = Mock()
        mock_service.get_datacenters.return_value = [
            {'name': 'Crystal', 'region': 'NA', 'worlds': ['Behemoth']},
            {'name': 'Light', 'region': 'EU', 'worlds': ['Lich']}
        ]
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['datacenters'])
        
        assert result.exit_code == 0
        mock_service.get_datacenters.assert_called_once()
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_datacenters_command_error(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test datacenters command with API error."""
        mock_service = Mock()
        mock_service.get_datacenters.side_effect = Exception("API Error")
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['datacenters'])
        
        # Should exit with error
        assert result.exit_code != 0
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_top_command(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test top command."""
        mock_service = Mock()
        mock_service.get_top_items.return_value = [
            {
                'item_id': 12345,
                'item_name': 'Test Item',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'last_updated': '2025-12-01 00:00:00',
                'snapshot_date': '2025-12-01'
            }
        ]
        mock_service.format_time_ago.return_value = "1h ago"
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['top', '--world', 'Behemoth', '--limit', '10'])
        
        assert result.exit_code == 0
        mock_service.get_top_items.assert_called_once_with('Behemoth', 10)
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_report_command(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test report command."""
        mock_service = Mock()
        mock_service.get_item_report.return_value = [
            {
                'snapshot_date': '2025-12-01',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'min_price': 900,
                'max_price': 1100,
                'total_listings': 5
            }
        ]
        mock_service.calculate_trends.return_value = {}
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['report', '--world', 'Behemoth', '--item-id', '12345', '--days', '30'])
        
        assert result.exit_code == 0
        mock_service.get_item_report.assert_called_once_with('Behemoth', 12345, 30)
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_report_command_no_data(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test report command with no data."""
        mock_service = Mock()
        mock_service.get_item_report.return_value = []
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['report', '--world', 'Behemoth', '--item-id', '12345'])
        
        assert result.exit_code == 0
        # Should print warning about no data
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_import_static_data_command(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test import-static-data command."""
        mock_service = Mock()
        mock_service.sync_items_database.return_value = 47000
        mock_service.sync_marketable_items.return_value = 30000
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['import-static-data'])
        
        assert result.exit_code == 0
        mock_service.sync_items_database.assert_called_once()
        mock_service.sync_marketable_items.assert_called_once()
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_import_static_data_alias(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test isd alias for import-static-data."""
        mock_service = Mock()
        mock_service.sync_items_database.return_value = 47000
        mock_service.sync_marketable_items.return_value = 30000
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['isd'])
        
        assert result.exit_code == 0
        mock_service.sync_items_database.assert_called_once()
        mock_service.sync_marketable_items.assert_called_once()
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_import_static_data_error(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test import-static-data command with error."""
        mock_service = Mock()
        mock_service.sync_items_database.side_effect = Exception("Network Error")
        mock_service_cls.return_value = mock_service
        mock_db_cls.return_value = Mock()
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['import-static-data'])
        
        # Should exit with error
        assert result.exit_code != 0
    
    def test_db_path_option(self, runner):
        """Test --db-path option is accepted."""
        result = runner.invoke(cli, ['--db-path', '/tmp/test.db', '--help'])
        assert result.exit_code == 0
    
    def test_verbose_option(self, runner):
        """Test --verbose option is accepted."""
        result = runner.invoke(cli, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    @patch('universus.MarketDatabase')
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_cleanup_called(self, mock_service_cls, mock_api_cls, mock_db_cls, runner):
        """Test that cleanup is called after command execution."""
        mock_db = Mock()
        mock_db_cls.return_value = mock_db
        
        mock_api = Mock()
        mock_api_cls.return_value = mock_api
        
        mock_service = Mock()
        mock_service.sync_items_database.return_value = 1000
        mock_service.sync_marketable_items.return_value = 500
        mock_service_cls.return_value = mock_service
        
        result = runner.invoke(cli, ['import-static-data'])
        
        # Verify cleanup was called
        mock_db.close.assert_called_once()
        mock_api.close.assert_called_once()


class TestDatabaseIntegration:
    """Integration tests for CLI with database."""
    
    @pytest.fixture
    def runner(self):
        """Create a Click CLI runner."""
        return CliRunner()
    
    @patch('universus.UniversalisAPI')
    @patch('universus.MarketService')
    def test_cli_with_memory_db(self, mock_service_cls, mock_api_cls, runner):
        """Test CLI with in-memory database."""
        mock_service = Mock()
        mock_service.sync_items_database.return_value = 1000
        mock_service.sync_marketable_items.return_value = 500
        mock_service_cls.return_value = mock_service
        mock_api_cls.return_value = Mock()
        
        result = runner.invoke(cli, ['--db-path', ':memory:', 'import-static-data'])
        
        assert result.exit_code == 0
