from django.urls import path
from . import views

urlpatterns = [ 
    path("", views.members, name='members-page'),
    path("profile/", views.profile, name='profile-page'),
    path("member_profile/<int:primary_key>", views.member_profile, name='member-profile-page'),
    path("reset_password/", views.reset_password_profile, name='reset-password'),
]