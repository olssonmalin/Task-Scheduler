#!/usr/bin/python3
from .exceptions import NoTime


class Day:
    """Day class"""

    def __init__(self, date, max, _next=None, _prev=None) -> None:
        self.date = date
        self.max = max
        self.next = _next
        self.prev = _prev
        self.hours = []
        self.surplus = []
        pass

    def add_task(self, task):
        if self.hours is 0:
            raise NoTime
        pass

    # def get_tasks(self):
    #     return self.tasks

    # def remove_task_hours()

    def get_avalible_hours(self):
        # is deadline date?
        # return max - len(hours)
        # return self.next.getAvalibleHours() + max - len(hours)
        pass
