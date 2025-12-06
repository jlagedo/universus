"""
GUI utilities package.
"""

from .formatters import format_gil, format_velocity, format_time_ago
from .theme import ThemeManager
from .icons import GameIcons, SpriteIcon
from .design_system import (
    COLORS, TYPOGRAPHY, SPACING, STYLES, PROPS, TABLE_SLOTS,
    card_classes, text_classes, heading_classes, metric_classes, row_classes
)

__all__ = [
    # Formatters
    'format_gil', 
    'format_velocity', 
    'format_time_ago',
    # Theme
    'ThemeManager',
    # Icons
    'GameIcons',
    'SpriteIcon',
    # Design System
    'COLORS',
    'TYPOGRAPHY', 
    'SPACING',
    'STYLES',
    'PROPS',
    'TABLE_SLOTS',
    'card_classes',
    'text_classes',
    'heading_classes',
    'metric_classes',
    'row_classes',
]
