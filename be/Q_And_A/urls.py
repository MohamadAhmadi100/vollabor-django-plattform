from django.urls import path
from . import views

urlpatterns = [
    path("", views.questions, name='questions-page'),
    path("question/<int:question_id>", views.question_and_answers, name='question-and-answers-page'),
]
