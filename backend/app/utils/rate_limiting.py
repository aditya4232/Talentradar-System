"""
Professional Rate Limiting Utility

Implements token bucket algorithm for API rate limiting.
Prevents hitting API quotas and getting banned.
"""

import time
import random
from typing import Dict, Optional
from dataclasses import dataclass, field
from threading import Lock


@dataclass
class RateLimitBucket:
    """Token bucket for rate limiting."""
    
    max_tokens: int
    refill_rate: float  # tokens per second
    current_tokens: float = field(init=False)
    last_refill: float = field(init=False)
    lock: Lock = field(default_factory=Lock, init=False)
    
    def __post_init__(self):
        self.current_tokens = float(self.max_tokens)
        self.last_refill = time.time()
    
    def _refill(self):
        """Refill tokens based on time elapsed."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on refill rate
        tokens_to_add = elapsed * self.refill_rate
        self.current_tokens = min(
            self.max_tokens,
            self.current_tokens + tokens_to_add
        )
        self.last_refill = now
    
    def acquire(self, tokens: int = 1, timeout: Optional[float] = None) -> bool:
        """
        Try to acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire
            timeout: Max time to wait for tokens (None = wait indefinitely)
        
        Returns:
            bool: True if tokens acquired, False if timeout
        """
        start_time = time.time()
        
        with self.lock:
            while True:
                self._refill()
                
                if self.current_tokens >= tokens:
                    self.current_tokens -= tokens
                    return True
                
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        return False
                
                # Calculate wait time until enough tokens
                tokens_needed = tokens - self.current_tokens
                wait_time = tokens_needed / self.refill_rate
                
                # Cap wait time to timeout
                if timeout is not None:
                    remaining = timeout - (time.time() - start_time)
                    wait_time = min(wait_time, remaining)
                
                if wait_time > 0:
                    time.sleep(min(wait_time, 0.1))  # Sleep in small increments


class RateLimiter:
    """
    Centralized rate limiter for all API sources.
    
    Configured limits:
    - Adzuna: 1 request/second (free tier)
    - JSearch: 5 requests/minute (RapidAPI free)
    - Apify: 10 requests/minute
    """
    
    def __init__(self):
        self._buckets: Dict[str, RateLimitBucket] = {
            # Adzuna: 1 req/sec = 60 req/min
            "adzuna": RateLimitBucket(
                max_tokens=5,  # Burst capacity
                refill_rate=1.0  # 1 token per second
            ),
            
            # JSearch: 5 req/min = 1 req per 12 seconds
            "jsearch": RateLimitBucket(
                max_tokens=5,
                refill_rate=5.0 / 60.0  # 5 tokens per 60 seconds
            ),
            
            # Apify: 10 req/min = 1 req per 6 seconds
            "apify": RateLimitBucket(
                max_tokens=10,
                refill_rate=10.0 / 60.0
            ),
            
            # Crawl4AI: Local, no limit
            "crawl4ai": RateLimitBucket(
                max_tokens=1000,
                refill_rate=1000.0
            ),
        }
    
    def acquire(self, source: str, tokens: int = 1, timeout: float = 30.0) -> bool:
        """
        Acquire permission to make an API call.
        
        Args:
            source: API source name (adzuna, jsearch, apify, crawl4ai)
            tokens: Number of requests (default 1)
            timeout: Max seconds to wait (default 30)
        
        Returns:
            bool: True if acquired, False if timeout
        """
        source_lower = source.lower()
        
        if source_lower not in self._buckets:
            # Unknown source, allow by default
            return True
        
        bucket = self._buckets[source_lower]
        return bucket.acquire(tokens, timeout)
    
    def get_status(self) -> Dict[str, dict]:
        """Get current status of all rate limiters."""
        status = {}
        
        for name, bucket in self._buckets.items():
            with bucket.lock:
                bucket._refill()
                status[name] = {
                    "available_tokens": round(bucket.current_tokens, 2),
                    "max_tokens": bucket.max_tokens,
                    "refill_rate": bucket.refill_rate,
                    "percentage": round(
                        (bucket.current_tokens / bucket.max_tokens) * 100, 1
                    ),
                }
        
        return status


# Global rate limiter instance
rate_limiter = RateLimiter()


def rate_limit(source: str, timeout: float = 30.0):
    """
    Decorator for rate-limited functions.
    
    Usage:
        @rate_limit("adzuna")
        def fetch_adzuna_jobs(query):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not rate_limiter.acquire(source, timeout=timeout):
                raise TimeoutError(
                    f"Rate limit timeout for {source} after {timeout}s"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Exponential backoff for retries
def exponential_backoff(
    func,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0
):
    """
    Execute function with exponential backoff on failure.
    
    Args:
        func: Function to execute
        max_retries: Maximum retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
    
    Returns:
        Function result or raises last exception
    """
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            # Calculate delay: base_delay * 2^attempt
            delay = min(base_delay * (2 ** attempt), max_delay)
            # Add random jitter to prevent thundering herd
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter
            
            time.sleep(delay)
    
    raise RuntimeError("Exponential backoff failed")
