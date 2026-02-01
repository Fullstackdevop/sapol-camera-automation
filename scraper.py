import osmnx as ox
from shapely import wkt

def get_street_geometry(street_name, suburb):
    query = f"{street_name}, {suburb}, South Australia"
    try:
        # 1. Fetch the road network
        graph = ox.graph_from_address(query, dist=1000, network_type='drive')
        edges = ox.graph_to_gdfs(graph, nodes=False)
        
        # 2. Filter for the specific street name
        street_gdf = edges[edges['name'].str.contains(street_name, case=False, na=False)]
        
        # 3. Combine segments into one geometry
        combined_geom = street_gdf.union_all()
        
        # 4. SIMPLIFY (The Fix)
        # 0.0001 is roughly 10 meters. It removes tiny zig-zags to save space.
        simplified_geom = combined_geom.simplify(0.0001, preserve_topology=True)
        
        # 5. Convert to WKT and Check Length
        wkt_text = simplified_geom.wkt
        
        if len(wkt_text) > 45000:
            # If still too big, simplify even more (roughly 50 meters)
            wkt_text = simplified_geom.simplify(0.0005).wkt
            
        return wkt_text
    except Exception as e:
        print(f"Skipping {street_name}: {e}")
        return None
