import datetime
import os
import time
import random
import webbrowser
from alarm_function.active import active
#from alarm_function.music import music
import datetime

from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao, CollectionDao, PersonDao
from wake_up_bright.alarm_clock.app.crud.models import db, Person, Alarm
from wake_up_bright.alarm_clock.app import create_app

# from music import music
from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao

app = create_app()
db.app = app
db.init_app(app)


def currency_time():  # this function for trturn the real time
    print("Current time: ")
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def check_time_format(my_hour, my_minute):  # check whether the input is correct format
    if "0" < my_hour < "24" and "0" < my_minute < "60":
        return True
    return False


def set_multi_alarm():  # set a new alarm
    show_alarm_database()  # show the time which were set before
    number_of_alarm = int(input("How many alarms do you want to add? "))  # get new alarm
    for i in range(number_of_alarm):  # i means the number of alarms you want to set
        while True:  # first loop for recording the alarm
            my_hour = input("please：input hour:")
            my_minute = input("please：input minute:")
            if not check_time_format(my_hour, my_minute):  # call check function to see whether has correct format
                print("wrong format, please input again")
            else:
                break
        while True:  # second loop for recording the alarm+range
            my_hour_max = input("please input latest hour:")
            my_minute_max = input("please input latest minute")
            if not check_time_format(my_hour_max, my_minute_max):
                print("wrong format, please input again")
            else:
                break
        print("alarm has been set!")
        with open("set_alarm_time.txt", "a+") as add_new_alarm:  # add new alarm in file
            add_new_alarm.seek(0)  # make sure read the file from first line
            count = 0  # this count is used to check whether input the same alarm which already in file
            for line in add_new_alarm:
                # line = line.rstrip('\n').rstrip('E')  # E means active, without E means this alarm is turn off
                line = line.rstrip('\n').rstrip('E')
                str = line.split(" ", 1)  # only check the start alarm, wont check range, cuz the system will choose the smallest range time
                check = my_hour + my_minute
                if str[0] == check:  # if input the same alarm
                    count += 1
            if count > 0:  # the input alarm already been file
                active(my_hour, my_minute, my_hour_max,
                       my_minute_max)  # call active function for changing the status(remove E or add E)
            elif count == 0:  # the input is a new alarm
                set_time = my_hour + my_minute
                set_time += " "  # if input a new alarm, we left it active by default.
                set_time += my_hour_max + my_minute_max
                set_time += "E"
                set_time += "\n"
                add_new_alarm.write(set_time)  # write the new alarm in file, format like"1120 1200E"

                ct = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                alarmservice = AlarmDao()
                at = datetime.time(int(my_hour), int(my_minute))
                at1 = datetime.time(int(my_hour_max), int(my_minute_max))
                on_off = check_alarm_status(my_hour, my_minute, my_hour_max, my_minute_max)  # 0 means off, 1 means on
                alarmservice.create_Alarm(ct, at, at1, 5, ct, 2, on_off)
    alarm()  # call alarm function


def check_alarm_status(my_hour, my_minute, my_hour_max, my_minute_max):
    with open("set_alarm_time.txt") as check:
        check.seek(0)
        while True:
            alarms = check.readlines()  # Take out all the saved alarm clocks.
            for one_alarm in alarms:
                str = one_alarm.split(" ", 1)  # we only check the starting time
                if str[0] == my_hour + my_minute and str[1] == my_hour_max + my_minute_max + '\n':  # without E
                    print(one_alarm)
                    return 0
                elif str[0] == my_hour + my_minute and str[1] == my_hour_max + my_minute_max + "E" + '\n': # with E
                    return 1
                else:
                    continue


def show_alarm_database():  # show the alarm which are in file, I tried lots of way but cant decode the file :( so just show the original file
    with open("set_alarm_time.txt") as show:
        print(show.read())


def alarm():  # this function is looping through alarm file to see if there is an alarm matching the real time
    with open("set_alarm_time.txt") as f:
        while True:
            alarms = f.readlines()  # Take out all the saved alarm clocks.
            for one_alarm in alarms:
                str = one_alarm.split(" ", 1)
                str[1] = str[1].rstrip('\n')
                str1_without_state = str[1].rstrip("E")
                Time = time.strftime('%H%M')
                if Time == str[0] and one_alarm.find("E"):  # alarm = time and the its status is active
                    while True:
                        Time_for_check_range = time.strftime('%H%M')
                        if Time_for_check_range == str1_without_state:
                            print("wake up!")
                            # music()  # run in raspberry pi using music() to make sound
                            break # jump out of while, then to else, to next alarm
                        else:
                            print("waiting for the signal")
                            time.sleep(1)
                            #
                            # need one light sleep signal
                            #

                    # music()  # run in raspberry pi using music() to make sound
                else:
                    continue  # read next alarm


if __name__ == '__main__':
    currency_time()
    set_multi_alarm()
