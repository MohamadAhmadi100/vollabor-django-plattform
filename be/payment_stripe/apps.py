from django.apps import AppConfig


class PaymentStripeConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'payment_stripe'

    def ready(self):
        import payment_stripe.signals
