"""
Unit tests for the GUI module.
Tests all GUI features including views, actions, and user interactions.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime
import asyncio

# Mock nicegui before importing gui module
import sys
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.app'] = MagicMock()

from gui import UniversusGUI, format_gil, format_velocity, format_time_ago


class TestFormatFunctions:
    """Test suite for formatting utility functions."""
    
    def test_format_gil_valid_amount(self):
        """Test formatting gil with valid amount."""
        assert format_gil(1000) == "1,000"
        assert format_gil(1000000) == "1,000,000"
        assert format_gil(500) == "500"
        assert format_gil(0) == "0"
    
    def test_format_gil_float_amount(self):
        """Test formatting gil with float amount."""
        assert format_gil(1234.56) == "1,234"
        assert format_gil(999.99) == "999"
    
    def test_format_gil_none(self):
        """Test formatting gil with None."""
        assert format_gil(None) == "N/A"
    
    def test_format_velocity_valid(self):
        """Test formatting velocity with valid value."""
        assert format_velocity(10.5) == "10.50"
        assert format_velocity(0.5) == "0.50"
        assert format_velocity(100.123) == "100.12"
    
    def test_format_velocity_none(self):
        """Test formatting velocity with None."""
        assert format_velocity(None) == "N/A"
    
    def test_format_time_ago_days(self):
        """Test time ago formatting for days."""
        from datetime import timedelta
        past_time = datetime.now() - timedelta(days=5)
        result = format_time_ago(past_time.isoformat())
        assert "d ago" in result
    
    def test_format_time_ago_hours(self):
        """Test time ago formatting for hours."""
        from datetime import timedelta
        past_time = datetime.now() - timedelta(hours=5)
        result = format_time_ago(past_time.isoformat())
        assert "h ago" in result or "m ago" in result
    
    def test_format_time_ago_minutes(self):
        """Test time ago formatting for minutes."""
        from datetime import timedelta
        past_time = datetime.now() - timedelta(minutes=30)
        result = format_time_ago(past_time.isoformat())
        assert "m ago" in result
    
    def test_format_time_ago_empty(self):
        """Test time ago formatting with empty string."""
        assert format_time_ago("") == "Never"
    
    def test_format_time_ago_invalid(self):
        """Test time ago formatting with invalid timestamp."""
        assert format_time_ago("invalid") == "Unknown"


class TestUniversusGUIInitialization:
    """Test suite for UniversusGUI initialization."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    def test_initialization(self, gui_instance):
        """Test GUI initialization."""
        assert gui_instance.selected_datacenter == ""
        assert gui_instance.selected_world == ""
        assert gui_instance.worlds == []
        assert gui_instance.datacenters == []
        assert gui_instance.datacenter_names == []
        assert gui_instance.worlds_by_datacenter == {}
        assert gui_instance.world_id_to_name == {}
        assert gui_instance.world_name_to_id == {}
        assert gui_instance.current_view == "dashboard"
    
    def test_ui_components_initialized_as_none(self, gui_instance):
        """Test that UI components start as None."""
        assert gui_instance.status_label is None
        assert gui_instance.datacenter_select is None
        assert gui_instance.world_select is None
        assert gui_instance.main_content is None


