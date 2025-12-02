"""
Datacenters view.
"""

from nicegui import ui


def render(state, service, api, dark_mode: bool = False):
    """Render the datacenters view.
    
    Args:
        state: Application state
        service: Market service instance
        api: API client instance
        dark_mode: Whether dark mode is active
    
    Returns:
        Container for dynamic content
    """
    ui.label('FFXIV Datacenters').classes('text-2xl font-bold mb-4')
    ui.label('List of all available datacenters and their worlds.').classes('text-gray-500 mb-4')
    
    content_container = ui.column().classes('w-full')
    
    if state.datacenters:
        _render_table(state, content_container)
    
    return content_container


def _render_table(state, container):
    """Render the datacenters table."""
    with container:
        if not state.datacenters:
            ui.label('No datacenters loaded.').classes('text-gray-500')
            return
        
        # Sort by region and name
        sorted_dcs = sorted(state.datacenters, key=lambda x: (x.get('region', ''), x.get('name', '')))
        
        columns = [
            {'name': 'name', 'label': 'Datacenter', 'field': 'name', 'align': 'left', 'sortable': True},
            {'name': 'region', 'label': 'Region', 'field': 'region', 'align': 'left', 'sortable': True},
            {'name': 'worlds', 'label': 'Worlds', 'field': 'worlds', 'align': 'left'},
        ]
        
        rows = [
            {
                'name': dc.get('name', 'N/A'),
                'region': dc.get('region', 'N/A'),
                'worlds': ', '.join(
                    state.world_id_to_name.get(wid, str(wid)) 
                    for wid in dc.get('worlds', [])
                ) if dc.get('worlds') else 'No worlds'
            }
            for dc in sorted_dcs
        ]
        
        ui.table(columns=columns, rows=rows, row_key='name').classes('w-full')
        ui.label(f'Total: {len(state.datacenters)} datacenters').classes('text-sm text-gray-500 mt-2')
