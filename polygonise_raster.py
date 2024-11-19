# This script helps you create a mask or polygon from a raster.

# If you look up the minimum and maximum values of your raster in a GIS 
# platform and use them as inputs in this script, you will generate a 
# mask of the raster you selected. This method is far superior to the 
# normal GIS raster extent tool because it will show if your DEM has 
# any holes in it. This is a common issue that crashes raster processes 
# or introduces errors in the results. Having a mask that shows holes 
# in surfaces is very important to ensure high-quality results.

# If the minimum and maximum values are selected as a range of values 
# from the input raster, you will get a polygon extent of the results. 
# This is useful for mapping flood hazards, for example.

# WARNING:

# This code DOES NOT WORK with .ASC files!
# If your input file is an ASC raster or a FLT, you need to export it 
# to a .TIF file first.

#%%

# libraries
#----------------------------------------------------------------------------------------------------------------
import os
import rasterio
import numpy as np
from osgeo import gdal, ogr, osr
#----------------------------------------------------------------------------------------------------------------

# Inputs
#----------------------------------------------------------------------------------------------------------------

# Define file paths
raster_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_FIA_2024\model\grid'
raster_file = r'Mosaic_DEM_1m_AHD_model_extent.tif'

output_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\shapes\shapefiles_2024'

# this parameters define what type of output you will get
lower_bound = -5
upper_boud=  75

# name of the shaepfile output
#extension_input_file = str(os.path.splitext(raster_file)[1])
#name_input_file =  "Extent_" + raster_file.replace(extension_input_file, '.shp')
#output_shapefile =  "Extent_" + name_input_file + '.shp'
output_shapefile = r'Extent_Mosaic_DEM_1m_AHD.shp'

Field_ID = r'ID'

# Additional fields for output shapefile:
Field_name = r'File'
Field_type = ogr.OFTString # ogr.OFTReal
#----------------------------------------------------------------------------------------------------------------


# Start
#----------------------------------------------------------------------------------------------------------------
extension_input_file = str(os.path.splitext(raster_file)[1])

# Check if the DataSource was created successfully
if extension_input_file == ".asc":
    raise RuntimeError(f"You can't run this code with .asc files !")

shp_path = os.path.join(output_location, output_shapefile)

# Raster and output paths
raster_path = os.path.join(raster_location, raster_file)
output_raster = raster_path.replace(extension_input_file, '_mask.tif')

# Define the output driver for the shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")

# Create the output shapefile
if os.path.exists(shp_path):
    driver.DeleteDataSource(shp_path)
out_ds = driver.CreateDataSource(shp_path)

# Check if the DataSource was created successfully
if out_ds is None:
    raise RuntimeError(f"Failed to create the output shapefile at {shp_path}")

# Define the spatial reference based on the raster's projection
with rasterio.open(raster_path) as src:
    srs = osr.SpatialReference()
    srs.ImportFromWkt(src.crs.to_wkt())

    # Create the layer for polygons
    layer_name = os.path.splitext(os.path.basename(output_shapefile))[0]
    out_layer = out_ds.CreateLayer(layer_name, srs=srs, geom_type=ogr.wkbPolygon)
    
    new_field = ogr.FieldDefn(Field_ID, ogr.OFTInteger)
    out_layer.CreateField(new_field)
    
    new_field = ogr.FieldDefn(Field_name, Field_type)
    
    if new_field == ogr.OFTString:
        new_field.SetWidth(100)
    
    out_layer.CreateField(new_field)

    # Read the raster data as a numpy array
    raster_data = src.read(1)

    # Reclassify the raster: set all values between lower_bound and upper_boud to 1, others to 0
    reclassified_data = np.where((raster_data >= lower_bound) & (raster_data <= upper_boud), 1, 0)

    # Define the metadata for the output raster
    out_meta = src.meta.copy()

    # Update the metadata to match the data type of the reclassified raster
    out_meta.update(dtype=rasterio.uint8, count=1, nodata=0)

    # Write the reclassified raster to a new file
    with rasterio.open(output_raster, 'w', **out_meta) as dst:
        dst.write(reclassified_data, 1)

# Re-open the mask raster file for polygonization
raster_ds = gdal.Open(output_raster)
band = raster_ds.GetRasterBand(1)

# Ensure the 'out_layer' is passed correctly as an OGRLayer object
gdal.Polygonize(band, None, out_layer, 0, [], callback=None)

# Filter polygons where the raster value is not equal to 1
for feature in out_layer:
    if feature.GetField(Field_ID) != 1:
        out_layer.DeleteFeature(feature.GetFID())

# Clean up
out_layer = None
out_ds = None
band = None
raster_ds = None

print(f"Polygon shapefile created: {shp_path}")

#----------------------------------------------------------------------------------------------------------------
# %%
