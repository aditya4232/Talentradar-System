# TalentRadar AI — Recruitment Operating System

> **Zero-cost, AI-native replacement for Naukri Resdex, LinkedIn Recruiter, and Way2Hire.**
> Built for Indian candidate sourcing and end-to-end hiring management.

---

## What It Does

| Feature | Details |
|---|---|
| **Multi-source Candidate Aggregation** | GitHub (official API), Naukri, LinkedIn, mock data |
| **AI TalentScore (0–100)** | 8-dimension scoring: Skills, Experience, Domain, Seniority, Freshness, Location, Salary, Trajectory |
| **JD Parsing** | Paste any JD → AI extracts skills, experience, domain, location, salary |
| **Recruitment Pipeline** | Kanban board with 13 stages, SLA tracking, notes |
| **AI Outreach Emails** | Personalized emails per candidate/job using Groq LLaMA |
| **Analytics Dashboard** | Funnel, source effectiveness, score distribution, SLA risk |
| **Indian-specific** | ₹ LPA salaries, notice periods, Indian city groupings, Naukri/LinkedIn focus |

**Total monthly cost: ₹0** (vs ₹25-75 Lakhs/yr for Naukri Resdex)

---

## Quick Start

### Windows
```bat
start.bat
```

### Mac / Linux
```bash
chmod +x start.sh && ./start.sh
```

Open **http://localhost:5173** in your browser.

**First time:** Go to **Source** page → click **"Seed 100 Demo Candidates"** to populate with realistic data.

---

## Manual Setup

### Backend (Python)

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your API keys (optional but recommended)

# Run
uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

### Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

---

## API Keys (All Free)

| Key | Where to Get | Why |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | AI scoring, JD parsing, email generation. **Free: 14,400 tokens/min** |
| `GITHUB_TOKEN` | [github.com/settings/tokens](https://github.com/settings/tokens) | Source developers from GitHub. **Free with higher rate limits** |
| `RESEND_API_KEY` | [resend.com](https://resend.com) | Send outreach emails. **Free: 3,000 emails/month** |

> **Works without any API keys** — AI falls back to regex-based scoring, email generation is shown as preview.

---

## Project Structure

```
TalentRadar System/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app entry
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # SQLite setup
│   │   ├── config.py            # Settings via .env
│   │   ├── api/
│   │   │   ├── jobs.py          # Jobs CRUD + JD parsing
│   │   │   ├── candidates.py    # Candidates CRUD + search
│   │   │   ├── pipeline.py      # Kanban board + stage moves
│   │   │   ├── outreach.py      # AI email generation + send
│   │   │   ├── analytics.py     # Dashboard + funnel stats
│   │   │   └── scrape.py        # Trigger scrapers
│   │   └── services/
│   │       ├── ai_engine.py     # TalentScore, JD parse, email gen
│   │       ├── email_service.py # Resend + SMTP + dry-run
│   │       ├── pipeline_service.py # SLA, stage logic
│   │       └── scrapers/
│   │           ├── github.py    # GitHub API scraper
│   │           ├── naukri.py    # Naukri Playwright scraper
│   │           ├── linkedin.py  # LinkedIn scraper
│   │           └── mock_data.py # Demo data generator
│   ├── requirements.txt
│   ├── .env.example
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── api/client.js        # API client (all endpoints)
│   │   ├── components/
│   │   │   ├── Layout.jsx       # Sidebar navigation
│   │   │   ├── TalentScoreBadge.jsx
│   │   │   └── StageBadge.jsx
│   │   └── pages/
│   │       ├── Dashboard.jsx    # KPIs, activity, charts
│   │       ├── Jobs.jsx         # Job list + create
│   │       ├── JobDetail.jsx    # AI candidate matches + email
│   │       ├── Candidates.jsx   # Searchable candidate pool
│   │       ├── CandidateDetail.jsx  # Full profile
│   │       ├── Pipeline.jsx     # Kanban board
│   │       ├── Analytics.jsx    # Charts + top candidates
│   │       └── Scrape.jsx       # Source candidates UI
│   └── Dockerfile
├── docker-compose.yml
├── start.bat                    # Windows one-click start
├── start.sh                     # Linux/Mac one-click start
└── README.md
```

---

## TalentScore Algorithm

Scored 0–100 across 8 dimensions:

| Dimension | Weight | How |
|---|---|---|
| Skills Match | 28% | Synonym-expanded skill matching vs JD requirements |
| Experience | 22% | Years of experience vs job requirements |
| Domain Relevance | 18% | DOMAIN_KEYWORDS matching (fintech, healthtech, etc.) |
| Seniority | 14% | Seniority level match (Senior/Staff/Principal/etc.) |
| Freshness | 8% | Last active recency (GitHub pushes, profile updates) |
| Location | 6% | City/region match with NCR grouping |
| Salary Fit | 4% | Expected salary within job budget |
| Trajectory | 6% | Career growth indicators |

Enhanced with Groq LLaMA 3.1 70B when `GROQ_API_KEY` is set.

---

## Pipeline Stages

```
SOURCED → APPROACHED → RESPONDED → SCREENING_SCHEDULED → SCREENING_DONE
→ SHORTLISTED → L1_INTERVIEW → L2_INTERVIEW → OFFER_SENT → OFFER_ACCEPTED → JOINED

Terminal: REJECTED | ON_HOLD
```

SLA alerts trigger at 3-7 days per stage (configurable in `pipeline_service.py`).

---

## Docker

```bash
cp backend/.env.example backend/.env
# Edit backend/.env with your keys

docker-compose up --build
```

---

## Tech Stack

| Layer | Technology | Cost |
|---|---|---|
| Backend | Python 3.12 + FastAPI | Free |
| Database | SQLite (upgradeable to PostgreSQL) | Free |
| AI/LLM | Groq API (LLaMA 3.1 70B) | Free tier |
| Frontend | React 18 + Vite + Tailwind CSS | Free |
| Charts | Recharts | Free |
| Icons | Lucide React | Free |
| Email | Resend / SMTP | Free tier |
| Scraping | Playwright + GitHub API | Free |

---

## Internship Notes

- This system is designed to **replace Naukri Resdex (~₹50L/yr) with a ₹0 self-hosted alternative**
- All AI features degrade gracefully without API keys (regex fallbacks)
- The mock data generator creates 100 realistic Indian candidates for demos
- GitHub scraper targets Indian developers by city detection in profile location
- Built for ScriptBees internal hiring ops — customize `STAGE_ORDER`, `STAGE_SLA_DAYS`, and scoring weights per your process
