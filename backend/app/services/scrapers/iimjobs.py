"""iimjobs scraper stub."""
import logging
from app.services.scrapers.base import BaseScraper
logger = logging.getLogger(__name__)


class IimjobsScraper(BaseScraper):
    SOURCE_NAME = "iimjobs"

    async def scrape(self, keywords: str, location: str = "India", limit: int = 20) -> list:
        logger.info("iimjobs scraping requires authentication - using mock fallback")
        return []
