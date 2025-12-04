"""
Reports views (item report, sell volume, charts).

Uses the unified design system for consistent styling.
"""

import asyncio
from nicegui import ui
from ..utils.formatters import format_gil, format_velocity
from ..utils.design_system import heading_classes, PROPS
from ..components.cards import warning_card
from config import get_config

config = get_config()


def render_item_report(state, service, dark_mode: bool = False):
    """Render item report view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    
    Returns:
        Tuple of (item_id_input, days_input, report_container)
    """
    ui.label('Item Report').classes(heading_classes(2))
    ui.label('View detailed historical report for a specific item.').classes('text-gray-400 mb-6')
    
    if not state.selected_world:
        warning_card('No world selected', 'Please select a world from the header dropdown.')
        return None, None, None
    
    with ui.card().classes('w-full max-w-xl p-4'):
        ui.label('Report Parameters').classes('text-lg font-semibold text-white mb-4')
        
        item_id_input = ui.number('Item ID', value=0, min=1).classes('w-full')
        days_input = ui.number(
            'Days of history',
            value=config.get('cli', 'default_report_days', 30),
            min=1,
            max=365
        ).classes('w-full')
        
        report_container = ui.column().classes('w-full mt-4')
    
    return item_id_input, days_input, report_container


def generate_item_report(state, service, item_id, days, container, set_status):
    """Generate item report.
    
    Args:
        state: Application state
        service: Market service instance
        item_id: Item ID to report on
        days: Number of days of history
        container: UI container
        set_status: Status callback
    """
    container.clear()
    set_status(f'Generating report for item {item_id}...')
    
    try:
        snapshots = service.get_item_report(state.selected_world, item_id, days)
        
        with container:
            if not snapshots:
                warning_card('No data available', f'No data available for item {item_id} on {state.selected_world}')
                return
            
            item_name = service.get_item_name(item_id) or f"Item #{item_id}"
            ui.label(f'{item_name}').classes('text-xl font-bold text-white')
            ui.label(f'{state.selected_world} • {len(snapshots)} days of data').classes('text-gray-400 mb-4')
            
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
            
            report_table = ui.table(columns=columns, rows=rows, row_key='date', pagination={'rowsPerPage': 15}).classes('w-full')
            
            # Add slot templates for styled columns
            report_table.add_slot('body-cell-velocity', '''
                <q-td :props="props" class="metric-highlight text-weight-bold">{{ props.row.velocity }}</q-td>
            ''')
            report_table.add_slot('body-cell-min_price', '''
                <q-td :props="props" class="metric-price text-weight-bold">{{ props.row.min_price }}</q-td>
            ''')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-500')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')


def render_sell_volume(state, service, dark_mode: bool = False):
    """Render sell volume by world report.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    
    Returns:
        Tuple of (world_options, world_select, limit_input, report_container)
    """
    ui.label('Sell Volume by World').classes(heading_classes(2))
    ui.label('Top items by HQ sales velocity for selected tracked world.').classes('text-gray-400 mb-6')
    
    tracked = service.list_tracked_worlds()
    if not tracked:
        warning_card('No tracked worlds configured', 'Add tracked worlds in Settings > Tracked Worlds first.')
        return None, None, None, None
    
    world_options = {}
    for w in tracked:
        world_id = w.get('world_id')
        world_name = w.get('world_name') or state.world_id_to_name.get(world_id, f"World {world_id}")
        world_options[world_name] = world_id
    
    # Sticky filter card
    with ui.card().classes('w-full max-w-xl p-4 sticky top-0 z-10').style('position: sticky; top: 0;'):
        ui.label('Filters').classes('text-lg font-semibold text-white mb-4')
        
        selected_world_name = list(world_options.keys())[0] if world_options else None
        world_select = ui.select(
            options=list(world_options.keys()),
            value=selected_world_name,
            label='Tracked World'
        ).classes('w-full').props(PROPS.SELECT_OUTLINED)
        
        limit_input = ui.number('Limit', value=100, min=1, max=500).classes('w-full')
        report_container = ui.column().classes('w-full mt-4')
    
    return world_options, world_select, limit_input, report_container


