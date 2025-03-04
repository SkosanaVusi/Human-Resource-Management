from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Employee
        exclude = ['employee_number']
    
    manager = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False)