"""
Professional Candidate Deduplication Utility

Prevents duplicate profiles from multiple sources using:
- Fuzzy name matching
- Company normalization
- Email matching
- Phone number normalization
"""

import hashlib
import re
from difflib import SequenceMatcher


def normalize_name(name: str) -> str:
    """Normalize name for comparison: lowercase, remove special chars, trim."""
    if not name:
        return ""
    # Remove titles like Dr., Mr., Ms., etc
    name = re.sub(r'\b(dr|mr|ms|mrs|prof|sir|miss)\.?\s+', '', name.lower())
    # Remove special characters except spaces
    name = re.sub(r'[^a-z\s]', '', name)
    # Normalize whitespace
    name = ' '.join(name.split())
    return name


def normalize_company(company: str) -> str:
    """Normalize company name for comparison."""
    if not company:
        return ""
    company = company.lower().strip()
    # Remove common suffixes
    suffixes = [
        r'\s+(inc|incorporated|llc|ltd|limited|pvt|private|corp|corporation|co)\.?$',
        r'\s+(india|technologies|solutions|services|systems|software)$',
    ]
    for suffix in suffixes:
        company = re.sub(suffix, '', company, flags=re.IGNORECASE)
    # Remove special characters
    company = re.sub(r'[^a-z0-9\s]', '', company)
    company = ' '.join(company.split())
    return company


def normalize_email(email: str) -> str:
    """Normalize email for comparison."""
    if not email:
        return ""
    email = email.lower().strip()
    # Remove + aliases (e.g., user+tag@domain.com → user@domain.com)
    email = re.sub(r'\+[^@]+@', '@', email)
    return email


def normalize_phone(phone: str) -> str:
    """Normalize phone number for comparison."""
    if not phone:
        return ""
    # Remove all non-digit characters
    phone = re.sub(r'\D', '', phone)
    # Remove country code if present (assuming +91 for India)
    if phone.startswith('91') and len(phone) > 10:
        phone = phone[2:]
    # Return last 10 digits
    return phone[-10:] if len(phone) >= 10 else phone


def fuzzy_match(str1: str, str2: str, threshold: float = 0.85) -> bool:
    """Check if two strings are similar using fuzzy matching."""
    if not str1 or not str2:
        return False
    similarity = SequenceMatcher(None, str1, str2).ratio()
    return similarity >= threshold


def generate_dedup_hash(name: str, company: str, source: str = "") -> str:
    """
    Generate unique hash for deduplication.
    
    Uses normalized name + company combination.
    Different sources can have different hashes for same person.
    """
    norm_name = normalize_name(name)
    norm_company = normalize_company(company)
    
    # Create fingerprint
    fingerprint = f"{norm_name}|{norm_company}|{source}"
    
    # Generate hash
    return hashlib.md5(fingerprint.encode()).hexdigest()[:16]


def is_duplicate(
    candidate1: dict,
    candidate2: dict,
    strict: bool = False
) -> bool:
    """
    Check if two candidate dictionaries represent the same person.
    
    Args:
        candidate1: First candidate dict with keys: name, company, email, phone
        candidate2: Second candidate dict
        strict: If True, requires higher similarity threshold
    
    Returns:
        bool: True if candidates are likely duplicates
    """
    # Email match = definite duplicate (if both have emails)
    email1 = normalize_email(candidate1.get("email", ""))
    email2 = normalize_email(candidate2.get("email", ""))
    if email1 and email2 and email1 == email2:
        return True
    
    # Phone match = likely duplicate (if both have phones)
    phone1 = normalize_phone(candidate1.get("phone", ""))
    phone2 = normalize_phone(candidate2.get("phone", ""))
    if phone1 and phone2 and len(phone1) >= 10 and phone1 == phone2:
        return True
    
    # Name + Company fuzzy match
    name1 = normalize_name(candidate1.get("name", ""))
    name2 = normalize_name(candidate2.get("name", ""))
    company1 = normalize_company(candidate1.get("company", ""))
    company2 = normalize_company(candidate2.get("company", ""))
    
    threshold = 0.90 if strict else 0.85
    
    # Both name and company must match
    if fuzzy_match(name1, name2, threshold) and fuzzy_match(company1, company2, threshold):
        return True
    
    # Name match + same source = likely duplicate
    if fuzzy_match(name1, name2, 0.92):
        source1 = candidate1.get("source", "").split("(")[0].strip()
        source2 = candidate2.get("source", "").split("(")[0].strip()
        if source1 == source2:
            return True
    
    return False


