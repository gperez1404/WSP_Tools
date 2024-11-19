# This script loads the RAW file with Rainfall IFD data downloaded
# from ARR data hub / BoM website for a parricular location and calculates the 
# corresponding ARF factors and apply them accordingly to teh rainfall depths

# the output of this script is a new CSV file that replicates the format of the original RAW
# file but has the rainfall depths values with the corresponding ARF applied to them

#%%

import pandas as pd
import numpy as np
import os

# Inputs:
#-------------------------------------------------------------------------------------------------

# Input file with rainfall depths as downloaded from BoM / ARR Data hub
input_file = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\05_Hydrology\DRAINS\rainfall\ARR2024\depths_-12.986_141.724_all_design.csv'
output_folder_path = r'H:\ProjectsAU\PS211032 - Arraw Dam FIA CCA update\05_Hydrology\DRAINS\rainfall\ARR2024\Files_with ARF'
location_point = r'-12.986_141.724' # copy from the name of the input file this is only to name output
catchment_area = 7.82  # area in square kilometers

#  ARF region input (see Figure 2.4.2 of ARR Book 2, Chapter 4, Section 3 page 79 of pdf file)
ARF_region = "Northern Coastal" # "South-East Coast" | "Semi-arid Inland Queensland" | "Northern Coastal"
                                # "Tasmania" | "South-West Western Australia" | "Central New South Wales"
                                # "Southern Semi-arid" | "Southern Temperate" | "Inland Arid"
#-------------------------------------------------------------------------------------------------

# Dictionaries for conversions of input file headers
#-------------------------------------------------------------------------------------------------
# AEP dictionary (Annual Exceedance Probability) expressed as percentage

aep_fraction_dict = {
    '12EY': (99.9994/100),
    '6EY': (99.75/100),
    '4EY': (98.17/100),
    '3EY': (95.02/100),
    '2EY': (86.47/100),
    '63.2%': (63.20/100),
    '50%': (50.00/100),
    '0.5EY': (39.35/100),
    '20%': (20.00/100),
    '0.2EY': (18.13/100),
    '10%': (10.00/100),
    '5%': (5.00/100),
    '2%': (2.00/100),
    '1%': (1.00/100),
    '1 in 200': (0.5/100),
    '1 in 500': (0.2/100),
    '1 in 1000': (0.1/100),
    '1 in 2000': (0.05/100),
    '1 in 5000': (0.02/100)
}

aep_percentage_dict = {
    '12EY': 99.9994,
    '6EY': 99.75,
    '4EY': 98.17,
    '3EY': 95.02,
    '2EY': 86.47,
    '63.2%': 63.20,
    '50%': 50.00,
    '0.5EY': 39.35,
    '20%': 20.00,
    '0.2EY': 18.13,
    '10%': 10.00,
    '5%': 5.00,
    '2%': 2.00,
    '1%': 1.00,
    '1 in 200': 0.5,
    '1 in 500': 0.2,
    '1 in 1000': 0.1,
    '1 in 2000': 0.05,
    '1 in 5000': 0.02
}

aep_EY_dict = {
    '12EY': '12EY',
    '6EY': '6EY',
    '4EY': '4EY',
    '3EY': '3EY',
    '2EY': '2EY',
    '63.2%': '1EY',
    '50%': '0.69EY',
    '0.5EY': '0.5EY',
    '20%': '0.22EY',
    '0.2EY': '0.2EY',
    '10%': '0.11EY',
    '5%': '0.05EY',
    '2%': '0.02EY',
    '1%': '0.01EY',
    '1 in 200': '0.005EY',
    '1 in 500': '0.002EY',
    '1 in 1000': '0.001EY',
    '1 in 2000': '0.0002EY',
}

