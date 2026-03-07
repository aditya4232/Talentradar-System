"""
TalentRadar AI Engine
Core AI logic: JD parsing, TalentScore computation, email generation
Works without API keys using rule-based fallbacks.
"""

import re
import json
import logging
from typing import Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Skill synonym map for fuzzy matching
SKILL_SYNONYMS = {
    "react": ["reactjs", "react.js", "react js", "react 18", "react18"],
    "node": ["nodejs", "node.js", "node js"],
    "javascript": ["js", "es6", "es2015", "ecmascript", "vanilla js"],
    "typescript": ["ts"],
    "python": ["python3", "python 3"],
    "machine learning": ["ml", "machine-learning"],
    "artificial intelligence": ["ai", "deep learning", "dl"],
    "kubernetes": ["k8s"],
    "postgresql": ["postgres", "pg"],
    "mongodb": ["mongo"],
    "amazon web services": ["aws", "amazon aws"],
    "google cloud": ["gcp", "google cloud platform"],
    "microsoft azure": ["azure"],
    "spring boot": ["springboot", "spring"],
    "angular": ["angularjs", "angular.js"],
    "vue": ["vuejs", "vue.js"],
    "docker": ["containerization", "containers"],
    "ci/cd": ["cicd", "continuous integration", "continuous deployment", "devops pipeline"],
    "rest api": ["restful", "rest", "api development"],
    "graphql": ["gql"],
    "redis": ["redis cache"],
    "elasticsearch": ["elastic search", "elk"],
    "kafka": ["apache kafka", "event streaming"],
    "microservices": ["micro services", "microservice architecture"],
    "data science": ["data analytics", "data analysis"],
    "tableau": ["tableau desktop"],
    "power bi": ["powerbi", "microsoft power bi"],
    ".net": ["dotnet", "asp.net", "c#"],
    "flutter": ["flutter sdk", "dart flutter"],
    "react native": ["rn", "react-native"],
}

# Domain keywords for classification
DOMAIN_KEYWORDS = {
    "fintech": ["payment", "banking", "finance", "fintech", "neobank", "lending", "insurtech", "trading", "wallet", "upi", "nbfc"],
    "healthtech": ["health", "medical", "hospital", "pharma", "clinical", "ehr", "telemedicine", "healthcare"],
    "ecommerce": ["ecommerce", "e-commerce", "marketplace", "retail", "shopping", "d2c", "inventory", "logistics"],
    "edtech": ["education", "edtech", "learning", "lms", "course", "tutoring", "upskilling"],
    "saas": ["saas", "software as a service", "b2b software", "platform", "enterprise software"],
    "logistics": ["logistics", "supply chain", "fleet", "delivery", "shipping", "warehousing"],
    "gaming": ["game", "gaming", "unity", "unreal", "mobile game"],
    "media": ["media", "content", "streaming", "entertainment", "ott", "news"],
    "hrtech": ["hr", "hrms", "payroll", "recruitment", "talent", "workforce"],
    "proptech": ["real estate", "property", "proptech", "realty"],
    "agritech": ["agriculture", "farm", "agri", "crop"],
}

# Seniority level patterns
SENIORITY_PATTERNS = {
    "junior": ["junior", "fresher", "entry level", "entry-level", "0-2 years", "1-2 years", "graduate"],
    "mid": ["mid", "mid-level", "intermediate", "2-5 years", "3-5 years", "3-6 years"],
    "senior": ["senior", "sr.", "sr ", "5+ years", "5-8 years", "6-8 years", "experienced"],
    "lead": ["lead", "tech lead", "team lead", "principal", "8+ years", "8-12 years"],
    "manager": ["manager", "engineering manager", "director", "head of", "vp of", "vice president"],
}


def normalize_skill(skill: str) -> str:
    return skill.lower().strip()


def skills_match(candidate_skill: str, required_skill: str) -> bool:
    cs = normalize_skill(candidate_skill)
    rs = normalize_skill(required_skill)
    if cs == rs:
        return True
    # Check synonyms
    for canonical, synonyms in SKILL_SYNONYMS.items():
        all_variants = [canonical] + synonyms
        if cs in all_variants and rs in all_variants:
            return True
    # Substring match
    if rs in cs or cs in rs:
        return True
    return False


