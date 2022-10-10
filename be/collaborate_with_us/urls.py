from django.urls import path
from . import views

urlpatterns = [
    path("", views.collaborate_with_us, name='collaborate-with-us-page'),
    path("manage/", views.manage_staff, name='staff-manager-page'),
]
