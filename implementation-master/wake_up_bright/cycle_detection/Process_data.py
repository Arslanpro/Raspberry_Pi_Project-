import pandas as pd
import matplotlib.pyplot as plt

x_vector = []
y_vector = []


def process_data(n_points):
    # Read excel sheets, and give names to columns
    df = pd.read_excel("First_night_Lars_data_processed.xlsx")
    df.columns = ['Time_absolute', 'Sensor1', 'Sensor2', 'Time_real', 'Not used', 'Not used', 'Not used', 'Not used',
                  'Not used',
                  'Not used']

    # Initialization
    n_rows = df.shape[0]
    steps = round(n_rows / n_points)
    global x_vector
    global y_vector

    # Get the moving average of the sensor data, and relative time
    first_moving_average = df.Sensor1.rolling(window=60).mean()
    second_moving_average = first_moving_average.rolling(window=1200).mean()

    for i in range(1, n_points):
        x_vector.append(df.Time_absolute[i * steps])
        y_vector.append(second_moving_average[i * steps])