# Duration dictionary, converting text to values in minutes
duration_dict = {
    '1 min': 1,
    '2 min': 2,
    '3 min': 3,
    '4 min': 4,
    '5 min': 5,
    '10 min': 10,
    '15 min': 15,
    '20 min': 20,
    '25 min': 25,
    '30 min': 30,
    '45 min': 45,
    '1 hour': 60,
    '1.5 hour': 90,
    '2 hour': 120,
    '3 hour': 180,
    '4.5 hour': 270,
    '6 hour': 360,
    '9 hour': 540,
    '12 hour': 720,
    '18 hour': 1080,
    '24 hour': 1440,
    '30 hour': 1800,
    '36 hour': 2160,
    '48 hour': 2880,
    '72 hour': 4320,
    '96 hour': 5760,
    '120 hour': 7200,
    '144 hour': 8640,
    '168 hour': 10080
}

# Define the ARF parameters for each region as a dictionary
coefficients_dict = {
    "Semi-arid Inland Queensland": {"a": 0.1590, "b": 0.283, "c": 0.250, "d": 0.308, "e": 7.3e-07, "f": 1.000, "g": 0.0390, "h": 0.00000, "i": 0.00000},
    "Tasmania": {"a": 0.0605, "b": 0.347, "c": 0.200, "d": 0.283, "e": 7.6e-04, "f": 0.347, "g": 0.0877, "h": 0.01200, "i": -0.00033},
    "South-West Western Australia": {"a": 0.1830, "b": 0.259, "c": 0.271, "d": 0.330, "e": 3.85e-06, "f": 0.410, "g": 0.5500, "h": 0.00817, "i": -0.00045},
    "Central New South Wales": {"a": 0.2650, "b": 0.241, "c": 0.505, "d": 0.321, "e": 5.6e-04, "f": 0.414, "g": -0.0210, "h": 0.01500, "i": -0.00033},
    "South-East Coast": {"a": 0.3270, "b": 0.241, "c": 0.448, "d": 0.360, "e": 9.6e-04, "f": 0.480, "g": -0.2100, "h": 0.01200, "i": -0.00130},
    "Southern Semi-arid": {"a": 0.2710, "b": 0.270, "c": 0.480, "d": 0.270, "e": 1.2e-04, "f": 0.507, "g": 0.1600, "h": 0.00560, "i": -0.00021},
    "Southern Temperate": {"a": 0.2960, "b": 0.256, "c": 0.467, "d": 0.285, "e": 1.0e-03, "f": 0.419, "g": -0.0500, "h": 0.00913, "i": -0.00045},
    "Northern Coastal": {"a": 0.3260, "b": 0.223, "c": 0.442, "d": 0.323, "e": 1.3e-03, "f": 0.580, "g": -0.3740, "h": 0.01300, "i": -0.00150},
    "Inland Arid": {"a": 0.2130, "b": 0.282, "c": 0.325, "d": 0.370, "e": 3.7e-06, "f": 0.491, "g": 0.2520, "h": 0.00189, "i": -0.00020}
}


#-------------------------------------------------------------------------------------------------

# Functions:
#-------------------------------------------------------------------------------------------------

# this assumes that the duration is already in minutes
def calculate_arf_short_durations(area_sq_km, duration_minutes, AEP_in_fraction_units):
    
    AEP_log = np.log10(AEP_in_fraction_units)
    ARF = min(1,
              1 - 0.287 * (area_sq_km ** 0.265 - 0.439 * np.log10(duration_minutes)) * (duration_minutes ** -0.36) +
              (2.26*(10**-3)) * (area_sq_km ** 0.326) * (duration_minutes ** 0.125) * (0.3 + AEP_log) +
              0.0141 * (area_sq_km ** 0.213) * 10 ** ((-0.0221 * (((duration_minutes - 180) ** 2)) / 1440)) * (0.3 + AEP_log)
              )
    return ARF

def calculate_arf_long_durations(area_sq_km, duration_minutes, a, b, c, d, e, f, g, h, i, AEP_in_fraction_units):
    
    AEP_log = np.log10(AEP_in_fraction_units)
    ARF = min(1,
              1 - a * (area_sq_km ** b - c * np.log10(duration_minutes)) * (duration_minutes ** -d) +
              e * (area_sq_km ** f) * (duration_minutes ** g) * (0.3 + AEP_log) +
              h * (10 ** ((area_sq_km * duration_minutes) / 1440)) * (0.3 + AEP_log)
              )
    return ARF

