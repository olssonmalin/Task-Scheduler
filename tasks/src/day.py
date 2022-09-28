#!/usr/bin/python3
from .exceptions import NoTime


class Day:
    """Day class"""

    def __init__(self, date, hours) -> None:
        self.date = date
        self.hours = hours
        self.tasks = []
        pass

    def add_task(self, task):
        if self.hours is 0:
            raise NoTime
        pass

    def get_tasks(self):
        return self.tasks
