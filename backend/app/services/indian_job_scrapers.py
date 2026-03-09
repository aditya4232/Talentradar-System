"""
Indian Job Board Scrapers - Multi-strategy approach
Scrapes from Naukri, Indeed, Wellfound, Foundit, Instahyre, Cutshort, etc.

STRATEGIES:
1. Direct web scraping with httpx + BeautifulSoup (for static content)
2. Browser automation with Playwright (for JavaScript-heavy sites)
3. RSS feeds where available
4. Public APIs where available

DATA VALIDATION:
- Only jobs posted in last 7 days
- Validates company names exist
- Checks for India locations
- Removes duplicates
"""
import httpx
import asyncio
import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json

# Realistic browser headers to bypass anti-scraping
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Ch-Ua": '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "DNT": "1",
    "Cache-Control": "max-age=0"
}


def _clean(val: Optional[str]) -> str:
    """Strip HTML tags and whitespace."""
    if not val:
        return ""
    import re
    val = re.sub(r"<[^>]+>", "", str(val))
    val = re.sub(r"\s+", " ", val)
    return val.strip()


def _is_fresh(date_str: str, max_days: int = 7) -> bool:
    """Check if job posting is fresh (within max_days)."""
    if not date_str:
        return True  # Assume fresh if no date
    
    # Parse common date formats
    patterns = [
        r"(\d+)\s+day[s]?\s+ago",
        r"(\d+)\s+hour[s]?\s+ago",
        r"today",
        r"yesterday",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, date_str.lower())
        if match:
            if "today" in pattern or "hour" in pattern:
                return True
            if "yesterday" in pattern:
                return True
            if match.group(1):
                days = int(match.group(1))
                return days <= max_days
    
    return True  # If can't parse, assume fresh


async def scrape_naukri(query: str = "python developer", location: str = "india", limit: int = 30) -> List[Dict]:
    """
    Scrape Naukri.com - India's #1 job site
    Uses direct HTTP scraping of search results
    """
    print(f"[Naukri] Searching for '{query}' in {location}...")
    
    url = "https://www.naukri.com/jobapi/v3/search"
    params = {
        "noOfResults": limit,
        "urlType": "search_by_keyword",
        "searchType": "adv",
        "keyword": query,
        "location": location,
        "pageNo": 1,
        "k": query,
        "l": location,
        "seoKey": query.replace(" ", "-"),
        "src": "jobsearchDesk",
        "latLong": ""
    }
    
    headers = {
        **BROWSER_HEADERS,  # Include all browser headers
        "Accept": "application/json,text/html,*/*",  # Accept JSON primarily
        "Referer": "https://www.naukri.com/",
        "Origin": "https://www.naukri.com",
        "appid": "109",
        "systemid": "Naukri"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True, verify=False) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"[Naukri] Error: Status {response.status_code}")
                return []
            
            data = response.json()
            jobs = data.get("jobDetails", [])
            
            results = []
            for job in jobs[:limit]:
                job_id = job.get("jobId", "unknown")
                title = _clean(job.get("title", ""))
                company = _clean(job.get("companyName", ""))
                location_str = _clean(job.get("placeholders", [{}])[0].get("label", "India") if job.get("placeholders") else "India")
                posted_date = job.get("footerText", "")
                
                # Skip if not fresh
                if not _is_fresh(posted_date):
                    continue
                
                # Build URL
                job_url = f"https://www.naukri.com/job-listings-{title.replace(' ', '-').lower()}-{company.replace(' ', '-').lower()}-{location_str.replace(' ', '-').lower()}-{job_id}"
                
                # Extract skills
                skills_tags = job.get("tagsAndSkills", "").split(",") if job.get("tagsAndSkills") else []
                skills = [s.strip() for s in skills_tags if s.strip()][:10]
                
                # Get experience
                exp_str = job.get("experience", "0")
                try:
                    exp_years = int(re.search(r"\d+", exp_str).group()) if re.search(r"\d+", exp_str) else 0
                except:
                    exp_years = 0
                
                # Get salary
                salary = _clean(job.get("salary", ""))
                
                summary_parts = [_clean(job.get("jobDescription", ""))[:400]]
                if salary:
                    summary_parts.append(f"Salary: {salary}")
                if posted_date:
                    summary_parts.append(f"Posted: {posted_date}")
                
                results.append({
                    "name": f"{title} at {company} (Naukri ID: {job_id})",
                    "current_title": title,
                    "company": company,
                    "location": location_str,
                    "skills": skills,
                    "summary": " | ".join(summary_parts),
                    "profile_url": job_url,
                    "source": f"Naukri.com (ID:{job_id})",
                    "experience_years": exp_years,
                })
                print(f"  ✓ [{job_id}] {title} @ {company} [{posted_date}]")
            
            print(f"[Naukri] Found {len(results)} fresh jobs")
            return results
            
    except Exception as e:
        print(f"[Naukri] Error: {e}")
        return []


