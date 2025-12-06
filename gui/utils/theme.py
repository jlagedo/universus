"""
Theme management for the GUI.

Uses the unified design system for consistent styling across all components.
"""

from nicegui import ui
from .design_system import COLORS, TYPOGRAPHY


# Google Fonts for gaming aesthetic (Material Icons are built into NiceGUI/Quasar)
GOOGLE_FONTS_HTML = '''
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Exo+2:ital,wght@0,100..900;1,100..900&family=Rajdhani:wght@300;400;500;600;700&display=swap" rel="stylesheet">
'''

# Font and base CSS for gaming theme
BASE_CSS = f'''
/* ============================================
   UNIVERSUS DESIGN SYSTEM - Base Styles
   ============================================ */

/* CSS Custom Properties (Design Tokens) */
:root {{
    /* Fonts */
    --font-display: {TYPOGRAPHY.FONT_DISPLAY};
    --font-body: {TYPOGRAPHY.FONT_BODY};
    --font-accent: {TYPOGRAPHY.FONT_ACCENT};
    
    /* Colors */
    --color-bg-main: {COLORS.BG_MAIN};
    --color-bg-card: {COLORS.BG_CARD};
    --color-bg-elevated: {COLORS.BG_ELEVATED};
    --color-bg-hover: {COLORS.BG_HOVER};
    --color-text-primary: {COLORS.TEXT_PRIMARY};
    --color-text-secondary: {COLORS.TEXT_SECONDARY};
    --color-text-muted: {COLORS.TEXT_MUTED};
    --color-hq: {COLORS.HQ_ACCENT};
    --color-nq: {COLORS.NQ_ACCENT};
    --color-interactive: {COLORS.INTERACTIVE};
    --color-interactive-hover: {COLORS.INTERACTIVE_HOVER};
    --color-border: {COLORS.BORDER};
    --color-success: {COLORS.SUCCESS};
    --color-warning: {COLORS.WARNING};
    --color-error: {COLORS.ERROR};
    
    /* Typography Scale */
    --text-xs: {TYPOGRAPHY.SIZE_XS};
    --text-sm: {TYPOGRAPHY.SIZE_SM};
    --text-base: {TYPOGRAPHY.SIZE_BASE};
    --text-lg: {TYPOGRAPHY.SIZE_LG};
    --text-xl: {TYPOGRAPHY.SIZE_XL};
    --text-2xl: {TYPOGRAPHY.SIZE_2XL};
    
    /* Line Heights */
    --leading-tight: {TYPOGRAPHY.LINE_HEIGHT_TIGHT};
    --leading-normal: {TYPOGRAPHY.LINE_HEIGHT_NORMAL};
    --leading-relaxed: {TYPOGRAPHY.LINE_HEIGHT_RELAXED};
}}

/* Base body font */
body, html {{
    font-family: var(--font-body);
    line-height: var(--leading-normal);
}}

/* ============================================
   TYPOGRAPHY HIERARCHY
   ============================================ */

/* Page titles and major headings - Orbitron for gaming feel */
h1, h2, h3,
.text-2xl, .text-xl,
.title, .header-title,
.q-toolbar__title {{
    font-family: var(--font-display);
    font-weight: 700;
    letter-spacing: 0.05em;
    line-height: var(--leading-tight);
}}

/* Section headings and subheadings */
h4, h5, h6,
.text-lg {{
    font-family: var(--font-display);
    font-weight: 600;
    letter-spacing: 0.03em;
}}

/* Navigation, menus, and labels - Rajdhani for clean tech look */
.q-item__label,
.nav-item, .menu-item,
.q-tab__label,
.sidebar-item,
.stat-label {{
    font-family: var(--font-accent);
    font-weight: 500;
    font-size: var(--text-sm);
}}

/* Stats and metrics - Rajdhani for clarity */
.stat-value,
.q-table tbody td,
.q-table thead th,
.data-value {{
    font-family: var(--font-accent);
}}

/* ============================================
   TABLE STYLING
   ============================================ */

.q-table tbody td {{
    font-size: var(--text-base);
    padding: 10px 14px;
    line-height: var(--leading-normal);
}}

.q-table thead th {{
    font-size: 1.05rem;
    font-weight: 700;
    padding: 12px 14px;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}}

/* Item name column - larger and bolder */
.q-table tbody td[data-col="item_name"],
.q-table tbody td[data-col="item"],
.q-table tbody td[data-col="name"] {{
    font-size: 1.05rem;
    font-weight: 600;
}}

/* ============================================
   HQ/NQ ACCENT SYSTEM
   ============================================ */

.hq-accent, .text-hq {{
    color: var(--color-hq) !important;
    font-weight: 600;
}}

.nq-accent, .text-nq {{
    color: var(--color-nq) !important;
    font-weight: 600;
}}

.bg-hq {{
    background-color: rgba(0, 200, 162, 0.15);
    border-left: 3px solid var(--color-hq);
}}

.bg-nq {{
    background-color: rgba(255, 180, 0, 0.15);
    border-left: 3px solid var(--color-nq);
}}

/* ============================================
   ITEM ICONS (Spritesheet-based)
   ============================================ */

.item-icon {{
    display: inline-block;
    vertical-align: middle;
    flex-shrink: 0;
    background-repeat: no-repeat;
}}

/* Item name cell with icon - flexbox layout */
.item-cell-with-icon {{
    display: flex !important;
    align-items: center;
    gap: 12px;
}}

.item-cell-with-icon .item-name {{
    font-weight: 600;
    font-size: 1.05rem;
}}

/* ============================================
   METRIC HIGHLIGHTING
   ============================================ */

.metric-highlight {{
    color: var(--color-interactive) !important;
    font-weight: 600;
}}

.metric-volume {{
    color: var(--color-hq) !important;
    font-weight: 600;
}}

.metric-price {{
    color: var(--color-nq) !important;
    font-weight: 600;
}}

/* ============================================
   BUTTONS
   ============================================ */

.q-btn__content,
.q-btn {{
    font-family: var(--font-body);
    font-weight: 600;
    letter-spacing: 0.02em;
}}

/* ============================================
   FORM ELEMENTS
   ============================================ */

.q-field__native input,
.q-field__native textarea,
.q-field__label {{
    font-family: var(--font-body);
}}

/* ============================================
   CARDS AND PANELS
   ============================================ */

.q-card__section {{
    font-family: var(--font-body);
}}

/* ============================================
   NOTIFICATIONS AND BADGES
   ============================================ */

.q-notification__message,
.q-badge {{
    font-family: var(--font-accent);
    font-weight: 600;
}}

/* ============================================
   FOOTER
   ============================================ */

.q-footer {{
    font-family: var(--font-accent);
}}

/* ============================================
   ACCESSIBILITY
   ============================================ */

/* Focus styles for keyboard navigation */
*:focus {{
    outline: 2px solid var(--color-interactive);
    outline-offset: 2px;
}}

*:focus:not(:focus-visible) {{
    outline: none;
}}

*:focus-visible {{
    outline: 2px solid var(--color-interactive);
    outline-offset: 2px;
}}

/* Skip link for keyboard users */
.skip-link {{
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--color-interactive);
    color: white;
    padding: 8px 16px;
    z-index: 100;
    text-decoration: none;
    font-weight: 600;
}}

.skip-link:focus {{
    top: 0;
}}

/* Button keyboard focus enhancement */
.q-btn:focus-visible {{
    box-shadow: 0 0 0 3px rgba(77, 166, 255, 0.4);
}}

/* Input keyboard focus enhancement */
.q-field--focused .q-field__control {{
    box-shadow: 0 0 0 2px rgba(77, 166, 255, 0.3);
}}

/* Table row keyboard focus */
.q-table tbody tr:focus-within {{
    background-color: rgba(77, 166, 255, 0.1);
}}

/* Ensure minimum touch target size (44px for WCAG) */
.q-btn, .q-item {{
    min-height: 44px;
    min-width: 44px;
}}
'''

