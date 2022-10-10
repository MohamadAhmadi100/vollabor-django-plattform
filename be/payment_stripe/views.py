import uuid
import requests
from django.http import HttpResponse,Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views import View
import stripe
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from coin import param

from django.conf import settings
from decimal import Decimal
from paypal.standard.forms import PayPalPaymentsForm
from django.contrib import messages
from .utils import *
from .forms import PymentForm, PaymentMethodForm
from .models import Payment, Dollar 
from django.utils import timezone
from accounting.models import Invoice
from accounting.views import invoice_pay
from accounting.functions import  check_discount_aftertimes,check_membership_aftertimes,check_amount_discount,check_amount_membership

from dashboard.utilities import user_has_memberprofile

stripe.api_key = settings.STRIPE_PRIVATE_KEY

# You can find your endpoint's secret in your webhook settings
endpoint_secret = 'whsec_e3JfbbPQHt943Mc9qhE4IIDhes074Lgd'


class CreateCheckoutSessionView(View):
    responsibility_fee_VALUE = param.responsibility_fee_value

    def post(self, request, *args, **kwargs):
        coin_quantity = request.POST.get('coin-quantity')
        if request.POST.get('payment_method') == "Stripe":
            if request.get_host() == '127.0.0.1:8000':
                coin_price_id = "price_1JYBleHqDsGa1SRrNx7vtoGQ"
            else:
                coin_price_id = 'price_1JYBnZHqDsGa1SRr8gt8UPLK'
    
            if coin_quantity is not None:
                if request.is_secure():
                    protocol = "https://"
                else:
                    protocol = "http://"

                domain = f"{protocol}{request.get_host()}/international-payment"
                checkout_session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    customer_email=request.user.email,
                    line_items=[
                        {
                            #'price': coin_price_id,  # Value is ID of 'coin' in stripe
                            'quantity': 1,
			                'currency':'usd',
			                'amount':coin_quantity,
			                'name':request.user.first_name,
                        }],

                    mode='payment',
                    success_url=domain + '/success/',
                    cancel_url=domain + '/cancel/',
                )
                print(checkout_session.url)
                return redirect(checkout_session.url, code=303)
        elif request.POST.get('payment_method') == "Paypal":
            return redirect('process_payment', amount=coin_quantity)

    def get(self, request):
        if not user_has_memberprofile(request.user):
            return render(request, 'ivc_website/403.html')

        return render(request, 'payment_stripe/checkout.html', context={
            'responsibility_fee_value': self.responsibility_fee_VALUE,
            'default_value': request.GET.get('fill', 1)
        })