class TestUniversusGUIDataLoading:
    """Test suite for GUI data loading functionality."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    @pytest.fixture
    def mock_api(self):
        """Create a mock API client."""
        mock = Mock()
        mock.get_worlds.return_value = [
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'},
            {'id': 54, 'name': 'Faerie'}
        ]
        return mock
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        mock = Mock()
        mock.get_datacenters.return_value = [
            {
                'name': 'Aether',
                'region': 'North-America',
                'worlds': [73, 79]
            },
            {
                'name': 'Primal',
                'region': 'North-America',
                'worlds': [54]
            }
        ]
        return mock
    
    @pytest.mark.asyncio
    async def test_load_datacenters_success(self, gui_instance, mock_api, mock_service):
        """Test successful datacenter loading."""
        # Create async mock for get_worlds_async
        async_api = Mock()
        async_api.get_worlds_async = AsyncMock(return_value=[
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'},
            {'id': 54, 'name': 'Faerie'}
        ])
        
        with patch('gui.api', async_api), patch('gui.service', mock_service):
            await gui_instance.load_datacenters()
        
        assert len(gui_instance.datacenters) == 2
        assert len(gui_instance.datacenter_names) == 2
        assert 'Aether' in gui_instance.datacenter_names
        assert 'Primal' in gui_instance.datacenter_names
        
        # Check world mappings
        assert gui_instance.world_id_to_name[73] == 'Adamantoise'
        assert gui_instance.world_id_to_name[79] == 'Cactuar'
        assert gui_instance.world_id_to_name[54] == 'Faerie'
        
        # Check worlds by datacenter
        assert set(gui_instance.worlds_by_datacenter['Aether']) == {'Adamantoise', 'Cactuar'}
        assert set(gui_instance.worlds_by_datacenter['Primal']) == {'Faerie'}
        
        # Check default selections
        assert gui_instance.selected_datacenter in gui_instance.datacenter_names
        assert gui_instance.selected_world in gui_instance.worlds
    
    @pytest.mark.asyncio
    async def test_load_datacenters_error_handling(self, gui_instance, mock_api):
        """Test datacenter loading error handling."""
        mock_api.get_worlds.side_effect = Exception("API Error")
        
        with patch('gui.api', mock_api), patch('gui.logger') as mock_logger:
            await gui_instance.load_datacenters()
        
        mock_logger.error.assert_called_once()
        assert len(gui_instance.datacenters) == 0


class TestUniversusGUIStatusAndNavigation:
    """Test suite for GUI status and navigation."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    def test_set_status_with_label(self, gui_instance):
        """Test setting status when label exists."""
        mock_label = Mock()
        gui_instance.status_label = mock_label
        
        gui_instance.set_status("Test message")
        
        mock_label.set_text.assert_called_once_with("Test message")
    
    def test_set_status_without_label(self, gui_instance):
        """Test setting status when label is None."""
        gui_instance.status_label = None
        
        # Should not raise an error
        gui_instance.set_status("Test message")
    
    def test_change_datacenter(self, gui_instance):
        """Test changing datacenter."""
        gui_instance.datacenter_names = ['Aether', 'Primal']
        gui_instance.worlds_by_datacenter = {
            'Aether': ['Adamantoise', 'Cactuar'],
            'Primal': ['Behemoth', 'Excalibur']
        }
        gui_instance.selected_world = 'Adamantoise'
        
        mock_world_select = Mock()
        mock_world_select.value = 'Adamantoise'
        gui_instance.world_select = mock_world_select
        
        # Mock show_view to avoid context manager issues
        with patch('gui.ui') as mock_ui, patch.object(gui_instance, 'show_view') as mock_show:
            gui_instance.change_datacenter('Primal')
        
        assert gui_instance.selected_datacenter == 'Primal'
        assert mock_world_select.options == ['Behemoth', 'Excalibur']
        mock_world_select.update.assert_called_once()
        mock_show.assert_called_once()
    
    def test_change_world(self, gui_instance):
        """Test changing world."""
        # Mock show_view to avoid context manager issues
        with patch('gui.ui') as mock_ui, patch.object(gui_instance, 'show_view') as mock_show:
            gui_instance.change_world('Cactuar')
        
        assert gui_instance.selected_world == 'Cactuar'
        mock_ui.notify.assert_called_once()
        mock_show.assert_called_once()


