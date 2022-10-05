from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.contrib import messages


from .models import Availability, Task, Category
from .forms import AvailabilityForm, TaskForm
import plotly.express as px
import pandas as pd
import datetime


def index(request):
    tasks = Task.objects.all()
    context = {}
    if tasks:
        colors = {
            'Not started': '#ff595e',
            'On going': '#ffca3a',
            'Completed': '#8ac926'
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

        df = pd.DataFrame(task_data)

        hover = {
            'Task': True,
            'Start': True,
            'Deadline': True,
            'End': False,
            'Status': True,
            'Category': True
        }

        fig = px.timeline(df, x_start="Start", x_end="End", y="Task", color="Status", color_discrete_map=colors, hover_data=hover)
        fig.update_yaxes(autorange="reversed")
        today = datetime.date.today()
        fig.update_layout(shapes=[
            dict(
                type='line',
                yref='paper', y0=0, y1=1,
                xref='x', x0=today, x1=today
            )
        ])
        chart = fig.to_html()
        context['data'] = chart
    
    return render(request, "timeline.html", context)


def add_task(request):
    """
    Renders template with a form to add a task, 
    accepts post request and and task to db
    """
    context = {}
    form = TaskForm()
    if request.method == 'POST':
        form  = TaskForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                category = Category.objects.get(name=request.POST['category'])
            except:
                category = Category(name=request.POST['category'])
                category.save()
            obj.category = category
            if obj.enough_time():
                obj.save()
                messages.add_message(request, messages.SUCCESS, 'Task was added sucessfully')
                return redirect('all tasks')
            else:
                suggested_deadline = obj.get_new_deadline()
                messages.add_message(request, messages.ERROR, f'Not enough time to complete task before deadline, next possible deadline is {suggested_deadline}')
    categories = Category.objects.all()
    context['form'] = form
    context['categories'] = categories
    return render(request, "add_task.html", context)

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
        messages.add_message(request, messages.SUCCESS, f'{add_hours}h was added to task {task.description}')
    return redirect('all tasks')

def remove_task(request, id):
    """
    Removes task with requested id
    """
    Task.objects.get(id=id).delete()
    messages.add_message(request, messages.SUCCESS, 'Task was removed successfully')
    return redirect('all tasks')


def remove_category(request, id):
    """
    Removes category with requested id
    """
    Category.objects.get(id=id).delete()
    messages.add_message(request, messages.SUCCESS, 'Category was removed successfully')
    return redirect('all categories')


def update_task(request, id):
    """
    updates task with requested id
    """
    task = Task.objects.get(id=id)
    task_form = TaskForm(instance=task)
    if request.method == 'POST':
        form  = TaskForm(request.POST, instance=task)
        if form.is_valid():
            obj = form.save(commit=False)
            try:
                category = Category.objects.get(name=request.POST['category'])
            except:
                category = Category(name=request.POST['category'])
                category.save()
            obj.category = category
            if obj.enough_time():
                obj.save()
                messages.add_message(request, messages.SUCCESS, 'Task was added sucessfully')
                return redirect('all tasks')
            else:
                suggested_deadline = obj.get_new_deadline()
                messages.add_message(request, messages.ERROR, f'Not enough time to complete task before deadline, next possible deadline is {suggested_deadline}')        
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
