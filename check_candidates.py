"""Quick check of current candidates"""
import sqlite3

db_path = "backend/talentradar.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get total count
cursor.execute("SELECT COUNT(*) FROM candidates")
total = cursor.fetchone()[0]
print(f"✅ Total Candidates Found: {total}\n")

# Get Hyderabad count
cursor.execute("SELECT COUNT(*) FROM candidates WHERE location LIKE '%Hyderabad%' OR location LIKE '%Telangana%'")
hyd_count = cursor.fetchone()[0]
print(f"📍 Hyderabad/Telangana Jobs: {hyd_count}")
print(f"🌐 Other India/Remote: {total - hyd_count}\n")

# Show sources
print("📊 By Source:")
cursor.execute("SELECT source, COUNT(*) as count FROM candidates GROUP BY source ORDER BY count DESC")
for source, count in cursor.fetchall():
    source_name = source.split("(")[0].strip() if source else "Unknown"
    print(f"   • {source_name}: {count}")

# Top 10 from Hyderabad
print("\n" + "=" * 80)
print("🌟 TOP 10 DATA/AI ENGINEER JOBS IN HYDERABAD (Best Talent Score)")
print("=" * 80)

cursor.execute("""
    SELECT current_title, company, location, talent_score, skills, profile_url, source
    FROM candidates
    WHERE (location LIKE '%Hyderabad%' OR location LIKE '%Telangana%')
    ORDER BY talent_score DESC
    LIMIT 10
""")

for i, (title, company, location, score, skills, url, source) in enumerate(cursor.fetchall(), 1):
    print(f"\n#{i} {title}")
    print(f"   🏢 Company: {company}")
    print(f"   📍 Location: {location}")
    print(f"   ⭐ Score: {score}/100")
    print(f"   💡 Skills: {skills}")
    print(f"   🔗 URL: {url}")
    print(f"   📂 Source: {source}")

conn.close()

print("\n" + "=" * 80)
print("🌐 View all in browser: http://localhost:8080/candidates")
print("=" * 80)
