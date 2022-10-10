from django.urls import path
from . import views

urlpatterns = [
    path("", views.courses, name='courses-page'),
    path("id/<int:course_id>", views.course_item, name='course-item-page'),
]