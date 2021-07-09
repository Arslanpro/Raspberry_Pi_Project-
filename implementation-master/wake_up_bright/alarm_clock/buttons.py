import RPi.GPIO as GPIO


class TactileButton:

    def __init__(self, pin_nr: int, callback, bounce_ms: int = 200) -> None:
        GPIO.setmode(GPIO.BCM)
        self.pin = pin_nr
        self.callback = callback
        self.bouncetime = bounce_ms

        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self._pressed, bouncetime=self.bouncetime)

    def _pressed(self, channel):
        self.callback()

    def set_callback(self, callback):
        self.callback = callback


class RotaryEncoder:
    D_LEFT = 1  # Counter clockwise (when encoder is in front of wheel)
    D_RIGHT = -1  # Clockwise (when encoder is in front of wheel)

    def __init__(self, left_pin_nr: int, right_pin_nr: int, callback, samples: int = 3, bounce_ms=10) -> None:
        GPIO.setmode(GPIO.BCM)
        self.left_pin = left_pin_nr
        self.right_pin = right_pin_nr
        self.left_state = 0
        self.right_state = 0
        self.sampled_direction = 0
        self.samples = samples
        self.callback = callback
        self.bouncetime = bounce_ms

        GPIO.setup(self.left_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.left_pin, GPIO.BOTH, callback=self._pulse, bouncetime=self.bouncetime)
        GPIO.setup(self.right_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.add_event_detect(self.right_pin, GPIO.BOTH, callback=self._pulse, bouncetime=self.bouncetime)

        # Read the initial state
        self.left_state = GPIO.input(self.left_pin)
        self.right_state = GPIO.input(self.right_pin)

    def set_callback(self, callback):
        self.callback = callback

    def _pulse(self, channel):
        next_left_state = GPIO.input(self.left_pin)
        next_right_state = GPIO.input(self.right_pin)
        direction = self.next_state_to_direction(next_left_state, next_right_state)

        self.sampled_direction = self.sampled_direction + direction

        if self.sampled_direction <= (self.D_LEFT * self.samples):  # Enough changes in the D_NEG direction were detected
            # print("Turned left  (channel %d)" % channel)
            self.callback(direction)
            self.sampled_direction = 0  # Reset the sampled direction
        elif self.sampled_direction >= (self.D_RIGHT * self.samples):
            # print("Turned right (channel %d)" % channel)
            self.callback(direction)
            self.sampled_direction = 0  # Reset the sampled direction

        self.left_state = next_left_state
        self.right_state = next_right_state

    def next_state_to_direction(self, next_left_state: int, next_right_state: int) -> int:
        direction = 0
        if self.left_state == 0 and self.right_state == 0:
            if next_left_state == 1 and next_right_state == 1:
                direction = self.D_LEFT
            elif next_left_state == 1 and next_right_state == 0:
                direction = self.D_RIGHT
            else:
                pass
                # print("Not recognised, was 00, next %d%d" % (next_left_state, next_right_state))
        elif self.left_state == 1 and self.right_state == 1:
            if next_left_state == 1 and next_right_state == 0:
                direction = self.D_LEFT
            elif next_left_state == 0 and next_right_state == 0:
                direction = self.D_RIGHT
            else:
                pass
                # print("Not recognised, was 11, next %d%d" % (next_left_state, next_right_state))
        elif self.left_state == 0 and self.right_state == 1:
            if next_left_state == 0 and next_right_state == 0:
                direction = self.D_LEFT
            elif next_left_state == 1 and next_right_state == 1:
                direction = self.D_RIGHT
            else:
                pass
                # print("Not recognised, was 01, next %d%d" % (next_left_state, next_right_state))
        else:
            pass
            # print("Illegal state")

        return direction


def button_pressed(channel):
    print("Button pressed on channel %d" % channel)


def rotation_callback(dir):
    arrow = "<--" if dir < 0 else "-->"
    print("%s" % arrow)


if __name__ == '__main__':
    # button1 = TactileButton(26, button_pressed)
    # button1.start()
    # button2 = TactileButton(20, button_pressed)
    # button2.start()
    # button3 = TactileButton(19, button_pressed)
    # button3.start()
    # button4 = TactileButton(16, button_pressed)
    # button4.start()
    #
    # rotary_button = RotaryEncoder(5, 6, rotation_callback, samples=2)
    # rotary_button.start()

    message = input("Press enter to quit\n\n")
