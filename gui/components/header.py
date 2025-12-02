"""
Application header component.
"""

from typing import Callable, Optional
from nicegui import ui


class Header:
    """Application header with datacenter/world selectors."""
    
    def __init__(
        self,
        datacenter_names: list,
        selected_datacenter: str,
        worlds: list,
        selected_world: str,
        on_datacenter_change: Callable,
        on_world_change: Callable,
        on_refresh: Callable,
        on_theme_toggle: Callable,
        dark_mode: bool = False,
        version: str = "1.0.0"
    ):
        """Initialize header component.
        
        Args:
            datacenter_names: List of datacenter names
            selected_datacenter: Currently selected datacenter
            worlds: List of world names
            selected_world: Currently selected world
            on_datacenter_change: Callback for datacenter change
            on_world_change: Callback for world change
            on_refresh: Callback for refresh button
            on_theme_toggle: Callback for theme toggle
            dark_mode: Whether dark mode is active
            version: Application version
        """
        self.datacenter_select: Optional[ui.select] = None
        self.world_select: Optional[ui.select] = None
        self.dark_mode = dark_mode
        
        self._render(
            datacenter_names,
            selected_datacenter,
            worlds,
            selected_world,
            on_datacenter_change,
            on_world_change,
            on_refresh,
            on_theme_toggle,
            version
        )
    
    def _render(
        self,
        datacenter_names,
        selected_datacenter,
        worlds,
        selected_world,
        on_datacenter_change,
        on_world_change,
        on_refresh,
        on_theme_toggle,
        version
    ):
        """Render the header."""
        header_class = 'bg-blue-800 text-white' if not self.dark_mode else 'bg-gray-900 text-white'
        
        with ui.header().classes(header_class):
            with ui.row().classes('w-full items-center'):
                ui.icon('public', size='lg').classes('mr-2')
                ui.label('Universus').classes('text-2xl font-bold')
                ui.label('FFXIV Market Tracker').classes('text-sm ml-2 opacity-75')
                
                ui.space()
                
                # Datacenter selector
                select_class = 'bg-blue-700 text-white' if not self.dark_mode else 'bg-gray-800 text-white'
                self.datacenter_select = ui.select(
                    options=datacenter_names if datacenter_names else ['Loading...'],
                    value=selected_datacenter if selected_datacenter else None,
                    label='Datacenter',
                    on_change=lambda e: on_datacenter_change(e.value) if e.value and e.value != 'Loading...' else None
                ).classes(f'w-40 {select_class}').props('dark dense outlined' if self.dark_mode else 'dense outlined')
                
                # World selector
                self.world_select = ui.select(
                    options=worlds if worlds else ['Loading...'],
                    value=selected_world if selected_world else None,
                    label='World',
                    on_change=lambda e: on_world_change(e.value) if e.value and e.value != 'Loading...' else None
                ).classes(f'w-40 {select_class}').props('dark dense outlined' if self.dark_mode else 'dense outlined')
                
                ui.button(icon='refresh', on_click=on_refresh).props('flat round').tooltip('Refresh')
                
                # Theme toggle button
                theme_icon = 'dark_mode' if not self.dark_mode else 'light_mode'
                ui.button(icon=theme_icon, on_click=on_theme_toggle).props('flat round').tooltip('Toggle Theme')
    
    def update_datacenters(self, datacenter_names: list, selected_datacenter: str):
        """Update datacenter options.
        
        Args:
            datacenter_names: New list of datacenter names
            selected_datacenter: New selected datacenter
        """
        if self.datacenter_select:
            self.datacenter_select.options = datacenter_names
            self.datacenter_select.value = selected_datacenter
            self.datacenter_select.update()
    
    def update_worlds(self, worlds: list, selected_world: str):
        """Update world options.
        
        Args:
            worlds: New list of world names
            selected_world: New selected world
        """
        if self.world_select:
            self.world_select.options = worlds if worlds else ['No worlds']
            self.world_select.value = selected_world
            self.world_select.update()
