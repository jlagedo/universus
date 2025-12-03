"""
Views package initialization.
"""

from . import dashboard
from . import datacenters
from . import top_items
from . import reports
from . import settings

__all__ = [
    'dashboard',
    'datacenters',
    'top_items',
    'reports',
    'settings'
]
