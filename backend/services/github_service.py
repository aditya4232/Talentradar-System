import requests
from typing import List, Dict, Optional
from config import get_settings


class GitHubService:
    """GitHub API integration for finding developers"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://api.github.com"
        self.headers = {}
        
        if self.settings.github_token and self.settings.github_token != "your_github_token_here":
            self.headers["Authorization"] = f"token {self.settings.github_token}"
    
    def search_users(self, location: str, language: str = None, limit: int = 10) -> List[Dict]:
        """Search GitHub users by location and programming language"""
        query_parts = [f"location:{location}"]
        
        if language:
            query_parts.append(f"language:{language}")
        
        query = " ".join(query_parts)
        
        url = f"{self.base_url}/search/users"
        params = {
            'q': query,
            'per_page': limit
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            # If rate limited or no token, return mock data
            if response.status_code == 403 or response.status_code == 401:
                return self._mock_github_users(location, language, limit)
            
            response.raise_for_status()
            data = response.json()
            
            users = []
            for user in data.get('items', [])[:limit]:
                user_detail = self.get_user_details(user['login'])
                if user_detail:
                    users.append(user_detail)
            
            return users
        except Exception as e:
            print(f"GitHub search error: {e}")
            return self._mock_github_users(location, language, limit)
    
    def get_user_details(self, username: str) -> Optional[Dict]:
        """Get detailed information about a GitHub user"""
        url = f"{self.base_url}/users/{username}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Try to get email from events (commits)
            email = self._extract_email_from_events(username)
            
            return {
                'username': data.get('login'),
                'name': data.get('name'),
                'email': email or data.get('email'),
                'bio': data.get('bio'),
                'location': data.get('location'),
                'github_url': data.get('html_url'),
                'blog': data.get('blog'),
                'public_repos': data.get('public_repos', 0),
                'followers': data.get('followers', 0)
            }
        except Exception as e:
            print(f"Error getting user details: {e}")
            return None
    
    def _extract_email_from_events(self, username: str) -> Optional[str]:
        """Try to extract email from user's recent events/commits"""
        url = f"{self.base_url}/users/{username}/events/public"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            if response.status_code != 200:
                return None
            
            events = response.json()
            
            # Look through recent events for commits
            for event in events[:10]:
                if event.get('type') == 'PushEvent':
                    commits = event.get('payload', {}).get('commits', [])
                    for commit in commits:
                        author = commit.get('author', {})
                        email = author.get('email')
                        if email and '@users.noreply.github.com' not in email:
                            return email
            
            return None
        except:
            return None
    
    def get_user_languages(self, username: str) -> List[str]:
        """Get programming languages used by a user"""
        url = f"{self.base_url}/users/{username}/repos"
        params = {'per_page': 10, 'sort': 'updated'}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            
            if response.status_code != 200:
                return []
            
            repos = response.json()
            languages = set()
            
            for repo in repos:
                lang = repo.get('language')
                if lang:
                    languages.add(lang)
            
            return list(languages)
        except:
            return []
    
    def _mock_github_users(self, location: str, language: str, limit: int) -> List[Dict]:
        """Generate mock GitHub user data"""
        mock_users = [
            {
                'username': 'rahul_dev',
                'name': 'Rahul Kumar',
                'email': 'rahul.kumar@gmail.com',
                'bio': 'Python developer passionate about ML and cloud technologies',
                'location': location,
                'github_url': 'https://github.com/rahul_dev',
                'blog': 'https://rahuldev.com',
                'public_repos': 45,
                'followers': 120
            },
            {
                'username': 'ankit_reddy',
                'name': 'Ankit Reddy',
                'email': 'ankit.reddy@outlook.com',
                'bio': 'Full stack developer | React | Node.js | AWS',
                'location': location,
                'github_url': 'https://github.com/ankit_reddy',
                'blog': '',
                'public_repos': 32,
                'followers': 85
            },
            {
                'username': 'priya_ml',
                'name': 'Priya Patel',
                'email': 'priya.patel@yahoo.com',
                'bio': 'ML Engineer | TensorFlow | PyTorch | Deep Learning enthusiast',
                'location': location,
                'github_url': 'https://github.com/priya_ml',
                'blog': 'https://priyaml.dev',
                'public_repos': 28,
                'followers': 156
            },
            {
                'username': 'vikram_tech',
                'name': 'Vikram Singh',
                'email': 'vikram.singh@gmail.com',
                'bio': 'DevOps Engineer | Kubernetes | Docker | CI/CD',
                'location': location,
                'github_url': 'https://github.com/vikram_tech',
                'blog': '',
                'public_repos': 38,
                'followers': 92
            },
            {
                'username': 'sneha_data',
                'name': 'Sneha Gupta',
                'email': 'sneha.gupta@gmail.com',
                'bio': 'Data Scientist | Python | R | SQL | Machine Learning',
                'location': location,
                'github_url': 'https://github.com/sneha_data',
                'blog': 'https://sneha-analytics.com',
                'public_repos': 22,
                'followers': 67
            }
        ]
        
        return mock_users[:limit]
