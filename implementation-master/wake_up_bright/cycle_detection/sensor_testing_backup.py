# import inspect
# import os
# import sys
# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# parentparentdir = os.path.dirname(parentdir)
# sys.path.insert(0, parentparentdir)

import os
import logging
import mpu6050
# from mpu6050 import mpu6050
import time
import RPi.GPIO as gp
from datetime import datetime
from threading import Thread

# try to connect to sensors
from wake_up_bright.alarm_clock.app.crud.controllers import CollectionDao
# from wake_up_bright.alarm_clock.app.crud.models import db
# from wake_up_bright.alarm_clock.app import create_app


from wake_up_bright.log import get_logger
from wake_up_bright.alarm_clock.display import Color

logger = get_logger()


class SensorsThread(Thread):

    # def __init__(self, sensor1_pin: int, sensor2_pin: int, alarm_thread: ActiveAlarmThread = None,
    #              thread_name: str = "SensorThread"):
    def __init__(self, sensor1_pin: int, sensor2_pin: int, alarm_thread=None,
                 thread_name: str = "SensorThread", display_controller=None):
        super().__init__(name=thread_name)
        self.alarm_thread = alarm_thread
        self.pin1 = sensor1_pin
        self.pin2 = sensor2_pin
        self.display_controller = display_controller

        self.sensors = self.init_sensors()
        self.write_output = "sensors_bak"  # input("please specify a filename. Leave empty to only write to console.")

        self.interrupted = False

        gp.setmode(gp.BCM)
        gp.setup(23, gp.OUT)
        gp.output(23, gp.LOW)

        # self.app = create_app()
        # db.app = self.app
        # db.init_app(self.app)

    def interrupt(self):
        self.interrupted = True

    def run(self):
        logger.debug("Starting sensors")
        if self.alarm_thread is None:
            logger.warning("Starting without alarm thread!")
        logger.info("writing to file " + self.write_output + ".csv")
        # start here
        # collection = Collection(move_detection_sensor1=0, move_detection_sensor2=0, collected_time=ct, caid=1)
        ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.debug('Been here 1')
        collectionservice = CollectionDao()
        logger.debug('Been here 2')
        collectionservice.create_collection(0, 0, ct, 1)
        # !!!!!!!!!!!!!IMPORTANT!!!!!!!!!!!!!!!!    here I choose alarm one, there
        # should also be a variable that determines which alarm it is !!!!!!!!!!
        # I would like to hear what jelle would think about it.
        # end here
        f = open(self.write_output + ".csv", "a")
        f.write("Sleep logging started on " + datetime.now().strftime("%D") + " at " + datetime.now().strftime(
            "%H:%M:%S") + "\n")
        f.write("TIMESTAMP, SENSOR1, SENSOR2, HUMAN READABLE TIME \n")

        # clear interrupt pin state AGAIN
        for sensor in self.sensors:
            sensor.read_i2c_word(0x3A)

        # Initialization of flags for light sleep is detected
        count_ones = 0
        count_zeros = 0
        end_light_sleep = 0
        ones_allowed = 20

        try:
            f = open(self.write_output + ".csv", "a")
            while self.interrupted is not True:
                # Get input from sensors
                if gp.input(self.pin1) and gp.input(self.pin2):
                    logger.debug("motion detected by both sensors! Writing to file and resetting!.")
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(1, 1, ct, 1)
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 1, 1, %H : %M : %S\n"))
                    for sensor in self.sensors:
                        sensor.read_i2c_word(0x3A)
                    count_ones = count_ones + 1

                elif gp.input(self.pin1):
                    logger.debug("motion detected by s1! Writing to file and resetting!.")
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(1, 0, ct, 1)
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 1, 0, %H : %M : %S\n"))
                    for sensor in self.sensors:
                        sensor.read_i2c_word(0x3A)
                    count_ones = count_ones + 1

                elif gp.input(self.pin2):
                    logger.debug("motion detected by s2! Writing to file and resetting!.")
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(0, 1, ct, 1)
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 0, 1, %H : %M : %S\n"))
                    for sensor in self.sensors:
                        sensor.read_i2c_word(0x3A)
                    count_ones = count_ones + 1

                else:
                    logger.debug("no motion detected")
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(0, 0, ct, 1)
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 0, 0, %H : %M : %S\n"))
                    count_zeros = count_zeros + 1

                current_ID = collectionservice.last_one()[0]
                ones_allowed = 3  # ones_allowed = 20
                # Check current sleep cycle
                if count_ones >= ones_allowed and count_zeros > 10:  # 2000: # Deep to light sleep
                    logger.info("Deep sleep to light sleep transition")
                    self.set_light_sleep()
                    gp.output(23, gp.HIGH)
                    # if self.display_controller is not None:
                    #     # Display a dot when we detect light sleep
                    #     dot = [(6, 30), (7, 30), (6, 31), (7, 31)]
                    #     self.display_controller.paint_pixel_tuples(dot, row_origin=0, col_origin=0,
                    #                                                color=Color(0, 0, 255), show=False)
                    start_light_sleep = current_ID  # Set the start light sleep time
                    end_light_sleep = start_light_sleep + 10  # + 20 * 60  # Keep in light sleep for 20 minutes
                    count_zeros = 0  # Reset the variables after light sleep has been detected.
                    count_ones = 0
                elif count_ones >= ones_allowed and count_zeros <= 10:  # 2000:  # User still in light sleep
                    logger.info("Still in light sleep")
                    count_ones = 0
                    count_zeros = 0

                # Check if light sleep is over
                if current_ID >= end_light_sleep:
                    if self.alarm_thread.in_light_sleep is True:
                        logger.info("Moving out of light sleep")
                        self.set_deep_sleep()
                    gp.output(23, gp.LOW)
                    # dot = [(6, 30), (7, 30), (6, 31), (7, 31)]
                    # self.display_controller.paint_pixel_tuples(dot, row_origin=0, col_origin=0,
                    #                                            color=Color(0, 0, 0), show=False)

                # Check in one second again
                time.sleep(1)

            logger.info("Sensor thread interrupted")
        except IOError:
            logger.error("sensor(s) disconnected!")
            f.write("sensor(s) disconnected!")
        finally:
            gp.setmode(gp.BCM)
            gp.output(23, gp.LOW)
            f.close()
            logger.debug("Sensor thread stopped and backup file closed")

    def set_light_sleep(self):
        if self.alarm_thread is not None:
            self.alarm_thread.in_light_sleep = True

    def set_deep_sleep(self):
        if self.alarm_thread is not None:
            self.alarm_thread.in_light_sleep = False

    def init_sensors(self):
        # just checking to see whether we're running remotely
        for s in str(os.uname()).split(","):
            logger.debug(s)

        gp.setmode(gp.BCM)
        gp.setup(self.pin1, gp.IN, pull_up_down=gp.PUD_DOWN)
        gp.setup(self.pin2, gp.IN, pull_up_down=gp.PUD_DOWN)

        detected_sensors = []
        try:
            s1 = mpu6050.mpu6050(0x68, bus=1)
        except OSError:
            logger.error("s1@0x68 failed to connect.")
        else:
            detected_sensors.append(s1)

        try:
            s2 = mpu6050.mpu6050(0x69, bus=1)
        except OSError:
            logger.error("s2@0x69 failed to connect.")
        else:
            detected_sensors.append(s2)

        finally:
            if len(detected_sensors) > 0:
                logger.info("{} sensor(s) connected successfully".format(len(detected_sensors)))

                for init_sensor in detected_sensors:
                    # reset write paths? whatever that means
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x68, 0x07)

                    # configure interrupt pin
                    # print("interrupt " + bin(init_sensor.read_i2c_word(0x37)))
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x37, 0x20)
                    # print(bin(init_sensor.read_i2c_word(0x37)))

                    # digital high pass filter
                    # print("highpass " + bin(init_sensor.read_i2c_word(0x1C))) << this was bugging out the accel range...
                    # init_sensor.bus.write_byte_data(init_sensor.address, 0x1C, 0x01)
                    init_sensor.bus.write_byte_data(init_sensor.address,
                                                    init_sensor.ACCEL_CONFIG,
                                                    0x00)
                    # print(bin(init_sensor.read_i2c_word(0x1C)))

                    # motion threshold
                    # print("motion threshold " + bin(init_sensor.read_i2c_word(0x1F)))
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x1F, 1)
                    # print(bin(init_sensor.read_i2c_word(0x1F)))

                    # motion duration
                    # print("motion duration " + bin(init_sensor.read_i2c_word(0x20)))
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x20, 1)
                    # print(bin(init_sensor.read_i2c_word(0x20)))

                    # motion decrement
                    # print("motion decrement+ freefall " + bin(init_sensor.read_i2c_word(0x69)))
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x69, 0x15)
                    # print(bin(init_sensor.read_i2c_word(0x69)))

                    # motion detect interrupt
                    # print("motion detect interrupt " + bin(init_sensor.read_i2c_word(0x38)))
                    init_sensor.bus.write_byte_data(init_sensor.address, 0x38, 0x40)
                    # print(bin(init_sensor.read_i2c_word(0x38)))

                    # clear interrupt pin state
                    init_sensor.read_i2c_word(0x3A)

                return detected_sensors
            else:
                logger.warning("no sensors connected! exiting...")
                # exit(5)

    # gets data from sensor and reads 0x3A register to reset motion pin
    def get_data(self, sensor):
        data = [sensor.get_accel_data()["x"],
                sensor.get_accel_data()["y"],
                sensor.get_accel_data()["z"],
                sensor.get_gyro_data()["x"],
                sensor.get_gyro_data()["y"],
                sensor.get_gyro_data()["z"],
                sensor.get_temp()]
        sensor.read_i2c_word(0x3A)
        return data


