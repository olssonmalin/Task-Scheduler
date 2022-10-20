"""
Models for Task Scheduler
"""

from datetime import timedelta, date
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError


class Category(models.Model):
    """
    Category model class
    """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Task(models.Model):
    """
    Task model class
    """
    not_started = "NS"
    on_going = "OG"
    completed = "C"
    STATUS = (
        (not_started, "Not started"),
        (on_going, "Ongoing"),
        (completed, "Completed")
    )

    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start = models.DateField("Start date")
    deadline = models.DateField("Deadline")
    estimated_duration = models.IntegerField(default=0)
    status = models.CharField(
        max_length=2, choices=STATUS, default=not_started)

    duration_verbose = "Actual duration" if status == "C" else "Elapsed time"
    actual_duration = models.IntegerField(duration_verbose, default=0)

    def get_date_range(self):
        """
        Creates array of date objects
        First date is start of task or current day
        if start is prior to current day.
        Last day is task deadline
        """
        start = self.start if self.start > date.today() else date.today()
        delta = self.deadline - start  # as timedelta
        days = [start + timedelta(days=i) for i in range(delta.days + 1)]
        return days

    def is_in_range(self, date_range):
        """
        Check is task is scheduled in provided date range
        """
        self_range = self.get_date_range()
        for day in date_range:
            if day in self_range:
                return True
        return False

    def get_new_deadline(self, tasks=None):
        """
        Finds new possible deadline for task
        """
        while not self.enough_time(tasks):
            self.deadline = self.deadline + timedelta(days = 1)
        return self.deadline

    def get_new_start_date(self):
        """
        Find gap where ?
        """
        self.start = self.deadline
        while not self.enough_time():
            self.start = self.start - timedelta(days = 1)
        return self.start

    def avalible_hours(self, date_range=None):
        """
        Gets avalible hours based on user availability
        during current tasks date range
        """
        if date_range is None:
            date_range = self.get_date_range()
        availability = Availability.objects.get(id=1).as_list()
        hours = 0
        for day in date_range:
            hours += availability[day.weekday()]
        return hours


    def enough_time(self, all_tasks=None):
        """
        Checks if there is enough avalible time to schedule task
        @return: bool
        """
        hours_left = self.estimated_duration - self.actual_duration
        if self.avalible_hours() - hours_left < 0:
            return False
        if all_tasks is None:
            all_tasks = __class__.objects.exclude(id=self.id).order_by('deadline')
        self_range = self.get_date_range()
        for task in all_tasks:
            if task.is_in_range(self_range) and task.status != 'C':
                task_range = task.get_date_range()
                self_range.extend(x for x in task_range if x not in self_range)
                hours_left += (task.estimated_duration - task.actual_duration)
                if (self.avalible_hours(self_range) - hours_left) < 0:
                    return False
        return True

    def clean(self) -> None:
        """
        Cleans attributes before save
        """
        # Ensure deadline is not prior to start date
        if self.deadline < self.start:
            raise ValidationError({'deadline': ('Deadline may not be prior to start date')})

        # Ensure there is enough avalible time to schedule new task
        if self.pk is None:
            if not self.enough_time():
                raise ValidationError({'deadline': \
                    (f'Not enough time to complete task before deadline, \
                        next possible deadline: {self.get_new_deadline()}.'),
                        'start': (f'Possible start date: {self.get_new_start_date()}')})
        return super().clean()

    def __str__(self) -> str:
        return self.description

    def __len__(self):
        return len(self.get_date_range())



class Availability(models.Model):
    """
    Availability model class
    """
    monday = models.PositiveIntegerField(
        "Monday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    tuesday = models.PositiveIntegerField(
        "Tuesday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    wednesday = models.PositiveIntegerField(
        "Wednesday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    thursday = models.PositiveIntegerField(
        "Thursday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    friday = models.PositiveIntegerField(
        "Friday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    saturday = models.PositiveIntegerField(
        "Saturday", validators=[MaxValueValidator(24), MinValueValidator(0)])
    sunday = models.PositiveIntegerField(
        "Sunday", validators=[MaxValueValidator(24), MinValueValidator(0)])

    def as_list(self):
        """
        Returns list of availible hours mon-sun = 0-6
        """
        return [
            self.monday,
            self.tuesday,
            self.wednesday,
            self.thursday,
            self.friday,
            self.saturday,
            self.sunday
        ]
    
    def get_hour_per_week(self):
        """
        Returns total amount of availible hours
        per week
        """
        return sum(self.as_list())

    def save(self, *args, **kwargs):
        """
        Set pk to 1 to ensure singleton table
        """
        self.pk = 1
        super().save(*args, **kwargs)
