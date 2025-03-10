from django.shortcuts import render, get_object_or_404, redirect
from .models import Employee, Note
from .forms import EmployeeForm, NoteForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages

# Handles user login and redirects to employee list on success
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('employee_list') # Successful login redirects to employee list
        else:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})
    return render(request, 'employees/login.html')

# Logs out the user and redirects to login page
def logout_view(request):
    logout(request)
    return redirect('login')

# Displays and filters the list of employees (requires login)
@login_required
def employee_list(request):
    employees = Employee.objects.all()
    sort_by = request.GET.get('sort_by', 'surname') # Default sort by surname
    employees = employees.order_by(sort_by)
    
    # Filter variables from GET request
    search_name = request.GET.get('search_name', '')
    search_surname = request.GET.get('search_surname', '')
    search_employee_number = request.GET.get('search_employee_number', '')
    search_salary = request.GET.get('search_salary', '')
    salary_filter = request.GET.get('salary_filter', '')
    search_role = request.GET.get('search_role', '')
    search_manager = request.GET.get('search_manager', '')
    search_department = request.GET.get('search_department', '')

    # Use session value if no status_filter in GET params, otherwise update session
    if 'status_filter' in request.GET:
        status_filter = request.GET.get('status_filter', 'active')
        request.session['status_filter'] = status_filter  # Store in session
    else:
        status_filter = request.session.get('status_filter', 'active')  # Retrieve from session  
    
    if status_filter == 'active':
        employees = employees.filter(is_active=True)  
    elif status_filter == 'inactive':
        employees = employees.filter(is_active=False)

    # Apply filters based on search inputs
    if search_department:
        employees = employees.filter(department__name__icontains=search_department)
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
        'search_department': search_department,
        'search_name': search_name,
        'search_surname': search_surname,
        'search_employee_number': search_employee_number,
        'search_salary': search_salary,
        'salary_filter': salary_filter,
        'search_role': search_role,
        'search_manager': search_manager,
        'sort_by': sort_by,
        'status_filter': status_filter,  

    })

# Creates a new employee (requires login)
@login_required
def create_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            employee = form.save()
            employee.is_active = True  # Ensure status is active after edit
            employee.save()  # Save again to update is_active
            return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'employees/employee_form.html', {'form': form})

# Edits an existing employee (requires login)
@login_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            employee = form.save()
            employee.is_active = True  # Ensure status is active after edit
            employee.save()  # Save again to update is_active
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/employee_form.html', {'form': form})

# Deletes an employee after confirmation (requires login)
@login_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        employee.delete()
        return redirect('employee_list')
    return render(request, 'employees/employee_confirm_delete.html', {'employee': employee})

# Builds a hierarchical structure of employees
def build_hierarchy(manager=None):
    employees = Employee.objects.filter(manager=manager)
    return [
        {
            "id": emp.id,
            "name": f"{emp.name} {emp.surname}",
            "role": emp.role,
            "children": build_hierarchy(emp), # Recursive call for subordinates
            "employee_number": emp.employee_number
        }
        for emp in employees
    ]

# Returns employee hierarchy as JSON for visualization
def hierarchy_view(request):
    data = build_hierarchy(None) # Start with top-level (no manager)
    return JsonResponse({"hierarchy": data})

# Renders the hierarchy page
def hierarchy_page(request):
    return render(request, 'employees/employee_hierarchy.html')

# Displays employee details and manages notes (requires login)
@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        note_form = NoteForm(request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.employee = employee
            note.save()
            messages.success(request, "Note added successfully.")
            return redirect('employee_detail', pk=pk) 
    else:
        note_form = NoteForm()
    return render(request, 'employees/employee_detail.html', {
        'employee': employee,
        'note_form': note_form,
        'notes': employee.notes.order_by('-created_at'), # Latest notes first
    })

# Deletes multiple employees at once (requires login)
@login_required
def bulk_delete_employees(request):
    if request.method == 'POST':
        employee_ids = request.POST.getlist('employee_ids') # Get list of IDs to delete
        if employee_ids:
            Employee.objects.filter(id__in=employee_ids).delete()
        return redirect('employee_list')
    return redirect('employee_list')

# Toggles an employee’s active/inactive status (requires login)
@login_required
def toggle_employee_status(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        old_status = "active" if employee.is_active else "inactive"
        employee.is_active = not employee.is_active # Toggle status
        new_status = "active" if employee.is_active else "inactive"
        employee.save()
        messages.success(request, f"Employee status changed from {old_status} to {new_status}.")  # success message
    return redirect('employee_detail', pk=pk)

# Deletes a specific note (requires login)
@login_required
def delete_note(request, note_id):
    note = get_object_or_404(Note, id=note_id)
    employee_id = note.employee.id
    note.delete()
    messages.success(request, "Note deleted successfully.")
    return redirect('employee_detail', pk=employee_id)

# Uploads a profile picture for an employee (requires login)
@login_required
def upload_profile_picture(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        profile_picture = request.FILES.get('profile_picture')
        if profile_picture:
            employee.profile_picture = profile_picture.read()  # Store as binary data
            employee.save()
            messages.success(request, "Profile picture uploaded successfully.")
        else:
            messages.error(request, "No picture provided.")
        return redirect('employee_detail', pk=pk)
    return redirect('employee_detail', pk=pk)  # Fallback for GET requests