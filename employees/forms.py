from django import forms
from .models import Employee, Note
from django.core.exceptions import ValidationError
from .models import Department

class EmployeeForm(forms.ModelForm):
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}) # HTML5 date picker
    )
    profile_picture = forms.FileField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Employee
        exclude = ['employee_number'] # Auto-managed field
    
    manager = forms.ModelChoiceField(queryset=Employee.objects.all(), required=False)
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False)

    def save(self, commit=True):
        instance = super().save(commit=False)
        profile_picture = self.cleaned_data.get('profile_picture')
        if profile_picture:
            instance.profile_picture = profile_picture.read() # Store file as binary
        elif 'profile_picture' in self.changed_data and not profile_picture:
            instance.profile_picture = None # Clear if removed
        if commit:
            instance.save()
        return instance

    def clean_email(self):
        email = self.cleaned_data.get('email')
        employee = self.instance
        if email != employee.email and Employee.objects.filter(email=email).exists():
            raise ValidationError("An employee with this email already exists.") # Ensure unique email
        return email

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter your note here...'}),
        }