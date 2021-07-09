# import RPi.GPIO as GPIO
import time
# GPIO.setmode(GPIO.BOARD)

import wiringpi


# define the pin that goes to the circuit
# pin_to_circuit = 17


def rc_time():
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(26, 1)  # use the GPIO 26
    wiringpi.digitalWrite(26, 1)
    time.sleep(1)
    wiringpi.digitalWrite(26, 0)
    time.sleep(1)
    wiringpi.pinMode(26, 0)
    return 0


