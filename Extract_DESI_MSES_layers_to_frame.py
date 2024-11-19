# This code extracts the MSES layers to an specific Frame window using 
# the inputs given by the user

# Warning !!
# if you run this script on your laptop it can take up to 1 hour to execute !!
# input layers are too big to be handled efficently 

#%%
import os
import geopandas as gpd

# Inputs
#----------------------------------------------------------------------------------------> start
path_to_MSES_data = r'C:\GPM_CD\14_GIS\MSES layers' # This normally does not change

path_to_save_results = r'C:\GPM_CD\Fig_gen_PS211032_106_FIA_local\data_input\shp' # Adjust path if needed
shp_frame_to_extract_data = gpd.read_file(r"C:\GPM_CD\Fig_gen_PS211032_106_FIA_local\data_input\shp\Frame_to_extract_DES_MSES_data.shp")  # Adjust path if needed
#----------------------------------------------------------------------------------------> End
# Get CRS of the overlay layer (shp_frame_to_extract_data)
overlay_crs = shp_frame_to_extract_data.crs

# Step 1: Create list of shapefile paths
list_of_shps_MSES = [os.path.join(path_to_MSES_data, file) for file in os.listdir(path_to_MSES_data) if file.endswith('.shp')]

# Step 2: Clip each shapefile in list_of_shps_MSES and save the output
for shp_file in list_of_shps_MSES:
    try:
        # Read the input shapefile
        gdf = gpd.read_file(shp_file)
        
        # Check and align CRS with overlay layer
        if gdf.crs != overlay_crs:
            gdf = gdf.to_crs(overlay_crs)
        
        # Perform the clip operation
        clipped_gdf = gpd.clip(gdf, shp_frame_to_extract_data)
        
        # Construct output file path
        output_file = os.path.join(path_to_save_results, os.path.basename(shp_file))
        
        # Save the clipped shapefile
        clipped_gdf.to_file(output_file)
        
        print(f"Clipped and saved {os.path.basename(output_file)}")
    
    except Exception as e:
        print(f"Error processing {shp_file}: {e}")
#%%