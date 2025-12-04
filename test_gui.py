"""
Unit tests for the refactored GUI module.
Tests utilities, components, and main app structure.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from datetime import datetime, timedelta

# Mock nicegui before importing gui module
import sys
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.app'] = MagicMock()

from gui.utils import format_gil, format_velocity, format_time_ago
from gui.utils import ThemeManager
from gui.state import AppState
from gui import UniversusGUI


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
        assert format_gil(1234.56) == "1,235"
        assert format_gil(999.99) == "1,000"
    
    def test_format_gil_none(self):
        """Test formatting gil with None."""
        assert format_gil(None) == "N/A"
    
    def test_format_velocity_valid(self):
        """Test formatting velocity with valid value."""
        result = format_velocity(10.5)
        assert "10" in result and "5" in result
        
        result = format_velocity(0.5)
        assert "0" in result and "5" in result
    
    def test_format_velocity_none(self):
        """Test formatting velocity with None."""
        assert format_velocity(None) == "N/A"
    
    def test_format_time_ago_days(self):
        """Test time ago formatting for days."""
        past_time = datetime.now() - timedelta(days=5)
        result = format_time_ago(past_time.isoformat())
        assert "d ago" in result
    
    def test_format_time_ago_hours(self):
        """Test time ago formatting for hours."""
        past_time = datetime.now() - timedelta(hours=5)
        result = format_time_ago(past_time.isoformat())
        assert "h ago" in result or "m ago" in result
    
    def test_format_time_ago_minutes(self):
        """Test time ago formatting for minutes."""
        past_time = datetime.now() - timedelta(minutes=30)
        result = format_time_ago(past_time.isoformat())
        assert "m ago" in result
    
    def test_format_time_ago_empty(self):
        """Test time ago formatting with empty string."""
        assert format_time_ago("") == "Never"
    
    def test_format_time_ago_invalid(self):
        """Test time ago formatting with invalid timestamp."""
        assert format_time_ago("invalid") == "Unknown"


class TestThemeManager:
    """Test suite for ThemeManager (dark mode only)."""
    
    def test_initialization_always_dark(self):
        """Test theme manager always initializes to dark mode."""
        theme = ThemeManager('light')  # Even with 'light', should be dark
        assert theme.dark_mode is True
        
        theme = ThemeManager('dark')
        assert theme.dark_mode is True
        
        theme = ThemeManager()  # Default
        assert theme.dark_mode is True
    
    def test_get_theme_classes_always_dark(self):
        """Test getting theme classes always returns dark classes."""
        theme = ThemeManager('light')
        assert theme.get_theme_classes('light-class', 'dark-class') == 'dark-class'
        
        theme = ThemeManager('dark')
        assert theme.get_theme_classes('light-class', 'dark-class') == 'dark-class'


class TestAppState:
    """Test suite for AppState."""
    
    def test_initialization(self):
        """Test app state initialization."""
        state = AppState()
        assert state.selected_datacenter == ""
        assert state.selected_world == ""
        assert state.worlds == []
        assert state.datacenters == []
        assert state.current_view == "dashboard"
    
    def test_set_datacenters(self):
        """Test setting datacenters."""
        state = AppState()
        datacenters = [
            {'name': 'Aether', 'worlds': [73, 79]},
            {'name': 'Primal', 'worlds': [54]}
        ]
        world_id_to_name = {73: 'Adamantoise', 79: 'Cactuar', 54: 'Faerie'}
        
        state.set_datacenters(datacenters, world_id_to_name)
        
        assert len(state.datacenters) == 2
        assert 'Aether' in state.datacenter_names
        assert 'Primal' in state.datacenter_names
        assert state.world_id_to_name == world_id_to_name
        assert 'Adamantoise' in state.worlds
        assert 'Cactuar' in state.worlds
        assert 'Faerie' in state.worlds
    
    def test_change_datacenter(self):
        """Test changing datacenter."""
        state = AppState()
        state.worlds_by_datacenter = {
            'Aether': ['Adamantoise', 'Cactuar'],
            'Primal': ['Faerie', 'Behemoth']
        }
        state.selected_world = 'Adamantoise'
        
        worlds = state.change_datacenter('Primal')
        
        assert state.selected_datacenter == 'Primal'
        assert 'Faerie' in worlds
        assert 'Behemoth' in worlds
        # World should be auto-selected
        assert state.selected_world in ['Faerie', 'Behemoth']
    
    def test_change_world(self):
        """Test changing world."""
        state = AppState()
        state.change_world('Cactuar')
        
        assert state.selected_world == 'Cactuar'
    
    def test_get_worlds_for_datacenter(self):
        """Test getting worlds for datacenter."""
        state = AppState()
        state.worlds_by_datacenter = {
            'Aether': ['Adamantoise', 'Cactuar']
        }
        state.selected_datacenter = 'Aether'
        
        worlds = state.get_worlds_for_datacenter()
        
        assert 'Adamantoise' in worlds
        assert 'Cactuar' in worlds


class TestUniversusGUIInitialization:
    """Test suite for UniversusGUI initialization."""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Create mock dependencies for GUI."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return mock_db, mock_api, mock_service, mock_config
    
    def test_initialization(self, mock_dependencies):
        """Test GUI initialization."""
        mock_db, mock_api, mock_service, mock_config = mock_dependencies
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        
        assert gui.db == mock_db
        assert gui.api == mock_api
        assert gui.service == mock_service
        assert gui.config == mock_config
        assert gui.state is not None
        assert gui.theme is not None
        assert gui.theme.dark_mode is True  # Always dark mode
    
    def test_initialization_dark_mode(self, mock_dependencies):
        """Test GUI initialization always uses dark mode."""
        mock_db, mock_api, mock_service, mock_config = mock_dependencies
        mock_config.get.return_value = 'dark'
        
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        
        assert gui.theme.dark_mode is True
    
    def test_initialization_light_mode_ignored(self, mock_dependencies):
        """Test GUI initialization ignores light mode setting."""
        mock_db, mock_api, mock_service, mock_config = mock_dependencies
        mock_config.get.return_value = 'light'
        
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        
        assert gui.theme.dark_mode is True  # Still dark mode
    
    def test_ui_components_initialized_as_none(self, mock_dependencies):
        """Test that UI components start as None."""
        mock_db, mock_api, mock_service, mock_config = mock_dependencies
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        
        assert gui.header is None
        assert gui.sidebar is None
        assert gui.footer is None
        assert gui.main_content is None


class TestUniversusGUIDataLoading:
    """Test suite for GUI data loading."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_api.session = Mock()
        mock_api.session.get = Mock()
        mock_api.base_url = "https://universalis.app/api/v2"
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return UniversusGUI(mock_db, mock_api, mock_service, mock_config)
    
    @pytest.mark.asyncio
    async def test_load_datacenters_success(self, gui_instance):
        """Test successful datacenter loading."""
        gui_instance.service.get_available_worlds_async = AsyncMock(return_value=[
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'}
        ])
        gui_instance.service.get_datacenters.return_value = [
            {'name': 'Aether', 'region': 'NA', 'worlds': [73, 79]}
        ]
        gui_instance.service.list_tracked_worlds.return_value = []
        gui_instance.service.ensure_api_connection.return_value = True
        
        await gui_instance.load_datacenters()
        
        assert len(gui_instance.state.datacenters) == 1
        assert 'Aether' in gui_instance.state.datacenter_names
        assert gui_instance.state.world_id_to_name[73] == 'Adamantoise'
        assert gui_instance.state.world_id_to_name[79] == 'Cactuar'
    
    @pytest.mark.asyncio
    async def test_load_datacenters_error_handling(self, gui_instance):
        """Test datacenter loading error handling."""
        gui_instance.service.ensure_api_connection.side_effect = Exception("API Error")
        
        with patch('gui.app.ui') as mock_ui, patch('gui.app.logger'):
            await gui_instance.load_datacenters()
        
        # Should show error notification
        mock_ui.notify.assert_called_once()


