import datetime
import os
import time
import random
import webbrowser

#Time = time.strftime('%H%M')
#print(Time)

def currency_time():
    print("Current time: ")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def check_time_format(my_hour, my_minute):
    if my_hour > "0" and my_hour < "24" and my_minute > "0" and my_minute < "60":
        return True
    return False


def set_multi_alarm():
    if not os.path.isfile("set_alarm_time.txt"):
        with open("set_alarm_time.txt", "w") as alarm_file:
            number_of_alarm = int(input("How many alarms do you want to add? "))
            for i in range(number_of_alarm):
                my_hour = input("please：input hour:")
                my_minute = input("please：input minute:")
                if check_time_format:
                    set_time = my_hour + my_minute
                    set_time += "\n"
                    alarm_file.write(set_time)


def alarm():
    with open("set_alarm_time.txt") as f:
        alarms = f.readlines()
        for one_alarm in alarms:
            one_alarm = one_alarm.rstrip('\n')
            #print(one_alarm)
           # while Time != one_alarm:
           #     #print('The time is: ' + Time + '\n')
           #     time.sleep(1)
           #     continue
            while True:
                Time = time.strftime('%H%M')
                if Time == one_alarm:
                    print("wake up!")
                    with open(r"alarm_videos.txt", "r") as f:
                        videos = f.readline()
                        webbrowser.open(videos)
                    break


currency_time()
set_multi_alarm()
alarm()