# Dark theme CSS - WCAG AA compliant
DARK_THEME_CSS = f'''
/* ============================================
   DARK THEME - WCAG AA Compliant
   
   Contrast Ratios:
   - Primary Text (#FFFFFF) on Main BG (#1E1E1E): 21:1 ✓
   - Secondary Text (#B0B0B0) on Main BG (#1E1E1E): 8.5:1 ✓
   - Secondary Text (#B0B0B0) on Card BG (#2A2A2A): 6.5:1 ✓
   - Interactive (#4DA6FF) on Main BG (#1E1E1E): 7.2:1 ✓
   ============================================ */

/* Base styles */
body, html {{
    background-color: var(--color-bg-main);
    color: var(--color-text-primary);
}}

.nicegui-app {{
    background-color: var(--color-bg-main);
}}

/* Typography - Headings */
h1, h2, h3, h4, h5, h6,
.text-2xl, .text-xl, .text-lg {{
    color: var(--color-text-primary);
}}

/* Typography - Body text line height */
p, .q-table tbody td, .q-item__label {{
    line-height: var(--leading-normal);
}}

/* ============================================
   CARDS AND PANELS
   ============================================ */

.q-card, .q-expansion-item {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}}

.q-card .text-gray-500,
.q-card .text-gray-400,
.q-card .text-sm {{
    color: var(--color-text-secondary) !important;
}}

/* Expansion items */
.q-expansion-item .q-item__label {{
    color: var(--color-text-primary) !important;
}}

.q-expansion-item__container {{
    background-color: var(--color-bg-card);
}}

/* ============================================
   FORM ELEMENTS
   ============================================ */

.q-field__control, 
.q-field__native input, 
.q-field__native textarea {{
    color: var(--color-text-primary);
    background-color: var(--color-bg-card);
}}

.q-field__label {{
    color: var(--color-text-secondary);
}}

.q-field--focused .q-field__label {{
    color: var(--color-interactive) !important;
}}

.q-field--focused .q-field__control {{
    border-color: var(--color-interactive);
    box-shadow: 0 0 0 2px rgba(77, 166, 255, 0.3);
}}

/* ============================================
   TABLES
   ============================================ */

.q-table__card {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
}}

.q-table tbody td {{
    color: var(--color-text-primary);
    border-color: var(--color-border);
}}

/* Alternating row colors */
.q-table tbody tr:nth-child(even) {{
    background-color: rgba(58, 58, 58, 0.5);
}}

.q-table tbody tr:nth-child(odd) {{
    background-color: transparent;
}}

.q-table tbody tr:hover {{
    background-color: var(--color-bg-hover);
}}

.q-table tbody tr:focus-within {{
    background-color: rgba(77, 166, 255, 0.2);
    outline: 2px solid var(--color-interactive);
    outline-offset: -2px;
}}

.q-table thead tr {{
    background-color: var(--color-bg-card);
}}

.q-table thead th {{
    color: var(--color-text-primary);
    background-color: var(--color-bg-card);
    border-color: var(--color-border);
    font-weight: 700;
}}

/* ============================================
   BUTTONS
   ============================================ */

.q-btn {{
    color: var(--color-text-primary);
}}

.q-btn--flat {{
    color: var(--color-interactive);
}}

.q-btn--flat:hover {{
    background-color: rgba(77, 166, 255, 0.15);
}}

.q-btn:focus-visible {{
    box-shadow: 0 0 0 3px rgba(77, 166, 255, 0.5);
}}

.q-btn.bg-primary {{
    background-color: var(--color-interactive) !important;
    color: var(--color-bg-main) !important;
}}

.q-btn.bg-primary:hover {{
    background-color: var(--color-interactive-hover) !important;
}}

/* ============================================
   SEPARATORS
   ============================================ */

.q-separator {{
    background-color: var(--color-border);
}}

/* ============================================
   SELECT/DROPDOWN
   ============================================ */

.q-menu {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}}

.q-item {{
    color: var(--color-text-primary);
}}

.q-item:hover {{
    background-color: var(--color-bg-hover);
}}

.q-item:focus-visible {{
    background-color: rgba(77, 166, 255, 0.2);
    outline: 2px solid var(--color-interactive);
    outline-offset: -2px;
}}

.q-item--active {{
    background-color: var(--color-bg-hover);
    color: var(--color-interactive);
}}

/* ============================================
   SCROLLBARS
   ============================================ */

::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}

::-webkit-scrollbar-track {{
    background: var(--color-bg-main);
}}

::-webkit-scrollbar-thumb {{
    background: var(--color-border);
    border-radius: 4px;
}}

::-webkit-scrollbar-thumb:hover {{
    background: #4A4A4A;
}}

/* ============================================
   TEXT COLOR OVERRIDES
   ============================================ */

.text-gray-900, .text-white {{
    color: var(--color-text-primary) !important;
}}

.text-gray-500, .text-gray-400 {{
    color: var(--color-text-secondary) !important;
}}

.text-gray-600, .text-gray-300 {{
    color: #BBBBBB !important;
}}

/* ============================================
   BACKGROUND COLOR OVERRIDES
   ============================================ */

.bg-white {{
    background-color: var(--color-bg-card) !important;
}}

.bg-gray-100, .bg-gray-200 {{
    background-color: var(--color-bg-card) !important;
}}

.bg-gray-800, .bg-gray-900 {{
    background-color: var(--color-bg-main) !important;
}}

.bg-blue-50 {{
    background-color: var(--color-bg-card) !important;
    border-left: 3px solid var(--color-interactive) !important;
}}

.bg-yellow-50 {{
    background-color: var(--color-bg-card) !important;
    border-left: 3px solid var(--color-nq) !important;
}}

/* ============================================
   ACCENT TEXT COLORS
   ============================================ */

.text-yellow-700, .text-yellow-600, 
.text-amber-400, .text-amber-600, .text-orange-400 {{
    color: var(--color-nq) !important;
}}

.text-blue-700, .text-blue-600, .text-blue-400 {{
    color: var(--color-interactive) !important;
}}

.text-green-600, .text-green-400, 
.text-teal-400, .text-teal-600 {{
    color: var(--color-hq) !important;
}}

.text-red-600, .text-red-400 {{
    color: var(--color-error) !important;
}}

.text-purple-600, .text-purple-400 {{
    color: #B794F6 !important;
}}

/* ============================================
   PROGRESS BAR
   ============================================ */

.q-linear-progress {{
    background-color: var(--color-border);
}}

.q-linear-progress__track {{
    background-color: var(--color-border) !important;
}}

.q-linear-progress__model {{
    background-color: var(--color-interactive) !important;
}}

/* ============================================
   NOTIFICATIONS
   ============================================ */

.q-notification {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}}

/* ============================================
   SIDEBAR / DRAWER
   ============================================ */

.q-drawer {{
    background-color: var(--color-bg-main) !important;
}}

.q-drawer .q-item {{
    color: var(--color-text-primary);
}}

.q-drawer .q-item:hover {{
    background-color: var(--color-bg-card);
}}

.q-drawer .q-item:focus-visible {{
    background-color: rgba(77, 166, 255, 0.2);
    outline: 2px solid var(--color-interactive);
    outline-offset: -2px;
}}

.q-drawer .q-item--active {{
    background-color: var(--color-bg-hover);
    color: var(--color-interactive);
    border-left: 3px solid var(--color-interactive);
}}

.q-drawer .q-expansion-item {{
    border: none;
}}

.q-drawer .q-expansion-item .q-item {{
    color: var(--color-text-primary);
}}

.q-drawer .q-expansion-item .q-item__section--side {{
    color: var(--color-text-secondary);
}}

/* ============================================
   HEADER
   ============================================ */

.q-header {{
    background-color: var(--color-bg-main) !important;
    border-bottom: 1px solid var(--color-border);
}}

/* ============================================
   FOOTER
   ============================================ */

.q-footer {{
    background-color: var(--color-bg-main) !important;
    border-top: 1px solid var(--color-border);
}}

/* ============================================
   TABS
   ============================================ */

.q-tabs {{
    background-color: var(--color-bg-main);
}}

.q-tab {{
    color: var(--color-text-secondary);
}}

.q-tab--active {{
    color: var(--color-interactive) !important;
}}

.q-tab__indicator {{
    background-color: var(--color-interactive) !important;
}}

/* ============================================
   DIALOGS
   ============================================ */

.q-dialog__backdrop {{
    background-color: rgba(0, 0, 0, 0.7);
}}

.q-dialog .q-card {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
}}

/* ============================================
   CHIPS/TAGS
   ============================================ */

.q-chip {{
    background-color: var(--color-bg-hover);
    color: var(--color-text-primary);
}}

.q-chip--selected {{
    background-color: var(--color-interactive);
    color: var(--color-bg-main);
}}

/* ============================================
   TOGGLE
   ============================================ */

.q-toggle__inner {{
    color: var(--color-text-secondary);
}}

.q-toggle__inner--truthy {{
    color: var(--color-hq) !important;
}}

/* ============================================
   CHECKBOX
   ============================================ */

.q-checkbox__inner {{
    color: var(--color-text-secondary);
}}

.q-checkbox__inner--truthy {{
    color: var(--color-interactive) !important;
}}

/* ============================================
   LINKS
   ============================================ */

a {{
    color: var(--color-interactive);
}}

a:hover {{
    color: var(--color-interactive-hover);
}}

/* ============================================
   SELECTION
   ============================================ */

::selection {{
    background-color: rgba(77, 166, 255, 0.3);
    color: var(--color-text-primary);
}}

/* ============================================
   TOOLTIP
   ============================================ */

.q-tooltip {{
    background-color: var(--color-bg-card);
    color: var(--color-text-primary);
    border: 1px solid var(--color-border);
}}

/* ============================================
   BADGE
   ============================================ */

.q-badge {{
    background-color: var(--color-interactive);
    color: var(--color-bg-main);
}}

/* ============================================
   AVATAR
   ============================================ */

.q-avatar {{
    background-color: var(--color-bg-hover);
    color: var(--color-interactive);
}}
'''


class ThemeManager:
    """Manages theme for the application (dark mode only)."""
    
    def __init__(self, initial_mode: str = 'dark'):
        """Initialize theme manager.
        
        Args:
            initial_mode: Ignored, always uses dark mode
        """
        self.dark_mode = True
    
    def load_fonts(self):
        """Load Google Fonts for gaming aesthetic.
        
        Note: This must be called on every page render to ensure
        fonts and base CSS are applied after page reload.
        """
        ui.add_head_html(GOOGLE_FONTS_HTML)
        ui.add_css(BASE_CSS)
    
    def apply_css(self):
        """Apply theme CSS to the application.
        
        Note: This must be called on every page render to ensure
        dark theme CSS is applied after page reload.
        """
        self.load_fonts()
        ui.colors(primary='#4DA6FF')  # Interactive blue
        ui.add_css(DARK_THEME_CSS)
    
    def get_theme_classes(self, light: str, dark: str) -> str:
        """Get CSS classes based on current theme.
        
        Args:
            light: Classes for light theme (ignored)
            dark: Classes for dark theme
        
        Returns:
            Dark theme classes (always)
        """
        return dark
