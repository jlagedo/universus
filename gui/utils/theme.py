"""
Theme management for the GUI.
"""

from pathlib import Path
from nicegui import ui


class ThemeManager:
    """Manages dark/light theme for the application."""
    
    def __init__(self, initial_mode: str = 'light'):
        """Initialize theme manager.
        
        Args:
            initial_mode: 'light' or 'dark'
        """
        self.dark_mode = initial_mode == 'dark'
    
    def toggle(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        ui.colors(primary='#1976d2' if not self.dark_mode else '#2196f3')
        self.apply_css()
        self.save_preference()
    
    def apply_css(self):
        """Apply theme CSS to the application."""
        if self.dark_mode:
            ui.add_css(self._get_dark_css())
    
    def get_theme_classes(self, light: str, dark: str) -> str:
        """Get CSS classes based on current theme.
        
        Args:
            light: Classes for light theme
            dark: Classes for dark theme
        
        Returns:
            Appropriate classes for current theme
        """
        return dark if self.dark_mode else light
    
    def save_preference(self):
        """Save theme preference to config file."""
        config_path = Path.cwd() / "config.toml"
        if not config_path.exists():
            config_path = Path(__file__).parent.parent.parent / "config.toml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update theme setting
            theme_value = 'dark' if self.dark_mode else 'light'
            if '[gui]' in content:
                # Replace existing theme setting
                import re
                content = re.sub(
                    r'theme\s*=\s*"(light|dark)"',
                    f'theme = "{theme_value}"',
                    content
                )
            else:
                content += f'\n[gui]\ntheme = "{theme_value}"\n'
            
            with open(config_path, 'w') as f:
                f.write(content)
    
    @staticmethod
    def _get_dark_css() -> str:
        """Get dark theme CSS."""
        return '''
            body, html {
                background-color: #1e1e1e;
                color: #e0e0e0;
            }
            
            .nicegui-app {
                background-color: #1e1e1e;
            }
            
            /* Cards */
            .q-card, .q-expansion-item {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            
            /* Input fields */
            .q-field__control, .q-field__native input, .q-field__native textarea {
                color: #e0e0e0;
                background-color: #3a3a3a;
            }
            
            .q-field__label {
                color: #b0b0b0;
            }
            
            /* Tables */
            .q-table__card {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            
            .q-table tbody td {
                color: #e0e0e0;
            }
            
            .q-table thead tr {
                background-color: #3a3a3a;
            }
            
            .q-table thead th {
                color: #b0b0b0;
                background-color: #3a3a3a;
            }
            
            /* Buttons */
            .q-btn {
                color: #e0e0e0;
            }
            
            .q-btn--flat {
                color: #e0e0e0;
            }
            
            .q-btn--flat:hover {
                background-color: #3a3a3a;
            }
            
            /* Separators */
            .q-separator {
                background-color: #3a3a3a;
            }
            
            /* Select/Dropdown */
            .q-menu {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
            
            .q-item {
                color: #e0e0e0;
            }
            
            .q-item:hover {
                background-color: #3a3a3a;
            }
            
            /* Scrollbars */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #2d2d2d;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #555;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #777;
            }
            
            /* Labels and text */
            .text-gray-900 {
                color: #e0e0e0 !important;
            }
            
            .text-gray-500 {
                color: #b0b0b0 !important;
            }
            
            .text-gray-600 {
                color: #a0a0a0 !important;
            }
            
            .text-gray-400 {
                color: #c0c0c0 !important;
            }
            
            .bg-white {
                background-color: #2d2d2d !important;
            }
            
            .bg-gray-100 {
                background-color: #2d2d2d !important;
            }
            
            .bg-gray-200 {
                background-color: #1e1e1e !important;
            }
            
            .bg-gray-800 {
                background-color: #2d2d2d !important;
            }
            
            .bg-gray-900 {
                background-color: #1e1e1e !important;
            }
            
            .bg-blue-50 {
                background-color: #1a3a52 !important;
            }
            
            .bg-yellow-50 {
                background-color: #3a3420 !important;
            }
            
            .text-yellow-700 {
                color: #e8d97d !important;
            }
            
            .text-yellow-600 {
                color: #f5e08d !important;
            }
            
            .text-blue-700 {
                color: #6eb5ff !important;
            }
            
            .text-blue-600 {
                color: #7fc5ff !important;
            }
            
            .text-green-600 {
                color: #6cc874 !important;
            }
            
            .text-red-600 {
                color: #ff6b6b !important;
            }
            
            /* Progress bar */
            .q-linear-progress {
                background-color: #3a3a3a;
            }
            
            /* Notifications */
            .q-notification {
                background-color: #2d2d2d;
                color: #e0e0e0;
            }
        '''