# main sensor reading loop
if __name__ == '__main__':

    sensor_thread = SensorsThread(14, 15)
    sensor_thread.start()

"""

from mpu6050 import mpu6050

import os, sys, inspect

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parentparentdir = os.path.dirname(parentdir)
sys.path.insert(0, parentparentdir)

import os
import time
import RPi.GPIO as gp
from datetime import datetime

# try to connect to sensors
from wake_up_bright.alarm_clock.app import create_app
from wake_up_bright.alarm_clock.app.crud.controllers import CollectionDao
from wake_up_bright.alarm_clock.app.crud.models import Collection, db
from wake_up_bright.alarm_clock.app import create_app

app = create_app()
db.app = app
db.init_app(app)

app = create_app()
db.app = app
db.init_app(app)


def init_sensors():
    detected_sensors = []
    try:
        s1 = mpu6050(0x68, bus=1)
    except OSError as e:
        print("s1@0x68 failed to connect.")
    else:
        detected_sensors.append(s1)

    try:
        s2 = mpu6050(0x69, bus=1)
    except OSError as e:
        print("s2@0x69 failed to connect.")
    else:
        detected_sensors.append(s2)

    finally:
        if len(detected_sensors) > 0:
            print("{} sensor(s) connected successfully".format(len(detected_sensors)))

            for init_sensor in detected_sensors:
                # reset write paths? whatever that means
                init_sensor.bus.write_byte_data(init_sensor.address, 0x68, 0x07)

                # configure interrupt pin
                # print("interrupt " + bin(init_sensor.read_i2c_word(0x37)))
                init_sensor.bus.write_byte_data(init_sensor.address, 0x37, 0x20)
                # print(bin(init_sensor.read_i2c_word(0x37)))

                # digital high pass filter
                # print("highpass " + bin(init_sensor.read_i2c_word(0x1C))) << this was bugging out the accel range...
                # init_sensor.bus.write_byte_data(init_sensor.address, 0x1C, 0x01)
                init_sensor.bus.write_byte_data(init_sensor.address,
                                                init_sensor.ACCEL_CONFIG,
                                                0x00)
                # print(bin(init_sensor.read_i2c_word(0x1C)))

                # motion threshold
                # print("motion threshold " + bin(init_sensor.read_i2c_word(0x1F)))
                init_sensor.bus.write_byte_data(init_sensor.address, 0x1F, 1)
                # print(bin(init_sensor.read_i2c_word(0x1F)))

                # motion duration
                # print("motion duration " + bin(init_sensor.read_i2c_word(0x20)))
                init_sensor.bus.write_byte_data(init_sensor.address, 0x20, 1)
                # print(bin(init_sensor.read_i2c_word(0x20)))

                # motion decrement
                # print("motion decrement+ freefall " + bin(init_sensor.read_i2c_word(0x69)))
                init_sensor.bus.write_byte_data(init_sensor.address, 0x69, 0x15)
                # print(bin(init_sensor.read_i2c_word(0x69)))

                # motion detect interrupt
                # print("motion detect interrupt " + bin(init_sensor.read_i2c_word(0x38)))
                init_sensor.bus.write_byte_data(init_sensor.address, 0x38, 0x40)
                # print(bin(init_sensor.read_i2c_word(0x38)))

                # clear interrupt pin state
                init_sensor.read_i2c_word(0x3A)

            return detected_sensors
        else:
            print("no sensors connected! exiting...")
            exit(5)


# gets data from sensor and reads 0x3A register to reset motion pin
def getData(sensor):
    data = [sensor.get_accel_data()["x"],
            sensor.get_accel_data()["y"],
            sensor.get_accel_data()["z"],
            sensor.get_gyro_data()["x"],
            sensor.get_gyro_data()["y"],
            sensor.get_gyro_data()["z"],
            sensor.get_temp()]
    sensor.read_i2c_word(0x3A)
    return data


# main sensor reading loop
if __name__ == '__main__':
    # just checking to see whether we're running remotely
    for s in str(os.uname()).split(","):
        print(s)

    gp.setmode(gp.BCM)
    gp.setup(14, gp.IN, pull_up_down=gp.PUD_DOWN)
    gp.setup(15, gp.IN, pull_up_down=gp.PUD_DOWN)
    sensors = init_sensors()

    # setup file to write:
    x = input("please specify a filename. Leave empty to only write to console.")

    if len(x) is not 0:
        print("writing to file " + x + ".csv")
        # strat here
        # collection = Collection(move_detection_sensor1=0, move_detection_sensor2=0, collected_time=ct, caid=1)
        ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print('Been here 1')
        collectionservice = CollectionDao()
        print('Been here 2')
#         collectionservice.create_collection(0, 0, ct, 1)
        # !!!!!!!!!!!!!IMPORTANT!!!!!!!!!!!!!!!!    here I choose alarm one, there
        # should also be a variable that determines which alarm it is !!!!!!!!!!
        # I would like to hear what jelle would think about it.
        # end here
        f = open(x + ".csv", "a")
        f.write("Sleep logging started on " + datetime.now().strftime("%D") + " at " + datetime.now().strftime(
            "%H:%M:%S") + "\n")
        f.write("TIMESTAMP, SENSOR1, SENSOR2, HUMAN READABLE TIME \n")

        # clear interrupt pin state AGAIN
        for sensor in sensors:
            sensor.read_i2c_word(0x3A)

        while True:
            try:
                if gp.input(14) and gp.input(15):
                    # start
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(1, 1, ct, 1)
                    # end
                    print("motion detected by both sensors!\n writing to file and resetting!.")
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 1, 1, %H : %M : %S\n"))
                    for sensor in sensors:
                        sensor.read_i2c_word(0x3A)

                elif gp.input(14):
                    # start
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(1, 0, ct, 1)
                    # end
                    print("motion detected by s1!\n writing to file and resetting!.")
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 1, 0, %H : %M : %S\n"))
                    for sensor in sensors:
                        sensor.read_i2c_word(0x3A)

                elif gp.input(15):
                    # start
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(0, 1, ct, 1)
                    # end
                    print("motion detected by s2!\n writing to file and resetting!.")
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 0, 1, %H : %M : %S\n"))
                    for sensor in sensors:
                        sensor.read_i2c_word(0x3A)

                else:
                    ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    collectionservice.create_collection(0, 0, ct, 1)
                    print("no motion detected")
                    f.write(str(int(datetime.timestamp(datetime.now()))) + datetime.now().strftime(
                        ", 0, 0, %H : %M : %S\n"))

                f.close()
                time.sleep(1)
                f = open(x + ".csv", "a")
            except IOError:
                # error occured, log error and reinitalize sensors.
                f.write("sensor(s) disconnected!")
                sensors = init_sensors()

    else:
        # clear interrupt pin state AGAIN
        for sensor in sensors:
            sensor.read_i2c_word(0x3A)
        while True:
            try:
                if gp.input(14) and gp.input(15):
                    print("motion detected by both sensors!\n waiting 1s and resetting!.")
                    for sensor in sensors:
                        print(getData(sensor))

                elif gp.input(14):
                    print("motion detected by s1!\n waiting 1s and resetting!.")
                    for sensor in sensors:
                        print(getData(sensor))

                elif gp.input(15):
                    print("motion detected by s2!\n waiting 1s and resetting!.")
                    for sensor in sensors:
                        print(getData(sensor))

                else:
                    print("no motion detected")

                time.sleep(1)


            except IOError:
                # error occured, log error and reinitalize sensors.
                print("sensor error! reinitializing...")
                time.sleep(5)
                sensors = init_sensors()
                for sensor in sensors:
                    sensor.read_i2c_word(0x3A)
"""
