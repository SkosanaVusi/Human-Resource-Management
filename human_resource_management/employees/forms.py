from django import forms
from .models import Employee
from django.core.exceptions import ValidationError
from .models import Department

class EmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Employee
        exclude = ['employee_number']
    
    manager = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        employee = self.instance
        if email != employee.email and Employee.objects.filter(email=email).exists():
            raise ValidationError("An employee with this email already exists.")
        return email