"""
Dashboard view.

Provides an overview of market data and key metrics.
Uses the unified design system for consistent styling.
"""

from nicegui import ui
from ..utils.formatters import format_time_ago
from ..utils.design_system import STYLES, heading_classes, TABLE_SLOTS
from ..components.cards import stat_card, stat_card_hq, stat_card_nq
from ..utils.icons import GameIcons, SpriteIcon


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
        dark_mode: Ignored (always dark mode)
    """
    # Page title
    ui.label('Dashboard').classes(heading_classes(2))
    
    # Get world_id for selected world
    world_id = None
    if state.selected_world and state.world_id_to_name:
        for wid, wname in state.world_id_to_name.items():
            if wname == state.selected_world:
                world_id = wid
                break
    
    # Stats cards row
    with ui.row().classes('w-full gap-4 mb-6 flex-wrap'):
        # Tracked Worlds count
        tracked_worlds_count = service.get_tracked_worlds_count()
        stat_card('Tracked Worlds', format_number(tracked_worlds_count), GameIcons.WORLD, accent='blue')
        
        # Current Prices count
        if world_id:
            current_prices_count = service.get_current_prices_count(world_id)
        else:
            current_prices_count = service.get_current_prices_count()
        stat_card('Current Prices', format_number(current_prices_count), GameIcons.SCROLL, accent='green')
        
        # Latest Price Timestamp
        if world_id:
            latest_timestamp = service.get_latest_current_price_timestamp(world_id)
        else:
            latest_timestamp = service.get_latest_current_price_timestamp()
        
        timestamp_display = format_time_ago(latest_timestamp) if latest_timestamp else 'No data'
        stat_card('Latest Update', timestamp_display, GameIcons.CLOCK, accent='purple')
        
        # Marketable Items Database
        marketable_count = service.get_marketable_items_count()
        stat_card('Marketable Items', format_number(marketable_count), GameIcons.TREASURE, accent='teal')
    
    # World-specific data section
    if state.selected_world and world_id:
        # Section heading
        ui.label(f'{state.selected_world} Market Analysis').classes(heading_classes(3))
        
        # Gil volume stats
        volume_data = service.get_datacenter_gil_volume(world_id)
        
        with ui.row().classes('w-full gap-4 mb-6 flex-wrap'):
            stat_card_hq('HQ Gil Volume', format_gil(volume_data['hq_volume']), GameIcons.TRENDING)
            stat_card_nq('NQ Gil Volume', format_gil(volume_data['nq_volume']), GameIcons.CHART_BAR)
            stat_card('Total Gil Volume', format_gil(volume_data['total_volume']), GameIcons.GOLD, accent='red')
        
        # Top 10 items by HQ velocity
        ui.label('Top 10 Items by HQ Velocity').classes(heading_classes(3))
        
        top_items = service.get_top_items_by_hq_velocity(world_id, limit=10)
        
        if top_items:
            columns = [
                {'name': 'rank', 'label': '#', 'field': 'rank', 'align': 'center'},
                {'name': 'item_name', 'label': 'Item', 'field': 'item_name', 'align': 'left'},
                {'name': 'hq_velocity', 'label': 'HQ Vel/Day', 'field': 'hq_velocity', 'align': 'right'},
                {'name': 'hq_avg_price', 'label': 'HQ Avg Price', 'field': 'hq_avg_price', 'align': 'right'},
                {'name': 'hq_volume', 'label': 'HQ Gil Volume', 'field': 'hq_volume', 'align': 'right'},
                {'name': 'nq_velocity', 'label': 'NQ Vel/Day', 'field': 'nq_velocity', 'align': 'right'},
            ]
            rows = [
                {
                    'rank': idx + 1,
                    'item_id': item['item_id'],
                    'item_name': item.get('item_name') or f"Item #{item['item_id']}",
                    'icon_style': SpriteIcon.get_icon_style(item['item_id'], size=40),
                    'hq_velocity': format_decimal(item['hq_world_daily_velocity'], 1),
                    'hq_avg_price': format_gil(item['hq_world_avg_price']),
                    'hq_volume': format_gil(item['hq_gil_volume']),
                    'nq_velocity': format_decimal(item['nq_region_daily_velocity'], 1) if item['nq_region_daily_velocity'] else 'N/A',
                }
                for idx, item in enumerate(top_items)
            ]
            table = ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')
            
            # Add styled slots for HQ/NQ values with icon for item name
            table.add_slot('body-cell-item_name', TABLE_SLOTS.item_name_with_icon_slot())
            table.add_slot('body-cell-hq_velocity', '''
                <q-td :props="props">
                    <span class="hq-accent font-semibold">{{ props.value }}</span>
                </q-td>
            ''')
            table.add_slot('body-cell-hq_avg_price', '''
                <q-td :props="props">
                    <span class="hq-accent">{{ props.value }}</span>
                </q-td>
            ''')
            table.add_slot('body-cell-hq_volume', '''
                <q-td :props="props">
                    <span class="hq-accent font-bold">{{ props.value }}</span>
                </q-td>
            ''')
            table.add_slot('body-cell-nq_velocity', '''
                <q-td :props="props">
                    <span :class="props.value === 'N/A' ? 'text-gray-500' : 'nq-accent'">{{ props.value }}</span>
                </q-td>
            ''')
        else:
            ui.label('No price data available. Run "Update Market Data" to fetch current prices.').classes('text-gray-400')
    else:
        with ui.card().classes('w-full p-6'):
            with ui.row().classes('items-center gap-2'):
                ui.icon('info').classes('text-blue-400')
                ui.label('Select a world from the header dropdown to view market analysis.').classes('text-gray-400')
    
    return None, None, None

