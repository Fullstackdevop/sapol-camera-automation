import osmnx as ox
import gspread
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import os

# 1. AUTHENTICATE
# We will store the JSON key in GitHub Secrets later
creds_dict = json.loads(os.environ['GOOGLE_CREDS'])
gc = gspread.service_account_from_dict(creds_dict)
sh = gc.open_by_key(os.environ['SHEET_ID'])
worksheet = sh.get_worksheet(0)

# 2. SCRAPE SAPOL
url = "https://www.police.sa.gov.au/your-safety/road-safety/traffic-camera-locations/mobile-camera-container"
soup = BeautifulSoup(requests.get(url).text, 'html.parser')

# Logic to grab Wednesday's data specifically
# (Simplified for the example)
target_day = "Wednesday"
locations = ["ADDISON RD, PENNINGTON", "MAIN NORTH RD, GEPPS CROSS"] 

# 3. GET FULL ROAD GEOMETRY
data = []
for loc in locations:
    try:
        # Search for the street within the suburb
        query = f"{loc}, South Australia"
        graph = ox.graph_from_address(query, dist=1000, network_type='drive')
        edges = ox.graph_to_gdfs(graph, nodes=False)
        
        # Get the LineString (WKT)
        wkt_line = edges.unary_union.wkt
        data.append([target_day, loc, wkt_line])
    except Exception as e:
        print(f"Error finding {loc}: {e}")

# 4. UPDATE SHEET
worksheet.clear()
worksheet.update('A1', [["Day", "Location", "WKT"]])
worksheet.append_rows(data)
