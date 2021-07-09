import time


class Alarm(object):

    @property
    def current_time(self):
        return self.current_time

    @current_time.setter
    def current_time(self, value):
        self.current_time = time.strftime("%H:%M:%S", time.localtime())

    @property
    def alarm_time(self):
        return self.alarm_time

    @alarm_time.setter
    def alarm_time(self, value):
        self.alarm_time = value

    @property
    def time_range(self):
        return self.time_range

    @time_range.setter
    def time_range(self, value):
        self.time_range = value

    @property
    def snooze_time(self):
        return self.snooze_time

    @snooze_time.setter
    def snooze_time(self, value):
        self.snooze_time = value

    @property
    def current_date(self):
        return self.current_date

    @current_date.setter
    def current_date(self, value):
        self.current_date = time.strftime("%Y-%m-%d", time.localtime())

    @property
    def aid(self):
        return self.aid

    @aid.setter
    def aid(self, value):
        self.aid = value

    @property
    def auid(self):
        return self.auid

    @auid.setter
    def auid(self, value):
        self.auid = value

    def __init__(self, current_time, alarm_time, time_range, snooze_time, current_date, aid, auid):
        self.aid = aid
        self.current_date = current_date
        self.snooze_time = snooze_time
        self.time_range = time_range
        self.alarm_time = alarm_time
        self.current_time = current_time
        self.auid = auid
