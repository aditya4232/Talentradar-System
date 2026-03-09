import os
from dotenv import load_dotenv

load_dotenv()

APIFY_API_TOKEN = os.getenv("APIFY_API_TOKEN", "")

try:
    from apify_client import ApifyClient
    client = ApifyClient(APIFY_API_TOKEN) if APIFY_API_TOKEN else None
except ImportError:
    client = None
    print("[ApifyService] apify-client not installed. Apify engine disabled.")


async def scrape_with_apify(actor_id: str, input_data: dict):
    """Run an Apify actor and return the results from the dataset."""
    if not client:
        print("[ApifyService] Client not initialized. APIFY_API_TOKEN missing or apify-client not installed.")
        return []
        
    try:
        print(f"[ApifyService] Running actor {actor_id}...")
        run = client.actor(actor_id).call(run_input=input_data, timeout_secs=120)
        
        print(f"[ApifyService] Actor finished. Fetching results from dataset {run['defaultDatasetId']}...")
        dataset_items = client.dataset(run["defaultDatasetId"]).list_items().items
        
        return dataset_items
    except Exception as e:
        print(f"[ApifyService] Error running {actor_id}: {e}")
        return []


async def get_linkedin_candidates(keywords: str, location: str = "India", limit: int = 10):
    """Specialized helper for LinkedIn Jobs/Profiles via Apify."""
    actor_id = "curious_coder/linkedin-jobs-scraper"
    
    input_data = {
        "searchKeywords": keywords,
        "locationName": location,
        "maxItems": limit,
        "proxyConfiguration": {"useApifyProxy": True}
    }
    
    return await scrape_with_apify(actor_id, input_data)


async def get_naukri_candidates(keywords: str, limit: int = 10):
    """Specialized helper for Naukri via Apify."""
    actor_id = "apify/naukri-scraper"
    
    input_data = {
        "keywords": keywords,
        "limit": limit
    }
    
    return await scrape_with_apify(actor_id, input_data)
