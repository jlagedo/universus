#!/usr/bin/env python3
"""
Universus GUI - NiceGUI-based market tracking interface.

A modern web-based GUI for tracking FFXIV market prices.
Implements all features from the CLI version.
"""

import asyncio
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any

import requests
from nicegui import ui, app

from config import get_config
from database import MarketDatabase
from api_client import UniversalisAPI
from service import MarketService

# Application version
__version__ = "1.0.0"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
config = get_config()
db: Optional[MarketDatabase] = None
api: Optional[UniversalisAPI] = None
service: Optional[MarketService] = None


def init_services():
    """Initialize database, API, and service instances."""
    global db, api, service
    db_path = config.get('database', 'default_path', 'market_data.db')
    db = MarketDatabase(db_path)
    api = UniversalisAPI()
    service = MarketService(db, api)
    logger.info(f"Services initialized with database: {db_path}")


def ensure_api_connection():
    """Ensure API client has a fresh connection."""
    global api, service
    try:
        # Test the connection with a lightweight request
        test_response = api.session.get(f"{api.base_url}/data-centers", timeout=2)
        test_response.raise_for_status()
        logger.debug("API connection verified")
    except (requests.exceptions.ConnectionError, 
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
            Exception) as e:
        logger.warning(f"API connection lost or unhealthy, reinitializing: {e}")
        # Close old session and create new API client
        if api:
            try:
                api.close()
            except:
                pass
        api = UniversalisAPI()
        service = MarketService(db, api)
        logger.info("API client reinitialized with fresh session")


def format_gil(amount: Optional[float]) -> str:
    """Format gil amount with thousands separator."""
    if amount is None:
        return "N/A"
    return f"{int(amount):,}"


def format_velocity(velocity: Optional[float]) -> str:
    """Format sales velocity."""
    if velocity is None:
        return "N/A"
    return f"{velocity:.2f}"


def format_time_ago(timestamp_str: str) -> str:
    """Format a timestamp as relative time."""
    if not timestamp_str:
        return "Never"
    try:
        last_updated = datetime.fromisoformat(timestamp_str)
        time_ago = datetime.now() - last_updated
        if time_ago.days > 0:
            return f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            return f"{time_ago.seconds // 3600}h ago"
        else:
            return f"{time_ago.seconds // 60}m ago"
    except (ValueError, TypeError):
        return "Unknown"


