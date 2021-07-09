import datetime
import os
import time
import random
import webbrowser
import os
from wake_up_bright.alarm_clock.app.crud.controllers import AlarmDao, CollectionDao, PersonDao
from wake_up_bright.alarm_clock.app.crud.models import db, Person, Alarm
from wake_up_bright.alarm_clock.app import create_app

app = create_app()
db.app = app
db.init_app(app)
alarmservice = AlarmDao()


# update the function about if the alarm time is same but range time is different, will use the shorter range time
def active(my_hour, my_minute, my_hour_max, my_minute_max):
    with open("set_alarm_time.txt", "a+") as fin, open("temp.txt", "a+") as fout:
        fin.seek(0)  # "a+" means point start from the end
        for line in fin:
            str = line.split(" ")
            str[1] = str[1].rstrip("\n").rstrip("E")
            print(str[1])
            print(line)
            if str[0] == my_hour + my_minute and line.find("E") != -1:  # old one is an active alarm
                if int(my_hour_max + my_minute_max) < int(str[1]):  # if the new range is shorter
                    print("case1")
                    alarmservice.use_alarm_time_and_change_at1(my_hour + ":" + my_minute,
                                                               my_hour_max + ":" + my_minute_max)
                    fout.write(
                        my_hour + my_minute + " " + my_hour_max + my_minute_max + "E" + "\n")  # i keep the E cuz changing range also belongs to changing alarm
                    #  fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")
                    # alarmservice.use_alarm_time_and_change_at1(my_hour + ":" + my_minute,
                    #                                           my_hour_max + ":" + my_minute_max)
                elif int(my_hour_max + my_minute_max) > int(
                        str[1]):  # old one is shorter, dont change status dont change range
                    print("case2")
                    fout.write(my_hour + my_minute + " " + str[1] + "E" + "\n")
                    #  fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")
                elif int(my_hour_max + my_minute_max) == int(str[1]):
                    print("case3")
                    alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                    fout.write(my_hour + my_minute + " " + str[1] + "\n")
                    #  fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")
                    # update database
                    print(my_hour + ":" + my_minute)
                    # alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                    break
                break
            elif str[0] == my_hour + my_minute and (line.find("E") == -1):  # old one is disabled
                if int(my_hour_max + my_minute_max) < int(str[1]):  # if the new range is shorter
                    print("case4")
                    alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                    alarmservice.use_alarm_time_and_change_at1(my_hour + ":" + my_minute,
                                                               my_hour_max + ":" + my_minute_max)
                    fout.write(my_hour + my_minute + " " + my_hour_max + my_minute_max + "E" + "\n")
                    #   fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")
                    # update database
                # alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                # alarmservice.use_alarm_time_and_change_at1(my_hour + ":" + my_minute,
                #                                            my_hour_max + ":" + my_minute_max)
                elif int(my_hour_max + my_minute_max) > int(str[1]):  # old one is shorter
                    print("case5")
                    fout.write(my_hour + my_minute + " " + str[1] + "E" + "\n")
                    #  fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")

                    # update database
                    alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                elif my_hour_max + my_minute_max == str[1]:
                    print("case6")
                    # print(int(my_hour_max + my_minute_max))
                    alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                    fout.write(my_hour + my_minute + " " + str[1] + "E" + "\n")
                    #  fin.seek(0)
                    for original_line in fin:
                        fout.write(original_line)
                    fin.seek(0)
                    fin.truncate()
                    fout.seek(0)
                    fin.write(fout.read())
                    fout.close()
                    os.remove("temp.txt")
                    # alarmservice.use_alarm_time_and_change_on_off(my_hour + ":" + my_minute)
                    break
                break
            else:
                fout.write(line)