def generate_sell_volume_report(state, service, world_options, world_name, limit, container, set_status):
    """Generate sell volume report.
    
    Args:
        state: Application state
        service: Market service instance
        world_options: World name to ID mapping
        world_name: Selected world name
        limit: Number of items to show
        container: UI container
        set_status: Status callback
    """
    container.clear()
    if not world_name or world_name not in world_options:
        ui.notify('Please select a valid tracked world', type='warning')
        return
    
    wid = world_options[world_name]
    set_status(f'Generating report for {world_name}...')
    
    try:
        results = service.get_sell_volume_report(wid, limit)
        
        with container:
            if not results:
                warning_card('No data available', f'No data available for {world_name}. Run "Update Current Prices" CLI command first.')
                return
            
            ui.label(f'Top {len(results)} items by HQ daily velocity on {world_name}').classes('text-lg font-semibold text-white mb-4')
            
            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                {'name': 'item_name', 'label': 'Item Name', 'field': 'item_name', 'align': 'left'},
                {'name': 'hq_velocity', 'label': 'HQ Daily Velocity', 'field': 'hq_velocity', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'hq_recent_price', 'label': 'HQ Recent Price', 'field': 'hq_recent_price', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'hq_avg_price', 'label': 'HQ Avg Price', 'field': 'hq_avg_price', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'hq_min_price', 'label': 'HQ Min Price', 'field': 'hq_min_price', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'gil_volume', 'label': 'Gil Volume', 'field': 'gil_volume', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
            ]
            
            rows = []
            for idx, item in enumerate(results, start=1):
                rows.append({
                    'rank': idx,
                    'item_name': item['item_name'],
                    'hq_velocity': item['hq_velocity'],
                    'hq_velocity_fmt': format_velocity(item['hq_velocity']),
                    'hq_recent_price': format_gil(item['hq_recent_price']),
                    'hq_avg_price': format_gil(item['hq_avg_price']),
                    'hq_min_price': item['hq_min_price'],
                    'hq_min_price_fmt': format_gil(item['hq_min_price']),
                    'gil_volume': format_gil(item['gil_volume']),
                })
            
            table = ui.table(columns=columns, rows=rows, row_key='rank', pagination={'rowsPerPage': 20}).classes('w-full')
            
            # Add header tooltips
            table.add_slot('header-cell-hq_velocity', '''
                <q-th :props="props">
                    <span>HQ Daily Velocity</span>
                    <q-tooltip class="bg-grey-8 text-body2">HQ Velocity: Average High Quality items sold per day</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-hq_recent_price', '''
                <q-th :props="props">
                    <span>HQ Recent Price</span>
                    <q-tooltip class="bg-grey-8 text-body2">Most recent sale price for HQ items</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-hq_avg_price', '''
                <q-th :props="props">
                    <span>HQ Avg Price</span>
                    <q-tooltip class="bg-grey-8 text-body2">Average sale price for HQ items</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-hq_min_price', '''
                <q-th :props="props">
                    <span>HQ Min Price</span>
                    <q-tooltip class="bg-grey-8 text-body2">Lowest current listing price for HQ items</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-gil_volume', '''
                <q-th :props="props">
                    <span>Gil Volume</span>
                    <q-tooltip class="bg-grey-8 text-body2">Estimated daily gil traded (velocity × price)</q-tooltip>
                </q-th>
            ''')
            
            # Add slot templates for styled columns with zero-value highlighting
            table.add_slot('body-cell-item_name', '''
                <q-td :props="props" class="text-weight-bold" style="font-size: 1.05rem;">{{ props.row.item_name }}</q-td>
            ''')
            table.add_slot('body-cell-hq_velocity', '''
                <q-td :props="props" :class="props.row.hq_velocity == 0 ? 'text-grey-5' : ''">
                    <q-icon v-if="props.row.hq_velocity == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                        <q-tooltip>No HQ sales recorded</q-tooltip>
                    </q-icon>
                    {{ props.row.hq_velocity_fmt }}
                </q-td>
            ''')
            table.add_slot('body-cell-hq_min_price', '''
                <q-td :props="props" :class="props.row.hq_min_price == 0 ? 'text-grey-5' : 'metric-price text-weight-bold'">
                    <q-icon v-if="props.row.hq_min_price == 0" name="remove_shopping_cart" class="text-grey-5 q-mr-xs" size="xs">
                        <q-tooltip>No HQ listings available</q-tooltip>
                    </q-icon>
                    {{ props.row.hq_min_price_fmt }}
                </q-td>
            ''')
            table.add_slot('body-cell-gil_volume', '''
                <q-td :props="props" class="metric-volume text-weight-bold">{{ props.row.gil_volume }}</q-td>
            ''')
            
            ui.label(f'Showing {len(results)} items').classes('text-sm text-gray-400 mt-2')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-500')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')


def render_sell_volume_chart(state, service, dark_mode: bool = False):
    """Render sell volume chart view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    
    Returns:
        Tuple of (world_options, world_select, chart_container)
    """
    ui.label('Sell Volume Chart').classes(heading_classes(2))
    ui.label('Visualization of top 10 items by HQ gil volume.').classes('text-gray-400 mb-6')
    
    tracked = service.list_tracked_worlds()
    if not tracked:
        warning_card('No tracked worlds configured', 'Add tracked worlds first to view chart.')
        return None, None, None
    
    world_options = {}
    for w in tracked:
        wid = w.get('world_id')
        wname = w.get('world_name') or state.world_id_to_name.get(wid, f"World {wid}")
        world_options[wname] = wid
    
    with ui.card().classes('w-full max-w-xl p-4'):
        ui.label('Filters').classes('text-lg font-semibold text-white mb-4')
        selected_world_name = list(world_options.keys())[0] if world_options else None
        world_select = ui.select(
            options=list(world_options.keys()), 
            value=selected_world_name, 
            label='Tracked World'
        ).classes('w-full').props(PROPS.SELECT_OUTLINED)
        
        chart_container = ui.column().classes('w-full mt-4')
    
    return world_options, world_select, chart_container


def generate_chart(state, service, world_options, world_name, container, set_status):
    """Generate sell volume chart.
    
    Args:
        state: Application state
        service: Market service instance
        world_options: World name to ID mapping
        world_name: Selected world name
        container: UI container
        set_status: Status callback
    """
    container.clear()
    if not world_name:
        ui.notify('Select a tracked world', type='warning')
        return
    
    wid = world_options.get(world_name)
    set_status(f'Building chart for {world_name}...')
    
    try:
        data_points = service.get_sell_volume_chart_data(wid)
        
        if not data_points:
            with container:
                warning_card('No data available', 'No data available. Run price update first.')
            set_status('Ready')
            return
        
        total_volume = sum(item['gil_volume'] for item in data_points)
        
        with container:
            ui.label(f'Top 10 Gil Volume Items on {world_name} (Total {format_gil(total_volume)} gil)').classes('text-lg font-semibold text-white mb-4')
            
            labels = [item['name'] for item in data_points]
            values = [item['gil_volume'] for item in data_points]
            
            # Fallback: display proportional bar list
            total = sum(values) or 1
            with ui.column().classes('w-full'):
                for name, val in zip(labels, values):
                    pct = (val / total) * 100
                    bar_width = pct
                    with ui.row().classes('items-center w-full gap-2'):
                        ui.label(name).classes('w-40 truncate font-semibold')
                        ui.html(
                            f'<div style="flex:1;background:#eee;height:24px;position:relative;border-radius:4px">'
                            f'<div style="background:#1f77b4;width:{bar_width}%;height:24px;border-radius:4px"></div>'
                            f'<span style="position:absolute;left:8px;top:3px;font-size:12px;font-weight:600;color:#333">{format_gil(val)} gil ({pct:.1f}%)</span>'
                            f'</div>',
                            sanitize=False
                        ).classes('flex-1')
            
            chart_table = ui.table(
                columns=[
                    {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                    {'name': 'item', 'label': 'Item', 'field': 'item', 'align': 'left'},
                    {'name': 'gil_volume', 'label': 'Gil Volume', 'field': 'gil_volume', 'align': 'right'},
                    {'name': 'velocity', 'label': 'Velocity', 'field': 'velocity', 'align': 'right'},
                ],
                rows=[
                    {
                        'rank': idx + 1,
                        'item': item['name'],
                        'gil_volume': format_gil(item['gil_volume']),
                        'velocity': format_velocity(item['velocity'])
                    }
                    for idx, item in enumerate(data_points)
                ],
                row_key='rank'
            ).classes('w-full mt-4')
            
            # Add slot templates for styled columns
            chart_table.add_slot('body-cell-item', '''
                <q-td :props="props" class="text-weight-bold" style="font-size: 1.05rem;">{{ props.row.item }}</q-td>
            ''')
            chart_table.add_slot('body-cell-gil_volume', '''
                <q-td :props="props" class="metric-volume text-weight-bold">{{ props.row.gil_volume }}</q-td>
            ''')
        
        set_status('Ready')
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-500')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')
