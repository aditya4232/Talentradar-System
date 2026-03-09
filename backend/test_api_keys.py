from dotenv import load_dotenv
import os

load_dotenv()

print("="*70)
print("🔑 API KEYS STATUS CHECK")
print("="*70)

adzuna_app_id = os.getenv("ADZUNA_APP_ID")
adzuna_api_key = os.getenv("ADZUNA_API_KEY")
rapidapi_key = os.getenv("RAPIDAPI_KEY")

if adzuna_app_id:
    print(f"✅ Adzuna App ID: {adzuna_app_id[:10]}... (LOADED)")
else:
    print("❌ Adzuna App ID: NOT FOUND")

if adzuna_api_key:
    print(f"✅ Adzuna API Key: {adzuna_api_key[:10]}... (LOADED)")
else:
    print("❌ Adzuna API Key: NOT FOUND")

if rapidapi_key:
    print(f"✅ RapidAPI Key: {rapidapi_key[:10]}... (LOADED)")
else:
    print("❌ RapidAPI Key: NOT FOUND")

print("\n" + "="*70)
if adzuna_app_id and adzuna_api_key and rapidapi_key:
    print("🎉 ALL API KEYS LOADED SUCCESSFULLY!")
    print("   Now testing actual API calls...")
    print("="*70)
    
    # Test the APIs
    import asyncio
    from app.services.job_api_scraper import fetch_adzuna_india, fetch_jsearch_india
    
    async def test_apis():
        print("\n📡 Testing Adzuna India API (Naukri + Monster + Indeed)...")
        adzuna_jobs = await fetch_adzuna_india("python developer", limit=5)
        print(f"   Got {len(adzuna_jobs)} jobs from Adzuna!")
        if adzuna_jobs:
            print(f"   Sample: {adzuna_jobs[0].get('current_title')} @ {adzuna_jobs[0].get('company')}")
        
        print("\n📡 Testing JSearch API (LinkedIn + Glassdoor)...")
        jsearch_jobs = await fetch_jsearch_india("react developer", limit=5)
        print(f"   Got {len(jsearch_jobs)} jobs from JSearch!")
        if jsearch_jobs:
            print(f"   Sample: {jsearch_jobs[0].get('current_title')} @ {jsearch_jobs[0].get('company')}")
        
        print("\n" + "="*70)
        print(f"🎯 TOTAL: {len(adzuna_jobs) + len(jsearch_jobs)} jobs from premium APIs!")
        print("="*70)
    
    asyncio.run(test_apis())
else:
    print("⚠️ SOME KEYS MISSING - Check backend/.env file")
    print("="*70)
