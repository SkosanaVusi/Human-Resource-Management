from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.employee_list, name='employee_list'),
    path('create/', views.create_employee, name='create_employee'),
    path('edit/<int:pk>/', views.edit_employee, name='edit_employee'),
    path('delete/<int:pk>/', views.delete_employee, name='delete_employee'),
    path('hierarchy/', views.hierarchy_page, name='employee_hierarchy'),  
    path('api/hierarchy/', views.hierarchy_view, name='hierarchy_data'),  
    path('detail/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('bulk-delete/', views.bulk_delete_employees, name='bulk_delete_employees'), 
    path('toggle-status/<int:pk>/', views.toggle_employee_status, name='toggle_employee_status'),  
    path('note/delete/<int:note_id>/', views.delete_note, name='delete_note'),

]