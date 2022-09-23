from django.db import models
from django.core.validators import MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self) -> str:
        return self.name


class Task(models.Model):
    not_started = "NS"
    on_going = "OG"
    completed = "C"
    STATUS = (
        (not_started, "Not started"),
        (on_going, "On going"),
        (completed, "Completed")
    )

    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    start = models.DateField("Start date")  # add default?
    deadline = models.DateField("Deadline")  # add default?
    estimated_duration = models.IntegerField(default=0)
    actual_duration = models.IntegerField(default=0)
    status = models.CharField(
        max_length=2, choices=STATUS, default=not_started)

    def __str__(self) -> str:
        return self.description


class Availability(models.Model):

    MONDAY = "MO"
    TUESDAY = "TU"
    WEDNESDAY = "WE"
    THURSDAY = "TH"
    FRIDAY = "FR"
    SATURDAY = "SA"
    SUNDAY = "SU"

    DAYS = (
        (MONDAY, "Monday"),
        (TUESDAY, "Tuesday"),
        (WEDNESDAY, "Wednesday"),
        (THURSDAY, "Thursday"),
        (FRIDAY, "Friday"),
        (SATURDAY, "Saturday"),
        (SUNDAY, "Sunday")
    )

    day = models.CharField(max_length=2, choices=DAYS, primary_key=True)
    hours = models.PositiveIntegerField(validators=[MaxValueValidator(24)])
