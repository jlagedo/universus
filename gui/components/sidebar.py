"""
Navigation sidebar component.
"""

from typing import Callable
from nicegui import ui

from ..utils.icons import GameIcons


class Sidebar:
    """Navigation sidebar component."""
    
    def __init__(self, on_view_change: Callable, dark_mode: bool = False):
        """Initialize sidebar component.
        
        Args:
            on_view_change: Callback when view changes
            dark_mode: Whether dark mode is active
        """
        self.dark_mode = dark_mode
        self._render(on_view_change)
    
    def _render(self, on_view_change: Callable):
        """Render the sidebar."""
        sidebar_class = 'bg-gray-100' if not self.dark_mode else 'bg-gray-800'
        nav_label_class = 'text-lg font-bold p-4 text-gray-900' if not self.dark_mode else 'text-lg font-bold p-4 text-white'
        section_label_class = 'text-sm text-gray-500 px-4 py-2' if not self.dark_mode else 'text-sm text-gray-400 px-4 py-2'
        
        with ui.left_drawer(value=True).classes(sidebar_class):
            ui.label('Navigation').classes(nav_label_class)
            
            with ui.column().classes('w-full gap-0'):
                # Dashboard
                ui.button(
                    'Dashboard',
                    icon=GameIcons.DASHBOARD,
                    on_click=lambda: on_view_change('dashboard')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Market Data').classes(section_label_class)
                
                # Datacenters
                ui.button(
                    'Datacenters',
                    icon=GameIcons.DATACENTER,
                    on_click=lambda: on_view_change('datacenters')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Top Items
                ui.button(
                    'Top Items',
                    icon=GameIcons.TRENDING,
                    on_click=lambda: on_view_change('top')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Analysis').classes(section_label_class)
                
                # Item Report
                ui.button(
                    'Item Report',
                    icon=GameIcons.ANALYTICS,
                    on_click=lambda: on_view_change('report')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Sell Volume by World Report
                ui.button(
                    'Sell Volume by World',
                    icon=GameIcons.INSIGHTS,
                    on_click=lambda: on_view_change('sell_volume')
                ).classes('w-full justify-start').props('flat align=left')

                # Sell Volume Chart
                ui.button(
                    'Sell Volume Chart',
                    icon=GameIcons.CHART_PIE,
                    on_click=lambda: on_view_change('sell_volume_chart')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Settings').classes(section_label_class)
                
                # Import Static Data
                ui.button(
                    'Import Static Data',
                    icon=GameIcons.CLOUD_DOWNLOAD,
                    on_click=lambda: on_view_change('import_static_data')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Tracked Worlds
                ui.button(
                    'Tracked Worlds',
                    icon=GameIcons.WORLD,
                    on_click=lambda: on_view_change('tracked_worlds')
                ).classes('w-full justify-start').props('flat align=left')
