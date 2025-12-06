"""
Market Analysis view - Comprehensive HQ/NQ price and volume analysis.

Uses the unified design system for consistent styling.
"""

from nicegui import ui
from ..utils.formatters import format_gil, format_velocity
from ..utils.design_system import heading_classes, PROPS, TABLE_SLOTS
from ..utils.icons import SpriteIcon
from ..components.cards import warning_card


def render(state, service, dark_mode: bool = False):
    """Render market analysis view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    
    Returns:
        Tuple of (world_options, world_select, search_input, results_container)
    """
    ui.label('Market Analysis').classes(heading_classes(2))
    ui.label('Total volume analysis based on world min prices and daily velocity.').classes('text-gray-400 mb-6')
    
    tracked = service.list_tracked_worlds()
    if not tracked:
        warning_card('No tracked worlds configured', 'Add tracked worlds in Settings > Tracked Worlds first.')
        return None, None, None, None
    
    world_options = {}
    for w in tracked:
        world_id = w.get('world_id')
        world_name = w.get('world_name') or state.world_id_to_name.get(world_id, f"World {world_id}")
        world_options[world_name] = world_id
    
    # Sticky filter card that stays visible when scrolling
    with ui.card().classes('w-full max-w-2xl p-4 sticky top-0 z-10').style('position: sticky; top: 0;'):
        ui.label('Filters').classes('text-lg font-semibold text-white mb-4')
        
        with ui.row().classes('w-full gap-4 items-end'):
            selected_world_name = list(world_options.keys())[0] if world_options else None
            world_select = ui.select(
                options=list(world_options.keys()),
                value=selected_world_name,
                label='Tracked World'
            ).classes('w-64').props(PROPS.SELECT_OUTLINED)
            
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
                warning_card('No data available', msg)
                return
            
            search_info = f' • Filtered by "{search_term}"' if search_term and search_term.strip() else ''
            ui.label(f'{world_name} Market Analysis • Data from {latest_date}{search_info}').classes('text-lg font-semibold text-white mb-4')
            
            # Define columns for the table with tooltips
            columns = [
                {'name': 'rank', 'label': '#', 'field': 'rank', 'sortable': True, 'align': 'center'},
                {'name': 'item_name', 'label': 'Item Name', 'field': 'item_name', 'sortable': True, 'align': 'left'},
                {'name': 'total_volume', 'label': 'Total Volume', 'field': 'total_volume', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'total_velocity', 'label': 'Total Vel/Day', 'field': 'total_velocity', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'hq_velocity', 'label': 'HQ Vel/Day', 'field': 'hq_velocity', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'hq_min_price', 'label': 'HQ Min Price', 'field': 'hq_min_price', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'nq_velocity', 'label': 'NQ Vel/Day', 'field': 'nq_velocity', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
                {'name': 'nq_min_price', 'label': 'NQ Min Price', 'field': 'nq_min_price', 'sortable': True, 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
            ]
            
            rows = []
            for idx, item in enumerate(results, start=1):
                rows.append({
                    'rank': idx,
                    'item_id': item['item_id'],
                    'item_name': item['item_name'],
                    'icon_style': SpriteIcon.get_icon_style(item['item_id'], size=40),
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
            
            # Add header slot with tooltips
            table.add_slot('header-cell-total_volume', '''
                <q-th :props="props">
                    <span>Total Volume</span>
                    <q-tooltip class="bg-grey-8 text-body2">Daily velocity × minimum price (estimated daily gil traded)</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-total_velocity', '''
                <q-th :props="props">
                    <span>Total Vel/Day</span>
                    <q-tooltip class="bg-grey-8 text-body2">Velocity/Day: Average number of items sold per day (HQ + NQ combined)</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-hq_velocity', '''
                <q-th :props="props">
                    <span>HQ Vel/Day</span>
                    <q-tooltip class="bg-grey-8 text-body2">HQ Velocity/Day: High Quality items sold per day</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-hq_min_price', '''
                <q-th :props="props">
                    <span>HQ Min Price</span>
                    <q-tooltip class="bg-grey-8 text-body2">HQ Min Price: Lowest current listing price for High Quality items</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-nq_velocity', '''
                <q-th :props="props">
                    <span>NQ Vel/Day</span>
                    <q-tooltip class="bg-grey-8 text-body2">NQ Velocity/Day: Normal Quality items sold per day</q-tooltip>
                </q-th>
            ''')
            table.add_slot('header-cell-nq_min_price', '''
                <q-th :props="props">
                    <span>NQ Min Price</span>
                    <q-tooltip class="bg-grey-8 text-body2">NQ Min Price: Lowest current listing price for Normal Quality items</q-tooltip>
                </q-th>
            ''')
            
            # Add slot templates to display formatted values with highlighting and zero-value warnings
            table.add_slot('body-cell-item_name', TABLE_SLOTS.item_name_with_icon_slot())
            table.add_slot('body-cell-total_volume', '''
                <q-td :props="props" class="metric-volume text-weight-bold">{{ props.row.total_volume_fmt }}</q-td>
            ''')
            table.add_slot('body-cell-total_velocity', '''
                <q-td :props="props" :class="props.row.total_velocity == 0 ? 'text-grey-5' : ''">
                    <q-icon v-if="props.row.total_velocity == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                        <q-tooltip>No sales recorded</q-tooltip>
                    </q-icon>
                    {{ props.row.total_velocity_fmt }}
                </q-td>
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
            table.add_slot('body-cell-nq_velocity', '''
                <q-td :props="props" :class="props.row.nq_velocity == 0 ? 'text-grey-5' : ''">
                    <q-icon v-if="props.row.nq_velocity == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                        <q-tooltip>No NQ sales recorded</q-tooltip>
                    </q-icon>
                    {{ props.row.nq_velocity_fmt }}
                </q-td>
            ''')
            table.add_slot('body-cell-nq_min_price', '''
                <q-td :props="props" :class="props.row.nq_min_price == 0 ? 'text-grey-5' : 'metric-price text-weight-bold'">
                    <q-icon v-if="props.row.nq_min_price == 0" name="remove_shopping_cart" class="text-grey-5 q-mr-xs" size="xs">
                        <q-tooltip>No NQ listings available</q-tooltip>
                    </q-icon>
                    {{ props.row.nq_min_price_fmt }}
                </q-td>
            ''')
            
            ui.label(f'Showing {len(results)} items').classes('text-sm text-gray-400 mt-2')
        
        set_status('Ready')
        
    except Exception as e:
        with container:
            ui.label(f'Error: {e}').classes('text-red-500')
        set_status('Error')
        ui.notify(f'Error: {e}', type='negative')
