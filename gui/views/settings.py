"""
Settings views (sync items, tracked worlds).
"""

import asyncio
from nicegui import ui
from ..components.cards import progress_card, warning_card, success_card


def render_sync_items(db, dark_mode: bool = False):
    """Render sync items view.
    
    Args:
        db: Database instance
        dark_mode: Whether dark mode is active
    
    Returns:
        progress_container for updates
    """
    ui.label('Sync Item Names').classes('text-2xl font-bold mb-4')
    ui.label('Download and sync item names from FFXIV Teamcraft.').classes('text-gray-500 mb-4')
    
    current_count = db.get_items_count()
    
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Item Database').classes('text-lg font-semibold mb-2')
        ui.label(f'Current items in database: {current_count:,}').classes('text-gray-600')
        
        ui.label('This will fetch ~47,000 item names from FFXIV Teamcraft and update the local database.').classes('text-sm text-gray-500 mt-2')
        ui.label('Any existing items will be replaced.').classes('text-sm text-gray-400')
        
        progress_container = ui.column().classes('w-full mt-4')
    
    return progress_container


async def execute_sync_items(service, progress_container, set_status):
    """Execute item sync.
    
    Args:
        service: Market service instance
        progress_container: UI container for progress
        set_status: Status callback
    """
    with progress_container:
        progress_container.clear()
        
        with ui.card().classes('w-full bg-blue-50'):
            ui.label('Syncing items...').classes('text-blue-700 font-semibold')
            ui.linear_progress(show_value=False).props('indeterminate')
            ui.label('Fetching from FFXIV Teamcraft (running in background, this may take a moment)...').classes('text-sm text-blue-600')
        
        set_status('Syncing items...')
        
        try:
            count = await service.sync_items_database_async()
            
            await asyncio.sleep(0.5)
            progress_container.clear()
            
            with progress_container:
                success_card(f'Successfully synced {count:,} items to local database')
            
            set_status('Ready')
            ui.notify(f'Synced {count:,} items', type='positive')
            
        except Exception as e:
            progress_container.clear()
            with progress_container:
                ui.label(f'Error: {e}').classes('text-red-600')
            set_status('Error')
            ui.notify(f'Error: {e}', type='negative')


def render_tracked_worlds(state, service, dark_mode: bool = False):
    """Render tracked worlds configuration view.
    
    Args:
        state: Application state
        service: Market service instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Tuple of (world_select, worlds_container) for dynamic updates
    """
    ui.label('Tracked Worlds').classes('text-2xl font-bold mb-4')
    ui.label('Manage the list of worlds to track.').classes('text-gray-500 mb-4')
    
    # Add world section
    with ui.card().classes('w-full max-w-xl'):
        ui.label('Add World').classes('text-lg font-semibold mb-2')
        
        world_select = ui.select(
            options=sorted(list(state.world_name_to_id.keys())),
            label='World'
        ).classes('w-full')
    
    # Existing tracked worlds
    worlds_container = ui.column().classes('w-full mt-4')
    
    return world_select, worlds_container


def render_tracked_worlds_table(state, service, container, on_refresh):
    """Render tracked worlds table.
    
    Args:
        state: Application state
        service: Market service instance
        container: UI container
        on_refresh: Refresh callback
    """
    container.clear()
    
    tracked = service.list_tracked_worlds()
    
    with container:
        if not tracked:
            warning_card('No tracked worlds configured.', '')
        else:
            ui.label('Configured Worlds').classes('text-lg font-semibold mb-2')
            
            columns = [
                {'name': 'world_id', 'label': 'World ID', 'field': 'world_id', 'align': 'left'},
                {'name': 'world_name', 'label': 'World Name', 'field': 'world_name', 'align': 'left'},
                {'name': 'added_at', 'label': 'Added', 'field': 'added_at', 'align': 'left'},
                {'name': 'actions', 'label': 'Actions', 'field': 'actions', 'align': 'center'},
            ]
            
            rows = []
            for w in tracked:
                rows.append({
                    'world_id': w.get('world_id'),
                    'world_name': w.get('world_name') or state.world_id_to_name.get(w.get('world_id'), 'Unknown'),
                    'added_at': w.get('added_at') or '',
                    'actions': ''
                })
            
            table = ui.table(columns=columns, rows=rows, row_key='world_id').classes('w-full')
            
            slot_html = (
                '<q-td key="actions" :props="props">'
                '<q-btn size="sm" flat color="negative" icon="delete" '
                '@click="$parent.$emit(\'remove_world\', props.row)"></q-btn>'
                '</q-td>'
            )
            table.add_slot('body-cell-actions', slot_html)
            
            def on_remove_world(e):
                row = e.args
                wid = row.get('world_id')
                wname = row.get('world_name')
                try:
                    service.remove_tracked_world(world_id=wid)
                    ui.notify(f'Removed tracked world: {wname or wid}', type='positive')
                    on_refresh()
                except Exception as ex:
                    ui.notify(f'Error: {ex}', type='negative')
            
            table.on('remove_world', on_remove_world)


async def add_tracked_world(state, service, world_name, on_success):
    """Add a tracked world.
    
    Args:
        state: Application state
        service: Market service instance
        world_name: World name to add
        on_success: Success callback
    """
    try:
        wid = state.world_name_to_id.get(world_name)
        if not wid:
            ui.notify('Invalid world selected', type='warning')
            return
        
        service.add_tracked_world(world=world_name, world_id=wid)
        ui.notify(f'Added tracked world: {world_name}', type='positive')
        on_success()
    except Exception as e:
        ui.notify(f'Error: {e}', type='negative')
