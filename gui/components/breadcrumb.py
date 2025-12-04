"""
Breadcrumb navigation component.
"""

from typing import List, Tuple, Optional, Callable
from nicegui import ui

from ..utils.icons import GameIcons


# View name to display name and section mapping
VIEW_CONFIG = {
    'dashboard': {'label': 'Dashboard', 'section': None, 'icon': GameIcons.DASHBOARD},
    'datacenters': {'label': 'Datacenters', 'section': 'Market Data', 'icon': GameIcons.DATACENTER},
    'top': {'label': 'Top Items', 'section': 'Market Data', 'icon': GameIcons.TRENDING},
    'report': {'label': 'Item Report', 'section': 'Analysis', 'icon': GameIcons.ANALYTICS},
    'sell_volume': {'label': 'Sell Volume by World', 'section': 'Analysis', 'icon': GameIcons.INSIGHTS},
    'sell_volume_chart': {'label': 'Sell Volume Chart', 'section': 'Analysis', 'icon': GameIcons.CHART_PIE},
    'market_analysis': {'label': 'Market Analysis', 'section': 'Analysis', 'icon': GameIcons.CHART_BAR},
    'appearance': {'label': 'Appearance', 'section': 'Settings', 'icon': GameIcons.THEME_DARK},
    'import_static_data': {'label': 'Import Static Data', 'section': 'Settings', 'icon': GameIcons.CLOUD_DOWNLOAD},
    'tracked_worlds': {'label': 'Tracked Worlds', 'section': 'Settings', 'icon': GameIcons.WORLD},
}


class Breadcrumb:
    """Breadcrumb navigation component."""
    
    def __init__(
        self,
        current_view: str,
        selected_world: Optional[str] = None,
        on_navigate: Optional[Callable] = None,
        dark_mode: bool = False
    ):
        """Initialize breadcrumb component.
        
        Args:
            current_view: Current view name
            selected_world: Currently selected world (optional context)
            on_navigate: Callback when navigating via breadcrumb
            dark_mode: Whether dark mode is active
        """
        self.current_view = current_view
        self.selected_world = selected_world
        self.on_navigate = on_navigate
        self.dark_mode = dark_mode
        self.container = None
        self._render()
    
    def _render(self):
        """Render the breadcrumb."""
        view_config = VIEW_CONFIG.get(self.current_view, {'label': self.current_view, 'section': None, 'icon': 'help'})
        
        bg_class = 'bg-gray-50' if not self.dark_mode else 'bg-gray-800'
        text_class = 'text-gray-600' if not self.dark_mode else 'text-gray-300'
        active_class = 'text-blue-600 font-semibold' if not self.dark_mode else 'text-blue-400 font-semibold'
        separator_class = 'text-gray-400' if not self.dark_mode else 'text-gray-500'
        
        self.container = ui.row().classes(f'w-full items-center gap-2 px-4 py-2 {bg_class} rounded-lg mb-4')
        
        with self.container:
            # Home icon - always links to dashboard
            home_btn = ui.button(icon=GameIcons.HOME, on_click=lambda: self._navigate('dashboard')).props('flat dense round size=sm')
            home_btn.classes(text_class)
            
            # Separator
            ui.icon('chevron_right').classes(f'{separator_class} text-sm')
            
            # Section (if any)
            section = view_config.get('section')
            if section:
                ui.label(section).classes(f'{text_class} text-sm')
                ui.icon('chevron_right').classes(f'{separator_class} text-sm')
            
            # Current view with icon
            ui.icon(view_config['icon']).classes(f'{active_class} text-sm')
            ui.label(view_config['label']).classes(f'{active_class} text-sm')
            
            # World context (if selected and relevant)
            if self.selected_world and self.current_view in ['top', 'report', 'datacenters']:
                ui.icon('chevron_right').classes(f'{separator_class} text-sm')
                ui.icon(GameIcons.WORLD).classes(f'{active_class} text-sm')
                ui.label(self.selected_world).classes(f'{active_class} text-sm')
    
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
            with self.container:
                self._render_content()
    
    def _render_content(self):
        """Render breadcrumb content (for updates)."""
        view_config = VIEW_CONFIG.get(self.current_view, {'label': self.current_view, 'section': None, 'icon': 'help'})
        
        text_class = 'text-gray-600' if not self.dark_mode else 'text-gray-300'
        active_class = 'text-blue-600 font-semibold' if not self.dark_mode else 'text-blue-400 font-semibold'
        separator_class = 'text-gray-400' if not self.dark_mode else 'text-gray-500'
        
        # Home icon
        home_btn = ui.button(icon=GameIcons.HOME, on_click=lambda: self._navigate('dashboard')).props('flat dense round size=sm')
        home_btn.classes(text_class)
        
        ui.icon('chevron_right').classes(f'{separator_class} text-sm')
        
        section = view_config.get('section')
        if section:
            ui.label(section).classes(f'{text_class} text-sm')
            ui.icon('chevron_right').classes(f'{separator_class} text-sm')
        
        ui.icon(view_config['icon']).classes(f'{active_class} text-sm')
        ui.label(view_config['label']).classes(f'{active_class} text-sm')
        
        if self.selected_world and self.current_view in ['top', 'report', 'datacenters']:
            ui.icon('chevron_right').classes(f'{separator_class} text-sm')
            ui.icon(GameIcons.WORLD).classes(f'{active_class} text-sm')
            ui.label(self.selected_world).classes(f'{active_class} text-sm')


def render_breadcrumb(
    current_view: str,
    selected_world: Optional[str] = None,
    on_navigate: Optional[Callable] = None,
    dark_mode: bool = False
) -> Breadcrumb:
    """Render a breadcrumb navigation.
    
    Args:
        current_view: Current view name
        selected_world: Currently selected world
        on_navigate: Navigation callback
        dark_mode: Whether dark mode is active
    
    Returns:
        Breadcrumb component instance
    """
    return Breadcrumb(current_view, selected_world, on_navigate, dark_mode)
