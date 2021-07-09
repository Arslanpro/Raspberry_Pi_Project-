import datetime
import os
import time
import random
import webbrowser
import os
from .active import active


# Time = time.strftime('%H%M')
# print(Time)

def currency_time():
    print("Current time: ")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def check_time_format(my_hour, my_minute):
    if "0" < my_hour < "24" and "0" < my_minute < "60":
        return True
    return False


def set_multi_alarm():
    show_alarm_database()
    """""
    #with open("set_alarm_time.txt", "a+") as set_alarm_file:  # a+ means file readable and writeable and can appendix
    with open("set_alarm_time.txt", "a+") as set_alarm_file:
        lines = []
        for line in set_alarm_file.readlines():
            if line != '\n':
                lines.append(line)
                set_alarm_file.close()
    """""
    number_of_alarm = int(input("How many alarms do you want to add? "))
    for i in range(number_of_alarm):
        my_hour = input("please：input hour:")
        my_minute = input("please：input minute:")
        if check_time_format(my_hour, my_minute):
            with open("set_alarm_time.txt", "a+") as add_new_alarm:
                add_new_alarm.seek(0)
                count = 0
                for line in add_new_alarm:
                    line = line.rstrip('\n').rstrip('E')
                    # line2 = line1.rstrip('E')
                    check = my_hour + my_minute
                    # print(check)
                    if line == check:
                        count += 1
                # print(line2)
                # print(count)
                # add_new_alarm.seek(0)
                if count > 0:
                    # print(count)
                    #  add_new_alarm.seek(0)
                    active(my_hour, my_minute)
                #  add_new_alarm.seek(0)
                elif count == 0:
                    set_time = my_hour + my_minute
                    set_time += "E"
                    set_time += "\n"
                    add_new_alarm.write(set_time)
    #    add_new_alarm.seek(0)
    alarm()


def show_alarm_database():
    with open("set_alarm_time.txt") as show:
        print(show.read())
        """"
            hour = line[0:2]  # .rstrip('\n')
            #minute = line[2:]  # .rstrip('\n')
            if len(line) == 4:
                status = line[4]
            #else:
                #status = ""
            print(hour, end='')
            #print(minute, end='')
                #print(status)
                """""


def alarm():
    with open("set_alarm_time.txt") as f:
        alarms = f.readlines()
        for one_alarm in alarms:
            one_alarm = one_alarm.rstrip('\n')
            one_alarm_without_state = one_alarm.rstrip("E")
            # print(one_alarm)
            # while Time != one_alarm:
            #     #print('The time is: ' + Time + '\n')
            #     time.sleep(1)
            #     continue
            while True:
                Time = time.strftime('%H%M')
                # print(Time)
                if Time == one_alarm_without_state and one_alarm.find("E"):
                    print("wake up!")
                    with open("alarm_videos.txt", "r") as f_music:
                        videos = f_music.readline()
                        webbrowser.open(videos)
                    break


currency_time()
set_multi_alarm()