class TestUniversusGUIViews:
    """Test suite for GUI view rendering."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        # Create a mock that supports context manager protocol
        mock_content = MagicMock()
        mock_content.__enter__ = MagicMock(return_value=mock_content)
        mock_content.__exit__ = MagicMock(return_value=False)
        gui.main_content = mock_content
        gui.selected_world = 'Behemoth'
        gui.selected_datacenter = 'Primal'
        return gui
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        return Mock()
    
    def test_show_view_dashboard(self, gui_instance):
        """Test showing dashboard view."""
        with patch.object(gui_instance, 'render_dashboard') as mock_render:
            gui_instance.show_view('dashboard')
        
        assert gui_instance.current_view == 'dashboard'
        gui_instance.main_content.clear.assert_called_once()
        mock_render.assert_called_once()
    
    def test_show_view_datacenters(self, gui_instance):
        """Test showing datacenters view."""
        with patch.object(gui_instance, 'render_datacenters') as mock_render:
            gui_instance.show_view('datacenters')
        
        assert gui_instance.current_view == 'datacenters'
        mock_render.assert_called_once()
    
    def test_show_view_top_items(self, gui_instance):
        """Test showing top items view."""
        with patch.object(gui_instance, 'render_top_items') as mock_render:
            gui_instance.show_view('top')
        
        assert gui_instance.current_view == 'top'
        mock_render.assert_called_once()
    
    def test_show_view_tracked(self, gui_instance):
        """Test showing tracked items view."""
        with patch.object(gui_instance, 'render_tracked_items') as mock_render:
            gui_instance.show_view('tracked')
        
        assert gui_instance.current_view == 'tracked'
        mock_render.assert_called_once()
    
    def test_show_view_init_tracking(self, gui_instance):
        """Test showing init tracking view."""
        with patch.object(gui_instance, 'render_init_tracking') as mock_render:
            gui_instance.show_view('init_tracking')
        
        assert gui_instance.current_view == 'init_tracking'
        mock_render.assert_called_once()
    
    def test_show_view_update(self, gui_instance):
        """Test showing update view."""
        with patch.object(gui_instance, 'render_update') as mock_render:
            gui_instance.show_view('update')
        
        assert gui_instance.current_view == 'update'
        mock_render.assert_called_once()
    
    def test_show_view_report(self, gui_instance):
        """Test showing report view."""
        with patch.object(gui_instance, 'render_report') as mock_render:
            gui_instance.show_view('report')
        
        assert gui_instance.current_view == 'report'
        mock_render.assert_called_once()
    
    def test_show_view_sync_items(self, gui_instance):
        """Test showing sync items view."""
        with patch.object(gui_instance, 'render_sync_items') as mock_render:
            gui_instance.show_view('sync_items')
        
        assert gui_instance.current_view == 'sync_items'
        mock_render.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_refresh_current_view(self, gui_instance):
        """Test refreshing current view."""
        gui_instance.current_view = 'dashboard'
        
        with patch.object(gui_instance, 'show_view') as mock_show, patch('gui.ui') as mock_ui:
            await gui_instance.refresh_current_view()
        
        mock_show.assert_called_once_with('dashboard')
        mock_ui.notify.assert_called_once()


class TestDashboardRendering:
    """Test suite for dashboard rendering."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    def test_render_dashboard_with_world(self, gui_instance):
        """Test rendering dashboard with selected world."""
        mock_db = Mock()
        mock_db.get_tracked_items.return_value = [
            {'item_id': 123, 'item_name': 'Potion', 'world': 'Behemoth', 'last_updated': '2024-12-01T10:00:00'}
        ]
        mock_db.get_items_count.return_value = 47000
        
        with patch('gui.db', mock_db), patch('gui.ui') as mock_ui:
            gui_instance.render_dashboard()
        
        # Verify UI calls were made
        assert mock_ui.label.called
        mock_db.get_tracked_items.assert_called_once_with('Behemoth')
        mock_db.get_items_count.assert_called_once()
    
    def test_render_dashboard_without_world(self, gui_instance):
        """Test rendering dashboard without selected world."""
        gui_instance.selected_world = ""
        
        with patch('gui.ui') as mock_ui:
            gui_instance.render_dashboard()
        
        # Should display a message to select a world
        assert mock_ui.label.called
    
    def test_stat_card(self, gui_instance):
        """Test stat card creation."""
        with patch('gui.ui') as mock_ui:
            gui_instance._stat_card('Test', '100', 'icon', 'blue')
        
        assert mock_ui.card.called
        assert mock_ui.label.called
        assert mock_ui.icon.called