def compute_skills_overlap(candidate_skills: list, required_skills: list) -> tuple[list, list, float]:
    matched = []
    missing = []
    if not required_skills:
        return [], [], 0.5
    for req_skill in required_skills:
        found = False
        for cand_skill in candidate_skills:
            if skills_match(cand_skill, req_skill):
                matched.append(req_skill)
                found = True
                break
        if not found:
            missing.append(req_skill)
    score = len(matched) / len(required_skills) if required_skills else 0.5
    return matched, missing, score


def compute_experience_score(candidate_exp: float, job_exp_min: float, job_exp_max: float) -> float:
    if candidate_exp is None:
        return 0.5
    if job_exp_min is None and job_exp_max is None:
        return 0.7
    if job_exp_min is None:
        job_exp_min = 0
    if job_exp_max is None:
        job_exp_max = job_exp_min + 10

    if candidate_exp < job_exp_min:
        gap = job_exp_min - candidate_exp
        return max(0, 1.0 - gap * 0.15)
    elif candidate_exp > job_exp_max + 5:
        return 0.6  # Overqualified
    elif candidate_exp > job_exp_max:
        return 0.8
    else:
        return 1.0


def compute_freshness_score(last_active: datetime) -> float:
    if last_active is None:
        return 0.4
    days_ago = (datetime.utcnow() - last_active).days
    if days_ago <= 7:
        return 1.0
    elif days_ago <= 30:
        return 0.9
    elif days_ago <= 90:
        return 0.7
    elif days_ago <= 180:
        return 0.5
    elif days_ago <= 365:
        return 0.3
    else:
        return 0.1


def compute_location_score(candidate_location: str, job_location: str) -> float:
    if not candidate_location or not job_location:
        return 0.6
    cl = candidate_location.lower()
    jl = job_location.lower()
    if "remote" in jl or "anywhere" in jl:
        return 1.0
    if cl == jl:
        return 1.0
    # Same city partial match
    cl_words = set(cl.replace(",", " ").split())
    jl_words = set(jl.replace(",", " ").split())
    overlap = cl_words.intersection(jl_words)
    if overlap:
        return 0.9
    # Delhi NCR grouping
    ncr_cities = {"delhi", "noida", "gurgaon", "gurugram", "faridabad", "ghaziabad", "ncr"}
    if cl_words.intersection(ncr_cities) and jl_words.intersection(ncr_cities):
        return 0.95
    # Willing to relocate indicator
    if "relocate" in cl:
        return 0.75
    return 0.5


def compute_salary_score(candidate_expected: float, job_min: float, job_max: float) -> float:
    if candidate_expected is None or (job_min is None and job_max is None):
        return 0.7
    if job_min is None:
        job_min = 0
    if job_max is None:
        job_max = job_min * 1.5
    if job_min <= candidate_expected <= job_max:
        return 1.0
    elif candidate_expected < job_min:
        return 0.9  # Under budget - good
    else:
        overshoot = (candidate_expected - job_max) / job_max
        return max(0.2, 1.0 - overshoot * 0.8)


def compute_domain_score(candidate: dict, job: dict) -> float:
    job_domain = (job.get("domain") or "").lower()
    if not job_domain:
        return 0.6
    # Check candidate's work history and summary for domain keywords
    candidate_text = " ".join([
        candidate.get("summary", "") or "",
        candidate.get("resume_text", "") or "",
        candidate.get("current_company", "") or "",
        " ".join([w.get("company", "") or "" for w in (candidate.get("work_history") or [])]),
    ]).lower()
    domain_kws = DOMAIN_KEYWORDS.get(job_domain, [job_domain])
    matches = sum(1 for kw in domain_kws if kw in candidate_text)
    if matches >= 2:
        return 1.0
    elif matches == 1:
        return 0.7
    return 0.4


