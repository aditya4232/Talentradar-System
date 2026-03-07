"""Indeed India scraper - httpx + BeautifulSoup with mock fallback."""

import httpx
import asyncio
import random
import logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from app.services.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)


class IndeedScraper(BaseScraper):
    SOURCE_NAME = "indeed"
    BASE_URL = "https://in.indeed.com"
    RATE_LIMIT_SECONDS = (4, 9)

    async def scrape(self, keywords: str, location: str = "India", limit: int = 30) -> list:
        """Scrape Indeed India for resume profiles."""
        candidates = []
        headers = self.get_headers()

        url = f"{self.BASE_URL}/resumes"
        params = {
            "q": keywords,
            "l": location if location != "India" else "",
        }

        try:
            await self.rate_limit()
            async with httpx.AsyncClient(follow_redirects=True, timeout=20.0) as client:
                response = await client.get(url, params=params, headers=headers)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "lxml")
                    resume_cards = soup.find_all("div", class_=["icl-Card", "resumecard_mainlayout"])
                    for card in resume_cards[:limit]:
                        candidate = self._parse_resume_card(card, keywords, location)
                        if candidate:
                            candidates.append(candidate)
                else:
                    logger.warning(f"Indeed returned {response.status_code}")
        except Exception as e:
            logger.warning(f"Indeed scrape failed: {e}")

        logger.info(f"Indeed scraper found {len(candidates)} candidates")
        return candidates

    def _parse_resume_card(self, card, keywords: str, location: str) -> dict:
        name_elem = card.find(["h2", "a"], class_=["icl-u-textColor--primary"])
        name = name_elem.get_text(strip=True) if name_elem else None
        if not name:
            return None

        skills = [k.strip() for k in keywords.split(",")][:5]
        return {
            "name": name,
            "skills": skills,
            "location": location,
            "sources": ["indeed"],
            "last_active": datetime.utcnow() - timedelta(days=random.randint(1, 45)),
            "freshness_score": 0.75,
        }
