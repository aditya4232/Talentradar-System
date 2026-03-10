import sys
import os
import asyncio

# Setup paths
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper import ScrapingManager
from app.config import settings

async def test_linkedin_sdk_mock():
    print("Testing LinkedIn SDK integration (Mock URL)...")
    manager = ScrapingManager()
    
    # We use a real-looking but example URL
    test_url = "https://www.linkedin.com/in/williamhgates"
    
    print(f"Scraping {test_url}...")
    try:
        # This will attempt to use linkedin-scraper if credentials exist, 
        # or fall back to standard scraping if not.
        result = await manager.scrape_url(test_url)
        
        if result:
            print("\nSUCCESS! Extracted Data:")
            print(f"Name: {result.name}")
            print(f"Title: {result.current_title}")
            print(f"Company: {result.company}")
            print(f"Source: {result.source}")
        else:
            print("\nFAILED: No data returned. This is expected if no credentials/Chrome are setup.")
            
    except Exception as e:
        print(f"\nERROR during test: {str(e)}")

if __name__ == "__main__":
    if not settings.linkedin_email:
        print("WARNING: LINKEDIN_EMAIL not set in .env. Will test fallback logic.")
    asyncio.run(test_linkedin_sdk_mock())
