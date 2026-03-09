import asyncio
from .llm_parser import extract_candidates_from_text

try:
    from crawl4ai import AsyncWebCrawler
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("[Crawl4AI] crawl4ai not installed. Crawl4AI engine will be skipped.")

async def crawl_with_ai(url: str, source: str = "Web"):
    """
    Use Crawl4AI's AsyncWebCrawler to get LLM-optimized content from any URL.
    This bypasses many anti-bot mechanisms and provides high-quality text.
    """
    if not CRAWL4AI_AVAILABLE:
        print(f"[Crawl4AI] Skipping {url} — crawl4ai not installed.")
        return []

    print(f"[Crawl4AI] Intelligent crawl initiated for: {url}")
    
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=url)
        
        if result.success:
            print(f"[Crawl4AI] Successfully crawled {url}")
            markdown_content = result.markdown
            
            candidates = await extract_candidates_from_text(
                raw_text=markdown_content,
                source=source,
                page_title=url,
                url=url
            )
            return candidates
        else:
            print(f"[Crawl4AI] Crawl failed for {url}: {result.error_message}")
            return []
