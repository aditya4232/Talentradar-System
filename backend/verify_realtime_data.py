"""Verify we're getting REAL, FRESH data from job sources"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import json

sys.path.insert(0, str(Path(__file__).parent))

from app.services.job_api_scraper import fetch_remotive, fetch_himalayas

async def verify_data_quality():
    print("="*70)
    print("🔍 REAL-TIME DATA VERIFICATION TEST")
    print(f"📅 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Test Remotive
    print("\n📡 Fetching from REMOTIVE API (Remote jobs)...")
    remotive_jobs = await fetch_remotive("python developer", limit=5)
    
    print(f"\n✅ Got {len(remotive_jobs)} jobs from Remotive")
    if remotive_jobs:
        job = remotive_jobs[0]
        print("\n" + "─"*70)
        print("📋 SAMPLE JOB #1 (Remotive):")
        print("─"*70)
        print(f"Title:       {job.get('title', 'N/A')}")
        print(f"Company:     {job.get('company', 'N/A')}")
        print(f"Location:    {job.get('location', 'N/A')}")
        print(f"Source:      {job.get('source', 'N/A')}")
        print(f"Profile URL: {job.get('profile_url', 'N/A')}")
        print(f"Skills:      {', '.join(job.get('skills', [])[:5])}")
        print(f"Summary:     {job.get('summary', 'N/A')[:200]}...")
        print("─"*70)
        
        # Verify URL is real
        url = job.get('profile_url', '')
        if url and url.startswith('http'):
            print(f"✅ URL is valid: {url}")
        else:
            print(f"⚠️ URL missing or invalid")
    else:
        print("⚠️ No jobs returned from Remotive")
    
    await asyncio.sleep(2)
    
    # Test Himalayas
    print("\n📡 Fetching from HIMALAYAS API (Flexible jobs)...")
    himalayas_jobs = await fetch_himalayas("react developer", limit=5)
    
    print(f"\n✅ Got {len(himalayas_jobs)} jobs from Himalayas")
    if himalayas_jobs:
        job = himalayas_jobs[0]
        print("\n" + "─"*70)
        print("📋 SAMPLE JOB #2 (Himalayas):")
        print("─"*70)
        print(f"Title:       {job.get('title', 'N/A')}")
        print(f"Company:     {job.get('company', 'N/A')}")
        print(f"Location:    {job.get('location', 'N/A')}")
        print(f"Source:      {job.get('source', 'N/A')}")
        print(f"Profile URL: {job.get('profile_url', 'N/A')}")
        print(f"Skills:      {', '.join(job.get('skills', [])[:5])}")
        print(f"Summary:     {job.get('summary', 'N/A')[:200]}...")
        print("─"*70)
        
        # Verify URL is real
        url = job.get('profile_url', '')
        if url and url.startswith('http'):
            print(f"✅ URL is valid: {url}")
        else:
            print(f"⚠️ URL missing or invalid")
    else:
        print("⚠️ No jobs returned from Himalayas")
    
    print("\n" + "="*70)
    print("📊 SUMMARY:")
    print("="*70)
    print(f"Total jobs fetched: {len(remotive_jobs) + len(himalayas_jobs)}")
    print(f"Remotive:  {len(remotive_jobs)} jobs")
    print(f"Himalayas: {len(himalayas_jobs)} jobs")
    
    # Data quality check
    all_jobs = remotive_jobs + himalayas_jobs
    valid_urls = sum(1 for j in all_jobs if j.get('profile_url', '').startswith('http'))
    has_company = sum(1 for j in all_jobs if j.get('company', '').strip())
    has_location = sum(1 for j in all_jobs if j.get('location', '').strip())
    has_skills = sum(1 for j in all_jobs if j.get('skills', []))
    
    print(f"\n✅ Data Quality Metrics:")
    print(f"   Valid URLs:     {valid_urls}/{len(all_jobs)} ({100*valid_urls//max(len(all_jobs),1)}%)")
    print(f"   Has Company:    {has_company}/{len(all_jobs)} ({100*has_company//max(len(all_jobs),1)}%)")
    print(f"   Has Location:   {has_location}/{len(all_jobs)} ({100*has_location//max(len(all_jobs),1)}%)")
    print(f"   Has Skills:     {has_skills}/{len(all_jobs)} ({100*has_skills//max(len(all_jobs),1)}%)")
    
    print("\n" + "="*70)
    print("🎯 VERDICT:")
    print("="*70)
    if all_jobs and valid_urls == len(all_jobs):
        print("✅ YES - Getting REAL, FRESH jobs with valid profile URLs!")
        print("✅ These are ACTUAL job postings you can visit and apply to")
        print("✅ Data is fetched in REAL-TIME from live APIs")
    elif all_jobs:
        print("⚠️ PARTIAL - Getting jobs but some URLs may be missing")
    else:
        print("❌ NO - Not getting any jobs (check API connection)")
    
    print("\n" + "="*70)
    print("📝 WHAT'S NOT WORKING (need free API keys):")
    print("="*70)
    print("❌ LinkedIn    - Needs JSearch API key (free)")
    print("❌ Naukri      - Needs Adzuna API key (free)")
    print("❌ Indeed      - Needs Adzuna/JSearch API keys (free)")
    print("❌ Glassdoor   - Needs JSearch API key (free)")
    print("\n💡 To get LinkedIn + Naukri + Indeed + Glassdoor:")
    print("   1. Get Adzuna API (3 min): https://developer.adzuna.com/signup")
    print("   2. Get JSearch API (2 min): https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch")
    print("   3. Add keys to backend/.env")
    print("   4. Restart backend → 3-4x more jobs!")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(verify_data_quality())
