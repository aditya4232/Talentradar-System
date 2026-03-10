import requests
from typing import List, Dict
import time


class StackOverflowSearch:
    """Stack Overflow API for finding developers"""
    
    def __init__(self):
        self.base_url = "https://api.stackexchange.com/2.3"
        self.site = "stackoverflow"
    
    def search_developers(self, skills: List[str], location: str = "Hyderabad", 
                         min_reputation: int = 100, max_results: int = 20) -> List[Dict]:
        """
        Search for developers on Stack Overflow by skills and location
        
        Args:
            skills: List of skill tags (python, javascript, etc.)
            location: Location to filter by
            min_reputation: Minimum reputation score
            max_results: Maximum number of results
        """
        candidates = []
        
        # Search by tags (skills)
        for skill in skills[:3]:  # Top 3 skills to avoid rate limits
            try:
                users = self._search_users_by_tag(skill, location, min_reputation, max_results // 3)
                candidates.extend(users)
                time.sleep(0.1)  # Rate limit friendly
            except Exception as e:
                print(f"Error searching Stack Overflow for {skill}: {e}")
                continue
        
        # Remove duplicates by user_id
        seen_ids = set()
        unique_candidates = []
        for candidate in candidates:
            if candidate.get('user_id') not in seen_ids:
                seen_ids.add(candidate['user_id'])
                unique_candidates.append(candidate)
        
        return unique_candidates[:max_results]
    
    def _search_users_by_tag(self, tag: str, location: str, min_reputation: int, 
                            max_results: int) -> List[Dict]:
        """Search users who answer questions with specific tag"""
        
        # First, get top answerers for this tag
        url = f"{self.base_url}/tags/{tag}/top-answerers/all_time"
        params = {
            'site': self.site,
            'pagesize': max_results,
            'filter': 'default'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data:
                return []
            
            # Get detailed user info
            user_ids = [str(user['user']['user_id']) for user in data['items'][:max_results]]
            if not user_ids:
                return []
            
            return self._get_user_details(user_ids, location, min_reputation)
            
        except Exception as e:
            print(f"Error fetching top answerers for {tag}: {e}")
            return []
    
    def _get_user_details(self, user_ids: List[str], location_filter: str, 
                         min_reputation: int) -> List[Dict]:
        """Get detailed information for specific users"""
        
        url = f"{self.base_url}/users/{';'.join(user_ids)}"
        params = {
            'site': self.site,
            'filter': '!9_bDDxJY5'  # Includes profile, location, website
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data:
                return []
            
            candidates = []
            for user in data['items']:
                # Filter by reputation
                if user.get('reputation', 0) < min_reputation:
                    continue
                
                # Filter by location (case insensitive, partial match)
                user_location = user.get('location', '').lower()
                if location_filter.lower() not in user_location and user_location:
                    # If location specified but doesn't match, skip
                    # But include if no location specified
                    if user_location:
                        continue
                
                candidate = self._format_candidate(user)
                candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            print(f"Error fetching user details: {e}")
            return []
    
    def _format_candidate(self, user: Dict) -> Dict:
        """Format Stack Overflow user to candidate format"""
        
        # Extract name
        name = user.get('display_name', 'Unknown')
        
        # Build bio from reputation and badges
        reputation = user.get('reputation', 0)
        badge_counts = user.get('badge_counts', {})
        gold = badge_counts.get('gold', 0)
        silver = badge_counts.get('silver', 0)
        bronze = badge_counts.get('bronze', 0)
        
        bio_parts = [f"Stack Overflow developer with {reputation:,} reputation"]
        if gold or silver or bronze:
            bio_parts.append(f"Badges: {gold} gold, {silver} silver, {bronze} bronze")
        
        # Get location
        location = user.get('location', None)
        
        # Get website/GitHub
        website = user.get('website_url', None)
        github_url = None
        portfolio_url = None
        
        if website:
            if 'github.com' in website.lower():
                github_url = website
            else:
                portfolio_url = website
        
        # Stack Overflow profile
        so_profile = user.get('link', None)
        
        # Extract skills from top tags (if available)
        skills = []
        if 'top_tags' in user:
            skills = user['top_tags'][:10]
        
        # Estimate experience based on account age and reputation
        experience_years = 1
        if 'creation_date' in user:
            from datetime import datetime
            creation_date = datetime.fromtimestamp(user['creation_date'])
            account_age_years = (datetime.now() - creation_date).days / 365
            experience_years = max(1, min(int(account_age_years), int(reputation // 5000)))
        
        candidate = {
            'name': name,
            'email': None,
            'location': location,
            'skills': skills,
            'bio': ' | '.join(bio_parts),
            'github_url': github_url,
            'linkedin_url': None,
            'portfolio_url': portfolio_url or so_profile,
            'source': 'stackoverflow',
            'reputation': reputation,
            'user_id': user.get('user_id'),
            'experience_years': int(experience_years),
            'open_to_work': False  # Can't determine from SO
        }
        
        return candidate
    
    def search_by_location(self, location: str, max_results: int = 30) -> List[Dict]:
        """Search developers by location only"""
        
        url = f"{self.base_url}/users"
        params = {
            'site': self.site,
            'pagesize': max_results,
            'min': 500,  # Minimum reputation
            'sort': 'reputation',
            'order': 'desc',
            'filter': '!9_bDDxJY5'
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'items' not in data:
                return []
            
            # Filter by location
            candidates = []
            for user in data['items']:
                user_location = user.get('location', '').lower()
                if location.lower() in user_location:
                    candidate = self._format_candidate(user)
                    candidates.append(candidate)
            
            return candidates
            
        except Exception as e:
            print(f"Error searching by location: {e}")
            return []
