# import RPi.GPIO as GPIO
import time
# GPIO.setmode(GPIO.BOARD)

import wiringpi

# define the pin that goes to the circuit
pin_for_power = 5  # this one will always be on
pin_for_control = 17


def music():
    wiringpi.wiringPiSetupGpio()
    wiringpi.pinMode(pin_for_power, 1)  
    wiringpi.pinMode(pin_for_control, 1)# use the GPIO 17
    wiringpi.digitalWrite(pin_for_control, 1)
    time.sleep(0.5)
    wiringpi.digitalWrite(pin_for_control, 0)
    # time.sleep(1)
    wiringpi.pinMode(pin_for_control, 0)

    return 0
