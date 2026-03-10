from typing import List, Dict
from services.skill_extractor import SkillExtractor
from services.google_search import GoogleXRaySearch
from services.github_service import GitHubService
from services.stackoverflow_service import StackOverflowSearch
from services.devto_service import DevToSearch
from services.email_extractor import EmailExtractor
from services.ai_matching import AIMatchingEngine
import json


class RecruitmentEngine:
    """Main recruitment engine that orchestrates all services"""
    
    def __init__(self):
        self.skill_extractor = SkillExtractor()
        self.google_search = GoogleXRaySearch()
        self.github_service = GitHubService()
        self.stackoverflow_search = StackOverflowSearch()
        self.devto_search = DevToSearch()
        self.email_extractor = EmailExtractor()
        self.ai_matcher = AIMatchingEngine()
    
    def find_candidates(
        self, 
        job_description: str, 
        location: str = "Hyderabad",
        limit: int = 20
    ) -> List[Dict]:
        """
        Main pipeline to find candidates for a job description
        
        1. Extract skills from job description
        2. Search Google for profiles
        3. Search GitHub for developers
        4. Extract emails
        5. Match candidates with AI
        6. Return sorted leads
        """
        print(f"\n🔍 Starting candidate search for location: {location}")
        print(f"📝 Job Description: {job_description[:100]}...")
        
        # Step 1: Extract skills
        print("\n1️⃣ Extracting skills from job description...")
        skills = self.skill_extractor.extract_skills(job_description)
        print(f"   Found skills: {skills}")
        
        # Step 2: Google X-Ray Search
        print("\n2️⃣ Performing Google X-Ray search...")
        search_queries = self.google_search.generate_search_queries(skills, location)
        print(f"   Generated {len(search_queries)} search queries")
        
        search_results = self.google_search.search_all_queries(search_queries, results_per_query=3)
        print(f"   Found {len(search_results)} profile links")
        
        # Step 3: GitHub Search
        print("\n3️⃣ Searching GitHub...")
        primary_language = skills[0].title() if skills else "Python"
        github_users = self.github_service.search_users(location, primary_language, limit=10)
        print(f"   Found {len(github_users)} GitHub developers")
        
        # Step 4: Stack Overflow Search
        print("\n4️⃣ Searching Stack Overflow...")
        so_developers = self.stackoverflow_search.search_developers(
            skills=skills,
            location=location,
            min_reputation=500,
            max_results=10
        )
        print(f"   Found {len(so_developers)} Stack Overflow developers")
        
        # Step 5: Dev.to Search
        print("\n5️⃣ Searching Dev.to...")
        devto_developers = self.devto_search.search_developers(
            skills=skills,
            max_results=10
        )
        print(f"   Found {len(devto_developers)} Dev.to developers")
        
        # Step 6: Process and combine candidates
        print("\n6️⃣ Processing candidates...")
        candidates = []
        
        # Process Google search results
        for result in search_results:
            candidate = self._process_search_result(result)
            if candidate:
                candidates.append(candidate)
        
        # Process GitHub users
        for gh_user in github_users:
            candidate = self._process_github_user(gh_user)
            if candidate:
                candidates.append(candidate)
        
        # Process Stack Overflow developers
        for so_dev in so_developers:
            if so_dev:  # Already formatted by StackOverflowSearch
                candidates.append(so_dev)
        
        # Process Dev.to developers
        for devto_dev in devto_developers:
            if devto_dev:  # Already formatted by DevToSearch
                candidates.append(devto_dev)
        
        print(f"   Processed {len(candidates)} unique candidates")
        
        # Step 7: AI Matching
        print("\n7️⃣ Running AI matching...")
        matched_candidates = self.ai_matcher.match_candidates_to_job(
            candidates, 
            job_description, 
            top_k=limit
        )
        
        # Step 8: Format results
        print("\n8️⃣ Formatting results...")
        formatted_leads = []
        for candidate, score in matched_candidates:
            lead = {
                'name': candidate.get('name', 'Unknown'),
                'email': candidate.get('email'),
                'location': candidate.get('location', location),
                'skills': candidate.get('skills', []),
                'github_url': candidate.get('github_url'),
                'linkedin_url': candidate.get('linkedin_url'),
                'portfolio_url': candidate.get('portfolio_url'),
                'bio': candidate.get('bio', ''),
                'open_to_work': candidate.get('open_to_work', False),
                'match_score': round(score, 2),
                'experience_years': candidate.get('experience_years', 0)
            }
            formatted_leads.append(lead)
        
        print(f"\n✅ Found {len(formatted_leads)} qualified candidates!")
        return formatted_leads
    
    def _process_search_result(self, result: Dict) -> Dict:
        """Process a Google search result into candidate data"""
        title = result.get('title', '')
        snippet = result.get('snippet', '')
        link = result.get('link', '')
        
        # Extract information
        combined_text = f"{title} {snippet}"
        
        # Determine profile type
        linkedin_url = link if 'linkedin.com' in link else None
        github_url = link if 'github.com' in link else None
        portfolio_url = link if not linkedin_url and not github_url else None
        
        # Extract name (usually first part of title)
        name = title.split('-')[0].strip() if '-' in title else title.split('|')[0].strip()
        
        # Extract skills
        skills = self.skill_extractor.extract_skills(combined_text)
        
        # Check if open to work
        open_to_work = self.skill_extractor.detect_open_to_work(combined_text)
        
        # Extract experience
        experience_years = self.skill_extractor.extract_experience(combined_text)
        
        # Try to extract email
        emails = self.email_extractor.extract_from_text(combined_text)
        email = emails[0] if emails else None
        
        return {
            'name': name[:100],  # Limit length
            'email': email,
            'location': None,  # Will be inferred
            'skills': skills,
            'github_url': github_url,
            'linkedin_url': linkedin_url,
            'portfolio_url': portfolio_url,
            'bio': snippet[:500],
            'open_to_work': open_to_work,
            'experience_years': experience_years
        }
    
    def _process_github_user(self, gh_user: Dict) -> Dict:
        """Process GitHub user data into candidate format"""
        # Get languages/skills from GitHub
        bio = gh_user.get('bio', '')
        
        # Extract skills from bio
        skills = self.skill_extractor.extract_skills(bio)
        
        # Check if open to work
        open_to_work = self.skill_extractor.detect_open_to_work(bio)
        
        return {
            'name': gh_user.get('name') or gh_user.get('username', 'Unknown'),
            'email': gh_user.get('email'),
            'location': gh_user.get('location'),
            'skills': skills,
            'github_url': gh_user.get('github_url'),
            'linkedin_url': None,
            'portfolio_url': gh_user.get('blog') if gh_user.get('blog') else None,
            'bio': bio,
            'open_to_work': open_to_work,
            'experience_years': 0  # GitHub doesn't provide this
        }
    
    def match_existing_candidates(
        self,
        candidates: List[Dict],
        job_description: str,
        top_k: int = 10
    ) -> List[Dict]:
        """Match existing candidates to a job description"""
        matched = self.ai_matcher.match_candidates_to_job(
            candidates,
            job_description,
            top_k=top_k
        )
        
        results = []
        for candidate, score in matched:
            candidate['match_score'] = round(score, 2)
            results.append(candidate)
        
        return results
