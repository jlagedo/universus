"""
Unified Design System for Universus GUI.

This module defines the complete design token system including colors,
typography, spacing, and component styles. All GUI components should
reference these constants for consistent styling.

Color Palette (WCAG AA Compliant):
- Main Background: #1E1E1E
- Card/Panel Background: #2A2A2A  
- Primary Text: #FFFFFF (21:1 contrast on #1E1E1E)
- Secondary Text: #B0B0B0 (8.5:1 contrast - improved from #AAAAAA)
- HQ Tag: #00C8A2
- NQ Tag: #FFB400
- Interactive Elements: #4DA6FF
- Borders/Dividers: #3A3A3A
"""

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# COLOR PALETTE
# =============================================================================

@dataclass(frozen=True)
class Colors:
    """Design system color tokens."""
    
    # Background colors
    BG_MAIN: str = "#1E1E1E"
    BG_CARD: str = "#2A2A2A"
    BG_ELEVATED: str = "#333333"
    BG_HOVER: str = "#3A3A3A"
    
    # Text colors
    TEXT_PRIMARY: str = "#FFFFFF"
    TEXT_SECONDARY: str = "#B0B0B0"  # Improved contrast from #AAAAAA
    TEXT_MUTED: str = "#888888"
    
    # Accent colors
    HQ_ACCENT: str = "#00C8A2"       # Teal for HQ items
    NQ_ACCENT: str = "#FFB400"       # Amber for NQ items
    INTERACTIVE: str = "#4DA6FF"     # Blue for interactive elements
    INTERACTIVE_HOVER: str = "#6BB8FF"
    
    # Semantic colors
    SUCCESS: str = "#00C8A2"
    WARNING: str = "#FFB400"
    ERROR: str = "#FF6B6B"
    INFO: str = "#4DA6FF"
    
    # Border colors
    BORDER: str = "#3A3A3A"
    BORDER_SUBTLE: str = "#2E2E2E"
    BORDER_FOCUS: str = "#4DA6FF"
    
    # Metric colors (for data visualization)
    METRIC_VOLUME: str = "#00C8A2"   # Green/teal
    METRIC_PRICE: str = "#FFB400"    # Amber
    METRIC_VELOCITY: str = "#4DA6FF" # Blue


COLORS = Colors()


# =============================================================================
# TYPOGRAPHY
# =============================================================================

@dataclass(frozen=True)
class Typography:
    """Design system typography tokens."""
    
    # Font families (from theme.py)
    FONT_DISPLAY: str = "'Orbitron', 'Segoe UI', Roboto, sans-serif"
    FONT_BODY: str = "'Exo 2', 'Segoe UI', Roboto, sans-serif"
    FONT_ACCENT: str = "'Rajdhani', 'Segoe UI', Roboto, sans-serif"
    
    # Font sizes
    SIZE_XS: str = "0.75rem"      # 12px
    SIZE_SM: str = "0.875rem"     # 14px - Labels
    SIZE_BASE: str = "1rem"       # 16px - Body/Metrics
    SIZE_LG: str = "1.125rem"     # 18px - Subheadings
    SIZE_XL: str = "1.25rem"      # 20px
    SIZE_2XL: str = "1.5rem"      # 24px - Page titles
    SIZE_3XL: str = "1.875rem"    # 30px
    
    # Font weights
    WEIGHT_NORMAL: str = "400"    # Labels, body text
    WEIGHT_MEDIUM: str = "500"    # Emphasis
    WEIGHT_SEMIBOLD: str = "600"  # Metrics, subheadings
    WEIGHT_BOLD: str = "700"      # Headings
    
    # Line heights
    LINE_HEIGHT_TIGHT: str = "1.25"
    LINE_HEIGHT_NORMAL: str = "1.5"
    LINE_HEIGHT_RELAXED: str = "1.75"


TYPOGRAPHY = Typography()


# =============================================================================
# SPACING
# =============================================================================

