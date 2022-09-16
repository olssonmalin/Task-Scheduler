from django.shortcuts import render
from django.http import HttpResponse

from .models import Task, Category
from .forms import TaskForm


def index(request):
    return render(request, "index.html")


def add_task(request):
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
                            status=['status']
                            )
            new_task.save()
    categories = Category.objects.all()
    return render(request, "add_task.html", {"form": form, 'categories': categories})


def show_tasks(request):
    tasks = Task.objects.all()
    return render(request, 'all_tasks.html', {'tasks': tasks})
