"""
Market Analysis view - Comprehensive HQ/NQ price and volume analysis.
"""

from nicegui import ui
from ..utils.formatters import format_gil, format_velocity


def render(state, service, dark_mode: bool = False):
    """Render market analysis view.
    
    Args:
        state: Application state
        service: Market service instance
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


def generate_analysis(state, service, world_options, world_name, search_term, container, set_status):
    """Generate market analysis report.
    
    Args:
        state: Application state
        service: Market service instance
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
        results, latest_date = service.get_market_analysis_data(wid, search_term)
        
        with container:
            if not results:
                msg = f'No data available for {world_name}.'
                if search_term:
                    msg += f' No items matching "{search_term}".'
                msg += ' Run "Update Current Prices" CLI command first.'
                ui.label(msg).classes('text-yellow-600')
                return
            
            search_info = f' • Filtered by "{search_term}"' if search_term and search_term.strip() else ''
            ui.label(f'{world_name} Market Analysis • Data from {latest_date}{search_info}').classes('text-lg font-semibold mb-2')
            
            # Define columns for the table
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
            for idx, item in enumerate(results, start=1):
                rows.append({
                    'rank': idx,
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    # Use raw numeric values - table will sort correctly
                    'total_volume': item['total_volume'],
                    'total_velocity': item['total_velocity'],
                    'hq_velocity': item['hq_velocity'],
                    'hq_min_price': item['hq_min_price'],
                    'nq_velocity': item['nq_velocity'],
                    'nq_min_price': item['nq_min_price'],
                    # Formatted values for display
                    'total_volume_fmt': format_gil(item['total_volume']),
                    'total_velocity_fmt': format_velocity(item['total_velocity']),
                    'hq_velocity_fmt': format_velocity(item['hq_velocity']),
                    'hq_min_price_fmt': format_gil(item['hq_min_price']),
                    'nq_velocity_fmt': format_velocity(item['nq_velocity']),
                    'nq_min_price_fmt': format_gil(item['nq_min_price']),
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
