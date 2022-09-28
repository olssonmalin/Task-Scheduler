#!/usr/bin/python3


from .exceptions import NoTime


class Timeline:
    """Timeline class"""

    def __init__(self, availability) -> None:
        self.timeline = []
        self.availability = availability
        pass

    def add_days(self, task):
        if self.timeline is []:
            # add days between start and deadline
            pass
        # if first day after start of task
            # add days between
        # if last day before task deadline
            # add days between

    def add_task(self, task):
        # Check if completed tasks should be inculded in timeline?
        self.add_days(task)
        hours = task.estimated_duration
        for day in self.timeline:
            # if day.date >= task.start
            try:
                day.add_task(task)
            except NoTime:
                continue

    def get_timeLine(self):
        return self.timeline
