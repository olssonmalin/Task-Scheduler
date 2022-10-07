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

    def get_avg_per_day(self):
        """
        Gets avarage amount of hours needed to spend
        on current task to complete on time
        """
        days = len(self.get_date_range())
        hours_left = self.estimated_duration - self.actual_duration
        return hours_left/days

    def get_hours_range(self, date_range):
        """
        Gets hours scheduled to spend on task
        within given date range
        """
        saved_range = self.get_date_range()
        total = 0
        for day in date_range:
            if day in saved_range:
                total += self.get_avg_per_day()
        return total

    def get_new_deadline(self):
        """
        Finds new possible deadline for task
        """
        while not self.enough_time():
            self.deadline = self.deadline + timedelta(days = 1)
        return self.deadline

    def avalible_hours(self):
        """
        Gets avalible hours based on user availability
        during current tasks date range
        """
        availability = Availability.objects.get(id=1).as_list()
        hours = 0
        for day in self.get_date_range():
            hours += availability[day.weekday()]
        return hours

    def time_left(self):
        """
        Chacks avalible time left during current tasks date-range
        including paralell tasks
        @return: float
        """
        all_tasks = __class__.objects.exclude(id=self.id)
        available_time = self.avalible_hours()
        date_range = self.get_date_range()
        for task in all_tasks:
            if task.status == "C":
                continue
            available_time -= task.get_hours_range(date_range)
        total = (available_time - self.estimated_duration) + self.actual_duration
        return total

    def enough_time(self):
        """
        Checks if there is enough avalible time to schedule task
        @return: bool
        """
        if self.time_left() >= 0:
            return True

        all_tasks = __class__.objects.exclude(id=self.id)

        for task in all_tasks:
            if task.status == "C":
                continue
            if task.time_left() - self.estimated_duration >= 0:
                return True
        return False

    def clean(self) -> None:
        """
        Cleans attributes before save
        """
        # Ensure deadline is not prior to start date
        if self.deadline < self.start:
            raise ValidationError({'deadline': ('Deadline may not be prior to start date')})

        # Ensure there is enough avalible time to schedule new task/update existing task
        if not self.enough_time():
            raise ValidationError({'deadline': \
                (f'Not enough time to complete task before deadline, \
                    next possible deadline: {self.get_new_deadline()}')})
        return super().clean()

    def __str__(self) -> str:
        return self.description


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

    def save(self, *args, **kwargs):
        """
        Set pk to 1 to ensure singleton table
        """
        self.pk = 1
        super().save(*args, **kwargs)
