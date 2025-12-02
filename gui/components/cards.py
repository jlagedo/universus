"""
Reusable card components.
"""

from nicegui import ui


def stat_card(title: str, value: str, icon: str, color: str, dark_mode: bool = False):
    """Create a statistics card.
    
    Args:
        title: Card title
        value: Statistic value
        icon: Icon name
        color: Color theme
        dark_mode: Whether dark mode is active
    """
    card_class = 'bg-white' if not dark_mode else 'bg-gray-800'
    title_class = 'text-sm text-gray-500' if not dark_mode else 'text-sm text-gray-400'
    value_class = f'text-2xl font-bold text-{color}-600' if not dark_mode else f'text-2xl font-bold text-{color}-400'
    
    with ui.card().classes(f'w-64 {card_class}'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.column().classes('gap-0'):
                ui.label(title).classes(title_class)
                ui.label(value).classes(value_class)
            ui.icon(icon, size='xl').classes(f'text-{color}-400')


def progress_card(title: str, status_text: str, progress_value: float = 0, show_value: bool = True):
    """Create a progress card.
    
    Args:
        title: Card title
        status_text: Status message
        progress_value: Progress value (0-1)
        show_value: Whether to show progress value
    
    Returns:
        Tuple of (progress element, status_text element) for updating
    """
    with ui.card().classes('w-full bg-blue-50'):
        ui.label(title).classes('text-blue-700 font-semibold')
        if show_value:
            progress = ui.linear_progress(value=progress_value).classes('w-full')
        else:
            progress = ui.linear_progress(show_value=False).props('indeterminate')
        status_label = ui.label(status_text).classes('text-sm text-blue-600')
    
    return progress, status_label


def warning_card(title: str, message: str):
    """Create a warning card.
    
    Args:
        title: Warning title
        message: Warning message
    """
    with ui.card().classes('w-full bg-yellow-50'):
        ui.label(title).classes('text-yellow-700')
        ui.label(message).classes('text-sm text-yellow-600')


def success_card(message: str):
    """Create a success card.
    
    Args:
        message: Success message
    """
    with ui.card().classes('w-full'):
        ui.label(f'✓ {message}').classes('text-green-600 font-semibold')
