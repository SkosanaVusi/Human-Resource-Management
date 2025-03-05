from django.db import models
from django.core.exceptions import ValidationError
import hashlib

class Employee(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    birth_date = models.DateField()
    employee_number = models.IntegerField(unique=True)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    role = models.CharField(max_length=100)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')

    def __str__(self):
        return f"{self.name} {self.surname} - {self.role}"

    def clean(self):
        if self.manager == self:
            raise ValidationError("An employee cannot be their own manager.")
    
    def save(self, *args, **kwargs):
        if not self.employee_number:
            if self.manager is None:
                self.employee_number = 1
            else:
                manager_employee_number = self.manager.employee_number
                max_employee_number = Employee.objects.filter(employee_number__gt=manager_employee_number).aggregate(models.Max('employee_number'))['employee_number__max']
                if max_employee_number is None:
                    self.employee_number = manager_employee_number + 1
                else:
                    self.employee_number = max(manager_employee_number + 1, max_employee_number + 1)
        super().save(*args, **kwargs)

    def get_gravatar_url(self):
        email = self.email.strip().lower()
        gravatar_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
        return f"https://www.gravatar.com/avatar/{gravatar_hash}"

    class Meta:
        ordering = ['surname', 'name']