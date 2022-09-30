from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('task/add', views.add_task, name='add task'),
    path('task/all', views.show_tasks, name='all tasks'),
    path('task/<int:id>', views.show_single_task, name='single task'),
    path('task/remove/<int:id>', views.remove_task, name='remove task'),
    path('task/update/<int:id>', views.update_task, name='update task'),
    path('task/add-hours/<int:id>', views.add_time_task, name='add time'),
    path('category/all', views.show_categories, name='all categories'),
    path('category/<int:id>', views.remove_category, name='remove category'),
    path('category/update/<int:id>',
         views.update_category, name='update category'),
    path('profile/', views.profile, name='profile')
]
