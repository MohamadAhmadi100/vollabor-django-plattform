from django.urls import path
from . import views

urlpatterns = [
    path("", views.frequently_asked_question_view, name='FAQ-page'),
]
