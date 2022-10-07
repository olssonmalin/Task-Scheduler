"""
Modelform classes
"""

from django import forms
from .models import Availability, Task


class TaskForm(forms.ModelForm):
    """
    Form class for task model
    """
    class Meta:
        """
        Form meta class
        """
        model = Task
        fields = ['description', 'start', 'deadline',
            'estimated_duration', 'actual_duration', 'status']
        widgets = {
            'start': forms.DateInput(attrs={'class': 'form-control',
                'placeholder': 'Select a date', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'form-control',
                'placeholder': 'Select a date', 'type': 'date'})
        }
        

class AvailabilityForm(forms.ModelForm):
    """
    Form class for availability model
    """
    class Meta:
        """
        Form meta class
        """
        model = Availability
        fields = "__all__"
