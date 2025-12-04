"""
Theme management for the GUI.
"""

from pathlib import Path
from nicegui import ui


# Google Fonts for gaming aesthetic (Material Icons are built into NiceGUI/Quasar)
GOOGLE_FONTS_HTML = '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:ital,wght@0,100..900;1,100..900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
'''

# Font CSS for gaming theme
FONT_CSS = '''
/* Gaming Font Stack */
:root {
    --font-display: 'Orbitron', 'Segoe UI', Roboto, sans-serif;
    --font-body: 'Exo 2', 'Segoe UI', Roboto, sans-serif;
    --font-accent: 'Rajdhani', 'Segoe UI', Roboto, sans-serif;
}

/* Base body font */
body, html {
    font-family: var(--font-body);
}

/* Headers and titles - Orbitron for futuristic gaming feel */
h1, h2, h3, h4, h5, h6,
.title, .header-title,
.q-toolbar__title {
    font-family: var(--font-display);
    letter-spacing: 0.05em;
}

/* Navigation and menu items - Rajdhani for clean tech look */
.q-item__label,
.nav-item, .menu-item,
.q-tab__label,
.sidebar-item {
    font-family: var(--font-accent);
    font-weight: 500;
}

/* Stats, numbers, and data - Rajdhani for clarity */
.stat-value, .stat-label,
.q-table tbody td,
.q-table thead th,
.data-value {
    font-family: var(--font-accent);
}

/* Table font sizing - enhanced readability */
.q-table tbody td {
    font-size: 1rem;
    padding: 10px 14px;
}

