"""
Dashboard view.
"""

from nicegui import ui
from ..utils.formatters import format_time_ago
from ..components.cards import stat_card
from ..utils.icons import GameIcons


def format_number(num):
    """Format number with thousand separators."""
    if num is None:
        return 'N/A'
    return f'{int(num):,}'


def format_gil(amount):
    """Format gil amount with separators."""
    if amount is None or amount == 0:
        return '0 gil'
    return f'{int(amount):,} gil'


def format_decimal(num, decimals=2):
    """Format decimal number with thousand separators."""
    if num is None:
        return 'N/A'
    return f'{num:,.{decimals}f}'


def render(state, service, dark_mode: bool = False):
    """Render the dashboard view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is active
    """
    title_class = 'text-2xl font-bold mb-4 text-gray-900' if not dark_mode else 'text-2xl font-bold mb-4 text-white'
    label_class = 'text-gray-500' if not dark_mode else 'text-gray-400'
    actions_class = 'text-xl font-semibold mb-2 text-gray-900' if not dark_mode else 'text-xl font-semibold mb-2 text-white'
    
    ui.label('Dashboard').classes(title_class)
    
    # Get world_id for selected world
    world_id = None
    if state.selected_world and state.world_id_to_name:
        # Reverse lookup to get world_id from name
        for wid, wname in state.world_id_to_name.items():
            if wname == state.selected_world:
                world_id = wid
                break
    
    # Stats cards - NEW TRACKERS
    with ui.row().classes('w-full gap-4 mb-6'):
        # Tracked Worlds count
        tracked_worlds_count = service.get_tracked_worlds_count()
        stat_card('Tracked Worlds', format_number(tracked_worlds_count), GameIcons.WORLD, 'blue', dark_mode)
        
        # Current Prices count (for selected world if available)
        if world_id:
            current_prices_count = service.get_current_prices_count(world_id)
            stat_card('Current Prices', format_number(current_prices_count), GameIcons.SCROLL, 'green', dark_mode)
        else:
            current_prices_count = service.get_current_prices_count()
            stat_card('Current Prices', format_number(current_prices_count), GameIcons.SCROLL, 'green', dark_mode)
        
        # Latest Price Timestamp
        if world_id:
            latest_timestamp = service.get_latest_current_price_timestamp(world_id)
        else:
            latest_timestamp = service.get_latest_current_price_timestamp()
        
        timestamp_display = format_time_ago(latest_timestamp) if latest_timestamp else 'No data'
        stat_card('Latest Update', timestamp_display, GameIcons.CLOCK, 'purple', dark_mode)
        
        # Marketable Items Database
        marketable_count = service.get_marketable_items_count()
        stat_card('Marketable Items', format_number(marketable_count), GameIcons.TREASURE, 'teal', dark_mode)
    
    # World-specific data section
    if state.selected_world and world_id:
        # Datacenter Gil Volume Widget
        ui.label(f'{state.selected_world} Market Analysis').classes(actions_class + ' mt-6')
        
        volume_data = service.get_datacenter_gil_volume(world_id)
        
        with ui.row().classes('w-full gap-4 mb-6'):
            stat_card('HQ Gil Volume', format_gil(volume_data['hq_volume']), GameIcons.TRENDING, 'amber', dark_mode)
            stat_card('NQ Gil Volume', format_gil(volume_data['nq_volume']), GameIcons.CHART_BAR, 'orange', dark_mode)
            stat_card('Total Gil Volume', format_gil(volume_data['total_volume']), GameIcons.GOLD, 'red', dark_mode)
        
        # Top 10 items by HQ velocity
        ui.label('Top 10 Items by HQ Velocity').classes(actions_class + ' mt-6')
        
        top_items = service.get_top_items_by_hq_velocity(world_id, limit=10)
        
        if top_items:
            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                {'name': 'item_name', 'label': 'Item', 'field': 'item_name', 'align': 'left'},
                {'name': 'hq_velocity', 'label': 'HQ Velocity', 'field': 'hq_velocity', 'align': 'right'},
                {'name': 'hq_avg_price', 'label': 'HQ Avg Price', 'field': 'hq_avg_price', 'align': 'right'},
                {'name': 'hq_volume', 'label': 'HQ Gil Volume', 'field': 'hq_volume', 'align': 'right'},
                {'name': 'nq_velocity', 'label': 'NQ Velocity', 'field': 'nq_velocity', 'align': 'right'},
            ]
            rows = [
                {
                    'rank': idx + 1,
                    'item_name': item.get('item_name') or f"Item #{item['item_id']}",
                    'hq_velocity': format_decimal(item['hq_world_daily_velocity'], 1),
                    'hq_avg_price': format_gil(item['hq_world_avg_price']),
                    'hq_volume': format_gil(item['hq_gil_volume']),
                    'nq_velocity': format_decimal(item['nq_region_daily_velocity'], 1) if item['nq_region_daily_velocity'] else 'N/A',
                }
                for idx, item in enumerate(top_items)
            ]
            ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')
        else:
            ui.label('No price data available. Run "Update Market Data" to fetch current prices.').classes(label_class)
    else:
        ui.label('Please select a world from the header dropdown to view market analysis.').classes(label_class)
    
    return None, None, None

