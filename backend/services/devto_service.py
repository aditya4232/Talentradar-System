import requests
from typing import List, Dict
import time


class DevToSearch:
    """Dev.to API for finding developer content creators"""
    
    def __init__(self):
        self.base_url = "https://dev.to/api"
    
    def search_developers(self, skills: List[str], max_results: int = 20) -> List[Dict]:
        """
        Search for developers on Dev.to by searching articles with tags
        
        Args:
            skills: List of skills/tags to search for
            max_results: Maximum number of unique authors to return
        """
        candidates = {}  # Use dict to deduplicate by username
        
        for skill in skills[:3]:  # Top 3 skills
            try:
                authors = self._search_articles_by_tag(skill, max_results)
                for author in authors:
                    username = author.get('username')
                    if username and username not in candidates:
                        candidates[username] = author
                
                if len(candidates) >= max_results:
                    break
                    
                time.sleep(0.2)  # Be nice to API
                
            except Exception as e:
                print(f"Error searching Dev.to for {skill}: {e}")
                continue
        
        return list(candidates.values())[:max_results]
    
    def _search_articles_by_tag(self, tag: str, max_results: int) -> List[Dict]:
        """Search articles by tag and extract unique authors"""
        
        url = f"{self.base_url}/articles"
        params = {
            'tag': tag,
            'per_page': 30,  # Get more articles to find diverse authors
            'top': 7  # Top articles from last week
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()
            
            # Extract unique authors
            seen_users = set()
            candidates = []
            
            for article in articles:
                user = article.get('user', {})
                username = user.get('username')
                
                if username and username not in seen_users:
                    seen_users.add(username)
                    
                    # Get full user profile
                    user_data = self._get_user_profile(username)
                    if user_data:
                        candidates.append(user_data)
                    
                    if len(candidates) >= max_results:
                        break
            
            return candidates
            
        except Exception as e:
            print(f"Error fetching articles for tag {tag}: {e}")
            return []
    
    def _get_user_profile(self, username: str) -> Dict:
        """Get detailed user profile from Dev.to"""
        
        url = f"{self.base_url}/users/by_username"
        params = {'url': username}
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            user_data = response.json()
            
            return self._format_candidate(user_data)
            
        except Exception as e:
            print(f"Error fetching user profile for {username}: {e}")
            return None
    
    def _format_candidate(self, user: Dict) -> Dict:
        """Format Dev.to user to candidate format"""
        
        name = user.get('name', user.get('username', 'Unknown'))
        username = user.get('username', '')
        
        # Build bio
        bio_parts = []
        if user.get('summary'):
            bio_parts.append(user['summary'])
        
        bio_parts.append(f"Dev.to developer/writer")
        
        # Get location
        location = user.get('location', None)
        
        # Get social links
        github_url = user.get('github_username')
        if github_url and not github_url.startswith('http'):
            github_url = f"https://github.com/{github_url}"
        
        twitter = user.get('twitter_username')
        website = user.get('website_url', None)
        
        # Dev.to profile
        devto_profile = f"https://dev.to/{username}"
        
        # Get joined date for experience estimation
        joined_at = user.get('joined_at', '')
        experience_years = 1
        if joined_at:
            try:
                from datetime import datetime
                joined_date = datetime.fromisoformat(joined_at.replace('Z', '+00:00'))
                years_on_platform = (datetime.now(joined_date.tzinfo) - joined_date).days / 365
                experience_years = max(1, int(years_on_platform * 2))  # Estimate
            except:
                pass
        
        candidate = {
            'name': name,
            'email': None,
            'location': location,
            'skills': [],  # Dev.to doesn't expose tags in user profile
            'bio': ' | '.join(bio_parts),
            'github_url': github_url,
            'linkedin_url': None,
            'portfolio_url': website or devto_profile,
            'source': 'devto',
            'username': username,
            'experience_years': experience_years,
            'open_to_work': False
        }
        
        return candidate
    
    def get_trending_authors(self, max_results: int = 20) -> List[Dict]:
        """Get currently trending article authors"""
        
        url = f"{self.base_url}/articles"
        params = {
            'per_page': 50,
            'top': 1  # Top from today
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            articles = response.json()
            
            # Extract unique authors
            seen_users = set()
            candidates = []
            
            for article in articles:
                user = article.get('user', {})
                username = user.get('username')
                
                if username and username not in seen_users:
                    seen_users.add(username)
                    user_data = self._get_user_profile(username)
                    if user_data:
                        candidates.append(user_data)
                    
                    if len(candidates) >= max_results:
                        break
            
            return candidates
            
        except Exception as e:
            print(f"Error fetching trending authors: {e}")
            return []
