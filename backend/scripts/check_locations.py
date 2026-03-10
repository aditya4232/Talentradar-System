import httpx

r = httpx.get('http://localhost:8000/api/v1/candidates')
candidates = r.json()
print(f'Total candidates: {len(candidates)}')
print('\nCandidate locations:')
for c in candidates:
    print(f'  - {c["name"]}: {c["location"]}')