def compute_seniority_score(candidate_exp: float, job: dict) -> float:
    if not candidate_exp:
        return 0.5
    parsed = job.get("parsed_requirements") or {}
    seniority = (parsed.get("seniority_level") or "").lower()
    # Map seniority to experience ranges
    seniority_exp_map = {
        "junior": (0, 3),
        "mid": (3, 6),
        "senior": (5, 10),
        "lead": (8, 15),
        "manager": (8, 20),
    }
    if seniority in seniority_exp_map:
        min_exp, max_exp = seniority_exp_map[seniority]
        if min_exp <= candidate_exp <= max_exp:
            return 1.0
        gap = min(abs(candidate_exp - min_exp), abs(candidate_exp - max_exp))
        return max(0.3, 1.0 - gap * 0.1)
    return 0.7


def compute_talent_score(candidate: dict, job: dict) -> dict:
    """
    Compute TalentScore 0-100 with breakdown.
    Weights: skills 28%, experience 22%, domain 18%, seniority 14%, freshness 8%, location 6%, salary 4%
    """
    weights = {
        "skills": 0.28,
        "experience": 0.22,
        "domain": 0.18,
        "seniority": 0.14,
        "freshness": 0.08,
        "location": 0.06,
        "salary": 0.04,
    }

    # Override weights if job has custom weights
    if job.get("talent_score_weights"):
        custom = job["talent_score_weights"]
        total = sum(custom.values())
        weights = {k: v / total for k, v in custom.items()}

    required_skills = job.get("skills_required") or []
    candidate_skills = candidate.get("skills") or []
    matched_skills, missing_skills, skills_score = compute_skills_overlap(candidate_skills, required_skills)

    experience_score = compute_experience_score(
        candidate.get("experience_years"),
        job.get("experience_min"),
        job.get("experience_max"),
    )

    last_active = candidate.get("last_active")
    if isinstance(last_active, str):
        try:
            last_active = datetime.fromisoformat(last_active.replace("Z", "+00:00"))
        except Exception:
            last_active = None
    freshness_score = compute_freshness_score(last_active)

    location_score = compute_location_score(
        candidate.get("location"),
        job.get("location"),
    )

    salary_score = compute_salary_score(
        candidate.get("salary_expected"),
        job.get("salary_min"),
        job.get("salary_max"),
    )

    domain_score = compute_domain_score(candidate, job)
    seniority_score = compute_seniority_score(candidate.get("experience_years"), job)

    component_scores = {
        "skills": skills_score,
        "experience": experience_score,
        "domain": domain_score,
        "seniority": seniority_score,
        "freshness": freshness_score,
        "location": location_score,
        "salary": salary_score,
    }

    weighted_sum = sum(component_scores[k] * weights[k] for k in weights)
    final_score = round(weighted_sum * 100, 1)

    breakdown_pct = {k: round(v * weights[k] * 100 / weighted_sum if weighted_sum > 0 else 0, 1)
                     for k, v in component_scores.items()}

    explanation = generate_score_explanation(
        candidate, job, final_score, component_scores, matched_skills, missing_skills
    )

    return {
        "score": final_score,
        "breakdown": {k: round(v * 100, 1) for k, v in component_scores.items()},
        "explanation": explanation,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
    }


def generate_score_explanation(candidate: dict, job: dict, score: float,
                                 components: dict, matched: list, missing: list) -> str:
    name = candidate.get("name", "Candidate")
    role = job.get("title", "this role")
    exp = candidate.get("experience_years", 0)
    location = candidate.get("location", "unknown")

    parts = []
    if components["skills"] >= 0.8:
        parts.append(f"Strong skill alignment ({len(matched)} of {len(job.get('skills_required', []))} required skills matched)")
    elif components["skills"] >= 0.5:
        parts.append(f"Partial skill match ({len(matched)} matched, missing: {', '.join(missing[:3])})")
    else:
        parts.append(f"Limited skill overlap (key gaps: {', '.join(missing[:3]) if missing else 'N/A'})")

    if components["experience"] >= 0.9:
        parts.append(f"ideal experience ({exp} yrs)")
    elif components["experience"] >= 0.6:
        parts.append(f"acceptable experience ({exp} yrs)")
    else:
        parts.append(f"experience mismatch ({exp} yrs vs required {job.get('experience_min', 'N/A')}-{job.get('experience_max', 'N/A')} yrs)")

    if components["location"] >= 0.8:
        parts.append(f"location match ({location})")
    else:
        parts.append(f"location mismatch (candidate in {location})")

    if components["freshness"] >= 0.8:
        parts.append("recently active")

    return f"{name} scores {score}/100 for {role}. {'. '.join(parts).capitalize()}."


