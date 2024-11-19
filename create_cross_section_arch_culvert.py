#%%
import numpy as np
import pandas as pd
import os

# Given dimensions
height_max = 3.28
width_max = 8.5

file_location = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\11_Hydraulic_model\TUFLOW_SA_HR_2024\model\xs'
file_name = "arch_culvert_3.28m_high_x_8.5m_Wide.csv"

# Generate height values from 0 to height_max
heights = np.linspace(0, height_max, 20)  # 20 points for smooth curvature

# Function to calculate width for each height in a typical arch shape
def calculate_width(h, h_max, w_max):
    # Arch approximation formula
    return w_max * np.sqrt(1 - (h / h_max)**2)

# Calculate width values
widths = [calculate_width(h, height_max, width_max) if h < height_max else 0.001 for h in heights]

# Create DataFrame
df = pd.DataFrame({
    'Height': heights,
    'Width': widths
})


# Save to CSV:
file_path =os.path.join(file_location,file_name)

df.to_csv(file_path, index=False)

print(f'file creaated at: {file_path}')
#%%