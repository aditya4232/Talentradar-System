import os
from openai import AsyncOpenAI
from dotenv import load_dotenv
import json
import re

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY if GROQ_API_KEY else "dummy_key"
)

async def parse_jd_with_llm(raw_text: str) -> dict:
    """Parse raw JD text into structured JSON using Groq LLM."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing.")

    system_prompt = """You are an expert technical recruiter AI.
Extract structured information from the provided job description text.
Respond ONLY with a valid JSON object matching this schema:
{
  "title": "Job Title",
  "company": "Company Name or Unknown",
  "required_skills": ["skill1", "skill2", ...],
  "experience_min": 0,
  "experience_max": 5,
  "domain": "Domain like Fintech, SaaS, E-commerce etc"
}
Rules:
- required_skills should be specific technical skills (React, Python, AWS, etc.)
- experience_min and experience_max should be numbers
- If company is not mentioned, write "Not Specified"
- domain should be the industry/vertical
Do NOT include markdown backticks. Just raw JSON."""

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Parse this JD:\n\n{raw_text[:6000]}"}
            ],
            temperature=0.1,
            max_tokens=1000
        )
        result = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping
        result = re.sub(r'^```(?:json)?\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        return json.loads(result)
    except Exception as e:
        raise Exception(f"JD parse failed: {e}")


async def extract_candidates_from_text(raw_text: str, source: str, page_title: str = "", url: str = "") -> list[dict]:
    """Extract candidate/job listing data from scraped page text using AI."""
    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY is missing.")

    # Guard against blocked/empty pages — prevents LLM hallucination
    blocked_signals = ["access denied", "403 forbidden", "cloudflare", "captcha",
                       "just a moment", "verify you are human", "blocked",
                       "enable javascript", "please enable cookies"]
    text_lower = raw_text.lower().strip()
    if len(raw_text.strip()) < 200:
        print(f"[LLM Parser] Skipping — too little text ({len(raw_text.strip())} chars) from {source}")
        return []
    if any(sig in text_lower[:500] for sig in blocked_signals):
        print(f"[LLM Parser] Skipping — blocked/captcha page detected from {source}")
        return []

    system_prompt = f"""You are TalentRadar AI — an expert data extraction engine for recruitment.
You are extracting JOB LISTINGS (which represent potential candidate requirements) OR CANDIDATE PROFILES 
from text scraped from {source} ({url}).

Page title: "{page_title}"

CRITICAL RULES:
1. Extract EVERY listing/profile you can find — aim for 10-20+ entries
2. For job listings (like from Naukri/LinkedIn), extract the role info as if they are candidate profiles:
   - The job TITLE becomes current_title
   - The COMPANY posting the job becomes company
   - The LOCATION mentioned becomes location
   - The EXPERIENCE range becomes experience_years (use the average)
   - The SKILLS/TAGS mentioned become skills
   - The JOB DESCRIPTION snippet becomes summary
3. For actual candidate profiles, extract their details directly
4. Construct profile_url from the source site when possible:
   - For Naukri: use the job URL pattern
   - For LinkedIn: use the job/profile URL pattern
5. NEVER return empty arrays if there is any usable data in the text
6. Use real data from the text — NO fabrication

