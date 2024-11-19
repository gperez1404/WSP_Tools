# This create a the  folder estructure into your 
#%%
import os

# Define the output location
output_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\02_DEMs_LiDAR\2024_Survey'  # Replace with your actual output location

# List of folder names to create
folders = [
    "Derived_CAD_files",
    "Derived_DEMs",
    "Derived_shapefiles",
    "Raw_cloud_point_data"
]

# Create each folder in the specified output location
for folder in folders:
    folder_path = os.path.join(output_location, folder)
    os.makedirs(folder_path, exist_ok=True)
    print(f"Created folder: {folder_path}")
#%%