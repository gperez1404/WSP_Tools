# This script crates Z shape poitns along a Z shape line and extracts elevation values to them
# based on an input raster with elevations

# All layers must be in the same CRS

#%%
import os
import pandas as pd
import geopandas as gpd
import rasterio
from shapely.geometry import Point, LineString
from rasterio.sample import sample_gen

# Inputs:
#------------------------------------------------------------------------------------------------------------------

Template_layer_with_points = r"C:\GPM_CD\12-fast_exe\GIS\TUFLOW_SoEE_FS_2024\model\gis\2d_zsh_SoEE_rds_crest_000_P.shp"
input_layer_with_lines = r"C:\GPM_CD\12-fast_exe\GIS\TUFLOW_SoEE_FS_2024\model\gis\2d_zsh_SoEE_rds_crest_001_L.shp"

interpol_dist = 100 # distance between points in meters

raster_with_elevation = r"C:\GPM_CD\12-fast_exe\GIS\TUFLOW_SoEE_FS_2024\model\grid\Combined_embankments_1m.tif"

output_layer_location =r'C:\GPM_CD\12-fast_exe\GIS\TUFLOW_SoEE_FS_2024\model\gis'
output_layer_name = r'2d_zsh_SoEE_rds_crest_001_P.shp'

#------------------------------------------------------------------------------------------------------------------


# start :
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

# Load the shapefiles
layer_points = gpd.read_file(Template_layer_with_points)
layer_lines = gpd.read_file(input_layer_with_lines)

# Load the raster file
terrain_raster = rasterio.open(raster_with_elevation)


# Function to generate points every X meters along a line
def generate_points_along_line(line, spacing=interpol_dist):
    num_points = int(line.length // spacing)
    return [line.interpolate(i * spacing) for i in range(num_points + 1)]

# Create new points along each line in layer_lines
new_points = []
for _, line in layer_lines.iterrows():
    if isinstance(line.geometry, LineString):
        points = generate_points_along_line(line.geometry)
        for point in points:
            # Create new point with default attributes
            new_point = {
                'geometry': point,
                'Z': 0,                # Default value as per the requirement
                'dZ': 0,               # Default value as per the requirement
                'Shape_Widt': 0,       # Default value as per the requirement
                'Shape_Opti': ''       # You can change the value if needed
            }
            new_points.append(new_point)

# Convert the list of new points to a GeoDataFrame
new_points_gdf = gpd.GeoDataFrame(new_points, crs=layer_points.crs)

# Now extract elevation values from the raster for each new point
for i, point in new_points_gdf.iterrows():
    coord = [(point.geometry.x, point.geometry.y)]
    for val in terrain_raster.sample(coord):
        new_points_gdf.at[i, 'Z'] = float(f"{val[0]:.3f}")  # Update 'Z' with formatted value

# Concatenate the original layer_points and the new_points_gdf
updated_layer_points = gpd.GeoDataFrame(pd.concat([layer_points, new_points_gdf], ignore_index=True), crs=layer_points.crs)

# Save the updated points (original + new points) to the same shapefile or a new one
new_file_path =os.path.join(output_layer_location,output_layer_name)
updated_layer_points.to_file(new_file_path, driver="ESRI Shapefile")

print( f'layer created at: {new_file_path}')
# Close the raster file
terrain_raster.close()

# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
#%%