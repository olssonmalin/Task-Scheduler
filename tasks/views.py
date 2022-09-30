from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.core import serializers

from .models import Availability, Task, Category
from .forms import AvailabilityForm, TaskForm
import plotly.express as px
import pandas as pd

def index(request):
    tasks = Task.objects.all()
    # data = serializers.serialize('json', tasks)

    df = pd.DataFrame([
    dict(Task="Job A", Start='2009-01-01', Finish='2009-02-28', Resource="Alex"),
    dict(Task="Job B", Start='2009-03-05', Finish='2009-04-15', Resource="Alex"),
    dict(Task="Job C", Start='2009-02-20', Finish='2009-05-30', Resource="Max")
    ])

    fig = px.timeline(df, x_start="Start", x_end="Finish", y="Task", color="Resource")
    fig.update_yaxes(autorange="reversed")
    chart = fig.to_html()
    
    return render(request, "timeline.html", {'data': chart})


def add_task(request):
    """
    Renders template with a form to add a task, 
    accepts post request and and task to db
    """
    form = TaskForm()
    if request.method == 'POST':
        try:
            category = Category.objects.get(name=request.POST['category'])
        except:
            category = Category(name=request.POST['category'])
            category.save()
        posted_form = TaskForm(request.POST)
        if posted_form.is_valid():
            data = request.POST
            new_task = Task(description=data['description'],
                            category=category,
                            start=data['start'],
                            deadline=data['deadline'],
                            estimated_duration=data['estimated_duration'],
                            actual_duration=data['actual_duration'],
                            status=data['status']
                            )
            new_task.save()
            return redirect('all tasks')
    categories = Category.objects.all()
    return render(request, "add_task.html", {"form": form, 'categories': categories})

def search_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
    q = request.GET['q']
    if q is not None and q != '':
        categories = Category.objects.filter(name__contains=q).values_list('id', flat=True)
        q_category = Q(category__in=list(categories))
        q_description = Q(description__contains=q)
        tasks = Task.objects.filter(q_description | q_category)
    return tasks


def show_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
    if 'q' in request.GET:
        tasks = search_tasks(request)
    else:
        tasks = Task.objects.all()
    return render(request, 'all_tasks.html', {'tasks': tasks})


def show_categories(request):
    """
    Renders template that shows all categories as a list
    """
    categories = Category.objects.all()
    return render(request, 'all_categories.html', {'categories': categories})


def show_single_task(request, id=1):
    """
    renders single task template. Shows details of the task
    :param <int> id 
    """
    task = Task.objects.get(id=id)
    return render(request, "single_task.html", {'task': task})

def add_time_task(request, id):
    """
    Adds elapsed time to task
    """
    task = Task.objects.get(id=id)
    if request.method == "POST":
        elapsed_hours = task.actual_duration
        add_hours = request.POST['hours']
        sum_hours = elapsed_hours + int(add_hours)
        task.actual_duration = sum_hours
        task.save()
    return redirect('all tasks')

def remove_task(request, id):
    """
    Removes task with requested id
    """
    Task.objects.get(id=id).delete()
    return redirect('all tasks')


def remove_category(request, id):
    """
    Removes category with requested id
    """
    Category.objects.get(id=id).delete()
    return redirect('all categories')


def update_task(request, id):
    """
    updates task with requested id
    """
    task = Task.objects.get(id=id)
    if request.method == 'POST':
        try:
            category = Category.objects.get(name=request.POST['category'])
        except:
            category = Category(name=request.POST['category'])
            category.save()
        posted_form = TaskForm(request.POST)
        if posted_form.is_valid():
            data = request.POST
            task.description = data['description']
            task.category = category
            task.start = data['start']
            task.deadline = data['deadline']
            task.estimated_duration = data['estimated_duration']
            task.actual_duration = data['actual_duration']
            task.status = data['status']
            task.save()
            return redirect('all tasks')
    task_form = TaskForm(instance=task)
    current_category = task.category
    categories = Category.objects.all()
    return render(request, "update_task.html", {'form': task_form, 'categories': categories, 'current_category': current_category, 'task': task})


def update_category(request, id):
    """Updates given category"""
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        category.name = data['category']
        category.save()
        return redirect('all categories')
    return render(request, "update_category.html", {'category': category})


def profile(request):
    """Profile view, shows form for availability"""
    try:
        availability = Availability.objects.get(id=1)
        form = AvailabilityForm(instance=availability)
        if request.method == 'POST':
            form = AvailabilityForm(request.POST, instance=availability)
            if form.is_valid():
                form.save()
    except:
        form = AvailabilityForm()
        if request.method == 'POST':
            form = AvailabilityForm(request.POST)
            if form.is_valid():
                form.save()
    return render(request, "profile.html", {"form": form})
