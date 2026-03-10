import asyncio
import random
import re
import time
from ..constants import JOB_PORTAL_KEYWORDS
from ..database import SessionLocal
from ..models import Candidate
from ..utils.contact_extraction import normalize_contact_info
from ..utils.deduplication import find_and_mark_duplicates, generate_profile_hash
from ..utils.lead_scoring import (
    classify_source_reliability,
    compute_contactability_score,
    is_outreach_ready,
)
from ..utils.logging_config import scraper_logger as logger, PerformanceLogger
from .httpx_scraper import httpx_scrape
from .llm_parser import extract_candidates_from_text, compute_talent_score
from ..config import settings

# PROXY LIST - ADD YOURS HERE (Example: "http://user:pass@host:port")
PROXIES = []

def is_job_portal_lead(source: str | None, profile_url: str | None) -> bool:
    """Return True when entry appears to come from a real job-application portal."""
    source_text = (source or "").lower()
    url_text = (profile_url or "").lower()

    if any(keyword in source_text for keyword in JOB_PORTAL_KEYWORDS):
        return True

    if any(keyword in url_text for keyword in JOB_PORTAL_KEYWORDS):
        return True

    return False


def is_candidate_profile_lead(c_data: dict) -> bool:
    """Strictly accept candidate/profile leads and reject job posting links."""
    profile_url = (c_data.get("profile_url") or c_data.get("url") or "").lower()
    source = (c_data.get("source") or "").lower()
    summary = (c_data.get("summary") or c_data.get("raw_text") or "").lower()

    if not is_job_portal_lead(source, profile_url):
        return False

    # Reject clear job-posting pages.
    job_url_markers = [
        "/job", "/jobs", "job-listing", "job-description", "careers", "vacancy", "hiring",
        "apply", "jobid", "search?", "results?",
    ]
    if any(marker in profile_url for marker in job_url_markers):
        return False

    # Prefer clear profile URL patterns.
    profile_markers = [
        "/in/", "/profile", "/profiles", "/candidate", "/candidates", "/resume", "/u/", "/user/"
    ]
    if any(marker in profile_url for marker in profile_markers):
        return True

    # Fallback: direct contact details indicate candidate-level lead.
    has_contact = bool(c_data.get("email") or c_data.get("phone"))
    if has_contact and not any(term in summary for term in ["job description", "responsibilities", "apply now"]):
        return True

    return False

# Platform Training Memory (ML Base)
PLATFORM_SUCCESS_RATES = {
    "linkedin": 0.85,
    "github": 0.90,
    "naukri": 0.70,
    "instahyre": 0.75,
    "wellfound": 0.80,
    "foundit": 0.65,
}

SEARCH_QUERIES = [
    # AI-Optimized Skill Queries
    "data engineer hyderabad",
    "ai engineer hyderabad",
    "machine learning bangalore",
    "python developer india resume",
    "react engineer lead mumbai",
    "software architect cloud bangalore",
    "devops engineer terraform",
    "full stack developer remote india",
]

