import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

cwd = os.getcwd()
print(cwd)

# Read excel sheets, and give names to columns
df = pd.read_csv("Excel_files/Second_night_Lars_processed.csv", delimiter=';')
df.columns = ['Address', 'Sensor1', 'Sensor2', 'Time']

# Set graph
fig, (ax1, ax2) = plt.subplots(2, num=1, clear=True)
ax1.set_title('Sensor 1')
ax1.set_ylabel('Activity (Yes/No)')

ax2.set_title('Sensor 2')
ax2.set_ylabel('Activity (Yes/No)')
ax2.set_xlabel('Time (HH-MM-SS)')

# Get the number of rows so that the relevant data can be retrieved from the dataframe
n_rows = df.shape[0]
x_plot = df.Time[2:n_rows]
y1_plot = df.Sensor1[2:n_rows]
y2_plot = df.Sensor2[2:n_rows]
ax1.plot(x_plot, y1_plot)
ax2.plot(x_plot, y2_plot)

# Format the x-axis
locator = mdates.AutoDateLocator(minticks=6, maxticks=14)
ax1.xaxis.set_major_locator(locator)
ax2.xaxis.set_major_locator(locator)
fig.autofmt_xdate()

plt.draw() # draw the plot
plt.pause(5) # show it for 5 seconds
print("Done")

"""
plt.figure(2)
plt.plot(x_plot, y1_plot)
plt.show()
# Plot combined activity
#
"""