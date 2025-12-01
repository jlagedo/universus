"""
API client for interacting with the Universalis API.
"""

import time
import logging
from typing import Optional, Dict, Any
import requests

logger = logging.getLogger(__name__)


# Constants
MAX_ITEMS_PER_QUERY = 200
DEFAULT_HISTORY_ENTRIES = 100
DEFAULT_TIMEOUT = 10
DEFAULT_RATE_LIMIT = 2.0  # requests per second


class RateLimiter:
    """Rate limiter to respect API limits."""
    
    def __init__(self, requests_per_second: float = DEFAULT_RATE_LIMIT):
        """Initialize rate limiter.
        
        Conservative limit of 2 requests/second based on API implementation
        showing 100ms delays between requests.
        """
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
    
    BASE_URL = "https://universalis.app/api"
    
    def __init__(self, timeout: int = DEFAULT_TIMEOUT, rate_limiter: Optional[RateLimiter] = None):
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
        result = self._make_request(f"{self.BASE_URL}/data-centers")
        logger.info(f"Retrieved {len(result)} datacenters")
        return result
    
    def get_most_recently_updated(self, world: str, entries: int = MAX_ITEMS_PER_QUERY) -> Dict:
        """Fetch most recently updated items for a world."""
        logger.info(f"Fetching most recently updated items for {world} (limit: {entries})")
        result = self._make_request(
            f"{self.BASE_URL}/extra/stats/most-recently-updated",
            params={"world": world, "entries": min(entries, MAX_ITEMS_PER_QUERY)}
        )
        logger.info(f"Retrieved {len(result.get('items', []))} items")
        return result
    
    def get_market_data(self, world: str, item_id: int) -> Dict:
        """Fetch current market data for an item on a world."""
        logger.debug(f"Fetching market data for item {item_id} on {world}")
        return self._make_request(f"{self.BASE_URL}/{world}/{item_id}")
    
    def get_history(self, world: str, item_id: int, entries: int = DEFAULT_HISTORY_ENTRIES) -> Dict:
        """Fetch sales history for an item on a world."""
        logger.debug(f"Fetching history for item {item_id} on {world} (limit: {entries})")
        return self._make_request(
            f"{self.BASE_URL}/history/{world}/{item_id}",
            params={"entries": entries}
        )
