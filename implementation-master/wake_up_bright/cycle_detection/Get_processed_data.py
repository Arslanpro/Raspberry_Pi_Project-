import sys
import matplotlib.pyplot as plt

sys.path.append('/home/pi/Project/implementation/wake_up_bright/cycle_detection')

from Combined_get_database import *

# This file is meant to be an example for extracting the processed data from the file Process_data.py. As input,
# the number of points to be plotted is required. The output is an x-vector and y-vector which can be plotted in the
# Web-UI. The x-vector is the relative time in (s) from when the person went to sleep. The y-vector represents the
# activity.

# Initialize n_points
n_points = 100

# Get data from function
combined_get_database(n_points)

print(x_vector)
print(y_vector)
# Example plot of data
plt.plot(x_vector, y_vector, label='1')
plt.show()