@dataclass(frozen=True)
class Spacing:
    """Design system spacing tokens (in Tailwind units)."""
    
    # Base spacing scale
    NONE: str = "0"
    XS: str = "1"      # 0.25rem / 4px
    SM: str = "2"      # 0.5rem / 8px
    MD: str = "4"      # 1rem / 16px
    LG: str = "6"      # 1.5rem / 24px
    XL: str = "8"      # 2rem / 32px
    XXL: str = "12"    # 3rem / 48px
    
    # Component-specific spacing
    CARD_PADDING: str = "4"        # p-4
    SECTION_GAP: str = "6"         # gap-6
    ELEMENT_GAP: str = "4"         # gap-4
    INLINE_GAP: str = "2"          # gap-2


SPACING = Spacing()


# =============================================================================
# COMPONENT STYLES
# =============================================================================

@dataclass(frozen=True)
class ComponentStyles:
    """Pre-built component class strings for consistency."""
    
    # Cards
    CARD_BASE: str = "bg-gray-800 border border-gray-700 rounded-lg"
    CARD_ELEVATED: str = "bg-gray-800 border border-gray-700 rounded-lg shadow-lg"
    CARD_FULL: str = "w-full bg-gray-800 border border-gray-700 rounded-lg p-4"
    CARD_FIXED: str = "w-64 bg-gray-800 border border-gray-700 rounded-lg p-4"
    
    # Buttons
    BTN_PRIMARY: str = "bg-blue-500 text-white hover:bg-blue-400"
    BTN_SECONDARY: str = "bg-gray-700 text-white hover:bg-gray-600"
    BTN_GHOST: str = "text-blue-400 hover:bg-gray-700"
    BTN_DANGER: str = "bg-red-600 text-white hover:bg-red-500"
    
    # Text styles
    HEADING_PAGE: str = "text-2xl font-bold text-white mb-4"
    HEADING_SECTION: str = "text-xl font-semibold text-white mb-2"
    HEADING_CARD: str = "text-lg font-semibold text-white mb-2"
    TEXT_BODY: str = "text-base text-gray-300"
    TEXT_SECONDARY: str = "text-sm text-gray-400"
    TEXT_LABEL: str = "text-sm font-normal text-gray-400"
    TEXT_METRIC: str = "text-base font-semibold"
    
    # Accent text
    TEXT_HQ: str = "text-teal-400 font-semibold"
    TEXT_NQ: str = "text-amber-400 font-semibold"
    TEXT_SUCCESS: str = "text-teal-400"
    TEXT_WARNING: str = "text-amber-400"
    TEXT_ERROR: str = "text-red-400"
    TEXT_INFO: str = "text-blue-400"
    
    # Layout containers
    PAGE_CONTAINER: str = "w-full p-6"
    SECTION_CONTAINER: str = "w-full mb-6"
    ROW_CENTERED: str = "w-full items-center"
    ROW_SPACED: str = "w-full items-center justify-between"
    
    # Form elements
    INPUT_BASE: str = "w-full bg-gray-800 text-white"
    SELECT_BASE: str = "w-full bg-gray-800 text-white"
    
    # Table styles
    TABLE_BASE: str = "w-full"
    
    # Badges/Tags
    TAG_HQ: str = "bg-teal-900 text-teal-300 border border-teal-700 px-2 py-1 rounded text-xs font-semibold"
    TAG_NQ: str = "bg-amber-900 text-amber-300 border border-amber-700 px-2 py-1 rounded text-xs font-semibold"
    TAG_DEFAULT: str = "bg-gray-700 text-gray-300 border border-gray-600 px-2 py-1 rounded text-xs font-semibold"


STYLES = ComponentStyles()


# =============================================================================
# QUASAR PROPS
# =============================================================================

@dataclass(frozen=True)
class QuasarProps:
    """Standard Quasar component props for consistency."""
    
    # Buttons
    BTN_PRIMARY: str = "color=primary unelevated"
    BTN_SECONDARY: str = "color=grey-8 unelevated"
    BTN_FLAT: str = "flat"
    BTN_ICON: str = "flat round"
    BTN_DENSE: str = "dense unelevated"
    
    # Inputs
    INPUT_OUTLINED: str = "dark dense outlined"
    INPUT_FILLED: str = "dark dense filled"
    SELECT_OUTLINED: str = "dark dense outlined"
    
    # Tables
    TABLE_FLAT: str = "flat bordered"
    TABLE_VIRTUAL: str = "flat bordered virtual-scroll"
    
    # Cards
    CARD_FLAT: str = "flat"
    CARD_BORDERED: str = "flat bordered"
    
    # Expansion items
    EXPANSION_DENSE: str = "dense header-class=\"text-weight-medium\""


