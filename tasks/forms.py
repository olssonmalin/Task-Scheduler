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
            'start': forms.DateInput(attrs={'class': 'input',
                'placeholder': 'Select a date', 'type': 'date'}),
            'deadline': forms.DateInput(attrs={'class': 'input',
                'placeholder': 'Select a date', 'type': 'date'})
        }
    
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['description'].widget.attrs.update({'class': 'input'})
        self.fields['estimated_duration'].widget.attrs.update({'class': 'input'})
        self.fields['actual_duration'].widget.attrs.update({'class': 'input'})
        self.fields['status'].widget.attrs.update({'class': 'input'})


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
    
    def __init__(self, *args, **kwargs):
        super(AvailabilityForm, self).__init__(*args, **kwargs)
        self.fields['monday'].widget.attrs.update({'class': 'input'})
        self.fields['tuesday'].widget.attrs.update({'class': 'input'})
        self.fields['wednesday'].widget.attrs.update({'class': 'input'})
        self.fields['thursday'].widget.attrs.update({'class': 'input'})
        self.fields['friday'].widget.attrs.update({'class': 'input'})
        self.fields['saturday'].widget.attrs.update({'class': 'input'})
        self.fields['sunday'].widget.attrs.update({'class': 'input'})


class UploadFileForm(forms.Form):
    """
    Import tasks form
    """
    file = forms.FileField()
