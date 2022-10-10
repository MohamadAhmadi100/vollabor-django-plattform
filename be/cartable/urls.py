from django.urls import path
from . import views

urlpatterns = [
    path("", views.cartable_panel, name='cartable-main-panel'),
    path("send-new-letter/", views.send_new_letter_panel, name='send-new-letter-panel'),
    path("cartable-letter/", views.cartable_letter, name='cartable-letter-panel'),
    path("refer-letter/<int:pk>/", views.refer_letter, name='refer-letter'),
    path("send-letter/<int:pk>/", views.send_letter, name='sent-letter'),
]
