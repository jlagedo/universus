"""
Navigation sidebar component.

Uses the unified design system for consistent styling.
"""

from typing import Callable
from nicegui import ui

from ..utils.icons import GameIcons
from ..utils.design_system import PROPS


class Sidebar:
    """Navigation sidebar component."""
    
    def __init__(self, on_view_change: Callable):
        """Initialize sidebar component.
        
        Args:
            on_view_change: Callback when view changes
        """
        self._render(on_view_change)
    
    def _render(self, on_view_change: Callable):
        """Render the sidebar with collapsible sections."""
        with ui.left_drawer(value=True):
            with ui.column().classes('w-full gap-1 px-2 pt-4'):
                # Dashboard - always visible at top
                self._nav_button(
                    'Dashboard',
                    GameIcons.DASHBOARD,
                    lambda: on_view_change('dashboard')
                )
                
                ui.separator().classes('my-2')
                
                # Market Data Section - Collapsible
                with ui.expansion(
                    'Market Data', 
                    icon=GameIcons.CHART_BAR, 
                    value=False
                ).classes('w-full').props(PROPS.EXPANSION_DENSE):
                    with ui.column().classes('w-full gap-1 pl-2'):
                        self._nav_button(
                            'Datacenters',
                            GameIcons.DATACENTER,
                            lambda: on_view_change('datacenters'),
                            dense=True
                        )
                        self._nav_button(
                            'Top Items',
                            GameIcons.TRENDING,
                            lambda: on_view_change('top'),
                            dense=True
                        )
                
                # Analysis Section - Collapsible
                with ui.expansion(
                    'Analysis', 
                    icon=GameIcons.ANALYTICS, 
                    value=False
                ).classes('w-full').props(PROPS.EXPANSION_DENSE):
                    with ui.column().classes('w-full gap-1 pl-2'):
                        self._nav_button(
                            'Item Report',
                            GameIcons.ANALYTICS,
                            lambda: on_view_change('report'),
                            dense=True
                        )
                        self._nav_button(
                            'Sell Volume by World',
                            GameIcons.INSIGHTS,
                            lambda: on_view_change('sell_volume'),
                            dense=True
                        )
                        self._nav_button(
                            'Sell Volume Chart',
                            GameIcons.CHART_PIE,
                            lambda: on_view_change('sell_volume_chart'),
                            dense=True
                        )
                        self._nav_button(
                            'Market Analysis',
                            GameIcons.CHART_BAR,
                            lambda: on_view_change('market_analysis'),
                            dense=True
                        )
                
                # Settings Section - Collapsible  
                with ui.expansion(
                    'Settings', 
                    icon=GameIcons.SETTINGS, 
                    value=False
                ).classes('w-full').props(PROPS.EXPANSION_DENSE):
                    with ui.column().classes('w-full gap-1 pl-2'):
                        self._nav_button(
                            'Import Static Data',
                            GameIcons.CLOUD_DOWNLOAD,
                            lambda: on_view_change('import_static_data'),
                            dense=True
                        )
                        self._nav_button(
                            'Tracked Worlds',
                            GameIcons.WORLD,
                            lambda: on_view_change('tracked_worlds'),
                            dense=True
                        )
    
    def _nav_button(
        self, 
        label: str, 
        icon: str, 
        on_click: Callable, 
        dense: bool = False
    ):
        """Create a navigation button with consistent styling.
        
        Args:
            label: Button label
            icon: Icon name
            on_click: Click handler
            dense: Whether to use dense styling
        """
        props = 'flat align=left dense' if dense else 'flat align=left'
        ui.button(
            label,
            icon=icon,
            on_click=on_click
        ).classes('w-full justify-start').props(props)
