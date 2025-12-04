"""
Reusable card components.

Uses the unified design system for consistent styling.
All components are designed for dark mode only.
"""

from nicegui import ui
from ..utils.design_system import STYLES, COLORS


def stat_card(
    title: str, 
    value: str, 
    icon: str, 
    accent: str = "default",
    **kwargs  # Accept dark_mode for backward compatibility
):
    """Create a statistics card with consistent styling.
    
    Args:
        title: Card title/label
        value: Statistic value to display
        icon: Material icon name
        accent: Accent color - 'default', 'hq', 'nq', 'blue', 'green', 
                'purple', 'teal', 'red'
        **kwargs: Ignored (for backward compatibility with dark_mode param)
    """
    # Map accent colors to CSS classes
    accent_map = {
        "default": ("text-white", "text-gray-400"),
        "blue": ("text-blue-400", "text-blue-400"),
        "green": ("text-teal-400", "text-teal-400"),
        "teal": ("text-teal-400", "text-teal-400"),
        "purple": ("text-purple-400", "text-purple-400"),
        "red": ("text-red-400", "text-red-400"),
        "hq": ("hq-accent", "hq-accent"),
        "nq": ("nq-accent", "nq-accent"),
    }
    
    value_class, icon_class = accent_map.get(accent, accent_map["default"])
    
    with ui.card().classes('w-64 p-4'):
        with ui.row().classes('items-center justify-between w-full'):
            with ui.column().classes('gap-1'):
                ui.label(title).classes('text-sm text-gray-400')
                ui.label(value).classes(f'text-2xl font-bold {value_class}')
            ui.icon(icon, size='xl').classes(icon_class)


def stat_card_hq(title: str, value: str, icon: str, **kwargs):
    """Create a HQ-themed statistics card with teal accent.
    
    Args:
        title: Card title
        value: Statistic value
        icon: Icon name
        **kwargs: Ignored (for backward compatibility)
    """
    stat_card(title, value, icon, accent="hq")


def stat_card_nq(title: str, value: str, icon: str, **kwargs):
    """Create a NQ-themed statistics card with amber accent.
    
    Args:
        title: Card title
        value: Statistic value
        icon: Icon name
        **kwargs: Ignored (for backward compatibility)
    """
    stat_card(title, value, icon, accent="nq")


def info_card(title: str, content: str, icon: str = None):
    """Create an informational card.
    
    Args:
        title: Card title
        content: Card content text
        icon: Optional icon name
    """
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('items-center gap-2 mb-2'):
            if icon:
                ui.icon(icon).classes('text-blue-400')
            ui.label(title).classes('text-lg font-semibold text-white')
        ui.label(content).classes('text-sm text-gray-400')


def progress_card(
    title: str, 
    status_text: str, 
    progress_value: float = 0, 
    show_value: bool = True
):
    """Create a progress card for async operations.
    
    Args:
        title: Card title
        status_text: Status message
        progress_value: Progress value (0-1)
        show_value: Whether to show progress value
    
    Returns:
        Tuple of (progress element, status_label element) for updating
    """
    with ui.card().classes('w-full p-4'):
        with ui.row().classes('items-center gap-2 mb-2'):
            ui.icon('hourglass_empty').classes('text-blue-400')
            ui.label(title).classes('text-lg font-semibold text-white')
        
        if show_value:
            progress = ui.linear_progress(value=progress_value).classes('w-full')
        else:
            progress = ui.linear_progress(show_value=False).props('indeterminate')
        
        status_label = ui.label(status_text).classes('text-sm text-blue-400 mt-2')
    
    return progress, status_label


def warning_card(title: str, message: str = ""):
    """Create a warning card.
    
    Args:
        title: Warning title
        message: Warning message (optional)
    """
    with ui.card().classes('w-full p-4 border-l-4').style(f'border-left-color: {COLORS.WARNING}'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('warning').classes('text-amber-400')
            ui.label(title).classes('text-amber-400 font-semibold')
        if message:
            ui.label(message).classes('text-sm text-gray-400 mt-1')


def error_card(title: str, message: str = ""):
    """Create an error card.
    
    Args:
        title: Error title
        message: Error message (optional)
    """
    with ui.card().classes('w-full p-4 border-l-4').style(f'border-left-color: {COLORS.ERROR}'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('error').classes('text-red-400')
            ui.label(title).classes('text-red-400 font-semibold')
        if message:
            ui.label(message).classes('text-sm text-gray-400 mt-1')


def success_card(message: str, title: str = "Success"):
    """Create a success card.
    
    Args:
        message: Success message
        title: Optional title (default: "Success")
    """
    with ui.card().classes('w-full p-4 border-l-4').style(f'border-left-color: {COLORS.SUCCESS}'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('check_circle').classes('text-teal-400')
            ui.label(title).classes('text-teal-400 font-semibold')
        ui.label(message).classes('text-sm text-gray-300 mt-1')


def section_card(title: str = None, width: str = "full"):
    """Create a section container card.
    
    Args:
        title: Optional section title
        width: Card width - 'full', 'lg', 'xl', '2xl'
    
    Returns:
        Card element for use as context manager
    
    Usage:
        with section_card("Settings", width="xl") as card:
            ui.label("Content here")
    """
    width_map = {
        "full": "w-full",
        "lg": "w-full max-w-lg",
        "xl": "w-full max-w-xl",
        "2xl": "w-full max-w-2xl",
    }
    
    card = ui.card().classes(f'{width_map.get(width, "w-full")} p-4')
    
    if title:
        with card:
            ui.label(title).classes('text-lg font-semibold text-white mb-4')
    
    return card


def filter_card(title: str = "Filters", sticky: bool = True):
    """Create a filter/controls card that can be sticky.
    
    Args:
        title: Card title (default: "Filters")
        sticky: Whether card should stick to top when scrolling
    
    Returns:
        Card element for use as context manager
    """
    classes = 'w-full max-w-xl p-4'
    if sticky:
        classes += ' sticky top-0 z-10'
    
    card = ui.card().classes(classes)
    
    if sticky:
        card.style('position: sticky; top: 0;')
    
    with card:
        ui.label(title).classes('text-lg font-semibold text-white mb-4')
    
    return card
