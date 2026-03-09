"""Test scraper without search query"""
import asyncio
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.job_api_scraper import fetch_remotive, fetch_himalayas

async def test():
    print("Testing Remotive with generic 'developer' query...")
    jobs = await fetch_remotive("developer", limit=50)
    print(f"\n✅ Got {len(jobs)} jobs!")
    if jobs:
        for i, job in enumerate(jobs[:5]):
            print(f"\n{i+1}. {job['current_title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   URL: {job['profile_url'][:80]}...")
    
    print("\n" + "="*70)
    print("Testing Himalayas with generic 'developer' query...")
    jobs2 = await fetch_himalayas("developer", limit=50)
    print(f"\n✅ Got {len(jobs2)} jobs!")
    if jobs2:
        for i, job in enumerate(jobs2[:5]):
            print(f"\n{i+1}. {job['current_title']}")
            print(f"   Company: {job['company']}")
            print(f"   Location: {job['location']}")
            print(f"   URL: {job['profile_url'][:80]}...")

if __name__ == "__main__":
    asyncio.run(test())
