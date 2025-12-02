"""
Tracking initialization and update views.
"""

import asyncio
from nicegui import ui
from ..components.cards import progress_card, warning_card, success_card
from ..utils.formatters import format_gil
from config import get_config

config = get_config()


def render_init_tracking(state, service, dark_mode: bool = False):
    """Render init tracking view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (limit_input, progress_container)
    """
    ui.label('Initialize Tracking').classes('text-2xl font-bold mb-4')
    ui.label('Start tracking the top volume items on a world.').classes('text-gray-500 mb-4')
    
    if not state.selected_world:
        ui.label('Please select a world first.').classes('text-yellow-600')
        return None, None
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Configuration').classes('text-lg font-semibold mb-2')
        ui.label(f'World: {state.selected_world}').classes('text-gray-600')
        
        limit_input = ui.number(
            'Number of items to track',
            value=config.get('cli', 'default_tracking_limit', 50),
            min=1,
            max=200
        ).classes('w-full')
        
        ui.label('This will analyze recently updated items and track those with the highest sales velocity.').classes('text-sm text-gray-500 mt-2')
        
        progress_container = ui.column().classes('w-full mt-4')
    
    return limit_input, progress_container


async def execute_init_tracking(state, service, limit, progress_container, set_status):
    """Execute tracking initialization.
    
    Args:
        state: Application state
        service: Market service instance
        limit: Number of items to track
        progress_container: UI container for progress
        set_status: Status update callback
    """
    with progress_container:
        progress_container.clear()
        
        progress, status_text = progress_card(
            'Initializing tracking...',
            'Starting...',
            0.3
        )
        
        set_status('Initializing tracking...')
        
        try:
            status_text.set_text('Fetching market data (running in background)...')
            await asyncio.sleep(0.1)
            
            top_items, total_found, items_with_sales = await service.initialize_tracking_async(
                state.selected_world, 
                limit
            )
            
            progress.set_value(1.0)
            status_text.set_text('Complete!')
            await asyncio.sleep(0.5)
            
            progress_container.clear()
            
            if not top_items:
                with progress_container:
                    ui.label(f'No items with sales data found for {state.selected_world}').classes('text-yellow-600')
            else:
                with progress_container:
                    success_card(f'Successfully initialized tracking for {len(top_items)} items')
                    
                    columns = [
                        {'name': 'item_id', 'label': 'Item ID', 'field': 'item_id', 'align': 'left'},
                        {'name': 'velocity', 'label': 'Sales/Day', 'field': 'velocity', 'align': 'right'},
                        {'name': 'avg_price', 'label': 'Avg Price', 'field': 'avg_price', 'align': 'right'},
                    ]
                    rows = [
                        {
                            'item_id': item['item_id'],
                            'velocity': f"{item['velocity']:.2f}",
                            'avg_price': f"{format_gil(item['avg_price'])} gil"
                        }
                        for item in top_items[:20]
                    ]
                    ui.table(columns=columns, rows=rows, row_key='item_id').classes('w-full mt-4')
                    
                    if len(top_items) > 20:
                        ui.label(f'...and {len(top_items) - 20} more items').classes('text-sm text-gray-500')
            
            set_status('Ready')
            ui.notify(f'Tracking initialized for {len(top_items)} items', type='positive')
            
        except Exception as e:
            progress_container.clear()
            with progress_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            set_status('Error')
            ui.notify(f'Error: {e}', type='negative')


def render_update(state, db, dark_mode: bool = False):
    """Render update view.
    
    Args:
        state: Application state
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        progress_container for updates
    """
    ui.label('Update Market Data').classes('text-2xl font-bold mb-4')
    ui.label('Fetch latest market data for all tracked items.').classes('text-gray-500 mb-4')
    
    if not state.selected_world:
        ui.label('Please select a world first.').classes('text-yellow-600')
        return None
    
    tracked_count = db.get_tracked_items_count(state.selected_world)
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label(f'World: {state.selected_world}').classes('text-lg font-semibold')
        ui.label(f'Tracked items: {tracked_count}').classes('text-gray-600')
        
        if tracked_count == 0:
            ui.label('No items tracked for this world. Run "Initialize Tracking" first.').classes('text-yellow-600 mt-2')
            return None
        
        estimated_time = tracked_count // 2
        ui.label(f'Estimated time: ~{estimated_time} seconds').classes('text-sm text-gray-500')
        ui.label('Rate limit: 20 requests/second (80% of API capacity)').classes('text-sm text-gray-400')
        
        progress_container = ui.column().classes('w-full mt-4')
    
    return progress_container


async def execute_update(state, service, progress_container, set_status):
    """Execute market data update.
    
    Args:
        state: Application state
        service: Market service instance
        progress_container: UI container for progress
        set_status: Status update callback
    """
    with progress_container:
        progress_container.clear()
        
        progress, status_text = progress_card(
            'Updating market data...',
            'Fetching market data and history (running in background)...',
            0.1
        )
        
        set_status('Updating market data...')
        
        try:
            successful, failed, tracked_items = await service.update_tracked_items_async(state.selected_world)
            
            progress.set_value(1.0)
            status_text.set_text('Complete!')
            await asyncio.sleep(0.5)
            
            progress_container.clear()
            
            with progress_container:
                if successful > 0:
                    success_card(f'Successfully updated {successful} items')
                if failed > 0:
                    ui.label(f'⚠ Failed to update {failed} items').classes('text-yellow-600')
                
                ui.label('Tip: Schedule this command daily via cron/Task Scheduler').classes('text-sm text-gray-500 mt-2')
            
            set_status('Ready')
            ui.notify(f'Updated {successful} items ({failed} failed)', type='positive' if failed == 0 else 'warning')
            
        except Exception as e:
            progress_container.clear()
            with progress_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            set_status('Error')
            ui.notify(f'Error: {e}', type='negative')
