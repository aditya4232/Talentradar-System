"""Check database contents"""
import sqlite3
import os

# Get the correct path
db_path = "talentradar.db" if os.path.exists("talentradar.db") else "backend/talentradar.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("=" * 80)
print("DATABASE CONTENT CHECK")
print("=" * 80)

# Get count
cursor.execute("SELECT COUNT(*) FROM candidates")
total = cursor.fetchone()[0]
print(f"\nTotal candidates: {total}\n")

# Get first 5 records
cursor.execute("SELECT id, name, current_title, company, location, source FROM candidates LIMIT 5")
print("First 5 candidates:")
print("-" * 80)

for row in cursor.fetchall():
    print(f"\nID: {row[0]}")
    print(f"Name: {row[1]}")
    print(f"Title: {row[2]}")
    print(f"Company: {row[3]}")
    print(f"Location: {row[4]}")
    print(f"Source: {row[5]}")

conn.close()
