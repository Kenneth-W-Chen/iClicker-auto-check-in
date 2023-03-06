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
    def __init__(self, ht: hour_minute, course: str):
        self.ht: hour_minute = copy.deepcopy(ht)
        self.course: str = copy.deepcopy(course)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.ht == other.ht
        elif isinstance(other, self.ht.__class__):
            return self.ht == other
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if isinstance(other, self.__class__):
            return self.ht > other.ht
        elif isinstance(other, self.ht.__class__):
            return self.ht > other
        else:
            return False

    def __ge__(self, other):
        if isinstance(other, self.__class__):
            return self.ht >= other.ht
        elif isinstance(other, self.ht.__class__):
            return self.ht >= other
        else:
            return False

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.ht < other.ht
        elif isinstance(other, self.ht.__class__):
            return self.ht < other
        else:
            return False

    def __le__(self, other):
        if isinstance(other, self.__class__):
            return self.ht <= other.ht
        elif isinstance(other, self.ht.__class__):
            return self.ht <= other
        else:
            return False

