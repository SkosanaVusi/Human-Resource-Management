from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee
from .forms import EmployeeForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('employee_list')
        else:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})
    return render(request, 'employees/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def employee_list(request):
    employees = Employee.objects.all()
    sort_by = request.GET.get('sort_by', 'surname')
    employees = employees.order_by(sort_by)
    search_name = request.GET.get('search_name', '')
    search_surname = request.GET.get('search_surname', '')
    search_employee_number = request.GET.get('search_employee_number', '')
    search_salary = request.GET.get('search_salary', '')
    salary_filter = request.GET.get('salary_filter', '')
    search_role = request.GET.get('search_role', '')
    search_manager = request.GET.get('search_manager', '')

    if search_name:
        employees = employees.filter(name__icontains=search_name)
    if search_surname:
        employees = employees.filter(surname__icontains=search_surname)
    if search_employee_number:
        employees = employees.filter(employee_number__icontains=search_employee_number)
    if search_salary:
        if salary_filter == 'greater_than':
            employees = employees.filter(salary__gt=search_salary)
        elif salary_filter == 'lower_than':
            employees = employees.filter(salary__lt=search_salary)
        else:
            employees = employees.filter(salary=search_salary)
    if search_role:
        employees = employees.filter(role__icontains=search_role)
    if search_manager:
        employees = employees.filter(manager__name__icontains=search_manager)

    return render(request, 'employees/employee_list.html', {
        'employees': employees,
        'search_name': search_name,
        'search_surname': search_surname,
        'search_employee_number': search_employee_number,
        'search_salary': search_salary,
        'salary_filter': salary_filter,
        'search_role': search_role,
        'search_manager': search_manager,
        'sort_by': sort_by,
    })

@login_required
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form})

@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form})

@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})