Respond ONLY with a raw JSON array (no markdown):
[
  {{
    "name": "Job Title or Candidate Name",
    "email": null,
    "phone": null,
    "profile_url": "URL if available",
    "source": "{source}",
    "current_title": "Actual Job Title",
    "company": "Company Name",
    "location": "City, State",
    "experience_years": 3.0,
    "skills": ["skill1", "skill2", "skill3"],
    "summary": "Brief description"
  }}
]"""

    try:
        # Truncate to fit context window (Llama 3.1 8B: 8K context)
        truncated = raw_text[:12000]
        
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract all candidate/job data from this {source} page:\n\n{truncated}"}
            ],
            temperature=0.15,
            max_tokens=3000
        )
        
        result = response.choices[0].message.content.strip()
        
        # Clean markdown wrapping
        result = re.sub(r'^```(?:json)?\s*', '', result)
        result = re.sub(r'\s*```$', '', result)
        
        parsed = json.loads(result)
        if isinstance(parsed, list):
            print(f"[LLM Parser] Extracted {len(parsed)} entries from {source}")
            return parsed
        elif isinstance(parsed, dict):
            return [parsed]
        return []
        
    except json.JSONDecodeError as je:
        print(f"[LLM Parser] JSON decode error: {je}")
        # Try to extract JSON from response
        try:
            match = re.search(r'\[.*\]', result, re.DOTALL)
            if match:
                return json.loads(match.group())
        except:
            pass
        return []
    except Exception as e:
        print(f"[LLM Parser] Error: {e}")
        return []


def extract_experience_from_title(title: str) -> float:
    """Extract estimated years of experience from job title."""
    if not title:
        return 0.0
    
    title_lower = title.lower()
    
    # Extract explicit years from patterns like "3+ years", "5-7 years", etc.
    import re
    year_patterns = [
        r'(\d+)\+?\s*(?:to|-)\s*(\d+)?\s*(?:years?|yrs?)',
        r'(\d+)\+\s*(?:years?|yrs?)'
    ]
    for pattern in year_patterns:
        match = re.search(pattern, title_lower)
        if match:
            return float(match.group(1))
    
    # Infer from seniority level
    seniority_map = {
        "intern": 0.0,
        "trainee": 0.5,
        "junior": 1.5,
        "associate": 2.0,
        "mid": 3.5,
        "senior": 5.0,
        "sr": 5.0,
        "lead": 7.0,
        "staff": 8.0,
        "principal": 10.0,
        "architect": 9.0,
        "manager": 6.0,
        "head": 10.0,
        "director": 12.0,
        "vp": 15.0,
        "vice president": 15.0,
        "chief": 18.0,
        "cto": 18.0,
        "ceo": 20.0
    }
    
    for keyword, years in seniority_map.items():
        if keyword in title_lower:
            return years
    
    # Default for generic titles
    return 2.0


def compute_talent_score(candidate_data: dict) -> float:
    """Compute a TalentScore (0-100) based on profile completeness and signals.
    
    Enhanced scoring with better weights for Data/AI Engineer roles:
    - Skills: 30 points (most important)
    - Experience: 20 points  
    - Title relevance: 18 points
    - Company quality: 12 points
    - Profile completeness: 20 points
    """
    score = 0.0
    title = candidate_data.get("current_title", "")
    company = candidate_data.get("company", "")
    skills = candidate_data.get("skills", []) or []
    exp = candidate_data.get("experience_years", 0) or 0
    
    # === SKILLS MATCH (30 points) - MOST IMPORTANT ===
    if skills:
        base_skill_score = min(10 + len(skills), 22)  # 10-22 pts for having skills
        score += base_skill_score
        
        # BONUS: Premium Data/AI Engineer skills (+8 points)
        premium_skills = {
            "python", "sql", "aws", "azure", "gcp", "spark", "hadoop", "kafka",
            "airflow", "snowflake", "databricks", "tensorflow", "pytorch", "scikit-learn",
            "pandas", "numpy", "docker", "kubernetes", "etl", "data warehouse",
            "machine learning", "deep learning", "nlp", "computer vision",
            "mlops", "data pipeline", "big data", "scala", "redshift", "bigquery"
        }
        skills_lower = [s.lower() for s in skills]
        premium_count = sum(1 for s in skills_lower if any(p in s for p in premium_skills))
        score += min(premium_count, 8)
    else:
        # If no skills extracted, give some base points for having a job posting
        score += 5
    
    # === EXPERIENCE (20 points) ===
    if exp > 0:
        # Progressive scoring: 0-2 yrs = 5 pts, 3-5 yrs = 10 pts, 6-8 yrs = 15 pts, 9+ yrs = 20 pts
        if exp <= 2:
            score += 5
        elif exp <= 5:
            score += 10
        elif exp <= 8:
            score += 15
        else:
            score += 20
    
    # === TITLE RELEVANCE (18 points) ===
    if title:
        score += 10  # Base for having a title
        
        # Data/AI Engineer bonus (+5 pts)
        target_roles = ["data engineer", "ai engineer", "machine learning", "ml engineer", 
                       "data scientist", "mlops", "analytics engineer", "big data"]
        if any(role in title.lower() for role in target_roles):
            score += 5
        
        # Seniority bonus (+3 pts)
        if any(w in title.lower() for w in ["senior", "lead", "principal", "staff", "architect", "manager", "director", "vp"]):
            score += 3
    
    # === COMPANY QUALITY (12 points) ===
    if company:
        score += 5  # Base for having a company
        
        # Top tech company bonus (+7 pts)
        top_companies = {
            "google", "microsoft", "amazon", "meta", "apple", "netflix", "uber", "airbnb",
            "flipkart", "razorpay", "zomato", "swiggy", "paytm", "phonepe", "cred", "zerodha",
            "tcs", "infosys", "wipro", "hcl", "accenture", "deloitte", "cognizant",
            "deutsche bank", "jp morgan", "goldman sachs", "morgan stanley", "citi", "hsbc",
            "tredence", "fractal", "mu sigma", "tiger analytics"
        }
        if any(comp in company.lower() for comp in top_companies):
            score += 7
    
    # === PROFILE COMPLETENESS (20 points) ===
    # Name (3 pts)
    if candidate_data.get("name"):
        score += 3
    
    # Location - Hyderabad Priority (5 pts + 2 bonus)
    location = candidate_data.get("location", "")
    if location:
        score += 5
        if "hyderabad" in location.lower() or "telangana" in location.lower():
            score += 2  # Hyderabad bonus
    
    # Contact info (5 pts)
    if candidate_data.get("email"):
        score += 3
    if candidate_data.get("phone"):
        score += 2
    
    # Profile URL (3 pts)
    if candidate_data.get("profile_url"):
        score += 3
    
    # Summary/Description (4 pts)
    summary = candidate_data.get("summary", "")
    if summary and len(summary) > 50:
        score += 4
    
    return min(round(score, 1), 100.0)