def parse_jd_with_regex(jd_text: str) -> dict:
    """Regex-based JD parsing fallback when Groq is unavailable."""
    jd_lower = jd_text.lower()

    # Extract skills
    common_skills = [
        "python", "java", "javascript", "typescript", "react", "angular", "vue", "node.js",
        "spring boot", "django", "fastapi", "flask", "aws", "azure", "gcp", "docker",
        "kubernetes", "sql", "postgresql", "mysql", "mongodb", "redis", "kafka",
        "machine learning", "deep learning", "tensorflow", "pytorch", "scikit-learn",
        "data science", "power bi", "tableau", "salesforce", "sap", "selenium",
        "cypress", "jest", "flutter", "react native", "swift", "kotlin",
        "c#", ".net", "go", "rust", "scala", "r", "matlab",
        "microservices", "rest api", "graphql", "ci/cd", "git", "agile", "scrum",
        "jira", "linux", "bash", "terraform", "ansible",
    ]
    found_skills = [s for s in common_skills if s in jd_lower]

    # Extract experience
    exp_patterns = [
        r"(\d+)\s*[-–to]+\s*(\d+)\s*years?",
        r"minimum\s+(\d+)\s*\+?\s*years?",
        r"(\d+)\s*\+\s*years?",
        r"(\d+)\s*years?\s+of\s+experience",
    ]
    exp_min, exp_max = None, None
    for pattern in exp_patterns:
        match = re.search(pattern, jd_lower)
        if match:
            groups = match.groups()
            if len(groups) >= 2 and groups[1]:
                exp_min = float(groups[0])
                exp_max = float(groups[1])
            else:
                exp_min = float(groups[0])
                exp_max = exp_min + 4
            break

    # Extract location
    locations = ["bangalore", "mumbai", "delhi", "pune", "hyderabad", "chennai",
                 "kolkata", "noida", "gurgaon", "ahmedabad", "remote", "hybrid"]
    found_location = next((loc.title() for loc in locations if loc in jd_lower), None)

    # Detect domain
    found_domain = "saas"
    for domain, keywords in DOMAIN_KEYWORDS.items():
        if any(kw in jd_lower for kw in keywords):
            found_domain = domain
            break

    # Detect seniority
    found_seniority = "mid"
    for seniority, patterns in SENIORITY_PATTERNS.items():
        if any(p in jd_lower for p in patterns):
            found_seniority = seniority
            break

    # Extract salary
    salary_pattern = r"(\d+)\s*[-–to]+\s*(\d+)\s*l(?:pa|akh)"
    salary_match = re.search(salary_pattern, jd_lower)
    salary_min, salary_max = None, None
    if salary_match:
        salary_min = float(salary_match.group(1))
        salary_max = float(salary_match.group(2))

    return {
        "required_skills": found_skills[:10],
        "nice_to_have_skills": found_skills[10:15] if len(found_skills) > 10 else [],
        "experience_min": exp_min,
        "experience_max": exp_max,
        "domain": found_domain,
        "seniority_level": found_seniority,
        "implied_requirements": [],
        "salary_range_min": salary_min,
        "salary_range_max": salary_max,
        "location": found_location,
    }


async def parse_jd(jd_text: str) -> dict:
    """Parse job description using Groq API with regex fallback."""
    from app.config import settings

    if not settings.GROQ_API_KEY:
        logger.info("GROQ_API_KEY not set, using regex-based JD parsing")
        return parse_jd_with_regex(jd_text)

    try:
        from groq import Groq
        client = Groq(api_key=settings.GROQ_API_KEY)

        prompt = f"""You are an expert technical recruiter. Analyze this job description and extract structured information.

JOB DESCRIPTION:
{jd_text[:3000]}

Return a JSON object with exactly these fields:
{{
  "required_skills": ["skill1", "skill2", ...],
  "nice_to_have_skills": ["skill1", ...],
  "experience_min": <number or null>,
  "experience_max": <number or null>,
  "domain": "<fintech|healthtech|ecommerce|edtech|saas|logistics|gaming|media|hrtech|proptech|other>",
  "seniority_level": "<junior|mid|senior|lead|manager>",
  "implied_requirements": ["requirement1", ...],
  "salary_range_min": <number in LPA or null>,
  "salary_range_max": <number in LPA or null>,
  "location": "<city name or remote or hybrid or null>"
}}

Return ONLY the JSON, no explanation."""

        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=1000,
        )

        content = response.choices[0].message.content.strip()
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return parse_jd_with_regex(jd_text)

    except Exception as e:
        logger.error(f"Groq JD parsing failed: {e}")
        return parse_jd_with_regex(jd_text)


