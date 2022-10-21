"""
Url module
"""
from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/add', views.add_task, name='add task'),
    path('task/import', views.import_tasks, name='import tasks'),
    path('task/all', views.show_tasks, name='all tasks'),
    path('task/<int:task_id>', views.show_single_task, name='single task'),
    path('task/remove/<int:task_id>', views.remove_task, name='remove task'),
    path('task/update/<int:task_id>', views.update_task, name='update task'),
    path('task/add-hours/<int:task_id>', views.add_time_task, name='add time'),
    path('category/all', views.show_categories, name='all categories'),
    path('category/<int:category_id>', views.remove_category, name='remove category'),
    path('category/update/<int:category_id>',
         views.update_category, name='update category'),
    path('profile/', views.profile, name='profile')
]
