import datetime
import os
import time
import random
import webbrowser
import os


def active(my_hour,my_minute):
    with open("set_alarm_time.txt", "a+") as fin, open("temp.txt", "a+") as fout:
        fin.seek(0)  # "a+" means point start from the end
        for line in fin:
            if line == my_hour + my_minute + "E" + "\n":
                fout.write(my_hour + my_minute + "\n")
                #  fin.seek(0)
                for original_line in fin:
                    fout.write(original_line)
                fin.seek(0)
                fin.truncate()
                fout.seek(0)
                fin.write(fout.read())
                fout.close()
                os.remove("temp.txt")
                break
            elif line == my_hour + my_minute + "\n":
                fout.write(my_hour + my_minute + "E" + "\n")
                #   fin.seek(0)
                for original_line in fin:
                    fout.write(original_line)
                fin.seek(0)
                fin.truncate()
                fout.seek(0)
                fin.write(fout.read())
                fout.close()
                os.remove("temp.txt")
                break
            else:
                fout.write(line)