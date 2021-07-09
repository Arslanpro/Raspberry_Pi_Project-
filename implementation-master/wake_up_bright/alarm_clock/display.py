from threading import Thread, Event
from queue import Queue
import time
from datetime import datetime
from rpi_ws281x import PixelStrip, Color
import logging

from wake_up_bright.log import get_logger
logger = get_logger()


# LED strip configuration:
MATRIX_COLS = 32  # Nr of columns on the matrix
MATRIX_ROWS = 8  # Nr of rows on the matrix
LED_BRIGHTNESS = 7  # Set to 0 for darkest and 255 for brightest
LED_PIN = 18  # GPIO pin connected to the pixels (18 uses PWM!)
DEFAULT_UPDATE_TIME = 250  # Default screen update time in ms

LED_COUNT = MATRIX_COLS * MATRIX_ROWS  # Number of LED pixels
# LED_PIN = 10            # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0  # set to '1' for GPIOs 13, 19, 41, 45 or 53


# Set up local functions to use for bounds checking
def transfer(n, minn, maxn):
    """
    Local function to transfer n back into bounds if it is outside range [minn, maxn] inclusive.

    Example: Range [0, 3]
    Input n = 1 ==> Output = 1
    Input n = 5 ==> Output = 1
    Input n = 3 ==> Output = 3
    Input n = 4 ==> Output = 0

    :param n: Input number
    :param minn: Lower bound of range (this number is also included in bounds)
    :param maxn: Upper bound of range (this number is also included in bounds)
    :return: Transferred number
    """
    if n < minn:
        n = n + maxn + 1
    elif n > maxn:
        n = n - maxn - 1
    return n


def clamp(n, minn, maxn):
    """
    Local function to clamp n to bounds if it is outside range [minn, maxn] inclusive.

    Example: Range [0, 3]
    Input n = 1 ==> Output = 1
    Input n = 5 ==> Output = 3
    Input n = 3 ==> Output = 3
    Input n = -2 ==> Output = 0

    :param n: Input number
    :param minn: Lower bound of range (this number is also included in bounds)
    :param maxn: Upper bound of range (this number is also included in bounds)
    :return: Clamped number
    """
    return max(min(maxn, n), minn)


def within_bounds(n, minn, maxn):
    """
    Return True when minn <= n <= maxn.
    """
    return minn <= n <= maxn


class MATRIX_CHARS:

    @classmethod
    def get(cls, character: str) -> dict:
        """
        Return the pixel tuples and size for the requested character. If the character is not found, return ERROR_CHAR.
        :param character: Character to request
        :return: A dict with fields 'size' and 'pixels'
        """
        try:
            return cls.CHARS[character]
        except KeyError:  # If the character is not found
            logger.warning("Character '" + character + "' not found.")
            return cls.ERROR_CHAR

    ERROR_CHAR = dict({'size': (5, 3),
                       'pixels': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                                  (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
                                  (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]})

    CHARS = dict({
        '0': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                         (0, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
              },
        '1': {'size': (5, 3),
              'pixels': [(1, 0), (4, 0),
                         (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
                         (4, 2)]
              },
        '2': {'size': (5, 3),
              'pixels': [(0, 0), (2, 0), (3, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2), (4, 2)]
              },
        '3': {'size': (5, 3),
              'pixels': [(0, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
              },
        '4': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0),
                         (2, 1),
                         (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
              },
        '5': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (2, 2), (3, 2), (4, 2)]
              },
        '6': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (2, 2), (3, 2), (4, 2)]
              },
        '7': {'size': (5, 3),
              'pixels': [(0, 0), (3, 0), (4, 0),
                         (0, 1), (2, 1),
                         (0, 2), (1, 2)]
              },
        '8': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
              },
        '9': {'size': (5, 3),
              'pixels': [(0, 0), (1, 0), (2, 0), (4, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2), (3, 2), (4, 2)]
              },
        ':': {'size': (5, 1),
              'pixels': [(1, 0), (3, 0)]
              },
        '.': {'size': (5, 1),
              'pixels': [(4, 0)]
              },
        ' ': {'size': (5, 1),
              'pixels': []
              },
        '?': {'size': (5, 3),
              'pixels': [(0, 0),
                         (0, 1), (2, 1), (4, 1),
                         (0, 2), (1, 2), (2, 2)]
              },
        '!': {'size': (5, 1),
              'pixels': [(0, 0), (1, 0), (2, 0), (4, 0)]
              },
        '>': {'size': (5, 3),
              'pixels': [(0, 0), (4, 0),
                         (1, 1), (3, 1),
                         (2, 2)]
              },
        '<': {'size': (5, 3),
              'pixels': [(2, 0),
                         (1, 1), (3, 1),
                         (0, 2), (4, 2)]
              }

    })


