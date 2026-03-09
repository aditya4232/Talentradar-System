"""
FOCUSED 10-MINUTE SCAN FOR BEST DATA & AI ENGINEER CANDIDATES IN HYDERABAD
- Targets: Data Engineer, AI Engineer roles
- Location: Hyderabad, Telangana (+ remote India)
- Sources: Adzuna (Naukri/Monster/Indeed), JSearch (LinkedIn/Glassdoor)
- Duration: 10 minutes
- Quality: Premium APIs only (Remotive & Himalayas removed)
"""
import httpx
import time
import asyncio
from datetime import datetime

async def run_focused_scan():
    base_url = "http://localhost:8000/api/v1"
    
    print("=" * 80)
    print("🎯 STARTING FOCUSED 10-MINUTE SCAN - DATA & AI ENGINEERS IN HYDERABAD")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target Roles: Data Engineer, AI Engineer, ML Engineer")
    print(f"Target Location: Hyderabad, Telangana (+ remote India)")
    print(f"Data Sources: Adzuna (Naukri/Monster/Indeed) + JSearch (LinkedIn/Glassdoor)")
    print(f"Duration: 10 minutes")
    print("=" * 80)
    print()
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Start the scraper
        print("🚀 Starting scraper...")
        try:
            response = await client.post(f"{base_url}/scraper/run")
            if response.status_code == 200:
                print("✓ Scraper started successfully!")
            else:
                print(f"✗ Failed to start scraper: {response.text}")
                return
        except Exception as e:
            print(f"✗ Error starting scraper: {e}")
            return
        
        print()
        print("📊 MONITORING PROGRESS (10 minutes)...")
        print("-" * 80)
        
        start_time = time.time()
        end_time = start_time + (10 * 60)  # 10 minutes
        last_count = 0
        
        while time.time() < end_time:
            try:
                # Get status
                status = await client.get(f"{base_url}/scraper/status")
                status_data = status.json()
                
                # Get candidate count
                candidates = await client.get(f"{base_url}/candidates")
                candidate_data = candidates.json()
                total_candidates = candidate_data.get("total", 0)
                
                # Calculate progress
                elapsed = int(time.time() - start_time)
                remaining = int(end_time - time.time())
                new_candidates = total_candidates - last_count
                last_count = total_candidates
                
                # Display progress
                print(f"\r⏱️  {elapsed//60:02d}:{elapsed%60:02d} elapsed | "
                      f"🎯 {total_candidates} candidates found | "
                      f"➕ {new_candidates} new | "
                      f"⏳ {remaining//60}m {remaining%60}s remaining", end="", flush=True)
                
                await asyncio.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"\n⚠️  Error monitoring: {e}")
                await asyncio.sleep(5)
        
        print("\n")
        print("-" * 80)
        print("⏱️  10 MINUTES COMPLETE - STOPPING SCRAPER...")
        
        # Stop the scraper
        try:
            stop = await client.post(f"{base_url}/scraper/stop")
            if stop.status_code == 200:
                print("✓ Scraper stopped successfully!")
            else:
                print(f"✗ Failed to stop scraper: {stop.text}")
        except Exception as e:
            print(f"⚠️  Error stopping scraper: {e}")
        
        print()
        print("=" * 80)
        print("📈 FINAL RESULTS - BEST DATA & AI ENGINEER CANDIDATES")
        print("=" * 80)
        
        # Get final statistics
        try:
            candidates_resp = await client.get(f"{base_url}/candidates", params={"limit": 1000})
            candidates_data = candidates_resp.json()
            total = candidates_data.get("total", 0)
            candidates_list = candidates_data.get("candidates", [])
            
            print(f"\n✅ Total Candidates Found: {total}")
            print(f"📍 Location Focus: Hyderabad, Telangana, Remote India")
            print(f"💼 Role Focus: Data Engineer, AI Engineer, ML Engineer")
            print()
            
            # Count by source
            sources = {}
            hyderabad_count = 0
            for c in candidates_list:
                source = c.get("source", "Unknown").split("(")[0].strip()
                sources[source] = sources.get(source, 0) + 1
                location = c.get("location", "").lower()
                if "hyderabad" in location or "telangana" in location:
                    hyderabad_count += 1
            
            print("📊 Breakdown by Source:")
            for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
                print(f"   • {source}: {count} candidates")
            
            print(f"\n📍 Hyderabad/Telangana Jobs: {hyderabad_count}")
            print(f"🌐 Remote/Other India: {total - hyderabad_count}")
            
            # Show top candidates
            if candidates_list:
                print("\n" + "=" * 80)
                print("🌟 TOP 10 CANDIDATES (Sorted by Talent Score)")
                print("=" * 80)
                
                # Sort by talent_score
                top_candidates = sorted(candidates_list, key=lambda x: x.get("talent_score", 0), reverse=True)[:10]
                
                for i, candidate in enumerate(top_candidates, 1):
                    print(f"\n#{i} {candidate.get('name', 'Unknown')}")
                    print(f"   📌 Title: {candidate.get('current_title', 'N/A')}")
                    print(f"   🏢 Company: {candidate.get('company', 'N/A')}")
                    print(f"   📍 Location: {candidate.get('location', 'N/A')}")
                    print(f"   ⭐ Score: {candidate.get('talent_score', 0)}/100")
                    print(f"   💡 Skills: {', '.join(candidate.get('skills', [])[:5])}")
                    print(f"   🔗 URL: {candidate.get('profile_url', 'N/A')}")
                    print(f"   📂 Source: {candidate.get('source', 'N/A')}")
            
            print("\n" + "=" * 80)
            print("✅ SCAN COMPLETE!")
            print("=" * 80)
            print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n🌐 View all candidates in browser: http://localhost:8080/candidates")
            print(f"🎯 Access API: http://localhost:8000/api/v1/candidates")
            print()
            
        except Exception as e:
            print(f"✗ Error fetching final results: {e}")

if __name__ == "__main__":
    asyncio.run(run_focused_scan())
