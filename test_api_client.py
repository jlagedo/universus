"""
Unit tests for the API client layer.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from api_client import RateLimiter, UniversalisAPI, DEFAULT_RATE_LIMIT
import requests


class TestRateLimiter:
    """Test suite for RateLimiter class."""
    
    def test_initialization(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_second=5.0)
        assert limiter.min_interval == 0.2  # 1/5
        assert limiter.last_request_time == 0.0
    
    def test_default_rate_limit(self):
        """Test default rate limit is applied."""
        limiter = RateLimiter()
        assert limiter.min_interval == 0.5  # 1/2
    
    def test_first_request_no_wait(self):
        """Test that first request doesn't wait."""
        limiter = RateLimiter(requests_per_second=10.0)
        start_time = time.time()
        limiter.wait()
        elapsed = time.time() - start_time
        assert elapsed < 0.01  # Should be nearly instant
    
    def test_rate_limiting_enforced(self):
        """Test that rate limiting actually delays requests."""
        limiter = RateLimiter(requests_per_second=10.0)  # 0.1s between requests
        
        limiter.wait()  # First request
        start_time = time.time()
        limiter.wait()  # Second request should wait
        elapsed = time.time() - start_time
        
        assert elapsed >= 0.09  # Should wait ~0.1s
        assert elapsed < 0.15   # But not too long
    
    def test_multiple_requests_rate_limited(self):
        """Test multiple requests are properly rate limited."""
        limiter = RateLimiter(requests_per_second=20.0)  # 0.05s between requests
        
        start_time = time.time()
        for _ in range(3):
            limiter.wait()
        elapsed = time.time() - start_time
        
        # Should take at least 0.1s (2 intervals for 3 requests)
        assert elapsed >= 0.09


class TestUniversalisAPI:
    """Test suite for UniversalisAPI class."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock requests session."""
        with patch('api_client.requests.Session') as mock:
            session = Mock()
            mock.return_value = session
            yield session
    
    @pytest.fixture
    def api(self, mock_session):
        """Create API client with mocked session."""
        return UniversalisAPI(timeout=5)
    
    def test_initialization(self, api):
        """Test API client initialization."""
        assert api.timeout == 5
        assert api.rate_limiter is not None
        assert api.session is not None
    
    def test_user_agent_header(self, mock_session):
        """Test that User-Agent header is set."""
        api = UniversalisAPI()
        mock_session.headers.update.assert_called_once()
        call_args = mock_session.headers.update.call_args[0][0]
        assert 'User-Agent' in call_args
        assert call_args['User-Agent'] == "Universus-CLI/1.0"
    
    def test_context_manager(self, mock_session):
        """Test API client as context manager."""
        with UniversalisAPI() as api:
            assert api.session is not None
        
        mock_session.close.assert_called_once()
    
    def test_close(self, api, mock_session):
        """Test closing API client."""
        api.close()
        mock_session.close.assert_called_once()
    
    def test_make_request_success(self, api, mock_session):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_session.get.return_value = mock_response
        
        result = api._make_request("https://test.com/api")
        
        assert result == {'data': 'test'}
        mock_session.get.assert_called_once()
        mock_response.raise_for_status.assert_called_once()
    
    def test_make_request_with_params(self, api, mock_session):
        """Test API request with parameters."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_session.get.return_value = mock_response
        
        params = {'world': 'Behemoth', 'entries': 100}
        api._make_request("https://test.com/api", params=params)
        
        call_args = mock_session.get.call_args
        assert call_args[1]['params'] == params
    
    def test_make_request_http_error(self, api, mock_session):
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_session.get.return_value = mock_response
        
        with pytest.raises(requests.HTTPError):
            api._make_request("https://test.com/api")
    
    def test_make_request_timeout(self, api, mock_session):
        """Test handling of timeout errors."""
        mock_session.get.side_effect = requests.Timeout("Request timeout")
        
        with pytest.raises(requests.Timeout):
            api._make_request("https://test.com/api")
    
    def test_make_request_connection_error(self, api, mock_session):
        """Test handling of connection errors."""
        mock_session.get.side_effect = requests.ConnectionError("Connection failed")
        
        with pytest.raises(requests.ConnectionError):
            api._make_request("https://test.com/api")
    
    def test_get_datacenters(self, api, mock_session):
        """Test fetching datacenters."""
        expected_data = [
            {'name': 'Crystal', 'region': 'NA', 'worlds': ['Behemoth']},
            {'name': 'Light', 'region': 'EU', 'worlds': ['Lich']}
        ]
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_session.get.return_value = mock_response
        
        result = api.get_datacenters()
        
        assert result == expected_data
        assert 'data-centers' in mock_session.get.call_args[0][0]
    
    def test_get_most_recently_updated(self, api, mock_session):
        """Test fetching most recently updated items."""
        expected_data = {
            'items': [
                {'itemID': 12345, 'worldName': 'Behemoth'},
                {'itemID': 67890, 'worldName': 'Behemoth'}
            ]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_session.get.return_value = mock_response
        
        result = api.get_most_recently_updated('Behemoth', entries=100)
        
        assert result == expected_data
        assert len(result['items']) == 2
        
        # Check params were passed
        call_args = mock_session.get.call_args
        assert call_args[1]['params']['world'] == 'Behemoth'
        assert call_args[1]['params']['entries'] == 100
    
    def test_get_most_recently_updated_limit(self, api, mock_session):
        """Test that entries are limited to MAX_ITEMS_PER_QUERY."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'items': []}
        mock_session.get.return_value = mock_response
        
        api.get_most_recently_updated('Behemoth', entries=500)
        
        call_args = mock_session.get.call_args
        assert call_args[1]['params']['entries'] == 200  # MAX_ITEMS_PER_QUERY
    
    def test_get_market_data(self, api, mock_session):
        """Test fetching market data for an item."""
        expected_data = {
            'itemID': 12345,
            'averagePrice': 1000.5,
            'regularSaleVelocity': 5.5,
            'listings': []
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_session.get.return_value = mock_response
        
        result = api.get_market_data('Behemoth', 12345)
        
        assert result == expected_data
        url = mock_session.get.call_args[0][0]
        assert 'Behemoth' in url
        assert '12345' in url
    
    def test_get_history(self, api, mock_session):
        """Test fetching sales history."""
        expected_data = {
            'itemID': 12345,
            'entries': [
                {'timestamp': 1234567890, 'pricePerUnit': 1000},
                {'timestamp': 1234567900, 'pricePerUnit': 1100}
            ]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = expected_data
        mock_session.get.return_value = mock_response
        
        result = api.get_history('Behemoth', 12345, entries=50)
        
        assert result == expected_data
        assert len(result['entries']) == 2
        
        # Check URL and params
        call_args = mock_session.get.call_args
        url = call_args[0][0]
        assert 'history' in url
        assert 'Behemoth' in url
        assert '12345' in url
        assert call_args[1]['params']['entries'] == 50
    
    def test_rate_limiting_integration(self, api, mock_session):
        """Test that rate limiter is used in requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_session.get.return_value = mock_response
        
        start_time = time.time()
        api._make_request("https://test.com/api1")
        api._make_request("https://test.com/api2")
        elapsed = time.time() - start_time
        
        # Should take at least 0.5s due to rate limiting (2 req/sec)
        assert elapsed >= 0.49
