

#%%

import geopandas as gpd
import rasterio
import numpy as np
import pandas as pd
from rasterstats import zonal_stats
import os

# Define input variables
shp_input_catchments = r"H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\shapes\shapefiles_2024\Sub_Sub_Catchments_2A.shp"
raster_DEM = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\04_GIS\raster\DEM_cat_2A.tif'
output_folder = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\05_Hydrology\DRAINS\Slope_calcs'
output_file_name = r'slopes_Cat_2A'

# Output CSV path
output_csv_path = os.path.join(output_folder, f"{output_file_name}.csv")

# Step 1: Load the catchment shapefile
catchments_gdf = gpd.read_file(shp_input_catchments)

# Step 2: Calculate slope from DEM in percentage
with rasterio.open(raster_DEM) as src:
    dem_data = src.read(1)
    dem_affine = src.transform
    
    # Calculate slope in % using numpy gradient and pixel size
    x, y = np.gradient(dem_data, src.res[0], src.res[1])
    slope = np.sqrt(x**2 + y**2) * 100  # Slope in percentage

    # Save slope to a new raster to use with zonal_stats
    slope_meta = src.meta.copy()
    slope_meta.update(dtype=rasterio.float32, compress='lzw')
    
    # Temporary slope raster path
    temp_slope_raster = os.path.join(output_folder, "temp_slope.tif")
    
    with rasterio.open(temp_slope_raster, 'w', **slope_meta) as slope_dst:
        slope_dst.write(slope.astype(rasterio.float32), 1)

# Step 3: Calculate average slope for each catchment using zonal statistics
zonal_statistics = zonal_stats(
    shp_input_catchments,
    temp_slope_raster,
    stats=['mean'],
    geojson_out=False,
    nodata=np.nan
)

# Step 4: Extract the results and save to CSV
slope_results = pd.DataFrame({
    'ID': catchments_gdf['ID'],
    'Average_Slope_%': [stat['mean'] for stat in zonal_statistics]
})

# Save the results as a CSV file
slope_results.to_csv(output_csv_path, index=False)
print(f"Average slope values saved to {output_csv_path}")

# Optional: Remove the temporary slope raster
os.remove(temp_slope_raster)

# %%
