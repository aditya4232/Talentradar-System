"""
GitHub Scraper - Uses official GitHub REST API (free, no auth required for public data)
Rate limit: 10 req/min unauthenticated, 30/min with token
"""

import httpx
import asyncio
import logging
import re
from datetime import datetime
from typing import Optional

from app.services.scrapers.base import BaseScraper

logger = logging.getLogger(__name__)

INDIAN_CITIES = [
    "bangalore", "mumbai", "delhi", "pune", "hyderabad", "chennai",
    "kolkata", "noida", "gurgaon", "gurugram", "ahmedabad", "jaipur",
    "kochi", "india", "bengaluru", "new delhi", "ncr",
]

LANGUAGE_TO_SKILLS = {
    "Python": ["Python", "FastAPI", "Django", "Flask", "NumPy", "Pandas"],
    "JavaScript": ["JavaScript", "Node.js", "React", "Vue", "Express"],
    "TypeScript": ["TypeScript", "Node.js", "React", "Angular"],
    "Java": ["Java", "Spring Boot", "Maven", "JUnit"],
    "Go": ["Go", "Golang", "gRPC", "Docker"],
    "Rust": ["Rust", "WebAssembly", "Systems Programming"],
    "C#": ["C#", ".NET", "ASP.NET", "Azure"],
    "Ruby": ["Ruby", "Rails", "RSpec"],
    "Kotlin": ["Kotlin", "Android", "JVM"],
    "Swift": ["Swift", "iOS", "Xcode"],
    "Dart": ["Dart", "Flutter", "Mobile Development"],
    "Shell": ["Bash", "Linux", "DevOps", "CI/CD"],
    "Dockerfile": ["Docker", "DevOps", "Containers", "Kubernetes"],
    "HCL": ["Terraform", "Infrastructure as Code", "AWS", "DevOps"],
}


