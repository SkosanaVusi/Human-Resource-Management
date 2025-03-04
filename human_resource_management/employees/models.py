from django.db import models

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

    class Meta:
        ordering = ['surname', 'name']