#%%
import os
from osgeo import gdal, ogr, osr
# Inputs
ecw_file_location = r"C:\Users\AUGM509787\OneDrive - WSP O365\GPM\02_Projects\Arraw_Dam_FIA_CCA\05_GIS\01_areal_imagery_local\20220731_Weipa_MGA94z54.ecw"
output_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\01_Aerial_imagery\Derived_shps'
# Determine the file extension
extension_input_file = str(os.path.splitext(ecw_file_location)[1])

# Define output shapefile name
output_shapefile = os.path.join(output_location, "Extent_" + os.path.basename(ecw_file_location).replace(extension_input_file, '.shp'))

# Open the ECW file with GDAL
dataset = gdal.Open(ecw_file_location)

if not dataset:
    raise Exception(f"Failed to open ECW file: {ecw_file_location}")

# Get geotransform and projection
geotransform = dataset.GetGeoTransform()
projection = dataset.GetProjection()

# Get the size of the image
x_size = dataset.RasterXSize
y_size = dataset.RasterYSize

# Calculate the coordinates of the four corners
x_min = geotransform[0]
y_max = geotransform[3]
x_max = x_min + geotransform[1] * x_size
y_min = y_max + geotransform[5] * y_size

# Create a polygon from the extent
ring = ogr.Geometry(ogr.wkbLinearRing)
ring.AddPoint(x_min, y_min)
ring.AddPoint(x_min, y_max)
ring.AddPoint(x_max, y_max)
ring.AddPoint(x_max, y_min)
ring.AddPoint(x_min, y_min)

polygon = ogr.Geometry(ogr.wkbPolygon)
polygon.AddGeometry(ring)

# Create the shapefile
driver = ogr.GetDriverByName("ESRI Shapefile")
if os.path.exists(output_shapefile):
    driver.DeleteDataSource(output_shapefile)
out_ds = driver.CreateDataSource(output_shapefile)

srs = osr.SpatialReference()
srs.ImportFromWkt(projection)

layer = out_ds.CreateLayer("extent", srs, ogr.wkbPolygon)
layer_defn = layer.GetLayerDefn()

feature = ogr.Feature(layer_defn)
feature.SetGeometry(polygon)
layer.CreateFeature(feature)

# Clean up
feature = None
out_ds = None

print(f"Shapefile saved at: {output_shapefile}")
#%%