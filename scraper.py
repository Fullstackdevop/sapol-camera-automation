import os
import json
import requests
import gspread
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_next_wednesday():
    # Returns the date for the coming Wednesday
    today = datetime.now()
    days_ahead = (2 - today.weekday()) % 7 # 2 is Wednesday
    if days_ahead == 0: days_ahead = 7
    return (today + timedelta(days=days_ahead)).strftime('%d/%m/%Y')

def scrape_sapol_metro():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    found_data = []
    current_date = get_next_wednesday()

    # 1. Find the "Metropolitan" section
    metro_header = soup.find(lambda tag: tag.name == "h3" and "Metropolitan" in tag.text)
    
    if metro_header:
        # 2. Look for the Wednesday block following that header
        # We search siblings until we hit another major section
        current_node = metro_header.find_next_sibling()
        while current_node and current_node.name != "h2":
            if "Wednesday" in current_node.text:
                # The text usually follows in the next <p> tag
                locations_node = current_node.find_next_sibling("p")
                if locations_node:
                    # Clean the string (it's often one big blob with dots or newlines)
                    raw_text = locations_node.get_text().replace('.', '\n')
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
