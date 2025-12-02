"""
Navigation sidebar component.
"""

from typing import Callable
from nicegui import ui


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
                    icon='dashboard',
                    on_click=lambda: on_view_change('dashboard')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Market Data').classes(section_label_class)
                
                # Datacenters
                ui.button(
                    'Datacenters',
                    icon='dns',
                    on_click=lambda: on_view_change('datacenters')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Top Items
                ui.button(
                    'Top Items',
                    icon='trending_up',
                    on_click=lambda: on_view_change('top')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Tracking').classes(section_label_class)
                
                # Tracked Items
                ui.button(
                    'Tracked Items',
                    icon='visibility',
                    on_click=lambda: on_view_change('tracked')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Init Tracking
                ui.button(
                    'Initialize Tracking',
                    icon='add_circle',
                    on_click=lambda: on_view_change('init_tracking')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Update
                ui.button(
                    'Update Data',
                    icon='sync',
                    on_click=lambda: on_view_change('update')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Analysis').classes(section_label_class)
                
                # Item Report
                ui.button(
                    'Item Report',
                    icon='analytics',
                    on_click=lambda: on_view_change('report')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Sell Volume by World Report
                ui.button(
                    'Sell Volume by World',
                    icon='insights',
                    on_click=lambda: on_view_change('sell_volume')
                ).classes('w-full justify-start').props('flat align=left')

                # Sell Volume Chart
                ui.button(
                    'Sell Volume Chart',
                    icon='pie_chart',
                    on_click=lambda: on_view_change('sell_volume_chart')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Settings').classes(section_label_class)
                
                # Sync Items
                ui.button(
                    'Sync Item Names',
                    icon='cloud_download',
                    on_click=lambda: on_view_change('sync_items')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Tracked Worlds
                ui.button(
                    'Tracked Worlds',
                    icon='public',
                    on_click=lambda: on_view_change('tracked_worlds')
                ).classes('w-full justify-start').props('flat align=left')
