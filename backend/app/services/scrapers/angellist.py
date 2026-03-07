"""AngelList/Wellfound scraper stub."""
import logging
from app.services.scrapers.base import BaseScraper
logger = logging.getLogger(__name__)


class AngelListScraper(BaseScraper):
    SOURCE_NAME = "angellist"

    async def scrape(self, keywords: str, location: str = "India", limit: int = 20) -> list:
        logger.info("AngelList/Wellfound scraping requires authentication - using mock fallback")
        return []
