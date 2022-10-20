"""
Functions for Task Scheduler views
"""

import datetime
from time import time
import plotly.express as px
import pandas as pd

from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from .models import Availability, Task, Category
from .forms import AvailabilityForm, TaskForm, UploadFileForm
from .utils import handle_uploaded_file, get_category_object, availability_exists

def get_possible_deadlines(tasks):
    """
    Creates array of objects if overtime is needed
    on any task
    """
    deadlines = []
    ot_tasks = []
    for task in tasks:
        old = task.deadline
        new = task.get_new_deadline(None if not ot_tasks else ot_tasks)
        if task.status != 'C' and old != new:
            deadlines.append({
                'Task': task.description,
                'Start': old + datetime.timedelta(days=1),
                'Deadline': new,
                'End': new + datetime.timedelta(days=1),
                'Status': 'Overtime needed',
                'Category': task.category.name,
                'Hours left': task.estimated_duration - task.actual_duration
            })
            ot_tasks.append(task)
    return deadlines

def index(request):
    """
    Index of task scheduler
    """
    tasks = Task.objects.all().order_by('start', '-deadline')

    context = {}
    if tasks:
        week = (604800 * 1000)
        today = time() * 1000
        colors = {
            'Not started': '#6c757d',
            'Ongoing': '#ffca3a',
            'Completed': '#8ac926',
            'Overtime needed': 'rgba(255, 89, 94, 0.5)',
        }
        task_data = [
            {
                'Task': task.description,
                'Start': task.start,
                'Deadline': task.deadline,
                'End': task.deadline + datetime.timedelta(days=1),
                'Status': task.get_status_display(),
                'Category': task.category.name,
                'Hours left': task.estimated_duration - task.actual_duration
            } for task in tasks if task.deadline >= (datetime.date.today() - datetime.timedelta(days = 14) or task.status != 'C')
        ]
        if Availability.objects.get(id=1).get_hour_per_week() > 0:
            deadlines = get_possible_deadlines(tasks)
            data_frame = pd.DataFrame((task_data + deadlines))
        else:
            data_frame = pd.DataFrame((task_data))
            messages.add_message(request, messages.ERROR, "Not able to calculate overtime, 0 availible hours")

        hover = {
            'Task': False,
            'Start': '|%b %e',
            'Deadline': '|%b %e',
            'End': False,
            'Status': True,
            'Category': True,
            'Hours left': True
        }
        fig = px.timeline(data_frame, x_start="Start", x_end="End", y="Task", color="Status",
            color_discrete_map=colors, hover_data=hover, hover_name="Task", range_y=[0,len(tasks) - 1],
            range_x=[today - week, today + week])
        fig.update_layout(dragmode='pan',
        font_color='#10002B',
        font_family='Montserrat',
        title={
            'text': "Task Timeline",
            'xanchor': 'center',
            'yanchor': 'top',
            'y':1,
            'x':0.3,
            'font':{'size':28 }
            }
            )
        fig.update_yaxes(autorange="reversed", title=None, automargin=True)
        fig.update_xaxes(
            tickformat="%a %e/%m \n w.%W",
            type = 'date',
            tickformatstops=(dict(dtickrange=[None, 604800000], value="%a %e/%m \n w.%W"),
                dict(dtickrange=[604800000, "M1"], value="w.%W"),
                dict(dtickrange=["M1", "M12"], value="%b %Y"),
                dict(dtickrange=["M12", None], value="%Y Y"))
        )
        fig.add_vline(x=today, line_width=2, line_color="#10002B",
            annotation={'text': 'Now', 'font': {'size': 14, 'color': '#10002B'},
            'yshift': 20, 'xshift': -15})
        chart = fig.to_html()
        context['data'] = chart

    return render(request, "timeline.html", context)


def add_task(request):
    """
    Renders template with a form to add a task,
    accepts post request and and task to db
    """
    form = TaskForm()
    categories = Category.objects.all()
    current_category = ""
    if not availability_exists():
        messages.add_message(request, messages.WARNING, 'Please add your avalible hours \
            in Profile before adding a task')
        return redirect('profile')
    if request.method == 'POST':
        form  = TaskForm(request.POST)
        current_category = request.POST['category']
        if form.is_valid():
            obj = form.save(commit=False)
            obj.category = get_category_object(request.POST['category'])
            if obj.enough_time():
                obj.save()
                messages.add_message(request, messages.SUCCESS, 'Task was added sucessfully')
                return redirect('all tasks')
            suggested_deadline = obj.get_new_deadline()
            messages.add_message(request, messages.ERROR,\
                f'Not enough time to complete task before deadline, \
                    next possible deadline is {suggested_deadline}')
    context = {
        'form': form,
        'categories': categories,
        'current_category': current_category,
        'title': 'Add task'
    }
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
    q_value = ""
    status_value = ""
    if 'q' in request.GET:
        tasks = search_tasks(request)
        q_value = request.GET['q']
        status_value = request.GET['status']
    else:
        tasks = Task.objects.all().order_by('-status', 'deadline')

    context = {
        'tasks': tasks,
        'title': "Task List",
        'q': q_value,
        'status': status_value,
    }
    return render(request, 'all_tasks.html', context)

def import_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
    import_form = UploadFileForm()
    
    if not availability_exists():
        messages.add_message(request, messages.WARNING, 'Please add your avalible hours \
            in Profile before adding a task')
        return redirect('profile')
    if request.method == "POST":
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            handle_uploaded_file(request)

    context = {
        'title': "Import Tasks",
        'import_form': import_form
    }
    return render(request, 'import_tasks.html', context)


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
    context = {
        'task': task,
        'title': task.description
    }
    return render(request, "single_task.html", context)

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
    form = TaskForm(instance=task)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.category = get_category_object(request.POST['category'])
            obj.save()
            return redirect('all tasks')

    current_category = task.category
    categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories,
        'current_category': current_category,
        'task': task,
        'title': f'Update {task.description}'
    }
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
        messages.add_message(request, messages.SUCCESS,\
                'Category edited successfully!')
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
                messages.add_message(request, messages.SUCCESS,\
                'Availible hours edited successfully!')
    except ObjectDoesNotExist:
        form = AvailabilityForm()
        if request.method == 'POST':
            form = AvailabilityForm(request.POST)
            if form.is_valid():
                form.save()
                messages.add_message(request, messages.SUCCESS,\
                'Availible hours added successfully!')
    return render(request, "profile.html", {"form": form, 'title': "Availability"})