def merge_candidates(candidates: list[dict]) -> dict:
    """
    Merge duplicate candidates, keeping the best data from each.
    
    Args:
        candidates: List of candidate dicts to merge
    
    Returns:
        dict: Merged candidate with best fields from all sources
    """
    if not candidates:
        return {}
    
    if len(candidates) == 1:
        return candidates[0]
    
    # Sort by talent_score (descending) to prioritize best profile
    sorted_candidates = sorted(
        candidates,
        key=lambda c: c.get("talent_score", 0),
        reverse=True
    )
    
    # Start with best candidate as base
    merged = sorted_candidates[0].copy()
    
    # Merge skills from all sources
    all_skills = set()
    for c in sorted_candidates:
        skills = c.get("skills", [])
        if isinstance(skills, list):
            all_skills.update(skills)
    merged["skills"] = sorted(list(all_skills))[:20]  # Keep top 20 skills
    
    # Take longest summary
    longest_summary = max(
        (c.get("summary", "") for c in sorted_candidates),
        key=len
    )
    if longest_summary:
        merged["summary"] = longest_summary
    
    # Prefer filled fields over empty ones
    for candidate in sorted_candidates[1:]:
        if not merged.get("email") and candidate.get("email"):
            merged["email"] = candidate["email"]
        if not merged.get("phone") and candidate.get("phone"):
            merged["phone"] = candidate["phone"]
        if not merged.get("profile_url") and candidate.get("profile_url"):
            merged["profile_url"] = candidate["profile_url"]
    
    # Track merged sources (preserve original sources)
    sources = [c.get("source", "") for c in sorted_candidates]
    merged["original_sources"] = sources  # Preserve for verification
    merged["source"] = f"{merged['source']} (merged from {len(sources)} sources)"
    
    # Recalculate talent score (average of all sources)
    avg_score = sum(c.get("talent_score", 0) for c in sorted_candidates) / len(sorted_candidates)
    merged["talent_score"] = round(avg_score, 1)
    
    return merged


# Aliases for compatibility with scraper.py
def generate_profile_hash(candidate_data: dict) -> str:
    """Alias for generate_dedup_hash for backwards compatibility."""
    return generate_dedup_hash(
        candidate_data.get("name", ""),
        candidate_data.get("company", ""),
        candidate_data.get("source", "")
    )


def are_duplicates(candidate1: dict, candidate2: dict) -> bool:
    """Alias for is_duplicate for backwards compatibility."""
    return is_duplicate(candidate1, candidate2, strict=False)


def find_and_mark_duplicates(db, new_candidate_data: dict):
    """
    Find duplicates in database and mark them.
    
    Args:
        db: SQLAlchemy session
        new_candidate_data: Candidate to check
    
    Returns:
        ID of master record if duplicate found, else None
    """
    from ..models import Candidate
    
    # Get all candidates
    existing = db.query(Candidate).all()
    
    for candidate in existing:
        existing_data = {
            "name": candidate.name,
            "email": candidate.email,
            "company": candidate.company,
            "phone": candidate.phone,
            "source": candidate.source,
        }
        
        if are_duplicates(existing_data, new_candidate_data):
            # Found duplicate! Merge data into existing record
            merged_data = merge_candidates([existing_data, new_candidate_data])
            
            # Update existing record with merged data
            for field, value in merged_data.items():
                if hasattr(candidate, field) and value:
                    setattr(candidate, field, value)
            
            db.commit()
            return candidate.id  # Return master record ID
    
    return None  # No duplicate found