class TestUniversusGUINavigation:
    """Test suite for GUI navigation."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        gui.state.selected_world = 'Behemoth'
        gui.state.datacenter_names = ['Aether', 'Primal']
        gui.state.worlds_by_datacenter = {
            'Aether': ['Adamantoise', 'Cactuar'],
            'Primal': ['Behemoth', 'Excalibur']
        }
        return gui
    
    def test_change_datacenter(self, gui_instance):
        """Test changing datacenter."""
        gui_instance.header = Mock()
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        # Mock the service methods for new dashboard
        gui_instance.service.get_tracked_worlds_count = Mock(return_value=5)
        gui_instance.service.get_current_prices_count = Mock(return_value=100)
        gui_instance.service.get_latest_current_price_timestamp = Mock(return_value='2025-12-02 10:00:00')
        gui_instance.service.get_marketable_items_count = Mock(return_value=2000)
        gui_instance.service.get_datacenter_gil_volume = Mock(return_value={'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0})
        gui_instance.service.get_top_items_by_hq_velocity = Mock(return_value=[])
        
        with patch('gui.app.ui'), patch('gui.views.dashboard.ui'):
            gui_instance.change_datacenter('Primal')
        
        assert gui_instance.state.selected_datacenter == 'Primal'
        gui_instance.header.update_worlds.assert_called_once()
    
    def test_change_world(self, gui_instance):
        """Test changing world."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        # Mock the service methods for new dashboard
        gui_instance.service.get_tracked_worlds_count = Mock(return_value=5)
        gui_instance.service.get_current_prices_count = Mock(return_value=100)
        gui_instance.service.get_latest_current_price_timestamp = Mock(return_value='2025-12-02 10:00:00')
        gui_instance.service.get_marketable_items_count = Mock(return_value=2000)
        gui_instance.service.get_datacenter_gil_volume = Mock(return_value={'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0})
        gui_instance.service.get_top_items_by_hq_velocity = Mock(return_value=[])
        
        with patch('gui.app.ui'), patch('gui.views.dashboard.ui'):
            gui_instance.change_world('Cactuar')
        
        assert gui_instance.state.selected_world == 'Cactuar'
    
    def test_show_view(self, gui_instance):
        """Test showing different views."""
        gui_instance.main_content = Mock()
        gui_instance.main_content.__enter__ = Mock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = Mock(return_value=False)
        
        with patch.object(gui_instance, '_render_dashboard') as mock_render:
            gui_instance.show_view('dashboard')
        
        assert gui_instance.state.current_view == 'dashboard'
        gui_instance.main_content.clear.assert_called_once()
        mock_render.assert_called_once()


class TestUniversusGUIBuild:
    """Test suite for GUI build method."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return UniversusGUI(mock_db, mock_api, mock_service, mock_config)
    
    def test_build(self, gui_instance):
        """Test building GUI."""
        with patch.object(gui_instance, 'create_header'), \
             patch.object(gui_instance, 'create_sidebar'), \
             patch.object(gui_instance, 'create_main_content'), \
             patch.object(gui_instance, 'create_footer'), \
             patch.object(gui_instance, 'show_view'):
            
            gui_instance.build()
        
        # All components should be created
        assert True  # If no exception is raised, test passes


class TestUniversusGUIStatusManagement:
    """Test suite for status management."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return UniversusGUI(mock_db, mock_api, mock_service, mock_config)
    
    def test_set_status_with_footer(self, gui_instance):
        """Test setting status when footer exists."""
        gui_instance.footer = Mock()
        gui_instance.footer.set_status = Mock()
        
        gui_instance.set_status("Test message")
        
        gui_instance.footer.set_status.assert_called_once_with("Test message")
    
    def test_set_status_without_footer(self, gui_instance):
        """Test setting status when footer is None."""
        gui_instance.footer = None
        
        # Should not raise an error
        gui_instance.set_status("Test message")


class TestUniversusGUIThemeToggle:
    """Test suite for theme toggle."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return UniversusGUI(mock_db, mock_api, mock_service, mock_config)
    
    def test_gui_uses_dark_mode(self, gui_instance):
        """Test GUI always uses dark mode."""
        assert gui_instance.theme.dark_mode is True


class TestUniversusGUIAsyncOperations:
    """Test suite for async operations."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        return UniversusGUI(mock_db, mock_api, mock_service, mock_config)
    
    @pytest.mark.asyncio
    async def test_initialize(self, gui_instance):
        """Test GUI initialization."""
        with patch.object(gui_instance, 'load_datacenters', new_callable=AsyncMock):
            await gui_instance.initialize()
        
        # Should complete without error
        assert True
    
    @pytest.mark.asyncio
    async def test_refresh_current_view(self, gui_instance):
        """Test refreshing current view."""
        gui_instance.state.current_view = 'dashboard'
        
        with patch.object(gui_instance, 'show_view'), \
             patch('gui.app.ui'):
            await gui_instance.refresh_current_view()
        
        # Should complete without error
        assert True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


class TestFormatGilEdgeCases:
    """Additional test cases for format_gil."""
    
    def test_format_gil_negative_amount(self):
        """Test formatting gil with negative amount."""
        assert format_gil(-1000) == "-1,000"
    
    def test_format_gil_large_amount(self):
        """Test formatting gil with very large amount."""
        assert format_gil(999999999) == "999,999,999"
    
    def test_format_gil_invalid_string(self):
        """Test formatting gil with invalid string."""
        assert format_gil("not a number") == "N/A"
    
    def test_format_gil_empty_string(self):
        """Test formatting gil with empty string."""
        assert format_gil("") == "N/A"


class TestFormatVelocityEdgeCases:
    """Additional test cases for format_velocity."""
    
    def test_format_velocity_negative(self):
        """Test formatting negative velocity."""
        result = format_velocity(-10.5)
        assert "-10" in result
    
    def test_format_velocity_large(self):
        """Test formatting large velocity."""
        result = format_velocity(1234567.89)
        # Should contain comma thousands separators and period for decimals
        assert "," in result and "." in result
    
    def test_format_velocity_invalid_string(self):
        """Test formatting velocity with invalid string."""
        assert format_velocity("not a number") == "N/A"
    
    def test_format_velocity_zero(self):
        """Test formatting zero velocity."""
        result = format_velocity(0)
        assert "0.00" in result


class TestFormatTimeAgoEdgeCases:
    """Additional test cases for format_time_ago."""
    
    def test_format_time_ago_just_now(self):
        """Test time ago formatting for just now (seconds)."""
        past_time = datetime.now() - timedelta(seconds=30)
        result = format_time_ago(past_time.isoformat())
        assert "m ago" in result
    
    def test_format_time_ago_weeks(self):
        """Test time ago formatting for weeks (still shows days)."""
        past_time = datetime.now() - timedelta(days=14)
        result = format_time_ago(past_time.isoformat())
        assert "14d ago" in result
    
    def test_format_time_ago_none(self):
        """Test time ago formatting with None."""
        assert format_time_ago(None) == "Never"


class TestAppStateEdgeCases:
    """Additional test cases for AppState."""
    
    def test_change_datacenter_empty(self):
        """Test changing to datacenter with no worlds."""
        state = AppState()
        state.worlds_by_datacenter = {
            'Empty': []
        }
        
        worlds = state.change_datacenter('Empty')
        
        assert worlds == []
        assert state.selected_datacenter == 'Empty'
    
    def test_change_datacenter_nonexistent(self):
        """Test changing to nonexistent datacenter."""
        state = AppState()
        state.worlds_by_datacenter = {}
        
        worlds = state.change_datacenter('NonExistent')
        
        assert worlds == []
    
    def test_set_datacenters_empty(self):
        """Test setting empty datacenters."""
        state = AppState()
        state.set_datacenters([], {})
        
        assert state.datacenters == []
        assert state.datacenter_names == []
        assert state.worlds == []
    
    def test_get_worlds_for_datacenter_no_selection(self):
        """Test getting worlds when no datacenter selected."""
        state = AppState()
        state.worlds_by_datacenter = {}
        state.selected_datacenter = ''
        
        worlds = state.get_worlds_for_datacenter()
        
        assert worlds == []


class TestThemeManagerEdgeCases:
    """Additional test cases for ThemeManager (dark mode only)."""
    
    def test_always_dark_mode(self):
        """Test theme is always dark mode regardless of input."""
        theme = ThemeManager('light')
        assert theme.dark_mode is True
        
        theme = ThemeManager('dark')
        assert theme.dark_mode is True
    
    def test_get_theme_classes_returns_dark(self):
        """Test getting theme classes always returns dark classes."""
        theme = ThemeManager('light')
        assert theme.get_theme_classes('light-class', 'dark-class') == 'dark-class'
        
        theme = ThemeManager('dark')
        assert theme.get_theme_classes('light-class', 'dark-class') == 'dark-class'
        
        # Even with None, returns whatever dark value is
        theme = ThemeManager('light')
        assert theme.get_theme_classes('light-class', None) is None


class TestUniversusGUIViewRendering:
    """Test suite for view rendering."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_db.conn = Mock()
        mock_db.conn.cursor = Mock(return_value=Mock())
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        gui.state.selected_world = 'Behemoth'
        gui.state.selected_datacenter = 'Primal'
        return gui
    
    def test_render_top_items_view(self, gui_instance):
        """Test rendering top items view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_top_items') as mock_render:
            gui_instance.show_view('top')  # Correct view name
        
        assert gui_instance.state.current_view == 'top'
        mock_render.assert_called_once()
    
    def test_render_datacenters_view(self, gui_instance):
        """Test rendering datacenters view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_datacenters') as mock_render:
            gui_instance.show_view('datacenters')
        
        assert gui_instance.state.current_view == 'datacenters'
        mock_render.assert_called_once()
    
    def test_render_import_static_data_view(self, gui_instance):
        """Test rendering import static data view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_import_static_data') as mock_render:
            gui_instance.show_view('import_static_data')
        
        assert gui_instance.state.current_view == 'import_static_data'
        mock_render.assert_called_once()
    
    def test_render_report_view(self, gui_instance):
        """Test rendering report view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_report') as mock_render:
            gui_instance.show_view('report')
        
        assert gui_instance.state.current_view == 'report'
        mock_render.assert_called_once()
    
    def test_render_market_analysis_view(self, gui_instance):
        """Test rendering market analysis view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_market_analysis') as mock_render:
            gui_instance.show_view('market_analysis')
        
        assert gui_instance.state.current_view == 'market_analysis'
        mock_render.assert_called_once()
    
    def test_render_tracked_worlds_view(self, gui_instance):
        """Test rendering tracked worlds view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_tracked_worlds') as mock_render:
            gui_instance.show_view('tracked_worlds')
        
        assert gui_instance.state.current_view == 'tracked_worlds'
        mock_render.assert_called_once()
    
    def test_render_sell_volume_view(self, gui_instance):
        """Test rendering sell volume view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_sell_volume') as mock_render:
            gui_instance.show_view('sell_volume')
        
        assert gui_instance.state.current_view == 'sell_volume'
        mock_render.assert_called_once()
    
    def test_render_sell_volume_chart_view(self, gui_instance):
        """Test rendering sell volume chart view."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        with patch.object(gui_instance, '_render_sell_volume_chart') as mock_render:
            gui_instance.show_view('sell_volume_chart')
        
        assert gui_instance.state.current_view == 'sell_volume_chart'
        mock_render.assert_called_once()


class TestUniversusGUIWorldManagement:
    """Test suite for world management in GUI."""
    
    @pytest.fixture
    def gui_instance(self):
        """Create a GUI instance for testing."""
        mock_db = Mock()
        mock_api = Mock()
        mock_service = Mock()
        mock_config = Mock()
        mock_config.get.return_value = 'light'
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        gui.state.worlds_by_datacenter = {
            'Aether': ['Adamantoise', 'Cactuar'],
            'Primal': ['Behemoth', 'Excalibur']
        }
        return gui
    
    def test_get_world_id_from_name(self, gui_instance):
        """Test getting world ID from name."""
        gui_instance.state.world_id_to_name = {73: 'Adamantoise', 79: 'Cactuar'}
        
        # Create reverse lookup
        name_to_id = {v: k for k, v in gui_instance.state.world_id_to_name.items()}
        
        assert name_to_id.get('Adamantoise') == 73
        assert name_to_id.get('Cactuar') == 79
        assert name_to_id.get('NonExistent') is None
    
    def test_datacenter_change_updates_world_selection(self, gui_instance):
        """Test that changing datacenter updates world selection."""
        gui_instance.header = Mock()
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        gui_instance.service.get_tracked_worlds_count = Mock(return_value=0)
        gui_instance.service.get_current_prices_count = Mock(return_value=0)
        gui_instance.service.get_latest_current_price_timestamp = Mock(return_value=None)
        gui_instance.service.get_marketable_items_count = Mock(return_value=0)
        gui_instance.service.get_datacenter_gil_volume = Mock(return_value={'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0})
        gui_instance.service.get_top_items_by_hq_velocity = Mock(return_value=[])
        
        gui_instance.state.selected_world = 'Adamantoise'
        
        with patch('gui.app.ui'), patch('gui.views.dashboard.ui'):
            gui_instance.change_datacenter('Primal')
        
        # World should be auto-selected from new datacenter
        assert gui_instance.state.selected_world in ['Behemoth', 'Excalibur']


class TestGameIcons:
    """Test suite for GameIcons class."""
    
    def test_icon_constants_are_strings(self):
        """Test that all icon constants are strings."""
        from gui.utils.icons import GameIcons
        
        icon_attrs = [attr for attr in dir(GameIcons) if not attr.startswith('_')]
        
        for attr in icon_attrs:
            value = getattr(GameIcons, attr)
            assert isinstance(value, str), f"{attr} should be a string"
    
    def test_required_icons_exist(self):
        """Test that required icons exist."""
        from gui.utils.icons import GameIcons
        
        required_icons = [
            'HOME', 'DASHBOARD', 'MENU', 'SETTINGS',
            'MARKET', 'TRENDING', 'ANALYTICS',
            'SERVER', 'DATABASE', 'WORLD',
            'ADD', 'REMOVE', 'REFRESH', 'SYNC'
        ]
        
        for icon_name in required_icons:
            assert hasattr(GameIcons, icon_name), f"Missing icon: {icon_name}"
