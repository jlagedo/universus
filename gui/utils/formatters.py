"""
Formatting utilities for GUI display.
"""

from datetime import datetime
from typing import Optional


def format_gil(amount: Optional[float]) -> str:
    """Format gil amount with thousands separators (e.g. 1,234,567)."""
    if amount is None:
        return "N/A"
    try:
        amt = int(round(float(amount)))
    except (TypeError, ValueError):
        return "N/A"
    # Use standard comma thousands separator
    return f"{amt:,}"


def format_velocity(velocity: Optional[float]) -> str:
    """Format sales velocity with 2 decimal places (e.g. 12.34)."""
    if velocity is None:
        return "N/A"
    try:
        v = float(velocity)
    except (TypeError, ValueError):
        return "N/A"
    # Use standard comma thousands separator with period for decimals
    return f"{v:,.2f}"
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
