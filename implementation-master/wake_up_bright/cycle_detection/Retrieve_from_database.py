# Module Imports
import mariadb
import sys

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

# Get Cursor
cur = conn.cursor()
print('Done')

cur.execute(
    "SELECT move_detection_sensor1, move_detection_sensor2, collected_time, cid FROM collection")

# Print Result-set
for (move_detection_sensor1, move_detection_sensor2, collected_time, cid) in cur:
    print(f"Sensor1: {move_detection_sensor1}, Sensor2: {move_detection_sensor2}, Collected time: {collected_time}, Cid: {cid}")