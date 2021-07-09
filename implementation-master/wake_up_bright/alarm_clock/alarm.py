import inspect
import logging
import os
import sys
from datetime import datetime, timedelta

import RPi.GPIO as GPIO
import time
from threading import Thread
from pathlib import Path

# currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
# parentdir = os.path.dirname(currentdir)
# # parentparentdir = os.path.dirname(parentdir)
# # sys.path.insert(0, parentparentdir)
# sys.path.insert(0, parentdir)

from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao
from wake_up_bright.cycle_detection.controller import SensorController, SensorsThread

from wake_up_bright.log import get_logger

logger = get_logger()


class DFPlayer:

    def __init__(self, pin1: int, pin2: int):
        self.pin1 = pin1
        self.pin2 = pin2
        GPIO.setmode(GPIO.BCM)
        # self.pin1 = 11
        # self.pin2 = 13
        # GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin1, GPIO.OUT)
        GPIO.setup(self.pin2, GPIO.OUT)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)

    def start_sound(self):
        logger.info("Playing sound")
        GPIO.output(self.pin1, GPIO.HIGH)
        time.sleep(1)  # This is done to simulate a short press which will start playing music
        GPIO.output(self.pin1, GPIO.LOW)
        # time.sleep(1)
        # GPIO.output(self.pin1, GPIO.LOW)

    def pause_sound(self):
        logger.info("Stopping sound")
        GPIO.output(self.pin1, GPIO.HIGH)
        GPIO.output(self.pin2, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.pin1, GPIO.LOW)
        GPIO.output(self.pin2, GPIO.LOW)


class ActiveAlarmThread(Thread):

    def __init__(self, start_wake_up_period: str, max_wake_up_time: str, callback, sensor_thread: SensorsThread = None):
        super().__init__(name="alarm_" + start_wake_up_period)
        self.start_wake_up_period_str = start_wake_up_period
        self.start_wake_up_period = datetime.strptime(self.start_wake_up_period_str, "%H%M")
        self.max_wake_up_time_str = max_wake_up_time
        self.max_wake_up_time = datetime.strptime(self.max_wake_up_time_str, "%H%M")
        self.callback = callback
        self.sensor_thread = sensor_thread
        self.interrupted = False
        self.in_light_sleep = False

    def run(self):
        logger.debug("Alarm %s started" % (self.start_wake_up_period_str + "-" + self.max_wake_up_time_str))
        while self.interrupted is False:  # Run until interrupted
            current_time = datetime.strptime(str(datetime.now().hour).zfill(2) + str(datetime.now().minute).zfill(2),
                                             '%H%M')
            current_time_str = current_time.strftime('%H%M')

            if current_time_str == self.max_wake_up_time_str:  # If the clock has reached its maximum wake up time
                logger.info("Max wake up time reached, alarm is ringing!")
                if self.sensor_thread is not None:
                    self.sensor_thread.interrupt()  # Stop the sensors too
                self.callback()  # Execute the callback for the alarm
                return  # Exit the thread

            elif self.in_light_sleep is True and self.start_wake_up_period <= current_time <= self.max_wake_up_time:  # If we are in the wake up period and in light sleep
                logger.info("Light sleep detected in wake up period, alarm is ringing!")
                if self.sensor_thread is not None:
                    self.sensor_thread.interrupt()  # Stop the sensors too
                self.callback()  # Execute the callback for the alarm
                return  # Exit the thread

            else:  # No need to wake up yet
                time.sleep(5)  # Sleep before checking the time again
        logger.info("Stopping thread")

    def interrupt(self):
        self.interrupted = True


