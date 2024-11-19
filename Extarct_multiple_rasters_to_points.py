# Extract raster values to points

# This script loads as input a shapefile and an input raster and 
# then extracts the raster values to the points 

#%%
import os
import rasterio
import geopandas as gpd
import pandas as pd
from rasterio import features
from shapely.geometry import Point

# Inputs
input_shp = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\shapes\Catchment_draining_to_ArrawDam\UPS_DS_points_DRAINS.shp'
point_ID_col = 'name'

location_rasters_h = r'C:\GPM_CD\07-Python\inputs\rasters_h'
location_rasters_d = r'C:\GPM_CD\07-Python\inputs\rasters_d'

CRS_for_analysis = 'EPSG:28354'  # GDA94 / MGA zone 54

output_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_SA_HR_2024\results'
results_file = r'python_extraction.xlsx'

# Step 1: Get the raster file names from the specified directories
files_h = [f for f in os.listdir(location_rasters_h) if f.endswith('.tif')]
files_d = [f for f in os.listdir(location_rasters_d) if f.endswith('.tif')]

# Step 2: Create full paths for the raster files
file_path_h_rasters = [os.path.join(location_rasters_h, f) for f in files_h]
file_path_d_rasters = [os.path.join(location_rasters_d, f) for f in files_d]

# Step 3: Load the shapefile and reproject it to the desired CRS
shp_points = gpd.read_file(input_shp)

# Reproject to the target CRS if necessary
if shp_points.crs != CRS_for_analysis:
    print(f"Reprojecting shapefile from {shp_points.crs} to {CRS_for_analysis}")
    shp_points = shp_points.to_crs(CRS_for_analysis)

# Step 4: Function to extract raster values at point locations
def extract_raster_values(raster_path, points_gdf, point_ID_col):
    extracted_values = []
    with rasterio.open(raster_path) as src:
        for idx, row in points_gdf.iterrows():
            point_coords = [(row.geometry.x, row.geometry.y)]
            for val in src.sample(point_coords):
                extracted_values.append({
                    point_ID_col: row[point_ID_col],
                    'raster': os.path.basename(raster_path),
                    'value': val[0]  # Assuming single band raster
                })
    return extracted_values

# Step 5: Loop over rasters and extract values for all points
all_extracted_values = []

# Process 'h' rasters
for raster_file in file_path_h_rasters:
    print(f"Extracting values from {raster_file}")
    all_extracted_values.extend(extract_raster_values(raster_file, shp_points, point_ID_col))

# Process 'd' rasters
for raster_file in file_path_d_rasters:
    print(f"Extracting values from {raster_file}")
    all_extracted_values.extend(extract_raster_values(raster_file, shp_points, point_ID_col))

# Step 6: Save extracted values to an Excel file
df_extracted = pd.DataFrame(all_extracted_values)

output_path = os.path.join(output_location, results_file)
df_extracted.to_excel(output_path, index=False)

print(f"Extraction complete. Results saved to {output_path}")

#%%