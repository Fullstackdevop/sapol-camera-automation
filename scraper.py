import os
import json
import requests
import pandas as pd
import osmnx as ox
import gspread
from bs4 import BeautifulSoup
from shapely import wkt

def get_wednesday_locations():
    url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Target the Wednesday Metropolitan section
    target_header = soup.find(['h3', 'strong'], string=lambda t: "Wednesday" in t if t else False)
    if not target_header:
        return []
    
    # SAPOL often puts addresses in the next <p> or <div> block
    content_block = target_header.find_next(['p', 'div'])
    if not content_block:
        return []
        
    raw_text = content_block.get_text(separator="\n")
    locations = [loc.strip() for loc in raw_text.split('\n') if loc.strip() and ',' in loc]
    return locations

def get_simplified_geometry(addr):
    try:
        # Request road data within 1km of the address
        query = f"{addr}, South Australia"
        graph = ox.graph_from_address(query, dist=1000, network_type='drive', truncate_by_edge=True)
        edges = ox.graph_to_gdfs(graph, nodes=False)
        
        # Merge all road segments into one line
        combined = edges.union_all()
        
        # Aggressive simplification (0.0005 is roughly 50m precision)
        # This keeps the shape but slashes the character count significantly
        simplified = combined.simplify(0.0005, preserve_topology=True)
        
        wkt_out = simplified.wkt
        # Final safety check for Google Sheets cell limit
        if len(wkt_out) > 48000:
            return simplified.simplify(0.002).wkt
        return wkt_out
    except:
        return None

# --- MAIN EXECUTION ---
if __name__ == "__main__":
    # 1. Scrape
    loc_list = get_wednesday_locations()
    print(f"Found {len(loc_list)} locations.")

    # 2. Get Geometry
    data_rows = []
    for loc in loc_list:
        geom = get_simplified_geometry(loc)
        if geom:
            data_rows.append(["Wednesday", loc, geom])
            print(f"Success: {loc}")

    # 3. Push to Google Sheets
    if data_rows:
        creds = json.loads(os.environ['GOOGLE_CREDS'])
        gc = gspread.service_account_from_dict(creds)
        sh = gc.open_by_key(os.environ['SHEET_ID'])
        worksheet = sh.get_worksheet(0)
        
        # Clear and update
        worksheet.clear()
        # Modern gspread update format: (values, range_name)
        headers = [["Day", "Location", "WKT"]]
        worksheet.update(headers, "A1") 
        worksheet.append_rows(data_rows)
        print("Sheet updated successfully!")
    else:
        print("No data to upload.")
