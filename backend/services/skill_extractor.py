import re
from typing import List, Set


class SkillExtractor:
    """Extract skills from job descriptions and candidate profiles"""
    
    # Common tech skills database
    COMMON_SKILLS = {
        # Programming Languages
        'python', 'javascript', 'java', 'c++', 'c#', 'ruby', 'go', 'rust', 'php', 
        'typescript', 'swift', 'kotlin', 'scala', 'r', 'matlab', 'perl',
        
        # Web Technologies
        'react', 'angular', 'vue', 'node.js', 'express', 'django', 'flask', 
        'fastapi', 'spring', 'asp.net', 'html', 'css', 'tailwind', 'bootstrap',
        
        # Databases
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch', 
        'cassandra', 'dynamodb', 'oracle', 'sqlite',
        
        # Cloud & DevOps
        'aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform',
        'ansible', 'ci/cd', 'linux', 'nginx', 'apache',
        
        # Data Science & ML
        'machine learning', 'deep learning', 'tensorflow', 'pytorch', 'scikit-learn',
        'pandas', 'numpy', 'nlp', 'computer vision', 'data science', 'ai',
        'llm', 'transformers', 'bert', 'gpt',
        
        # Other
        'git', 'agile', 'scrum', 'rest api', 'graphql', 'microservices',
        'kafka', 'rabbitmq', 'spark', 'hadoop', 'airflow'
    }
    
    @classmethod
    def extract_skills(cls, text: str) -> List[str]:
        """Extract skills from text"""
        if not text:
            return []
        
        text_lower = text.lower()
        found_skills = set()
        
        # Find exact matches
        for skill in cls.COMMON_SKILLS:
            # Use word boundaries for exact matching
            pattern = r'\b' + re.escape(skill) + r'\b'
            if re.search(pattern, text_lower):
                found_skills.add(skill)
        
        # Also extract words that might be skills (capitalized tech terms)
        # Match things like "React", "AWS", "Node.js"
        potential_skills = re.findall(r'\b[A-Z][a-zA-Z0-9+#.]*\b', text)
        for skill in potential_skills:
            if skill.lower() in cls.COMMON_SKILLS:
                found_skills.add(skill.lower())
        
        return sorted(list(found_skills))
    
    @classmethod
    def extract_experience(cls, text: str) -> float:
        """Extract years of experience from text"""
        if not text:
            return 0.0
        
        # Pattern: "X years", "X-Y years", "X+ years"
        patterns = [
            r'(\d+)\+?\s*years?',
            r'(\d+)-(\d+)\s*years?',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                if len(match.groups()) == 2:
                    return float(match.group(1))
                else:
                    return float(match.group(1))
        
        return 0.0
    
    @classmethod
    def detect_open_to_work(cls, text: str) -> bool:
        """Detect if candidate is open to work"""
        if not text:
            return False
        
        text_lower = text.lower()
        keywords = [
            'open to work',
            'seeking opportunities',
            'looking for job',
            'available for hire',
            'freelancer',
            'open to opportunities',
            'actively looking',
            'job search'
        ]
        
        return any(keyword in text_lower for keyword in keywords)