class TestDatacentersView:
    """Test suite for datacenters view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.datacenters = [
            {'name': 'Aether', 'region': 'NA', 'worlds': [73, 79]},
            {'name': 'Primal', 'region': 'NA', 'worlds': [54]}
        ]
        gui.world_id_to_name = {73: 'Adamantoise', 79: 'Cactuar', 54: 'Faerie'}
        return gui
    
    def test_render_datacenters_with_data(self, gui_instance):
        """Test rendering datacenters view with data."""
        with patch('gui.ui') as mock_ui:
            gui_instance.render_datacenters()
        
        assert mock_ui.label.called
    
    def test_render_datacenters_table(self, gui_instance):
        """Test rendering datacenters table."""
        with patch('gui.ui') as mock_ui:
            gui_instance._render_datacenters_table()
        
        assert mock_ui.table.called
        assert mock_ui.label.called
    
    def test_render_datacenters_table_empty(self):
        """Test rendering empty datacenters table."""
        gui = UniversusGUI()
        gui.datacenters = []
        
        with patch('gui.ui') as mock_ui:
            gui._render_datacenters_table()
        
        # Should show "No datacenters loaded" message
        assert mock_ui.label.called


class TestTopItemsView:
    """Test suite for top items view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    def test_render_top_items_with_world(self, gui_instance):
        """Test rendering top items view with selected world."""
        with patch('gui.ui') as mock_ui:
            gui_instance.render_top_items()
        
        assert mock_ui.label.called
        assert mock_ui.number.called
        assert mock_ui.button.called
    
    def test_render_top_items_without_world(self):
        """Test rendering top items view without selected world."""
        gui = UniversusGUI()
        gui.selected_world = ""
        
        with patch('gui.ui') as mock_ui:
            gui.render_top_items()
        
        # Should display message to select world
        assert mock_ui.label.called
    
    def test_render_top_items_table_with_data(self, gui_instance):
        """Test rendering top items table with data."""
        items = [
            {
                'item_id': 123,
                'item_name': 'Potion',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'last_updated': '2024-12-01T10:00:00',
                'snapshot_date': '2024-12-01'
            }
        ]
        
        # Create a mock that supports context manager protocol
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        gui_instance.top_items_container = mock_container
        
        with patch('gui.ui') as mock_ui:
            gui_instance._render_top_items_table(items)
        
        gui_instance.top_items_container.clear.assert_called_once()
    
    def test_render_top_items_table_empty(self, gui_instance):
        """Test rendering top items table with no data."""
        # Create a mock that supports context manager protocol
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        gui_instance.top_items_container = mock_container
        
        with patch('gui.ui') as mock_ui:
            gui_instance._render_top_items_table([])
        
        gui_instance.top_items_container.clear.assert_called_once()


class TestTrackedItemsView:
    """Test suite for tracked items view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        mock = Mock()
        mock.get_all_tracked_items.return_value = {
            'Behemoth': [
                {'item_id': 123, 'item_name': 'Potion', 'first_tracked': '2024-01-01', 'last_updated': '2024-12-01T10:00:00'}
            ]
        }
        return mock
    
    def test_render_tracked_items_with_data(self, gui_instance, mock_service):
        """Test rendering tracked items view with data."""
        with patch('gui.service', mock_service), patch('gui.ui') as mock_ui:
            gui_instance.render_tracked_items()
        
        assert mock_ui.label.called
        mock_service.get_all_tracked_items.assert_called_once()
    
    def test_render_tracked_items_empty(self, gui_instance):
        """Test rendering tracked items view with no data."""
        mock_service = Mock()
        mock_service.get_all_tracked_items.return_value = {}
        
        with patch('gui.service', mock_service), patch('gui.ui') as mock_ui:
            gui_instance.render_tracked_items()
        
        # Should display "No items being tracked" message
        assert mock_ui.card.called
        assert mock_ui.label.called


class TestInitTrackingView:
    """Test suite for init tracking view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        mock = Mock()
        mock.get.return_value = 50
        return mock
    
    def test_render_init_tracking_with_world(self, gui_instance, mock_config):
        """Test rendering init tracking view with selected world."""
        with patch('gui.config', mock_config), patch('gui.ui') as mock_ui:
            gui_instance.render_init_tracking()
        
        assert mock_ui.label.called
        assert mock_ui.card.called
        assert mock_ui.number.called
        assert mock_ui.button.called
    
    def test_render_init_tracking_without_world(self):
        """Test rendering init tracking view without selected world."""
        gui = UniversusGUI()
        gui.selected_world = ""
        
        with patch('gui.ui') as mock_ui:
            gui.render_init_tracking()
        
        # Should display message to select world
        assert mock_ui.label.called


