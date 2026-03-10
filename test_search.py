import requests
import json

# API endpoint
API_URL = "http://localhost:8000"

print("=" * 80)
print("🧪 TESTING TALENTRADAR - DATA ENGINEER SEARCH")
print("=" * 80)

# Job Description
job_description = """
Looking for a Data Engineer in Hyderabad with minimum 2 years of experience.

Required Skills:
- Python
- SQL
- Data Pipelines
- ETL
- Apache Spark or similar big data tools
- Cloud platforms (AWS/Azure/GCP)
- Data Warehousing
- PostgreSQL or similar databases

Experience: 2+ years
Location: Hyderabad
"""

print("\n📝 JOB DESCRIPTION:")
print(job_description)
print("\n" + "=" * 80)

# Make search request
print("\n🔍 Searching for candidates...")
print("(This may take a moment while Claude Opus analyzes candidates...)\n")

try:
    response = requests.post(
        f"{API_URL}/search",
        json={
            "job_description": job_description,
            "location": "Hyderabad",
            "limit": 15
        },
        timeout=180
    )
    
    if response.status_code == 200:
        candidates = response.json()
        
        print(f"\n✅ FOUND {len(candidates)} CANDIDATES!\n")
        print("=" * 80)
        
        for i, candidate in enumerate(candidates, 1):
            print(f"\n{'='*80}")
            print(f"CANDIDATE #{i}")
            print(f"{'='*80}")
            
            print(f"👤 Name:           {candidate.get('name', 'N/A')}")
            print(f"📧 Email:          {candidate.get('email', 'Not available')}")
            print(f"📍 Location:       {candidate.get('location', 'N/A')}")
            print(f"⭐ Match Score:    {candidate.get('match_score', 0)}%")
            
            # Parse skills
            skills = candidate.get('skills', '[]')
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except:
                    skills = []
            
            if skills:
                print(f"🛠️  Skills:         {', '.join(skills[:10])}")
                if len(skills) > 10:
                    print(f"                  ... and {len(skills) - 10} more")
            
            if candidate.get('experience_years'):
                print(f"💼 Experience:     {candidate.get('experience_years')} years")
            
            if candidate.get('open_to_work'):
                print(f"✅ Status:         OPEN TO WORK")
            
            print(f"\n🔗 Profile Links:")
            if candidate.get('github_url'):
                print(f"   GitHub:   {candidate.get('github_url')}")
            if candidate.get('linkedin_url'):
                print(f"   LinkedIn: {candidate.get('linkedin_url')}")
            if candidate.get('portfolio_url'):
                print(f"   Portfolio: {candidate.get('portfolio_url')}")
            
            if candidate.get('bio'):
                bio = candidate['bio'][:150]
                print(f"\n📝 Bio: {bio}{'...' if len(candidate.get('bio', '')) > 150 else ''}")
        
        print("\n" + "=" * 80)
        print("📊 SUMMARY STATISTICS")
        print("=" * 80)
        
        # Get stats
        stats_response = requests.get(f"{API_URL}/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            print(f"\n📈 Total Candidates in Database: {stats['total_candidates']}")
            print(f"✅ Open to Work: {stats['candidates_open_to_work']}")
            print(f"💼 Job Postings: {stats['total_jobs']}")
        
        # Quality metrics
        print("\n" + "=" * 80)
        print("🎯 QUALITY METRICS")
        print("=" * 80)
        
        avg_score = sum(c.get('match_score', 0) for c in candidates) / len(candidates) if candidates else 0
        with_email = sum(1 for c in candidates if c.get('email'))
        with_github = sum(1 for c in candidates if c.get('github_url'))
        open_to_work = sum(1 for c in candidates if c.get('open_to_work'))
        
        print(f"\n📊 Average Match Score: {avg_score:.2f}%")
        print(f"📧 Candidates with Email: {with_email}/{len(candidates)} ({with_email/len(candidates)*100:.1f}%)")
        print(f"🐙 Candidates with GitHub: {with_github}/{len(candidates)} ({with_github/len(candidates)*100:.1f}%)")
        print(f"✅ Open to Work: {open_to_work}/{len(candidates)} ({open_to_work/len(candidates)*100:.1f}%)")
        
        print("\n" + "=" * 80)
        print("💡 RECOMMENDED TOP 5 CANDIDATES")
        print("=" * 80)
        
        for i, candidate in enumerate(candidates[:5], 1):
            skills = candidate.get('skills', '[]')
            if isinstance(skills, str):
                try:
                    skills = json.loads(skills)
                except:
                    skills = []
            
            print(f"\n{i}. {candidate.get('name', 'N/A')} - {candidate.get('match_score', 0)}% match")
            print(f"   📧 {candidate.get('email', 'Contact via profile')}")
            print(f"   🛠️  Top Skills: {', '.join(skills[:5])}")
            if candidate.get('open_to_work'):
                print(f"   ✅ ACTIVELY SEEKING")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE - System is working properly!")
        print("=" * 80)
        
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Cannot connect to backend server!")
    print("Make sure the backend is running:")
    print("  cd backend")
    print("  python main.py")
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")

print("\n📥 Want to export these results?")
print("Visit http://localhost:3000 (frontend) and click 'Export CSV'\n")
