# Raster calculator to find the difference in flood depth between two rasters 
# Calcualtes Afflux Flood modelling results as raster 1 - raster 2
#%%

#load libraries:
import rasterio
from rasterio import Affine
import numpy as np
import os

# this script will execute the following calculation:  raster 1 - raster 2

# File paths

raster_1_path = r"H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_SA_HR_2024\results\With_Road\1_in_100_AEP\016\2d\grids\1_in_100_AEP_Afflux_SA_Haul_Road_With_Road_Run_No_016_002_d_Max.tif"
raster_2_path = r"H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_SA_HR_2024\results\No_road\1_in_100_AEP\012\2d\grids\1_in_100_AEP_Afflux_SA_Haul_Road_No_road_Run_No_012_d_Max.tif"

output_dir = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_SA_HR_2024\results\With_Road\1_in_100_AEP\016\2d\grids'
output_raster_name = r'1_in_100_AEP_Run_16_minus_Run_12_d_Afflux.tif'

# Output file path
output_raster_path = os.path.join(output_dir, output_raster_name)

# Open raster 1
with rasterio.open(raster_1_path) as src1:
    raster_1 = src1.read(1)  # Reading the first band
    profile = src1.profile  # Copy the profile to use in the output raster
    nodata_value = src1.nodata or -999  # Get the NoData value or default to -999

# Open raster 2
with rasterio.open(raster_2_path) as src2:
    raster_2 = src2.read(1)  # Reading the first band

# Perform the raster calculation considering NoData values
result_raster = np.where(
    (raster_1 != nodata_value) & (raster_2 != nodata_value),  # Condition: both have valid data
    raster_1 - raster_2,  # Perform subtraction where both have valid data
    np.where(  # Nested where to handle NoData conditions
        (raster_1 != nodata_value) & (raster_2 == nodata_value),  # raster_1 has data, raster_2 is NoData
        raster_1,  # Keep raster_1's value
        nodata_value  # If both are NoData, set to NoData
    )
)

# Update the profile to reflect the number of layers (bands) in the output raster
profile.update(dtype=rasterio.float32, count=1, nodata=nodata_value)

# Write the result to a new raster file
with rasterio.open(output_raster_path, 'w', **profile) as dst:
    dst.write(result_raster.astype(rasterio.float32), 1)  # Write the result raster to the first band

print(f"Raster subtraction complete. Result saved to {output_raster_path}")
#%%