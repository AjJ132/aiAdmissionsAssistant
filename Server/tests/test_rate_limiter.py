"""
Tests for the rate limiter module.
"""

import time
import pytest
from src.util.rate_limiter import RateLimiter


def test_rate_limiter_allows_requests_within_limit():
    """Test that requests within the limit are allowed."""
    limiter = RateLimiter(max_requests=5, window_seconds=10)
    
    # Make 5 requests - all should be allowed
    for i in range(5):
        is_allowed, info = limiter.is_allowed("test_user")
        assert is_allowed is True
        assert info['allowed'] is True
        assert info['current_count'] == i + 1
        assert info['limit'] == 5


def test_rate_limiter_blocks_requests_over_limit():
    """Test that requests over the limit are blocked."""
    limiter = RateLimiter(max_requests=3, window_seconds=10)
    
    # Make 3 requests - all should be allowed
    for i in range(3):
        is_allowed, _ = limiter.is_allowed("test_user")
        assert is_allowed is True
    
    # 4th request should be blocked
    is_allowed, info = limiter.is_allowed("test_user")
    assert is_allowed is False
    assert info['allowed'] is False
    assert 'retry_after' in info


def test_rate_limiter_sliding_window():
    """Test that the sliding window works correctly."""
    limiter = RateLimiter(max_requests=2, window_seconds=1)
    
    # Make 2 requests
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is True
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is True
    
    # 3rd request should be blocked
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is False
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Should be allowed again
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is True


def test_rate_limiter_multiple_identifiers():
    """Test that different identifiers are tracked separately."""
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    
    # Make 2 requests for user1
    is_allowed, _ = limiter.is_allowed("user1")
    assert is_allowed is True
    is_allowed, _ = limiter.is_allowed("user1")
    assert is_allowed is True
    
    # 3rd request for user1 should be blocked
    is_allowed, _ = limiter.is_allowed("user1")
    assert is_allowed is False
    
    # But user2 should still be able to make requests
    is_allowed, _ = limiter.is_allowed("user2")
    assert is_allowed is True
    is_allowed, _ = limiter.is_allowed("user2")
    assert is_allowed is True


def test_rate_limiter_reset():
    """Test that reset works correctly."""
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    
    # Make 2 requests
    limiter.is_allowed("test_user")
    limiter.is_allowed("test_user")
    
    # 3rd request should be blocked
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is False
    
    # Reset the user
    limiter.reset("test_user")
    
    # Should be able to make requests again
    is_allowed, _ = limiter.is_allowed("test_user")
    assert is_allowed is True


def test_rate_limiter_cleanup():
    """Test that cleanup removes old entries."""
    limiter = RateLimiter(max_requests=5, window_seconds=1)
    
    # Make requests for multiple users
    limiter.is_allowed("user1")
    limiter.is_allowed("user2")
    limiter.is_allowed("user3")
    
    # Wait for window to expire
    time.sleep(1.1)
    
    # Cleanup should remove all entries
    cleaned = limiter.cleanup_old_entries()
    assert cleaned == 3
    
    # After cleanup, new requests should start fresh
    is_allowed, info = limiter.is_allowed("user1")
    assert is_allowed is True
    assert info['current_count'] == 1


def test_rate_limiter_remaining_count():
    """Test that remaining count is calculated correctly."""
    limiter = RateLimiter(max_requests=5, window_seconds=10)
    
    is_allowed, info = limiter.is_allowed("test_user")
    assert info['remaining'] == 4
    
    is_allowed, info = limiter.is_allowed("test_user")
    assert info['remaining'] == 3
    
    is_allowed, info = limiter.is_allowed("test_user")
    assert info['remaining'] == 2


def test_rate_limiter_retry_after():
    """Test that retry_after is calculated correctly."""
    limiter = RateLimiter(max_requests=2, window_seconds=10)
    
    # Make 2 requests
    limiter.is_allowed("test_user")
    time.sleep(0.1)  # Small delay to ensure time difference
    limiter.is_allowed("test_user")
    
    # 3rd request should be blocked with retry_after
    is_allowed, info = limiter.is_allowed("test_user")
    assert is_allowed is False
    assert 'retry_after' in info
    assert info['retry_after'] > 0
    assert info['retry_after'] <= 10
