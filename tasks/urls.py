from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/add', views.add_task, name='add task'),
    path('task/all', views.show_tasks, name='all tasks'),
    path('task/<int:id>', views.show_single_task, name='single task')
]
