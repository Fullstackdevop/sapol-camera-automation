import numpy as np
from shapely.geometry import LineString

def get_points_every_300m(addr):
    try:
        # 1. Get the road graph
        query = f"{addr}, South Australia"
        graph = ox.graph_from_address(query, dist=1000, network_type='drive')
        
        # 2. Project to a metric CRS (UTM) to measure in meters
        graph_proj = ox.project_graph(graph)
        edges = ox.graph_to_gdfs(graph_proj, nodes=False)
        
        # 3. Merge segments and calculate length
        combined_line = edges.union_all()
        total_length = combined_line.length  # Now in meters
        
        # 4. Generate points every 300m
        distances = np.arange(0, total_length, 300)
        points = [combined_line.interpolate(d) for d in distances]
        
        # 5. Convert back to Lat/Lon (WGS84) for Google Maps
        # We create a temporary GeoSeries to handle the re-projection back
        import geopandas as gpd
        points_gdf = gpd.GeoSeries(points, crs=edges.crs).to_crs("EPSG:4326")
        
        # Return as a MultiPoint WKT string
        return points_gdf.union_all().wkt
    except Exception as e:
        print(f"Error on {addr}: {e}")
        return None
