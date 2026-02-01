def scrape_sapol_full_week():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
    
    # This header mimics a standard Windows Chrome browser
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print("Error 403: SAPOL is blocking the GitHub server. Trying alternative headers...")
            return []
        print(f"HTTP Error: {e}")
        return []
    except Exception as e:
        print(f"Network Error: {e}")
        return []
