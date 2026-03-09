import time
import urllib.request
import urllib.error
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_service(url, name):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req, timeout=5)
        if response.status == 200:
            logging.info(f"[OK] {name} is up and running at {url}")
            return True
        else:
            logging.warning(f"[WARNING] {name} returned status code {response.status}")
            return False
    except urllib.error.URLError as e:
        logging.error(f"[ERROR] {name} is unreachable: {e.reason}")
        return False
    except Exception as e:
        logging.error(f"[ERROR] {name} check failed: {str(e)}")
        return False

def run_validator():
    logging.info("Starting TalentRadar System Validator...")
    while True:
        logging.info("--- Performing Health Checks ---")
        
        # Check Frontend
        check_service("http://localhost:5173/", "Frontend (Vite)")
        
        # Check Backend Health (Root endpoint should return 200)
        check_service("http://localhost:8000/", "Backend API (Root)")
        
        # Check Database/Candidate Endpoint
        check_service("http://localhost:8000/api/v1/candidates", "Backend Candidates API")
        
        logging.info("--- Health Checks Completed. Sleeping for 30s... ---")
        time.sleep(30)

if __name__ == "__main__":
    run_validator()