class TestUpdateView:
    """Test suite for update view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = Mock()
        mock.get_tracked_items_count.return_value = 50
        return mock
    
    def test_render_update_with_world(self, gui_instance, mock_db):
        """Test rendering update view with selected world."""
        with patch('gui.db', mock_db), patch('gui.ui') as mock_ui:
            gui_instance.render_update()
        
        assert mock_ui.label.called
        assert mock_ui.card.called
        mock_db.get_tracked_items_count.assert_called_once_with('Behemoth')
    
    def test_render_update_without_world(self):
        """Test rendering update view without selected world."""
        gui = UniversusGUI()
        gui.selected_world = ""
        
        with patch('gui.ui') as mock_ui:
            gui.render_update()
        
        # Should display message to select world
        assert mock_ui.label.called
    
    def test_render_update_no_tracked_items(self, gui_instance):
        """Test rendering update view with no tracked items."""
        mock_db = Mock()
        mock_db.get_tracked_items_count.return_value = 0
        
        with patch('gui.db', mock_db), patch('gui.ui') as mock_ui:
            gui_instance.render_update()
        
        # Should display message about no tracked items
        assert mock_ui.label.called


class TestReportView:
    """Test suite for report view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock config."""
        mock = Mock()
        mock.get.return_value = 30
        return mock
    
    def test_render_report_with_world(self, gui_instance, mock_config):
        """Test rendering report view with selected world."""
        with patch('gui.config', mock_config), patch('gui.ui') as mock_ui:
            gui_instance.render_report()
        
        assert mock_ui.label.called
        assert mock_ui.card.called
        assert mock_ui.number.called
        assert mock_ui.button.called
    
    def test_render_report_without_world(self):
        """Test rendering report view without selected world."""
        gui = UniversusGUI()
        gui.selected_world = ""
        
        with patch('gui.ui') as mock_ui:
            gui.render_report()
        
        # Should display message to select world
        assert mock_ui.label.called


class TestSyncItemsView:
    """Test suite for sync items view."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database."""
        mock = Mock()
        mock.get_items_count.return_value = 47000
        return mock
    
    def test_render_sync_items(self, gui_instance, mock_db):
        """Test rendering sync items view."""
        with patch('gui.db', mock_db), patch('gui.ui') as mock_ui:
            gui_instance.render_sync_items()
        
        assert mock_ui.label.called
        assert mock_ui.card.called
        assert mock_ui.button.called
        mock_db.get_items_count.assert_called_once()


class TestAsyncOperations:
    """Test suite for async operations in GUI."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        gui.datacenter_names = ['Aether', 'Primal']
        gui.worlds = ['Behemoth', 'Cactuar']
        gui.datacenter_select = Mock()
        gui.world_select = Mock()
        return gui
    
    @pytest.mark.asyncio
    async def test_initialize(self, gui_instance):
        """Test GUI initialization."""
        with patch.object(gui_instance, 'load_datacenters', new_callable=AsyncMock) as mock_load:
            await gui_instance.initialize()
        
        mock_load.assert_called_once()
        gui_instance.datacenter_select.update.assert_called_once()
        gui_instance.world_select.update.assert_called_once()


class TestBuildMethod:
    """Test suite for GUI build method."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        return UniversusGUI()
    
    def test_build(self, gui_instance):
        """Test building GUI."""
        with patch.object(gui_instance, 'create_header') as mock_header, \
             patch.object(gui_instance, 'create_sidebar') as mock_sidebar, \
             patch.object(gui_instance, 'create_main_content') as mock_content, \
             patch.object(gui_instance, 'create_footer') as mock_footer, \
             patch.object(gui_instance, 'show_view') as mock_show_view:
            
            gui_instance.build()
        
        mock_header.assert_called_once()
        mock_sidebar.assert_called_once()
        mock_content.assert_called_once()
        mock_footer.assert_called_once()
        mock_show_view.assert_called_once_with('dashboard')


