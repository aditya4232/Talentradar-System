"""
Professional Contact Information Extraction Utility

Extracts and validates email addresses and phone numbers from text.
"""

import re
from typing import Optional, Tuple


# Comprehensive email regex pattern
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    re.IGNORECASE
)

# Indian phone number patterns
PHONE_PATTERNS = [
    # +91-9876543210, +91 9876543210, +919876543210
    re.compile(r'\+91[\s\-]?(\d{10})'),
    # 91-9876543210, 91 9876543210
    re.compile(r'\b91[\s\-]?(\d{10})\b'),
    # 9876543210 (10 digits starting with 6-9)
    re.compile(r'\b([6-9]\d{9})\b'),
    # (0)9876543210, 09876543210
    re.compile(r'\(0\)(\d{10})\b'),
    re.compile(r'\b0(\d{10})\b'),
]


def extract_email(text: str) -> Optional[str]:
    """
    Extract first valid email address from text.
    
    Args:
        text: Text to search for email
    
    Returns:
        str: Normalized email address or None
    """
    if not text:
        return None
    
    matches = EMAIL_PATTERN.findall(text)
    if not matches:
        return None
    
    # Filter out common invalid patterns
    valid_emails = []
    for email in matches:
        email_lower = email.lower()
        # Skip obviously fake emails
        if any(word in email_lower for word in [
            'noreply', 'no-reply', 'donotreply', 'example.com',
            'test@', '@test', 'fake', 'dummy', 'placeholder'
        ]):
            continue
        valid_emails.append(email.lower())
    
    return valid_emails[0] if valid_emails else None


def extract_phone(text: str) -> Optional[str]:
    """
    Extract and normalize Indian phone number from text.
    
    Args:
        text: Text to search for phone number
    
    Returns:
        str: Normalized phone number (+91-XXXXXXXXXX) or None
    """
    if not text:
        return None
    
    # Try each pattern
    for pattern in PHONE_PATTERNS:
        match = pattern.search(text)
        if match:
            # Extract just the 10 digits
            if match.groups():
                phone = match.group(1)
            else:
                phone = match.group(0)
            
            # Remove any non-digits
            phone = re.sub(r'\D', '', phone)
            
            # Ensure it's 10 digits
            if len(phone) == 10 and phone[0] in '6789':
                return f"+91-{phone}"
    
    return None


def extract_contacts(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract both email and phone from text.
    
    Args:
        text: Text to search
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (email, phone)
    """
    email = extract_email(text)
    phone = extract_phone(text)
    return email, phone


def validate_email(email: str) -> bool:
    """
    Validate if email address is properly formatted.
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid
    """
    if not email:
        return False
    
    # Check format
    if not EMAIL_PATTERN.match(email):
        return False
    
    # Check for common invalid patterns
    email_lower = email.lower()
    invalid_patterns = [
        'noreply', 'no-reply', 'donotreply', 'example.com',
        'test@', '@test', 'fake', 'dummy', 'placeholder'
    ]
    
    return not any(pattern in email_lower for pattern in invalid_patterns)


def validate_phone(phone: str) -> bool:
    """
    Validate if phone number is properly formatted Indian number.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        bool: True if valid
    """
    if not phone:
        return False
    
    # Remove non-digits
    digits = re.sub(r'\D', '', phone)
    
    # Check if it's 10 or 12 digits (with country code)
    if len(digits) == 10:
        return digits[0] in '6789'
    elif len(digits) == 12:
        return digits.startswith('91') and digits[2] in '6789'
    
    return False


def normalize_contact_info(candidate_data: dict) -> dict:
    """
    Extract and normalize contact information from candidate data.
    
    Args:
        candidate_data: Dict with 'summary', 'email', 'phone' fields
    
    Returns:
        dict: Updated candidate_data with normalized contacts
    """
    # Extract from summary if not already present
    summary = candidate_data.get("summary", "")
    
    # Email
    if not candidate_data.get("email") and summary:
        extracted_email = extract_email(summary + " " + candidate_data.get("profile_url", ""))
        if extracted_email:
            candidate_data["email"] = extracted_email
    
    # Phone
    if not candidate_data.get("phone") and summary:
        extracted_phone = extract_phone(summary)
        if extracted_phone:
            candidate_data["phone"] = extracted_phone
    
    # Normalize existing email
    if candidate_data.get("email"):
        candidate_data["email"] = candidate_data["email"].lower().strip()
        if not validate_email(candidate_data["email"]):
            candidate_data["email"] = None
    
    # Normalize existing phone
    if candidate_data.get("phone"):
        if validate_phone(candidate_data["phone"]):
            digits = re.sub(r'\D', '', candidate_data["phone"])
            if len(digits) == 12:
                digits = digits[2:]  # Remove country code
            candidate_data["phone"] = f"+91-{digits}"
        else:
            candidate_data["phone"] = None
    
    return candidate_data
