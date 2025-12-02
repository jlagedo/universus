"""
Formatting utilities for GUI display.
"""

from datetime import datetime
from typing import Optional


def format_gil(amount: Optional[float]) -> str:
    """Format gil amount using locale-style separators (e.g. 1.234.567)."""
    if amount is None:
        return "N/A"
    try:
        amt = int(round(float(amount)))
    except (TypeError, ValueError):
        return "N/A"
    # Use US formatting then swap to PT-BR style: thousands '.'
    s = f"{amt:,}"  # e.g. 1,234,567
    return s.replace(',', '.')


def format_velocity(velocity: Optional[float]) -> str:
    """Format sales velocity with decimal comma (e.g. 12,34)."""
    if velocity is None:
        return "N/A"
    try:
        v = float(velocity)
    except (TypeError, ValueError):
        return "N/A"
    s = f"{v:,.2f}"  # e.g. 1,234.56
    # Swap separators: temporary marker for commas
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return s


def format_time_ago(timestamp_str: str) -> str:
    """Format a timestamp as relative time."""
    if not timestamp_str:
        return "Never"
    try:
        last_updated = datetime.fromisoformat(timestamp_str)
        time_ago = datetime.now() - last_updated
        if time_ago.days > 0:
            return f"{time_ago.days}d ago"
        elif time_ago.seconds > 3600:
            return f"{time_ago.seconds // 3600}h ago"
        else:
            return f"{time_ago.seconds // 60}m ago"
    except (ValueError, TypeError):
        return "Unknown"
