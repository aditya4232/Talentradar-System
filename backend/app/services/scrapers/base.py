"""Base scraper class with rate limiting, user agent rotation, and error handling."""

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
]


class BaseScraper(ABC):
    SOURCE_NAME = "unknown"
    RATE_LIMIT_SECONDS = (3, 8)

    def __init__(self):
        self.logger = logging.getLogger(f"scraper.{self.SOURCE_NAME}")

    def get_headers(self) -> dict:
        return {
            "User-Agent": random.choice(USER_AGENTS),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }

    async def rate_limit(self):
        delay = random.uniform(*self.RATE_LIMIT_SECONDS)
        await asyncio.sleep(delay)

    @abstractmethod
    async def scrape(self, keywords: str, location: str = "India", limit: int = 50) -> list:
        """Scrape candidates. Returns list of candidate dicts."""
        pass

    def normalize_candidate(self, raw: dict) -> dict:
        """Normalize a raw scraped candidate to standard format."""
        return {
            "name": raw.get("name", "Unknown"),
            "email": raw.get("email"),
            "phone": raw.get("phone"),
            "current_role": raw.get("current_role") or raw.get("title") or raw.get("headline"),
            "current_company": raw.get("current_company") or raw.get("company"),
            "experience_years": raw.get("experience_years") or raw.get("experience"),
            "skills": raw.get("skills", []),
            "location": raw.get("location"),
            "linkedin_url": raw.get("linkedin_url"),
            "github_url": raw.get("github_url"),
            "naukri_url": raw.get("naukri_url"),
            "sources": [self.SOURCE_NAME],
            "salary_current": raw.get("salary_current") or raw.get("current_salary"),
            "salary_expected": raw.get("salary_expected") or raw.get("expected_salary"),
            "notice_period": raw.get("notice_period"),
            "summary": raw.get("summary") or raw.get("bio"),
            "last_active": raw.get("last_active") or datetime.utcnow(),
            "freshness_score": raw.get("freshness_score", 0.7),
            "work_history": raw.get("work_history", []),
            "education": raw.get("education", []),
        }
