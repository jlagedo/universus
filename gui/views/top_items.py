"""
Top items view.

Displays the top selling items by sales volume.
Uses the unified design system for consistent styling.
"""

from nicegui import ui
from ..utils.formatters import format_velocity, format_gil, format_time_ago
from ..utils.design_system import heading_classes, TABLE_SLOTS
from ..utils.icons import SpriteIcon
from ..components.cards import warning_card


def render(state, service, dark_mode: bool = False):
    """Render the top items view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Ignored (always dark mode)
    
    Returns:
        Tuple of (limit_input, results_container)
    """
    ui.label('Top Selling Items').classes(heading_classes(2))
    
    if not state.selected_world:
        warning_card('No world selected', 'Please select a world from the header dropdown.')
        return None, None
    
    ui.label(f'Top items by sales volume on {state.selected_world}').classes('text-gray-400 mb-6')
    
    # Controls
    with ui.row().classes('items-end gap-4 mb-4'):
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
            warning_card('No data available', 'Run "Update Data" to fetch current market data.')
            return
        
        columns = [
            {'name': 'rank', 'label': '#', 'field': 'rank', 'align': 'center'},
            {'name': 'item_name', 'label': 'Item', 'field': 'item_name', 'align': 'left'},
            {'name': 'sale_velocity', 'label': 'Sales/Day', 'field': 'sale_velocity', 'align': 'right'},
            {'name': 'average_price', 'label': 'Avg Price', 'field': 'average_price', 'align': 'right'},
            {'name': 'last_updated', 'label': 'Updated', 'field': 'last_updated', 'align': 'right'},
        ]
        
        rows = [
            {
                'rank': idx + 1,
                'item_id': item.get('item_id'),
                'item_name': item.get('item_name') or str(item.get('item_id', 'Unknown')),
                'icon_style': SpriteIcon.get_icon_style(item.get('item_id'), size=40),
                'sale_velocity_raw': item.get('sale_velocity') or 0,
                'sale_velocity': format_velocity(item.get('sale_velocity')),
                'average_price': f"{format_gil(item.get('average_price'))} gil",
                'last_updated': format_time_ago(item.get('last_updated', ''))
            }
            for idx, item in enumerate(items)
        ]
        
        table = ui.table(columns=columns, rows=rows, row_key='rank').classes('w-full')
        
        # Add header tooltips
        table.add_slot('header-cell-sale_velocity', 
            TABLE_SLOTS.header_tooltip_slot(
                'sale_velocity', 
                'Sales/Day', 
                'Average number of items sold per day based on recent sales history'
            )
        )
        table.add_slot('header-cell-average_price', 
            TABLE_SLOTS.header_tooltip_slot(
                'average_price', 
                'Avg Price', 
                'Average sale price from recent transactions'
            )
        )
        
        # Add styled slots with icon for item name
        table.add_slot('body-cell-item_name', TABLE_SLOTS.item_name_with_icon_slot())
        table.add_slot('body-cell-sale_velocity', '''
            <q-td :props="props" :class="props.row.sale_velocity_raw == 0 ? 'text-gray-500' : 'metric-highlight text-weight-bold'">
                <q-icon v-if="props.row.sale_velocity_raw == 0" name="warning" class="text-amber-400 q-mr-xs" size="xs">
                    <q-tooltip>No sales recorded</q-tooltip>
                </q-icon>
                {{ props.row.sale_velocity }}
            </q-td>
        ''')
        table.add_slot('body-cell-average_price', '''
            <q-td :props="props" class="metric-price text-weight-bold">{{ props.row.average_price }}</q-td>
        ''')
        
        if items:
            ui.label(f'Snapshot date: {items[0].get("snapshot_date", "N/A")}').classes('text-sm text-gray-500 mt-4')
