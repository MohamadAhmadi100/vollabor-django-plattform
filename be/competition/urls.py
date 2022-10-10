from django.urls import path
from . import views

urlpatterns = [
    path("", views.competition_manager, name='competition-manager-page'),
]
