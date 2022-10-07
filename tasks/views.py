"""
Functions for Task Scheduler views
"""

import datetime
from multiprocessing import context
from time import time
import plotly.express as px
import pandas as pd

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import Availability, Task, Category
from .forms import AvailabilityForm, TaskForm

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

def add_possible_deadlines(fig, tasks):
    """
    Gets possible deadlines
    """
    # tasks = reversed(tasks)
    index = 0
    for task in tasks:
        new = task.get_new_deadline() + datetime.timedelta(days=1)
        if task.status != 'C':
            fig.add_shape(type="line", y0=(index - 0.5), y1=(index + 0.5), x0=new, x1=new, line=dict(
        color='#1982c4',
        width=2,
    ))
        index+=1
            
def index(request):
    """
    Index of task scheduler
    """
    tasks = Task.objects.all()
    context = {
        'title': 'Timeline'
    }
    if tasks:
        colors = {
            'Not started': '#ff595e',
            'Ongoing': '#ffca3a',
            'Completed': '#8ac926',
            'Possible finish date': '#1982c4',
        }
        task_data = [
            {
                'Task': task.description,
                'Start': task.start,
                'Deadline': task.deadline,
                'End': task.deadline + datetime.timedelta(days=1),
                'Status': task.get_status_display(),
                'Category': task.category.name
            } for task in tasks
        ]

        data_frame = pd.DataFrame((task_data))
        hover = {
            'Task': True,
            'Start': True,
            'Deadline': True,
            'End': False,
            'Status': True,
            'Category': True
        }

        fig = px.timeline(data_frame, x_start="Start", x_end="End", y="Task", color="Status",
            color_discrete_map=colors, hover_data=hover, range_y=[0,len(tasks) - 1])
        fig.update_yaxes(autorange="reversed")
        today = time() * 1000
        fig.add_vline(x=today, line_width=2, line_color="#10002B", 
            annotation={'text': 'Now', 'font': {'size': 14, 'color': '#10002B'}, 'yshift': 20, 'xshift': -15})
        add_possible_deadlines(fig, tasks)
        chart = fig.to_html()
        context['data'] = chart
        context['fig'] = fig

    return render(request, "timeline.html", context)


def add_task(request):
    """
    Renders template with a form to add a task,
    accepts post request and and task to db
    """
    form = TaskForm()
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'title': 'Add task'
    }
    if not availability_exists():
        messages.add_message(request, messages.ERROR, 'Please add your avalible hours \
            in Profile before adding a task')
        return redirect('profile')
    if request.method == 'POST':
        form  = TaskForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                category = Category.objects.get(name=request.POST['category'])
            except ObjectDoesNotExist:
                category = Category(name=request.POST['category'])
                category.save()
            obj.category = category
            if obj.enough_time():
                obj.save()
                messages.add_message(request, messages.SUCCESS, 'Task was added sucessfully')
                return redirect('all tasks')
            suggested_deadline = obj.get_new_deadline()
            messages.add_message(request, messages.ERROR,\
                f'Not enough time to complete task before deadline, \
                    next possible deadline is {suggested_deadline}')
    return render(request, "add_task.html", context)

def search_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
    query = request.GET['q']
    status = request.GET['status']
    if query is not None:
        categories = Category.objects.filter(name__contains=query).values_list('id', flat=True)
        q_category = Q(category__in=list(categories))
        q_description = Q(description__contains=query)
        tasks = Task.objects.filter(q_description | q_category)
        if status != '':
            tasks = Task.objects.filter(q_description | q_category, status=status)
    return tasks

def show_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
    if 'q' in request.GET:
        tasks = search_tasks(request)
    else:
        tasks = Task.objects.all()
    
    context = {
        'tasks': tasks,
        'title': "Tasks",
    }
    return render(request, 'all_tasks.html', context)


def show_categories(request):
    """
    Renders template that shows all categories as a list
    """
    categories = Category.objects.all()
    context = {
        'categories': categories,
        'title': "Categories"
    }
    return render(request, 'all_categories.html', context)


def show_single_task(request, task_id=1):
    """
    renders single task template. Shows details of the task
    :param <int> id
    """
    task = Task.objects.get(id=task_id)
    return render(request, "single_task.html", {'task': task})

def add_time_task(request, task_id):
    """
    Adds elapsed time to task
    """
    task = Task.objects.get(id=task_id)
    if request.method == "POST":
        elapsed_hours = task.actual_duration
        add_hours = request.POST['hours']
        if task.actual_duration == 0:
            task.status = "OG"
        sum_hours = elapsed_hours + int(add_hours)
        task.actual_duration = sum_hours
        task.save()
        messages.add_message(request, messages.SUCCESS,\
            f'{add_hours}h was added to task {task.description}')
    return redirect('all tasks')

def remove_task(request, task_id):
    """
    Removes task with requested id
    """
    Task.objects.get(id=task_id).delete()
    messages.add_message(request, messages.SUCCESS, 'Task was removed successfully')
    return redirect('all tasks')


def remove_category(request, category_id):
    """
    Removes category with requested id
    """
    Category.objects.get(id=category_id).delete()
    messages.add_message(request, messages.SUCCESS, 'Category was removed successfully')
    return redirect('all categories')


def update_task(request, task_id):
    """
    updates task with requested id
    """
    task = Task.objects.get(id=task_id)
    task_form = TaskForm(instance=task)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                category = Category.objects.get(name=request.POST['category'])
            except ObjectDoesNotExist:
                category = Category(name=request.POST['category'])
                category.save()
            obj.category = category
            if obj.enough_time():
                obj.save()
                messages.add_message(request, messages.SUCCESS, 'Task was added sucessfully')
                return redirect('all tasks')
            suggested_deadline = obj.get_new_deadline()
            messages.add_message(request, messages.ERROR,\
                f'Not enough time to complete task before deadline, \
                    next possible deadline is {suggested_deadline}')
    current_category = task.category
    categories = Category.objects.all()
    context = {
        'form': task_form,
        'categories': categories,
        'current_category': current_category,
        'task': task}
    return render(request, "update_task.html", context)


def update_category(request, category_id):
    """
    Updates given category
    """
    category = Category.objects.get(id=category_id)
    if request.method == 'POST':
        data = request.POST
        category.name = data['category']
        category.save()
        return redirect('all categories')
    return render(request, "update_category.html", {'category': category})


def profile(request):
    """
    Profile view, shows form for availability
    """
    try:
        availability = Availability.objects.get(id=1)
        form = AvailabilityForm(instance=availability)
        if request.method == 'POST':
            form = AvailabilityForm(request.POST, instance=availability)
            if form.is_valid():
                form.save()
    except ObjectDoesNotExist:
        form = AvailabilityForm()
        if request.method == 'POST':
            form = AvailabilityForm(request.POST)
            if form.is_valid():
                form.save()
    return render(request, "profile.html", {"form": form})