PROPS = QuasarProps()


# =============================================================================
# CSS CLASS BUILDERS
# =============================================================================

def card_classes(width: str = "full", padding: bool = True) -> str:
    """Build consistent card classes.
    
    Args:
        width: Card width - 'full', 'fixed', 'lg', 'xl', '2xl'
        padding: Whether to include padding
    
    Returns:
        CSS class string
    """
    base = "bg-gray-800 border border-gray-700 rounded-lg"
    
    width_map = {
        "full": "w-full",
        "fixed": "w-64",
        "lg": "w-full max-w-lg",
        "xl": "w-full max-w-xl",
        "2xl": "w-full max-w-2xl",
    }
    
    width_class = width_map.get(width, "w-full")
    padding_class = "p-4" if padding else ""
    
    return f"{width_class} {base} {padding_class}".strip()


def text_classes(
    size: str = "base",
    weight: str = "normal",
    color: str = "primary"
) -> str:
    """Build consistent text classes.
    
    Args:
        size: Font size - 'xs', 'sm', 'base', 'lg', 'xl', '2xl'
        weight: Font weight - 'normal', 'medium', 'semibold', 'bold'
        color: Text color - 'primary', 'secondary', 'muted', 'hq', 'nq', 'success', etc.
    
    Returns:
        CSS class string
    """
    size_map = {
        "xs": "text-xs",
        "sm": "text-sm",
        "base": "text-base",
        "lg": "text-lg",
        "xl": "text-xl",
        "2xl": "text-2xl",
    }
    
    weight_map = {
        "normal": "font-normal",
        "medium": "font-medium",
        "semibold": "font-semibold",
        "bold": "font-bold",
    }
    
    color_map = {
        "primary": "text-white",
        "secondary": "text-gray-400",
        "muted": "text-gray-500",
        "hq": "text-teal-400",
        "nq": "text-amber-400",
        "success": "text-teal-400",
        "warning": "text-amber-400",
        "error": "text-red-400",
        "info": "text-blue-400",
    }
    
    return f"{size_map.get(size, 'text-base')} {weight_map.get(weight, '')} {color_map.get(color, 'text-white')}".strip()


def heading_classes(level: int = 2, margin: bool = True) -> str:
    """Build consistent heading classes.
    
    Args:
        level: Heading level 1-4
        margin: Whether to include bottom margin
    
    Returns:
        CSS class string
    """
    level_styles = {
        1: "text-3xl font-bold text-white",
        2: "text-2xl font-bold text-white",
        3: "text-xl font-semibold text-white",
        4: "text-lg font-semibold text-white",
    }
    
    base = level_styles.get(level, level_styles[2])
    margin_class = "mb-4" if margin and level <= 2 else "mb-2" if margin else ""
    
    return f"{base} {margin_class}".strip()


def metric_classes(type: str = "default") -> str:
    """Build consistent metric display classes.
    
    Args:
        type: Metric type - 'default', 'hq', 'nq', 'volume', 'price', 'velocity'
    
    Returns:
        CSS class string
    """
    type_map = {
        "default": "text-base font-semibold text-white",
        "hq": "text-base font-semibold hq-accent",
        "nq": "text-base font-semibold nq-accent",
        "volume": "text-base font-semibold metric-volume",
        "price": "text-base font-semibold metric-price",
        "velocity": "text-base font-semibold metric-highlight",
    }
    
    return type_map.get(type, type_map["default"])


def row_classes(
    align: str = "start",
    justify: str = "start",
    gap: str = "4",
    wrap: bool = False
) -> str:
    """Build consistent row layout classes.
    
    Args:
        align: Vertical alignment - 'start', 'center', 'end', 'stretch'
        justify: Horizontal alignment - 'start', 'center', 'end', 'between', 'around'
        gap: Gap size - '0', '1', '2', '4', '6', '8'
        wrap: Whether content should wrap
    
    Returns:
        CSS class string
    """
    align_map = {
        "start": "items-start",
        "center": "items-center",
        "end": "items-end",
        "stretch": "items-stretch",
    }
    
    justify_map = {
        "start": "justify-start",
        "center": "justify-center",
        "end": "justify-end",
        "between": "justify-between",
        "around": "justify-around",
    }
    
    base = "w-full"
    wrap_class = "flex-wrap" if wrap else ""
    
    return f"{base} {align_map.get(align, '')} {justify_map.get(justify, '')} gap-{gap} {wrap_class}".strip()


