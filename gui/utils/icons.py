"""
Gaming icon theme for Universus GUI.

Uses Material Icons (built into NiceGUI/Quasar) with gaming-appropriate choices.
Reference: https://fonts.google.com/icons?icon.set=Material+Icons
         
Icon prefixes supported:
- None: filled icons (default)
- "o_": outlined icons
- "r_": rounded icons  
- "s_": sharp icons
- "sym_o_": outlined symbols
- "sym_r_": rounded symbols

Also includes SpriteIcon class for FFXIV item icons using spritesheets.
"""

import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SpriteIcon:
    """Utility for rendering FFXIV item icons from spritesheets.
    
    Icons are stored as 80x80 pixels in 4096x4096 spritesheet images.
    The sprite_index.json maps item_id to sheet number and coordinates.
    
    Usage:
        # Get inline style for an item icon
        style = SpriteIcon.get_icon_style(5594)
        
        # Get complete HTML for an item icon  
        html = SpriteIcon.get_icon_html(5594)
    """
    
    _index: Optional[dict] = None
    _loaded: bool = False
    
    # Spritesheet constants
    ICON_SIZE = 80  # Original icon size in pixels
    SHEET_SIZE = 4096  # Spritesheet dimension
    NUM_SHEETS = 7  # spritesheet_0.png through spritesheet_6.png
    
    @classmethod
    def _load_index(cls) -> None:
        """Load the sprite index from JSON file (lazy loading)."""
        if cls._loaded:
            return
            
        cls._loaded = True
        index_path = Path(__file__).parent.parent.parent / 'static' / 'sprite_index.json'
        
        try:
            with open(index_path, 'r') as f:
                cls._index = json.load(f)
            logger.info(f"Loaded sprite index with {len(cls._index)} items")
        except FileNotFoundError:
            logger.warning(f"Sprite index not found at {index_path}")
            cls._index = {}
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse sprite index: {e}")
            cls._index = {}
    
    @classmethod
    def get_icon_data(cls, item_id: int) -> Optional[dict]:
        """Get sprite data for an item.
        
        Args:
            item_id: FFXIV item ID
            
        Returns:
            Dict with 'sheet', 'x', 'y', 'w', 'h' or None if not found
        """
        cls._load_index()
        return cls._index.get(str(item_id))
    
    @classmethod
    def get_icon_style(cls, item_id: int, size: int = 80) -> Optional[str]:
        """Get inline CSS style for displaying an item icon.
        
        Args:
            item_id: FFXIV item ID
            size: Display size in pixels (default 80, same as source)
            
        Returns:
            CSS style string or None if item not in index
        """
        data = cls.get_icon_data(item_id)
        if not data:
            return None
        
        sheet = data['sheet']
        x = data['x']
        y = data['y']
        
        # Scale factor for display size
        scale = size / cls.ICON_SIZE
        
        # Calculate scaled background position and size
        bg_x = -x * scale
        bg_y = -y * scale
        bg_size = cls.SHEET_SIZE * scale
        
        return (
            f"width: {size}px; "
            f"height: {size}px; "
            f"display: inline-block; "
            f"background-image: url('/static/spritesheet_{sheet}.png'); "
            f"background-position: {bg_x}px {bg_y}px; "
            f"background-size: {bg_size}px {bg_size}px; "
            f"background-repeat: no-repeat; "
            f"vertical-align: middle; "
            f"flex-shrink: 0;"
        )
    
    @classmethod
    def get_icon_html(cls, item_id: int, size: int = 80, extra_class: str = '') -> str:
        """Get complete HTML for displaying an item icon.
        
        Args:
            item_id: FFXIV item ID
            size: Display size in pixels (default 80)
            extra_class: Additional CSS classes to apply
            
        Returns:
            HTML string with icon div, or empty string if not found
        """
        style = cls.get_icon_style(item_id, size)
        if not style:
            return ''
        
        classes = f'item-icon {extra_class}'.strip()
        return f'<div class="{classes}" style="{style}"></div>'
    
    @classmethod
    def has_icon(cls, item_id: int) -> bool:
        """Check if an item has an icon in the sprite index.
        
        Args:
            item_id: FFXIV item ID
            
        Returns:
            True if icon exists, False otherwise
        """
        return cls.get_icon_data(item_id) is not None


class GameIcons:
    """Centralized gaming icon definitions using Material Icons."""
    
    # ===================
    # Navigation Icons
    # ===================
    HOME = "home"
    DASHBOARD = "dashboard"
    MENU = "menu"
    SETTINGS = "settings"
    
    # ===================
    # Market/Trading Icons
    # ===================
    MARKET = "store"
    TRENDING = "trending_up"
    CHART_BAR = "bar_chart"
    CHART_PIE = "pie_chart"
    ANALYTICS = "analytics"
    INSIGHTS = "insights"
    PRICE = "sell"
    
    # ===================
    # Data/Server Icons
    # ===================
    SERVER = "dns"
    DATABASE = "storage"
    WORLD = "public"
    DATACENTER = "lan"
    CLOUD_SYNC = "cloud_sync"
    CLOUD_DOWNLOAD = "cloud_download"
    
    # ===================
    # Tracking Icons
    # ===================
    TRACK = "track_changes"
    VISIBILITY = "visibility"
    WATCH = "preview"
    TARGET = "gps_fixed"
    
    # ===================
    # Action Icons
    # ===================
    ADD = "add_circle"
    REMOVE = "remove_circle"
    DELETE = "delete"
    EDIT = "edit"
    SAVE = "save"
    CANCEL = "cancel"
    CONFIRM = "check_circle"
    REFRESH = "refresh"
    SYNC = "sync"
    SEARCH = "search"
    FILTER = "filter_list"
    SORT = "sort"
    PLAY = "play_circle"
    PAUSE = "pause_circle"
    STOP = "stop_circle"
    
    # ===================
    # Game/RPG Icons
    # ===================
    SWORD = "sports_kabaddi"  # Combat/fighting
    SHIELD = "shield"
    POTION = "science"  # Flask/potion
    TREASURE = "inventory_2"  # Chest/inventory
    GOLD = "paid"  # Currency
    CRYSTAL = "diamond"
    SCROLL = "description"
    BOOK = "menu_book"
    
    # ===================
    # Item Icons
    # ===================
    ITEM = "inventory"
    ITEM_RARE = "star"
    INVENTORY = "backpack"
    CRAFTING = "construction"
    GEAR = "handyman"
    
    # ===================
    # Status/Notification Icons
    # ===================
    NOTIFICATION = "notifications"
    NOTIFICATION_NEW = "notification_important"
    ALERT = "error"
    INFO = "info"
    SUCCESS = "check_circle"
    WARNING = "warning"
    ERROR = "cancel"
    
    # ===================
    # UI Control Icons
    # ===================
    EXPAND = "expand_more"
    COLLAPSE = "expand_less"
    NEXT = "chevron_right"
    PREVIOUS = "chevron_left"
    FULLSCREEN = "fullscreen"
    
    # ===================
    # Theme Icons
    # ===================
    THEME_LIGHT = "light_mode"
    THEME_DARK = "dark_mode"
    
    # ===================
    # Misc Icons
    # ===================
    CLOCK = "schedule"
    CALENDAR = "calendar_today"
    HISTORY = "history"
    HELP = "help"
    ABOUT = "info_outline"
    VERSION = "tag"
