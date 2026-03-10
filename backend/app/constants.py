"""
Shared constants used across API and scraper layers.
"""

JOB_PORTAL_KEYWORDS: set[str] = {
    "naukri",
    "instahyre",
    "foundit",
    "monster",
    "timesjobs",
    "indeed",
    "linkedin",
    "glassdoor",
    "ziprecruiter",
    "wellfound",
    "cutshort",
    "hirist",
    "adzuna",
    "jsearch",
    "remotive",
    "himalayas",
    "arbeitnow",
    "apna",
    "freshersworld",
}

# Sources that are typically safer/more stable for structured, legal API-driven ingestion.
TRUSTED_API_SOURCES: set[str] = {
    "adzuna",
    "jsearch",
    "remotive",
    "himalayas",
    "arbeitnow",
}