# =============================================================================
# TABLE SLOT TEMPLATES
# =============================================================================

class TableSlots:
    """Reusable table slot templates for consistent styling."""
    
    @staticmethod
    def item_name_slot() -> str:
        """Slot for bold item name column."""
        return '''
            <q-td :props="props" class="text-weight-bold" style="font-size: 1.05rem;">
                {{ props.row.item_name }}
            </q-td>
        '''
    
    @staticmethod
    def item_name_with_icon_slot(size: int = 80) -> str:
        """Slot for item name with sprite icon.
        
        Requires rows to have 'item_id' and 'item_name' fields.
        The icon style is computed dynamically based on item_id.
        Falls back to text-only if no icon style is available.
        
        Args:
            size: Icon display size in pixels (default 80)
        """
        return f'''
            <q-td :props="props" class="item-cell-with-icon">
                <div v-if="props.row.icon_style" class="item-icon" :style="props.row.icon_style"></div>
                <span class="item-name">{{{{ props.row.item_name }}}}</span>
            </q-td>
        '''
    
    @staticmethod
    def hq_value_slot(field: str, formatted_field: Optional[str] = None) -> str:
        """Slot for HQ-styled value with zero-value handling.
        
        Args:
            field: Raw value field name for comparison
            formatted_field: Formatted value field name (defaults to field + '_fmt')
        """
        fmt = formatted_field or f"{field}_fmt"
        return f'''
            <q-td :props="props" :class="props.row.{field} == 0 ? 'text-grey-5' : 'hq-accent font-semibold'">
                <q-icon v-if="props.row.{field} == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                    <q-tooltip>No HQ data</q-tooltip>
                </q-icon>
                {{{{ props.row.{fmt} }}}}
            </q-td>
        '''
    
    @staticmethod
    def nq_value_slot(field: str, formatted_field: Optional[str] = None) -> str:
        """Slot for NQ-styled value with zero-value handling."""
        fmt = formatted_field or f"{field}_fmt"
        return f'''
            <q-td :props="props" :class="props.row.{field} == 0 ? 'text-grey-5' : 'nq-accent font-semibold'">
                <q-icon v-if="props.row.{field} == 0" name="warning" class="text-amber-6 q-mr-xs" size="xs">
                    <q-tooltip>No NQ data</q-tooltip>
                </q-icon>
                {{{{ props.row.{fmt} }}}}
            </q-td>
        '''
    
    @staticmethod
    def metric_slot(field: str, metric_class: str = "metric-highlight") -> str:
        """Slot for metric value with custom styling."""
        return f'''
            <q-td :props="props" class="{metric_class} text-weight-bold">
                {{{{ props.row.{field} }}}}
            </q-td>
        '''
    
    @staticmethod
    def price_slot(field: str, formatted_field: Optional[str] = None) -> str:
        """Slot for price value with no-listing handling."""
        fmt = formatted_field or f"{field}_fmt"
        return f'''
            <q-td :props="props" :class="props.row.{field} == 0 ? 'text-grey-5' : 'metric-price text-weight-bold'">
                <q-icon v-if="props.row.{field} == 0" name="remove_shopping_cart" class="text-grey-5 q-mr-xs" size="xs">
                    <q-tooltip>No listings available</q-tooltip>
                </q-icon>
                {{{{ props.row.{fmt} }}}}
            </q-td>
        '''
    
    @staticmethod
    def header_tooltip_slot(field: str, label: str, tooltip: str) -> str:
        """Slot for header with tooltip."""
        return f'''
            <q-th :props="props">
                <span>{label}</span>
                <q-tooltip class="bg-grey-8 text-body2">{tooltip}</q-tooltip>
            </q-th>
        '''


TABLE_SLOTS = TableSlots()
