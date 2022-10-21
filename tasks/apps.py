"""
Apps module
"""
from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Task config class
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