class LedMatrix:

    def __init__(self, strip: PixelStrip, rows, cols) -> None:
        """
        Initialize this Led Matrix.
        :param strip: rpi_ws281x.PixelStrip instance
        :param rows: Total rows of this matrix
        :param cols: Total columns of this matrix
        """
        self.strip = strip
        self.rows = rows
        self.cols = cols
        self._interrupted = False  # Flag to interrupt looping methods

    def begin(self) -> None:
        """
        Start the LED strip (needed before other method calls).
        """
        self.strip.begin()

    def show(self) -> None:
        """
        Update the strip to display all buffered LED data.
        """
        self.strip.show()

    def interrupt(self) -> None:
        """
        Set the self._interrupted flag to True to interrupt a looping method
        """
        self._interrupted = True

    def uninterrupt(self) -> None:
        """
        Set the self._interrupted flag to False to allow looping method to run again
        """
        self._interrupted = False

    def clear(self, show: bool = True) -> None:
        """
        Turn off all LEDs.
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(0, 0, 0))
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_pixel_row_col(self, row: int, col: int, color, show: bool = True) -> None:
        """
        Paint a pixel.
        :param row: Row coordinate
        :param col: Col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        led_index = self._row_col_to_strip(row, col)
        self.strip.setPixelColor(led_index, color)
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_pixel_strip_index(self, strip_index: int, color, show: bool = True) -> None:
        """
        Paint a pixel.
        :param strip_index: Index number of the LED on the strip
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        self.strip.setPixelColor(strip_index, color)
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_row(self, row, color, show: bool = True) -> None:
        """
        Paint a row of pixels.
        :param row: Row coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        for i in range(self.cols):
            led_index = self._row_col_to_strip(row, i)
            self.strip.setPixelColor(led_index, color)
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_col(self, col, color, show: bool = True) -> None:
        """
        Paint a column of pixels.
        :param col: Col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        for i in range(self.rows):
            led_index = self._row_col_to_strip(i, col)
            self.strip.setPixelColor(led_index, color)
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_pixel_tuples(self, tuple_arr: list, row_origin: int, col_origin: int, color, show: bool = True) -> None:
        """
        Paint all pixels indicated by an array of (row, col) coordinate tuples. Pixels are placed relative to the
        origin.
        :param tuple_arr: List of (row, col) coordinate tuples
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        for pair in tuple_arr:
            row, col = pair
            led_index = self._row_col_to_strip(row_origin + row, col_origin + col)
            self.strip.setPixelColor(led_index, color)
        if show is True:  # Option to disable display updating
            self.strip.show()

    def paint_character(self, character: str, row_origin: int, col_origin: int, color, show: bool = True) -> None:
        """
        Paint a character from MATRIX_CHARS. Pixels are placed relative to the origin.
        :param character: Single character to paint. Characters are defined in MATRIX_CHARS.CHARS
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        self.paint_pixel_tuples(MATRIX_CHARS.get(character)['pixels'], row_origin, col_origin, color, show)

    def paint_string(self, string: str, row_origin: int, col_origin: int, color, col_padding: int = 1,
                     show: bool = True) -> None:
        """
        Paint a character from MATRIX_CHARS. Pixels are placed relative to the origin.
        :param string: String of characters to display
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param col_padding: The number of empty columns to leave in between each character of the string
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        col_index = col_origin
        for i in range(len(string)):
            char = string[i]
            char_size_row, char_size_col = MATRIX_CHARS.get(char)['size']
            self.paint_character(char, row_origin, col_index, color, show)
            col_index = col_index + char_size_col + col_padding

    def paint_clock(self, time_str, row_origin, col_origin, color, show: bool = True) -> None:
        """
        Paints a clock using the input time_str. Pixels are placed relative to the origin.
        :param time_str: A string of 5 characters HH:MM or 4 characters HHMM
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        if len(time_str) == 5:
            self.paint_string(time_str, row_origin, col_origin, color, col_padding=1, show=show)
        elif len(time_str) == 4:
            hh = time_str[0] + time_str[1]
            mm = time_str[2] + time_str[3]
            extended_time_str = hh + ':' + mm
            self.paint_string(extended_time_str, row_origin, col_origin, color, col_padding=1, show=show)
        else:
            raise ValueError("Expected string of exactly 4 or 5 characters, got '" + time_str + "' instead.")

    def clock_current_time_toggle(self, row_origin: int, col_origin: int, color, toggle_time: int = 1):
        """
        Paints a clock displaying the current time but toggling of and on every toggle_time seconds. Pixels are
        placed relative to the origin. This function will block until it is interrupted using Ctrl-c or
        self.interrupt().
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param toggle_time: Time between screen toggles
        """
        try:
            logger.info("Clock is ticking.")
            while True:
                if self._interrupted is True:  # Check the flag to interrupt the clock
                    raise InterruptedError

                # Toggle on
                curr_time = datetime.now()
                self.clear(show=False)
                self.paint_clock(curr_time.strftime('%H:%M'), row_origin, col_origin, color, show=False)
                self.show()
                time.sleep(toggle_time)

                if self._interrupted is True:  # Check the flag to interrupt the clock
                    raise InterruptedError
                # Toggle off
                curr_time = datetime.now()
                self.clear(show=True)
                time.sleep(toggle_time)
            # logger.info("Clock finished.")
        except KeyboardInterrupt:
            logger.warning("Clock interrupted by keypress.")
        except InterruptedError:
            logger.info("Clock interrupted by interrupt flag.")

    def clock_current_time(self, row_origin: int, col_origin: int, color) -> None:
        """
        Paints a clock displaying the current time and ticking the colon (:) each second. Pixels are placed relative to
        the origin. This function will block until it is interrupted using Ctrl-c or self.interrupt().
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        """
        try:
            logger.info("Clock is ticking.")
            while True:
                if self._interrupted is True:  # Check the flag to interrupt the clock
                    raise InterruptedError

                # Tick with colon
                curr_time = datetime.now()
                self.clear(show=False)
                self.paint_clock(curr_time.strftime('%H:%M'), row_origin, col_origin, color, show=False)
                self.show()
                time.sleep(1)

                if self._interrupted is True:  # Check the flag to interrupt the clock
                    raise InterruptedError
                # Tick without colon
                curr_time = datetime.now()
                self.clear(show=False)
                self.paint_clock(curr_time.strftime('%H %M'), row_origin, col_origin, color, show=False)
                self.show()
                time.sleep(1)
            # logger.info("Clock finished.")
        except KeyboardInterrupt:
            logger.warning("Clock interrupted by keypress.")
        except InterruptedError:
            logger.info("Clock interrupted by interrupt flag.")

    def shift(self, d_row: int = 0, d_col: int = -1, loop: bool = False) -> None:
        """
        Shifts the display in the directions provided.
        :param d_row: Direction of the row
        :param d_col: Direction of the column
        :param loop: If True, any LEDs which are shifted beyond the matrix bounds will reappear at the other side again.
        If False, any LEDs which are shifted beyond the matrix bounds will disappear.
        """
        old_colors = []  # Store old state of the matrix
        for i in range(self.strip.numPixels()):
            old_colors.append(self.strip.getPixelColor(i))

        # Create the new matrix state
        for i in range(self.strip.numPixels()):  # Loop all pixels
            row, col = self._strip_to_row_col(i)

            if loop is False:  # Values which go beyond matrix bounds are removed
                row_target = clamp(row + d_row, 0, self.rows - 1)
                col_target = clamp(col + d_col, 0, self.cols - 1)
                # Check whether or not the source LEDs are beyond the matrix bounds (if so, display nothing)
                if not within_bounds(row - d_row, 0, self.rows - 1) or not within_bounds(col - d_col, 0, self.cols - 1):
                    self.strip.setPixelColor(i, Color(0, 0, 0))

            else:  # loop is True:  # Values which go beyond matrix bounds appear at the other side again
                row_target = transfer(row + d_row, 0, self.rows - 1)
                col_target = transfer(col + d_col, 0, self.cols - 1)

            # Set the target LEDs
            i_target = self._row_col_to_strip(row_target, col_target)
            self.strip.setPixelColor(i_target, old_colors[i])
        # Update the view
        self.strip.show()

    def shift_stream(self, d_row: int = 0, d_col: int = -1, loop: bool = True, shift_times: int = 0,
                     wait_ms: int = DEFAULT_UPDATE_TIME) -> None:
        """
        Shift the matrix multiple times. The behaviour of this function depends on the loop and shift_times parameters:

        If loop is True and shift_times <= 0: Will shift continuously until interrupted, any LEDs beyond the matrix
        bounds will reappear at the other side.

        If loop is True and shift_times > 0: Will shift shift_times number of times, any LEDs beyond the matrix bounds
        will reappear at the other side.

        If loop is False and shift_times <= 0: Will shift until all pixels are shifted off the screen. LEDs will not
        loop.

        Else (loop is False and loop_times > 0): Will shift shift_times number of times. LEDs will not loop.

        :param d_row: Direction of the row
        :param d_col: Direction of the column
        :param loop: If True, any LEDs which are shifted beyond the matrix bounds will reappear at the other side again.
        If False, any LEDs which are shifted beyond the matrix bounds will disappear.
        :param shift_times: When 1 or higher, the matrix will shift this number of times. When 0 or lower, LEDs will
        shift continuously based on the loop parameter.
        :param wait_ms: The time to wait in between each shift.
        """
        try:
            logger.info("Shift is started. Press Ctrl-c to stop.")
            if loop is True and shift_times <= 0:  # loop until the program is interrupted
                logger.info("Shifting forever with loop.")
                while True:
                    if self._interrupted is True:  # Check the flag to interrupt the clock
                        raise InterruptedError
                    self.shift(d_row=d_row, d_col=d_col, loop=loop)
                    time.sleep(wait_ms / 1000.0)
            elif loop is True and shift_times > 0:
                logger.info("Shifting " + str(shift_times) + " times with loop.")
                for i in range(shift_times):
                    self.shift(d_row=d_row, d_col=d_col, loop=loop)
                    time.sleep(wait_ms / 1000.0)
            elif loop is False and shift_times <= 0:
                logger.info("Shifting without loop until screen is empty.")
                for i in range(max(self.cols, self.rows)):  # Shift until all LEDs are shifted off the screen
                    self.shift(d_row=d_row, d_col=d_col, loop=loop)
                    time.sleep(wait_ms / 1000.0)
            else:  # loop is False and loop_times > 0:
                logger.info("Shifting " + str(shift_times) + " times with loop.")
                for i in range(shift_times):
                    self.shift(d_row=d_row, d_col=d_col, loop=loop)
                    time.sleep(wait_ms / 1000.0)
            logger.info("Shift finished.")
        except KeyboardInterrupt:
            logger.warning("Shift interrupted by user.")

    def paint_snake(self, color, wait_ms=DEFAULT_UPDATE_TIME) -> None:
        """
        Snake color across display a pixel at a time.
        :param color: Color to display
        :param wait_ms: The time to wait in between each pixel paint.
        """
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, color)
            self.strip.show()
            time.sleep(wait_ms / 1000.0)

    def _row_col_to_strip(self, row: int, col: int) -> int:
        """
        Transforms row col coordinates to the index of the LED on the matrix. If one of the coordinates is out of bounds a ValueError is raised.

        :param row: Row coordinate (0 indexed)
        :param col: Col coordinate (0 indexed)
        :return: Strip index
        """
        if row < 0 or row >= self.rows or col < 0 or col >= self.cols:
            raise ValueError("Out of matrix bounds.")

        if col % 2 == 0:
            # Even columns are numbered from the top down
            led_index = (col * self.rows) + row
        else:
            # Odd columns are numbered from the bottom up
            led_index = (col + 1) * self.rows - row - 1
        return led_index

    def _strip_to_row_col(self, led_index: int) -> tuple:
        """
        Transforms the index of the LED to a tuple of (row, col) coordinates on the matrix. If the strip index is out of
        bounds a ValueError is raised.

        :param led_index: Pixel number as indicated by the strip index
        :return: A tuple of (row, col) matrix coordinates
        """
        if led_index < 0 or led_index >= self.rows * self.cols:
            raise ValueError("Out of strip bounds.")

        col = led_index // self.rows  # Determine the column used
        if col % 2 == 0:  # Even columns are numbered from the top down
            row = led_index - (col * self.rows)
        else:  # Odd columns are numbered from the bottom up
            row = ((col + 1) * self.rows) - led_index - 1
        return row, col


class LedMatrixThread(LedMatrix, Thread):

    def __init__(self, strip: PixelStrip, rows: int, cols: int, method_queue: Queue, signal_event: Event):
        """
        Initialize a LedMatrix as a thread.
        :param strip: rpi_ws281x.PixelStrip instance
        :param rows: Total rows of this matrix
        :param cols: Total columns of this matrix
        :param method_queue: queue.Queue instance for passing methods to run to this thread
        :param signal_event: threading.Event instance for passing signals from this thread
        """
        super().__init__(strip=strip, rows=rows, cols=cols)
        Thread.__init__(self)
        self.method_queue = method_queue
        self.signal_event = signal_event

    def run(self):
        self.begin()
        while True:
            self.signal_event.set()  # Signal the controller thread that the display is ready to receive a new method
            method_tuple = self.method_queue.get()  # Get the method passed from the controller thread
            self.uninterrupt()  # Set the interrupted flag to False
            if method_tuple is None:  # If None is passed, the thread is stopped
                self.signal_event.set()  # Signal the controller thread that the display is not working anymore
                logger.debug("Display stopped")
                return
            try:
                method, args = method_tuple
                method(*args)  # Run the method until done or interrupted
            except AttributeError as e:  # The attribute does not exist
                self.signal_event.set()  # Signal the controller thread that the display is not working anymore
                raise e  # Raise the error again


class DisplayController:

    def __init__(self, pin: int = LED_PIN):
        super().__init__()
        self.queue = Queue(maxsize=1)
        self.event = Event()
        strip = PixelStrip(LED_COUNT, pin, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
        matrix_thread = LedMatrixThread(strip, MATRIX_ROWS, MATRIX_COLS, self.queue, self.event)
        self.matrix_thread = matrix_thread

    def start(self):
        logger.debug("Display started")
        self.matrix_thread.start()

    def clear(self, show: bool = True):
        args = [show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.clear, args))  # Forward the method and args to matrix thread
        if show is True:
            logger.debug("Display cleared")

    def stop(self):
        self.matrix_thread.interrupt()
        self.event.wait()
        self.queue.put(None)

    def paint_pixel_row_col(self, row: int, col: int, color, show: bool = True) -> None:
        """
        Paint a pixel.
        :param row: Row coordinate
        :param col: Col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [row, col, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_pixel_row_col, args))  # Forward the method and args to matrix thread

    def paint_pixel_strip_index(self, strip_index: int, color, show: bool = True) -> None:
        """
        Paint a pixel.
        :param strip_index: Index number of the LED on the strip
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [strip_index, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put(
            (self.matrix_thread.paint_pixel_strip_index, args))  # Forward the method and args to matrix thread

    def paint_row(self, row, color, show: bool = True) -> None:
        """
        Paint a row of pixels.
        :param row: Row coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [row, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_row, args))  # Forward the method and args to matrix thread

    def paint_col(self, col, color, show: bool = True) -> None:
        """
        Paint a column of pixels.
        :param col: Col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [col, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_col, args))  # Forward the method and args to matrix thread

    def paint_pixel_tuples(self, tuple_arr: list, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255),
                           show: bool = True) -> None:
        """
        Paint all pixels indicated by an array of (row, col) coordinate tuples. Pixels are placed relative to the
        origin.
        :param tuple_arr: List of (row, col) coordinate tuples
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [tuple_arr, row_origin, col_origin, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_pixel_tuples, args))  # Forward the method and args to matrix thread

    def paint_character(self, character: str, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255),
                        show: bool = True) -> None:
        """
        Paint a character from MATRIX_CHARS. Pixels are placed relative to the origin.
        :param character: Single character to paint. Characters are defined in MATRIX_CHARS.CHARS
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [character, row_origin, col_origin, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_character, args))  # Forward the method and args to matrix thread

    def paint_string(self, string: str, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255),
                     col_padding: int = 1,
                     show: bool = True) -> None:
        """
        Paint a character from MATRIX_CHARS. Pixels are placed relative to the origin.
        :param string: String of characters to display
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param col_padding: The number of empty columns to leave in between each character of the string
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [string, row_origin, col_origin, color, col_padding, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_string, args))  # Forward the method and args to matrix thread

    def paint_clock(self, time_str, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255),
                    show: bool = True) -> None:
        """
        Paints a clock using the input time_str. Pixels are placed relative to the origin.
        :param time_str: A string of 5 characters HH:MM or 4 characters HHMM
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param show: If True, also update the strip. If False, the LED data is buffered instead
        """
        args = [time_str, row_origin, col_origin, color, show]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_clock, args))  # Forward the method and args to matrix thread

    def clock_current_time_toggle(self, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255),
                                  toggle_time: int = 1):
        """
        Paints a clock displaying the current time but toggling of and on every toggle_time seconds. Pixels are
        placed relative to the origin. This function will block until it is interrupted using Ctrl-c or
        self.interrupt().
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        :param toggle_time: Time between screen toggles
        """
        args = [row_origin, col_origin, color, toggle_time]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put(
            (self.matrix_thread.clock_current_time_toggle, args))  # Forward the method and args to matrix thread

    def clock_current_time(self, row_origin: int = 1, col_origin: int = 1, color=Color(255, 255, 255)) -> None:
        """
        Paints a clock displaying the current time and ticking the colon (:) each second. Pixels are placed relative to
        the origin. This function will block until it is interrupted using Ctrl-c or self.interrupt().
        :param row_origin: The origin row coordinate
        :param col_origin: The origin col coordinate
        :param color: Color to display
        """
        args = [row_origin, col_origin, color]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.clock_current_time, args))  # Forward the method and args to matrix thread

    def shift(self, d_row: int = 0, d_col: int = -1, loop: bool = False) -> None:
        """
        Shifts the display in the directions provided.
        :param d_row: Direction of the row
        :param d_col: Direction of the column
        :param loop: If True, any LEDs which are shifted beyond the matrix bounds will reappear at the other side again.
        If False, any LEDs which are shifted beyond the matrix bounds will disappear.
        """
        args = [d_row, d_col, loop]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.shift, args))  # Forward the method and args to matrix thread

    def shift_stream(self, d_row: int = 0, d_col: int = -1, loop: bool = True, shift_times: int = 0,
                     wait_ms: int = DEFAULT_UPDATE_TIME) -> None:
        """
        Shift the matrix multiple times. The behaviour of this function depends on the loop and shift_times parameters:

        If loop is True and shift_times <= 0: Will shift continuously until interrupted, any LEDs beyond the matrix
        bounds will reappear at the other side.

        If loop is True and shift_times > 0: Will shift shift_times number of times, any LEDs beyond the matrix bounds
        will reappear at the other side.

        If loop is False and shift_times <= 0: Will shift until all pixels are shifted off the screen. LEDs will not
        loop.

        Else (loop is False and loop_times > 0): Will shift shift_times number of times. LEDs will not loop.

        :param d_row: Direction of the row
        :param d_col: Direction of the column
        :param loop: If True, any LEDs which are shifted beyond the matrix bounds will reappear at the other side again.
        If False, any LEDs which are shifted beyond the matrix bounds will disappear.
        :param shift_times: When 1 or higher, the matrix will shift this number of times. When 0 or lower, LEDs will
        shift continuously based on the loop parameter.
        :param wait_ms: The time to wait in between each shift.
        """
        args = [d_row, d_col, loop, shift_times, wait_ms]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.shift_stream, args))  # Forward the method and args to matrix thread

    def paint_snake(self, color, wait_ms=DEFAULT_UPDATE_TIME) -> None:
        """
        Snake color across display a pixel at a time.
        :param color: Color to display
        :param wait_ms: The time to wait in between each pixel paint.
        """
        args = [color, wait_ms]  # Store args for matrix thread
        self.matrix_thread.interrupt()  # Interrupt the matrix thread so it can receive a new method
        self.event.wait()  # Wait until the matrix thread is ready for a new method
        self.queue.put((self.matrix_thread.paint_snake, args))  # Forward the method and args to matrix thread


if __name__ == '__main__':
    controller = DisplayController()
    # logging.basicConfig(format="%(threadName)s:%(message)s", level=logging.DEBUG)

    try:
        logging.debug("Test")
        controller.start()
        controller.clock_current_time_toggle(color=Color(255, 255, 0), toggle_time_ms=1)
        # controller.clock_current_time(1, 1, Color(255, 255, 255))  # Print the current time
        # # time.sleep(5.7)
        # # controller.clear()  # Clear the display
        # # controller.paint_string('325.1 2', 1, 1, Color(0, 0, 255))  # Print a string
        # time.sleep(3)
        # controller.clear()  # Clear the display
        # controller.paint_clock('1823', 1, 1, Color(255, 0, 0))  # Display a clock
        # time.sleep(4)
        # controller.clear()  # Clear the display
        # controller.paint_clock('03:45', 1, 1, Color(255, 255, 0))  # Display a different clock
        # time.sleep(6)

    finally:
        pass
        # controller.clear()  # Empty display
        controller.stop()  # Stop the matrix display
        controller.matrix_thread.join()  # Wait for the matrix thread to join
