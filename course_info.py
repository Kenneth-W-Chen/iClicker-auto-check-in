import copy
import datetime
import math
from typing import Union


class hour_minute:
    def __init__(self, hour: int, minute: int):
        self.hour = hour
        self.minute = minute

    @classmethod
    def from_str(cls, s: str):
        arr = s.split(':')
        return hour_minute(int(arr[0]),int(arr[1]))

    @classmethod
    def now(cls):
        n = datetime.datetime.now()
        return hour_minute(n.hour, n.minute)

    @classmethod
    def utcnow(cls):
        n = datetime.datetime.utcnow()
        return hour_minute(n.hour, n.minute)

    def toSeconds(self):
        return (60 * self.hour + self.minute) * 60

    def __str__(self):
        return f'{self.hour}:{self.minute}'

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.hour == other.hour and self.minute == other.hour
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            if self.hour > other.hour:
                return True
            elif self.hour < other.hour:
                return False
            else:
                return self.minute > other.minute
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            if self.hour > other.hour:
                return True
            elif self.hour < other.hour:
                return False
            else:
                return self.minute >= other.minute
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            if self.hour < other.hour:
                return True
            elif self.hour > other.hour:
                return False
            else:
                return self.minute < other.minute
        else:
            return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            if self.hour < other.hour:
                return True
            elif self.hour > other.hour:
                return False
            else:
                return self.minute <= other.minute
        else:
            return False


class course_info:
    def __init__(self, start_time: hour_minute, end_time: hour_minute, course: str):
        self.start_time: hour_minute = copy.deepcopy(start_time)
        self.end_time: hour_minute = copy.deepcopy(end_time)
        self.course: str = copy.deepcopy(course)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.start_time == other.start_time
        elif isinstance(other, self.start_time.__class__):
            return self.start_time == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.start_time > other.start_time
        elif isinstance(other, self.start_time.__class__):
            return self.start_time > other
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.start_time >= other.start_time
        elif isinstance(other, self.start_time.__class__):
            return self.start_time >= other
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.start_time < other.start_time
        elif isinstance(other, self.start_time.__class__):
            return self.start_time < other
        else:
            return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.start_time <= other.start_time
        elif isinstance(other, self.start_time.__class__):
            return self.start_time <= other
        else:
            return False

