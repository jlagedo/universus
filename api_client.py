"""
API client for interacting with the Universalis API.
"""

import time
import logging
import re
import asyncio
from typing import Optional, Dict, Any, List
import requests

from config import get_config
from executor import executor

logger = logging.getLogger(__name__)

# Load configuration
config = get_config()

# Valid world name pattern (alphanumeric, allows spaces for multi-word names)
WORLD_NAME_PATTERN = re.compile(r'^[A-Za-z][A-Za-z0-9\s-]{1,30}$')

# API client version - imported from main module to keep in sync
try:
    from universus import __version__ as API_VERSION
except ImportError:
    API_VERSION = "1.0.0"  # Fallback for tests/standalone use


def validate_world_name(world: str) -> str:
    """Validate and return a world name.
    
    Args:
        world: World name to validate
        
    Returns:
        The validated world name
        
    Raises:
        ValueError: If world name is invalid
    """
    if not world or not WORLD_NAME_PATTERN.match(world):
        raise ValueError(f"Invalid world name: '{world}'. World names must be alphanumeric.")
    return world


class RateLimiter:
    """Token bucket rate limiter to respect API limits.
    
    Universalis API limits: 25 req/s sustained, 50 req/s burst.
    We use 20 req/s (80% of limit) for safety margin.
    """
    
    def __init__(self, requests_per_second: float = None, burst_size: int = None):
        """Initialize token bucket rate limiter.
        
        Args:
            requests_per_second: Sustained rate limit (default 20 req/s)
            burst_size: Maximum burst capacity (default 40 tokens)
        """
        if requests_per_second is None:
            requests_per_second = config.get('api', 'rate_limit', 20.0)
        if burst_size is None:
            burst_size = config.get('api', 'burst_size', 40)
        
        self.rate = requests_per_second
        self.burst_size = burst_size
        self.tokens = float(burst_size)  # Start with full bucket
        self.last_refill_time = time.time()
        
        logger.debug(f"Rate limiter initialized: {requests_per_second} req/sec, burst: {burst_size}")
    
    def wait(self):
        """Wait if necessary to respect rate limit using token bucket algorithm."""
        # Refill tokens based on time elapsed
        current_time = time.time()
        time_elapsed = current_time - self.last_refill_time
        self.tokens = min(self.burst_size, self.tokens + time_elapsed * self.rate)
        self.last_refill_time = current_time
        
        # If no tokens available, wait for one token to be generated
        if self.tokens < 1.0:
            sleep_time = (1.0 - self.tokens) / self.rate
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s (tokens: {self.tokens:.2f})")
            time.sleep(sleep_time)
            self.tokens = 1.0
            self.last_refill_time = time.time()
        
        # Consume one token
        self.tokens -= 1.0


