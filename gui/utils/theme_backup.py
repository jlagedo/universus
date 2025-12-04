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

/* HQ/NQ Accent Colors - Light Mode */
.hq-accent, .text-hq {
    color: #00A88A !important;
    font-weight: 600;
}

.nq-accent, .text-nq {
    color: #D99200 !important;
    font-weight: 600;
}

.bg-hq {
    background-color: rgba(0, 168, 138, 0.1);
    border-left: 3px solid #00A88A;
}

.bg-nq {
    background-color: rgba(217, 146, 0, 0.1);
    border-left: 3px solid #D99200;
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
    """Manages theme for the application (dark mode only)."""
    
    def __init__(self, initial_mode: str = 'dark'):
        """Initialize theme manager.
        
        Args:
            initial_mode: Ignored, always uses dark mode
        """
        self.dark_mode = True
        self._fonts_loaded = False
    
    def load_fonts(self):
        """Load Google Fonts for gaming aesthetic."""
        if not self._fonts_loaded:
            ui.add_head_html(GOOGLE_FONTS_HTML)
            ui.add_css(FONT_CSS)
            self._fonts_loaded = True
    
    def apply_css(self):
        """Apply theme CSS to the application."""
        self.load_fonts()
        ui.colors(primary='#4DA6FF')  # Interactive blue
        ui.add_css(self._get_dark_css())
    
    def get_theme_classes(self, light: str, dark: str) -> str:
        """Get CSS classes based on current theme.
        
        Args:
            light: Classes for light theme (ignored)
            dark: Classes for dark theme
        
        Returns:
            Dark theme classes (always)
        """
        return dark
    
    @staticmethod
    def _get_dark_css() -> str:
        """Get dark theme CSS - Custom dark palette with WCAG AA contrast compliance.
        
        Color Palette:
        - Main Background: #1E1E1E
        - Card/Panel Background: #2A2A2A
        - Primary Text: #FFFFFF (headings, metrics)
        - Secondary Text: #AAAAAA (labels, descriptions)
        - HQ Tag Accent: #00C8A2
        - NQ Tag Accent: #FFB400
        - Interactive Elements: #4DA6FF
        - Borders/Dividers: #3A3A3A
        """
        return '''
            /* Dark Theme - WCAG AA Compliant
               Main Background: #1E1E1E
               Card Background: #2A2A2A
               Primary Text: #FFFFFF (21:1 contrast on #1E1E1E)
               Secondary Text: #AAAAAA (7.4:1 contrast on #1E1E1E)
               Interactive: #4DA6FF
               HQ Accent: #00C8A2
               NQ Accent: #FFB400
               Borders: #3A3A3A
            */
            
            /* Base styles */
            body, html {
                background-color: #1E1E1E;
                color: #FFFFFF;
                line-height: 1.5;
            }
            
            .nicegui-app {
                background-color: #1E1E1E;
            }
            
            /* Typography - Headings */
            h1, h2, h3, h4, h5, h6,
            .text-2xl, .text-xl, .text-lg {
                color: #FFFFFF;
                font-weight: 600;
            }
            
            /* Typography - Body text line height */
            p, .q-table tbody td, .q-item__label {
                line-height: 1.5;
            }
            
            /* Cards and Panels */
            .q-card, .q-expansion-item {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            
            .q-card .text-gray-500,
            .q-card .text-gray-400,
            .q-card .text-sm {
                color: #AAAAAA !important;
            }
            
            /* Expansion items in dark mode */
            .q-expansion-item .q-item__label {
                color: #FFFFFF !important;
            }
            
            .q-expansion-item__container {
                background-color: #2A2A2A;
            }
            
            /* Input fields */
            .q-field__control, .q-field__native input, .q-field__native textarea {
                color: #FFFFFF;
                background-color: #2A2A2A;
            }
            
            .q-field__label {
                color: #AAAAAA;
            }
            
            .q-field--focused .q-field__label {
                color: #4DA6FF !important;
            }
            
            .q-field--focused .q-field__control {
                border-color: #4DA6FF;
                box-shadow: 0 0 0 2px rgba(77, 166, 255, 0.3);
            }
            
            /* Tables */
            .q-table__card {
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
            
            .q-table tbody td {
                color: #FFFFFF;
                border-color: #3A3A3A;
                font-size: 1rem;
            }
            
            /* Alternating row colors */
            .q-table tbody tr:nth-child(even) {
                background-color: rgba(58, 58, 58, 0.5);
            }
            
            .q-table tbody tr:nth-child(odd) {
                background-color: transparent;
            }
            
            .q-table tbody tr:hover {
                background-color: #3A3A3A;
            }
            
            .q-table tbody tr:focus-within {
                background-color: rgba(77, 166, 255, 0.2);
                outline: 2px solid #4DA6FF;
                outline-offset: -2px;
            }
            
            .q-table thead tr {
                background-color: #2A2A2A;
            }
            
            .q-table thead th {
                color: #FFFFFF;
                background-color: #2A2A2A;
                border-color: #3A3A3A;
                font-weight: 700;
                font-size: 1.05rem;
            }
            
            /* HQ/NQ Accent Colors */
            .hq-accent, .text-hq {
                color: #00C8A2 !important;
                font-weight: 600;
            }
            
            .nq-accent, .text-nq {
                color: #FFB400 !important;
                font-weight: 600;
            }
            
            .bg-hq {
                background-color: rgba(0, 200, 162, 0.15);
                border-left: 3px solid #00C8A2;
            }
            
            .bg-nq {
                background-color: rgba(255, 180, 0, 0.15);
                border-left: 3px solid #FFB400;
            }
            
            /* High-impact metrics */
            .metric-highlight {
                color: #4DA6FF !important;
                font-weight: 600;
            }
            
            .metric-volume {
                color: #00C8A2 !important;
                font-weight: 600;
            }
            
            .metric-price {
                color: #FFB400 !important;
                font-weight: 600;
            }
            
            /* Buttons - Interactive elements */
            .q-btn {
                color: #FFFFFF;
            }
            
            .q-btn--flat {
                color: #4DA6FF;
            }
            
            .q-btn--flat:hover {
                background-color: rgba(77, 166, 255, 0.15);
            }
            
            .q-btn:focus-visible {
                box-shadow: 0 0 0 3px rgba(77, 166, 255, 0.5);
            }
            
            .q-btn.bg-primary {
                background-color: #4DA6FF !important;
                color: #1E1E1E !important;
            }
            
            .q-btn.bg-primary:hover {
                background-color: #6BB8FF !important;
            }
            
            /* Separators */
            .q-separator {
                background-color: #3A3A3A;
            }
            
            /* Select/Dropdown */
            .q-menu {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            
            .q-item {
                color: #FFFFFF;
            }
            
            .q-item:hover {
                background-color: #3A3A3A;
            }
            
            .q-item:focus-visible {
                background-color: rgba(77, 166, 255, 0.2);
                outline: 2px solid #4DA6FF;
                outline-offset: -2px;
            }
            
            .q-item--active {
                background-color: #3A3A3A;
                color: #4DA6FF;
            }
            
            /* Scrollbars */
            ::-webkit-scrollbar {
                width: 8px;
                height: 8px;
            }
            
            ::-webkit-scrollbar-track {
                background: #1E1E1E;
            }
            
            ::-webkit-scrollbar-thumb {
                background: #3A3A3A;
                border-radius: 4px;
            }
            
            ::-webkit-scrollbar-thumb:hover {
                background: #4A4A4A;
            }
            
            /* Labels and text */
            .text-gray-900, .text-white {
                color: #FFFFFF !important;
            }
            
            .text-gray-500, .text-gray-400 {
                color: #AAAAAA !important;
            }
            
            .text-gray-600, .text-gray-300 {
                color: #BBBBBB !important;
            }
            
            /* Background colors */
            .bg-white {
                background-color: #2A2A2A !important;
            }
            
            .bg-gray-100, .bg-gray-200 {
                background-color: #2A2A2A !important;
            }
            
            .bg-gray-800, .bg-gray-900 {
                background-color: #1E1E1E !important;
            }
            
            .bg-blue-50 {
                background-color: #2A2A2A !important;
                border-left: 3px solid #4DA6FF !important;
            }
            
            .bg-yellow-50 {
                background-color: #2A2A2A !important;
                border-left: 3px solid #FFB400 !important;
            }
            
            /* Accent text colors */
            .text-yellow-700, .text-yellow-600, .text-amber-400, .text-amber-600, .text-orange-400 {
                color: #FFB400 !important;
            }
            
            .text-blue-700, .text-blue-600, .text-blue-400 {
                color: #4DA6FF !important;
            }
            
            .text-green-600, .text-green-400, .text-teal-400, .text-teal-600 {
                color: #00C8A2 !important;
            }
            
            .text-red-600, .text-red-400 {
                color: #FF6B6B !important;
            }
            
            .text-purple-600, .text-purple-400 {
                color: #B794F6 !important;
            }
            
            /* Progress bar */
            .q-linear-progress {
                background-color: #3A3A3A;
            }
            
            .q-linear-progress__track {
                background-color: #3A3A3A !important;
            }
            
            .q-linear-progress__model {
                background-color: #4DA6FF !important;
            }
            
            /* Notifications */
            .q-notification {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            
            /* Sidebar */
            .q-drawer {
                background-color: #1E1E1E !important;
            }
            
            .q-drawer .q-item {
                color: #FFFFFF;
            }
            
            .q-drawer .q-item:hover {
                background-color: #2A2A2A;
            }
            
            .q-drawer .q-item:focus-visible {
                background-color: rgba(77, 166, 255, 0.2);
                outline: 2px solid #4DA6FF;
                outline-offset: -2px;
            }
            
            .q-drawer .q-item--active {
                background-color: #3A3A3A;
                color: #4DA6FF;
                border-left: 3px solid #4DA6FF;
            }
            
            .q-drawer .q-expansion-item {
                border: none;
            }
            
            .q-drawer .q-expansion-item .q-item {
                color: #FFFFFF;
            }
            
            .q-drawer .q-expansion-item .q-item__section--side {
                color: #AAAAAA;
            }
            
            /* Header */
            .q-header {
                background-color: #1E1E1E !important;
                border-bottom: 1px solid #3A3A3A;
            }
            
            /* Footer */
            .q-footer {
                background-color: #1E1E1E !important;
                border-top: 1px solid #3A3A3A;
            }
            
            /* Tabs */
            .q-tabs {
                background-color: #1E1E1E;
            }
            
            .q-tab {
                color: #AAAAAA;
            }
            
            .q-tab--active {
                color: #4DA6FF !important;
            }
            
            .q-tab__indicator {
                background-color: #4DA6FF !important;
            }
            
            /* Dialogs */
            .q-dialog__backdrop {
                background-color: rgba(0, 0, 0, 0.7);
            }
            
            .q-dialog .q-card {
                background-color: #2A2A2A;
                color: #FFFFFF;
            }
            
            /* Chips/Tags */
            .q-chip {
                background-color: #3A3A3A;
                color: #FFFFFF;
            }
            
            .q-chip--selected {
                background-color: #4DA6FF;
                color: #1E1E1E;
            }
            
            /* Toggle */
            .q-toggle__inner {
                color: #AAAAAA;
            }
            
            .q-toggle__inner--truthy {
                color: #00C8A2 !important;
            }
            
            /* Checkbox */
            .q-checkbox__inner {
                color: #AAAAAA;
            }
            
            .q-checkbox__inner--truthy {
                color: #4DA6FF !important;
            }
            
            /* Links */
            a {
                color: #4DA6FF;
            }
            
            a:hover {
                color: #6BB8FF;
            }
            
            /* Selection highlight */
            ::selection {
                background-color: rgba(77, 166, 255, 0.3);
                color: #FFFFFF;
            }
            
            /* Tooltip */
            .q-tooltip {
                background-color: #2A2A2A;
                color: #FFFFFF;
                border: 1px solid #3A3A3A;
            }
            
            /* Badge */
            .q-badge {
                background-color: #4DA6FF;
                color: #1E1E1E;
            }
            
            /* Avatar */
            .q-avatar {
                background-color: #3A3A3A;
                color: #4DA6FF;
            }
        '''
