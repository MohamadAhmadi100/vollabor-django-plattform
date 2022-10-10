from django.urls import path
from . import views

urlpatterns = [
    path("robots/", views.robots, name='meta-robots-page'),
    path("title-and-description/", views.title_and_description, name='title-and-description-page'),
    path("title-and-description/update/<int:pk>/", views.title_and_description_update, name='title-and-description-update'),
    path("meta-tag/", views.metatag_list, name='metatag-page'),
]
