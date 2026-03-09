import asyncio
import random
import re
import time
from ..database import SessionLocal
from ..models import Candidate
from .llm_parser import extract_candidates_from_text, compute_talent_score
from .httpx_scraper import httpx_scrape
from .job_api_scraper import fetch_all_apis
from .indian_job_scrapers import fetch_all_indian_sources

# PROXY LIST - ADD YOURS HERE (Example: "http://user:pass@host:port")
PROXIES = [] 

# Search queries - FOCUSED ON DATA ENGINEER & AI ENGINEER IN HYDERABAD
SEARCH_QUERIES = [
    # PRIMARY TARGET: Data Engineer & AI Engineer variations
    "data engineer hyderabad",
    "ai engineer hyderabad",
    "data engineer telangana",
    "ai engineer telangana",
    "machine learning engineer hyderabad",
    "data scientist hyderabad",
    "mlops engineer hyderabad",
    "big data engineer hyderabad",
    "analytics engineer hyderabad",
    "artificial intelligence engineer hyderabad",
    
    # Generic variations (for remote jobs)
    "data engineer",
    "ai engineer",
    "machine learning engineer",
    "data scientist",
    "mlops engineer",
    "ml engineer",
    "deep learning engineer",
    "ai ml engineer",
    "data analytics engineer",
    "big data developer",
    
    # Related skills/stacks for comprehensive coverage
    "python data engineer",
    "spark engineer",
    "etl developer",
    "aws data engineer",
    "azure data engineer",
    "nlp engineer",
    "computer vision engineer",
    "pytorch engineer",
    "tensorflow engineer",
    "data pipeline engineer",
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
        "last_update": time.time()
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
        print("[ScrapingEngine] Starting continuous scrape loop...")
        
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
                print(f"[ScrapingEngine] --- Cycle: query='{query}' ---")

                # Engine 1: Free Job APIs (structured JSON, most reliable)
                ScrapingManager.update_progress(f"APIs: {query}", "Job APIs")
                try:
                    api_results = await fetch_all_apis(query)
                    if api_results:
                        saved = await ScrapingManager.save_candidates(api_results, source="API")
                        ScrapingManager.update_progress(f"APIs: {query}", "Job APIs", saved)
                        print(f"[ScrapingEngine] APIs returned {len(api_results)} entries, saved {saved} new")
                except Exception as e:
                    print(f"[ScrapingEngine] API engine error: {e}")

                await asyncio.sleep(random.randint(3, 8))

                # Engine 2: Indian Job Board Scrapers (Naukri, Foundit, Instahyre, Wellfound, Cutshort)
                ScrapingManager.update_progress(f"Indian Boards: {query}", "Indian Job Scrapers")
                try:
                    indian_results = await fetch_all_indian_sources(query)
                    if indian_results:
                        saved = await ScrapingManager.save_candidates(indian_results, source="IndianBoard")
                        ScrapingManager.update_progress(f"Indian Boards: {query}", "Indian Job Scrapers", saved)
                        print(f"[ScrapingEngine] Indian job boards returned {len(indian_results)} entries, saved {saved} new")
                except Exception as e:
                    print(f"[ScrapingEngine] Indian job board scraper error: {e}")

                await asyncio.sleep(random.randint(5, 10))

                # Engine 3: Playwright for a specific known-accessible URL
                accessible_targets = [
                    (f"https://www.timesjobs.com/candidate/job-search.html?searchType=personalised&from=submit&txtKeywords={query.replace(' ', '+')}&txtLocation=India", "TimesJobs"),
                ]
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
                        print(f"[ScrapingEngine] Scraping error for {source_name}: {e}")
                    await asyncio.sleep(random.randint(10, 20))

                if not (ScrapingManager.SCRAPING_ACTIVE or ScrapingManager.SCHEDULING_CONFIG["enabled"]):
                    break

                print(f"[ScrapingEngine] Cycle complete. Resting before next query...")
                await asyncio.sleep(30)  # Short rest between queries
        except Exception as e:
            print(f"[ScrapingEngine] Loop Error: {e}")
            ScrapingManager.SCRAPING_ACTIVE = False
        finally:
            ScrapingManager.TASK_RUNNING = False
            ScrapingManager.update_progress("Idle", "None")

    @staticmethod
    async def scrape_url(url: str):
        """Advanced 2026 Stealth Scrape with Proxy and AI Parsing.
        Uses sync Playwright in a thread to avoid Python 3.14 asyncio subprocess issues."""
        print(f"\n[Scraper] [SAFE] Target URL: {url}")
        
        proxy_url = ScrapingManager.get_proxy()
        
        def _sync_scrape():
            """Run Playwright synchronously (called from executor thread)."""
            from playwright.sync_api import sync_playwright
            from playwright_stealth import Stealth
            
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
                Stealth().apply_stealth(page)
                
                print(f"[Scraper] Navigating...")
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                import time as _time
                _time.sleep(random.randint(3, 7))
                
                raw_text = page.evaluate("document.body.innerText")
                page_title = page.title()
                browser.close()
                return raw_text, page_title
        
        try:
            loop = asyncio.get_event_loop()
            raw_text, page_title = await loop.run_in_executor(None, _sync_scrape)
            
            # Identify source
            source = "Web"
            if "naukri.com" in url.lower(): source = "Naukri"
            elif "linkedin.com" in url.lower(): source = "LinkedIn"
            elif "indeed.com" in url.lower(): source = "Indeed"
            elif "timesjobs.com" in url.lower(): source = "TimesJobs"
            elif "foundit.in" in url.lower(): source = "Foundit"
            
            # AI Parsing
            candidates_data = await extract_candidates_from_text(
                raw_text=raw_text, 
                source=source,
                page_title=page_title,
                url=url
            )
            
            # Save
            if candidates_data:
                saved = await ScrapingManager.save_candidates(candidates_data, source)
                ScrapingManager.update_progress(url, f"Stealth ({source})", saved)
                return len(candidates_data)
            return 0
        except Exception as e:
            print(f"[Scraper] [CRITICAL] {e}")
            return 0

    @staticmethod
    async def save_candidates(candidates_data: list[dict], source: str):
        """Helper to process and save candidates to DB. Returns count of NEW candidates saved."""
        db = SessionLocal()
        saved = 0
        try:
            for c_data in candidates_data:
                name = c_data.get("name", "").strip()
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

                # Score
                c_data["talent_score"] = compute_talent_score(c_data)
                
                # De-dup by name + source
                existing = db.query(Candidate).filter(
                    Candidate.name == name, 
                    Candidate.source == c_data["source"]
                ).first()
                if existing:
                    for k, v in c_data.items():
                        if v and k != "id":
                            setattr(existing, k, v)
                else:
                    valid = {k: v for k, v in c_data.items() if hasattr(Candidate, k) and v is not None}
                    db.add(Candidate(**valid))
                    saved += 1
            db.commit()
            print(f"[Scraper] [OK] Saved {saved} new candidates from {source}")
            return saved
        except Exception as de:
            print(f"[Scraper] [DB ERR] {de}")
            db.rollback()
            return 0
        finally:
            db.close()
