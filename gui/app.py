"""
Main GUI application module.
"""

import asyncio
import logging
from nicegui import ui

from .state import AppState
from .utils import ThemeManager
from .components import Header, Sidebar, Footer
from .views import (
    dashboard, datacenters, top_items, tracked_items,
    tracking, reports, settings
)

logger = logging.getLogger(__name__)

# Application version
__version__ = "1.0.0"


class UniversusGUI:
    """Main GUI application class."""
    
    def __init__(self, db, api, service, config):
        """Initialize the GUI application.
        
        Args:
            db: Database instance
            api: API client instance
            service: Market service instance
            config: Configuration object
        """
        self.db = db
        self.api = api
        self.service = service
        self.config = config
        
        # Application state
        self.state = AppState()
        
        # Theme management
        theme_mode = config.get('gui', 'theme', 'light')
        self.theme = ThemeManager(theme_mode)
        
        # UI component references
        self.header = None
        self.sidebar = None
        self.footer = None
        self.main_content = None
    
    async def load_datacenters(self):
        """Load datacenters and worlds from API."""
        try:
            self._ensure_api_connection()
            
            # Fetch worlds to build ID-to-name mapping
            worlds_data = await self.api.get_worlds_async()
            world_id_to_name = {w['id']: w['name'] for w in worlds_data}
            
            # Fetch datacenters
            datacenters = self.service.get_datacenters()
            
            # Update application state
            self.state.set_datacenters(datacenters, world_id_to_name)
            
            # Update header selectors
            if self.header:
                self.header.update_datacenters(
                    self.state.datacenter_names,
                    self.state.selected_datacenter
                )
                dc_worlds = self.state.get_worlds_for_datacenter()
                self.header.update_worlds(dc_worlds, self.state.selected_world)
            
            logger.info(f"Loaded {len(datacenters)} datacenters, {len(self.state.worlds)} worlds")
        except Exception as e:
            logger.error(f"Failed to load datacenters: {e}")
            ui.notify(f"Failed to load datacenters: {e}", type='negative')
    
    def _ensure_api_connection(self):
        """Ensure API client has a fresh connection."""
        try:
            test_response = self.api.session.get(f"{self.api.base_url}/data-centers", timeout=2)
            test_response.raise_for_status()
            logger.debug("API connection verified")
        except Exception as e:
            logger.warning(f"API connection lost, reinitializing: {e}")
            if self.api:
                try:
                    self.api.close()
                except:
                    pass
            # Recreate API and service
            from api_client import UniversalisAPI
            from service import MarketService
            self.api = UniversalisAPI()
            self.service = MarketService(self.db, self.api)
            logger.info("API client reinitialized")
    
    def set_status(self, message: str):
        """Update status bar message."""
        if self.footer:
            self.footer.set_status(message)
    
    def toggle_theme(self):
        """Toggle between light and dark themes."""
        self.theme.toggle()
        ui.notify(f'Switched to {"dark" if self.theme.dark_mode else "light"} theme', type='info')
        logger.info(f'Theme changed to {"dark" if self.theme.dark_mode else "light"}')
    
    def create_header(self):
        """Create the application header."""
        self.header = Header(
            datacenter_names=self.state.datacenter_names,
            selected_datacenter=self.state.selected_datacenter,
            worlds=self.state.get_worlds_for_datacenter(),
            selected_world=self.state.selected_world,
            on_datacenter_change=self.change_datacenter,
            on_world_change=self.change_world,
            on_refresh=self.refresh_current_view,
            on_theme_toggle=self.toggle_theme,
            dark_mode=self.theme.dark_mode,
            version=__version__
        )
    
    def create_sidebar(self):
        """Create the navigation sidebar."""
        self.sidebar = Sidebar(
            on_view_change=self.show_view,
            dark_mode=self.theme.dark_mode
        )
    
    def create_footer(self):
        """Create the application footer."""
        self.footer = Footer(
            version=__version__,
            dark_mode=self.theme.dark_mode
        )
    
    def create_main_content(self):
        """Create the main content area."""
        self.main_content = ui.column().classes('w-full p-6')
    
    def clear_main_content(self):
        """Clear the main content area."""
        if self.main_content:
            self.main_content.clear()
    
    def show_view(self, view: str):
        """Switch to a specific view.
        
        Args:
            view: View name to display
        """
        self.state.current_view = view
        self.clear_main_content()
        
        with self.main_content:
            if view == 'dashboard':
                self._render_dashboard()
            elif view == 'datacenters':
                self._render_datacenters()
            elif view == 'top':
                self._render_top_items()
            elif view == 'tracked':
                self._render_tracked_items()
            elif view == 'init_tracking':
                self._render_init_tracking()
            elif view == 'update':
                self._render_update()
            elif view == 'report':
                self._render_report()
            elif view == 'sync_items':
                self._render_sync_items()
            elif view == 'tracked_worlds':
                self._render_tracked_worlds()
            elif view == 'sell_volume':
                self._render_sell_volume()
            elif view == 'sell_volume_chart':
                self._render_sell_volume_chart()
    
    async def refresh_current_view(self):
        """Refresh the current view."""
        self.show_view(self.state.current_view)
        ui.notify('View refreshed', type='info')
    
    def change_datacenter(self, datacenter: str):
        """Change the selected datacenter."""
        dc_worlds = self.state.change_datacenter(datacenter)
        
        if self.header:
            self.header.update_worlds(dc_worlds, self.state.selected_world)
        
        ui.notify(f'Datacenter changed to {datacenter}', type='info')
        self.show_view(self.state.current_view)
    
    def change_world(self, world: str):
        """Change the selected world."""
        self.state.change_world(world)
        ui.notify(f'World changed to {world}', type='info')
        self.show_view(self.state.current_view)
    
    # View rendering methods
    def _render_dashboard(self):
        """Render dashboard view."""
        quick_actions_row, tracked_items, _ = dashboard.render(
            self.state, self.db, self.theme.dark_mode
        )
        if quick_actions_row:
            with quick_actions_row:
                ui.button('Update Market Data', icon='sync', on_click=lambda: self.show_view('update')).props('color=primary')
                ui.button('View Top Items', icon='trending_up', on_click=lambda: self.show_view('top')).props('color=secondary')
                ui.button('Initialize Tracking', icon='add_circle', on_click=lambda: self.show_view('init_tracking')).props('color=accent')
    
    def _render_datacenters(self):
        """Render datacenters view."""
        datacenters.render(self.state, self.service, self.api, self.theme.dark_mode)
    
    def _render_top_items(self):
        """Render top items view."""
        limit_input, results_container = top_items.render(
            self.state, self.service, self.theme.dark_mode
        )
        
        if limit_input and results_container:
            async def fetch_top():
                self.set_status(f'Fetching top {int(limit_input.value)} items...')
                try:
                    self._ensure_api_connection()
                    items = self.service.get_top_items(self.state.selected_world, int(limit_input.value))
                    top_items.render_table(items, results_container)
                    self.set_status('Ready')
                except Exception as e:
                    ui.notify(f'Error: {e}', type='negative')
                    self.set_status('Error')
            
            ui.button('Fetch Top Items', icon='trending_up', on_click=fetch_top).props('color=primary')
    
    def _render_tracked_items(self):
        """Render tracked items view."""
        tracked_items.render(self.state, self.service, self.theme.dark_mode)
    
    def _render_init_tracking(self):
        """Render init tracking view."""
        limit_input, progress_container = tracking.render_init_tracking(
            self.state, self.service, self.theme.dark_mode
        )
        
        if limit_input and progress_container:
            async def start_tracking():
                self._ensure_api_connection()
                await tracking.execute_init_tracking(
                    self.state, self.service, int(limit_input.value),
                    progress_container, self.set_status
                )
            
            ui.button('Start Tracking', icon='play_arrow', on_click=start_tracking).props('color=primary').classes('mt-4')
    
    def _render_update(self):
        """Render update view."""
        progress_container = tracking.render_update(
            self.state, self.db, self.theme.dark_mode
        )
        
        if progress_container:
            async def start_update():
                self._ensure_api_connection()
                await tracking.execute_update(
                    self.state, self.service, progress_container, self.set_status
                )
            
            ui.button('Update Now', icon='sync', on_click=start_update).props('color=primary').classes('mt-4')
    
    def _render_report(self):
        """Render item report view."""
        item_id_input, days_input, report_container = reports.render_item_report(
            self.state, self.service, self.db, self.theme.dark_mode
        )
        
        if item_id_input and days_input and report_container:
            def generate():
                item_id = int(item_id_input.value)
                days = int(days_input.value)
                
                if item_id <= 0:
                    ui.notify('Please enter a valid Item ID', type='warning')
                    return
                
                self._ensure_api_connection()
                reports.generate_item_report(
                    self.state, self.service, self.db, item_id, days,
                    report_container, self.set_status
                )
            
            ui.button('Generate Report', icon='analytics', on_click=generate).props('color=primary').classes('mt-4')
    
    def _render_sync_items(self):
        """Render sync items view."""
        progress_container = settings.render_sync_items(self.db, self.theme.dark_mode)
        
        async def start_sync():
            self._ensure_api_connection()
            await settings.execute_sync_items(
                self.service, progress_container, self.set_status
            )
        
        ui.button('Sync Now', icon='cloud_download', on_click=start_sync).props('color=primary').classes('mt-4')
    
    def _render_tracked_worlds(self):
        """Render tracked worlds view."""
        world_select, worlds_container = settings.render_tracked_worlds(
            self.state, self.service, self.theme.dark_mode
        )
        
        def refresh_table():
            settings.render_tracked_worlds_table(
                self.state, self.service, worlds_container, refresh_table
            )
        
        async def add_world():
            await settings.add_tracked_world(
                self.state, self.service, world_select.value, refresh_table
            )
        
        ui.button('Add', icon='add', on_click=add_world).props('color=primary').classes('mt-2')
        
        # Initial render
        refresh_table()
    
    def _render_sell_volume(self):
        """Render sell volume by world view."""
        world_options, world_select, limit_input, report_container = reports.render_sell_volume(
            self.state, self.service, self.db, self.theme.dark_mode
        )
        
        if world_options and world_select and limit_input and report_container:
            def generate():
                reports.generate_sell_volume_report(
                    self.state, self.db, world_options, world_select.value,
                    int(limit_input.value), report_container, self.set_status
                )
            
            ui.button('Generate Report', icon='bar_chart', on_click=generate).props('color=primary').classes('mt-4')
    
    def _render_sell_volume_chart(self):
        """Render sell volume chart view."""
        world_options, world_select, chart_container = reports.render_sell_volume_chart(
            self.state, self.service, self.db, self.theme.dark_mode
        )
        
        if world_options and world_select and chart_container:
            def generate():
                reports.generate_chart(
                    self.state, self.db, world_options, world_select.value,
                    chart_container, self.set_status
                )
            
            ui.button('Generate Chart', icon='pie_chart', on_click=generate).props('color=primary').classes('mt-4')
    
    async def initialize(self):
        """Initialize the GUI with data."""
        await self.load_datacenters()
    
    def build(self):
        """Build the complete GUI."""
        if self.theme.dark_mode:
            self.theme.apply_css()
        
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_footer()
        
        # Show initial view
        self.show_view('dashboard')
