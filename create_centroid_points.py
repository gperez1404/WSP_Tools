# This script creates points with the centroids of an input polygon shapefile

#%%
import os
import geopandas as gpd
from shapely.geometry import Point

from pyproj import CRS


# Inputs:
#----------------------------------------------------------------------------------------------------------------

# Input and output variables
input_shp_polygon = r"H:\ProjectsAU\PS212240 - SoE_Expansion_FA\03_GIS\shps\Catchment_delineation\Catchment_1_delineated_with_Mosaic_DEM_10m_v2024.shp"
ID_field = 'ID'
output_location = r'H:\ProjectsAU\PS212240 - SoE_Expansion_FA\03_GIS\shps\Catchment_delineation'
desired_CRS = 28354 # EPSG:28354 - GDA94 / MGA zone 54
#----------------------------------------------------------------------------------------------------------------

# Get the input file name without extension
input_file_name = os.path.splitext(os.path.basename(input_shp_polygon))[0]

# Define the output shapefile path
output_file = os.path.join(output_location, f'centroids_{input_file_name}.shp')

# Define the output shapefile path
output_file = os.path.join(output_location, f'centroid_{input_file_name}.shp')

# Read the input shapefile using Geopandas
gdf = gpd.read_file(input_shp_polygon)

# Ensure the input file has the necessary 'ID_field'
if ID_field not in gdf.columns:
    raise ValueError(f"The input shapefile does not contain the specified ID field: {ID_field}")

# Reproject input shapefile if needed
if gdf.crs is None:
    # Handle the case where the CRS is not set
    print(f"CRS is missing for {os.path.basename(input_shp_polygon)}.shp... Default CRS will be assigned EPSG: {desired_CRS}")
    # Assign the default CRS (desired_CRS in this case)
    gdf.set_crs(epsg=desired_CRS, inplace=True)
elif gdf.crs.to_epsg() != desired_CRS:
    # Check if CRS is different from the desired CRS
    print(f"Reprojecting {os.path.basename(input_shp_polygon)}.shp from EPSG:{gdf.crs.to_epsg()} to EPSG:{desired_CRS}...")
    # Reproject to the desired CRS
    gdf = gdf.to_crs(epsg=desired_CRS)
    gdf.to_file(os.path.join(output_location, f'{input_file_name}_reprojected.shp'))
else:
    print(f"{os.path.basename(input_shp_polygon)}.shp is already in the desired CRS: EPSG:{desired_CRS}")

# Create lists to store the centroids and their attributes
centroid_geometry = []
centroid_ids = []
centroid_x_coords = []
centroid_y_coords = []

# Iterate over each row in the GeoDataFrame
for idx, row in gdf.iterrows():
    # Check if the geometry is a polygon or multipolygon
    if row['geometry'].geom_type in ['Polygon', 'MultiPolygon']:
        # Calculate the centroid
        centroid = row['geometry'].centroid
        centroid_geometry.append(Point(centroid.x, centroid.y))
        centroid_ids.append(row[ID_field])
        centroid_x_coords.append(centroid.x)
        centroid_y_coords.append(centroid.y)
    else:
        print(f"Warning: Row {idx} does not contain a Polygon or MultiPolygon. Skipping...")

# Create a new GeoDataFrame for the centroids with the required attributes
centroid_gdf = gpd.GeoDataFrame({
    'ID': centroid_ids,
    'x_coord': centroid_x_coords,
    'y_coord': centroid_y_coords,
    'geometry': centroid_geometry
}, crs=gdf.crs)

# Save the centroids as a new shapefile
centroid_gdf.to_file(output_file)


# Load the shapefile to add coordinates
gdf = gpd.read_file(output_file)

# Get the CRS of the original shapefile
original_crs = gdf.crs

# Define the WGS 1984 CRS (EPSG:4326)
wgs84_crs = CRS.from_epsg(4326)

# Reproject the GeoDataFrame to WGS 1984 for coordinate calculation
gdf_wgs84 = gdf.to_crs(wgs84_crs)

# Calculate X (Longitude) and Y (Latitude) with 4 decimal places
gdf['X_WGS84'] = gdf_wgs84.geometry.x.round(4)
gdf['Y_WGS84'] = gdf_wgs84.geometry.y.round(4)

# Save back to the same file (overwriting the original file)
gdf.to_file(output_file)

# Clean up temporary GeoDataFrame in memory
del gdf_wgs84

print("X and Y coordinates have been added to the shapefile.")

print(f"Centroid shapefile saved at: {output_file}")

#%%
