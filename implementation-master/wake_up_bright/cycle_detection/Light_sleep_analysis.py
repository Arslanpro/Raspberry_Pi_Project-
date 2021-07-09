import mariadb
import sys, os, inspect
import pandas as pd
import datetime
import numpy as np

x_vector = []
y_vector = []
hours_diff = []
minutes_diff = []


def light_sleep_analysis(date):
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            password="123",
            host="127.0.0.1",
            port=3306,
            database="project"

        )
    except mariadb.Error as e:
        print(f"Error connecting to MariaDB Platform: {e}")
        sys.exit(1)

    # Get Cursor. This can retrieve the data from the database.
    cur = conn.cursor()
    # print('Done')
    # print(date)
    # Getting the dates right
    date1 = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    date2 = (date1 + datetime.timedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S")
    # print(date2)

    # Actually retrieving the data

    sql = "SELECT move_detection_sensor1, move_detection_sensor2, collected_time, cid FROM collection where DATE_FORMAT(collected_time,'%Y-%m-%d') between " + "'" + date + "'" + "and" + "'" + date2 + "'"
    cur.execute(sql)

    # Create variable records for further processing.
    records = cur.fetchall()
    rcount = int(cur.rowcount)
    n_points = rcount
    # print('nrows = ', rcount)

    # Assigning the correct data to the different vectors ########
    local_vector = []
    Sensor1 = []
    Sensor2 = []
    Time = []
    ID = []

    for u in range(0, rcount):
        local_vector = records[u]
        Sensor1.append(local_vector[0])
        Sensor2.append(local_vector[1])
        Time.append(local_vector[2])
        ID.append(local_vector[3])
        # local_vector = []
    # print("Sensor 1 = ", Sensor1)
    # print("Sensor 2 = ", Sensor2)
    # print("Time = ", Time)
    # print("ID = ", ID)

    global hours_diff
    global minutes_diff

    # Time_start = Time[0]
    # print(Time_start)
    # Time_end = Time[rcount-1]
    # print(Time_end)
    # format = "%Y-%m-%d %H:%M:%S"
    # diff = Time_end - Time_start
    # seconds = diff.seconds
    # hours_diff = seconds // 3600
    # minutes_diff = (seconds % 3600) // 60
    # Time_slept = hours_diff, minutes_diff
    # time = datetime.datetime.strptime('Time_end', format) - datetime.datetime.strptime('Time_start', format)

    # print(time)    # Time_slept = (Time_end-datetime.timedelta(hours=1)).strftime("%Y-%m-%d %H:%M:%S")
    ###############################################################

    # Show all data:
    # for (move_detection_sensor1, move_detection_sensor2, collected_time, cid) in cur:
    # print(f"Sensor1: {move_detection_sensor1}, Sensor2: {move_detection_sensor2}, Collected time: {collected_time}, Cid: {cid}")
    # Sensor1[k] = move_detection_sensor1
    # k = k+1

    # Initialization
    steps = 1

    global x_vector
    global y_vector

    def zero_runs(a):
        # Create an array that is 1 where a is 0, and pad each end with an extra 0.
        iszero = np.concatenate(([0], np.equal(a, 0).view(np.int8), [0]))
        absdiff = np.abs(np.diff(iszero))
        # Runs start and end where absdiff is 1.
        ranges = np.where(absdiff == 1)[0].reshape(-1, 2)
        return ranges

    # empty both vectors if filled
    if len(x_vector) > 1:
        for v in range(0, len(x_vector)):
            del x_vector[0]
            del y_vector[0]

    # Find optimal distribution of moving average
    window_1 = round(rcount / 20) + 1
    window_2 = round(rcount / 20) + 1

    # Extra code because in the night of 27-28th of october, nothing was written to the database when no movement was detected -> beun solution
    if date == "2020-10-27 12:00:00":
        Sensor_used = Sensor2
    else:
        Sensor_used = Sensor1

    # Get the moving average of the sensor data, and relative time
    Sensor_used_series = pd.Series(Sensor_used)
    first_moving_average = Sensor_used_series.rolling(window=window_1).mean()
    second_moving_average = first_moving_average.rolling(window=window_2).mean()

    # Trying to initialize both vectors
    # k = 0
    # x_vector = [1] * n_points
    # y_vector = [1] * n_points
    u = 0
    v = 0
    end_ID_deep_sleep = []
    ones_allowed = 20

    for i in range(3, n_points - 1):
        # print(ID)
        # print(i)
        # print(steps)
        # print(ID[i * steps])
        if u < ones_allowed:
            if Sensor1[i * steps] == 0:
                v = v + 1
            else:
                u = u + 1
            if u == ones_allowed - 1 and v > 1800:
                print(v)
                end_ID_deep_sleep.append(ID[i * steps])
                v = 0
                u = u + 1
        else:
            u = 0
            v = 0

        x_vector.append(ID[i * steps])
        y_vector.append(Sensor1[i * steps])

    # First analysing the data
    zero_vector = zero_runs(Sensor_used)
    # print(zero_vector)
    amount_zeros = zero_vector[:, 1] - zero_vector[:, 0]
    # print(amount_zeros)
    start_zeros = zero_vector[:, 1]
    # print(start_zeros)
    corresponding_times = []

    for k in range(0, len(start_zeros) - 1):
        start_zeros_scalar = start_zeros[k]
        corresponding_times.append(Time[start_zeros_scalar])
    # corresponding_times = Time[start_zeros]
    # print(corresponding_times)
    # print('after')
    # print(end_ID_deep_sleep)
    # print(len(end_ID_deep_sleep))




