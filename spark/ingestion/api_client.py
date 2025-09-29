"""
Advanced API client with rate limiting, exponential backoff, and retry logic.
"""

import time
import random
import logging
from typing import Dict, Any, Optional, List, Iterator, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from urllib3.util.retry import Retry
import threading
from collections import defaultdict

logger = logging.getLogger(__name__)


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    requests_per_second: float = 5.0
    requests_per_minute: int = 200
    requests_per_hour: int = 10000
    burst_limit: int = 10  # Maximum requests in a burst
    
    def __post_init__(self):
        self.min_interval = 1.0 / self.requests_per_second if self.requests_per_second > 0 else 0


@dataclass
class RetryConfig:
    """Retry configuration with exponential backoff."""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 300.0
    exponential_base: float = 2.0
    jitter: bool = True
    
    # HTTP status codes to retry
    retry_status_codes: List[int] = field(default_factory=lambda: [
        429,  # Too Many Requests
        500,  # Internal Server Error
        502,  # Bad Gateway
        503,  # Service Unavailable
        504,  # Gateway Timeout
        520,  # Unknown Error (Cloudflare)
        521,  # Web Server Is Down (Cloudflare)
        522,  # Connection Timed Out (Cloudflare)
        523,  # Origin Is Unreachable (Cloudflare)
        524,  # A Timeout Occurred (Cloudflare)
    ])
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for the given attempt number."""
        if attempt <= 0:
            return 0
        
        delay = min(
            self.base_delay * (self.exponential_base ** (attempt - 1)),
            self.max_delay
        )
        
        if self.jitter:
            # Add jitter to prevent thundering herd
            delay *= (0.5 + random.random() * 0.5)
        
        return delay


class RateLimiter:
    """Thread-safe rate limiter with multiple time windows."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self._locks = defaultdict(threading.Lock)
        self._request_times = defaultdict(list)
        self._last_request_time = defaultdict(float)
    
    def acquire(self, key: str = 'default') -> float:
        """
        Acquire permission to make a request.
        Returns the time to wait before making the request.
        """
        with self._locks[key]:
            now = time.time()
            request_times = self._request_times[key]
            
            # Clean old request times
            cutoff_minute = now - 60
            cutoff_hour = now - 3600
            
            # Remove requests older than an hour
            request_times[:] = [t for t in request_times if t > cutoff_hour]
            
            # Check hourly limit
            if len(request_times) >= self.config.requests_per_hour:
                oldest_request = min(request_times)
                wait_time = 3600 - (now - oldest_request)
                logger.warning(f"Hourly rate limit reached. Waiting {wait_time:.2f}s")
                return wait_time
            
            # Check minute limit
            minute_requests = [t for t in request_times if t > cutoff_minute]
            if len(minute_requests) >= self.config.requests_per_minute:
                oldest_minute_request = min(minute_requests)
                wait_time = 60 - (now - oldest_minute_request)
                logger.warning(f"Per-minute rate limit reached. Waiting {wait_time:.2f}s")
                return wait_time
            
            # Check requests per second limit
            last_request = self._last_request_time[key]
            if last_request > 0:
                elapsed = now - last_request
                if elapsed < self.config.min_interval:
                    wait_time = self.config.min_interval - elapsed
                    return wait_time
            
            # Record this request
            request_times.append(now)
            self._last_request_time[key] = now
            
            return 0.0
    
    def wait_if_needed(self, key: str = 'default') -> None:
        """Wait if rate limiting is required."""
        wait_time = self.acquire(key)
        if wait_time > 0:
            logger.info(f"Rate limiting: waiting {wait_time:.2f}s")
            time.sleep(wait_time)


