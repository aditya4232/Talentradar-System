"""
Enhanced Location Validator for India-only filtering
Ensures only candidates from India are accepted
"""

# Comprehensive list of Indian cities and states
INDIAN_CITIES = {
    # Major metros
    "mumbai", "delhi", "bangalore", "bengaluru", "hyderabad", "chennai",
    "kolkata", "pune", "ahmedabad", "surat", "jaipur", "lucknow",
    "kanpur", "nagpur", "indore", "thane", "bhopal", "visakhapatnam",
    "pimpri", "chinchwad", "patna", "vadodara", "ghaziabad", "ludhiana",
    "agra", "nashik", "faridabad", "meerut", "rajkot", "kalyan",
    "dombivli", "vasai", "virar", "varanasi", "srinagar", "aurangabad",
    "dhanbad", "amritsar", "navi mumbai", "allahabad", "prayagraj",
    "ranchi", "howrah", "coimbatore", "jabalpur", "gwalior", "vijayawada",
    "jodhpur", "madurai", "raipur", "kota", "chandigarh", "guwahati",
    
    # Tech hubs and emerging cities
    "noida", "gurugram", "gurgaon", "greater noida", "faridabad",
    "thiruvananthapuram", "trivandrum", "kochi", "cochin", "mysore",
    "mysuru", "mangalore", "mangaluru", "hubli", "dharwad", "belgaum",
    "tirupati", "guntur", "nellore", "warangal", "kakinada", "tiruppur",
    "salem", "tirunelveli", "vellore", "erode", "thrissur", "kollam",
    "kozhikode", "calicut", "bhubaneswar", "cuttack", "rourkela",
    "dehradun", "haridwar", "roorkee", "shimla", "jammu", "udaipur",
    "ajmer", "bikaner", "kota", "alwar", "bhilwara", "siliguri",
    "asansol", "durgapur", "kharagpur",
    
    # IT parks and startup cities
    "whitefield", "electronic city", "hinjewadi", "gachibowli",
    "hitec city", "madhapur", "banjara hills", "kondapur", "financial district",
    "salt lake", "sector v", "rajarhat", "new town", "sholinganallur",
    "omr", "guindy", "ambattur", "tambaram", "porur",
}

INDIAN_STATES = {
    "andhra pradesh", "ap", "arunachal pradesh", "assam", "bihar",
    "chhattisgarh", "goa", "gujarat", "haryana", "himachal pradesh", "hp",
    "jharkhand", "karnataka", "kerala", "madhya pradesh", "mp",
    "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland",
    "odisha", "orissa", "punjab", "rajasthan", "sikkim",
    "tamil nadu", "tn", "telangana", "tripura", "uttar pradesh", "up",
    "uttarakhand", "west bengal", "wb",
    # UTs
    "delhi", "jammu and kashmir", "j&k", "ladakh", "puducherry",
    "pondicherry", "chandigarh", "andaman and nicobar", "lakshadweep",
    "dadra and nagar haveli", "daman and diu",
}

# Non-Indian locations to explicitly reject
NON_INDIAN_LOCATIONS = {
    "usa", "united states", "america", "us", "canada", "uk", "united kingdom",
    "britain", "london", "singapore", "australia", "sydney", "melbourne",
    "dubai", "uae", "germany", "berlin", "netherlands", "amsterdam",
    "france", "paris", "spain", "sweden", "switzerland", "ireland",
    "new york", "california", "texas", "florida", "washington",
    "san francisco", "seattle", "boston", "chicago", "los angeles",
    "toronto", "vancouver", "hong kong", "tokyo", "beijing", "shanghai",
    "bahrain", "qatar", "saudi arabia", "kuwait", "oman",
    "europe", "apac", "latam", "africa", "middle east",
}

def is_valid_india_location(location: str) -> bool:
    """
    Strictly validates if a location is in India
    
    Returns:
        True if location is in India
        False if location is outside India or invalid
    """
    if not location or not isinstance(location, str):
        return False
    
    loc = location.lower().strip()
    
    # Empty or "remote" without India specification - REJECT
    if not loc or loc in ["remote", "n/a", "na", "unknown", "anywhere", "worldwide"]:
        return False
    
    # Explicitly check for non-Indian locations - REJECT
    for non_indian in NON_INDIAN_LOCATIONS:
        if non_indian in loc:
            return False
    
    # Check for India mention
    if "india" in loc or "ind" == loc or "in" == loc:
        return True
    
    # Check for Indian cities
    for city in INDIAN_CITIES:
        if city in loc:
            return True
    
    # Check for Indian states
    for state in INDIAN_STATES:
        if state in loc:
            return True
    
    # If "remote" WITH an Indian location, accept
    if "remote" in loc and any(city in loc for city in INDIAN_CITIES):
        return True
    
    # Default: REJECT if not explicitly identified as India
    return False


def normalize_india_location(location: str) -> str:
    """
    Normalizes location string to standard format
    
    Returns:
        Normalized location string or "India (Remote)" for remote jobs
    """
    if not location or not isinstance(location, str):
        return "India"
    
    loc = location.strip()
    loc_lower = loc.lower()
    
    # Check if it's remote with India
    if "remote" in loc_lower and any(city in loc_lower for city in INDIAN_CITIES):
        # Extract the city
        for city in sorted(INDIAN_CITIES, key=len, reverse=True):
            if city in loc_lower:
                return f"{city.title()} (Remote)"
        return "India (Remote)"
    
    # Check for Hyderabad variants
    if "hyderabad" in loc_lower or "hyd" in loc_lower:
        if "telangana" in loc_lower or "ts" in loc_lower:
            return "Hyderabad, Telangana"
        return "Hyderabad"
    
    # Check for Bangalore variants
    if "bangalore" in loc_lower or "bengaluru" in loc_lower or "blr" in loc_lower:
        if "karnataka" in loc_lower or "ka" in loc_lower:
            return "Bangalore, Karnataka"
        return "Bangalore"
    
    # Check for other major cities
    city_state_map = {
        "mumbai": "Mumbai, Maharashtra",
        "pune": "Pune, Maharashtra",
        "delhi": "New Delhi",
        "gurgaon": "Gurgaon, Haryana",
        "gurugram": "Gurugram, Haryana",
        "noida": "Noida, Uttar Pradesh",
        "chennai": "Chennai, Tamil Nadu",
        "kolkata": "Kolkata, West Bengal",
    }
    
    for city, full_name in city_state_map.items():
        if city in loc_lower:
            return full_name
    
    # Return as-is if already proper format
    return loc


def get_location_display_name(location: str) -> str:
    """
    Get a clean display name for a location
    Prioritizes Hyderabad > Other Metro > India
    """
    if not location:
        return "India"
    
    if not is_valid_india_location(location):
        return "Invalid Location"
    
    return normalize_india_location(location)


def filter_indian_candidates(candidates: list) -> list:
    """
    Filters a list of candidates to only include those from India
    
    Args:
        candidates: List of candidate dictionaries with 'location' field
    
    Returns:
        Filtered list of candidates from India only
    """
    indian_candidates = []
    
    for candidate in candidates:
        location = candidate.get("location", "")
        if is_valid_india_location(location):
            # Normalize the location
            candidate["location"] = normalize_india_location(location)
            indian_candidates.append(candidate)
    
    return indian_candidates
