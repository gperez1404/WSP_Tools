#%%
import os
import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape

# Inputs
input_file_location = r"C:\Users\AUGM509787\OneDrive - WSP O365\GPM\02_Projects\Arraw_Dam_FIA_CCA\05_GIS\03_rasters_local\DEMs_local\Unknow_source_Hydro_enforced_DEM_30m.tif"
output_location = r'C:\Users\AUGM509787\OneDrive - WSP O365\GPM\02_Projects\Arraw_Dam_FIA_CCA\05_GIS\02_shps_local'

# Determine the file extension
extension_input_file = str(os.path.splitext(input_file_location)[1])

# Define output shapefile name
output_shapefile = os.path.join(output_location, "Extent_" + os.path.basename(input_file_location).replace(extension_input_file, '.shp'))

# Open the TIFF  file
with rasterio.open(input_file_location) as src:
    # do something
    print('you have not written this part of the script')
    
print(f"Shapefile saved at: {output_shapefile}")
#%%