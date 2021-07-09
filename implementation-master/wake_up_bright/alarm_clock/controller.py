import logging
import time

from wake_up_bright.alarm_clock.buttons import TactileButton, RotaryEncoder
from wake_up_bright.alarm_clock.display import DisplayController, Color
from wake_up_bright.alarm_clock.alarm import AlarmController, DFPlayer
from wake_up_bright.cycle_detection.controller import SensorController
import RPi.GPIO as GPIO

# from wake_up_bright.web_ui.web_app import WebUIThread

from wake_up_bright.log import get_logger

logger = get_logger()


class MainController:
    MAIN_MENU = 'main_menu'

    SET_ALARM = 'set_alarm'
    SET_ALARM_HOUR_START = 'set_alarm_hour_start'
    SET_ALARM_MINUTE_START = 'set_alarm_minute_start'
    SET_ALARM_HOUR_MAX = 'set_alarm_hour_max'
    SET_ALARM_MINUTE_MAX = 'set_alarm_minute_max'
    SET_ALARM_SAVE = 'set_alarm_save'
    SET_ALARM_PRESET_1 = 'set_alarm_preset1'
    SET_ALARM_PRESET_2 = 'set_alarm_preset2'

    START_ALARM = 'start_alarm'
    RINGING = 'ringing'

    SHUTDOWN_CONFIRM = 'shutdown_confirm'
    SHUTDOWN = 'shutdown'

    COLOR_SET_ALARM = Color(255, 255, 0)
    COLOR_ALARM_STARTED = Color(0, 255, 0)
    COLOR_MAIN_MENU = Color(255, 255, 255)
    COLOR_SHUTDOWN = Color(255, 0, 0)
    COLOR_RINGING = Color(0, 0, 255)
    COLOR_OFF = Color(0, 0, 0)

    SET_MINUTE_INTERVAL = 1  # 5  # Default minute interval is 5 minutes
    SET_HOUR_INTERVAL = 1

    def __init__(self):
        self.current_state = None
        self.next_state = None

        self.threads = dict()

        # Initialize the buttons
        self.button1 = TactileButton(26, self.nothing)
        self.button2 = TactileButton(20, self.nothing)
        self.button3 = TactileButton(19, self.nothing)
        self.button4 = TactileButton(16, self.nothing)
        self.button_rotary = RotaryEncoder(5, 6, self.nothing)

        # Initialize the other hardware
        self.display_controller = DisplayController(18)  # Inialize the LED matrix controller
        self.df_player_controller = DFPlayer(17, 27)  # Controller for the DF player (audio output) on pins 17 and 27
        self.sensor_controller = SensorController(14, 15, self.display_controller)  # Controller for sensors 14 and 15
        self.alarm_controller = AlarmController(hour_interval=self.SET_HOUR_INTERVAL,
                                                minute_interval=self.SET_MINUTE_INTERVAL,
                                                sensor_controller=self.sensor_controller)  # Controller for alarm

        # Start the different threads
        self.threads['matrix'] = self.display_controller.matrix_thread  # Add the display thread to the thread pool
        self.display_controller.start()  # The LED thread is nested in the DisplayController class
        # self.web_ui_thread = WebUIThread(port=8080, debug=True)  # Web UI thread
        # self.web_ui_thread.start()
        # self.threads['web_ui'] = self.web_ui_thread

    def start(self):
        self.next_state = self.MAIN_MENU
        self.main_loop()

    def main_loop(self):
        while True:
            # Main menu state
            if self.next_state == self.MAIN_MENU:
                self.next_state = None
                self.main_menu()

            # Set alarm states
            elif self.next_state == self.SET_ALARM:
                self.next_state = None
                self.set_alarm()
            elif self.next_state == self.SET_ALARM_HOUR_START:
                self.next_state = None
                self.set_alarm_hour_start()
            elif self.next_state == self.SET_ALARM_MINUTE_START:
                self.next_state = None
                self.set_alarm_minute_start()
            elif self.next_state == self.SET_ALARM_HOUR_MAX:
                self.next_state = None
                self.set_alarm_hour_max()
            elif self.next_state == self.SET_ALARM_MINUTE_MAX:
                self.next_state = None
                self.set_alarm_minute_max()
            elif self.next_state == self.SET_ALARM_SAVE:
                self.next_state = None
                self.set_alarm_save()

            # Transitional states (do not require button input
            elif self.next_state == self.SET_ALARM_PRESET_1:
                self.next_state = None
                self.set_alarm_preset1()
            elif self.next_state == self.SET_ALARM_PRESET_2:
                self.next_state = None
                self.set_alarm_preset2()

            elif self.next_state == self.START_ALARM:
                self.next_state = None
                self.start_alarm()
            elif self.next_state == self.RINGING:
                self.next_state = None
                self.alarm_ringing()

            # Shutdown states
            elif self.next_state == self.SHUTDOWN_CONFIRM:
                self.next_state = None
                self.shutdown_confirm()
            elif self.next_state == self.SHUTDOWN:
                self.next_state = None
                self.shutdown()
                return  # Exit the loop
            else:
                time.sleep(0.5)

    def nothing(self, *args, **kwargs):
        logger.debug("Button not assigned.")
        pass

    ###################
    # Main Menu State #
    ###################

    def setstate_main_menu(self):
        self.next_state = self.MAIN_MENU

    def main_menu(self):
        # Set up current state
        self.current_state = self.MAIN_MENU
        logger.info(self.current_state)
        # Assign button callbacks
        self.button1.callback = self.setstate_set_alarm
        self.button2.callback = self.nothing
        self.button3.callback = self.nothing
        self.button4.callback = self.setstate_shutdown_confirm
        self.button_rotary.callback = self.nothing
        # Run methods on controllers
        self.display_controller.clock_current_time(color=self.COLOR_MAIN_MENU)

    ####################
    # Set Alarm States #
    ####################

    def setstate_set_alarm(self):
        self.next_state = self.SET_ALARM

    def set_alarm(self):
        """Set alarm base state."""
        self.current_state = self.SET_ALARM
        logger.info(self.current_state)

        self.button1.callback = self.nothing  # self.setstate_set_alarm_preset1
        self.button2.callback = self.nothing  # self.setstate_set_alarm_preset2
        self.button3.callback = self.setstate_set_alarm_hour_start
        self.button4.callback = self.setstate_main_menu
        self.button_rotary.callback = self.nothing

        self.display_controller.clear(show=False)
        self.display_controller.clock_current_time(col_origin=5, color=self.COLOR_SET_ALARM)

    def setstate_set_alarm_hour_start(self):
        self.next_state = self.SET_ALARM_HOUR_START

    def set_alarm_hour_start(self):
        """Set the hour of the alarm."""
        self.current_state = self.SET_ALARM_HOUR_START
        logger.info(self.current_state)
        self.button1.callback = self.nothing
        self.button2.callback = self.nothing
        self.button3.callback = self.setstate_set_alarm_minute_start
        self.button4.callback = self.setstate_set_alarm
        self.button_rotary.callback = self._set_hour_start_callback

        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_start_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='<', color=self.COLOR_SET_ALARM, show=False)
        hours_line = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        self.display_controller.paint_pixel_tuples(hours_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def _set_hour_start_callback(self, direction):
        """Callback for the rotary dial which updates the clock time and display when setting hours."""
        self.alarm_controller.set_hour_alarm_time_start(direction)
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_start_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='<', color=self.COLOR_SET_ALARM, show=False)
        hours_line = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        self.display_controller.paint_pixel_tuples(hours_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def setstate_set_alarm_minute_start(self):
        self.next_state = self.SET_ALARM_MINUTE_START

    def set_alarm_minute_start(self):
        """Set the minute of the alarm."""
        self.current_state = self.SET_ALARM_MINUTE_START
        logger.info(self.current_state)
        self.button1.callback = self.nothing
        self.button2.callback = self.nothing
        self.button3.callback = self.setstate_set_alarm_hour_max
        self.button4.callback = self.setstate_set_alarm_hour_start
        self.button_rotary.callback = self._set_minute_start_callback

        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_start_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='<', color=self.COLOR_SET_ALARM, show=False)
        minute_line = [(7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16), (7, 17)]
        self.display_controller.paint_pixel_tuples(minute_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def _set_minute_start_callback(self, direction):
        """Callback for the rotary dial which updates the clock time and display when setting minutes."""
        self.alarm_controller.set_minute_alarm_time_start(direction)
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_start_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='<', color=self.COLOR_SET_ALARM, show=False)
        minute_line = [(7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16), (7, 17)]
        self.display_controller.paint_pixel_tuples(minute_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def setstate_set_alarm_hour_max(self):
        self.next_state = self.SET_ALARM_HOUR_MAX

    def set_alarm_hour_max(self):
        """Set the hour of the alarm."""
        self.current_state = self.SET_ALARM_HOUR_MAX
        logger.info(self.current_state)
        self.button1.callback = self.nothing
        self.button2.callback = self.nothing
        self.button3.callback = self.setstate_set_alarm_minute_max
        self.button4.callback = self.setstate_set_alarm_minute_start
        self.button_rotary.callback = self._set_hour_max_callback

        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_max_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='>', col_origin=23, color=self.COLOR_SET_ALARM, show=False)
        hours_line = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        self.display_controller.paint_pixel_tuples(hours_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def _set_hour_max_callback(self, direction):
        """Callback for the rotary dial which updates the clock time and display when setting hours."""
        self.alarm_controller.set_hour_alarm_time_max(direction)
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_max_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='>', col_origin=23, color=self.COLOR_SET_ALARM, show=False)
        hours_line = [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6), (7, 7)]
        self.display_controller.paint_pixel_tuples(hours_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def setstate_set_alarm_minute_max(self):
        self.next_state = self.SET_ALARM_MINUTE_MAX

    def set_alarm_minute_max(self):
        """Set the minute of the alarm."""
        self.current_state = self.SET_ALARM_MINUTE_MAX
        logger.info(self.current_state)
        self.button1.callback = self.nothing
        self.button2.callback = self.nothing
        self.button3.callback = self.setstate_set_alarm_save
        self.button4.callback = self.setstate_set_alarm_hour_max
        self.button_rotary.callback = self._set_minute_max_callback

        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_max_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='>', col_origin=23, color=self.COLOR_SET_ALARM, show=False)
        minute_line = [(7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16), (7, 17)]
        self.display_controller.paint_pixel_tuples(minute_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def _set_minute_max_callback(self, direction):
        """Callback for the rotary dial which updates the clock time and display when setting minutes."""
        self.alarm_controller.set_minute_alarm_time_max(direction)
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_max_str, col_origin=5,
                                            color=self.COLOR_SET_ALARM, show=False)
        self.display_controller.paint_character(character='>', col_origin=23, color=self.COLOR_SET_ALARM, show=False)
        minute_line = [(7, 11), (7, 12), (7, 13), (7, 14), (7, 15), (7, 16), (7, 17)]
        self.display_controller.paint_pixel_tuples(minute_line, row_origin=0, col_origin=4, color=self.COLOR_SET_ALARM,
                                                   show=True)

    def setstate_set_alarm_save(self):
        self.next_state = self.SET_ALARM_SAVE

    def set_alarm_save(self):
        """Save the alarm to a preset or continue."""
        self.current_state = self.SET_ALARM_SAVE
        logger.info(self.current_state)
        self.button1.callback = self.nothing  # self.alarm_controller.save_alarm  # self.alarm_controller.save_preset1
        self.button2.callback = self.nothing  # self.alarm_controller.save_alarm  # self.alarm_controller.save_preset2
        self.button3.callback = self.nothing
        self.button4.callback = self.nothing
        self.button_rotary.callback = self.nothing

        self.alarm_controller.save_alarm()  # Save the current alarm

        # Display a green flashing overview of the alarm saved
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_start_str, col_origin=5,
                                            color=self.COLOR_ALARM_STARTED, show=False)
        self.display_controller.paint_character(character='<', color=self.COLOR_ALARM_STARTED, show=True)
        time.sleep(3)
        self.display_controller.clear(show=False)
        self.display_controller.paint_clock(self.alarm_controller.alarm_time_max_str, col_origin=5,
                                            color=self.COLOR_ALARM_STARTED, show=False)
        self.display_controller.paint_character(character='>', col_origin=23, color=self.COLOR_ALARM_STARTED, show=True)
        time.sleep(3)
        self.setstate_start_alarm()  # Start the alarm automatically

    def setstate_set_alarm_preset1(self):
        self.next_state = self.SET_ALARM_PRESET_1

    def set_alarm_preset1(self):
        """Set alarm stored in preset 1 (transitional state, no user input required)."""
        self.current_state = self.SET_ALARM_PRESET_1
        logger.info(self.current_state)
        # self.alarm_controller.load_preset1()
        self.setstate_start_alarm()

    def setstate_set_alarm_preset2(self):
        self.next_state = self.SET_ALARM_PRESET_2

    def set_alarm_preset2(self):
        """Set alarm stored in preset 2 (transitional state, no user input required)."""
        self.current_state = self.SET_ALARM_PRESET_2
        logger.info(self.current_state)
        # self.alarm_controller.load_preset2()
        self.setstate_start_alarm()

    #####################
    # Start Alarm State #
    #####################

    def setstate_start_alarm(self):
        self.next_state = self.START_ALARM

    def start_alarm(self):
        """Start the alarm (transitional state, no user input required)."""
        self.current_state = self.START_ALARM
        logger.info(self.current_state)
        self.alarm_controller.start_all_alarms(self.setstate_alarm_ringing)
        self.threads.update(self.alarm_controller.running_alarms)
        # self.alarm_controller.start_alarm()

        # self.display_controller.clock_current_time(color=self.COLOR_ALARM_STARTED)  # Show a green display for 4 seconds
        # time.sleep(4)

        self.setstate_main_menu()  # Go to the main menu

    def setstate_alarm_ringing(self):
        self.next_state = self.RINGING

    def alarm_ringing(self):
        self.current_state = self.RINGING
        logger.info(self.current_state)
        self.button1.callback = self.snooze
        self.button2.callback = self.snooze
        self.button3.callback = self.snooze
        self.button4.callback = self.dismiss

        self.df_player_controller.start_sound()  # Start sound
        # Display the wake up sequence
        self.display_controller.paint_snake(color=self.COLOR_RINGING, wait_ms=0)
        self.display_controller.paint_snake(color=self.COLOR_OFF, wait_ms=0)
        self.display_controller.clock_current_time_toggle(color=self.COLOR_RINGING, toggle_time=1)

    def snooze(self):
        self.df_player_controller.pause_sound()
        self.alarm_controller.snooze(self.setstate_alarm_ringing)
        self.threads.update(self.alarm_controller.running_alarms)
        self.setstate_main_menu()

    def dismiss(self):
        self.df_player_controller.pause_sound()
        self.setstate_main_menu()
        logger.info("Alarm dismissed")

    ##################
    # Shutdown State #
    ##################

    def setstate_shutdown_confirm(self):
        self.next_state = self.SHUTDOWN_CONFIRM

    def shutdown_confirm(self):
        self.current_state = self.SHUTDOWN_CONFIRM
        logger.info(self.current_state)
        self.button1.callback = self.setstate_main_menu
        self.button2.callback = self.setstate_main_menu
        self.button3.callback = self.setstate_main_menu
        self.button4.callback = self.setstate_shutdown
        self.display_controller.clock_current_time(color=self.COLOR_SHUTDOWN)

    def setstate_shutdown(self):
        self.next_state = self.SHUTDOWN

    def shutdown(self):
        logger.debug("Shutdown started")
        self.current_state = self.SHUTDOWN
        logger.info(self.current_state)
        self.button1.callback = self.nothing
        self.button2.callback = self.nothing
        self.button3.callback = self.nothing
        self.button4.callback = self.nothing

        # Clean up
        GPIO.cleanup()
        self.display_controller.clear()
        self.display_controller.stop()
        self.alarm_controller.stop_all_alarms()
        self.sensor_controller.stop_sensors()
        for thread in self.threads.values():
            thread.join()
        logger.info("Shutdown successful")


if __name__ == '__main__':
    # Setup the loggers
    # logging.basicConfig(format="%(threadName)s:%(message)s", level=logging.DEBUG)
    # logging.basicConfig(format="%(threadName)s:%(message)s", level=logging.INFO)
    # logging.getLogger('sqlalchemy').setLevel(logging.ERROR)

    from wake_up_bright.alarm_clock.app import create_app, db

    app = create_app()
    # app.db = db
    # db.init_app(app)

    controller = MainController()
    controller.start()
