from unicodedata import category
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .models import Task, Category
from .forms import TaskForm


def index(request):
    return render(request, "index.html")


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
    categories = Category.objects.all()
    return render(request, "add_task.html", {"form": form, 'categories': categories})


def show_tasks(request):
    """
    Renders template that shows all tasks as a list
    """
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


def remove_task(request, id):
    """
    Removes task with requested id
    """
    Task.objects.get(id=id).delete()
    return redirect('all tasks')


def remove_category(request, name):
    """
    Removes category with requested id
    """
    Category.objects.get(name=name).delete()
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
    return render(request, "update_task.html", {'form': task_form, 'categories': categories, 'current_category': current_category})


def update_category(request, id):
    """Updates given category"""
    category = Category.objects.get(id=id)
    if request.method == 'POST':
        data = request.POST
        category.name = data['category']
        category.save()
        return redirect('all categories')
    return render(request, "update_category.html", {'category': category})
