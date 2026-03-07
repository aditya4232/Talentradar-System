"""LinkedIn scraper stub - returns mock data (LinkedIn heavily restricts scraping)."""

import logging
from datetime import datetime, timedelta
import random

from app.services.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class LinkedInScraper(BaseScraper):
    SOURCE_NAME = "linkedin"

    async def scrape(self, keywords: str, location: str = "India", limit: int = 30) -> list:
        """LinkedIn is heavily protected. Returns empty to trigger mock fallback."""
        logger.info("LinkedIn scraping is restricted - using mock data fallback")
        return []