class UniversusGUI:
    """Main GUI application class implementing all CLI features."""
    
    def __init__(self):
        self.selected_datacenter: str = ""
        self.selected_world: str = ""
        self.worlds: List[str] = []
        self.datacenters: List[Dict] = []
        self.datacenter_names: List[str] = []
        self.worlds_by_datacenter: Dict[str, List[str]] = {}
        self.world_id_to_name: Dict[int, str] = {}  # Map world ID to name
        self.world_name_to_id: Dict[str, int] = {}  # Map world name to ID
        
        # UI component references
        self.status_label = None
        self.datacenter_select = None
        self.world_select = None
        self.main_content = None
        
        # Current view
        self.current_view = "dashboard"
    
    async def load_datacenters(self):
        """Load datacenters and worlds from API."""
        try:
            # Ensure we have a valid API connection
            ensure_api_connection()
            
            # Fetch worlds first to build ID-to-name mapping
            worlds_data = api.get_worlds()
            self.world_id_to_name = {w['id']: w['name'] for w in worlds_data}
            self.world_name_to_id = {w['name']: w['id'] for w in worlds_data}
            
            # Fetch datacenters
            self.datacenters = service.get_datacenters()
            self.worlds = []
            self.datacenter_names = []
            self.worlds_by_datacenter = {}
            
            for dc in self.datacenters:
                dc_name = dc.get('name', '')
                if dc_name:
                    self.datacenter_names.append(dc_name)
                    # Convert world IDs to names
                    world_ids = dc.get('worlds', [])
                    world_names = [self.world_id_to_name.get(wid, str(wid)) for wid in world_ids]
                    self.worlds_by_datacenter[dc_name] = sorted(world_names)
                    self.worlds.extend(world_names)
            
            self.datacenter_names = sorted(self.datacenter_names)
            self.worlds = sorted(set(self.worlds))
            
            # Set default selections
            if self.datacenter_names and not self.selected_datacenter:
                self.selected_datacenter = self.datacenter_names[0]
            if self.selected_datacenter and not self.selected_world:
                dc_worlds = self.worlds_by_datacenter.get(self.selected_datacenter, [])
                if dc_worlds:
                    self.selected_world = dc_worlds[0]
            
            logger.info(f"Loaded {len(self.datacenters)} datacenters, {len(self.worlds)} worlds")
        except Exception as e:
            logger.error(f"Failed to load datacenters: {e}")
            ui.notify(f"Failed to load datacenters: {e}", type='negative')
    
    def set_status(self, message: str):
        """Update status bar message."""
        if self.status_label:
            self.status_label.set_text(message)
    
    def create_header(self):
        """Create the application header."""
        with ui.header().classes('bg-blue-800 text-white'):
            with ui.row().classes('w-full items-center'):
                ui.icon('public', size='lg').classes('mr-2')
                ui.label('Universus').classes('text-2xl font-bold')
                ui.label('FFXIV Market Tracker').classes('text-sm ml-2 opacity-75')
                
                ui.space()
                
                # Datacenter selector
                self.datacenter_select = ui.select(
                    options=self.datacenter_names if self.datacenter_names else ['Loading...'],
                    value=self.selected_datacenter if self.selected_datacenter else None,
                    label='Datacenter',
                    on_change=lambda e: self.change_datacenter(e.value) if e.value and e.value != 'Loading...' else None
                ).classes('w-40 bg-blue-700').props('dark dense outlined')
                
                # World selector - filtered by datacenter
                current_worlds = self.worlds_by_datacenter.get(self.selected_datacenter, self.worlds) if self.selected_datacenter else self.worlds
                self.world_select = ui.select(
                    options=current_worlds if current_worlds else ['Loading...'],
                    value=self.selected_world if self.selected_world else None,
                    label='World',
                    on_change=lambda e: self.change_world(e.value) if e.value and e.value != 'Loading...' else None
                ).classes('w-40 bg-blue-700').props('dark dense outlined')
                
                ui.button(icon='refresh', on_click=self.refresh_current_view).props('flat round').tooltip('Refresh')
    
    def create_sidebar(self):
        """Create the navigation sidebar."""
        with ui.left_drawer(value=True).classes('bg-gray-100') as drawer:
            ui.label('Navigation').classes('text-lg font-bold p-4')
            
            with ui.column().classes('w-full gap-0'):
                # Dashboard
                ui.button(
                    'Dashboard',
                    icon='dashboard',
                    on_click=lambda: self.show_view('dashboard')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Market Data').classes('text-sm text-gray-500 px-4 py-2')
                
                # Datacenters - equivalent to CLI: datacenters
                ui.button(
                    'Datacenters',
                    icon='dns',
                    on_click=lambda: self.show_view('datacenters')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Top Items - equivalent to CLI: top
                ui.button(
                    'Top Items',
                    icon='trending_up',
                    on_click=lambda: self.show_view('top')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Tracking').classes('text-sm text-gray-500 px-4 py-2')
                
                # Tracked Items - equivalent to CLI: list-tracked
                ui.button(
                    'Tracked Items',
                    icon='visibility',
                    on_click=lambda: self.show_view('tracked')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Init Tracking - equivalent to CLI: init-tracking
                ui.button(
                    'Initialize Tracking',
                    icon='add_circle',
                    on_click=lambda: self.show_view('init_tracking')
                ).classes('w-full justify-start').props('flat align=left')
                
                # Update - equivalent to CLI: update
                ui.button(
                    'Update Data',
                    icon='sync',
                    on_click=lambda: self.show_view('update')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Analysis').classes('text-sm text-gray-500 px-4 py-2')
                
                # Item Report - equivalent to CLI: report
                ui.button(
                    'Item Report',
                    icon='analytics',
                    on_click=lambda: self.show_view('report')
                ).classes('w-full justify-start').props('flat align=left')
                
                ui.separator()
                ui.label('Settings').classes('text-sm text-gray-500 px-4 py-2')
                
                # Sync Items - equivalent to CLI: sync-items
                ui.button(
                    'Sync Item Names',
                    icon='cloud_download',
                    on_click=lambda: self.show_view('sync_items')
                ).classes('w-full justify-start').props('flat align=left')
    
    def create_footer(self):
        """Create the application footer."""
        with ui.footer().classes('bg-gray-200'):
            with ui.row().classes('w-full items-center justify-between px-4'):
                self.status_label = ui.label('Ready').classes('text-sm text-gray-600')
                ui.label(f'Universus v{__version__} | Data from Universalis API').classes('text-sm text-gray-500')
    
    def create_main_content(self):
        """Create the main content area."""
        self.main_content = ui.column().classes('w-full p-6')
    
    def clear_main_content(self):
        """Clear the main content area."""
        if self.main_content:
            self.main_content.clear()
    
    def show_view(self, view: str):
        """Switch to a specific view."""
        self.current_view = view
        self.clear_main_content()
        
        with self.main_content:
            if view == 'dashboard':
                self.render_dashboard()
            elif view == 'datacenters':
                self.render_datacenters()
            elif view == 'top':
                self.render_top_items()
            elif view == 'tracked':
                self.render_tracked_items()
            elif view == 'init_tracking':
                self.render_init_tracking()
            elif view == 'update':
                self.render_update()
            elif view == 'report':
                self.render_report()
            elif view == 'sync_items':
                self.render_sync_items()
    
    async def refresh_current_view(self):
        """Refresh the current view."""
        self.show_view(self.current_view)
        ui.notify('View refreshed', type='info')
    
    def change_datacenter(self, datacenter: str):
        """Change the selected datacenter and update world list."""
        self.selected_datacenter = datacenter
        
        # Update world selector with worlds from this datacenter
        dc_worlds = self.worlds_by_datacenter.get(datacenter, [])
        if self.world_select:
            self.world_select.options = dc_worlds if dc_worlds else ['No worlds']
            # Select first world in datacenter if current selection is not valid
            if self.selected_world not in dc_worlds and dc_worlds:
                self.selected_world = dc_worlds[0]
                self.world_select.value = self.selected_world
            self.world_select.update()
        
        ui.notify(f'Datacenter changed to {datacenter}', type='info')
        self.show_view(self.current_view)
    
    def change_world(self, world: str):
        """Change the selected world."""
        self.selected_world = world
        ui.notify(f'World changed to {world}', type='info')
        self.show_view(self.current_view)
    
    # ==================== DASHBOARD VIEW ====================
    def render_dashboard(self):
        """Render the dashboard view."""
        ui.label('Dashboard').classes('text-2xl font-bold mb-4')
        
        if not self.selected_world:
            ui.label('Please select a world from the header dropdown.').classes('text-gray-500')
            return
        
        # Stats cards
        with ui.row().classes('w-full gap-4 mb-6'):
            tracked_items = db.get_tracked_items(self.selected_world) if self.selected_world else []
            tracked_count = len(tracked_items)
            items_synced = db.get_items_count()
            
            self._stat_card('Tracked Items', str(tracked_count), 'visibility', 'blue')
            self._stat_card('Items Database', f'{items_synced:,}', 'inventory_2', 'green')
            self._stat_card('Selected World', self.selected_world or 'None', 'public', 'purple')
            self._stat_card('Status', 'Online', 'wifi', 'teal')
        
        # Quick actions
        ui.label('Quick Actions').classes('text-xl font-semibold mb-2')
        with ui.row().classes('gap-4 mb-6'):
            ui.button('Update Market Data', icon='sync', on_click=lambda: self.show_view('update')).props('color=primary')
            ui.button('View Top Items', icon='trending_up', on_click=lambda: self.show_view('top')).props('color=secondary')
            ui.button('Initialize Tracking', icon='add_circle', on_click=lambda: self.show_view('init_tracking')).props('color=accent')
        
        # Recent tracked items preview
        if tracked_items:
            ui.label('Recently Updated Items').classes('text-xl font-semibold mb-2')
            columns = [
                {'name': 'item_id', 'label': 'Item ID', 'field': 'item_id', 'align': 'left'},
                {'name': 'item_name', 'label': 'Name', 'field': 'item_name', 'align': 'left'},
                {'name': 'world', 'label': 'World', 'field': 'world', 'align': 'left'},
                {'name': 'last_updated', 'label': 'Last Updated', 'field': 'last_updated', 'align': 'right'},
            ]
            rows = [
                {
                    'item_id': item['item_id'],
                    'item_name': item.get('item_name') or f"Item #{item['item_id']}",
                    'world': item['world'],
                    'last_updated': format_time_ago(item.get('last_updated', ''))
                }
                for item in tracked_items[:10]
            ]
            ui.table(columns=columns, rows=rows, row_key='item_id').classes('w-full')
    
    def _stat_card(self, title: str, value: str, icon: str, color: str):
        """Create a statistics card."""
        with ui.card().classes('w-64'):
            with ui.row().classes('items-center justify-between w-full'):
                with ui.column().classes('gap-0'):
                    ui.label(title).classes('text-sm text-gray-500')
                    ui.label(value).classes(f'text-2xl font-bold text-{color}-600')
                ui.icon(icon, size='xl').classes(f'text-{color}-400')
    
    # ==================== DATACENTERS VIEW (CLI: datacenters) ====================
    def render_datacenters(self):
        """Render the datacenters view - equivalent to CLI 'datacenters' command."""
        ui.label('FFXIV Datacenters').classes('text-2xl font-bold mb-4')
        ui.label('List of all available datacenters and their worlds.').classes('text-gray-500 mb-4')
        
        async def fetch_datacenters():
            self.set_status('Fetching datacenters...')
            try:
                ensure_api_connection()
                await self.load_datacenters()
                self.set_status('Ready')
                self._render_datacenters_table()
            except Exception as e:
                ui.notify(f'Error: {e}', type='negative')
                self.set_status('Error fetching datacenters')
        
        if self.datacenters:
            self._render_datacenters_table()
        else:
            ui.button('Fetch Datacenters', icon='refresh', on_click=fetch_datacenters).props('color=primary')
    
    def _render_datacenters_table(self):
        """Render the datacenters table."""
        if not self.datacenters:
            ui.label('No datacenters loaded.').classes('text-gray-500')
            return
        
        # Sort by region and name
        sorted_dcs = sorted(self.datacenters, key=lambda x: (x.get('region', ''), x.get('name', '')))
        
        columns = [
            {'name': 'name', 'label': 'Datacenter', 'field': 'name', 'align': 'left', 'sortable': True},
            {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left', 'sortable': True},
            {'name': 'worlds', 'label': 'Worlds', 'field': 'worlds', 'align': 'left'},
        ]
        
        rows = [
            {
                'name': dc.get('name', 'N/A'),
                'region': dc.get('region', 'N/A'),
                'worlds': ', '.join(
                    self.world_id_to_name.get(wid, str(wid)) 
                    for wid in dc.get('worlds', [])
                ) if dc.get('worlds') else 'No worlds'
            }
            for dc in sorted_dcs
        ]
        
        ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')
        ui.label(f'Total: {len(self.datacenters)} datacenters').classes('text-sm text-gray-500 mt-2')
    
    # ==================== TOP ITEMS VIEW (CLI: top) ====================
    def render_top_items(self):
        """Render the top items view - equivalent to CLI 'top' command."""
        ui.label('Top Selling Items').classes('text-2xl font-bold mb-4')
        
        if not self.selected_world:
            ui.label('Please select a world first.').classes('text-gray-500')
            return
        
        ui.label(f'Top items by sales volume on {self.selected_world}').classes('text-gray-500 mb-4')
        
        # Limit selector
        with ui.row().classes('items-end gap-4 mb-4'):
            limit_input = ui.number('Number of items', value=10, min=1, max=100).classes('w-32')
            
            async def fetch_top():
                self.set_status(f'Fetching top {int(limit_input.value)} items...')
                try:
                    ensure_api_connection()
                    top_items = service.get_top_items(self.selected_world, int(limit_input.value))
                    self._render_top_items_table(top_items)
                    self.set_status('Ready')
                except Exception as e:
                    ui.notify(f'Error: {e}', type='negative')
                    self.set_status('Error')
            
            ui.button('Fetch Top Items', icon='trending_up', on_click=fetch_top).props('color=primary')
        
        # Results container
        self.top_items_container = ui.column().classes('w-full')
    
    def _render_top_items_table(self, items: List[Dict]):
        """Render the top items table."""
        if hasattr(self, 'top_items_container'):
            self.top_items_container.clear()
        
        with self.top_items_container:
            if not items:
                ui.label(f'No data available for {self.selected_world}. Run "Update Data" first.').classes('text-yellow-600')
                return
            
            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                {'name': 'item_name', 'label': 'Item', 'field': 'item_name', 'align': 'left'},
                {'name': 'sale_velocity', 'label': 'Sales/Day', 'field': 'sale_velocity', 'align': 'right'},
                {'name': 'average_price', 'label': 'Avg Price', 'field': 'average_price', 'align': 'right'},
                {'name': 'last_updated', 'label': 'Updated', 'field': 'last_updated', 'align': 'right'},
            ]
            
            rows = [
                {
                    'rank': idx + 1,
                    'item_name': item.get('item_name') or str(item.get('item_id', 'Unknown')),
                    'sale_velocity': format_velocity(item.get('sale_velocity')),
                    'average_price': f"{format_gil(item.get('average_price'))} gil",
                    'last_updated': format_time_ago(item.get('last_updated', ''))
                }
                for idx, item in enumerate(items)
            ]
            
            ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')
            
            if items:
                ui.label(f'Snapshot date: {items[0].get("snapshot_date", "N/A")}').classes('text-sm text-gray-500 mt-2')
    
    # ==================== TRACKED ITEMS VIEW (CLI: list-tracked) ====================
    def render_tracked_items(self):
        """Render tracked items view - equivalent to CLI 'list-tracked' command."""
        ui.label('Tracked Items').classes('text-2xl font-bold mb-4')
        ui.label('All items being tracked across all worlds.').classes('text-gray-500 mb-4')
        
        by_world = service.get_all_tracked_items()
        
        if not by_world:
            with ui.card().classes('w-full bg-yellow-50'):
                ui.label('No items being tracked.').classes('text-yellow-700')
                ui.label('Use "Initialize Tracking" to start tracking items.').classes('text-sm text-yellow-600')
            return
        
        for world, items in sorted(by_world.items()):
            with ui.expansion(f'{world} ({len(items)} items)', icon='public').classes('w-full mb-2'):
                columns = [
                    {'name': 'item_id', 'label': 'Item ID', 'field': 'item_id', 'align': 'left'},
                    {'name': 'item_name', 'label': 'Name', 'field': 'item_name', 'align': 'left'},
                    {'name': 'first_tracked', 'label': 'First Tracked', 'field': 'first_tracked', 'align': 'right'},
                    {'name': 'last_updated', 'label': 'Last Updated', 'field': 'last_updated', 'align': 'right'},
                ]
                
                rows = [
                    {
                        'item_id': item['item_id'],
                        'item_name': item.get('item_name') or f"Item #{item['item_id']}",
                        'first_tracked': item.get('first_tracked', 'N/A')[:10] if item.get('first_tracked') else 'N/A',
                        'last_updated': format_time_ago(item.get('last_updated', ''))
                    }
                    for item in items
                ]
                
                ui.table(columns=columns, rows=rows, row_key='item_id').classes('w-full')
    
    # ==================== INIT TRACKING VIEW (CLI: init-tracking) ====================
    def render_init_tracking(self):
        """Render init tracking view - equivalent to CLI 'init-tracking' command."""
        ui.label('Initialize Tracking').classes('text-2xl font-bold mb-4')
        ui.label('Start tracking the top volume items on a world.').classes('text-gray-500 mb-4')
        
        if not self.selected_world:
            ui.label('Please select a world first.').classes('text-yellow-600')
            return
        
        with ui.card().classes('w-full max-w-xl'):
            ui.label('Configuration').classes('text-lg font-semibold mb-2')
            
            ui.label(f'World: {self.selected_world}').classes('text-gray-600')
            
            limit_input = ui.number(
                'Number of items to track',
                value=config.get('cli', 'default_tracking_limit', 50),
                min=1,
                max=200
            ).classes('w-full')
            
            ui.label('This will analyze recently updated items and track those with the highest sales velocity.').classes('text-sm text-gray-500 mt-2')
            
            # Progress area
            progress_container = ui.column().classes('w-full mt-4')
            
            async def start_tracking():
                with progress_container:
                    progress_container.clear()
                    
                    with ui.card().classes('w-full bg-blue-50'):
                        ui.label('Initializing tracking...').classes('text-blue-700 font-semibold')
                        progress = ui.linear_progress(value=0).classes('w-full')
                        status_text = ui.label('Starting...').classes('text-sm text-blue-600')
                    
                    self.set_status('Initializing tracking...')
                    
                    try:
                        # Ensure fresh API connection before long operation
                        ensure_api_connection()
                        
                        status_text.set_text('Fetching market data...')
                        progress.set_value(0.3)
                        await asyncio.sleep(0.1)
                        
                        # Run the tracking initialization
                        top_items, total_found, items_with_sales = service.initialize_tracking(
                            self.selected_world, 
                            int(limit_input.value)
                        )
                        
                        progress.set_value(1.0)
                        status_text.set_text('Complete!')
                        
                        await asyncio.sleep(0.5)
                        progress_container.clear()
                        
                        if not top_items:
                            with progress_container:
                                ui.label(f'No items with sales data found for {self.selected_world}').classes('text-yellow-600')
                        else:
                            with progress_container:
                                ui.label(f'✓ Successfully initialized tracking for {len(top_items)} items').classes('text-green-600 font-semibold')
                                
                                # Show results table
                                columns = [
                                    {'name': 'item_id', 'label': 'Item ID', 'field': 'item_id', 'align': 'left'},
                                    {'name': 'velocity', 'label': 'Sales/Day', 'field': 'velocity', 'align': 'right'},
                                    {'name': 'avg_price', 'label': 'Avg Price', 'field': 'avg_price', 'align': 'right'},
                                ]
                                rows = [
                                    {
                                        'item_id': item['item_id'],
                                        'velocity': f"{item['velocity']:.2f}",
                                        'avg_price': f"{format_gil(item['avg_price'])} gil"
                                    }
                                    for item in top_items[:20]
                                ]
                                ui.table(columns=columns, rows=rows, row_key='item_id').classes('w-full mt-4')
                                
                                if len(top_items) > 20:
                                    ui.label(f'...and {len(top_items) - 20} more items').classes('text-sm text-gray-500')
                        
                        self.set_status('Ready')
                        ui.notify(f'Tracking initialized for {len(top_items)} items', type='positive')
                        
                    except Exception as e:
                        progress_container.clear()
                        with progress_container:
                            ui.label(f'Error: {e}').classes('text-red-600')
                        self.set_status('Error')
                        ui.notify(f'Error: {e}', type='negative')
            
            ui.button('Start Tracking', icon='play_arrow', on_click=start_tracking).props('color=primary').classes('mt-4')
    
    # ==================== UPDATE VIEW (CLI: update) ====================
    def render_update(self):
        """Render update view - equivalent to CLI 'update' command."""
        ui.label('Update Market Data').classes('text-2xl font-bold mb-4')
        ui.label('Fetch latest market data for all tracked items.').classes('text-gray-500 mb-4')
        
        if not self.selected_world:
            ui.label('Please select a world first.').classes('text-yellow-600')
            return
        
        tracked_count = db.get_tracked_items_count(self.selected_world)
        
        with ui.card().classes('w-full max-w-xl'):
            ui.label(f'World: {self.selected_world}').classes('text-lg font-semibold')
            ui.label(f'Tracked items: {tracked_count}').classes('text-gray-600')
            
            if tracked_count == 0:
                ui.label('No items tracked for this world. Run "Initialize Tracking" first.').classes('text-yellow-600 mt-2')
                return
            
            estimated_time = tracked_count // 2  # 2 requests per second
            ui.label(f'Estimated time: ~{estimated_time} seconds').classes('text-sm text-gray-500')
            ui.label('Rate limit: 2 requests/second (respecting API limits)').classes('text-sm text-gray-400')
            
            # Progress area
            progress_container = ui.column().classes('w-full mt-4')
            
            async def start_update():
                with progress_container:
                    progress_container.clear()
                    
                    with ui.card().classes('w-full bg-blue-50'):
                        ui.label('Updating market data...').classes('text-blue-700 font-semibold')
                        progress = ui.linear_progress(value=0).classes('w-full')
                        status_text = ui.label('Starting...').classes('text-sm text-blue-600')
                    
                    self.set_status('Updating market data...')
                    
                    try:
                        # Ensure fresh API connection before long operation
                        ensure_api_connection()
                        
                        status_text.set_text('Fetching market data and history...')
                        progress.set_value(0.1)
                        
                        # Run the update
                        successful, failed, tracked_items = service.update_tracked_items(self.selected_world)
                        
                        progress.set_value(1.0)
                        status_text.set_text('Complete!')
                        
                        await asyncio.sleep(0.5)
                        progress_container.clear()
                        
                        with progress_container:
                            if successful > 0:
                                ui.label(f'✓ Successfully updated {successful} items').classes('text-green-600 font-semibold')
                            if failed > 0:
                                ui.label(f'⚠ Failed to update {failed} items').classes('text-yellow-600')
                            
                            ui.label('Tip: Schedule this command daily via cron/Task Scheduler').classes('text-sm text-gray-500 mt-2')
                        
                        self.set_status('Ready')
                        ui.notify(f'Updated {successful} items ({failed} failed)', type='positive' if failed == 0 else 'warning')
                        
                    except Exception as e:
                        progress_container.clear()
                        with progress_container:
                            ui.label(f'Error: {e}').classes('text-red-600')
                        self.set_status('Error')
                        ui.notify(f'Error: {e}', type='negative')
            
            ui.button('Update Now', icon='sync', on_click=start_update).props('color=primary').classes('mt-4')
    
    # ==================== REPORT VIEW (CLI: report) ====================
    def render_report(self):
        """Render item report view - equivalent to CLI 'report' command."""
        ui.label('Item Report').classes('text-2xl font-bold mb-4')
        ui.label('View detailed historical report for a specific item.').classes('text-gray-500 mb-4')
        
        if not self.selected_world:
            ui.label('Please select a world first.').classes('text-yellow-600')
            return
        
        with ui.card().classes('w-full max-w-xl'):
            ui.label('Report Parameters').classes('text-lg font-semibold mb-2')
            
            item_id_input = ui.number('Item ID', value=0, min=1).classes('w-full')
            days_input = ui.number(
                'Days of history',
                value=config.get('cli', 'default_report_days', 30),
                min=1,
                max=365
            ).classes('w-full')
            
            # Results container
            report_container = ui.column().classes('w-full mt-4')
            
            async def generate_report():
                item_id = int(item_id_input.value)
                days = int(days_input.value)
                
                if item_id <= 0:
                    ui.notify('Please enter a valid Item ID', type='warning')
                    return
                
                report_container.clear()
                
                self.set_status(f'Generating report for item {item_id}...')
                
                try:
                    ensure_api_connection()
                    snapshots = service.get_item_report(self.selected_world, item_id, days)
                    
                    with report_container:
                        if not snapshots:
                            ui.label(f'No data available for item {item_id} on {self.selected_world}').classes('text-yellow-600')
                            return
                        
                        # Header
                        item_name = db.get_item_name(item_id) or f"Item #{item_id}"
                        ui.label(f'{item_name}').classes('text-xl font-bold')
                        ui.label(f'{self.selected_world} • {len(snapshots)} days of data').classes('text-gray-500 mb-4')
                        
                        # Trends
                        trends = service.calculate_trends(snapshots)
                        if trends:
                            with ui.row().classes('gap-4 mb-4'):
                                if 'velocity_change' in trends:
                                    change = trends['velocity_change']
                                    color = 'green' if change > 0 else 'red'
                                    icon = '📈' if change > 0 else '📉'
                                    ui.label(f'{icon} Sales velocity: {change:+.1f}%').classes(f'text-{color}-600')
                                
                                if 'price_change' in trends:
                                    change = trends['price_change']
                                    color = 'green' if change > 0 else 'red'
                                    icon = '💰' if change > 0 else '💸'
                                    ui.label(f'{icon} Price: {change:+.1f}%').classes(f'text-{color}-600')
                        
                        # Data table
                        columns = [
                            {'name': 'date', 'label': 'Date', 'field': 'date', 'align': 'left'},
                            {'name': 'velocity', 'label': 'Sales/Day', 'field': 'velocity', 'align': 'right'},
                            {'name': 'avg_price', 'label': 'Avg Price', 'field': 'avg_price', 'align': 'right'},
                            {'name': 'min_price', 'label': 'Min Price', 'field': 'min_price', 'align': 'right'},
                            {'name': 'max_price', 'label': 'Max Price', 'field': 'max_price', 'align': 'right'},
                            {'name': 'listings', 'label': 'Listings', 'field': 'listings', 'align': 'right'},
                        ]
                        
                        rows = [
                            {
                                'date': s['snapshot_date'],
                                'velocity': format_velocity(s.get('sale_velocity')),
                                'avg_price': format_gil(s.get('average_price')),
                                'min_price': format_gil(s.get('min_price')),
                                'max_price': format_gil(s.get('max_price')),
                                'listings': s.get('total_listings', 0)
                            }
                            for s in reversed(snapshots)
                        ]
                        
                        ui.table(columns=columns, rows=rows, row_key='date', pagination={'rowsPerPage': 15}).classes('w-full')
                    
                    self.set_status('Ready')
                    
                except Exception as e:
                    with report_container:
                        ui.label(f'Error: {e}').classes('text-red-600')
                    self.set_status('Error')
                    ui.notify(f'Error: {e}', type='negative')
            
            ui.button('Generate Report', icon='analytics', on_click=generate_report).props('color=primary').classes('mt-4')
    
    # ==================== SYNC ITEMS VIEW (CLI: sync-items) ====================
    def render_sync_items(self):
        """Render sync items view - equivalent to CLI 'sync-items' command."""
        ui.label('Sync Item Names').classes('text-2xl font-bold mb-4')
        ui.label('Download and sync item names from FFXIV Teamcraft.').classes('text-gray-500 mb-4')
        
        current_count = db.get_items_count()
        
        with ui.card().classes('w-full max-w-xl'):
            ui.label('Item Database').classes('text-lg font-semibold mb-2')
            ui.label(f'Current items in database: {current_count:,}').classes('text-gray-600')
            
            ui.label('This will fetch ~47,000 item names from FFXIV Teamcraft and update the local database.').classes('text-sm text-gray-500 mt-2')
            ui.label('Any existing items will be replaced.').classes('text-sm text-gray-400')
            
            # Progress area
            progress_container = ui.column().classes('w-full mt-4')
            
            async def start_sync():
                with progress_container:
                    progress_container.clear()
                    
                    with ui.card().classes('w-full bg-blue-50'):
                        ui.label('Syncing items...').classes('text-blue-700 font-semibold')
                        progress = ui.linear_progress(show_value=False).props('indeterminate')
                        status_text = ui.label('Fetching from FFXIV Teamcraft (this may take a moment)...').classes('text-sm text-blue-600')
                    
                    self.set_status('Syncing items...')
                    
                    try:
                        # Ensure fresh API connection before long operation
                        ensure_api_connection()
                        
                        # Run the sync
                        count = service.sync_items_database()
                        
                        await asyncio.sleep(0.5)
                        progress_container.clear()
                        
                        with progress_container:
                            ui.label(f'✓ Successfully synced {count:,} items to local database').classes('text-green-600 font-semibold')
                        
                        self.set_status('Ready')
                        ui.notify(f'Synced {count:,} items', type='positive')
                        
                    except Exception as e:
                        progress_container.clear()
                        with progress_container:
                            ui.label(f'Error: {e}').classes('text-red-600')
                        self.set_status('Error')
                        ui.notify(f'Error: {e}', type='negative')
            
            ui.button('Sync Now', icon='cloud_download', on_click=start_sync).props('color=primary').classes('mt-4')
    
    async def initialize(self):
        """Initialize the GUI with data."""
        await self.load_datacenters()
        
        # Update datacenter selector
        if self.datacenter_select and self.datacenter_names:
            self.datacenter_select.options = self.datacenter_names
            self.datacenter_select.value = self.selected_datacenter
            self.datacenter_select.update()
        
        # Update world selector with worlds from selected datacenter
        if self.world_select:
            dc_worlds = self.worlds_by_datacenter.get(self.selected_datacenter, self.worlds)
            self.world_select.options = dc_worlds if dc_worlds else self.worlds
            self.world_select.value = self.selected_world
            self.world_select.update()
    
    def build(self):
        """Build the complete GUI."""
        self.create_header()
        self.create_sidebar()
        self.create_main_content()
        self.create_footer()
        
        # Show initial view
        self.show_view('dashboard')


# Create global GUI instance
gui = UniversusGUI()


@ui.page('/')
async def main_page():
    """Main page entry point."""
    gui.build()
    await gui.initialize()


def main():
    """Main entry point for the GUI."""
    init_services()
    
    ui.run(
        title='Universus - FFXIV Market Tracker',
        port=8080,
        reload=False,
        show=True,
        favicon='🌍'
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