class TestServiceIntegration:
    """Test suite for GUI integration with service layer."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        gui.top_items_container = Mock()
        gui.main_content = Mock()
        return gui
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock service."""
        mock = Mock()
        mock.get_top_items.return_value = [
            {
                'item_id': 123,
                'item_name': 'Potion',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'last_updated': '2024-12-01T10:00:00',
                'snapshot_date': '2024-12-01'
            }
        ]
        mock.initialize_tracking.return_value = (
            [{'item_id': 123, 'velocity': 10.5, 'avg_price': 1000}],
            100,
            50
        )
        mock.update_tracked_items.return_value = (45, 5, [])
        mock.get_item_report.return_value = [
            {
                'snapshot_date': '2024-12-01',
                'sale_velocity': 10.5,
                'average_price': 1000,
                'min_price': 800,
                'max_price': 1200,
                'total_listings': 100
            }
        ]
        mock.calculate_trends.return_value = {
            'velocity_change': 5.0,
            'price_change': -2.0
        }
        mock.sync_items_database.return_value = 47000
        return mock
    
    def test_render_top_items_table_calls_service(self, gui_instance, mock_service):
        """Test that rendering top items table uses service data."""
        items = mock_service.get_top_items.return_value
        
        # Create a mock that supports context manager protocol
        mock_container = MagicMock()
        mock_container.__enter__ = MagicMock(return_value=mock_container)
        mock_container.__exit__ = MagicMock(return_value=False)
        gui_instance.top_items_container = mock_container
        
        with patch('gui.ui') as mock_ui:
            gui_instance._render_top_items_table(items)
        
        # Verify table creation with correct data
        assert mock_ui.table.called


class TestErrorHandling:
    """Test suite for error handling in GUI."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_world = 'Behemoth'
        return gui
    
    @pytest.mark.asyncio
    async def test_load_datacenters_api_error(self, gui_instance):
        """Test error handling when API fails during datacenter loading."""
        mock_api = Mock()
        mock_api.get_worlds.side_effect = Exception("API Error")
        
        with patch('gui.api', mock_api), \
             patch('gui.logger') as mock_logger, \
             patch('gui.ui') as mock_ui:
            await gui_instance.load_datacenters()
        
        # Should log error and show notification
        mock_logger.error.assert_called_once()
        assert mock_ui.notify.called


class TestUIComponentCreation:
    """Test suite for UI component creation."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        gui = UniversusGUI()
        gui.selected_datacenter = 'Aether'
        gui.selected_world = 'Behemoth'
        gui.datacenter_names = ['Aether', 'Primal']
        gui.worlds = ['Behemoth', 'Cactuar']
        gui.worlds_by_datacenter = {'Aether': ['Behemoth', 'Cactuar']}
        return gui
    
    def test_create_header(self, gui_instance):
        """Test header creation."""
        with patch('gui.ui') as mock_ui:
            gui_instance.create_header()
        
        # Verify UI components are created
        assert mock_ui.header.called
        assert mock_ui.select.called
        assert mock_ui.button.called
    
    def test_create_sidebar(self, gui_instance):
        """Test sidebar creation."""
        with patch('gui.ui') as mock_ui:
            gui_instance.create_sidebar()
        
        # Verify sidebar components are created
        assert mock_ui.left_drawer.called
        assert mock_ui.label.called
        assert mock_ui.button.called
    
    def test_create_footer(self, gui_instance):
        """Test footer creation."""
        with patch('gui.ui') as mock_ui:
            gui_instance.create_footer()
        
        # Verify footer components are created
        assert mock_ui.footer.called
        assert mock_ui.label.called
        assert gui_instance.status_label is not None
    
    def test_create_main_content(self, gui_instance):
        """Test main content creation."""
        with patch('gui.ui') as mock_ui:
            gui_instance.create_main_content()
        
        assert mock_ui.column.called
        assert gui_instance.main_content is not None
    
    def test_clear_main_content(self, gui_instance):
        """Test clearing main content."""
        gui_instance.main_content = Mock()
        
        gui_instance.clear_main_content()
        
        gui_instance.main_content.clear.assert_called_once()
    
    def test_clear_main_content_when_none(self, gui_instance):
        """Test clearing main content when it's None."""
        gui_instance.main_content = None
        
        # Should not raise an error
        gui_instance.clear_main_content()


class TestGlobalFunctions:
    """Test suite for global module functions."""
    
    def test_init_services(self):
        """Test service initialization."""
        mock_config = Mock()
        mock_config.get.return_value = 'test.db'
        
        with patch('gui.config', mock_config), \
             patch('gui.MarketDatabase') as mock_db_class, \
             patch('gui.UniversalisAPI') as mock_api_class, \
             patch('gui.MarketService') as mock_service_class, \
             patch('gui.logger') as mock_logger:
            
            from gui import init_services
            init_services()
        
        # Verify all services are initialized
        mock_db_class.assert_called_once_with('test.db')
        mock_api_class.assert_called_once()
        mock_service_class.assert_called_once()
        mock_logger.info.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
