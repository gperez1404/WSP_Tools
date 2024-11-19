# Calculate avertgae slope embankment

#%%

coordinates=[(0, 6.259), (0.529, 6.38), (1.058, 6.502), (1.588, 6.623), (2.117, 6.774),
    (2.646, 6.896), (3.175, 7.017), (3.704, 7.138), (4.234, 7.29), (4.763, 7.532),
    (5.292, 7.654), (5.821, 7.775), (6.35, 7.896), (6.88, 8.048), (7.409, 8.169),
    (7.938, 8.29), (8.467, 8.412), (8.996, 8.563), (9.526, 8.684), (10.055, 8.806),
    (10.584, 8.927), (11.113, 9.048), (11.642, 9.2), (12.172, 9.321), (12.172, 9.321)]


# Revised function to calculate the average slope for the entire embankment
def calculate_average_slope(coords):
    # Using the first and last points only to calculate overall slope
    x1, y1 = coords[0]
    x2, y2 = coords[-1]
    delta_x = x2 - x1
    delta_y = y2 - y1
    
    # Calculate the average slope in 1V:zH format
    if delta_y != 0:
        z = delta_x / delta_y
        average_slope = f"1V:{z:.2f}H"
    else:
        average_slope = "Undefined (vertical segment)"
    
    return average_slope

# Calculate average slope for the given coordinates
average_slope_result = calculate_average_slope(coordinates)
print(average_slope_result)
#%%