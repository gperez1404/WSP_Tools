# This script reads a csv file created by TUFLOW ARR plugin with rainfall TPs 
# and finds the median temporal pattern based on the median cumulative 
# rainfall across the entire event

# This pattern can be considered the "median" rainfall pattern.

# To select the most representative "median" temporal pattern, a reasonable 
# approach is to look at the central tendency of the patterns over time. 
# Since all patterns have the same total cumulative rainfall, a method to 
# determine the median pattern could be as follows:

# Calculate the cumulative sum for each time step in each pattern.
# At each time step, calculate the median cumulative rainfall across all patterns.
# Find the pattern whose cumulative rainfall trajectory is closest to the median 
# at each time step.

# This method would identify the temporal pattern that most closely follows the 
# median behavior of rainfall accumulation across the entire duration of the event.

#%%

import pandas as pd
import matplotlib.pyplot as plt

# Example usage: Call the function with the file path
file_path = r"U:\Transition\Golder\Brisbane\CAD\ss\GIS_SoEE\bc_dbase\1_in_10_AEP\rf_inflow\1_RF_1_in_10_AEP_180m.CSV"
Duration = '3 hours'
AEP = '1 in 10 AEP'

def find_median_temporal_pattern(file_path):
    # Step 2: Load the CSV file, ignoring first two rows, labels in row 3, data starting row 4
    data = pd.read_csv(file_path, skiprows=2)
    
    # Step 3: Extract time column and rainfall pattern columns
    time = data.iloc[:, 0]
    rainfall_patterns = data.drop(columns=[data.columns[0]])

    # Step 4: Calculate cumulative rainfall over time for each pattern
    cumulative_rainfall = rainfall_patterns.cumsum()

    # Step 5: Calculate the median cumulative rainfall at each time step
    median_cumulative_rainfall = cumulative_rainfall.median(axis=1)

    # Step 6: Calculate the absolute differences from the median for each pattern
    differences_from_median = (cumulative_rainfall.T - median_cumulative_rainfall).abs().sum(axis=1)

    # Step 7: Identify the most representative pattern (smallest difference from the median)
    most_representative_pattern = differences_from_median.idxmin()

    # Step 8: Plot all patterns, highlight the median pattern
    plt.figure(figsize=(10, 6))
    
    # Plot all the temporal patterns in light colors
    for column in rainfall_patterns.columns:
        if column == most_representative_pattern:
            plt.plot(time, rainfall_patterns[column], label=column, linewidth=3, color='red')
        else:
            plt.plot(time, rainfall_patterns[column], label=column, color='lightgray', linewidth=1)

    # Highlight the most representative pattern
    plt.title(f'TPs {AEP} | {Duration} (Median Highlighted)')
    plt.xlabel('Time (hours)')
    plt.ylabel('Rainfall Increment (mm)')
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1))
    plt.grid(True)
    plt.show()

    # Return the name of the most representative pattern
    return most_representative_pattern

# the main execution
median_pattern = find_median_temporal_pattern(file_path)

# Display the selected median pattern
print(f'The most representative median pattern is: {median_pattern}')

#%%