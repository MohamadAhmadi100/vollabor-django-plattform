from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # path('', views.home, name='home'),
    path('create-checkout-session/', login_required(views.create_checkout_session_view),
         name='create-checkout-session'),
    path('success/<int:pk>', views.success, name='success'),
    path('success/', views.success_, name='success_'),
    path('cancel/', views.cancel, name='cancel'),
    path('webhook/', views.my_webhook_view, name='webhook'),
    path('webhook/', views.my_webhook_view, name='webhook'),
    path('invoice/<str:slug>', views.in_voice, name='invoice-page'),
    path('paypal-pay/<str:amount>', views.process_payment, name='process_payment'),
]