async def compute_talent_score_async(candidate: dict, job: dict) -> dict:
    """Async wrapper with optional Groq explanation."""
    result = compute_talent_score(candidate, job)

    from app.config import settings
    if settings.GROQ_API_KEY and result["score"] > 60:
        try:
            explanation = await generate_groq_explanation(candidate, job, result)
            result["explanation"] = explanation
        except Exception as e:
            logger.warning(f"Groq explanation failed: {e}")

    return result


async def generate_groq_explanation(candidate: dict, job: dict, score_result: dict) -> str:
    """Generate rich explanation using Groq."""
    from app.config import settings
    from groq import Groq

    client = Groq(api_key=settings.GROQ_API_KEY)
    prompt = f"""You are a senior technical recruiter. Write a 2-3 sentence explanation of why this candidate scores {score_result['score']}/100 for this role.

CANDIDATE: {candidate.get('name')}, {candidate.get('experience_years')} years exp, {candidate.get('current_role')} at {candidate.get('current_company')}
SKILLS: {', '.join((candidate.get('skills') or [])[:8])}
LOCATION: {candidate.get('location')}

JOB: {job.get('title')} at {job.get('company')}
REQUIRED SKILLS: {', '.join((job.get('skills_required') or [])[:8])}
EXPERIENCE: {job.get('experience_min')}-{job.get('experience_max')} years
LOCATION: {job.get('location')}

MATCHED SKILLS: {', '.join(score_result.get('matched_skills', [])[:5])}
MISSING SKILLS: {', '.join(score_result.get('missing_skills', [])[:3])}

Write a concise, specific recruiter note. No bullet points."""

    response = client.chat.completions.create(
        model=settings.GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=200,
    )
    return response.choices[0].message.content.strip()


async def generate_outreach_email(candidate: dict, job: dict, tone: str = "professional") -> dict:
    """Generate personalized outreach email."""
    from app.config import settings

    candidate_name = candidate.get("name", "")
    first_name = candidate_name.split()[0] if candidate_name else "there"
    job_title = job.get("title", "")
    company = job.get("company", "")
    location = job.get("location", "")
    salary_min = job.get("salary_min")
    salary_max = job.get("salary_max")

    salary_str = ""
    if salary_min and salary_max:
        salary_str = f"₹{salary_min:.0f}-{salary_max:.0f} LPA"
    elif salary_max:
        salary_str = f"up to ₹{salary_max:.0f} LPA"

    if settings.GROQ_API_KEY:
        try:
            from groq import Groq
            client = Groq(api_key=settings.GROQ_API_KEY)

            prompt = f"""Write a personalized recruitment email for an Indian software professional.

CANDIDATE: {candidate_name}
CURRENT ROLE: {candidate.get('current_role', 'N/A')} at {candidate.get('current_company', 'N/A')}
SKILLS: {', '.join((candidate.get('skills') or [])[:5])}

JOB: {job_title} at {company}
LOCATION: {location or 'India'}
SALARY: {salary_str or 'Competitive'}
TONE: {tone}

Write a short, compelling email (150-200 words) that:
1. Personalizes based on their background
2. Mentions the specific role and company
3. Highlights relevant aspects
4. Has a clear CTA
5. Is professional yet friendly (Indian corporate style)

Format as:
SUBJECT: <subject line>
BODY:
<email body>"""

            response = client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400,
            )
            content = response.choices[0].message.content.strip()
            subject_match = re.search(r'SUBJECT:\s*(.+)', content)
            body_match = re.search(r'BODY:\s*\n(.*)', content, re.DOTALL)

            subject = subject_match.group(1).strip() if subject_match else f"Exciting {job_title} Opportunity at {company}"
            body = body_match.group(1).strip() if body_match else content

            return {"subject": subject, "body": body}

        except Exception as e:
            logger.error(f"Groq email generation failed: {e}")

    # Template fallback
    subject = f"Exciting {job_title} Opportunity at {company} | {salary_str}"
    body = f"""Hi {first_name},

I hope this message finds you well. I came across your profile and was impressed by your experience in {', '.join((candidate.get('skills') or ['software development'])[:2])}.

I'm reaching out about an exciting {job_title} opportunity at {company}{' in ' + location if location else ''}. This role is a great match for your background as a {candidate.get('current_role', 'software professional')}.

Key highlights:
- Role: {job_title}
- Company: {company}
- Location: {location or 'India'}{chr(10) + '- Compensation: ' + salary_str if salary_str else ''}
- Notice period considered: Your current notice period is acceptable

Would you be open to a quick 15-minute call this week to discuss further?

Looking forward to connecting.

Best regards,
TalentRadar Recruitment Team"""

    return {"subject": subject, "body": body}


