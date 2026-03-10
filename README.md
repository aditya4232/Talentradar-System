# 🎯 TalentRadar - AI-Powered Recruitment System

A professional, production-ready AI recruitment system that automatically finds and matches candidates with job descriptions using advanced AI and web scraping techniques.

## ✨ Features

- 🔍 **Google X-Ray Search** - Find candidate profiles across LinkedIn, GitHub, Stack Overflow
- 🤖 **AI-Powered Matching** - Use sentence transformers and embeddings for intelligent candidate matching
- 📧 **Email Extraction** - Automatically extract contact information from public sources
- 🐙 **GitHub Integration** - Search GitHub for developers by location and skills
- 📊 **Beautiful Dashboard** - Modern, responsive web interface
- 💾 **Database Storage** - Store and manage candidate leads
- 📥 **CSV Export** - Export candidate data for further processing
- 🚀 **RESTful API** - Full-featured API for integrations

## 🏗️ Architecture

```
Job Description
    ↓
Skill Extractor (AI)
    ↓
Google X-Ray Query Generator
    ↓
Multi-Source Search (Google, GitHub, etc.)
    ↓
Profile Scraper & Email Extractor
    ↓
AI Matching Engine (embeddings + FAISS)
    ↓
Ranked Candidate Leads
```

## 📋 Prerequisites

- Python 3.8+
- pip (Python package manager)
- A modern web browser

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment (Optional)

Copy `.env.example` to `.env` and add your API keys:

```bash
cp .env.example .env
```

Edit `.env`:
```
SERPER_API_KEY=your_serper_api_key_here  # Optional: Get from serper.dev
GITHUB_TOKEN=your_github_token_here       # Optional: For better GitHub rate limits
```

**Note:** The system works with mock data even without API keys!

### 3. Run the Backend

```bash
cd backend
python main.py
```

The API will start at `http://localhost:8000`

### 4. Open the Frontend

Open `frontend/index.html` in your browser, or use a simple HTTP server:

```bash
cd frontend
python -m http.server 3000
```

Then visit `http://localhost:3000`

## 📖 Usage

### Using the Web Dashboard

1. Enter a job description with required skills
2. Specify location (default: Hyderabad)
3. Click "Find Candidates"
4. View AI-matched candidates with scores
5. Export results to CSV

### Example Job Description

```
Looking for a Python Developer with experience in:
- FastAPI or Django
- AWS cloud services
- Machine Learning
- 2-5 years of experience
- Based in Hyderabad
```

### Using the API

#### Search for Candidates

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "job_description": "Python developer with AWS and ML experience",
    "location": "Hyderabad",
    "limit": 20
  }'
```

#### Get All Candidates

```bash
curl "http://localhost:8000/candidates"
```

#### View Statistics

```bash
curl "http://localhost:8000/stats"
```

## 📁 Project Structure

```
TalentRadar/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database models
│   ├── models.py               # Pydantic models
│   ├── config.py               # Configuration
│   ├── requirements.txt        # Dependencies
│   └── services/
│       ├── recruitment_engine.py  # Main orchestrator
│       ├── skill_extractor.py     # Skill extraction
│       ├── google_search.py       # Google X-Ray search
│       ├── github_service.py      # GitHub integration
│       ├── email_extractor.py     # Email extraction
│       └── ai_matching.py         # AI matching engine
├── frontend/
│   ├── index.html              # Dashboard
│   ├── styles.css              # Styling
│   └── app.js                  # Frontend logic
└── README.md
```

## 🔧 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/search` | POST | Search for candidates |
| `/candidates` | GET | List all candidates |
| `/candidates/{id}` | GET | Get candidate by ID |
| `/candidates` | POST | Add candidate manually |
| `/jobs` | GET | List job descriptions |
| `/jobs` | POST | Create job description |
| `/match/{job_id}` | POST | Match job with existing candidates |
| `/stats` | GET | Get system statistics |
| `/docs` | GET | Interactive API documentation |

## 🤖 AI Matching Engine

The system uses:
- **SentenceTransformers** (`all-MiniLM-L6-v2`) for semantic embeddings
- **FAISS** for fast similarity search
- **Cosine Similarity** for matching scores (0-100%)

Matching considers:
- Skills overlap
- Experience level
- Location
- Bio/description similarity
- "Open to work" status

## 🎨 Features Showcase

### Skill Extraction
Automatically identifies 50+ common tech skills from text:
- Programming languages (Python, JavaScript, Java, etc.)
- Frameworks (React, Django, FastAPI, etc.)
- Cloud platforms (AWS, Azure, GCP)
- Databases (PostgreSQL, MongoDB, Redis, etc.)
- ML/AI technologies (TensorFlow, PyTorch, etc.)

### Google X-Ray Search
Generates targeted search queries like:
```
site:linkedin.com/in "python developer" "Hyderabad" "open to work"
site:github.com "Hyderabad" "machine learning"
site:stackoverflow.com/users "Hyderabad" python
```

### Email Extraction
- Parses web pages for email addresses
- Validates email format
- Filters out fake/noreply emails
- Checks GitHub events for commit emails

## 📊 Sample Output

```json
{
  "name": "Rahul Sharma",
  "email": "rahul.sharma@gmail.com",
  "location": "Hyderabad",
  "skills": ["python", "aws", "machine learning", "django"],
  "match_score": 87.5,
  "open_to_work": true,
  "experience_years": 3,
  "github_url": "https://github.com/rahul-sharma",
  "linkedin_url": "https://linkedin.com/in/rahul-sharma"
}
```

## 🔐 Privacy & Ethics

- Only searches **public** data
- Respects robots.txt and rate limits
- No unauthorized data harvesting
- Follows platform terms of service
- Designed for legitimate recruitment purposes

## 🌟 Getting API Keys (Optional)

### Serper API (Google Search)
1. Visit [serper.dev](https://serper.dev)
2. Sign up for free tier (2,500 free searches)
3. Copy your API key to `.env`

### GitHub Token
1. Go to GitHub Settings → Developer Settings → Personal Access Tokens
2. Generate new token (public_repo scope)
3. Copy token to `.env`

**Note:** System works with mock data without these keys!

## 🚀 Deployment

### Railway / Render / Heroku
```bash
# Add these build commands
pip install -r backend/requirements.txt
python backend/main.py
```

### Docker (Coming Soon)
```bash
docker build -t talentradar .
docker run -p 8000:8000 talentradar
```

## 🛠️ Troubleshooting

### Backend won't start
- Ensure Python 3.8+ is installed
- Install dependencies: `pip install -r requirements.txt`
- Check if port 8000 is available

### Frontend can't connect to API
- Ensure backend is running on port 8000
- Check browser console for CORS errors
- Verify API_BASE_URL in `app.js`

### AI model download fails
- First run downloads the embedding model (~80MB)
- Requires internet connection
- Model cached after first download

## 📝 License

MIT License - Feel free to use for personal or commercial projects

## 🤝 Contributing

Contributions welcome! This is a learning project showcasing:
- FastAPI best practices
- AI/ML integration
- Web scraping techniques
- Modern UI/UX design

## 💡 Future Enhancements

- [ ] LinkedIn Sales Navigator integration
- [ ] Resume parsing (PDF/DOCX)
- [ ] Email outreach automation
- [ ] Chrome extension for quick searches
- [ ] Advanced filtering options
- [ ] Interview scheduling
- [ ] ATS integration

## 📧 Support

For issues or questions, create an issue in the repository.

---

**Built with ❤️ using FastAPI, Python, and AI**
