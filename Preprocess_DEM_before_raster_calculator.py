# This script helps the user fix those holes and no value data in a surface DEM

#%%
import rasterio
import geopandas as gpd
import numpy as np
import os
from rasterio.features import geometry_mask

# Define input and output file paths
working_folder = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\02_DEMs_LiDAR\01_Final_Mosaic_DEM'

input_file = "Mosaic_DEM_AHD_1m_v4_trimmed_to_tidal_area.tif"
output_file = "Mosaic_DEM_AHD_1m_v4_trimmed_to_tidal_area_infilled.tif"

# shapefile to check that no values inside the raster are lower than sea level
shp_extent_path = r'U:\Transition\Golder\Brisbane\CAD\ss\Arraw_dam\Derived_Shps\Potential_Flood_extent_Dam_Break_Arraw_Dam.shp'

# Define the values to fix your surface before executing another tool

fill_value = -1 # this is sea level elevation

input = os.path.join(working_folder, input_file)
output = os.path.join(working_folder, output_file)

# Load the shapefiles
gdf_extent_analysis = gpd.read_file(shp_extent_path)

# Open the input DEM
with rasterio.open(input) as src:
    
    # Read the DEM data
    dem_data = src.read(1)
    
    # Create mask
    mask = geometry_mask(gdf_extent_analysis.geometry, transform=src.transform, invert=True, out_shape=src.shape)
    
    # Replace NaN values  with the fill value ( this is the lowest possible elevation)
    dem_data_filled = np.copy(dem_data)
    dem_data_filled[mask & np.isnan(dem_data)] = fill_value
    
    # Replace any values within the mask that are lower than the fill_value (sea level)
    #dem_data_filled[mask & (dem_data_filled < fill_value)] = fill_value

    # Update the metadata to reflect the output file
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "nodata": fill_value
    })

# Write the filled DEM to the output file
with rasterio.open(output, 'w', **out_meta) as dest:
    dest.write(dem_data_filled, 1)

print(f"Holes and abnormal low pixels within the shapefile boundary filled. DEM saved as: {output}")

#%%