from django.db import models
from django.core.exceptions import ValidationError
import hashlib


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Employee(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
        
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    employee_number = models.IntegerField(unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    role = models.CharField(max_length=100)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default='O')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)  # Added here
    is_active = models.BooleanField(default=True) 

    def __str__(self):
        return f"{self.name} {self.surname} - {self.role}"

    def clean(self):
        if self.manager == self:
            raise ValidationError("An employee cannot be their own manager.")
    
    def save(self, *args, **kwargs):
        # If the employee doesn't have a number yet, assign a unique one
        if not self.employee_number:
            max_employee_number = Employee.objects.aggregate(models.Max('employee_number'))['employee_number__max']
            if max_employee_number is None:
                self.employee_number = 1  # First employee gets number 1
            else:
                self.employee_number = max_employee_number + 1  # Increment the highest existing number
        super().save(*args, **kwargs)

    def get_gravatar_url(self):
        email = self.email.strip().lower()
        gravatar_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{gravatar_hash}"

    class Meta:
        ordering = ['surname', 'name']


class Note(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='notes')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Note for {self.employee.name} {self.employee.surname} on {self.created_at}"