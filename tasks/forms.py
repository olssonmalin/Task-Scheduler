from django import forms
from .models import Task, Category


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['category']


class CategoryForm(forms.ModelForm):
    class Meta:
        model: Category
        fields = ['name']
