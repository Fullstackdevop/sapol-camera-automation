import os
import json
import requests
import gspread
from bs4 import BeautifulSoup

def scrape_sapol_full_week():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"Network Error: {e}")
        return []
    
    all_data = []
    
    # 1. Identify the Metropolitan section
    # We find the H2 that says 'Metropolitan traffic camera locations'
    metro_header = soup.find(lambda tag: tag.name == "h2" and "Metropolitan" in tag.text)
    # The Country section marks the end of our target data
    country_header = soup.find(lambda tag: tag.name == "h2" and "Country" in tag.text)

    if not metro_header:
        print("Could not find Metropolitan header.")
        return []

    # 2. Iterate through siblings until we hit Country or end of page
    current_node = metro_header.find_next_sibling()
    current_day_text = "Unknown Day"

    while current_node and current_node != country_header:
        text_content = current_node.get_text(separator=" ").strip()
        
        if not text_content:
            current_node = current_node.find_next_sibling()
            continue

        # Check if this node is a Date Header (e.g., 'Wednesday, 28 January 2026')
        days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        if any(day in text_content for day in days_of_week):
            current_day_text = text_content
        
        # If the node contains a comma, it's likely a list of 'STREET, SUBURB'
        elif "," in text_content:
            # SAPOL sometimes puts multiple addresses in one paragraph separated by newlines
            lines = text_content.split('\n')
            for line in lines:
                if "," in line:
                    parts = line.split(',')
                    street = parts[0].strip().upper()
                    suburb = parts[1].strip().upper() if len(parts) > 1 else ""
                    all_data.append([current_day_text, street, suburb])
        
        current_node = current_node.find_next_sibling()
            
    return all_data

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
