"""
Application header component.

Provides the main navigation bar with datacenter/world selectors.
Uses the unified design system for consistent styling.
"""

from typing import Callable, Optional
from nicegui import ui

from ..utils.icons import GameIcons
from ..utils.design_system import PROPS


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
            version: Application version
        """
        self.datacenter_select: Optional[ui.select] = None
        self.world_select: Optional[ui.select] = None
        
        self._render(
            datacenter_names,
            selected_datacenter,
            worlds,
            selected_world,
            on_datacenter_change,
            on_world_change,
            on_refresh,
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
        version
    ):
        """Render the header."""
        with ui.header().classes('items-center'):
            with ui.row().classes('w-full items-center gap-4'):
                # Logo and title
                with ui.row().classes('items-center gap-2'):
                    ui.icon(GameIcons.WORLD, size='lg').classes('text-blue-400')
                    ui.label('Universus').classes('text-2xl font-bold text-white')
                    ui.label('FFXIV Market Tracker').classes('text-sm text-gray-400 hidden sm:inline')
                
                ui.space()
                
                # Selectors row
                with ui.row().classes('items-center gap-4'):
                    # Datacenter selector
                    self.datacenter_select = ui.select(
                        options=datacenter_names if datacenter_names else ['Loading...'],
                        value=selected_datacenter if selected_datacenter else None,
                        label='Datacenter',
                        on_change=lambda e: on_datacenter_change(e.value) if e.value and e.value != 'Loading...' else None
                    ).classes('w-40').props(PROPS.SELECT_OUTLINED)
                    
                    # World selector
                    self.world_select = ui.select(
                        options=worlds if worlds else ['Loading...'],
                        value=selected_world if selected_world else None,
                        label='World',
                        on_change=lambda e: on_world_change(e.value) if e.value and e.value != 'Loading...' else None
                    ).classes('w-40').props(PROPS.SELECT_OUTLINED)
                    
                    # Refresh button with tooltip
                    ui.button(
                        icon=GameIcons.REFRESH, 
                        on_click=on_refresh
                    ).props(PROPS.BTN_ICON).tooltip('Refresh current view')
    
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