class GitHubScraper(BaseScraper):
    SOURCE_NAME = "github"
    BASE_URL = "https://api.github.com"

    def __init__(self):
        super().__init__()
        from app.config import settings
        self.token = settings.GITHUB_TOKEN
        self.session_headers = {
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            self.session_headers["Authorization"] = f"Bearer {self.token}"

    def _is_indian(self, location: str) -> bool:
        if not location:
            return False
        loc_lower = location.lower()
        return any(city in loc_lower for city in INDIAN_CITIES)

    async def search_users(self, query: str, per_page: int = 30) -> list:
        """Search GitHub users by query."""
        url = f"{self.BASE_URL}/search/users"
        params = {
            "q": query,
            "per_page": min(per_page, 30),
            "sort": "followers",
            "order": "desc",
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.session_headers,
                    timeout=15.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("items", [])
                elif response.status_code == 403:
                    logger.warning("GitHub API rate limit reached")
                    return []
                else:
                    logger.error(f"GitHub search failed: {response.status_code}")
                    return []
        except Exception as e:
            logger.error(f"GitHub search error: {e}")
            return []

    async def get_user_profile(self, username: str) -> Optional[dict]:
        """Get detailed user profile."""
        url = f"{self.BASE_URL}/users/{username}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers=self.session_headers,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
                return None
        except Exception as e:
            logger.error(f"GitHub profile fetch error for {username}: {e}")
            return None

    async def get_user_repos(self, username: str) -> list:
        """Get user's top repositories."""
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {"per_page": 10, "sort": "stars", "direction": "desc"}
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    params=params,
                    headers=self.session_headers,
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return response.json()
                return []
        except Exception:
            return []

    def extract_skills_from_repos(self, repos: list) -> list:
        """Extract skills from repository languages."""
        skills = set()
        for repo in repos:
            lang = repo.get("language")
            if lang and lang in LANGUAGE_TO_SKILLS:
                skills.update(LANGUAGE_TO_SKILLS[lang])
            # Extract from topics
            topics = repo.get("topics", [])
            for topic in topics:
                topic_title = topic.replace("-", " ").title()
                skills.add(topic_title)
        return list(skills)[:15]

    def estimate_experience(self, profile: dict) -> float:
        """Estimate years of experience from GitHub account age and activity."""
        created_at = profile.get("created_at", "")
        if created_at:
            try:
                created = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                years = (datetime.now(created.tzinfo) - created).days / 365
                # Cap reasonable estimate
                return min(round(years * 0.85, 1), 20.0)
            except Exception:
                pass
        return 3.0

    def build_candidate_profile(self, profile: dict, repos: list) -> dict:
        """Build candidate profile from GitHub data."""
        skills = self.extract_skills_from_repos(repos)

        # Get primary language from repos
        lang_counts = {}
        for repo in repos:
            lang = repo.get("language")
            if lang:
                lang_counts[lang] = lang_counts.get(lang, 0) + 1
        primary_lang = max(lang_counts, key=lang_counts.get) if lang_counts else None
        if primary_lang and primary_lang not in [s.split()[0] for s in skills]:
            skills.insert(0, primary_lang)

        # Build LinkedIn URL hint from blog/website
        blog = profile.get("blog", "") or ""
        linkedin_url = None
        if "linkedin.com" in blog.lower():
            linkedin_url = blog

        # Estimate salary from followers and repos (rough heuristic for demo)
        followers = profile.get("followers", 0)
        public_repos = profile.get("public_repos", 0)
        exp_years = self.estimate_experience(profile)

        base_salary = 5.0
        if exp_years > 7:
            base_salary = 20.0
        elif exp_years > 4:
            base_salary = 12.0
        elif exp_years > 2:
            base_salary = 8.0

        if followers > 100:
            base_salary *= 1.3
        if public_repos > 50:
            base_salary *= 1.1

        current_salary = round(base_salary, 1)
        expected_salary = round(base_salary * 1.25, 1)

        username = profile.get("login", "")
        name = profile.get("name") or username

        return {
            "name": name,
            "email": profile.get("email"),
            "current_role": profile.get("bio") or (f"Software Developer ({primary_lang})" if primary_lang else "Software Developer"),
            "current_company": profile.get("company", "").replace("@", "").strip() if profile.get("company") else None,
            "experience_years": exp_years,
            "skills": skills,
            "location": profile.get("location"),
            "github_url": f"https://github.com/{username}",
            "linkedin_url": linkedin_url,
            "sources": ["github"],
            "salary_current": current_salary,
            "salary_expected": expected_salary,
            "summary": f"GitHub developer with {public_repos} public repos and {followers} followers. "
                       f"Primary languages: {', '.join(list(lang_counts.keys())[:3])}",
            "last_active": datetime.utcnow(),
            "freshness_score": 0.9,
            "work_history": [],
            "education": [],
        }

    async def scrape(self, keywords: str, location: str = "India", limit: int = 50) -> list:
        """Scrape GitHub users matching keywords in India."""
        candidates = []
        skills_list = [k.strip() for k in keywords.split(",")]

        # Build queries for GitHub search
        queries = []
        for skill in skills_list[:3]:
            queries.append(f"location:India language:{skill}")
            queries.append(f"location:India {skill} in:bio")

        # Also search by Indian cities
        for city in ["Bangalore", "Mumbai", "Pune", "Hyderabad", "Delhi"][:2]:
            queries.append(f"location:{city} {skills_list[0]} followers:>10")

        seen_usernames = set()

        for query in queries[:4]:
            if len(candidates) >= limit:
                break

            await self.rate_limit()
            users = await self.search_users(query, per_page=min(20, limit - len(candidates)))

            for user in users:
                username = user.get("login")
                if not username or username in seen_usernames:
                    continue
                seen_usernames.add(username)

                await asyncio.sleep(0.5)

                profile = await self.get_user_profile(username)
                if not profile:
                    continue

                # Filter for Indian developers
                user_location = profile.get("location", "")
                if not self._is_indian(user_location) and "India" in location:
                    continue

                repos = await self.get_user_repos(username)
                candidate = self.build_candidate_profile(profile, repos)
                candidates.append(candidate)

                if len(candidates) >= limit:
                    break

        logger.info(f"GitHub scraper found {len(candidates)} candidates for '{keywords}'")
        return candidates


class MockGitHubScraper(GitHubScraper):
    """GitHub scraper that uses mock data when rate limited."""

    async def scrape(self, keywords: str, location: str = "India", limit: int = 50) -> list:
        """Try real GitHub first, fall back to mock if needed."""
        try:
            real_results = await super().scrape(keywords, location, min(limit, 15))
            if real_results:
                return real_results
        except Exception as e:
            logger.warning(f"Real GitHub scrape failed: {e}, using mock data")

        # Return empty - mock_data.py will fill in
        return []
