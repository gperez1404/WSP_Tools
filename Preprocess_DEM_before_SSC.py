# This script helps the user fix those holes in LiDAR data due to decant pond water
# Lidar produces error when there is water over the surface of the tailings.
# this script helps the user to infill those holes with known values based on DEM analysis 
# manual delineation of the polygon with the pond extent as inferred from high resolution iamgery

#%%
import rasterio
import geopandas as gpd
import numpy as np
import os
from rasterio.features import geometry_mask

# Define input and output file paths
working_folder = r'U:\Transition\Golder\Brisbane\CAD\ss\BHP_OD_TSF1_TSF2_3_TSF4\September_2020'

input_file = "BHP_TRS_SouthernArea_September_2020_DEM_50cm.tif"
output_file = "Mosaic_DEM_AHD_1m_v4_infilled_v1.tif"

# shapefile with the crest of the TSF to check that no values inside the inpoundment are lower than the pond elevation
shp_crest_path = r'U:\Transition\Golder\Brisbane\CAD\ss\BHP_OD_TSF1_TSF2_3_TSF4\SSAC_TSF4\data\Crest_TSF4_crs_28353_GDA94.shp'

# shapefile with the crest of the TSF to check that no values inside the inpoundment are lower than the pond elevation
shp_pond_path = r'U:\Transition\Golder\Brisbane\CAD\ss\BHP_OD_TSF1_TSF2_3_TSF4\SSAC_TSF4\data\Initial_pond_area_TSF4_September_2020.shp'

# Define the values to fix your surface before executing the SSC tool

fill_value = 0 # this is the pond elevation any value lower than this will be automaticaly set to this value
Base_terrain_value = 0 # base of the DEM outside of the TSF

input = os.path.join(working_folder, input_file)
output = os.path.join(working_folder, output_file)

# Load the shapefiles
gdf_Crest = gpd.read_file(shp_crest_path)
gdf_Pond = gpd.read_file(shp_pond_path)

# Open the input DEM
with rasterio.open(input) as src:
    
    # Read the DEM data
    dem_data = src.read(1)
    
    # Create masks for the area covered by the crest and the pond geometries
    mask_crest = geometry_mask(gdf_Crest.geometry, transform=src.transform, invert=True, out_shape=src.shape)
    mask_pond = geometry_mask(gdf_Pond.geometry, transform=src.transform, invert=True, out_shape=src.shape)
    
    # Replace NaN values within the crest (impounded area) with the fill value ( this is the lowest possible elevation)
    dem_data_filled = np.copy(dem_data)
    dem_data_filled[mask_crest & np.isnan(dem_data)] = fill_value
    
    # Replace any values inside the pond that are lower that the pond elevation with the fill value:
    # Replace any values inside the pond that are higher than the pond elevation with the fill value:
    # dem_data_filled[mask_pond & (dem_data_filled > fill_value)] = fill_value
    dem_data_filled[mask_pond] = fill_value
    
    # Replace any values within the crest that are lower than the pond level for the fill_value (pond level)
    dem_data_filled[mask_crest & (dem_data_filled < fill_value)] = fill_value

    # Apply condition to ensure there are no values are lower than Base_terrain_value (outside terrain)
    dem_data_filled[dem_data_filled < Base_terrain_value] = Base_terrain_value
    
    # Update the metadata to reflect the output file
    out_meta = src.meta.copy()
    out_meta.update({
        "driver": "GTiff",
        "nodata": Base_terrain_value
    })

# Write the filled DEM to the output file
with rasterio.open(output, 'w', **out_meta) as dest:
    dest.write(dem_data_filled, 1)

print(f"Holes and low-value pixels within the shapefile boundary filled. DEM saved as: {output}")

#%%