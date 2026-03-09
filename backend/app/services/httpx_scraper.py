import httpx
import random
from bs4 import BeautifulSoup
from .llm_parser import extract_candidates_from_text

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
]


async def httpx_scrape(url: str, source: str = "Web") -> list[dict]:
    """Lightweight fallback scraper using httpx + BeautifulSoup + LLM parsing."""
    print(f"[HttpxScraper] Fetching: {url}")

    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    try:
        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=30.0,
            headers=headers,
            verify=False,  # Handle sites with cert issues (e.g. TimesJobs)
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove script/style/nav/footer noise
            for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"]):
                tag.decompose()

            page_title = soup.title.string if soup.title else ""
            raw_text = soup.get_text(separator="\n", strip=True)

            if len(raw_text) < 100:
                print(f"[HttpxScraper] Too little text extracted from {url}")
                return []

            candidates = await extract_candidates_from_text(
                raw_text=raw_text,
                source=source,
                page_title=page_title or "",
                url=url,
            )
            print(f"[HttpxScraper] Extracted {len(candidates)} candidates from {url}")
            return candidates

    except httpx.HTTPStatusError as e:
        print(f"[HttpxScraper] HTTP {e.response.status_code} for {url}")
        return []
    except Exception as e:
        print(f"[HttpxScraper] Error: {e}")
        return []
