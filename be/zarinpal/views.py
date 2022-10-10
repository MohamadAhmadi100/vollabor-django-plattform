from django.utils import timezone
from payment_stripe.models import Payment 
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
import requests
from django.urls import reverse_lazy
import json
from django.urls import reverse

from paypal.standard.ipn.signals import valid_ipn_received
from django.dispatch import receiver
from django.db.models.signals import post_save

from payment_stripe.models import InternationalOrder

from ivc_project.email_sender import send_new_email
from ivc_project.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from accounting.views import invoice_pay


def request_amount(request, pk):
    obj_pay = get_object_or_404(Payment, pk=pk)
    global amount
    if request.method == 'POST':
        print('pooooooooooooooooooooost')
        print('pooooooooooooooooooooost')
        print('pooooooooooooooooooooost')
        # amount = 11000  # Rial / Required
        amount = obj_pay.total
        print(amount)
        print(amount)
        print(amount)
        print(amount)
        return redirect("zarinpal:request")






def send_request(request, pk):
    obj_pay = get_object_or_404(Payment, pk=pk)
    if obj_pay.total == 0:
            obj_pay.user.memberprofile.balance += obj_pay.zarinpal_amount
            obj_pay.invoice.is_paid
            obj_pay.user.memberprofile.save()
            obj_pay.paymented += 1
            obj_pay.success_date = timezone.now()
            obj_pay.save()
            invoice_pay(obj_pay.invoice.id)
            return redirect('accounting:invoice-detail', pk=obj_pay.invoice.id)

    MERCHANT = '4e843bef-6b60-4cd0-b85a-ae2d89147c9c'
    ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
    ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
    ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

   
    amount = obj_pay.total  # Rial / Required
    description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"  # Required
    # email = 'email@example.com'  # Optional
    # mobile = '09123456789'  # Optional
    # Important: need to edit for realy server.

    # CallbackURL = 'http://127.0.0.1:8000/verify/'

    CallbackURL = str(reverse('zarinpal:verify', args=[obj_pay.pk]))
    CallbackURL = 'http://tecvico.com' + CallbackURL


    req_data = {
        "merchant_id": MERCHANT,
        "amount": amount,
        "callback_url": CallbackURL,
        "description": description,
        "metadata": {"mobile": request.user.memberprofile.phone, "email": request.user.email}
    }

    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
        req_data), headers=req_header)
        
    authority = req.json()['data']['authority']
    if len(req.json()['errors']) == 0:
        obj_pay.merchant=MERCHANT
        obj_pay.save()
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    


def verify(request, pk):
    obj_pay = get_object_or_404(Payment, pk=pk)
    payment_url = obj_pay.back_url

    t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']
    if request.GET.get('Status') == 'OK':
        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": '4e843bef-6b60-4cd0-b85a-ae2d89147c9c',
            "amount": obj_pay.total,
            "authority": t_authority
        }
        req = requests.post(url="https://api.zarinpal.com/pg/v4/payment/verify.json", data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']
            if t_status == 100:

                obj_pay.invoice.is_paid
                obj_pay.paymented += 1
                obj_pay.success_date = timezone.now()
                obj_pay.merchant="4e843bef-6b60-4cd0-b85a-ae2d89147c9c"
                obj_pay.save()

                context = {
                    'invoice': obj_pay,
                    'RefID': str(req.json()['data']['ref_id']),
                    'payment_url':payment_url
                }

                context_email = {
                    'obj_pay': obj_pay,
                    'RefID': str(req.json()['data']['ref_id'])
                }
                html_body = render_to_string("payment_stripe/inv-email.html", context_email)
                e_subject = "TECVICO"
                #e_content = "Dear {user}\nHi\nHope you are going well.\nYou paid {cost} at {date}\n{intent} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: payment@tecvico.com\n\nThank you.\n\nBest regards\n\n".format(user = instance.user, cost = instance.purchased_amount, date = instance.date_created, intent = instance.payment_intent)
                e_content = ""
                e_destination = obj_pay.user.email
                msg = EmailMultiAlternatives(subject=e_subject, from_email=EMAIL_HOST_USER,to=[e_destination], body=e_content)
                msg.attach_alternative(html_body, "text/html")
                msg.send()

                invoice_pay(obj_pay.invoice.id)
                return redirect('accounting:invoice-detail', pk=obj_pay.invoice.id)


                return render(request, 'payment_stripe/inv.html', context)

            elif t_status == 101:
                return HttpResponse('Transaction submitted : ' + str(
                    req.json()['data']['message']
                ))
            else:
                return HttpResponse('Transaction failed.\nStatus: ' + str(
                    req.json()['data']['message']
                ))
        else:
            e_code = req.json()['errors']['code']
            e_message = req.json()['errors']['message']
            return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return HttpResponse('Transaction failed or canceled by user')

# def success(request, pk)