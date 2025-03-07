from django.contrib import admin
from .models import Employee, Department

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Department, DepartmentAdmin)

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_number', 'name', 'surname', 'role', 'salary', 'manager')
    search_fields = ('name', 'surname', 'role', 'manager__name')
    list_filter = ('role', 'manager') # Filter options
    ordering = ('employee_number',)

admin.site.register(Employee, EmployeeAdmin)