"""
Market Analysis view - Comprehensive HQ/NQ price and volume analysis.
"""

from nicegui import ui
from ..utils.formatters import format_gil, format_velocity


def render(state, service, db, dark_mode: bool = False):
    """Render market analysis view.
    
    Args:
        state: Application state
        service: Market service instance
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (world_options, world_select, search_input, results_container)
    """
    ui.label('Market Analysis').classes('text-2xl font-bold mb-4')
    ui.label('Total volume analysis based on world min prices and daily velocity.').classes('text-gray-500 mb-4')
    
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
    
    with ui.card().classes('w-full max-w-2xl'):
        ui.label('Filters').classes('text-lg font-semibold mb-2')
        
        with ui.row().classes('w-full gap-4 items-end'):
            selected_world_name = list(world_options.keys())[0] if world_options else None
            world_select = ui.select(
                options=list(world_options.keys()),
                value=selected_world_name,
                label='Tracked World'
            ).classes('w-64')
            
            search_input = ui.input(
                label='Search Item Name',
                placeholder='Type to search...'
            ).classes('w-64')
    
    # Results container outside the filter card for full-width display
    results_container = ui.column().classes('w-full mt-4')
    
    return world_options, world_select, search_input, results_container


def generate_analysis(state, db, world_options, world_name, search_term, container, set_status):
    """Generate market analysis report.
    
    Args:
        state: Application state
        db: Database instance
        world_options: World name to ID mapping
        world_name: Selected world name
        search_term: Item name search term (partial match)
        container: UI container
        set_status: Status callback
    """
    container.clear()
    if not world_name or world_name not in world_options:
        ui.notify('Please select a valid tracked world', type='warning')
        return
    
    wid = world_options[world_name]
    set_status(f'Generating analysis for {world_name}...')
    
    try:
        cursor = db.conn.cursor()
        
        # Build query with optional search filter
        # Only fetch latest data (same day as most recent fetched_at)
        base_query = """
            SELECT 
                i.item_id,
                i.name,
                (COALESCE(cp.hq_world_daily_velocity, 0) * COALESCE(cp.hq_world_min_price, 0)) 
                    + (COALESCE(cp.nq_world_daily_velocity, 0) * COALESCE(cp.nq_world_min_price, 0)) AS total_volume_min_price,
                COALESCE(cp.hq_world_daily_velocity, 0) + COALESCE(cp.nq_world_daily_velocity, 0) AS total_velocity,
                COALESCE(cp.hq_world_daily_velocity, 0) AS hq_world_daily_velocity,
                COALESCE(cp.hq_world_min_price, 0) AS hq_world_min_price,
                COALESCE(cp.nq_world_daily_velocity, 0) AS nq_world_daily_velocity,
                COALESCE(cp.nq_world_min_price, 0) AS nq_world_min_price
            FROM current_prices cp
            INNER JOIN items i ON i.item_id = cp.item_id
            WHERE cp.tracked_world_id = ?
            AND strftime('%Y-%m-%d', cp.fetched_at) = (
                SELECT strftime('%Y-%m-%d', MAX(fetched_at)) 
                FROM current_prices 
                WHERE tracked_world_id = ?
            )
        """
        
        params = [wid, wid]
        
        if search_term and search_term.strip():
            base_query += " AND i.name LIKE ?"
            params.append(f"%{search_term.strip()}%")
        
        # Order by total velocity descending
        base_query += """
            ORDER BY total_velocity DESC
        """
        
        cursor.execute(base_query, params)
        results = cursor.fetchall()
        
        with container:
            if not results:
                msg = f'No data available for {world_name}.'
                if search_term:
                    msg += f' No items matching "{search_term}".'
                msg += ' Run "Update Current Prices" CLI command first.'
                ui.label(msg).classes('text-yellow-600')
                return
            
            # Get latest fetch date for display
            cursor.execute("""
                SELECT strftime('%Y-%m-%d %H:%M', MAX(fetched_at)) as latest
                FROM current_prices WHERE tracked_world_id = ?
            """, (wid,))
            latest_row = cursor.fetchone()
            latest_date = latest_row[0] if latest_row else 'Unknown'
            
            search_info = f' • Filtered by "{search_term}"' if search_term and search_term.strip() else ''
            ui.label(f'{world_name} Market Analysis • Data from {latest_date}{search_info}').classes('text-lg font-semibold mb-2')
            
            # Define columns for the table
            # We store both raw values (for sorting) and formatted values (for display)
            # The ':' syntax in field allows accessing nested/formatted values
            columns = [
                {'name': 'rank', 'label': '#', 'field': 'rank', 'sortable': True, 'align': 'center'},
                {'name': 'item_name', 'label': 'Item Name', 'field': 'item_name', 'sortable': True, 'align': 'left'},
                {'name': 'total_volume', 'label': 'Total Volume', 'field': 'total_volume', 'sortable': True, 'align': 'right'},
                {'name': 'total_velocity', 'label': 'Total Vel/Day', 'field': 'total_velocity', 'sortable': True, 'align': 'right'},
                {'name': 'hq_velocity', 'label': 'HQ Vel/Day', 'field': 'hq_velocity', 'sortable': True, 'align': 'right'},
                {'name': 'hq_min_price', 'label': 'HQ Min Price', 'field': 'hq_min_price', 'sortable': True, 'align': 'right'},
                {'name': 'nq_velocity', 'label': 'NQ Vel/Day', 'field': 'nq_velocity', 'sortable': True, 'align': 'right'},
                {'name': 'nq_min_price', 'label': 'NQ Min Price', 'field': 'nq_min_price', 'sortable': True, 'align': 'right'},
            ]
            
            rows = []
            for idx, row in enumerate(results, start=1):
                # Store raw numeric values - sorting will work on these
                total_volume_val = row[2] or 0
                total_velocity_val = row[3] or 0
                hq_velocity_val = row[4] or 0
                hq_min_price_val = row[5] or 0
                nq_velocity_val = row[6] or 0
                nq_min_price_val = row[7] or 0
                
                rows.append({
                    'rank': idx,
                    'item_id': row[0],
                    'item_name': row[1] or 'Unknown',
                    # Use raw numeric values - table will sort correctly
                    # Format display using slot template below
                    'total_volume': total_volume_val,
                    'total_velocity': total_velocity_val,
                    'hq_velocity': hq_velocity_val,
                    'hq_min_price': hq_min_price_val,
                    'nq_velocity': nq_velocity_val,
                    'nq_min_price': nq_min_price_val,
                    # Formatted values for display
                    'total_volume_fmt': format_gil(total_volume_val),
                    'total_velocity_fmt': format_velocity(total_velocity_val),
                    'hq_velocity_fmt': format_velocity(hq_velocity_val),
                    'hq_min_price_fmt': format_gil(hq_min_price_val),
                    'nq_velocity_fmt': format_velocity(nq_velocity_val),
                    'nq_min_price_fmt': format_gil(nq_min_price_val),
                })
            
            # Create table with pagination and sorting - full width
            table = ui.table(
                columns=columns,
                rows=rows,
                row_key='rank',
                pagination={'rowsPerPage': 100, 'sortBy': 'rank', 'descending': False}
            ).classes('w-full').props('flat bordered wrap-cells virtual-scroll')
            
            # Add slot templates to display formatted values
            table.add_slot('body-cell-total_volume', '''
                <q-td :props="props">{{ props.row.total_volume_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-total_velocity', '''
                <q-td :props="props">{{ props.row.total_velocity_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-hq_velocity', '''
                <q-td :props="props">{{ props.row.hq_velocity_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-hq_min_price', '''
                <q-td :props="props">{{ props.row.hq_min_price_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-nq_velocity', '''
                <q-td :props="props">{{ props.row.nq_velocity_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-nq_min_price', '''
                <q-td :props="props">{{ props.row.nq_min_price_fmt }}</q-td>
            ''')
            
            ui.label(f'Showing {len(results)} items').classes('text-sm text-gray-500 mt-2')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-600')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')
