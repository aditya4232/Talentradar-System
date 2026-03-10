import requests
from typing import List, Dict
from config import get_settings
import json


class GoogleXRaySearch:
    """Google X-Ray Search for finding candidate profiles"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://google.serper.dev/search"
    
    def generate_search_queries(self, skills: List[str], location: str = "Hyderabad") -> List[str]:
        """Generate Google X-Ray search queries"""
        queries = []
        
        # LinkedIn searches
        skill_str = " ".join(skills[:3])  # Top 3 skills
        queries.extend([
            f'site:linkedin.com/in "{skill_str}" "{location}" "open to work"',
            f'site:linkedin.com/in "{skills[0]}" developer "{location}"',
        ])
        
        # GitHub searches
        if skills:
            queries.extend([
                f'site:github.com "{location}" "{skills[0]}"',
                f'site:github.com "{location}" developer',
            ])
        
        # Stack Overflow
        queries.append(f'site:stackoverflow.com/users "{location}" {skills[0] if skills else "developer"}')
        
        # Angel.co / Wellfound
        queries.append(f'site:angel.co "{location}" developer')
        
        # Portfolio sites
        queries.append(f'"{location}" developer portfolio {skills[0] if skills else ""}')
        
        return queries
    
    def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """Execute Google search via Serper API"""
        if not self.settings.serper_api_key or self.settings.serper_api_key == "your_serper_api_key_here":
            # Return mock data if no API key
            return self._mock_search_results(query, num_results)
        
        headers = {
            'X-API-KEY': self.settings.serper_api_key,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': num_results
        }
        
        try:
            response = requests.post(self.base_url, headers=headers, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            results = []
            for item in data.get('organic', []):
                results.append({
                    'title': item.get('title', ''),
                    'link': item.get('link', ''),
                    'snippet': item.get('snippet', '')
                })
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return self._mock_search_results(query, num_results)
    
    def _mock_search_results(self, query: str, num_results: int) -> List[Dict]:
        """Generate mock search results for testing"""
        mock_results = [
            {
                'title': 'Rahul Sharma - Python Developer | Hyderabad',
                'link': 'https://linkedin.com/in/rahul-sharma-dev',
                'snippet': 'Python Developer with 3 years experience in AWS, ML, Django. Based in Hyderabad. Open to work.'
            },
            {
                'title': 'Ankit Reddy - Full Stack Developer',
                'link': 'https://github.com/ankitreddy',
                'snippet': 'Full stack developer specializing in React, Node.js, and AWS. Hyderabad based.'
            },
            {
                'title': 'Priya Patel - ML Engineer Profile',
                'link': 'https://linkedin.com/in/priya-patel-ml',
                'snippet': 'Machine Learning Engineer with experience in TensorFlow, Python, and Deep Learning. Hyderabad. Actively seeking opportunities.'
            },
            {
                'title': 'Vikram Singh - GitHub Profile',
                'link': 'https://github.com/vikramsingh',
                'snippet': 'Software engineer focused on cloud technologies and DevOps. Location: Hyderabad, India.'
            },
            {
                'title': 'Sneha Gupta - Data Scientist',
                'link': 'https://linkedin.com/in/sneha-gupta-ds',
                'snippet': 'Data Scientist with 4+ years experience. Skills: Python, R, Machine Learning, SQL. Hyderabad. Available for hire.'
            }
        ]
        
        return mock_results[:num_results]
    
    def search_all_queries(self, queries: List[str], results_per_query: int = 5) -> List[Dict]:
        """Search all queries and aggregate results"""
        all_results = []
        seen_links = set()
        
        for query in queries:
            results = self.search(query, results_per_query)
            for result in results:
                link = result.get('link', '')
                if link and link not in seen_links:
                    seen_links.add(link)
                    all_results.append(result)
        
        return all_results
