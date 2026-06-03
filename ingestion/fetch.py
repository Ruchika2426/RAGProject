import os
import time
import requests
from urllib.parse import urlparse
from datetime import datetime

URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

def fetch_data():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_dir = os.path.join("data", "raw", timestamp)
    os.makedirs(raw_dir, exist_ok=True)
    
    print(f"Starting fetch. Saving to {raw_dir}")
    
    for url in URLS:
        try:
            print(f"Fetching: {url}")
            response = requests.get(url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            
            # Extract fund slug for filename
            parsed_url = urlparse(url)
            fund_slug = parsed_url.path.strip("/").split("/")[-1]
            
            file_path = os.path.join(raw_dir, f"{fund_slug}.html")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"  -> Saved to {file_path}")
            
            # Sleep to avoid rate limiting
            time.sleep(2)
        except Exception as e:
            print(f"  -> Error fetching {url}: {e}")

if __name__ == "__main__":
    fetch_data()
