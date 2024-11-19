
# This script merge different shapefiles given they all have an attribute named "ID"
# the attribute "ID" should be numeric
#%%
# Libraries
#--------------------------------------------------------------------------
import os
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
from pyproj import CRS  # Import from pyproj for CRS handling
#--------------------------------------------------------------------------

# Inputs
#-------------------------------------------------------------------------- 
path_to_load_shps = r'U:\Transition\Golder\Brisbane\CAD\ss\BHP_OD_TSF1_TSF2_3_TSF4\SSAC_TSF1_TSF2_3_TSF_4\data'
path_to_save_output = r'U:\Transition\Golder\Brisbane\CAD\ss\BHP_OD_TSF1_TSF2_3_TSF4\SSAC_TSF1_TSF2_3_TSF_4\data'

shapefiles = ["Crest_TSF1_crs_28353_GDA94.shp","Crest_TSF2_3_crs_28353_GDA94.shp","Crest_TSF4_crs_28353_GDA94.shp"]
desired_CRS = 'EPSG:28353'
output_filename = "Crest_TSF1_TSF_2_3_TSF4_crs_28353_GDA94.shp"
#--------------------------------------------------------------------------

# Define functions
#-------------------------------------------------------------------------- 

def validate_crs(crs_input):
    try:
        # Attempt to create a CRS object using pyproj
        crs = CRS.from_user_input(crs_input)
        return crs
    except ValueError:
        raise ValueError(f"Invalid CRS: {crs_input}")

def merge_shapefiles(path_to_load_shps, shapefile_list, desired_crs):
    # Validate and set the CRS
    crs = validate_crs(desired_crs)
    
    # List to store the loaded GeoDataFrames
    gdf_list = []
    
    for shapefile in shapefile_list:
        # Load the shapefile
        shp_path = os.path.join(path_to_load_shps, shapefile)
        gdf = gpd.read_file(shp_path)
        
        # Check if the CRS matches the desired CRS, reproject if necessary
        if gdf.crs != crs:
            gdf = gdf.to_crs(crs.to_string())
        
        # Normalize the 'ID' column
        id_column = None
        for col in gdf.columns:
            if col.lower() == 'id':
                id_column = col
                break
        
        if id_column is None:
            raise KeyError(f"'ID' column not found in shapefile: {shapefile}")
        
        # Rename the ID column to 'ID' and select only 'ID' and 'geometry' columns
        gdf = gdf.rename(columns={id_column: 'ID'})[['ID', 'geometry']]
        
        # Append to the list
        gdf_list.append(gdf)
    
    # Merge all GeoDataFrames into one
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdf_list, ignore_index=True), crs=crs.to_string())
    
    # Calculate area in square meters and hectares
    merged_gdf['Area_m2'] = merged_gdf['geometry'].area
    merged_gdf['Area_ha'] = merged_gdf['Area_m2'] / 10000
    
    return merged_gdf

def save_shapefile(gdf, output_filename):
    gdf.to_file(output_filename)

# ----------------------------------------------------------------------------------------

merged_gdf = merge_shapefiles(path_to_load_shps, shapefiles, desired_CRS)

output_path = os.path.join(path_to_save_output, output_filename)

save_shapefile(merged_gdf, output_path)

print(f"Merged shapefile saved as {output_path}")
#------------------------------------------------------------------------------------->End


#%%