class ScrapingManager:
    SCRAPING_ACTIVE = False
    TASK_RUNNING = False
    SCHEDULING_CONFIG = {
        "enabled": False,
        "interval_minutes": 60,
        "last_run": 0
    }
    PROGRESS = {
        "current_target": "Idle",
        "candidates_found": 0,
        "engine": "None",
        "last_update": time.time(),
        "target_count": 0
    }
    active_tasks = {}
    
    @staticmethod
    def get_proxy():
        if PROXIES:
            return random.choice(PROXIES)
        return None

    @staticmethod
    def update_progress(target, engine, found_inc=0):
        ScrapingManager.PROGRESS["current_target"] = target
        ScrapingManager.PROGRESS["engine"] = engine
        ScrapingManager.PROGRESS["candidates_found"] += found_inc
        ScrapingManager.PROGRESS["last_update"] = time.time()

    @staticmethod
    async def run_continuous_scrape():
        """Background loop: fetches from Job APIs (primary) + Playwright (for user URLs)."""
        if ScrapingManager.TASK_RUNNING:
            return
        ScrapingManager.TASK_RUNNING = True
        logger.info("🚀 Starting continuous scrape loop...")
        
        query_idx = 0
        
        try:
            while ScrapingManager.SCRAPING_ACTIVE or ScrapingManager.SCHEDULING_CONFIG["enabled"]:
                # If only scheduling is enabled, check if it's time
                if not ScrapingManager.SCRAPING_ACTIVE and ScrapingManager.SCHEDULING_CONFIG["enabled"]:
                    now = time.time()
                    elapsed = (now - ScrapingManager.SCHEDULING_CONFIG["last_run"]) / 60
                    if elapsed < ScrapingManager.SCHEDULING_CONFIG["interval_minutes"]:
                        ScrapingManager.update_progress("Waiting for next schedule", "Scheduler")
                        await asyncio.sleep(60)
                        continue
                
                ScrapingManager.SCHEDULING_CONFIG["last_run"] = time.time()
                query = SEARCH_QUERIES[query_idx % len(SEARCH_QUERIES)]
                query_idx += 1
                logger.info(f"📡 Cycle: query='{query}'")

                # Engine: Playwright Stealth via Smart X-Ray Web Dorks
                import urllib.parse
                accessible_targets = []
                platforms: list[str] = []
                location: str = "India"
                # AI-Ranked Platforms based on Training Memory
                sorted_platforms = sorted(
                    PLATFORM_SUCCESS_RATES.items(), 
                    key=lambda x: x[1], 
                    reverse=True
                )
                recommended = [p for p, rate in sorted_platforms if rate > 0.7]
                
                # Keep only proven candidate/profile-oriented sources.
                for p in (pl_lower if pl_lower else recommended):
                    dork = ""
                    if p == "linkedin":
                        dork = f'site:linkedin.com/in/ "{query}" "{location}"'
                    elif p == "github":
                        dork = f'site:github.com "{query}" "{location}"'
                    else:
                        dork = f'site:{p}.com "{query}" "{location}" resume OR profile'
                        # Skip unsupported sources instead of generating generic noisy links.
                        continue
                        
                    enc = urllib.parse.quote(dork)
                    ddg_url = f"https://html.duckduckgo.com/html/?q={enc}"
                    accessible_targets.append((ddg_url, p.capitalize()))

                for target_url, source_name in accessible_targets:
                    if not (ScrapingManager.SCRAPING_ACTIVE or ScrapingManager.SCHEDULING_CONFIG["enabled"]):
                        break
                    ScrapingManager.update_progress(target_url, f"Scraping {source_name}")
                    try:
                        # Try httpx first (works for server-rendered sites)
                        c_data = await httpx_scrape(target_url, source=source_name)
                        if c_data:
                            saved = await ScrapingManager.save_candidates(c_data, source=source_name)
                            ScrapingManager.update_progress(target_url, f"Httpx ({source_name})", saved)
                        else:
                            # Fallback to Playwright (sync via thread for Python 3.14 compat)
                            ScrapingManager.update_progress(target_url, "Playwright Stealth")
                            found = await ScrapingManager.scrape_url(target_url)
                            ScrapingManager.update_progress(target_url, "Playwright Stealth", found or 0)
                    except Exception as e:
                        logger.error(f"❌ Scraping error for {source_name}: {e}", exc_info=True)
                    await asyncio.sleep(random.randint(10, 20))

                if not (ScrapingManager.SCRAPING_ACTIVE or ScrapingManager.SCHEDULING_CONFIG["enabled"]):
                    break

                logger.info("🔁 Cycle complete. Resting before next query...")
                await asyncio.sleep(30)  # Short rest between queries
        except Exception as e:
            logger.error(f"❌ Loop Error: {e}", exc_info=True)
            ScrapingManager.SCRAPING_ACTIVE = False
        finally:
            ScrapingManager.TASK_RUNNING = False
            ScrapingManager.update_progress("Idle", "None")
            logger.info("🛑 Scraping loop stopped")

    @staticmethod
    async def run_bulk_scan(target_count: int = 100, query: str = "developer", location: str = "India", platforms: list = None):
        """Bulk scan mode: fetch and persist candidate leads until target count is reached."""
        if ScrapingManager.TASK_RUNNING:
            return
        ScrapingManager.TASK_RUNNING = True
        logger.info(f"🚀 Starting bulk scan: target={target_count} candidates, query='{query}'")

        db = SessionLocal()
        initial_count = db.query(Candidate).count()
        db.close()

        candidates_needed = target_count
        queries_used = []
        query_idx = 0

        try:
            while ScrapingManager.SCRAPING_ACTIVE and candidates_needed > 0:
                db = SessionLocal()
                current_count = db.query(Candidate).count()
                db.close()

                candidates_found = current_count - initial_count
                candidates_needed = target_count - candidates_found

                ScrapingManager.PROGRESS["current_target"] = f"Bulk scan: {candidates_found}/{target_count}"
                ScrapingManager.PROGRESS["candidates_found"] = candidates_found
                ScrapingManager.PROGRESS["last_update"] = time.time()

                if candidates_needed <= 0:
                    logger.info(f"✅ Bulk scan complete: {candidates_found}/{target_count} candidates")
                    break

                search_query = query
                if query_idx > 0:
                    base_query_idx = query_idx % len(SEARCH_QUERIES)
                    search_query = SEARCH_QUERIES[base_query_idx]
                    if location.lower() not in search_query.lower() and location.lower() != "india":
                        search_query = f"{search_query} {location}"

                queries_used.append(search_query)
                query_idx += 1
                logger.info(f"📡 Bulk scan query #{query_idx}: '{search_query}' ({candidates_needed} more needed)")

                # Candidate-only bulk path: profile-oriented DDG dorks + URL scraping.
                import urllib.parse
                targets = []
                for platform in (platforms if platforms else ["linkedin", "github"]):
                    if platform == "linkedin":
                        dork = f'site:linkedin.com/in/ "{search_query}" "{location}"'
                    elif platform == "github":
                        dork = f'site:github.com "{search_query}" "{location}"'
                    else:
                        dork = f'site:{platform}.com "{search_query}" "{location}" resume OR profile'
                    targets.append((f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(dork)}", platform.capitalize()))

                for target_url, source_name in targets:
                    if not ScrapingManager.SCRAPING_ACTIVE:
                        break
                    ScrapingManager.update_progress(target_url, f"Bulk Scraping {source_name}")
                    try:
                        c_data = await httpx_scrape(target_url, source=source_name)
                        if c_data:
                            saved = await ScrapingManager.save_candidates(c_data, source=source_name)
                        else:
                            found = await ScrapingManager.scrape_url(target_url)
                            saved = found or 0
                        ScrapingManager.update_progress(target_url, f"Bulk Scraping {source_name}", saved)
                    except Exception as e:
                        logger.error(f"❌ Bulk profile scrape failed for {source_name}: {e}", exc_info=True)
                    await asyncio.sleep(random.randint(2, 5))

                if query_idx >= 20:
                    logger.warning("⚠️ Reached query limit (20). Stopping bulk scan.")
                    break

            db = SessionLocal()
            final_count = db.query(Candidate).count()
            db.close()

            total_found = final_count - initial_count
            logger.info(f"🎉 Bulk scan finished: {total_found} candidates added (target was {target_count})")
            logger.info(f"📊 Queries used: {len(queries_used)}")

            ScrapingManager.PROGRESS["current_target"] = f"Complete: {total_found}/{target_count}"
            ScrapingManager.PROGRESS["candidates_found"] = total_found

        except Exception as e:
            logger.error(f"❌ Bulk scan error: {e}", exc_info=True)
        finally:
            ScrapingManager.TASK_RUNNING = False
            ScrapingManager.SCRAPING_ACTIVE = False
            ScrapingManager.update_progress("Idle", "None")
            logger.info("🛑 Bulk scan stopped")

    @staticmethod
    async def scrape_url(url: str):
        """Advanced 2026 Stealth Scrape with Proxy and AI Parsing.
        Uses linkedin-scraper for LinkedIn URLs and sync Playwright thread for others."""
        print(f"\n[Scraper] [SAFE] Target URL: {url}")
        
        # SPECIAL HANDLING FOR LINKEDIN
        if "linkedin.com/in/" in url.lower() and settings.linkedin_email:
            try:
                def _linkedin_scrape():
                    from linkedin_scraper import Person, actions
                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options
                    
                    options = Options()
                    options.add_argument("--headless")
                    options.add_argument("--no-sandbox")
                    options.add_argument("--disable-dev-shm-usage")
                    driver = webdriver.Chrome(options=options)
                    
                    try:
                        actions.login(driver, settings.linkedin_email, settings.linkedin_password)
                        person = Person(url, driver=driver)
                        return person
                    finally:
                        driver.quit()

                loop = asyncio.get_event_loop()
                person = await loop.run_in_executor(None, _linkedin_scrape)
                
                if person:
                        candidate_data = {
                            "name": person.name if person.name else "LinkedIn Candidate",
                            "current_title": "Professional",
                            "company": "Unknown",
                            "location": person.location if person.location else "India",
                            "source": "LinkedIn (Verified)",
                            "profile_url": url,
                            "skills": [],
                            "summary": "",
                            "experience_years": 0.0
                        }
                        
                        # Use safer access for person object attributes
                        try:
                            if hasattr(person, 'job_title') and person.job_title:
                                candidate_data["current_title"] = person.job_title[:100]
                            if hasattr(person, 'company') and person.company:
                                candidate_data["company"] = person.company[:100]
                            if hasattr(person, 'skills') and person.skills:
                                candidate_data["skills"] = [getattr(s, 'name', str(s)) for s in person.skills]
                            if hasattr(person, 'about') and person.about:
                                candidate_data["summary"] = person.about
                        except Exception as attr_err:
                            logger.warning(f"Error extracting some LinkedIn attributes: {attr_err}")

                        saved = await ScrapingManager.save_candidates([candidate_data], "LinkedIn")
                        return saved
            except Exception as e:
                logger.error(f"[Scraper] [LinkedIn-SDK] Error: {e}")
                # Fallback to standard scraper below
        
        proxy_url = ScrapingManager.get_proxy()
        
        def _sync_scrape():
            """Run Playwright synchronously (called from executor thread)."""
            from playwright.sync_api import sync_playwright

            proxy_config = {"server": proxy_url} if proxy_url else None
            ua = f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(120, 125)}.0.0.0 Safari/537.36"

            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    proxy=proxy_config,
                    args=["--no-sandbox", "--disable-blink-features=AutomationControlled"]
                )
                context = browser.new_context(viewport={"width": 1920, "height": 1080}, user_agent=ua)
                page = context.new_page()

                # Optional stealth: keep scraper functional even when playwright_stealth is unavailable.
                try:
                    from playwright_stealth import Stealth
                    stealth = Stealth()
                    if hasattr(stealth, "apply_stealth_sync"):
                        stealth.apply_stealth_sync(page)
                    elif hasattr(stealth, "apply_stealth"):
                        stealth.apply_stealth(page)
                except Exception:
                    pass

                print(f"[Scraper] Navigating...")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                import time as _time
                _time.sleep(random.randint(3, 7))

                raw_text = page.evaluate("document.documentElement.innerHTML")
                page_title = page.title()
                browser.close()
                return raw_text, page_title
        
        try:
            loop = asyncio.get_event_loop()
            raw_text, page_title = await loop.run_in_executor(None, _sync_scrape)
            
            # 1. AI EXTRACTION (Groq LLM) - NEW GOLD STANDARD
            print(f"[Scraper] [AI] Attempting AI parsing with Groq...")
            from .llm_parser import extract_candidates_from_text
            try:
                ai_leads = await extract_candidates_from_text(raw_text, source=source, page_title=page_title, url=url)
                if ai_leads:
                    # Map AI output to database schema
                    formatted_leads = []
                    for lead in ai_leads:
                        # Ensure profile URL is valid
                        profile_url = lead.get("profile_url")
                        if not profile_url or profile_url == "Unknown" or not profile_url.startswith("http"):
                           profile_url = url # fallback to page URL
                        
                        formatted_leads.append({
                            "name": lead.get("name", "Potential Candidate"),
                            "email": lead.get("email"),
                            "phone": lead.get("phone"),
                            "profile_url": profile_url,
                            "source": lead.get("source", source),
                            "current_title": lead.get("current_title", "Professional"),
                            "company": lead.get("company", "Independent"),
                            "location": lead.get("location", "India"),
                            "experience_years": float(lead.get("experience_years", 0)) if lead.get("experience_years") else 0.0,
                            "skills": lead.get("skills", []),
                            "summary": lead.get("summary", ""),
                            "talent_score": float(lead.get("talent_score", 50)) if lead.get("talent_score") else 50.0
                        })
                    
                    if formatted_leads:
                        saved_count = await ScrapingManager.save_candidates(formatted_leads, source)
                        print(f"[Scraper] [AI] Successfully extracted {saved_count} candidates from {source}")
                        return saved_count
            except Exception as ai_err:
                logger.error(f"[Scraper] [AI] Extraction failed: {ai_err}")

            # 2. HEURISTIC FALLBACK (If AI fails or returns nothing)
            # Identify source
            source = "Web"
            if "linkedin.com" in url.lower(): source = "LinkedIn"
            elif "naukri.com" in url.lower(): source = "Naukri"
            elif "instahyre.com" in url.lower(): source = "Instahyre"
            elif "foundit.in" in url.lower() or "foundit.com" in url.lower(): source = "Foundit"
            