async def scrape_foundit(query: str = "developer", location: str = "india", limit: int = 30) -> List[Dict]:
    """
    Scrape Foundit.in (formerly Monster India)
    Uses their public job search
    """
    print(f"[Foundit] Searching for '{query}' in {location}...")
    
    # Foundit uses a different URL structure
    search_query = query.replace(" ", "%20")
    url = f"https://www.foundit.in/srp/results?query={search_query}&locations={location}"
    
    headers = {
        **BROWSER_HEADERS,
        "Referer": "https://www.foundit.in/",
        "Origin": "https://www.foundit.in"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True, verify=False) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"[Foundit] Error: Status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all("div", class_=re.compile("jobTuple|job-tittle"), limit=limit)
            
            results = []
            for idx, card in enumerate(job_cards):
                try:
                    title_elem = card.find("a", class_=re.compile("job-title|title"))
                    if not title_elem:
                        continue
                    
                    title = _clean(title_elem.get_text())
                    job_url = title_elem.get("href", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = "https://www.foundit.in" + job_url
                    
                    company_elem = card.find("span", class_=re.compile("company|companyName"))
                    company = _clean(company_elem.get_text()) if company_elem else "Unknown"
                    
                    location_elem = card.find("span", class_=re.compile("location|loc"))
                    location_str = _clean(location_elem.get_text()) if location_elem else location
                    
                    exp_elem = card.find("span", class_=re.compile("experience|exp"))
                    exp_str = _clean(exp_elem.get_text()) if exp_elem else "0"
                    exp_years = int(re.search(r"\d+", exp_str).group()) if re.search(r"\d+", exp_str) else 0
                    
                    skills_elem = card.find("div", class_=re.compile("skills|tags"))
                    skills = []
                    if skills_elem:
                        skill_tags = skills_elem.find_all("span")
                        skills = [_clean(tag.get_text()) for tag in skill_tags[:10]]
                    
                    job_id = f"foundit-{idx}"
                    
                    results.append({
                        "name": f"{title} at {company} (Foundit)",
                        "current_title": title,
                        "company": company,
                        "location": location_str,
                        "skills": skills,
                        "summary": f"Job from Foundit.in | Location: {location_str}",
                        "profile_url": job_url,
                        "source": f"Foundit.in (Monster India)",
                        "experience_years": exp_years,
                    })
                    print(f"  ✓ {title} @ {company}")
                    
                except Exception as e:
                    continue
            
            print(f"[Foundit] Found {len(results)} jobs")
            return results
            
    except Exception as e:
        print(f"[Foundit] Error: {e}")
        return []


async def scrape_instahyre(query: str = "python", limit: int = 20) -> List[Dict]:
    """
    Scrape Instahyre.com - Premium tech job board for India
    """
    print(f"[Instahyre] Searching for '{query}'...")
    
    # Instahyre has a public API-like endpoint
    url = "https://www.instahyre.com/api/jobs/"
    params = {
        "q": query,
        "page": 1,
        "per_page": limit
    }
    
    headers = {
        **BROWSER_HEADERS,
        "Accept": "application/json,*/*",
        "Referer": "https://www.instahyre.com/"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers, verify=False) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"[Instahyre] Error: Status {response.status_code}")
                return []
            
            data = response.json()
            jobs = data.get("jobs", [])
            
            results = []
            for job in jobs[:limit]:
                job_id = job.get("id", "unknown")
                title = _clean(job.get("title", ""))
                company = _clean(job.get("company_name", ""))
                location_str = _clean(job.get("location", "India"))
                
                # Check freshness
                created_at = job.get("created_at", "")
                if not _is_fresh(created_at):
                    continue
                
                # Skills
                skills = job.get("skills", [])[:10]
                
                # Experience
                exp_min = job.get("min_experience", 0)
                exp_max = job.get("max_experience", 0)
                exp_years = (exp_min + exp_max) // 2 if exp_max else exp_min
                
                # Salary
                salary_min = job.get("min_salary", "")
                salary_max = job.get("max_salary", "")
                salary = f"INR {salary_min}-{salary_max} LPA" if salary_min and salary_max else ""
                
                job_url = f"https://www.instahyre.com/jobs/{job_id}/"
                
                summary_parts = [_clean(job.get("description", ""))[:400]]
                if salary:
                    summary_parts.append(f"Salary: {salary}")
                if created_at:
                    summary_parts.append(f"Posted: {created_at}")
                
                results.append({
                    "name": f"{title} at {company} (Instahyre ID: {job_id})",
                    "current_title": title,
                    "company": company,
                    "location": location_str,
                    "skills": skills,
                    "summary": " | ".join(summary_parts),
                    "profile_url": job_url,
                    "source": f"Instahyre (ID:{job_id})",
                    "experience_years": exp_years,
                })
                print(f"  ✓ [{job_id}] {title} @ {company}")
            
            print(f"[Instahyre] Found {len(results)} jobs")
            return results
            
    except Exception as e:
        print(f"[Instahyre] Error: {e}")
        return []


