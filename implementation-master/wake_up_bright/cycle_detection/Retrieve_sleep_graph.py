import mariadb
import sys, os, inspect
import pandas as pd
import datetime

x_vector = []
y_vector = []

n_points = 50


def retrieve_sleep_graph(date):
    # Connect to MariaDB Platform
    try:
        conn = mariadb.connect(
            user="root",
            # password="123",
            password="1234567890",
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
    ###############################################################

    # Show all data:
    # for (move_detection_sensor1, move_detection_sensor2, collected_time, cid) in cur:
    # print(f"Sensor1: {move_detection_sensor1}, Sensor2: {move_detection_sensor2}, Collected time: {collected_time}, Cid: {cid}")
    # Sensor1[k] = move_detection_sensor1
    # k = k+1

    # Initialization
    # n_rows = len(move_detection_sensor1)
    steps = round(rcount / n_points) - 1
    # print(steps)

    global x_vector
    global y_vector

    # empty both vectors if filled
    if len(x_vector) > 1:
        for v in range(0, len(x_vector)):
            del x_vector[0]
            del y_vector[0]

    # Find optimal distribution of moving average
    window_1 = round(rcount / 2000) + 1
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
    for i in range(3, n_points - 1):
        # print(ID)
        # print(i)
        # print(steps)
        # print(ID[i * steps])

        x_vector.append(ID[i * steps])
        y_vector.append(second_moving_average[i * steps])
    # print("x_vector in file ", x_vector)
    # print("y_vector in file ", y_vector)
    # print(x_vector)
    # print(y_vector)
