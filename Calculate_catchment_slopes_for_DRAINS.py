
# This script calculates the Average Slope of a Catchment to use in DRAINS

# The slope of a catchment in percent can be calculated as:

# Slope (%) = [ (ΔH)/ L ] × 100

# where:

# ΔH is the change in elevation across the catchment (usually the difference 
# between the maximum and minimum elevations).

# L is the flow path length or the distance over which the elevation change occurs 
# (typically the length of the main river or flow path within the catchment).

# This can be calculated by calcualting the slope of the DEM raster within 
# the catchment boundaries 
# using the Spatial Analyst tools available in GIS software like QGIS or ArcGIS.

# Slope is often represented in Percentage (%) and Degrees

# The Slope in  Degrees calculated using trigonometric functions based on elevation 
# differences and distances.

# Common Range of Values for "Sub Catchment Slope (%)"
# For sub-catchments, slope values generally range from very flat (close to 0%) 
# in plains and flat areas to steep (30% or higher) in mountainous regions. 
# For river catchments, slopes are usually between 0.1% and 15%.

#%%
import rasterio
import geopandas as gpd
import numpy as np
from rasterio.mask import mask
from scipy.ndimage import sobel

#Inputs:
#--------------------------------------------------------> Start

catchment_shapefile = r"U:\Transition\Golder\Brisbane\CAD\ss\FIA_Arraw_Dam\shps\Sub_Catchment_2A.shp"

dem_raster_path = r"U:\Transition\Golder\Brisbane\CAD\ss\FIA_Arraw_Dam\raster\DEM_cat_2A.tif"

#---------------------------------------------------------> End

# Load the catchment shapefile
catchment = gpd.read_file(catchment_shapefile)

# Load the DEM raster
with rasterio.open(dem_raster_path) as src:
    # Mask the DEM with the catchment polygon
    catchment_geom = catchment.geometry.values
    out_image, out_transform = mask(src, catchment_geom, crop=True)
    dem_data = out_image[0]  # Extracting the DEM band

# Calculate the slope in percentage using Sobel gradient
dx = sobel(dem_data, axis=0)  # Gradient in x direction
dy = sobel(dem_data, axis=1)  # Gradient in y direction

# Calculate the slope (rise/run) and convert to percentage
slope_radians = np.arctan(np.sqrt(dx**2 + dy**2))
slope_percent = np.tan(slope_radians) * 100

# Calculate the average slope within the catchment
average_slope = np.nanmean(slope_percent)

print(f"Average Slope (%): {average_slope:.2f}")

#---------------------------------------------------------> End
#%%