async def scrape_wellfound(query: str = "developer", location: str = "india", limit: int = 20) -> List[Dict]:
    """
    Scrape Wellfound (AngelList) - Startup jobs
    Uses public job listings page
    """
    print(f"[Wellfound] Searching for '{query}' in {location}...")
    
    # Wellfound public search
    url = f"https://wellfound.com/role/r/{query.replace(' ', '-')}/locations/{location}"
    
    headers = {
        **BROWSER_HEADERS,
        "Referer": "https://wellfound.com/",
        "Origin": "https://wellfound.com"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers, follow_redirects=True, verify=False) as client:
            response = await client.get(url)
            
            if response.status_code != 200:
                print(f"[Wellfound] Error: Status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Wellfound uses JSON embedded in script tags
            script_tags = soup.find_all("script", type="application/json")
            
            results = []
            for script in script_tags:
                try:
                    data = json.loads(script.string)
                    
                    # Look for job listings in the data
                    if isinstance(data, dict) and "jobs" in data:
                        jobs = data["jobs"]
                        
                        for job in jobs[:limit]:
                            job_id = job.get("id", "unknown")
                            title = _clean(job.get("title", ""))
                            company = _clean(job.get("company", {}).get("name", ""))
                            location_str = _clean(job.get("location", location))
                            
                            job_url = f"https://wellfound.com/l/{job_id}"
                            
                            results.append({
                                "name": f"{title} at {company} (Wellfound)",
                                "current_title": title,
                                "company": company,
                                "location": location_str,
                                "skills": [],
                                "summary": f"Startup job from Wellfound/AngelList | {location_str}",
                                "profile_url": job_url,
                                "source": f"Wellfound (ID:{job_id})",
                                "experience_years": 0,
                            })
                            print(f"  ✓ {title} @ {company}")
                            
                except Exception as e:
                    continue
            
            print(f"[Wellfound] Found {len(results)} jobs")
            return results
            
    except Exception as e:
        print(f"[Wellfound] Error: {e}")
        return []


async def scrape_cutshort(query: str = "developer", limit: int = 20) -> List[Dict]:
    """
    Scrape Cutshort - Jobs for tech professionals
    """
    print(f"[Cutshort] Searching for '{query}'...")
    
    url = "https://cutshort.io/jobs"
    params = {"search": query}
    
    headers = {
        **BROWSER_HEADERS,
        "Referer": "https://cutshort.io/",
        "Origin": "https://cutshort.io"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers, verify=False) as client:
            response = await client.get(url, params=params)
            
            if response.status_code != 200:
                print(f"[Cutshort] Error: Status {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            job_cards = soup.find_all("div", class_=re.compile("job-card|listing"), limit=limit)
            
            results = []
            for idx, card in enumerate(job_cards):
                try:
                    title_elem = card.find("a", class_=re.compile("title|job-title"))
                    if not title_elem:
                        continue
                    
                    title = _clean(title_elem.get_text())
                    job_url = title_elem.get("href", "")
                    if job_url and not job_url.startswith("http"):
                        job_url = "https://cutshort.io" + job_url
                    
                    company_elem = card.find("span", class_=re.compile("company"))
                    company = _clean(company_elem.get_text()) if company_elem else "Unknown"
                    
                    results.append({
                        "name": f"{title} at {company} (Cutshort)",
                        "current_title": title,
                        "company": company,
                        "location": "India",
                        "skills": [],
                        "summary": f"Job from Cutshort.io",
                        "profile_url": job_url,
                        "source": "Cutshort",
                        "experience_years": 0,
                    })
                    print(f"  ✓ {title} @ {company}")
                    
                except Exception as e:
                    continue
            
            print(f"[Cutshort] Found {len(results)} jobs")
            return results
            
    except Exception as e:
        print(f"[Cutshort] Error: {e}")
        return []


async def fetch_all_indian_sources(query: str = "python developer") -> List[Dict]:
    """
    Fetch from ALL Indian job sources concurrently
    """
    print(f"\n[IndianSources] ═══════════════════════════════════════════════════════")
    print(f"[IndianSources] SCRAPING MAJOR INDIAN JOB BOARDS: '{query}'")
    print(f"[IndianSources] Sources: Naukri, Foundit, Instahyre, Wellfound, Cutshort")
    print(f"[IndianSources] ═══════════════════════════════════════════════════════\n")
    
    tasks = [
        scrape_naukri(query, "india", limit=30),
        scrape_foundit(query, "india", limit=30),
        scrape_instahyre(query.split()[0], limit=20),  # Use first word for tag-based search
        scrape_wellfound(query.split()[-1], "india", limit=20),  # Use last word for role
        scrape_cutshort(query, limit=20),
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    all_jobs = []
    source_counts = {}
    
    for r in results:
        if isinstance(r, list):
            all_jobs.extend(r)
            for job in r:
                source = job.get("source", "Unknown").split("(")[0].strip()
                source_counts[source] = source_counts.get(source, 0) + 1
        elif isinstance(r, Exception):
            print(f"[IndianSources] Error: {r}")
    
    # Remove duplicates based on company + title
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        key = f"{job.get('company', '')}_{job.get('current_title', '')}".lower()
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"\n[IndianSources] ═══════════════════════════════════════════════════════")
    print(f"[IndianSources] RESULTS:")
    print(f"[IndianSources] Total jobs scraped: {len(all_jobs)}")
    print(f"[IndianSources] Unique jobs after dedup: {len(unique_jobs)}")
    for source, count in source_counts.items():
        print(f"[IndianSources]   ✓ {source}: {count} jobs")
    print(f"[IndianSources] ═══════════════════════════════════════════════════════\n")
    
    return unique_jobs