def create_checkout_session_view(request):
    try:
        invoice_id=request.GET['invoice_id']
    except:
        raise Http404
    template_name = 'payment_stripe/checkout.html'
    previously_url=request.META.get('HTTP_REFERER')
    invoice=get_object_or_404(Invoice,pk=invoice_id)
    if Payment.objects.filter(invoice=invoice).exists():
        pay_invoice=Payment.objects.filter(invoice=invoice).first()
        pay_status=pay_invoice.paymented
        if pay_status == 1:
            return redirect('invoice-page',slug=pay_invoice.id_pay)


    #check membership and discount
    if check_discount_aftertimes(request,invoice):
        pass
    else:
        messages.error(request,'Sorry! The code has already been used and you are not allowed to use it longer.')
        return redirect('accounting:invoice-detail', pk=invoice.id)
    if check_membership_aftertimes(request,invoice):
        pass
    else:
        messages.error(request,'Your membership point has been expired.')
        return redirect('accounting:invoice-detail', pk=invoice.id)
    check_amount_membership(invoice)
    check_amount_discount(invoice)
    invoice_discount=int(float(invoice.session_discount.split('-')[1]))+ int(float(invoice.session_membership.split('-')[1]))
    if invoice.amount < invoice_discount:
        amount= 0
    else:
        amount=(invoice.amount - invoice_discount)
    


    if request.method == 'POST':
        form = PymentForm(request.POST, request.FILES)
        if form.is_valid():
            country = form.cleaned_data.get("country")
            gateway = form.cleaned_data.get("gateway")
            previously_url = request.POST.get("id_inv")

            time_now = timezone.now()
            time_now = str(time_now)
            time_now = time_now.split(" ")
            time_id = time_now[0]
            time_now = time_now[1]
            time_now = time_now.split(".")
            time_id = time_id + time_now[0]

            if gateway == 'zarinpal':
                user_id = request.user
                user_id = str(user_id)

                time_id = user_id + time_id

                

                # response = requests.get('http://api.navasan.tech/latest/?api_key=freeEvjUFsaQSG1mgKJvuus7ihMotOlQ')
                # dollar_price = response.json().get('usd')
                # dollar = dollar_price.get('value')
                # dollar = int(dollar + '0')
                
                dollar_obj = Dollar.objects.all().last()
                dollar = dollar_obj.price


                zarinpal_amount = int(amount)
                amount = int(amount) * dollar
                
                gsp=int(amount * 0.05)
                # pst=int(amount * 0.07)
                
                # if gateway == 'stripe':
                #     additional_fee = amount * 0.01
                # else:
                #     additional_fee = amount * 0.02
                    
                total = gsp + amount
                payment_obj=Payment.objects.filter(invoice=invoice).first()
                if not payment_obj:
                    create_payment = Payment.objects.create(
                        user=request.user, id_pay=time_id, country=country, amount=amount, pymeny_method=gateway, 
                        gsp=gsp, total=total, zarinpal_amount=zarinpal_amount,invoice=invoice)
                else: 
                    payment_obj.user=request.user;payment_obj.id_pay=time_id;payment_obj.country=country
                    payment_obj.amount=amount;payment_obj.pymeny_method=gateway; 
                    payment_obj.gsp=gsp;
                    payment_obj.total=total;payment_obj.zarinpal_amount=zarinpal_amount;payment_obj.invoice=invoice
                    payment_obj.save()


            else:

                user_id = request.user
                user_id = str(user_id)

                time_id = user_id + time_id
                
               
                    
                amount = int(amount)
                
                gsp=int(amount * 0.05)
                # pst=int(amount * 0.07)
                
                if gateway == 'stripe':
                    additional_fee = amount * 0.01
                else:
                    additional_fee = amount * 0.02

                
                total = gsp + additional_fee + amount
                payment_obj=Payment.objects.filter(invoice=invoice).first()
                if not payment_obj:
                    create_payment = Payment.objects.create(
                        user=request.user, id_pay=time_id, country=country, amount=amount, pymeny_method=gateway, 
                        gsp=gsp, additional_fee=additional_fee, total=total,invoice=invoice
                        )
                else:
                    payment_obj.user=request.user;payment_obj.id_pay=time_id;payment_obj.country=country
                    payment_obj.amount=amount;payment_obj.pymeny_method=gateway; 
                    payment_obj.gsp=gsp;payment_obj.additional_fee=additional_fee
                    payment_obj.total=total;payment_obj.invoice=invoice
                    payment_obj.save()
                
            obj_payment = Payment.objects.get(id_pay=time_id)
            return redirect("invoice-page", time_id)
    else:
        form = PymentForm
    context={
        'form': form,
        'amount': amount,
        'invoice_id': invoice_id,
       
    }
    return render(request, template_name, context)





