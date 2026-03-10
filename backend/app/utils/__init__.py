"""
TalentRadar Professional Utilities Package

- contact_extraction: Extract email/phone from text
- deduplication: Fuzzy matching and duplicate detection
- error_handling: Exception handling middleware
- logging_config: Structured logging with rotation
- rate_limiting: Token bucket rate limiter
"""

from .contact_extraction import extract_email, extract_phone, normalize_contact_info
from .deduplication import are_duplicates, find_and_mark_duplicates, generate_profile_hash
from .error_handling import (
    TalentRadarException,
    ScraperException,
    DatabaseException,
    ValidationException,
    APILimitException,
    register_exception_handlers,
)
from .logging_config import (
    app_logger,
    scraper_logger,
    api_logger,
    db_logger,
    PerformanceLogger,
)
from .rate_limiting import rate_limiter, rate_limit

__all__ = [
    # Contact extraction
    "extract_email",
    "extract_phone",
    "normalize_contact_info",
    # Deduplication
    "are_duplicates",
    "find_and_mark_duplicates",
    "generate_profile_hash",
    # Error handling
    "TalentRadarException",
    "ScraperException",
    "DatabaseException",
    "ValidationException",
    "APILimitException",
    "register_exception_handlers",
    # Logging
    "app_logger",
    "scraper_logger",
    "api_logger",
    "db_logger",
    "PerformanceLogger",
    # Rate limiting
    "rate_limiter",
    "rate_limit",
]
