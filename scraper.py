import os
import json
import requests
import gspread
from bs4 import BeautifulSoup

def scrape_sapol_full_week():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations"
    
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
        # --- GOOGLE SHEETS UPLOAD ---
if __name__ == "__main__":
    data = scrape_sapol_full_week()

    if data:
        print(f"Found {len(data)} Metropolitan entries. Connecting to Google Sheets...")
        
        # Load Credentials from GitHub Secrets
        creds_json = os.environ.get('GOOGLE_CREDS')
        sheet_id = os.environ.get('SHEET_ID')
        
        if not creds_json or not sheet_id:
            print("Error: Missing GOOGLE_CREDS or SHEET_ID secrets.")
        else:
            creds = json.loads(creds_json)
            gc = gspread.service_account_from_dict(creds)
            sh = gc.open_by_key(sheet_id)
            worksheet = sh.get_worksheet(0)
            
            # Clear and Update
            worksheet.clear()
            headers = [["Day/Date", "Street Name", "Suburb"]]
            worksheet.update(values=headers, range_name="A1")
            worksheet.append_rows(data)
            print("Successfully updated Google Sheet!")
    else:
        print("Scraper finished but no data was found.")
