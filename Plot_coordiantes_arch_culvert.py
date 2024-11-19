# generate coordiantes of Arch cuvlert cross section
#%%
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import simps

# Given parameters
span = 13.028  # span in meters
rise = 2.83    # rise in meters
area_target = 30.72   # total area of the culvert's cross section in square meters
number_of_coords = 20  # default number of coordinates

# Semi-ellipse parameters (semi-major axis = a, semi-minor axis = b)
a = span / 2   # half the span (semi-major axis)
b = rise       # the rise is the semi-minor axis

# Parametric equation for the ellipse (adjustable based on the desired area)
def ellipse_y(x, a, b):
    # Ensure the value inside the square root is non-negative
    return b * np.sqrt(1 - (x / a) ** 2) if abs(x) <= a else 0

# Function to calculate the X and Y coordinates
def generate_coordinates(a, b, number_of_coords):
    # Generate 'number_of_coords' evenly spaced X values between -a and a
    x_coords = np.linspace(-a, a, number_of_coords)
    # Calculate corresponding Y values using the parametric equation for the ellipse
    y_coords = np.array([ellipse_y(x, a, b) for x in x_coords])
    return x_coords, y_coords

# Generate the X and Y coordinates based on the number of coordinates
x_coords, y_coords = generate_coordinates(a, b, number_of_coords)

# Ensure the endpoints where Y = 0 are included (at the rightmost part of the culvert)
x_coords = np.append(x_coords, [a])  # Add the rightmost point where Y = 0
y_coords = np.append(y_coords, [0])  # Y = 0 at the rightmost point

# Display the coordinates
coordinates = np.column_stack((x_coords, y_coords))
print("X, Y Coordinates (top half of the arch):")
print(coordinates)

# Calculate the area under the curve using Simpson's rule
calculated_area = simps(y_coords, x_coords)
print(f"\nCalculated Cross-Sectional Area: {calculated_area:.2f} m²")
print(f"Target Area: {area_target} m²")

# Plot to visualize the culvert shape (top half only)
plt.figure(figsize=(10, 5))
plt.plot(x_coords, y_coords, label="Arch Culvert Shape", color="blue")
plt.fill_between(x_coords, y_coords, color='lightblue', alpha=0.6)
plt.title("Arch Culvert Cross-Section (Top Half)")
plt.xlabel("X Coordinate (m)")
plt.ylabel("Y Coordinate (m)")
plt.axhline(0, color='black', linewidth=0.5)
plt.axvline(0, color='black', linewidth=0.5)
plt.grid(True)
plt.legend()
plt.gca().set_aspect('equal', adjustable='box')
plt.show()


#%%