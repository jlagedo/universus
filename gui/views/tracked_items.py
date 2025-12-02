"""
Tracked items view.
"""

from nicegui import ui
from ..utils.formatters import format_time_ago
from ..components.cards import warning_card


def render(state, service, dark_mode: bool = False):
    """Render tracked items view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is active
    """
    ui.label('Tracked Items').classes('text-2xl font-bold mb-4')
    ui.label('All items being tracked across all worlds.').classes('text-gray-500 mb-4')
    
    by_world = service.get_all_tracked_items()
    
    if not by_world:
        warning_card('No items being tracked.', 'Use "Initialize Tracking" to start tracking items.')
        return
    
    for world, items in sorted(by_world.items()):
        with ui.expansion(f'{world} ({len(items)} items)', icon='public').classes('w-full mb-2'):
            columns = [
                {'name': 'item_id', 'label': 'Item ID', 'field': 'item_id', 'align': 'left'},
                {'name': 'item_name', 'label': 'Name', 'field': 'item_name', 'align': 'left'},
                {'name': 'first_tracked', 'label': 'First Tracked', 'field': 'first_tracked', 'align': 'right'},
                {'name': 'last_updated', 'label': 'Last Updated', 'field': 'last_updated', 'align': 'right'},
            ]
            
            rows = [
                {
                    'item_id': item['item_id'],
                    'item_name': item.get('item_name') or f"Item #{item['item_id']}",
                    'first_tracked': item.get('first_tracked', 'N/A')[:10] if item.get('first_tracked') else 'N/A',
                    'last_updated': format_time_ago(item.get('last_updated', ''))
                }
                for item in items
            ]
            
            ui.table(columns=columns, rows=rows, row_key='item_id').classes('w-full')
