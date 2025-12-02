"""
Application footer component.
"""

from typing import Optional
from nicegui import ui


class Footer:
    """Application footer with status bar."""
    
    def __init__(self, version: str = "1.0.0", dark_mode: bool = False):
        """Initialize footer component.
        
        Args:
            version: Application version
            dark_mode: Whether dark mode is active
        """
        self.status_label: Optional[ui.label] = None
        self.dark_mode = dark_mode
        self._render(version)
    
    def _render(self, version: str):
        """Render the footer."""
        footer_class = 'bg-gray-200' if not self.dark_mode else 'bg-gray-900'
        label_class = 'text-sm text-gray-600' if not self.dark_mode else 'text-sm text-gray-300'
        label_light_class = 'text-sm text-gray-500' if not self.dark_mode else 'text-sm text-gray-400'
        
        with ui.footer().classes(footer_class):
            with ui.row().classes('w-full items-center justify-between px-4'):
                self.status_label = ui.label('Ready').classes(label_class)
                ui.label(f'Universus v{version} | Data from Universalis API').classes(label_light_class)
    
    def set_status(self, message: str):
        """Update status message.
        
        Args:
            message: Status message to display
        """
        if self.status_label:
            self.status_label.set_text(message)
