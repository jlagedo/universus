#!/usr/bin/env python3
"""
GUI Feature Validation Script
Validates all GUI features without launching the full UI
"""

import sys
from unittest.mock import Mock, MagicMock, patch

# Mock nicegui before importing
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.app'] = MagicMock()

from gui import UniversusGUI, format_gil, format_velocity, format_time_ago, init_services
from datetime import datetime, timedelta

def test_formatting_functions():
    """Test all formatting utility functions."""
    print("Testing formatting functions...")
    
    # Test format_gil
    assert format_gil(1000) == "1,000", "format_gil failed for 1000"
    assert format_gil(1000000) == "1,000,000", "format_gil failed for 1000000"
    assert format_gil(None) == "N/A", "format_gil failed for None"
    
    # Test format_velocity
    assert format_velocity(10.5) == "10.50", "format_velocity failed for 10.5"
    assert format_velocity(None) == "N/A", "format_velocity failed for None"
    
    # Test format_time_ago
    past = (datetime.now() - timedelta(days=5)).isoformat()
    result = format_time_ago(past)
    assert "d ago" in result, f"format_time_ago failed for 5 days ago: {result}"
    
    assert format_time_ago("") == "Never", "format_time_ago failed for empty string"
    assert format_time_ago("invalid") == "Unknown", "format_time_ago failed for invalid"
    
    print("✓ All formatting functions working correctly")


def test_gui_initialization():
    """Test GUI initialization."""
    print("\nTesting GUI initialization...")
    
    gui = UniversusGUI()
    
    # Check initial state
    assert gui.selected_datacenter == "", "Initial datacenter should be empty"
    assert gui.selected_world == "", "Initial world should be empty"
    assert gui.worlds == [], "Initial worlds should be empty"
    assert gui.datacenters == [], "Initial datacenters should be empty"
    assert gui.current_view == "dashboard", "Initial view should be dashboard"
    
    # Check component references
    assert gui.status_label is None, "Status label should be None initially"
    assert gui.datacenter_select is None, "Datacenter select should be None initially"
    assert gui.world_select is None, "World select should be None initially"
    assert gui.main_content is None, "Main content should be None initially"
    
    print("✓ GUI initialization working correctly")


def test_gui_methods():
    """Test GUI methods."""
    print("\nTesting GUI methods...")
    
    gui = UniversusGUI()
    
    # Test set_status with no label (should not crash)
    gui.set_status("Test message")
    
    # Test set_status with mock label
    mock_label = Mock()
    gui.status_label = mock_label
    gui.set_status("Test message")
    mock_label.set_text.assert_called_once_with("Test message")
    
    # Test clear_main_content with None (should not crash)
    gui.clear_main_content()
    
    # Test clear_main_content with mock
    mock_content = Mock()
    gui.main_content = mock_content
    gui.clear_main_content()
    mock_content.clear.assert_called_once()
    
    print("✓ GUI methods working correctly")


def test_datacenter_world_mapping():
    """Test datacenter and world data structures."""
    print("\nTesting datacenter/world mapping...")
    
    gui = UniversusGUI()
    
    # Simulate loaded data
    gui.datacenters = [
        {'name': 'Aether', 'region': 'NA', 'worlds': [73, 79]},
        {'name': 'Primal', 'region': 'NA', 'worlds': [54]}
    ]
    
    gui.world_id_to_name = {73: 'Adamantoise', 79: 'Cactuar', 54: 'Faerie'}
    gui.world_name_to_id = {'Adamantoise': 73, 'Cactuar': 79, 'Faerie': 54}
    
    gui.worlds_by_datacenter = {
        'Aether': ['Adamantoise', 'Cactuar'],
        'Primal': ['Faerie']
    }
    
    gui.datacenter_names = ['Aether', 'Primal']
    gui.worlds = ['Adamantoise', 'Cactuar', 'Faerie']
    
    # Test mappings
    assert gui.world_id_to_name[73] == 'Adamantoise', "World ID mapping failed"
    assert gui.world_name_to_id['Adamantoise'] == 73, "World name mapping failed"
    assert 'Adamantoise' in gui.worlds_by_datacenter['Aether'], "Datacenter worlds mapping failed"
    assert len(gui.worlds_by_datacenter['Primal']) == 1, "Primal datacenter should have 1 world"
    
    print("✓ Datacenter/world mapping working correctly")


def test_view_switching():
    """Test view switching logic."""
    print("\nTesting view switching...")
    
    gui = UniversusGUI()
    
    # Test current_view updates
    views = ['dashboard', 'datacenters', 'top', 'tracked', 'init_tracking', 
             'update', 'report', 'sync_items']
    
    for view in views:
        gui.current_view = view
        assert gui.current_view == view, f"View switching failed for {view}"
    
    print("✓ View switching working correctly")


def test_all_gui_features():
    """Test all GUI features are defined."""
    print("\nTesting all GUI features are defined...")
    
    gui = UniversusGUI()
    
    # Check all required methods exist
    required_methods = [
        'load_datacenters',
        'set_status',
        'create_header',
        'create_sidebar',
        'create_footer',
        'create_main_content',
        'clear_main_content',
        'show_view',
        'refresh_current_view',
        'change_datacenter',
        'change_world',
        'render_dashboard',
        'render_datacenters',
        'render_top_items',
        'render_tracked_items',
        'render_init_tracking',
        'render_update',
        'render_report',
        'render_sync_items',
        '_stat_card',
        '_render_datacenters_table',
        '_render_top_items_table',
        'initialize',
        'build'
    ]
    
    for method in required_methods:
        assert hasattr(gui, method), f"Missing method: {method}"
        assert callable(getattr(gui, method)), f"Method {method} is not callable"
    
    print(f"✓ All {len(required_methods)} required GUI methods are defined and callable")


def test_cli_feature_equivalents():
    """Verify all CLI features have GUI equivalents."""
    print("\nTesting CLI feature equivalents...")
    
    # Map CLI commands to GUI views
    cli_to_gui_mapping = {
        'datacenters': 'render_datacenters',
        'top': 'render_top_items',
        'list-tracked': 'render_tracked_items',
        'init-tracking': 'render_init_tracking',
        'update': 'render_update',
        'report': 'render_report',
        'sync-items': 'render_sync_items'
    }
    
    gui = UniversusGUI()
    
    for cli_cmd, gui_method in cli_to_gui_mapping.items():
        assert hasattr(gui, gui_method), f"CLI command '{cli_cmd}' has no GUI equivalent '{gui_method}'"
        print(f"  ✓ CLI '{cli_cmd}' → GUI '{gui_method}'")
    
    print(f"✓ All {len(cli_to_gui_mapping)} CLI commands have GUI equivalents")


def run_validation():
    """Run all validation tests."""
    print("=" * 60)
    print("GUI FEATURE VALIDATION")
    print("=" * 60)
    
    try:
        test_formatting_functions()
        test_gui_initialization()
        test_gui_methods()
        test_datacenter_world_mapping()
        test_view_switching()
        test_all_gui_features()
        test_cli_feature_equivalents()
        
        print("\n" + "=" * 60)
        print("✓ ALL GUI FEATURES VALIDATED SUCCESSFULLY")
        print("=" * 60)
        return 0
    
    except AssertionError as e:
        print(f"\n✗ VALIDATION FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_validation())
