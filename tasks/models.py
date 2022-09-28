from calendar import SATURDAY
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


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

    def save(self, *args, **kwargs):
        self.pk = 1
        super(Availability, self).save(*args, **kwargs)
