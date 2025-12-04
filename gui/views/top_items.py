"""
Top items view.
"""

from nicegui import ui
from ..utils.formatters import format_velocity, format_gil, format_time_ago


def render(state, service, dark_mode: bool = False):
    """Render the top items view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (limit_input, results_container)
    """
    ui.label('Top Selling Items').classes('text-2xl font-bold mb-4')
    
    if not state.selected_world:
        ui.label('Please select a world first.').classes('text-gray-500')
        return None, None
    
    ui.label(f'Top items by sales volume on {state.selected_world}').classes('text-gray-500 mb-4')
    
    # Controls
    limit_input = ui.number('Number of items', value=10, min=1, max=100).classes('w-32')
    results_container = ui.column().classes('w-full')
    
    return limit_input, results_container


def render_table(items, container):
    """Render the top items table.
    
    Args:
        items: List of item dictionaries
        container: UI container to render into
    """
    container.clear()
    
    with container:
        if not items:
            ui.label('No data available. Run "Update Data" first.').classes('text-yellow-600')
            return
        
        columns = [
            {'name': 'rank', 'label': 'Rank', 'field': 'rank', 'align': 'center'},
            {'name': 'item_name', 'label': 'Item', 'field': 'item_name', 'align': 'left'},
            {'name': 'sale_velocity', 'label': 'Sales/Day', 'field': 'sale_velocity', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
            {'name': 'average_price', 'label': 'Avg Price', 'field': 'average_price', 'align': 'right', 'headerClasses': 'tooltip-header', 'headerStyle': 'cursor: help;'},
            {'name': 'last_updated', 'label': 'Updated', 'field': 'last_updated', 'align': 'right'},
        ]
        
        rows = [
            {
                'rank': idx + 1,
                'item_name': item.get('item_name') or str(item.get('item_id', 'Unknown')),
                'sale_velocity_raw': item.get('sale_velocity') or 0,
                'sale_velocity': format_velocity(item.get('sale_velocity')),
                'average_price': f"{format_gil(item.get('average_price'))} gil",
                'last_updated': format_time_ago(item.get('last_updated', ''))
            }
            for idx, item in enumerate(items)
        ]
        
        table = ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')
        
        # Add header tooltips
        table.add_slot('header-cell-sale_velocity', '''
            <q-th :props="props">
                <span>Sales/Day</span>
                <q-tooltip class="bg-grey-8 text-body2">Average number of items sold per day based on recent sales history</q-tooltip>
            </q-th>
        ''')
        table.add_slot('header-cell-average_price', '''
            <q-th :props="props">
                <span>Avg Price</span>
                <q-tooltip class="bg-grey-8 text-body2">Average sale price from recent transactions</q-tooltip>
            </q-th>
        ''')
        
        # Add slot templates for styled columns with zero-value highlighting
        table.add_slot('body-cell-item_name', '''
            <q-td :props="props" class="text-weight-bold" style="font-size: 1.05rem;">{{ props.row.item_name }}</q-td>
        ''')
        table.add_slot('body-cell-sale_velocity', '''
            <q-td :props="props" :class="props.row.sale_velocity_raw == 0 ? 'text-grey-5' : 'metric-highlight text-weight-bold'">
                <q-icon v-if="props.row.sale_velocity_raw == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                    <q-tooltip>No sales recorded</q-tooltip>
                </q-icon>
                {{ props.row.sale_velocity }}
            </q-td>
        ''')
        table.add_slot('body-cell-average_price', '''
            <q-td :props="props" class="metric-price text-weight-bold">{{ props.row.average_price }}</q-td>
        ''')
        
        if items:
            ui.label(f'Snapshot date: {items[0].get("snapshot_date", "N/A")}').classes('text-sm text-gray-500 mt-2')
