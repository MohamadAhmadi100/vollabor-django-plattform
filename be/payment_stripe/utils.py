from django.contrib.auth.models import User

from payment_stripe.models import InternationalOrder


def fulfill_order(session):
    print(session)
    the_order = InternationalOrder.objects.get(payment_intent=session['payment_intent'])
    the_order.has_completed = True
    the_order.save()
    print("Fulfilling order")


def create_order(session):
    print("Creating order")
    customer_email = session['customer_details']['email']
    customer_user = User.objects.get(email=customer_email)
    InternationalOrder(user=customer_user, purchased_amount=session['amount_total'] / 100,
                       payment_intent=session['payment_intent'], has_completed=False).save()


def email_customer_about_failed_payment(session):
    # print(session)
    print("Email customer")
