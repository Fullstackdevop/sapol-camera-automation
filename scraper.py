import os
import json
import requests
import gspread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def scrape_sapol_full_week():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    all_data = []
    
    # 1. Locate the Metropolitan container
    # SAPOL typically lists Metropolitan first, followed by Country
    metro_section = soup.find(lambda tag: tag.name == "h2" and "Metropolitan" in tag.text)
    country_section = soup.find(lambda tag: tag.name == "h2" and "Country" in tag.text)

    if not metro_section:
        return []

    # 2. Iterate through elements between Metropolitan and Country headers
    current_node = metro_section.find_next_sibling()
    current_day = None
    current_date = None

    while current_node and current_node != country_section:
        text = current_node.get_text().strip()
        
        # Identify Day/Date Headers (e.g., "Wednesday, 28 January 2026")
        if any(day in text for day in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]):
            parts = text.split(',')
            current_day = parts[0].strip()
            current_date = parts[1].strip() if len(parts) > 1 else ""
        
        # Identify Address Blocks
        elif current_day and current_node.name in ['p', 'div']:
            # Split by newlines or dots which SAPOL uses as separators
            lines = text.replace('.', '\n').split('\n')
            for line in lines:
                if ',' in line:
                    addr_parts = line.split(',')
                    street = addr_parts[0].strip().upper()
                    suburb = addr_parts[1].strip().upper()
                    all_data.append([current_day, current_date, street, suburb])
        
        current_node = current_node.find_next_sibling()
            
    return all_data

# --- MAIN EXECUTION ---
data = scrape_sapol_full_week()

if data:
    creds = json.loads(os.environ['GOOGLE_CREDS'])
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key(os.environ['SHEET_ID'])
    worksheet = sh.get_worksheet(0)
    
    worksheet.clear()
    headers = [["Day", "Date", "Street Name", "Suburb"]]
    worksheet.update(values=headers, range_name="A1")
    worksheet.append_rows(data)
    print(f"Success! Uploaded {len(data)} Metropolitan entries.")
else:
    print("Scraper failed to find Metropolitan data sections.")                    raw_text = locations_node.get_text().replace('.', '\n')
                    for line in raw_text.split('\n'):
                        if ',' in line:
                            parts = line.split(',')
                            street = parts[0].strip().upper()
                            suburb = parts[1].strip().upper()
                            found_data.append(["Wednesday", current_date, street, suburb])
            current_node = current_node.find_next_sibling()
            
    return found_data

# --- MAIN RUN ---
data = scrape_sapol_metro()

if data:
    # Connect to Sheets
    creds = json.loads(os.environ['GOOGLE_CREDS'])
    gc = gspread.service_account_from_dict(creds)
    sh = gc.open_by_key(os.environ['SHEET_ID'])
    worksheet = sh.get_worksheet(0)
    
    # Update Sheet with headers
    worksheet.clear()
    headers = [["Day", "Date", "Street Name", "Suburb"]]
    worksheet.update(headers, "A1")
    worksheet.append_rows(data)
    print(f"Success! Uploaded {len(data)} Metropolitan cameras.")
else:
    print("Scraper failed to find Wednesday Metropolitan data. Check the website HTML.")
