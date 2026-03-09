"""Quick test to verify Indian job board scrapers are working"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.indian_job_scrapers import (
    scrape_naukri,
    scrape_foundit,
    scrape_instahyre,
    scrape_wellfound,
    scrape_cutshort,
    fetch_all_indian_sources
)

async def test_naukri():
    """Test Naukri.com scraper"""
    print("\n" + "="*60)
    print("🧪 TESTING: Naukri.com Scraper")
    print("="*60)
    try:
        results = await scrape_naukri("python developer", limit=5)
        print(f"✅ Naukri scraper working! Found {len(results)} jobs")
        if results:
            print(f"\nSample job:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Company: {results[0]['company']}")
            print(f"  Location: {results[0].get('location', 'N/A')}")
            print(f"  URL: {results[0].get('profile_url', 'N/A')[:80]}...")
        return True
    except Exception as e:
        print(f"❌ Naukri scraper error: {e}")
        return False

async def test_foundit():
    """Test Foundit.in scraper"""
    print("\n" + "="*60)
    print("🧪 TESTING: Foundit.in (Monster India) Scraper")
    print("="*60)
    try:
        results = await scrape_foundit("python developer", limit=5)
        print(f"✅ Foundit scraper working! Found {len(results)} jobs")
        if results:
            print(f"\nSample job:")
            print(f"  Title: {results[0]['title']}")
            print(f"  Company: {results[0]['company']}")
            print(f"  Location: {results[0].get('location', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Foundit scraper error: {e}")
        return False

async def test_all_sources():
    """Test all Indian sources together"""
    print("\n" + "="*60)
    print("🧪 TESTING: All Indian Sources (Orchestrator)")
    print("="*60)
    try:
        results = await fetch_all_indian_sources("python developer india")
        print(f"\n✅ ALL INDIAN SOURCES TEST COMPLETE!")
        print(f"📊 Total unique jobs found: {len(results)}")
        
        # Show breakdown by source
        sources = {}
        for job in results:
            src = job.get('source', 'Unknown')
            sources[src] = sources.get(src, 0) + 1
        
        print(f"\n📈 Breakdown by source:")
        for src, count in sorted(sources.items(), key=lambda x: -x[1]):
            print(f"  {src}: {count} jobs")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    print("\n" + "🚀"*30)
    print("INDIAN JOB BOARD SCRAPERS - VERIFICATION TEST")
    print("🚀"*30)
    
    # Test individual scrapers
    naukri_ok = await test_naukri()
    await asyncio.sleep(2)  # Brief pause between tests
    
    # Test orchestrator (runs all at once)
    all_ok = await test_all_sources()
    
    print("\n" + "="*60)
    print("📝 TEST SUMMARY")
    print("="*60)
    print(f"Naukri.com:         {'✅ PASS' if naukri_ok else '❌ FAIL'}")
    print(f"All Sources:        {'✅ PASS' if all_ok else '❌ FAIL'}")
    print("="*60)
    
    if naukri_ok and all_ok:
        print("\n✅ ALL TESTS PASSED! Indian job board scrapers are working!")
        print("   You can now run the full scraper and get jobs from:")
        print("   - Naukri.com (India's #1 job site)")
        print("   - Foundit.in (Monster India)")
        print("   - Instahyre (Premium tech jobs)")
        print("   - Wellfound (AngelList startups)")
        print("   - Cutshort (Tech professionals)")
        return 0
    else:
        print("\n⚠️ SOME TESTS FAILED - Check errors above")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
