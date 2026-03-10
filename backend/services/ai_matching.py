import numpy as np
from typing import List, Dict, Tuple
import json

try:
    from anthropic import Anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

from config import get_settings


class AIMatchingEngine:
    def __init__(self):
        self.settings = get_settings()
        self.claude_client = None
        
        # Initialize Claude if available and API key is set
        if CLAUDE_AVAILABLE and self.settings.claude_api_key:
            try:
                self.claude_client = Anthropic(
                    api_key=self.settings.claude_api_key,
                    base_url=self.settings.claude_base_url
                )
                print("Claude Opus 4.6 AI matching enabled!")
            except Exception as e:
                print(f"Claude initialization failed: {e}. Using fallback matching.")
                self.claude_client = None
        else:
            print("No Claude API key found. Using keyword-based matching.")
    
    def match_candidates_to_job(self, candidates: List[Dict], job_description: str, top_k: int = 10) -> List[Tuple[Dict, float]]:
        if not candidates:
            return []
        
        matches = []
        
        # Use Claude AI if available
        if self.claude_client:
            print("   Using Claude Opus AI for intelligent matching...")
            for candidate in candidates:
                score = self._claude_match(candidate, job_description)
                matches.append((candidate, score))
        else:
            # Fallback to simple matching
            print("   Using keyword-based matching...")
            for candidate in candidates:
                candidate_text = self._create_candidate_text(candidate)
                score = self._simple_match(candidate_text, job_description)
                matches.append((candidate, score))
        
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:top_k]
    
    def _claude_match(self, candidate: Dict, job_description: str) -> float:
        """Use Claude Opus to intelligently match candidate to job"""
        
        candidate_text = self._create_candidate_text(candidate)
        
        prompt = f"""You are an expert technical recruiter. Analyze how well this candidate matches the job description.

JOB DESCRIPTION:
{job_description}

CANDIDATE PROFILE:
{candidate_text}

Analyze the match based on:
1. Skills alignment (technical + soft skills)
2. Experience level match
3. Location compatibility  
4. Career trajectory fit
5. Domain expertise

Respond with ONLY a JSON object in this exact format:
{{"match_score": 75, "reasoning": "Good match for Python skills"}}

Be precise and realistic. Only give high scores (80+) for excellent matches."""
        
        try:
            response = self.claude_client.messages.create(
                model=self.settings.claude_model,
                max_tokens=200,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Extract the response text
            response_text = response.content[0].text.strip()
            
            # Parse JSON response
            result = json.loads(response_text)
            score = float(result.get('match_score', 0))
            
            # Clamp score between 0-100
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            print(f"   Claude API error: {e}. Using fallback for this candidate.")
            # Fallback to simple matching
            return self._simple_match(candidate_text, job_description)
    
    def _simple_match(self, candidate_text: str, job_text: str) -> float:
        """Fallback keyword-based matching"""
        candidate_lower = candidate_text.lower()
        job_lower = job_text.lower()
        job_words = set(job_lower.split())
        candidate_words = set(candidate_lower.split())
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        job_words -= common_words
        candidate_words -= common_words
        if not job_words:
            return 50.0
        overlap = len(job_words & candidate_words)
        score = (overlap / len(job_words)) * 100
        for word in job_words:
            if len(word) > 3 and word in candidate_lower:
                score += 5
        return min(100.0, max(0.0, score))
    
    def _create_candidate_text(self, candidate: Dict) -> str:
        parts = []
        if candidate.get('name'):
            parts.append(f"Name: {candidate['name']}")
        if candidate.get('bio'):
            parts.append(f"Bio: {candidate['bio']}")
        if candidate.get('skills'):
            if isinstance(candidate['skills'], list):
                skills_str = ", ".join(candidate['skills'])
            else:
                skills_str = str(candidate['skills'])
            parts.append(f"Skills: {skills_str}")
        if candidate.get('experience_years'):
            parts.append(f"Experience: {candidate['experience_years']} years")
        if candidate.get('location'):
            parts.append(f"Location: {candidate['location']}")
        if candidate.get('reputation'):
            parts.append(f"Stack Overflow Reputation: {candidate['reputation']}")
        if candidate.get('source'):
            parts.append(f"Source: {candidate['source']}")
        return " | ".join(parts)
    
    def match_existing_candidates(self, candidates: List[Dict], job_description: str, top_k: int = 10) -> List[Dict]:
        matched = self.match_candidates_to_job(candidates, job_description, top_k)
        results = []
        for candidate, score in matched:
            candidate['match_score'] = round(score, 2)
            results.append(candidate)
        return results
