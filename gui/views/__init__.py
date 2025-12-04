"""
Views package initialization.
"""

from . import dashboard
from . import datacenters
from . import top_items
from . import reports
from . import settings
from . import market_analysis

__all__ = [
    'dashboard',
    'datacenters',
    'top_items',
    'reports',
    'settings',
    'market_analysis'
]