class AlarmController:
    ALARM_DATABASE_FILE = 'set_alarm_time.txt'

    def __init__(self, hour_interval: int = 1, minute_interval: int = 5, snooze_time: int = 5,
                 sensor_controller: SensorController = None):
        self.minute_interval = minute_interval
        self.hour_interval = hour_interval
        self.snooze_time = snooze_time
        self.sensor_controller = sensor_controller
        self.alarm_time_start_str = datetime.now().strftime('%H%M')  # '0000'
        self.alarm_time_max_str = datetime.now().strftime('%H%M')  # '0000'
        self.running_alarms = dict()
        self.alarmservice = AlarmDao()

        # Remove the text file at startup
        try:
            directory = Path(__file__).parent
            file_path = directory.joinpath(self.ALARM_DATABASE_FILE)
            os.remove(file_path)
        except FileNotFoundError:
            pass

    def update_hour(self, old_time_str: str, direction: int) -> str:
        """Take a time string of 4 numbers (e.g. '0223' or '2307') and update the hour."""
        if len(old_time_str) != 4:
            raise ValueError("Expected an old_time_str of length 4, got %d instead." % len(old_time_str))
        old_hour = int(old_time_str[0:2])
        new_hour = old_hour + (direction * self.hour_interval)

        # Check if new hour is within bounds [0,23] (24 hour display, but 24:00 is converted to 00:00)
        if new_hour < 0:
            new_hour = 24 + new_hour  # Loop hour around if it becomes negative
        elif new_hour >= 24:
            new_hour = new_hour - 24  # Loop hour around if it is 24 or higher

        new_hour_str = str(new_hour).zfill(2)  # Add 0s before the number if it is single digit
        old_minute_str = old_time_str[2:4]
        new_time_str = new_hour_str + old_minute_str
        return new_time_str

    def update_minute(self, old_time_str: str, direction: int) -> str:
        """Take a time string of 4 numbers (e.g. '0223' or '2307') and update the minute."""
        if len(old_time_str) != 4:
            raise ValueError("Expected an old_time_str of length 4, got %d instead." % len(old_time_str))
        old_minute = int(old_time_str[2:4])
        new_minute = old_minute + (direction * self.minute_interval)

        # Check if new hour is within bounds [0,59] (60 minute display, but 01:60 is converted to 01:00)
        if new_minute < 0:
            new_minute = 60 + new_minute  # Loop minute around
        elif new_minute >= 60:
            new_minute = new_minute - 60

        new_minute_str = str(new_minute).zfill(2)  # Add 0s before number if it is single digit (e.g. '9' becomes '09')
        old_hour_str = old_time_str[0:2]
        new_time_str = old_hour_str + new_minute_str
        return new_time_str

    def set_hour_alarm_time_start(self, direction):
        """Set the hour of the start of the wake up period."""
        self.alarm_time_start_str = self.update_hour(self.alarm_time_start_str, direction)
        logger.debug("Alarm time: %s" % self.alarm_time_start_str)

    def set_hour_alarm_time_max(self, direction):
        """Set the hour of the maximum wake up time."""
        self.alarm_time_max_str = self.update_hour(self.alarm_time_max_str, direction)
        logger.debug("Alarm time: %s" % self.alarm_time_max_str)

    def set_minute_alarm_time_start(self, direction):
        """Set the minute of the start of the wake up period."""
        self.alarm_time_start_str = self.update_minute(self.alarm_time_start_str, direction)
        logger.debug("Alarm time: %s" % self.alarm_time_start_str)

    def set_minute_alarm_time_max(self, direction):
        """Set the minute of the maximum wake up time."""
        self.alarm_time_max_str = self.update_minute(self.alarm_time_max_str, direction)
        logger.debug("Alarm time: %s" % self.alarm_time_max_str)

    def save_alarm(self):
        logger.debug("Starting save")
        directory = Path(__file__).parent
        file_path = directory.joinpath(self.ALARM_DATABASE_FILE)
        with open(file_path, 'a+') as f:
            f.seek(0)  # Make sure read the file from first line
            for line in f.readlines():
                logger.debug(line)
                line = line.rstrip('\n').rstrip('E')  # E means active, without E means this alarm is turn off
                read_time = line.split(' ', 1)[0]  # only check the start alarm, system will choose smallest range time
                if read_time == self.alarm_time_start_str:  # The alarm was already present in the db
                    self._toggle_active(self.alarm_time_start_str[0:2], self.alarm_time_start_str[2:4],
                                        self.alarm_time_max_str[0:2],
                                        self.alarm_time_max_str[2:4])  # Toggle whether the alarm is active
                    return  # Stop this function

            # If the alarm was not present in the file already, add it
            logger.debug("Alarm %s saved." % (self.alarm_time_start_str + " " + self.alarm_time_max_str))
            alarm_time = self.alarm_time_start_str + " " + self.alarm_time_max_str + 'E' + '\n'  # If we input a new alarm, we make it active by default
            f.write(alarm_time)  # Write the new alarm in file

            hour_start = self.alarm_time_start_str[0:2]
            minute_start = self.alarm_time_start_str[2:4]
            hour_max = self.alarm_time_max_str[0:2]
            minute_max = self.alarm_time_max_str[2:4]
            ct = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            alarmservice = AlarmDao()
            at = datetime.strptime(self.alarm_time_start_str, '%H%M')
            at1 = datetime.strptime(self.alarm_time_max_str, '%H%M')
            on_off = self._check_alarm_active(hour_start, minute_start, hour_max, minute_max)  # 0 means off, 1 means on
            alarmservice.create_Alarm(ct, at, at1, 5, ct, 2, on_off)
            return

    def _check_alarm_active(self, hour_start, minute_start, hour_max, minute_max):
        logger.debug("Starting save")
        directory = Path(__file__).parent
        file_path = directory.joinpath(self.ALARM_DATABASE_FILE)
        with open(file_path) as f:
            f.seek(0)
            for line in f.readlines():  # Take out all the saved alarm clocks.
                alarm = line.split(" ", 1)  # we only check the starting time
                if alarm[0] == hour_start + minute_start and alarm[1] == hour_max + minute_max + '\n':  # without E
                    logger.debug("Alarm is active")
                    return 0
                elif alarm[0] == hour_start + minute_start and alarm[
                    1] == hour_max + minute_max + "E" + '\n':  # with E
                    logger.debug("Alarm is inactive")
                    return 1
                else:
                    continue

    def start_alarm(self, start_wake_up_period: str, max_wake_up_time: str, callback):
        sensor_thread = self.sensor_controller.create_sensor_thread()
        alarm_thread = ActiveAlarmThread(start_wake_up_period, max_wake_up_time, callback=callback,
                                         sensor_thread=sensor_thread)
        sensor_thread.alarm_thread = alarm_thread
        self.running_alarms[start_wake_up_period] = alarm_thread
        self.sensor_controller.start_sensors()
        alarm_thread.start()

    def start_all_alarms(self, callback):
        directory = Path(__file__).parent
        file_path = directory.joinpath(self.ALARM_DATABASE_FILE)
        with open(file_path) as f:
            alarms = f.readlines()  # Take out all the saved alarm clocks.
            for alarm_str in alarms:
                if alarm_str.find("E"):  # If this alarm is active
                    alarm_time = alarm_str.split(" ", 1)
                    start_time = alarm_time[0][0:4]  # Extract the first 4 characters
                    max_time = alarm_time[1][0:4]  # Extract the first 4 characters
                    self.start_alarm(start_time, max_time, callback)

    def snooze(self, callback):
        dt = timedelta(minutes=self.snooze_time)
        next_alarm = datetime.now() + dt
        next_alarm_str = next_alarm.strftime('%H%M')
        start_alarm_dummy = datetime.now() + dt + dt  # Make sure the start_time is larger than max_time so light sleep detection is disabled
        start_alarm_dummy_str = start_alarm_dummy.strftime('%H%M')
        self.start_alarm(start_alarm_dummy_str, next_alarm_str, callback)
        logger.info("Snoozing until %s" % next_alarm_str)

    def stop_alarm(self, alarm_str: str):
        alarm_thread = self.running_alarms[alarm_str]
        logger.debug("Alarm %s interrupted" % (alarm_str))
        alarm_thread.interrupt()

    def stop_all_alarms(self):
        for alarm_thread in self.running_alarms.keys():
            self.stop_alarm(alarm_thread)

    def _toggle_active(self, hour_start, minute_start, hour_max, minute_max):
        directory = Path(__file__).parent
        file_path = directory.joinpath(self.ALARM_DATABASE_FILE)
        tmp_file = directory.joinpath('tmp.txt')
        with open(file_path, 'a+') as fin, open(tmp_file, 'a+') as fout:  # 'a+' means point start from the end
            fin.seek(0)
            for line in fin:
                start_time = line.split(" ", 1)[0]
                max_time = line.split(" ", 1)[1]
                max_time = max_time.rstrip("\n").rstrip("E")
                if start_time == hour_start + minute_start and line.find("E") != -1:  # Alarm is active already
                    if int(hour_max + minute_max) < int(max_time):  # if the new range is shorter
                        logger.debug("Wake up period will become shorter")
                        # Update in database
                        self.alarmservice.use_alarm_time_and_change_at1(hour_start + ":" + minute_start,
                                                                        hour_max + ":" + minute_max)
                        # Also store in txt file again
                        fout.write(hour_start + minute_start + " " + hour_max + minute_max + "E" + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                    elif int(hour_max + minute_max) > int(max_time):  # old one is shorter, dont change status and range
                        logger.debug("Wake up period will not change")
                        fout.write(hour_start + minute_start + " " + max_time + "E" + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                    elif int(hour_max + minute_max) == int(max_time):
                        logger.debug("Disable alarm")
                        self.alarmservice.use_alarm_time_and_change_on_off(hour_start + ":" + minute_start)
                        fout.write(hour_start + minute_start + " " + max_time + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                        break
                    break
                elif start_time == hour_start + minute_start and (line.find("E") == -1):  # old alarm is disabled
                    if int(hour_max + minute_max) < int(max_time):  # if the new range is shorter
                        logger.debug("Case 4")
                        self.alarmservice.use_alarm_time_and_change_on_off(hour_start + ":" + minute_start)
                        self.alarmservice.use_alarm_time_and_change_at1(hour_start + ":" + minute_start,
                                                                        hour_max + ":" + minute_max)
                        fout.write(hour_start + minute_start + " " + hour_max + minute_max + "E" + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                    elif int(hour_max + minute_max) > int(max_time):  # old one is shorter
                        logger.debug("case5")
                        fout.write(hour_start + minute_start + " " + max_time + "E" + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                        self.alarmservice.use_alarm_time_and_change_on_off(hour_start + ":" + minute_start)
                    elif hour_max + minute_max == max_time:
                        logger.debug("case6")
                        self.alarmservice.use_alarm_time_and_change_on_off(hour_start + ":" + minute_start)
                        fout.write(hour_start + minute_start + " " + max_time + "E" + "\n")
                        for original_line in fin:
                            fout.write(original_line)
                        fin.seek(0)
                        fin.truncate()
                        fout.seek(0)
                        fin.write(fout.read())
                        fout.close()
                        os.remove("temp.txt")
                        break
                    break
                else:
                    fout.write(line)
                #
                # if line == hour + minute + 'E' + '\n':
                #     fout.write(hour + minute + '\n')
                #     for original_line in fin:
                #         fout.write(original_line)
                #     fin.seek(0)
                #     fin.truncate()
                #     fout.seek(0)
                #     fin.write(fout.read())
                #     fout.close()
                #     os.remove(tmp_file)
                #     logger.debug("Alarm %s toggled OFF" % (hour + minute))
                #     break
                # elif line == hour + minute + '\n':
                #     fout.write(hour + minute + 'E' + '\n')
                #     for original_line in fin:
                #         fout.write(original_line)
                #     fin.seek(0)
                #     fin.truncate()
                #     fout.seek(0)
                #     fin.write(fout.read())
                #     fout.close()
                #     os.remove(tmp_file)
                #     logger.debug("Alarm %s toggled ON" % (hour + minute))
                #     break
                # else:
                #     fout.write(line)
                #     finally:
                #     pass


def _ring():
    logger.info('Wake up!')


if __name__ == '__main__':
    pass
    logger = get_logger()
    player = DFPlayer(17, 27)
    time.sleep(0.2)
    player.start_sound()
    time.sleep(5)
    player.pause_sound()
    GPIO.cleanup()
    # try:
    #     os.remove(Path(__file__).parent / AlarmController.ALARM_DATABASE_FILE)
    # except FileNotFoundError:
    #     pass
    #
    # controller = AlarmController()
    # controller.alarm_time_start_str = '0201'
    # controller.save_alarm()
    # controller.alarm_time_start_str = '0202'
    # controller.save_alarm()
    # controller.start_all_alarms(_ring)

    # alarm_thread = ActiveAlarmThread('0024', _ring)
    # alarm_thread.start()

    message = input('Press enter to quit\n\n')

    # alarm_controller = AlarmController()
    # alarm_controller.set_minute(-1)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_hour(-1)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_hour(-1)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_hour(-2)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_minute(1)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_minute(4)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_minute(-5)
    # print(alarm_controller.current_alarm)
    # alarm_controller.set_minute(-1)
    # print(alarm_controller.current_alarm)
