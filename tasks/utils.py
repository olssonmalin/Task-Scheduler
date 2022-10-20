"""
Utility functions for Task scheduler
"""
import json
import csv
import io
from datetime import date
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Task, Category, Availability

def get_category_object(name):
    """
    Gets Category model object if exists or create a new Category object
    """
    try:
        category = Category.objects.get(name=name)
    except ObjectDoesNotExist:
        category = Category(name=name)
        category.save()
    return category

def has_correct_structure(data):
    """
    Check that data has correct structure
    """
    if all(key in data for key in ('description', 'category', 'start date',
        'deadline', 'estimated duration', 'elapsed time', 'status')):
        return True
    return False

def add_task_from_dict(task):
    """
    Adds tasks from a dict
    """
    start_date = list(map(int, task['deadline'].split('-')))
    deadline = list(map(int, task['deadline'].split('-')))
    new_task = Task(
        description = task['description'],
        start = date(start_date[2], start_date[1], start_date[0]),
        deadline = date(deadline[2], deadline[1], deadline[0]),
        estimated_duration = int(task['estimated duration']),
        actual_duration = int(task['elapsed time']),
        category=get_category_object(task['category'])
    )
    if new_task.enough_time():
        new_task.save()
        return True
    return False

def handle_uploaded_file(request):
    """
    Handles imported file containing tasks
    """
    file = request.FILES['file']
    schdueled = []
    not_schdueled = []
    if file.name.endswith("json"):
    # JSON
        data = json.loads(file.read())
        for task in data:
            task = dict((k.lower(), v) for k, v in task .items())
            if has_correct_structure(task) and add_task_from_dict(task):
                schdueled.append(task['description'])
            else:
                not_schdueled.append(task['description'])
    # CSV
    elif file.name.endswith("csv"):
        csv_file = file.read()
        reader = csv.DictReader(io.StringIO(csv_file.decode('utf-8')), delimiter=";")
        for row in reader:
            row = dict((k.lower(), v) for k, v in row .items())
            if has_correct_structure(row) and add_task_from_dict(row):
                schdueled.append(row['description'])
            else:
                not_schdueled.append(row['description'])

    else:
        messages.add_message(request, messages.ERROR,
            'Not allowed filed, please import JSON or CSV file.')
    if len(not_schdueled) > 0:
        messages.add_message(request, messages.ERROR,
            f'The following tasks chould not be scheduled: {", ".join(not_schdueled)}')

    if len(schdueled) > 0:
        messages.add_message(request, messages.SUCCESS,
            f'The following tasks were scheduled: {", ".join(schdueled)}')
    
def availability_exists():
    """
    Checks that availability hours
    exists in database
    """
    try:
        Availability.objects.get(id=1)
        return True
    except ObjectDoesNotExist:
        return False