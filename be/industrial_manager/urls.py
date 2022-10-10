from django.urls import path
from . import views

urlpatterns = [
    path("emails/", views.industrial_email, name='industrial-email-page'),
]
