"""
Shared ThreadPoolExecutor for async operations.

This module provides a single ThreadPoolExecutor instance that is shared
across the application to avoid creating multiple thread pools.
"""

from concurrent.futures import ThreadPoolExecutor
from config import get_config

# Load configuration
config = get_config()

# Number of worker threads (from config or default)
_max_workers = config.get('api', 'executor_workers', 3)

# Shared thread pool executor for async operations
executor = ThreadPoolExecutor(max_workers=_max_workers)


def get_executor() -> ThreadPoolExecutor:
    """Get the shared ThreadPoolExecutor instance.
    
    Returns:
        The shared ThreadPoolExecutor
    """
    return executor


def shutdown_executor(wait: bool = True):
    """Shutdown the shared executor.
    
    Args:
        wait: If True, wait for pending tasks to complete
    """
    executor.shutdown(wait=wait)
