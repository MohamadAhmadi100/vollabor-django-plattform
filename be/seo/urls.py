from django.urls import path
from . import views

urlpatterns = [
    path("user_footprint/", views.user_footprint, name='user-footprint-page'),
    path("user_footprint-ajax/", views.user_footprint_ajax, name='user-footprint-ajax'),
    path("robots/", views.robots, name='meta-robots-page'),
    path("title-and-description/", views.title_and_description, name='title-and-description-page'),
    path("title-and-description/update/<int:pk>/", views.title_and_description_update, name='title-and-description-update'),
    path("meta-tag/", views.metatag_list, name='metatag-page'),

    path('chart', views.line_chart, name='line_chart'),
    path('chartJSON', views.line_chart_json, name='line_chart_json'),
]
