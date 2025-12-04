"""
Breadcrumb navigation component.

Uses the unified design system for consistent styling.
"""

from typing import Optional, Callable
from nicegui import ui

from ..utils.icons import GameIcons
from ..utils.design_system import PROPS


# View name to display name and section mapping
VIEW_CONFIG = {
    'dashboard': {'label': 'Dashboard', 'section': None, 'icon': GameIcons.DASHBOARD},
    'datacenters': {'label': 'Datacenters', 'section': 'Market Data', 'icon': GameIcons.DATACENTER},
    'top': {'label': 'Top Items', 'section': 'Market Data', 'icon': GameIcons.TRENDING},
    'report': {'label': 'Item Report', 'section': 'Analysis', 'icon': GameIcons.ANALYTICS},
    'sell_volume': {'label': 'Sell Volume by World', 'section': 'Analysis', 'icon': GameIcons.INSIGHTS},
    'sell_volume_chart': {'label': 'Sell Volume Chart', 'section': 'Analysis', 'icon': GameIcons.CHART_PIE},
    'market_analysis': {'label': 'Market Analysis', 'section': 'Analysis', 'icon': GameIcons.CHART_BAR},
    'import_static_data': {'label': 'Import Static Data', 'section': 'Settings', 'icon': GameIcons.CLOUD_DOWNLOAD},
    'tracked_worlds': {'label': 'Tracked Worlds', 'section': 'Settings', 'icon': GameIcons.WORLD},
}


class Breadcrumb:
    """Breadcrumb navigation component."""
    
    def __init__(
        self,
        current_view: str,
        selected_world: Optional[str] = None,
        on_navigate: Optional[Callable] = None
    ):
        """Initialize breadcrumb component.
        
        Args:
            current_view: Current view name
            selected_world: Currently selected world (optional context)
            on_navigate: Callback when navigating via breadcrumb
        """
        self.current_view = current_view
        self.selected_world = selected_world
        self.on_navigate = on_navigate
        self.container = None
        self._render()
    
    def _render(self):
        """Render the breadcrumb."""
        view_config = VIEW_CONFIG.get(
            self.current_view, 
            {'label': self.current_view, 'section': None, 'icon': 'help'}
        )
        
        self.container = ui.row().classes(
            'w-full items-center gap-2 px-4 py-2 rounded-lg mb-6'
        )
        
        with self.container:
            self._render_content(view_config)
    
    def _render_content(self, view_config: dict):
        """Render breadcrumb content."""
        # Home button - always links to dashboard
        ui.button(
            icon=GameIcons.HOME, 
            on_click=lambda: self._navigate('dashboard')
        ).props('flat dense round size=sm').classes('text-gray-400 hover:text-white')
        
        # Separator
        ui.icon('chevron_right').classes('text-gray-600 text-sm')
        
        # Section (if any)
        section = view_config.get('section')
        if section:
            ui.label(section).classes('text-sm text-gray-400')
            ui.icon('chevron_right').classes('text-gray-600 text-sm')
        
        # Current view with icon
        with ui.row().classes('items-center gap-1'):
            ui.icon(view_config['icon']).classes('text-blue-400 text-sm')
            ui.label(view_config['label']).classes('text-sm font-semibold text-blue-400')
        
        # World context (if selected and relevant)
        if self.selected_world and self.current_view in ['top', 'report', 'datacenters']:
            ui.icon('chevron_right').classes('text-gray-600 text-sm')
            with ui.row().classes('items-center gap-1'):
                ui.icon(GameIcons.WORLD).classes('text-blue-400 text-sm')
                ui.label(self.selected_world).classes('text-sm font-semibold text-blue-400')
    
    def _navigate(self, view: str):
        """Navigate to a view."""
        if self.on_navigate:
            self.on_navigate(view)
    
    def update(self, current_view: str, selected_world: Optional[str] = None):
        """Update the breadcrumb.
        
        Args:
            current_view: New current view
            selected_world: New selected world
        """
        self.current_view = current_view
        self.selected_world = selected_world
        
        if self.container:
            self.container.clear()
            view_config = VIEW_CONFIG.get(
                self.current_view, 
                {'label': self.current_view, 'section': None, 'icon': 'help'}
            )
            with self.container:
                self._render_content(view_config)


def render_breadcrumb(
    current_view: str,
    selected_world: Optional[str] = None,
    on_navigate: Optional[Callable] = None
) -> Breadcrumb:
    """Render a breadcrumb navigation.
    
    Args:
        current_view: Current view name
        selected_world: Currently selected world
        on_navigate: Navigation callback
    
    Returns:
        Breadcrumb component instance
    """
    return Breadcrumb(current_view, selected_world, on_navigate)
