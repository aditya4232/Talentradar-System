"""Monitor scraper progress and show results"""
import httpx
import time
import asyncio
from datetime import datetime

async def monitor():
    start_time = time.time()
    duration = 10 * 60  # 10 minutes
    last_count = 0
    
    print("\n" + "=" * 80)
    print("🎯 MONITORING 10-MINUTE DATA/AI ENGINEER SCAN - HYDERABAD")
    print("=" * 80)
    print(f"Start Time: {datetime.now().strftime('%H:%M:%S')}")
    print(f"Target: Data Engineer, AI Engineer in Hyderabad")
    print(f"Duration: 10 minutes")
    print("=" * 80 + "\n")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while time.time() - start_time < duration:
            try:
                # Get candidates
                resp = await client.get("http://localhost:8000/api/v1/candidates", params={"limit": 1})
                data = resp.json()
                total = data.get("total", 0)
                new = total - last_count
                last_count = total
                
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                print(f"\r⏱️  {elapsed//60:02d}:{elapsed%60:02d} | "
                      f"🎯 {total} found | "
                      f"➕ {new} new | "
                      f"⏳ {remaining//60}m {remaining%60}s left", 
                      end="", flush=True)
                
                await asyncio.sleep(10)
                
            except Exception as e:
                print(f"\nError: {e}")
                await asyncio.sleep(10)
        
        # Stop scraper
        print("\n\n⏹️  Stopping scraper...")
        await client.post("http://localhost:8000/api/v1/scraper/stop")
        
        # Get final results
        print("\n" + "=" * 80)
        print("📊 FINAL RESULTS")
        print("=" * 80 + "\n")
        
        resp = await client.get("http://localhost:8000/api/v1/candidates", params={"limit": 100})
        data = resp.json()
        candidates = data.get("candidates", [])
        total = data.get("total", 0)
        
        print(f"✅ Total Candidates: {total}\n")
        
        # Group by location
        hyderabad = [c for c in candidates if "hyderabad" in c.get("location", "").lower() or "telangana" in c.get("location", "").lower()]
        print(f"📍 Hyderabad/Telangana: {len(hyderabad)}")
        print(f"🌐 Other India/Remote: {total - len(hyderabad)}\n")
        
        # Group by source
        sources = {}
        for c in candidates:
            source = c.get("source", "Unknown").split("(")[0].strip()
            sources[source] = sources.get(source, 0) + 1
        
        print("📊 By Source:")
        for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
            print(f"   • {source}: {count}")
        
        # Show top 5 Hyderabad candidates
        if hyderabad:
            print("\n" + "=" * 80)
            print("🌟 TOP 5 CANDIDATES IN HYDERABAD")
            print("=" * 80)
            
            top = sorted(hyderabad, key=lambda x: x.get("talent_score", 0), reverse=True)[:5]
            for i, c in enumerate(top, 1):
                print(f"\n#{i} {c.get('current_title', 'Unknown')}")
                print(f"   🏢 {c.get('company', 'N/A')}")
                print(f"   📍 {c.get('location', 'N/A')}")
                print(f"   ⭐ Score: {c.get('talent_score', 0)}/100")
                print(f"   💡 {', '.join(c.get('skills', [])[:4])}")
                print(f"   🔗 {c.get('profile_url', 'N/A')}")
        
        print("\n" + "=" * 80)
        print("✅ SCAN COMPLETE!")
        print("=" * 80)
        print(f"🌐 View all: http://localhost:8080/candidates")
        print()

if __name__ == "__main__":
    asyncio.run(monitor())
