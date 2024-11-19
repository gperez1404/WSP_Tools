# Extract raster values to points

# This script loads as input a shapefile and an input raster and 
# then extracts the raster values to the points 

#%%
# Libraries:
#------------------------------------------------------------------------------------------------
import os
import geopandas as gpd
import rasterio
from shapely.geometry import Point, MultiPoint  # Ensure MultiPoint is imported
import numpy as np

#------------------------------------------------------------------------------------------------

# Inputs
#------------------------------------------------------------------------------------------------
input_shp = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\shapes\Catchment_draining_to_ArrawDam\UPS_DS_points_DRAINS.shp'
input_raster =r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\02_DEMs_LiDAR\01_Final_Mosaic_DEM\Mosaic_DEM_AHD_1m_v1_Catchment_1.tif'

col_name_raster_value =r'Elev_m'

output_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\shapes\Catchment_draining_to_ArrawDam'
#------------------------------------------------------------------------------------------------

# Start 
#------------------------------------------------------------------------------------------------

# Deriving input filename and stripping ".shp" if present
input_file_name = os.path.basename(input_shp)
if input_file_name.lower().endswith('.shp'):
    input_file_name = input_file_name[:-4]

# Define output filename
output_filename = f'{input_file_name}_with_{col_name_raster_value}.shp'
output_shp_path = os.path.join(output_location, output_filename)

# Load shapefile
shapefile = gpd.read_file(input_shp)

# Load raster and check CRS
with rasterio.open(input_raster) as src:
    raster_crs = src.crs
    raster_transform = src.transform
    raster_band = src.read(1)  # Assuming we're working with the first band
    nodata_value = src.nodata  # Get the NoData value from the raster

# Ensure the shapefile has the same CRS as the raster
if shapefile.crs != raster_crs:
    print(f"Reprojecting shapefile from {shapefile.crs} to {raster_crs}")
    shapefile = shapefile.to_crs(raster_crs)

# Function to get the raster value at a point
def get_raster_value(point, raster_band, transform, nodata_value):
    # Transform point coordinates to row, col of raster
    row, col = ~transform * (point.x, point.y)
    row, col = int(row), int(col)

    # Ensure the point is within the raster bounds
    if 0 <= row < raster_band.shape[0] and 0 <= col < raster_band.shape[1]:
        value = raster_band[row, col]
        # Check if the value is a NoData value
        if value == nodata_value:
            return np.nan  # Return NaN if the value is NoData
        return value
    else:
        return np.nan  # Return NaN if the point is outside the raster bounds

# Helper function to handle both Point and MultiPoint geometries
def extract_raster_value_from_geometry(geom, raster_band, transform, nodata_value):
    if isinstance(geom, Point):
        return get_raster_value(geom, raster_band, transform, nodata_value)
    elif isinstance(geom, MultiPoint):
        # Process each point in the MultiPoint and return the average raster value (or use another strategy)
        values = [get_raster_value(pt, raster_band, transform, nodata_value) for pt in geom]
        valid_values = [v for v in values if not np.isnan(v)]  # Filter out any NaN values
        if valid_values:
            return np.mean(valid_values)  # Return the average value
        else:
            return np.nan  # Return NaN if no valid values
    else:
        return np.nan  # Handle other geometry types if necessary

# Extract raster values for each point in the shapefile
shapefile[col_name_raster_value] = shapefile.geometry.apply(lambda geom: extract_raster_value_from_geometry(geom, raster_band, raster_transform, nodata_value))

# Add x and y coordinates to the shapefile for Point geometries only
shapefile['x_coord'] = shapefile.geometry.apply(lambda geom: geom.x if isinstance(geom, Point) else np.nan)
shapefile['y_coord'] = shapefile.geometry.apply(lambda geom: geom.y if isinstance(geom, Point) else np.nan)

# Define the data type for the new column (Double, 16 digits, 2 decimals)
shapefile[col_name_raster_value] = shapefile[col_name_raster_value].astype(float).round(2)

# Save the new shapefile with the raster values and coordinates
shapefile.to_file(output_shp_path, driver='ESRI Shapefile')

print(f"New shapefile created at {output_shp_path}")
# %%
