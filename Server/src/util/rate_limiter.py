"""
Simple rate limiter for Lambda functions.

This implements a sliding window rate limiter using in-memory storage.
Note: Lambda instances may be reused, so this provides rate limiting per instance.
For distributed rate limiting, consider using DynamoDB or Redis.
"""

import time
from typing import Dict, Tuple, Any
from collections import defaultdict, deque


class RateLimiter:
    """
    Simple sliding window rate limiter.
    
    Tracks requests per identifier (e.g., IP address) and enforces limits.
    """
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            max_requests: Maximum number of requests allowed in the time window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        # Store request timestamps per identifier
        self._requests: Dict[str, deque] = defaultdict(deque)
    
    def is_allowed(self, identifier: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request from the identifier is allowed.
        
        Args:
            identifier: Unique identifier (e.g., IP address, user ID)
            
        Returns:
            Tuple of (is_allowed, rate_limit_info)
            - is_allowed: True if request is allowed, False if rate limited
            - rate_limit_info: Dict with rate limit details
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        # Get requests for this identifier
        request_times = self._requests[identifier]
        
        # Remove expired requests (outside the time window)
        while request_times and request_times[0] < cutoff_time:
            request_times.popleft()
        
        # Count current requests in window
        current_count = len(request_times)
        
        # Check if rate limit is exceeded
        if current_count >= self.max_requests:
            # Calculate retry after time (when the oldest request expires)
            retry_after = int(request_times[0] + self.window_seconds - current_time) + 1
            
            return False, {
                'allowed': False,
                'current_count': current_count,
                'limit': self.max_requests,
                'window_seconds': self.window_seconds,
                'retry_after': retry_after
            }
        
        # Add current request timestamp
        request_times.append(current_time)
        
        return True, {
            'allowed': True,
            'current_count': current_count + 1,
            'limit': self.max_requests,
            'window_seconds': self.window_seconds,
            'remaining': self.max_requests - current_count - 1
        }
    
    def reset(self, identifier: str) -> None:
        """
        Reset rate limit for a specific identifier.
        
        Args:
            identifier: Unique identifier to reset
        """
        if identifier in self._requests:
            del self._requests[identifier]
    
    def cleanup_old_entries(self) -> int:
        """
        Clean up old entries to prevent memory buildup.
        
        Returns:
            Number of identifiers cleaned up
        """
        current_time = time.time()
        cutoff_time = current_time - self.window_seconds
        
        identifiers_to_remove = []
        
        for identifier, request_times in self._requests.items():
            # Remove expired requests
            while request_times and request_times[0] < cutoff_time:
                request_times.popleft()
            
            # If no requests remain, mark for removal
            if not request_times:
                identifiers_to_remove.append(identifier)
        
        # Remove empty identifiers
        for identifier in identifiers_to_remove:
            del self._requests[identifier]
        
        return len(identifiers_to_remove)


# Global rate limiter instances for different endpoints
# These will persist across Lambda invocations in the same container
chat_rate_limiter = RateLimiter(max_requests=20, window_seconds=60)  # 20 requests per minute
scrape_rate_limiter = RateLimiter(max_requests=5, window_seconds=300)  # 5 requests per 5 minutes
