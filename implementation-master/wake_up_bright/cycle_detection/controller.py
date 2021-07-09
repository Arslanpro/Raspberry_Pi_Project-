import logging

from wake_up_bright.cycle_detection.sensor_testing_backup import SensorsThread

from wake_up_bright.log import get_logger
logger = get_logger()

class SensorController:

    def __init__(self, sensor1_pin: int, sensor2_pin: int, display_controller):
        self.pin1 = sensor1_pin
        self.pin2 = sensor2_pin
        self.display_controller = display_controller
        self.sensor_thread = None

    def create_sensor_thread(self):
        self.sensor_thread = SensorsThread(self.pin1, self.pin2, display_controller=self.display_controller)
        return self.sensor_thread

    def start_sensors(self):
        logger.debug("Starting sensor thread")
        self.sensor_thread.start()

    def stop_sensors(self):
        self.sensor_thread.interrupt()
        logger.debug("Stopping sensor thread")