.q-table thead th {
    font-size: 1.05rem;
    font-weight: 700;
    padding: 12px 14px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

/* Alternating row colors for better scanability */
.q-table tbody tr:nth-child(even) {
    background-color: rgba(0, 0, 0, 0.03);
}

.q-table tbody tr:nth-child(odd) {
    background-color: transparent;
}

/* Item name column - larger and bolder */
.q-table tbody td[data-col="item_name"],
.q-table tbody td[data-col="item"],
.q-table tbody td[data-col="name"] {
    font-size: 1.05rem;
    font-weight: 600;
}

/* High-impact metrics - bold colored text */
.metric-highlight {
    font-weight: 700;
    color: #1976d2;
}

.metric-volume {
    font-weight: 700;
    color: #2e7d32;
}

.metric-price {
    font-weight: 700;
    color: #7b1fa2;
}

/* Buttons - Exo 2 for readability with gaming feel */
.q-btn__content,
.q-btn {
    font-family: var(--font-body);
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Input fields and forms */
.q-field__native input,
.q-field__native textarea,
.q-field__label {
    font-family: var(--font-body);
}

/* Cards and panels */
.q-card__section {
    font-family: var(--font-body);
}

/* Notifications and badges */
.q-notification__message,
.q-badge {
    font-family: var(--font-accent);
    font-weight: 600;
}

/* Footer */
.q-footer {
    font-family: var(--font-accent);
}

/* Accessibility - Focus styles for keyboard navigation */
*:focus {
    outline: 2px solid #1976d2;
    outline-offset: 2px;
}

*:focus:not(:focus-visible) {
    outline: none;
}

*:focus-visible {
    outline: 2px solid #1976d2;
    outline-offset: 2px;
}

/* Skip link for keyboard users */
.skip-link {
    position: absolute;
    top: -40px;
    left: 0;
    background: #1976d2;
    color: white;
    padding: 8px 16px;
    z-index: 100;
    text-decoration: none;
    font-weight: 600;
}

.skip-link:focus {
    top: 0;
}

/* Button keyboard focus enhancement */
.q-btn:focus-visible {
    box-shadow: 0 0 0 3px rgba(25, 118, 210, 0.4);
}

/* Input keyboard focus enhancement */
.q-field--focused .q-field__control {
    box-shadow: 0 0 0 2px rgba(25, 118, 210, 0.3);
}

/* Table row keyboard focus */
.q-table tbody tr:focus-within {
    background-color: rgba(25, 118, 210, 0.1);
}

/* Ensure minimum touch target size (48px) */
.q-btn, .q-item {
    min-height: 44px;
    min-width: 44px;
}
'''


class ThemeManager:
    """Manages dark/light theme for the application."""
    
    def __init__(self, initial_mode: str = 'light'):
        """Initialize theme manager.
        
        Args:
            initial_mode: 'light' or 'dark'
        """
        self.dark_mode = initial_mode == 'dark'
        self._fonts_loaded = False
    
    def load_fonts(self):
        """Load Google Fonts for gaming aesthetic."""
        if not self._fonts_loaded:
            ui.add_head_html(GOOGLE_FONTS_HTML)
            ui.add_css(FONT_CSS)
            self._fonts_loaded = True
    
    def toggle(self):
        """Toggle between light and dark themes."""
        self.dark_mode = not self.dark_mode
        # Tokyo Night primary blue for dark mode
        ui.colors(primary='#1976d2' if not self.dark_mode else '#7aa2f7')
        self.apply_css()
        self.save_preference()
    
    def apply_css(self):
        """Apply theme CSS to the application."""
        self.load_fonts()
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
        """Get dark theme CSS - Tokyo Night theme colors with WCAG 2.1 AA contrast."""
        return '''
            /* Tokyo Night Color Palette - Enhanced for Accessibility:
               Background: #1a1b26 (main), #16161e (darker), #1f2335 (lighter)
               Foreground: #c0caf5 (main text - 11.5:1 contrast), #e0e0e0 (bright text - 13:1 contrast)
               Muted: #9aa5ce (7:1 contrast for secondary text)
               Primary: #7aa2f7 (blue), #bb9af7 (purple), #7dcfff (cyan)
               Accent: #9ece6a (green), #e0af68 (yellow), #f7768e (red/magenta)
            */
            
            body, html {
                background-color: #1a1b26;
                color: #c0caf5;
            }
            
            .nicegui-app {
                background-color: #1a1b26;
            }
            
            /* Cards */
            .q-card, .q-expansion-item {
                background-color: #1f2335;
                color: #c0caf5;
                border: 1px solid #3d4a6b;
            }
            
            /* Expansion items in dark mode */
            .q-expansion-item .q-item__label {
                color: #c0caf5 !important;
            }
            
            .q-expansion-item__container {
                background-color: #1f2335;
            }
            
            /* Input fields - improved contrast */
            .q-field__control, .q-field__native input, .q-field__native textarea {
                color: #e0e0e0;
                background-color: #24283b;
            }
            
            .q-field__label {
                color: #9aa5ce;
            }
            
            .q-field--focused .q-field__label {
                color: #7dcfff !important;
            }
            
            .q-field--focused .q-field__control {
                border-color: #7aa2f7;
                box-shadow: 0 0 0 2px rgba(122, 162, 247, 0.3);
            }
                border-color: #7aa2f7;
            }
            
            /* Tables - improved contrast */
            .q-table__card {
                background-color: #1f2335;
                color: #c0caf5;
            }
            
            .q-table tbody td {
                color: #c0caf5;
                border-color: #3d4a6b;
            }
            
            /* Alternating row colors for dark theme */
            .q-table tbody tr:nth-child(even) {
                background-color: rgba(36, 40, 59, 0.7);
            }
            
            .q-table tbody tr:nth-child(odd) {
                background-color: transparent;
            }
            
            .q-table tbody tr:hover {
                background-color: #3d4a6b;
            }
            
            .q-table tbody tr:focus-within {
                background-color: rgba(122, 162, 247, 0.2);
                outline: 2px solid #7aa2f7;
                outline-offset: -2px;
            }
            
            .q-table thead tr {
                background-color: #24283b;
            }
            
            .q-table thead th {
                color: #7dcfff;
                background-color: #24283b;
                border-color: #3d4a6b;
                font-weight: 700;
            }
            
            /* High-impact metrics in dark mode - improved contrast */
            .metric-highlight {
                color: #7dcfff !important;
            }
            
            .metric-volume {
                color: #9ece6a !important;
            }
            
            .metric-price {
                color: #bb9af7 !important;
            }
            
            /* Buttons - improved contrast and focus */
            .q-btn {
                color: #e0e0e0;
            }
            
            .q-btn--flat {
                color: #c0caf5;
            }
            
            .q-btn--flat:hover {
                background-color: #2a2f45;
            }
            
            .q-btn:focus-visible {
                box-shadow: 0 0 0 3px rgba(122, 162, 247, 0.5);
            }
            
            .q-btn.bg-primary {
                background-color: #7aa2f7 !important;
                color: #1a1b26 !important;
            }
            
            .q-btn.bg-primary:hover {
                background-color: #89b4fa !important;
            }
            
            /* Separators */
            .q-separator {
                background-color: #3d4a6b;
            }
            
            /* Select/Dropdown - improved contrast */
            .q-menu {
                background-color: #1f2335;
                color: #c0caf5;
                border: 1px solid #3d4a6b;
            }
            
            .q-item {
                color: #c0caf5;
            }
            
            .q-item:hover {
                background-color: #2a2f45;
            }
            
            .q-item:focus-visible {
                background-color: rgba(122, 162, 247, 0.2);
                outline: 2px solid #7aa2f7;
                outline-offset: -2px;
            }
            
            .q-item--active {
                background-color: #3d4a6b;
                color: #7dcfff;
            }
            
            /* Scrollbars */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1a1b26;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #33467c;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #565f89;
            }
            
            /* Labels and text - improved contrast for accessibility */
            .text-gray-900 {
                color: #e0e0e0 !important;
            }
            
            .text-gray-500 {
                color: #9aa5ce !important;
            }
            
            .text-gray-600 {
                color: #a9b1d6 !important;
            }
            
            .text-gray-400 {
                color: #c0caf5 !important;
            }
            
            .text-gray-300 {
                color: #c0caf5 !important;
            }
            
            /* Background colors */
            .bg-white {
                background-color: #1f2335 !important;
            }
            
            .bg-gray-100 {
                background-color: #1f2335 !important;
            }
            
            .bg-gray-200 {
                background-color: #1a1b26 !important;
            }
            
            .bg-gray-800 {
                background-color: #1f2335 !important;
            }
            
            .bg-gray-900 {
                background-color: #16161e !important;
            }
            
            .bg-blue-50 {
                background-color: #1f2335 !important;
                border-left: 3px solid #7aa2f7 !important;
            }
            
            .bg-yellow-50 {
                background-color: #1f2335 !important;
                border-left: 3px solid #e0af68 !important;
            }
            
            /* Accent text colors - Tokyo Night palette */
            .text-yellow-700 {
                color: #e0af68 !important;
            }
            
            .text-yellow-600 {
                color: #e0af68 !important;
            }
            
            .text-blue-700 {
                color: #7aa2f7 !important;
            }
            
            .text-blue-600 {
                color: #7dcfff !important;
            }
            
            .text-green-600 {
                color: #9ece6a !important;
            }
            
            .text-red-600 {
                color: #f7768e !important;
            }
            
            .text-purple-600 {
                color: #bb9af7 !important;
            }
            
            /* Progress bar */
            .q-linear-progress {
                background-color: #24283b;
            }
            
            .q-linear-progress__track {
                background-color: #24283b !important;
            }
            
            .q-linear-progress__model {
                background-color: #7aa2f7 !important;
            }
            
            /* Notifications */
            .q-notification {
                background-color: #1f2335;
                color: #a9b1d6;
                border: 1px solid #33467c;
            }
            
            /* Sidebar - improved contrast and focus */
            .q-drawer {
                background-color: #16161e !important;
            }
            
            .q-drawer .q-item {
                color: #c0caf5;
            }
            
            .q-drawer .q-item:hover {
                background-color: #1f2335;
            }
            
            .q-drawer .q-item:focus-visible {
                background-color: rgba(122, 162, 247, 0.2);
                outline: 2px solid #7aa2f7;
                outline-offset: -2px;
            }
            
            .q-drawer .q-item--active {
                background-color: #24283b;
                color: #7dcfff;
                border-left: 3px solid #7aa2f7;
            }
            
            .q-drawer .q-expansion-item {
                border: none;
            }
            
            .q-drawer .q-expansion-item .q-item {
                color: #c0caf5;
            }
            
            .q-drawer .q-expansion-item .q-item__section--side {
                color: #9aa5ce;
            }
            
            /* Header */
            .q-header {
                background-color: #16161e !important;
                border-bottom: 1px solid #33467c;
            }
            
            /* Footer */
            .q-footer {
                background-color: #16161e !important;
                border-top: 1px solid #33467c;
            }
            
            /* Tabs */
            .q-tabs {
                background-color: #1a1b26;
            }
            
            .q-tab {
                color: #565f89;
            }
            
            .q-tab--active {
                color: #7aa2f7 !important;
            }
            
            .q-tab__indicator {
                background-color: #7aa2f7 !important;
            }
            
            /* Dialogs */
            .q-dialog__backdrop {
                background-color: rgba(22, 22, 30, 0.8);
            }
            
            .q-dialog .q-card {
                background-color: #1f2335;
                color: #a9b1d6;
            }
            
            /* Chips/Tags */
            .q-chip {
                background-color: #24283b;
                color: #a9b1d6;
            }
            
            .q-chip--selected {
                background-color: #33467c;
                color: #7aa2f7;
            }
            
            /* Toggle */
            .q-toggle__inner {
                color: #565f89;
            }
            
            .q-toggle__inner--truthy {
                color: #9ece6a !important;
            }
            
            /* Checkbox */
            .q-checkbox__inner {
                color: #565f89;
            }
            
            .q-checkbox__inner--truthy {
                color: #7aa2f7 !important;
            }
            
            /* Links */
            a {
                color: #7dcfff;
            }
            
            a:hover {
                color: #7aa2f7;
            }
            
            /* Selection highlight */
            ::selection {
                background-color: #33467c;
                color: #c0caf5;
            }
            
            /* Tooltip */
            .q-tooltip {
                background-color: #24283b;
                color: #a9b1d6;
                border: 1px solid #33467c;
            }
            
            /* Badge */
            .q-badge {
                background-color: #7aa2f7;
                color: #1a1b26;
            }
            
            /* Avatar */
            .q-avatar {
                background-color: #24283b;
                color: #bb9af7;
            }
        '''
