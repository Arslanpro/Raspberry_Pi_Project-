import mariadb
import sys

x_vector = []
y_vector = []
n_points = 90


def combined_get_database():
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
    print('Done')

    # Actually retrieving the data
    cur.execute(
        "SELECT move_detection_sensor1, move_detection_sensor2, collected_time, cid FROM collection")

    # Create variable records for further processing.
    records = cur.fetchall()
    rcount = int(cur.rowcount)
    print('nrows = ', rcount)

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
    print("Sensor 1 = ", Sensor1)
    print("Sensor 2 = ", Sensor2)
    # print("Time = ", Time)
    print("ID = ", ID)
    ###############################################################

    # Show all data:
    # for (move_detection_sensor1, move_detection_sensor2, collected_time, cid) in cur:
    # print(f"Sensor1: {move_detection_sensor1}, Sensor2: {move_detection_sensor2}, Collected time: {collected_time}, Cid: {cid}")
    # Sensor1[k] = move_detection_sensor1
    # k = k+1

    # Initialization
    # n_rows = len(move_detection_sensor1)
    # steps = round(rcount / n_points)
    steps = 1

    global x_vector
    global y_vector

    # Get the moving average of the sensor data, and relative time
    # first_moving_average = Sensor1.rolling(window=10).mean()
    # second_moving_average = first_moving_average.rolling(window=100).mean()

    for i in range(1, n_points - 1):
        # print(ID)
        # print(i)
        # print(steps)
        # print(ID[i * steps])
        x_vector.append(ID[i * steps])
        y_vector.append(Sensor2[i * steps])
    print("x_vector in file ", x_vector)
