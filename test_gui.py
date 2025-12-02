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
        assert format_gil(1000) == "1.000"
        assert format_gil(1000000) == "1.000.000"
        assert format_gil(500) == "500"
        assert format_gil(0) == "0"
    
    def test_format_gil_float_amount(self):
        """Test formatting gil with float amount."""
        assert format_gil(1234.56) == "1.235"
        assert format_gil(999.99) == "1.000"
    
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
    """Test suite for ThemeManager."""
    
    def test_initialization_light(self):
        """Test theme manager initialization with light mode."""
        theme = ThemeManager('light')
        assert theme.dark_mode is False
    
    def test_initialization_dark(self):
        """Test theme manager initialization with dark mode."""
        theme = ThemeManager('dark')
        assert theme.dark_mode is True
    
    def test_toggle(self):
        """Test theme toggle."""
        theme = ThemeManager('light')
        assert theme.dark_mode is False
        
        with patch('gui.utils.theme.ui'):
            theme.toggle()
        
        assert theme.dark_mode is True
    
    def test_get_theme_classes(self):
        """Test getting theme classes."""
        theme = ThemeManager('light')
        assert theme.get_theme_classes('light-class', 'dark-class') == 'light-class'
        
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
        assert gui.theme.dark_mode is False
    
    def test_initialization_dark_mode(self, mock_dependencies):
        """Test GUI initialization with dark mode."""
        mock_db, mock_api, mock_service, mock_config = mock_dependencies
        mock_config.get.return_value = 'dark'
        
        gui = UniversusGUI(mock_db, mock_api, mock_service, mock_config)
        
        assert gui.theme.dark_mode is True
    
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
        gui_instance.api.get_worlds_async = AsyncMock(return_value=[
            {'id': 73, 'name': 'Adamantoise'},
            {'id': 79, 'name': 'Cactuar'}
        ])
        gui_instance.service.get_datacenters.return_value = [
            {'name': 'Aether', 'region': 'NA', 'worlds': [73, 79]}
        ]
        
        # Mock session response for API check
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        gui_instance.api.session.get.return_value = mock_response
        
        await gui_instance.load_datacenters()
        
        assert len(gui_instance.state.datacenters) == 1
        assert 'Aether' in gui_instance.state.datacenter_names
        assert gui_instance.state.world_id_to_name[73] == 'Adamantoise'
        assert gui_instance.state.world_id_to_name[79] == 'Cactuar'
    
    @pytest.mark.asyncio
    async def test_load_datacenters_error_handling(self, gui_instance):
        """Test datacenter loading error handling."""
        gui_instance.api.get_worlds_async = AsyncMock(side_effect=Exception("API Error"))
        
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
        
        # Mock the db methods for new dashboard
        gui_instance.db.get_tracked_worlds_count = Mock(return_value=5)
        gui_instance.db.get_current_prices_count = Mock(return_value=100)
        gui_instance.db.get_latest_current_price_timestamp = Mock(return_value='2025-12-02 10:00:00')
        gui_instance.db.get_marketable_items_count = Mock(return_value=2000)
        gui_instance.db.get_datacenter_gil_volume = Mock(return_value={'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0})
        gui_instance.db.get_top_items_by_hq_velocity = Mock(return_value=[])
        
        with patch('gui.app.ui'), patch('gui.views.dashboard.ui'):
            gui_instance.change_datacenter('Primal')
        
        assert gui_instance.state.selected_datacenter == 'Primal'
        gui_instance.header.update_worlds.assert_called_once()
    
    def test_change_world(self, gui_instance):
        """Test changing world."""
        gui_instance.main_content = MagicMock()
        gui_instance.main_content.__enter__ = MagicMock(return_value=gui_instance.main_content)
        gui_instance.main_content.__exit__ = MagicMock(return_value=False)
        
        # Mock the db methods for new dashboard
        gui_instance.db.get_tracked_worlds_count = Mock(return_value=5)
        gui_instance.db.get_current_prices_count = Mock(return_value=100)
        gui_instance.db.get_latest_current_price_timestamp = Mock(return_value='2025-12-02 10:00:00')
        gui_instance.db.get_marketable_items_count = Mock(return_value=2000)
        gui_instance.db.get_datacenter_gil_volume = Mock(return_value={'hq_volume': 0, 'nq_volume': 0, 'total_volume': 0, 'item_count': 0})
        gui_instance.db.get_top_items_by_hq_velocity = Mock(return_value=[])
        
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
    
    def test_toggle_theme(self, gui_instance):
        """Test theme toggle."""
        initial_mode = gui_instance.theme.dark_mode
        
        with patch('gui.app.ui') as mock_ui, \
             patch.object(gui_instance.theme, 'toggle') as mock_toggle:
            gui_instance.toggle_theme()
        
        mock_toggle.assert_called_once()
        mock_ui.notify.assert_called_once()


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
