
#%%
import rasterio
import numpy as np
import os
# Define input and output file paths

working_folder =r'C:\Users\AUGM509787\OneDrive - WSP O365\GPM\02_Projects\BHP_OD_TSFs_flood_levels\GIS\LiDAR\Surveys_TSF4_TSF2_3_TSF1'

input_file = "22A0255_TSF4_Contours_500mm_MGA94z53_ODX_2401_DEM_1m.tif"
output_file = "22A0255_TSF4_Contours_500mm_MGA94z53_ODX_2401_DEM_1m_infilled_v3.tif"

input= os.path.join(working_folder,input_file)
output=os.path.join(working_folder,output_file)

# Define the fixed value to fill the holes
fill_value = 127.68
min_value = 99.40

# Open the input DEM
with rasterio.open(input) as src:
    # Read the DEM data as an array
    dem_data = src.read(1)
    
    # Replace NaN values and values lower than min_value with fill_value
    dem_data_filled = np.where((np.isnan(dem_data)) | (dem_data < min_value), min_value, dem_data)

    # Update the metadata to reflect the output file
    out_meta = src.meta.copy()

# Write the filled DEM to the output file
with rasterio.open(output, 'w', **out_meta) as dest:
    dest.write(dem_data_filled, 1)

print(f"Holes filled and DEM saved as: {output}")
#%%