
# This script generates a map with areas below an elevation treshold
# This is useful to quickly assess potentially flood-prone areas based 
# on high resolution Terrain

#%%

import os
import numpy as np
import rasterio
import matplotlib.pyplot as plt
from rasterio.plot import show
from rasterio.mask import mask

# Define file paths

file_name = r'Mosaic_DEM_AHD_1m_v4_trimmed_to_tidal_zone.tif'

raster_location = r'U:\Transition\Golder\Brisbane\CAD\ss\Arraw_dam\00_Mosaic_DEM'
raster_file = os.path.join(raster_location, file_name)
# Define threshold elevation
treshold_elevation = 2.2  # Elevation in m AHD

output_location = r'U:\Transition\Golder\Brisbane\CAD\ss\Arraw_dam\00_Mosaic_DEM'
output_file = os.path.join(output_location, f'elevation_below_level_{treshold_elevation}m_.tif')

# Open the input raster file
with rasterio.open(raster_file) as src:
    # Read the elevation data
    elevation_data = src.read(1)  # Assume the elevation data is in the first band
    profile = src.profile  # Get the profile of the source raster

    # Get the original nodata value
    nodata_value = src.nodata

    # Create a mask where the elevation is below the threshold
    below_threshold = elevation_data < treshold_elevation

    # Create a new array where the original elevation is kept if below the threshold,
    # otherwise set it to the nodata value
    output_data = np.where(below_threshold, elevation_data, nodata_value)

    # Update the profile for the output raster
    profile.update(dtype=rasterio.float32, count=1, nodata=nodata_value)

    # Save the output raster with the updated values
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(output_data.astype(rasterio.float32), 1)

print(f"New raster with areas below treshold saved at: {output_file}")

# Plotting the areas below the threshold
fig, ax = plt.subplots(figsize=(10, 10))

# Masking the data for visualization
below_mask = np.ma.masked_where(output_data == nodata_value, output_data)

# Plot areas below threshold in red
ax.imshow(below_mask, cmap='Reds', alpha=0.5, label="Below Threshold")

# Adding title and labels
ax.set_title(f"Areas below {treshold_elevation}m Elevation")
ax.set_xlabel('X Coordinate')
ax.set_ylabel('Y Coordinate')

# Show the plot
plt.show()

# %%
