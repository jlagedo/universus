"""
Dashboard view.
"""

from nicegui import ui
from ..utils.formatters import format_time_ago
from ..components.cards import stat_card


def render(state, db, dark_mode: bool = False):
    """Render the dashboard view.
    
    Args:
        state: Application state
        db: Database instance
        dark_mode: Whether dark mode is active
    """
    title_class = 'text-2xl font-bold mb-4 text-gray-900' if not dark_mode else 'text-2xl font-bold mb-4 text-white'
    label_class = 'text-gray-500' if not dark_mode else 'text-gray-400'
    actions_class = 'text-xl font-semibold mb-2 text-gray-900' if not dark_mode else 'text-xl font-semibold mb-2 text-white'
    
    ui.label('Dashboard').classes(title_class)
    
    if not state.selected_world:
        ui.label('Please select a world from the header dropdown.').classes(label_class)
        return None, None, None
    
    # Stats cards
    with ui.row().classes('w-full gap-4 mb-6'):
        tracked_items = db.get_tracked_items(state.selected_world) if state.selected_world else []
        tracked_count = len(tracked_items)
        items_synced = db.get_items_count()
        
        stat_card('Tracked Items', str(tracked_count), 'visibility', 'blue', dark_mode)
        stat_card('Items Database', f'{items_synced:,}', 'inventory_2', 'green', dark_mode)
        stat_card('Selected World', state.selected_world or 'None', 'public', 'purple', dark_mode)
        stat_card('Status', 'Online', 'wifi', 'teal', dark_mode)
    
    # Quick actions
    ui.label('Quick Actions').classes(actions_class)
    quick_actions_row = ui.row().classes('gap-4 mb-6')
    
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
    
    return quick_actions_row, tracked_items, None
