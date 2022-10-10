from django.urls import path
from . import views

app_name = 'zarinpal'
urlpatterns = [
    path('request/ajax/<int:pk>', views.request_amount, name='request-ajax'),
    path('request/<int:pk>', views.send_request, name='request'),
    path('verify/<int:pk>/', views.verify , name='verify'),
]