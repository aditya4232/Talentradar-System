"""Test location filter logic"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.job_api_scraper import _is_india_location

# Test with actual locations from the APIs
test_locations = [
    "Worldwide",
    "Americas, Europe, Asia, Oceania",
    "USA, Canada, USA timezones",
    "USA",
    "Remote",
    "India",
    "Bangalore, India",
    "Europe",
    "",
    None
]

print("="*70)
print("Testing _is_india_location() with real API values:")
print("="*70)

for loc in test_locations:
    result = _is_india_location(loc or "")
    status = "✅ PASS" if result else "❌ FAIL"
    print(f"{status}  '{loc}' → {result}")

print("\n" + "="*70)
print("Expected results:")
print("="*70)
print("✅ Worldwide - should PASS (remote keyword)")
print("❌ Americas, Europe, Asia, Oceania - should FAIL (no India or remote)")
print("❌ USA, Canada, USA timezones - should FAIL (specific countries)")
print("❌ USA - should FAIL (specific country)")
print("✅ Remote - should PASS (remote keyword)")
print("✅ India - should PASS (India keyword)")
print("✅ Bangalore, India - should PASS (India location)")
print("❌ Europe - should FAIL (specific region)")
print("✅ Empty/None - should PASS (no restrictions)")
