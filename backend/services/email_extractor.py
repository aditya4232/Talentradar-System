import re
from typing import List, Optional
import requests
from bs4 import BeautifulSoup


class EmailExtractor:
    """Extract emails from web pages and text"""
    
    EMAIL_REGEX = r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}'
    
    @classmethod
    def extract_from_text(cls, text: str) -> List[str]:
        """Extract all email addresses from text"""
        if not text:
            return []
        
        emails = re.findall(cls.EMAIL_REGEX, text)
        
        # Filter out common false positives
        filtered_emails = []
        exclude_patterns = [
            '@users.noreply.github.com',
            '@example.com',
            '@domain.com',
            '@email.com'
        ]
        
        for email in emails:
            if not any(pattern in email.lower() for pattern in exclude_patterns):
                filtered_emails.append(email)
        
        return list(set(filtered_emails))  # Remove duplicates
    
    @classmethod
    def extract_from_url(cls, url: str) -> List[str]:
        """Extract emails from a webpage"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Try to extract from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            text = soup.get_text()
            
            # Also check mailto links
            mailto_emails = []
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').split('?')[0]
                    mailto_emails.append(email)
            
            # Extract from text
            text_emails = cls.extract_from_text(text)
            
            # Combine both sources
            all_emails = list(set(mailto_emails + text_emails))
            
            return all_emails
        
        except Exception as e:
            print(f"Error extracting emails from {url}: {e}")
            return []
    
    @classmethod
    def extract_from_github_profile(cls, github_url: str) -> Optional[str]:
        """Try to extract email from GitHub profile page"""
        try:
            # GitHub profile pages sometimes show email
            emails = cls.extract_from_url(github_url)
            
            if emails:
                # Prioritize non-github emails
                for email in emails:
                    if 'github' not in email.lower():
                        return email
                
                # If only github emails, return the first one
                return emails[0] if emails else None
            
            return None
        
        except:
            return None
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """Validate if an email looks legitimate"""
        if not email:
            return False
        
        # Basic regex validation
        if not re.match(cls.EMAIL_REGEX, email):
            return False
        
        # Check for common fake patterns
        fake_patterns = [
            'noreply',
            'no-reply',
            'donotreply',
            'example.com',
            'test.com',
            'fake.com'
        ]
        
        email_lower = email.lower()
        if any(pattern in email_lower for pattern in fake_patterns):
            return False
        
        return True