class UniversalisAPI:
    """Client for interacting with the Universalis API."""
    
    def __init__(self, timeout: int = None, rate_limiter: Optional[RateLimiter] = None):
        if timeout is None:
            timeout = config.get('api', 'timeout', 10)
        self.base_url = config.get('api', 'base_url', 'https://universalis.app/api')
        self.timeout = timeout
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": f"Universus-CLI/{API_VERSION}"
        })
        logger.info(f"Universalis API client initialized (timeout: {timeout}s)")
    
    def close(self):
        """Close the session."""
        if self.session:
            logger.debug("Closing API session")
            self.session.close()
            logger.debug("API session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False
    
    def _make_request(self, url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
        """Make a rate-limited request to the API with retry logic.
        
        Args:
            url: API endpoint URL
            params: Optional query parameters
            max_retries: Maximum number of retry attempts for transient errors
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If request fails after all retries
        """
        logger.debug(f"Making API request: {url}" + (f" with params: {params}" if params else ""))
        
        last_exception = None
        for attempt in range(max_retries):
            self.rate_limiter.wait()
            try:
                response = self.session.get(url, params=params, timeout=self.timeout)
                logger.debug(f"Response status: {response.status_code}")
                response.raise_for_status()
                data = response.json()
                logger.debug(f"Response received: {len(str(data))} bytes")
                return data
            except (requests.Timeout, requests.ConnectionError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"API request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    # Recreate session on connection errors
                    try:
                        self.session.close()
                    except Exception as close_error:
                        logger.debug(f"Error closing session: {close_error}")
                    self.session = requests.Session()
                    self.session.headers.update({
                        "User-Agent": f"Universus-CLI/{API_VERSION}"
                    })
                    time.sleep(wait_time)
                else:
                    logger.error(f"API request failed after {max_retries} attempts: {url} - {e}")
            except requests.RequestException as e:
                logger.error(f"API request failed: {url} - {e}")
                raise
        
        raise last_exception
    
    async def _make_request_async(self, url: str, params: Optional[Dict[str, Any]] = None, max_retries: int = 3) -> Dict[str, Any]:
        """Make a rate-limited async request to the API with retry logic.
        
        Non-blocking version that runs _make_request in a thread pool.
        
        Args:
            url: API endpoint URL
            params: Optional query parameters
            max_retries: Maximum number of retry attempts for transient errors
            
        Returns:
            JSON response data
            
        Raises:
            requests.RequestException: If request fails after all retries
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            executor,
            self._make_request,
            url,
            params,
            max_retries
        )
    
    def get_datacenters(self) -> list:
        """Fetch all available datacenters from the API."""
        logger.info("Fetching datacenters list")
        result = self._make_request(f"{self.base_url}/data-centers")
        logger.info(f"Retrieved {len(result)} datacenters")
        return result
    
    async def get_datacenters_async(self) -> list:
        """Async version: Fetch all available datacenters from the API."""
        logger.info("Fetching datacenters list (async)")
        result = await self._make_request_async(f"{self.base_url}/data-centers")
        logger.info(f"Retrieved {len(result)} datacenters")
        return result
    
    def get_worlds(self) -> List[Dict[str, Any]]:
        """Fetch all available worlds from the API.
        
        Returns:
            List of world dictionaries with 'id' and 'name' keys
        """
        logger.info("Fetching worlds list")
        result = self._make_request(f"{self.base_url}/v2/worlds")
        logger.info(f"Retrieved {len(result)} worlds")
        return result
    
    async def get_worlds_async(self) -> List[Dict[str, Any]]:
        """Async version: Fetch all available worlds from the API.
        
        Returns:
            List of world dictionaries with 'id' and 'name' keys
        """
        logger.info("Fetching worlds list (async)")
        result = await self._make_request_async(f"{self.base_url}/v2/worlds")
        logger.info(f"Retrieved {len(result)} worlds")
        return result
    
    def get_most_recently_updated(self, world: str, entries: int = None) -> Dict[str, Any]:
        """Fetch most recently updated items for a world."""
        validate_world_name(world)
        if entries is None:
            entries = config.get('api', 'max_items_per_query', 200)
        max_items = config.get('api', 'max_items_per_query', 200)
        logger.info(f"Fetching most recently updated items for {world} (limit: {entries})")
        result = self._make_request(
            f"{self.base_url}/extra/stats/most-recently-updated",
            params={"world": world, "entries": min(entries, max_items)}
        )
        logger.info(f"Retrieved {len(result.get('items', []))} items")
        return result
    
    async def get_most_recently_updated_async(self, world: str, entries: int = None) -> Dict[str, Any]:
        """Async version: Fetch most recently updated items for a world."""
        validate_world_name(world)
        if entries is None:
            entries = config.get('api', 'max_items_per_query', 200)
        max_items = config.get('api', 'max_items_per_query', 200)
        logger.info(f"Fetching most recently updated items for {world} (async, limit: {entries})")
        result = await self._make_request_async(
            f"{self.base_url}/extra/stats/most-recently-updated",
            params={"world": world, "entries": min(entries, max_items)}
        )
        logger.info(f"Retrieved {len(result.get('items', []))} items")
        return result
    
    def get_market_data(self, world: str, item_id: int) -> Dict[str, Any]:
        """Fetch current market data for an item on a world."""
        validate_world_name(world)
        logger.debug(f"Fetching market data for item {item_id} on {world}")
        return self._make_request(f"{self.base_url}/{world}/{item_id}")
    
    async def get_market_data_async(self, world: str, item_id: int) -> Dict[str, Any]:
        """Async version: Fetch current market data for an item on a world."""
        validate_world_name(world)
        logger.debug(f"Fetching market data for item {item_id} on {world} (async)")
        return await self._make_request_async(f"{self.base_url}/{world}/{item_id}")
    
    def get_history(self, world: str, item_id: int, entries: int = None) -> Dict[str, Any]:
        """Fetch sales history for an item on a world."""
        validate_world_name(world)
        if entries is None:
            entries = config.get('api', 'default_history_entries', 100)
        logger.debug(f"Fetching history for item {item_id} on {world} (limit: {entries})")
        return self._make_request(
            f"{self.base_url}/history/{world}/{item_id}",
            params={"entries": entries}
        )
    
    async def get_history_async(self, world: str, item_id: int, entries: int = None) -> Dict[str, Any]:
        """Async version: Fetch sales history for an item on a world."""
        validate_world_name(world)
        if entries is None:
            entries = config.get('api', 'default_history_entries', 100)
        logger.debug(f"Fetching history for item {item_id} on {world} (async, limit: {entries})")
        return await self._make_request_async(
            f"{self.base_url}/history/{world}/{item_id}",
            params={"entries": entries}
        )

    def get_aggregated_prices(self, scope: str, item_ids: List[int]) -> Dict[str, Any]:
        """Fetch aggregated prices for multiple items within a scope.
        
        Args:
            scope: World/DC/Region name as required by Universalis (e.g., world name like 'Behemoth')
            item_ids: List of item IDs (up to 100)
        Returns:
            JSON dict with 'results' array for each itemId
        """
        logger.info(f"Fetching aggregated prices for {len(item_ids)} items on {scope}")
        ids_str = ",".join(str(i) for i in item_ids)
        url = f"{self.base_url}/v2/aggregated/{scope}/{ids_str}"
        return self._make_request(url)

    async def get_aggregated_prices_async(self, scope: str, item_ids: List[int]) -> Dict[str, Any]:
        """Async version: Fetch aggregated prices for multiple items within a scope."""
        ids_str = ",".join(str(i) for i in item_ids)
        url = f"{self.base_url}/v2/aggregated/{scope}/{ids_str}"
        return await self._make_request_async(url)
    
    def fetch_teamcraft_items(self) -> Dict[str, Dict]:
        """Fetch item names from FFXIV Teamcraft data dump.
        
        Returns:
            Dictionary mapping item_id (string) to item data with 'en' field
        """
        logger.info("Fetching items from FFXIV Teamcraft")
        url = config.get('teamcraft', 'items_url', 'https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json')
        timeout = config.get('teamcraft', 'timeout', 30)
        max_retries = config.get('teamcraft', 'max_retries', 3)
        
        # Retry with exponential backoff for external API
        last_exception = None
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                logger.info(f"Retrieved {len(data)} items from Teamcraft")
                return data
            except (requests.RequestException, ValueError) as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Teamcraft request failed (attempt {attempt + 1}/{max_retries}): {e}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Teamcraft request failed after {max_retries} attempts: {e}")
        
        raise last_exception
    
    async def fetch_teamcraft_items_async(self) -> Dict[str, Dict]:
        """Async version: Fetch item names from FFXIV Teamcraft data dump.
        
        Returns:
            Dictionary mapping item_id (string) to item data with 'en' field
        """
        logger.info("Fetching items from FFXIV Teamcraft (async)")
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, self.fetch_teamcraft_items)
    
    def get_marketable_items(self) -> List[int]:
        """Fetch all marketable item IDs from the Universalis API.
        
        Returns:
            List of marketable item IDs
        """
        logger.info("Fetching marketable items from Universalis API")
        result = self._make_request(f"{self.base_url}/v2/marketable")
        logger.info(f"Retrieved {len(result)} marketable items")
        return result
    
    async def get_marketable_items_async(self) -> List[int]:
        """Async version: Fetch all marketable item IDs from the Universalis API.
        
        Returns:
            List of marketable item IDs
        """
        logger.info("Fetching marketable items from Universalis API (async)")
        result = await self._make_request_async(f"{self.base_url}/v2/marketable")
        logger.info(f"Retrieved {len(result)} marketable items")
        return result
