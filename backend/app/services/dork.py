import urllib.parse
import re

async def google_dork_profiles(query: str, location: str, platform: str) -> list[str]:
    # Returns a list of search engine URLs that look for candidate profiles.
    # Platform could be linkedin, github, naukri (resumes), etc.
    dork = ""
    if platform.lower() == "linkedin":
        dork = f'site:linkedin.com/in/ "{query}" "{location}"'
    elif platform.lower() == "github":
        dork = f'site:github.com "{query}" "{location}"'
    elif platform.lower() == "naukri":
        dork = f'site:naukri.com/freelance/freelancer/ "{query}" "{location}"'
    elif platform.lower() == "instahyre":
        dork = f'site:instahyre.com/profile/ "{query}" "{location}"'
    else:
        dork = f'"{query}" "{location}" resume OR CV OR profile'
        
    encoded_query = urllib.parse.quote(dork)
    # Using DuckDuckGo HTML light version for easier scraping of links
    ddg_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"
    return [ddg_url]
