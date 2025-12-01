"""
API client for interacting with the Universalis API.
"""

import time
import logging
from typing import Optional, Dict, Any
import requests

from config import get_config

logger = logging.getLogger(__name__)

# Load configuration
config = get_config()


class RateLimiter:
    """Rate limiter to respect API limits."""
    
    def __init__(self, requests_per_second: float = None):
        """Initialize rate limiter.
        
        Conservative limit of 2 requests/second based on API implementation
        showing 100ms delays between requests.
        """
        if requests_per_second is None:
            requests_per_second = config.get('api', 'rate_limit', 2.0)
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        logger.debug(f"Rate limiter initialized: {requests_per_second} req/sec (interval: {self.min_interval:.3f}s)")
    
    def wait(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        if time_since_last_request < self.min_interval:
            sleep_time = self.min_interval - time_since_last_request
            logger.debug(f"Rate limiting: sleeping for {sleep_time:.3f}s")
            time.sleep(sleep_time)
        self.last_request_time = time.time()


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
            "User-Agent": "Universus-CLI/1.0"
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
    
    def _make_request(self, url: str, params: Optional[Dict] = None) -> Any:
        """Make a rate-limited request to the API."""
        logger.debug(f"Making API request: {url}" + (f" with params: {params}" if params else ""))
        self.rate_limiter.wait()
        try:
            response = self.session.get(url, params=params, timeout=self.timeout)
            logger.debug(f"Response status: {response.status_code}")
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Response received: {len(str(data))} bytes")
            return data
        except requests.RequestException as e:
            logger.error(f"API request failed: {url} - {e}")
            raise
    
    def get_datacenters(self) -> list:
        """Fetch all available datacenters from the API."""
        logger.info("Fetching datacenters list")
        result = self._make_request(f"{self.base_url}/data-centers")
        logger.info(f"Retrieved {len(result)} datacenters")
        return result
    
    def get_most_recently_updated(self, world: str, entries: int = None) -> Dict:
        """Fetch most recently updated items for a world."""
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
    
    def get_market_data(self, world: str, item_id: int) -> Dict:
        """Fetch current market data for an item on a world."""
        logger.debug(f"Fetching market data for item {item_id} on {world}")
        return self._make_request(f"{self.base_url}/{world}/{item_id}")
    
    def get_history(self, world: str, item_id: int, entries: int = None) -> Dict:
        """Fetch sales history for an item on a world."""
        if entries is None:
            entries = config.get('api', 'default_history_entries', 100)
        logger.debug(f"Fetching history for item {item_id} on {world} (limit: {entries})")
        return self._make_request(
            f"{self.base_url}/history/{world}/{item_id}",
            params={"entries": entries}
        )
    
    def fetch_teamcraft_items(self) -> Dict[str, Dict]:
        """Fetch item names from FFXIV Teamcraft data dump.
        
        Returns:
            Dictionary mapping item_id (string) to item data with 'en' field
        """
        logger.info("Fetching items from FFXIV Teamcraft")
        url = config.get('teamcraft', 'items_url', 'https://raw.githubusercontent.com/ffxiv-teamcraft/ffxiv-teamcraft/master/libs/data/src/lib/json/items.json')
        timeout = config.get('teamcraft', 'timeout', 30)
        
        # Don't apply rate limiting for external API
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Retrieved {len(data)} items from Teamcraft")
        return data
