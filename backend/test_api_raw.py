"""Debug test to see what APIs actually return"""
import asyncio
import httpx
import json

async def test_remotive_raw():
    print("="*70)
    print("Testing REMOTIVE API directly...")
    print("="*70)
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test without search first
        r = await client.get("https://remotive.com/api/remote-jobs", params={"limit": 5})
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Total jobs: {len(data.get('jobs', []))}")
            if data.get('jobs'):
                job = data['jobs'][0]
                print(f"\nFirst job:")
                print(f"  Title: {job.get('title')}")
                print(f"  Company: {job.get('company_name')}")
                print(f"  Location: {job.get('candidate_required_location')}")
                print(f"  URL: {job.get('url')}")
                print(f"  ID: {job.get('id')}")
        else:
            print(f"Error: {r.text[:200]}")
    
    await asyncio.sleep(2)
    
    # Test with search
    print("\n" + "="*70)
    print("Testing REMOTIVE with 'python' search...")
    print("="*70)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get("https://remotive.com/api/remote-jobs", params={"search": "python", "limit": 5})
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Jobs matching 'python': {len(data.get('jobs', []))}")
            for i, job in enumerate(data.get('jobs', [])[:3]):
                print(f"\nJob {i+1}:")
                print(f"  Title: {job.get('title')}")
                print(f"  Location: {job.get('candidate_required_location')}")

async def test_himalayas_raw():
    print("\n" + "="*70)
    print("Testing HIMALAYAS API directly...")
    print("="*70)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get("https://himalayas.app/jobs/api", params={"limit": 5})
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Total jobs: {len(data.get('jobs', []))}")
            if data.get('jobs'):
                job = data['jobs'][0]
                print(f"\nFirst job:")
                print(f"  Title: {job.get('title')}")
                print(f"  Company: {job.get('companyName')}")
                print(f"  Location Restrictions: {job.get('locationRestrictions', [])}")
                print(f"  Slug: {job.get('slug')}")
        else:
            print(f"Error: {r.text[:200]}")
    
    await asyncio.sleep(2)
    
    print("\n" + "="*70)
    print("Testing HIMALAYAS with 'react' search...")
    print("="*70)
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.get("https://himalayas.app/jobs/api", params={"q": "react", "limit": 5})
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"Jobs matching 'react': {len(data.get('jobs', []))}")
            for i, job in enumerate(data.get('jobs', [])[:3]):
                print(f"\nJob {i+1}:")
                print(f"  Title: {job.get('title')}")
                print(f"  Location: {job.get('locationRestrictions', [])}")

async def main():
    await test_remotive_raw()
    await test_himalayas_raw()

if __name__ == "__main__":
    asyncio.run(main())