def interpolate_arf(area_sq_km, duration_minutes, AEP_in_fraction_units, a, b, c, d, e, f, g, h, i):
    
    if 720 <= duration_minutes <= 1440:  # Duration in minutes between 12 and 24 hours
        arf_12hour = calculate_arf_long_durations(area_sq_km, duration_dict.get('12 hour'), a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
        arf_24hour = calculate_arf_long_durations(area_sq_km, duration_dict.get('24 hour'), a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
        ARF = arf_12hour + (arf_24hour - arf_12hour) * (duration_minutes - 720) / 720
        return ARF
    else:
        if duration_minutes < 720:
            return calculate_arf_short_durations(area_sq_km, duration_minutes, AEP_in_fraction_units)
        else:
            return calculate_arf_long_durations(area_sq_km, duration_minutes, a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)

def calculate_arf_small_area(area_sq_km, arf_10km2):
    if 1 <= area_sq_km <= 10:
        ARF = 1 - 0.6614 * (1 - arf_10km2) * (area_sq_km ** 0.4 - 1)
    else:
        raise ValueError("This equation is only valid for areas between 1 and 10 square kilometers.")
    return ARF

# this is the main function with all the info described in ARR Book 2, Chapter 4, Section 3.
def calculate_arf(area_sq_km, duration_minutes, AEP_in_fraction_units, a, b, c, d, e, f, g, h, i):
    if area_sq_km > 30000:
        raise ValueError("ERROR 101: Catchment area larger than 30,000 km2. Generalised equations not applicable. ARR 2019 guidelines recommend that the practitioner should perform a frequency analysis of catchment rainfall data for the catchment of interest.")

    if 1 <= area_sq_km <= 10:
        if duration_minutes <= 720:  # Case 1
            arf_10km2 = calculate_arf_short_durations(10, duration_minutes, AEP_in_fraction_units)
            ARF = calculate_arf_small_area(area_sq_km, arf_10km2)
        elif 720 < duration_minutes <= 1440:  # Case 2
            arf_24hr_10km2 = calculate_arf_long_durations(10, duration_dict.get('24 hour'), a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
            arf_12hr_10km2 = calculate_arf_short_durations(10, duration_dict.get('12 hour'), AEP_in_fraction_units)
            arf_10km2 = arf_12hr_10km2 + (arf_24hr_10km2 - arf_12hr_10km2) * (duration_minutes - 720) / 720
            ARF = calculate_arf_small_area(area_sq_km, arf_10km2)
        elif 1440 < duration_minutes <= 10080:  # Case 3
            arf_10km2 = calculate_arf_long_durations(10, duration_minutes, a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
            ARF = calculate_arf_small_area(area_sq_km, arf_10km2)
        else:
            raise ValueError("Duration is out of the valid range for the selected area.")

    elif 10 < area_sq_km <= 1000:
        if duration_minutes <= 720:  # Case 4
            ARF = calculate_arf_short_durations(area_sq_km, duration_minutes, AEP_in_fraction_units)
        elif 720 < duration_minutes <= 1440:  # Case 5
            arf_24hr = calculate_arf_long_durations(area_sq_km, duration_dict.get('24 hour'), a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
            arf_12hr = calculate_arf_short_durations(area_sq_km, duration_dict.get('12 hour'), AEP_in_fraction_units)
            ARF = arf_12hr + (arf_24hr - arf_12hr) * (duration_minutes - 720) / 720
        elif 1440 < duration_minutes <= 10080:  # Case 6
            ARF = calculate_arf_long_durations(area_sq_km, duration_minutes, a, b, c, d, e, f, g, h, i, AEP_in_fraction_units)
        else:
            raise ValueError("Duration is out of the valid range for the selected area.")
    else:
        raise ValueError("Area is out of the valid range.")

    return ARF
        
#-------------------------------------------------------------------------------------------------

# get the paramters:

# Retrieve the parameters for the selected ARF_region
params = coefficients_dict[ARF_region]

# Extract individual parameters
a = params['a']
b = params['b']
c = params['c']
d = params['d']
e = params['e']
f = params['f']
g = params['g']
h = params['h']
i = params['i']

# Load the input CSV file, skipping the initial metadata rows
df = pd.read_csv(input_file, header=None, skiprows=9)

# Extract and convert AEP and Duration labels

aep_labels = df.iloc[0, 2:].values
duration_labels = df.iloc[1:, 0].values

# Convert AEP labels to faraction values using the dictionary
AEP_values_as_fraction = np.array([aep_fraction_dict[label] for label in aep_labels])

# Convert Duration labels to numeric values using the dictionary
durations_as_minutes = np.array([duration_dict[label] for label in duration_labels])

# Extract the rainfall depths data
rainfall_depths = df.iloc[1:, 2:].values.astype(float) # You are not skipping rows

# Initialize ARF_values as a list of lists (2D array) with the same shape as rainfall_depths
ARF_values = np.zeros((len(durations_as_minutes), len(AEP_values_as_fraction)))

# Calculate ARF for each combination of AEP and Duration, and update rainfall increments
for i in range(len(durations_as_minutes)):
    for j in range(len(AEP_values_as_fraction)):
        
        # Catchments smaller than 1 squared kilometer do not need ARF
        if(catchment_area<1):
            ARF= 1
        else:
            ARF = calculate_arf(catchment_area, durations_as_minutes[i], AEP_values_as_fraction[j], a, b, c, d, e, f, g, h, i)
        
        # Fix numerical innacuracies
        if (ARF< 0):
            ARF= 1
        else:
            ARF =round(ARF,2)
        ARF_values[i, j] = ARF
        rainfall_depths[i, j] = round(rainfall_depths[i, j] * ARF, 2)
       
# Read the entire file into a list of lines
with open(input_file, 'r') as file:
    lines = file.readlines()
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
# save resutls in CSV files
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

output_file_name_ARF = f'ARF_for_{location_point}.csv'
output_file_name_New_Depths = f'Depths_after_applying_ARF_for_{location_point}.csv'

# Extract metadata (first 9 lines)
metadata = lines[:9]

# Convert the remaining lines (data) into a DataFrame
data_lines = lines[9:]

# save the file with the ARFs  
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
data = pd.DataFrame([x.strip().split(',') for x in data_lines])

# Replace the corresponding data in the original DataFrame
data.iloc[1:, 2:] = ARF_values

# Combine metadata and updated data
updated_lines = metadata + data.astype(str).apply(lambda x: ','.join(x), axis=1).tolist()

# Save the updated dataframe to a new CSV file
output_file = os.path.join(output_folder_path, output_file_name_ARF)

# Save the updated lines to a new CSV file
output_file = os.path.join(output_folder_path, output_file_name_ARF)
with open(output_file, 'w') as file:
    file.write('\n'.join(updated_lines))

print(f"Areal Reduction Factors saved to {output_file}")
# save the file with the new Depths  
#:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
data = pd.DataFrame([x.strip().split(',') for x in data_lines])

# Replace the corresponding data in the original DataFrame
data.iloc[1:, 2:] = rainfall_depths

# Combine metadata and updated data
updated_lines = metadata + data.astype(str).apply(lambda x: ','.join(x), axis=1).tolist()

# Save the updated dataframe to a new CSV file
output_file = os.path.join(output_folder_path, output_file_name_New_Depths)

# Save the updated lines to a new CSV file
output_file = os.path.join(output_folder_path, output_file_name_New_Depths)
with open(output_file, 'w') as file:
    file.write('\n'.join(updated_lines))


print(f"Updated rainfall increments saved to {output_file}")
#--------------------------------------------------------------------------------------> End
#%%