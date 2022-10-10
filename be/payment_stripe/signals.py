from django.shortcuts import get_object_or_404
from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.db.models.signals import post_save

from payment_stripe.models import InternationalOrder

from ivc_project.email_sender import send_new_email
from ivc_project.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


@receiver(valid_ipn_received)
def payment_notification(sender, **kwargs):
    ipn = sender
    if ipn.payment_status == 'Completed':
        # payment was successful
        order = get_object_or_404(InternationalOrder, id=ipn.invoice)

        if order.purchased_amount == ipn.mc_gross:
            # mark the order as paid
            order.has_completed = True
            order.save()
            # increase balance
            order.user.memberprofile.balance += order.purchased_amount
            order.user.memberprofile.save()



# @receiver(post_save, sender=InternationalOrder)
# def send_email(sender, instance, created, **kwargs):
#     context = {
#         'invoice': instance,
#     }
#     html_body = render_to_string("payment_stripe/inv.html", context)
#     e_subject = "TECVICO"
#     #e_content = "Dear {user}\nHi\nHope you are going well.\nYou paid {cost} at {date}\n{intent} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: payment@tecvico.com\n\nThank you.\n\nBest regards\n\n".format(user = instance.user, cost = instance.purchased_amount, date = instance.date_created, intent = instance.payment_intent)
#     e_content = ""
#     e_destination = instance.user.email
#     msg = EmailMultiAlternatives(subject=e_subject, from_email=EMAIL_HOST_USER,to=[e_destination], body=e_content)
#     msg.attach_alternative(html_body, "text/html")
#     msg.send()
    
    
    