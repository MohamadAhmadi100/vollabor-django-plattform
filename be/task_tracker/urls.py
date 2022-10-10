from django.urls import path


from . import views

urlpatterns = [
    path("", views.total_time, name='total_time'),
    path("delete/<int:pk>", views.delete_task, name='delete-task'),
    path("confirm/", views.confirm_task, name='confirm-task'),
    path("manager_list/", views.manager_list, name='manager-list'),
    path("manager_list/add_comment/", views.manager_comment, name='manager-comment'),
    path("manager_list/add_employee_task/", views.manager_add_task, name='add-employee-task'),
    path("human_resource_list/", views.human_resource_list, name='human-resource-list'),
    path("human_resource_list/attendance_list", views.attendance_list, name='attendance-list'),
    path("human_resource_list/pdf/", views.generate_pdf, name='generate-pdf'),
    
]