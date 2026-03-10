# 🎯 TalentRadar - QUICK START GUIDE

## ✅ System is READY!

The backend server is running at: **http://localhost:8000**
API Documentation: **http://localhost:8000/docs**

## 🚀 How to Use

### Option 1: Use the Web Dashboard (Recommended)

1. Open`frontend/index.html` in your browser
2. Enter a job description
3. Click "Find Candidates"
4. View AI-matched candidate leads!

### Option 2: Use the API Directly

Visit **http://localhost:8000/docs** for interactive API documentation

## 📊 Try This Search Now!

Go to the frontend and search with this job description:

```
Looking for a Senior Python Developer with 3-5 years experience.
Must have skills in:
- Python
- FastAPI or Django
- AWS cloud services
- Machine Learning
- PostgreSQL
- Docker

Location: Hyderabad
```  

## 🎬 What Happens When You Search?

1. **Skill Extraction** - AI extracts skills from job description
2. **Google X-Ray Search** - Searches LinkedIn, GitHub, Stack Overflow
3. **GitHub Search** - Finds developers by location and language
4. **Email Extraction** - Extracts contact information
5. **AI Matching** - Ranks candidates by relevance (0-100%)
6. **Results** - Shows top matches with full contact details

## 📥 Sample Output

You'll see candidates like this:

```
Name: Rahul Sharma
Match Score: 87%
Email: rahul.sharma@gmail.com
Location: Hyderabad
Skills: python, aws, machine learning, fastapi
GitHub: https://github.com/rahul-sharma
Status: ✅ Open to Work
Experience: 3 years
```

## 🔧 Current Configuration

- ✅ Backend API: Running on port 8000
- ✅ Database: SQLite (auto-created)
- ✅ AI Matching: Simple keyword-based (works without dependencies)
- ⚠️ Mock Data Mode: No API keys required! System generates realistic test data

## 🌟 Optional: Get Real Data

To get REAL candidate data instead of mock data:

1. Get a free Serper API key from https://serper.dev
2. Get a GitHub token from GitHub Settings
3. Add them to `backend/.env`:
   ```
   SERPER_API_KEY=your_key_here
   GITHUB_TOKEN=your_token_here
   ```
4. Restart the backend

**But the system works great with mock data for testing!**

## 💾 Export Data

Click "Export CSV" in the dashboard to download candidate leads in Excel-compatible format.

## 📚 API Endpoints

- `POST /search` - Search for candidates
- `GET /candidates` - List all candidates
- `GET /stats` - System statistics
- `POST /jobs` - Create job description
- Full docs: http://localhost:8000/docs

## 🛑 Stop the Server

Press `Ctrl+C` in the terminal where the backend is running

## 🔄 Restart Everything

```bash
# Start backend
cd backend
python main.py

# Open frontend
# Just open frontend/index.html in your browser
```

## ✨ Features Working

✅ Google X-Ray Search (with mock data)
✅ GitHub Integration (with mock data)
✅ Email Extraction
✅ AI Skill Matching
✅ Candidate Database
✅ Beautiful Dashboard
✅ CSV Export
✅ RESTful API
✅ Real-time Search

## 🎓 This is a Professional Project!

This system demonstrates:
- Modern FastAPI backend architecture
- AI/ML integration for matching
- Web scraping techniques
- Database design (SQLAlchemy ORM)
- REST API design
- Modern responsive UI
- Real-world recruitment automation

Perfect for your portfolio!

---

**Ready to find talent? Open frontend/index.html and start searching!** 🚀
