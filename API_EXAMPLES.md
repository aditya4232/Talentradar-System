# TalentRadar - API Examples

## Search for Candidates

### POST /search

Search for candidates based on job description.

**Request:**
```json
POST http://localhost:8000/search
Content-Type: application/json

{
  "job_description": "Looking for a Senior Python Developer with 3-5 years experience in FastAPI, AWS, and Machine Learning. Based in Hyderabad.",
  "location": "Hyderabad",
  "limit": 20
}
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Rahul Sharma",
    "email": "rahul.sharma@gmail.com",
    "location": "Hyderabad",
    "skills": "[\"python\", \"aws\", \"machine learning\", \"fastapi\"]",
    "github_url": "https://github.com/rahul-sharma",
    "linkedin_url": "https://linkedin.com/in/rahul-sharma",
    "portfolio_url": null,
    "bio": "Python Developer with 3 years experience...",
    "open_to_work": true,
    "experience_years": 3.0,
    "match_score": 87.5,
    "created_at": "2024-01-15T10:30:00",
    "updated_at": "2024-01-15T10:30:00"
  }
]
```

## Get All Candidates

### GET /candidates

**Request:**
```
GET http://localhost:8000/candidates?limit=50&open_to_work=true
```

**Response:**
```json
[
  {
    "id": 1,
    "name": "Rahul Sharma",
    "email": "rahul.sharma@gmail.com",
    ...
  }
]
```

## Create Job Description

### POST /jobs

**Request:**
```json
POST http://localhost:8000/jobs
Content-Type: application/json

{
  "title": "Senior Python Developer",
  "description": "We are looking for an experienced Python developer...",
  "required_skills": ["python", "fastapi", "aws", "postgresql"],
  "location": "Hyderabad",
  "experience_required": "3-5 years"
}
```

## Match Existing Candidates to Job

### POST /match/{job_id}

**Request:**
```
POST http://localhost:8000/match/1?limit=10
```

**Response:**
```json
{
  "job_id": 1,
  "matches": [
    {
      "id": 1,
      "name": "Rahul Sharma",
      "match_score": 87.5,
      ...
    }
  ]
}
```

## Get Statistics

### GET /stats

**Request:**
```
GET http://localhost:8000/stats
```

**Response:**
```json
{
  "total_candidates": 45,
  "candidates_open_to_work": 28,
  "total_jobs": 5,
  "total_matches": 120
}
```

## Python Code Examples

### Search using requests library

```python
import requests

# Search for candidates
response = requests.post(
    'http://localhost:8000/search',
    json={
        'job_description': 'Python developer with AWS experience',
        'location': 'Hyderabad',
        'limit': 20
    }
)

candidates = response.json()

for candidate in candidates:
    print(f"{candidate['name']} - Match: {candidate.get('match_score', 0)}%")
    print(f"  Email: {candidate['email']}")
    print(f"  Skills: {candidate['skills']}")
    print()
```

### Add a candidate manually

```python
import requests

response = requests.post(
    'http://localhost:8000/candidates',
    json={
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'location': 'Hyderabad',
        'skills': ['python', 'django', 'postgresql'],
        'github_url': 'https://github.com/johndoe',
        'bio': 'Full stack developer with 4 years experience',
        'open_to_work': True,
        'experience_years': 4.0
    }
)

print(response.json())
```

## JavaScript/Fetch Examples

### Search from frontend

```javascript
async function searchCandidates() {
    const response = await fetch('http://localhost:8000/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            job_description: 'Python developer with ML experience',
            location: 'Hyderabad',
            limit: 20
        })
    });
    
    const candidates = await response.json();
    console.log(candidates);
}
```

## cURL Examples

### Search
```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Python developer",
    "location": "Hyderabad",
    "limit": 10
  }'
```

### Get candidates
```bash
curl "http://localhost:8000/candidates?limit=10"
```

### Get stats
```bash
curl "http://localhost:8000/stats"
```
