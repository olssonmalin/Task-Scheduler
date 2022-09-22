from django import forms
from .models import Task, Category


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        exclude = ['category']
        widgets = {
            'start': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control', 'placeholder': 'Select a date', 'type': 'date'})
        }


# class CategoryForm(forms.ModelForm):
#     class Meta:
#         model: Category
#         fields = ['name']