def in_voice(request, slug):
    template_name = 'payment_stripe/inv.html'
    obj_pay = get_object_or_404(Payment, id_pay=slug)

     #check membership and discount
    if check_discount_aftertimes(request,obj_pay.invoice):
        pass
    else:
        messages.error(request,'Sorry! The code has already been used and you are not allowed to use it longer.')
        return redirect('accounting:invoice-detail', pk=obj_pay.invoice.id)
    if check_membership_aftertimes(request,obj_pay.invoice):
        pass
    else:
        messages.error(request,'Your membership point has been expired.')
        return redirect('accounting:invoice-detail', pk=obj_pay.invoice.id)
    check_amount_membership(obj_pay.invoice)
    check_amount_discount(obj_pay.invoice)

    if request.method == 'POST':
        if obj_pay.total == 0:
            obj_pay.invoice.is_paid
            obj_pay.paymented += 1
            obj_pay.success_date = timezone.now()
            obj_pay.save()
            invoice_pay(obj_pay.invoice.id)
            return redirect('accounting:invoice-detail', pk=obj_pay.invoice.id)


        form = PaymentMethodForm(request.POST, request.FILES)
        if form.is_valid():
            payment_method = form.cleaned_data.get("payment_method")
            if obj_pay.pymeny_method == 'stripe':
                if request.get_host() == '127.0.0.1:8000':
                    coin_price_id = "price_1JYBleHqDsGa1SRrNx7vtoGQ"
                else:
                    coin_price_id = 'price_1JYBnZHqDsGa1SRr8gt8UPLK'
        
                if obj_pay.amount is not None:
                    if request.is_secure():
                        protocol = "https://"
                    else:
                        protocol = "http://"
                        
                        
                    domain = f"{protocol}{request.get_host()}/international-payment"
                    checkout_session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        customer_email=request.user.email,
                        line_items=[
                            {
                                #'price': coin_price_id,  # Value is ID of 'coin' in stripe
                                'quantity': 1,
    			                'currency':'usd',
    			                'amount':str(obj_pay.total * 100),
    			                'name':request.user.first_name,
                            }],
    
                        mode='payment',
                        success_url=domain + '/success/{}'.format(obj_pay.pk),
                        cancel_url=domain + '/cancel/',
                    )
                    print(checkout_session.url)
                    return redirect(checkout_session.url, code=303)
    host = request.get_host()
    order = InternationalOrder(user=request.user, purchased_amount=float(obj_pay.amount))
    order.save()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(obj_pay.total),
        'item_name': "Tecvico Balance",
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
        'return_url': 'http://{}{}'.format(host,
                                           reverse('success_',)),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('cancel')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    
    context = {
        'invoice': obj_pay,
        'form': form,
    }

    return render(request, template_name, context)


@csrf_exempt
def success(request, pk):
    template_name = 'payment_stripe/inv.html'
    obj_pay = get_object_or_404(Payment, pk=pk)
    payment_url = obj_pay.back_url
    if  request.user == obj_pay.user:
        if obj_pay.paymented == 0:
            obj_pay.paymented = 1
            obj_pay.user.memberprofile.balance += obj_pay.amount
            obj_pay.user.memberprofile.save()
            obj_pay.save()
        
        context = {
            'invoice': obj_pay,
            'payment_url':payment_url
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")
    
@csrf_exempt
def success_(request):
    return render(request, "payment_stripe/success.html")


@csrf_exempt
def cancel(request):
    return render(request, "payment_stripe/cancel.html")


@csrf_exempt
def my_webhook_view(request):
    payload = request.body

    try:
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    except KeyError:
        return HttpResponse(status=400)

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Save an order in your database, marked as 'awaiting payment'
        create_order(session)

        # Check if the order is already paid (e.g., from a card payment)
        #
        # A delayed notification payment will have an `unpaid` status, as
        # you're still waiting for funds to be transferred from the customer's
        # account.
        if session.payment_status == "paid":
            # Fulfill the purchase
            fulfill_order(session)

    elif event['type'] == 'checkout.session.async_payment_succeeded':
        session = event['data']['object']

        # Fulfill the purchase
        fulfill_order(session)

    elif event['type'] == 'checkout.session.async_payment_failed':
        session = event['data']['object']

        # Send an email to the customer asking them to retry their order
        email_customer_about_failed_payment(session)

    # Passed signature verification
    return HttpResponse(status=200)


def process_payment(request, amount):
    host = request.get_host()
    order = InternationalOrder(user=request.user, purchased_amount=float(amount))
    order.save()

    paypal_dict = {
        'business': settings.PAYPAL_RECEIVER_EMAIL,
        'amount': str(amount),
        'item_name': "Tecvico Balance",
        'invoice': str(order.id),
        'currency_code': 'USD',
        'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
        # 'return_url': 'http://{}{}'.format(host,
        #                                   reverse('success',)),
        'cancel_return': 'http://{}{}'.format(host,
                                              reverse('cancel')),
    }

    form = PayPalPaymentsForm(initial=paypal_dict)
    return render(request, 'payment_stripe/paypal.html', {'form': form, 'amount': amount})
