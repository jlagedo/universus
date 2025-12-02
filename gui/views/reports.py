"""
Reports views (item report, sell volume, charts).
"""

import asyncio
from nicegui import ui
from ..utils.formatters import format_gil, format_velocity
from config import get_config

config = get_config()


def render_item_report(state, service, db, dark_mode: bool = False):
    """Render item report view.
    
    Args:
        state: Application state
        service: Market service instance
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (item_id_input, days_input, report_container)
    """
    ui.label('Item Report').classes('text-2xl font-bold mb-4')
    ui.label('View detailed historical report for a specific item.').classes('text-gray-500 mb-4')
    
    if not state.selected_world:
        ui.label('Please select a world first.').classes('text-yellow-600')
        return None, None, None
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Report Parameters').classes('text-lg font-semibold mb-2')
        
        item_id_input = ui.number('Item ID', value=0, min=1).classes('w-full')
        days_input = ui.number(
            'Days of history',
            value=config.get('cli', 'default_report_days', 30),
            min=1,
            max=365
        ).classes('w-full')
        
        report_container = ui.column().classes('w-full mt-4')
    
    return item_id_input, days_input, report_container


def generate_item_report(state, service, db, item_id, days, container, set_status):
    """Generate item report.
    
    Args:
        state: Application state
        service: Market service instance
        db: Database instance
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
                ui.label(f'No data available for item {item_id} on {state.selected_world}').classes('text-yellow-600')
                return
            
            item_name = db.get_item_name(item_id) or f"Item #{item_id}"
            ui.label(f'{item_name}').classes('text-xl font-bold')
            ui.label(f'{state.selected_world} • {len(snapshots)} days of data').classes('text-gray-500 mb-4')
            
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
            
            ui.table(columns=columns, rows=rows, row_key='date', pagination={'rowsPerPage': 15}).classes('w-full')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-600')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')


def render_sell_volume(state, service, db, dark_mode: bool = False):
    """Render sell volume by world report.
    
    Args:
        state: Application state
        service: Market service instance
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (world_options, world_select, limit_input, report_container)
    """
    ui.label('Sell Volume by World').classes('text-2xl font-bold mb-4')
    ui.label('Top items by HQ sales velocity for selected tracked world.').classes('text-gray-500 mb-4')
    
    tracked = service.list_tracked_worlds()
    if not tracked:
        with ui.card().classes('w-full bg-yellow-50'):
            ui.label('No tracked worlds configured.').classes('text-yellow-700')
            ui.label('Add tracked worlds in Settings > Tracked Worlds first.').classes('text-sm text-yellow-600')
        return None, None, None, None
    
    world_options = {}
    for w in tracked:
        world_id = w.get('world_id')
        world_name = w.get('world_name') or state.world_id_to_name.get(world_id, f"World {world_id}")
        world_options[world_name] = world_id
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Filter').classes('text-lg font-semibold mb-2')
        
        selected_world_name = list(world_options.keys())[0] if world_options else None
        world_select = ui.select(
            options=list(world_options.keys()),
            value=selected_world_name,
            label='Tracked World'
        ).classes('w-full')
        
        limit_input = ui.number('Limit', value=100, min=1, max=500).classes('w-full')
        report_container = ui.column().classes('w-full mt-4')
    
    return world_options, world_select, limit_input, report_container


def generate_sell_volume_report(state, db, world_options, world_name, limit, container, set_status):
    """Generate sell volume report.
    
    Args:
        state: Application state
        db: Database instance
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
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT 
                i.name,
                cp.hq_world_recent_price,
                cp.hq_world_avg_price,
                cp.hq_world_min_price,
                cp.hq_world_daily_velocity
            FROM marketable_items mi
            INNER JOIN items i ON mi.item_id = i.item_id
            INNER JOIN current_prices cp ON cp.item_id = i.item_id
            WHERE cp.tracked_world_id = ?
            ORDER BY cp.hq_world_daily_velocity DESC
            LIMIT ?
        """, (wid, limit))
        
        results = cursor.fetchall()
        
        with container:
            if not results:
                ui.label(f'No data available for {world_name}. Run "Update Current Prices" CLI command first.').classes('text-yellow-600')
                return
            
            ui.label(f'Top {len(results)} items by HQ daily velocity on {world_name}').classes('text-lg font-semibold mb-2')
            
            columns = [
                {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                {'name': 'item_name', 'label': 'Item Name', 'field': 'item_name', 'align': 'left'},
                {'name': 'hq_velocity', 'label': 'HQ Daily Velocity', 'field': 'hq_velocity', 'align': 'right'},
                {'name': 'hq_recent_price', 'label': 'HQ Recent Price', 'field': 'hq_recent_price', 'align': 'right'},
                {'name': 'hq_avg_price', 'label': 'HQ Avg Price', 'field': 'hq_avg_price', 'align': 'right'},
                {'name': 'hq_min_price', 'label': 'HQ Min Price', 'field': 'hq_min_price', 'align': 'right'},
                {'name': 'gil_volume', 'label': 'Gil Volume', 'field': 'gil_volume', 'align': 'right'},
            ]
            
            rows = []
            for idx, row in enumerate(results, start=1):
                recent_price = row[1] or 0
                avg_price = row[2] or 0
                min_price = row[3] or 0
                velocity = row[4] or 0
                price_for_volume = recent_price or avg_price or min_price
                gil_volume = velocity * price_for_volume
                rows.append({
                    'rank': idx,
                    'item_name': row[0] or 'Unknown',
                    'hq_velocity': format_velocity(row[4]),
                    'hq_recent_price': format_gil(row[1]),
                    'hq_avg_price': format_gil(row[2]),
                    'hq_min_price': format_gil(row[3]),
                    'gil_volume': format_gil(gil_volume),
                })
            
            ui.table(columns=columns, rows=rows, row_key='rank', pagination={'rowsPerPage': 20}).classes('w-full')
            ui.label(f'Showing {len(results)} items').classes('text-sm text-gray-500 mt-2')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-600')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')


def render_sell_volume_chart(state, service, db, dark_mode: bool = False):
    """Render sell volume chart view.
    
    Args:
        state: Application state
        service: Market service instance
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (world_options, world_select, chart_container)
    """
    ui.label('Sell Volume Chart').classes('text-2xl font-bold mb-4')
    ui.label('Pie chart of top 10 items by HQ gil volume (velocity * price).').classes('text-gray-500 mb-4')
    
    tracked = service.list_tracked_worlds()
    if not tracked:
        with ui.card().classes('w-full bg-yellow-50'):
            ui.label('No tracked worlds configured.').classes('text-yellow-700')
            ui.label('Add tracked worlds first to view chart.').classes('text-sm text-yellow-600')
        return None, None, None
    
    world_options = {}
    for w in tracked:
        wid = w.get('world_id')
        wname = w.get('world_name') or state.world_id_to_name.get(wid, f"World {wid}")
        world_options[wname] = wid
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Filter').classes('text-lg font-semibold mb-2')
        selected_world_name = list(world_options.keys())[0] if world_options else None
        world_select = ui.select(options=list(world_options.keys()), value=selected_world_name, label='Tracked World').classes('w-full')
        
        chart_container = ui.column().classes('w-full mt-4')
    
    return world_options, world_select, chart_container


def generate_chart(state, db, world_options, world_name, container, set_status):
    """Generate sell volume chart.
    
    Args:
        state: Application state
        db: Database instance
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
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT 
                i.name,
                cp.hq_world_recent_price,
                cp.hq_world_avg_price,
                cp.hq_world_min_price,
                cp.hq_world_daily_velocity
            FROM marketable_items mi
            INNER JOIN items i ON mi.item_id = i.item_id
            INNER JOIN current_prices cp ON cp.item_id = i.item_id
            WHERE cp.tracked_world_id = ?
            ORDER BY cp.hq_world_daily_velocity DESC
            LIMIT 200
        """, (wid,))
        rows = cursor.fetchall()
        
        data_points = []
        for row in rows:
            name = row[0] or 'Unknown'
            recent = row[1] or 0
            avg_p = row[2] or 0
            min_p = row[3] or 0
            velocity = row[4] or 0
            price_for_volume = recent or avg_p or min_p
            gil_volume = velocity * price_for_volume
            if gil_volume > 0:
                data_points.append((name, gil_volume, velocity, price_for_volume))
        
        data_points.sort(key=lambda x: x[1], reverse=True)
        top10 = data_points[:10]
        
        if not top10:
            with container:
                ui.label('No data available. Run price update first.').classes('text-yellow-600')
            set_status('Ready')
            return
        
        total_volume = sum(gv for _, gv, _, _ in top10)
        
        with container:
            ui.label(f'Top 10 Gil Volume Items on {world_name} (Total {format_gil(total_volume)} gil)').classes('text-lg font-semibold mb-2')
            
            labels = [d[0] for d in top10]
            values = [d[1] for d in top10]
            
            # Fallback: display proportional bar list
            total = sum(values) or 1
            with ui.column().classes('w-full'):
                for name, val in zip(labels, values):
                    pct = (val / total) * 100
                    bar_width = pct
                    with ui.row().classes('items-center w-full gap-2'):
                        ui.label(name).classes('w-40 truncate text-sm')
                        ui.html(
                            f'<div style="flex:1;background:#eee;height:20px;position:relative;border-radius:4px">'
                            f'<div style="background:#1f77b4;width:{bar_width}%;height:20px;border-radius:4px"></div>'
                            f'<span style="position:absolute;left:8px;top:2px;font-size:11px;color:#333">{format_gil(val)} gil ({pct:.1f}%)</span>'
                            f'</div>',
                            sanitize=False
                        ).classes('flex-1')
            
            ui.table(
                columns=[
                    {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
                    {'name': 'item', 'label': 'Item', 'field': 'item', 'align': 'left'},
                    {'name': 'gil_volume', 'label': 'Gil Volume', 'field': 'gil_volume', 'align': 'right'},
                    {'name': 'velocity', 'label': 'Velocity', 'field': 'velocity', 'align': 'right'},
                ],
                rows=[
                    {
                        'rank': idx + 1,
                        'item': name,
                        'gil_volume': format_gil(gv),
                        'velocity': format_velocity(vel)
                    }
                    for idx, (name, gv, vel, price) in enumerate(top10)
                ],
                row_key='rank'
            ).classes('w-full mt-4')
        
        set_status('Ready')
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-600')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')