# Extract using BeautifulSoup heuristics first
            from bs4 import BeautifulSoup
            import urllib.parse
            import re
            
            soup = BeautifulSoup(raw_text, 'html.parser')
            blocks = soup.select('div[class*="card"], div[class*="profile"], div[class*="candidate"], div[class*="user"], li, article')
            if not blocks:
                blocks = soup.find_all('div')
                
            email_pattern = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
            phone_pattern = re.compile(r'(?:(?:\+|0{0,2})91(\s*[\-]\s*)?|[0]?)?[6789]\d{9}')
            
            candidates_found = []
            for block in blocks:
                text = block.get_text(separator=' ', strip=True)
                if len(text) < 20: continue
                
                emails = list(set(email_pattern.findall(text)))
                phones = list(set(phone_pattern.findall(text)))
                
                name_elem = block.find(['h1', 'h2', 'h3', 'h4', 'strong'])
                name = name_elem.get_text(strip=True) if name_elem else "Unknown Candidate"
                
                candidate_link = None
                for a_tag in block.find_all('a', href=True):
                    href_lower = a_tag['href'].lower()
                    if any(bad in href_lower for bad in ['/job', '/company', '/careers', '/apply', 'about', 'privacy', 'login']):
                        continue
                    if any(good in href_lower for good in ['profile', 'user', 'candidate', 'resume', '/in/', 'portfolio']):
                        candidate_link = a_tag['href']
                        break
                    if not candidate_link:
                        candidate_link = a_tag['href']
                        
                if not candidate_link and not (emails or phones): continue
                
                full_link = urllib.parse.urljoin(url, candidate_link) if candidate_link else url
                is_profile = candidate_link and any(x in candidate_link.lower() for x in ['profile', 'user', 'candidate', '/in/'])
                
                if emails or phones or is_profile:
                    candidates_found.append({
                        "name": name[:100] if len(name) > 2 else "Potential Candidate",
                        "company": "N/A",
                        "title": "Candidate Profile" if not name else name[:100],
                        "location": "Unknown",
                        "source": source,
                        "url": full_link,
                        "email": emails[0] if emails else None,
                        "phone": phones[0] if phones else None,
                        "skills": [],
                        "raw_text": text[:500]
                    })
                    
            unique_candidates = list({c['url']: c for c in candidates_found}.values())
            
            # DUCKDUCKGO specific parsing fallback
            if not candidates_found and "duckduckgo.com" in url.lower():
                print("[Heuristic] DuckDuckGo results detected, extracting candidate profiles...")
                ddg_results = soup.select('.result__body')
                for res in ddg_results:
                    title_elem = res.select_one('.result__title a')
                    snippet_elem = res.select_one('.result__snippet')
                    if title_elem:
                        link = title_elem.get('href', '')
                        if 'uddg=' in link:
                            # Extract clean DDG redirect
                            enc_url = link.split('uddg=')[1].split('&')[0]
                            link = urllib.parse.unquote(enc_url)
                            
                        # Ignore common job boards if they are just generic job searches, but allow if it looks like a profile
                        if any(bad in link.lower() for bad in ['/jobs/', '/job/', '/career', '/company/', 'search']):
                            continue
                            
                        name = title_elem.get_text(strip=True)
                        snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                        
                        source_platform = "Web"
                        if "linkedin.com/in/" in link: source_platform = "LinkedIn"
                        elif "github.com" in link: source_platform = "GitHub"
                        elif "naukri.com" in link: source_platform = "Naukri (Resumes)"
                        elif "instahyre.com" in link: source_platform = "Instahyre (Resumes)"
                        
                        emails = list(set(email_pattern.findall(snippet)))
                        phones = list(set(phone_pattern.findall(snippet)))
                        
                        # Try to extract title/company from the snippet roughly
                        title_str = name.split("-")[1].strip() if " - " in name else "Professional"
                        company_str = "Independent"
                        if " at " in snippet:
                            company_str = snippet.split(" at ")[1].split(".")[0].split(",")[0].strip()
                        
                        candidates_found.append({
                            "name": name.split("-")[0].replace("LinkedIn", "").replace("|", "").strip()[:100],
                            "company": company_str[:100],
                            "current_title": title_str[:100],
                            "location": "India",
                            "source": source_platform,
                            "profile_url": link,
                            "skills": [],
                            "summary": snippet,
                            "talent_score": 65.0,
                            "email": emails[0] if emails else None,
                            "phone": phones[0] if phones else None,
                            "raw_text": snippet[:500]
                        })
                unique_candidates = list({c['profile_url'] if 'profile_url' in c else c.get('url'): c for c in candidates_found}.values())

            # AI Fallback if heuristic completely fails mapping
            if not unique_candidates:
                print(f"[Heuristic] 0 exact profiles found. Falling back to LLM...")
                clean_text = soup.get_text(separator=' ', strip=True)
                candidates_data = await extract_candidates_from_text(
                    raw_text=clean_text,
                    source=source,
                    page_title=page_title,
                    url=url
                )
            else:
                print(f"[Heuristic] Found {len(unique_candidates)} explicit profiles!")
                candidates_data = unique_candidates
            
            # Save
            if candidates_data:
                saved = await ScrapingManager.save_candidates(candidates_data, source)
                ScrapingManager.update_progress(url, f"Stealth ({source})", saved)
                return len(candidates_data)
            return 0
        except Exception as e:
            logger.error(f"[Scraper] [CRITICAL] {e}", exc_info=True)
            return 0

    @staticmethod
    async def save_candidates(candidates_data: list[dict], source: str):
        """
        Helper to process and save candidates to DB with professional enhancements.
        
        Features:
        - Contact extraction from text
        - Deduplication with fuzzy matching
        - Profile hash generation
        - Returns count of NEW candidates saved.
        """
        db = SessionLocal()
        saved = 0
        duplicates_found = 0
        
        try:
            for c_data in candidates_data:
                name = c_data.get("name", "").strip()
                
                # IMPORTANT: Map url to profile_url to ensure exact profile links are saved
                c_data["profile_url"] = c_data.get("url", c_data.get("profile_url", ""))
                
                # IMPORTANT: Map fields accurately 
                if "title" in c_data and "current_title" not in c_data:
                    c_data["current_title"] = c_data["title"]
                if "raw_text" in c_data and "summary" not in c_data:
                    c_data["summary"] = c_data["raw_text"]
                
                # Reject junk entries
                if not name or len(name) < 3:
                    continue
                junk_names = {"save", "apply", "login", "sign up", "register", "access denied",
                              "403 forbidden", "error", "none", "n/a", "unknown"}
                if name.lower() in junk_names:
                    continue
                
                # Clean Experience
                exp = c_data.get("experience_years", 0)
                if isinstance(exp, str):
                    nums = re.findall(r'\d+', exp)
                    exp = sum(map(float, nums))/len(nums) if nums else 0.0
                try:
                    exp = float(exp) if exp else 0.0
                except (ValueError, TypeError):
                    exp = 0.0
                c_data["experience_years"] = exp

                # Clean skills - ensure list
                skills = c_data.get("skills", [])
                if isinstance(skills, str):
                    skills = [s.strip() for s in skills.split(",") if s.strip()]
                c_data["skills"] = skills

                # Use the source from data if present, otherwise the parameter
                c_data["source"] = c_data.get("source", source)

                # Keep only candidate/profile leads (exclude job posting links).
                if not is_candidate_profile_lead(c_data):
                    logger.debug(f"⏭️ Skipped non-candidate lead: {name} | source={c_data.get('source')} | url={c_data.get('profile_url')}")
                    continue

                # ✅ NEW: Extract contacts from summary/text
                c_data = normalize_contact_info(c_data)
                
                # ✅ NEW: Generate profile hash for deduplication
                c_data["profile_hash"] = generate_profile_hash(c_data)

                # Score
                c_data["talent_score"] = compute_talent_score(c_data)
                c_data["contactability_score"] = compute_contactability_score(
                    c_data.get("email"), c_data.get("phone"), c_data.get("profile_url")
                )
                c_data["source_reliability"] = classify_source_reliability(c_data.get("source"))
                c_data["outreach_ready"] = is_outreach_ready(
                    c_data.get("email"), c_data.get("phone"), c_data.get("profile_url")
                )
                
                # ✅ NEW: Advanced deduplication check
                duplicate_master_id = find_and_mark_duplicates(db, c_data)
                
                if duplicate_master_id:
                    # This is a duplicate, skip creating new record
                    duplicates_found += 1
                    logger.debug(f"⏭️ Duplicate found for '{name}' - merged with record ID {duplicate_master_id}")
                    continue
                
                # De-dup by name + source (legacy check)
                existing = db.query(Candidate).filter(
                    Candidate.name == name, 
                    Candidate.source == c_data["source"]
                ).first()
                
                if existing:
                    # Update existing record
                    for k, v in c_data.items():
                        if v and k != "id":
                            setattr(existing, k, v)
                    logger.debug(f"🔄 Updated existing candidate: {name}")
                else:
                    # Create new record
                    valid = {k: v for k, v in c_data.items() if hasattr(Candidate, k) and v is not None}
                    db.add(Candidate(**valid))
                    saved += 1
                    logger.debug(f"✨ New candidate saved: {name}")
                    
            db.commit()
            
            logger.info(
                f"💾 Saved {saved} new candidates from {source} "
                f"(duplicates skipped: {duplicates_found})"
            )
            return saved
            
        except Exception as de:
            logger.error(f"❌ Database error while saving candidates: {de}", exc_info=True)
            db.rollback()
            return 0
        finally:
            db.close()
