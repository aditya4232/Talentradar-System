"""Cutshort scraper stub."""
import logging
from app.services.scrapers.base import BaseScraper
logger = logging.getLogger(__name__)


class CutshortScraper(BaseScraper):
    SOURCE_NAME = "cutshort"

    async def scrape(self, keywords: str, location: str = "India", limit: int = 20) -> list:
        logger.info("Cutshort scraping requires authentication - using mock fallback")
        return []
