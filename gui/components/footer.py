"""
Application footer component.

Provides status bar and version information.
Uses the unified design system for consistent styling.
"""

from typing import Optional
from nicegui import ui


class Footer:
    """Application footer with status bar."""
    
    def __init__(self, version: str = "1.0.0"):
        """Initialize footer component.
        
        Args:
            version: Application version
        """
        self.status_label: Optional[ui.label] = None
        self._render(version)
    
    def _render(self, version: str):
        """Render the footer."""
        with ui.footer().classes('items-center'):
            with ui.row().classes('w-full items-center justify-between px-4'):
                # Status indicator
                with ui.row().classes('items-center gap-2'):
                    self.status_icon = ui.icon('circle', size='xs').classes('text-teal-400')
                    self.status_label = ui.label('Ready').classes('text-sm text-gray-300')
                
                # Version and attribution
                ui.label(f'Universus v{version} • Data from Universalis API').classes('text-sm text-gray-500')
    
    def set_status(self, message: str, status: str = "ready"):
        """Update status message.
        
        Args:
            message: Status message to display
            status: Status type - 'ready', 'loading', 'error'
        """
        if self.status_label:
            self.status_label.set_text(message)
        
        # Update status icon color based on status
        icon_colors = {
            "ready": "text-teal-400",
            "loading": "text-blue-400",
            "error": "text-red-400",
        }
        if hasattr(self, 'status_icon'):
            self.status_icon.classes(replace=icon_colors.get(status, "text-gray-400"))
