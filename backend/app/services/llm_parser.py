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


def compute_talent_score(candidate_data: dict) -> float:
    """Compute a TalentScore (0-100) based on profile completeness and signals."""
    score = 0.0
    
    # Name presence (5 pts)
    if candidate_data.get("name"):
        score += 5
    
    # Title relevance (20 pts)
    title = candidate_data.get("current_title", "")
    if title:
        score += 15
        # Senior/Lead/Principal bonus
        if any(w in title.lower() for w in ["senior", "lead", "principal", "staff", "architect", "manager", "director"]):
            score += 5
    
    # Company (10 pts)
    company = candidate_data.get("company", "")
    if company:
        score += 7
        # Top company bonus
        if any(w in company.lower() for w in ["google", "microsoft", "amazon", "meta", "apple", "flipkart", 
                                                "razorpay", "zomato", "swiggy", "paytm", "phonepe", "cred",
                                                "infosys", "tcs", "wipro", "hcl", "accenture"]):
            score += 3
    
    # Experience (15 pts)
    exp = candidate_data.get("experience_years", 0) or 0
    if exp > 0:
        score += min(exp * 2, 15)
    
    # Skills (25 pts)
    skills = candidate_data.get("skills", []) or []
    if skills:
        score += min(len(skills) * 3, 25)
    
    # Location (5 pts)
    if candidate_data.get("location"):
        score += 5
    
    # Contact info (10 pts)
    if candidate_data.get("email"):
        score += 5
    if candidate_data.get("phone"):
        score += 5
    
    # Profile URL (5 pts)
    if candidate_data.get("profile_url"):
        score += 5
    
    # Summary (5 pts)
    summary = candidate_data.get("summary", "")
    if summary and len(summary) > 20:
        score += 5
    
    return min(round(score, 1), 100.0)
