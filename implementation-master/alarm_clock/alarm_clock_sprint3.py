'''
import time
import webbrowser
from time import gmtime, strftime
from datetime import datetime
import

#from alarm_clock import flash.flash


# pin_to_circuit=17
def currency_time():
    print("Current time: ")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def alarm(my_hour, my_minute):
    try:
        if my_hour > "0" and my_hour < "24" and my_minute > "0" and my_minute < "60":
            flash.rc_time()
            while True:
                t = time.localtime()
                fmt = "%H %M"
                now = time.strftime(fmt, t)
                now = now.split(' ')
                hour = now[0]
                minute = now[1]
                if hour == my_hour and minute == my_minute:
                    print("Wake Up!")

                    for i in range(4):
                        flash.rc_time()
                    with open("alarm_videos.txt", "r") as f:
                        videos = f.readline()
                        webbrowser.open(videos)
                        break
        else:
            raise ValueError
    except ValueError:
        print("ERROR: Enter time in HH:MM or HH:MM:SS format")


my_hour = input("please：input hour:")
my_minute = input("please：input minute:")

currency_time()
alarm(my_hour, my_minute)
'''