def expand_job_query(job: dict) -> list:
    """Expand job skills/keywords with synonyms and related terms."""
    skills = job.get("skills_required") or []
    expanded = list(skills)

    for skill in skills:
        skill_lower = skill.lower()
        for canonical, synonyms in SKILL_SYNONYMS.items():
            if skill_lower == canonical or skill_lower in synonyms:
                expanded.extend(synonyms)
                expanded.append(canonical)
                break

    # Add domain-related terms
    domain = (job.get("domain") or "").lower()
    if domain in DOMAIN_KEYWORDS:
        expanded.extend(DOMAIN_KEYWORDS[domain][:3])

    # Deduplicate
    seen = set()
    result = []
    for item in expanded:
        if item.lower() not in seen:
            seen.add(item.lower())
            result.append(item)

    return result[:20]


def generate_candidate_brief(candidate: dict, job: dict) -> str:
    """Generate a 1-page candidate brief for client submission."""
    score_data = compute_talent_score(candidate, job)
    score = score_data["score"]
    matched = score_data["matched_skills"]

    work_history = candidate.get("work_history") or []
    work_history_text = ""
    for w in work_history[:3]:
        work_history_text += f"  - {w.get('role', 'N/A')} at {w.get('company', 'N/A')} ({w.get('duration', 'N/A')})\n"

    education = candidate.get("education") or []
    edu_text = ""
    for e in education[:2]:
        edu_text += f"  - {e.get('degree', 'N/A')} from {e.get('institution', 'N/A')} ({e.get('year', 'N/A')})\n"

    brief = f"""
=== CANDIDATE BRIEF - TALENTRADAR AI ===

CANDIDATE: {candidate.get('name', 'N/A')}
TALENT SCORE: {score}/100 for {job.get('title')} at {job.get('company')}

CONTACT:
  Email: {candidate.get('email', 'N/A')}
  Phone: {candidate.get('phone', 'N/A')}
  Location: {candidate.get('location', 'N/A')}
  LinkedIn: {candidate.get('linkedin_url', 'N/A')}
  GitHub: {candidate.get('github_url', 'N/A')}

CURRENT STATUS:
  Role: {candidate.get('current_role', 'N/A')} at {candidate.get('current_company', 'N/A')}
  Experience: {candidate.get('experience_years', 'N/A')} years
  Current CTC: ₹{candidate.get('salary_current', 'N/A')} LPA
  Expected CTC: ₹{candidate.get('salary_expected', 'N/A')} LPA
  Notice Period: {candidate.get('notice_period', 'N/A')} days

SKILLS (Matched for this role):
  Matched: {', '.join(matched[:8])}
  All Skills: {', '.join((candidate.get('skills') or [])[:12])}

WORK HISTORY:
{work_history_text or '  N/A'}

EDUCATION:
{edu_text or '  N/A'}

SUMMARY:
  {candidate.get('summary', 'N/A')}

AI ASSESSMENT:
  {score_data['explanation']}

---
Generated by TalentRadar AI Platform | Confidential
"""
    return brief.strip()