class APIClient:
    """
    Advanced API client with rate limiting, retry logic, and exponential backoff.
    """
    
    def __init__(
        self,
        base_url: str,
        rate_limit_config: Optional[RateLimitConfig] = None,
        retry_config: Optional[RetryConfig] = None,
        timeout: int = 30,
        headers: Optional[Dict[str, str]] = None
    ):
        self.base_url = base_url.rstrip('/')
        self.rate_limit_config = rate_limit_config or RateLimitConfig()
        self.retry_config = retry_config or RetryConfig()
        self.timeout = timeout
        
        # Setup session with connection pooling
        self.session = requests.Session()
        
        # Setup retry strategy for connection issues
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set default headers
        default_headers = {
            'User-Agent': 'E-commerce-ETL-Pipeline/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        if headers:
            default_headers.update(headers)
        
        self.session.headers.update(default_headers)
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(self.rate_limit_config)
        
        # Request statistics
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'retried_requests': 0,
            'rate_limited_requests': 0
        }
    
    def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> requests.Response:
        """Make HTTP request with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Apply rate limiting
                self.rate_limiter.wait_if_needed()
                
                # Make the request
                self.stats['total_requests'] += 1
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                # Check if we should retry based on status code
                if response.status_code in self.retry_config.retry_status_codes:
                    raise HTTPError(f"HTTP {response.status_code}: {response.reason}")
                
                # Raise for other HTTP errors
                response.raise_for_status()
                
                self.stats['successful_requests'] += 1
                
                if attempt > 0:
                    logger.info(f"Request succeeded after {attempt} retries")
                
                return response
                
            except (RequestException, HTTPError, Timeout, ConnectionError) as e:
                last_exception = e
                
                if attempt == self.retry_config.max_retries:
                    self.stats['failed_requests'] += 1
                    logger.error(f"Request failed after {attempt + 1} attempts: {e}")
                    break
                
                # Handle rate limiting specially
                if hasattr(e, 'response') and e.response and e.response.status_code == 429:
                    self.stats['rate_limited_requests'] += 1
                    retry_after = e.response.headers.get('Retry-After')
                    if retry_after:
                        try:
                            wait_time = float(retry_after)
                            logger.warning(f"Rate limited. Waiting {wait_time}s as requested by server")
                            time.sleep(wait_time)
                            continue
                        except ValueError:
                            pass
                
                self.stats['retried_requests'] += 1
                
                # Calculate delay for exponential backoff
                delay = self.retry_config.calculate_delay(attempt + 1)
                
                logger.warning(
                    f"Request attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.2f}s..."
                )
                
                time.sleep(delay)
        
        # If we get here, all retries failed
        raise last_exception
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Make GET request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request_with_retry('GET', url, params=params)
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> requests.Response:
        """Make POST request with retry logic."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self._make_request_with_retry('POST', url, data=data, json=json)
    
    def get_paginated_data(
        self,
        endpoint: str,
        page_param: str = 'page',
        per_page_param: str = 'per_page',
        per_page: int = 100,
        max_pages: Optional[int] = None,
        params: Optional[Dict] = None,
        response_processor: Optional[Callable[[requests.Response], List[Dict]]] = None
    ) -> Iterator[List[Dict[str, Any]]]:
        """
        Fetch paginated data from API endpoint.
        
        Args:
            endpoint: API endpoint to fetch from
            page_param: Parameter name for page number
            per_page_param: Parameter name for items per page
            per_page: Number of items per page
            max_pages: Maximum number of pages to fetch (None for no limit)
            params: Additional query parameters
            response_processor: Function to extract data from response
            
        Yields:
            List of items for each page
        """
        if response_processor is None:
            response_processor = lambda r: r.json() if isinstance(r.json(), list) else r.json().get('data', [])
        
        if params is None:
            params = {}
        
        page = 1
        total_items = 0
        
        logger.info(f"Starting paginated fetch from {endpoint}")
        
        while True:
            if max_pages and page > max_pages:
                logger.info(f"Reached maximum pages limit: {max_pages}")
                break
            
            # Prepare request parameters
            request_params = params.copy()
            request_params.update({
                page_param: page,
                per_page_param: per_page
            })
            
            logger.debug(f"Fetching page {page} with {per_page} items per page")
            
            try:
                response = self.get(endpoint, params=request_params)
                
                # Process response to extract data
                page_data = response_processor(response)
                
                if not page_data:
                    logger.info(f"No more data found at page {page}")
                    break
                
                total_items += len(page_data)
                logger.info(f"Page {page}: fetched {len(page_data)} items (total: {total_items})")
                
                yield page_data
                
                # Check if we've reached the end based on response size
                if len(page_data) < per_page:
                    logger.info(f"Received fewer items than requested, assuming end of data")
                    break
                
                page += 1
                
            except Exception as e:
                logger.error(f"Error fetching page {page}: {e}")
                raise
        
        logger.info(f"Completed paginated fetch: {total_items} total items across {page - 1} pages")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get request statistics."""
        stats = self.stats.copy()
        if stats['total_requests'] > 0:
            stats['success_rate'] = stats['successful_requests'] / stats['total_requests']
            stats['failure_rate'] = stats['failed_requests'] / stats['total_requests']
            stats['retry_rate'] = stats['retried_requests'] / stats['total_requests']
        else:
            stats['success_rate'] = 0.0
            stats['failure_rate'] = 0.0
            stats['retry_rate'] = 0.0
        
        return stats
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
