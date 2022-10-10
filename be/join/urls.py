from django.urls import path
from . import views

urlpatterns = [
    path("", views.cv_list, name='cv-page'),
    path("join/", views.upload_cv, name='cv-upload-page'),
    path("email-activation/<str:applicant_email>/", views.activation_email, name='email-activation-page'),
    path("email-activation/legal/<str:applicant_email>/", views.legal_activation_email, name='legal-email-activation-page'),
    
    path("simple_register/", views.simple_register, name='simple-register'),
    path("simple_login/", views.simple_login, name='simple-login'),

]