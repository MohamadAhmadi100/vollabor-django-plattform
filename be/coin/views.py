from django.http import HttpResponse
from django.shortcuts import redirect

from coin.util import get_user_email_and_phone
from .models import Order
# from suds import Client

# set the merchant id in  MERCHANT
# MERCHANT = 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX'
# client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')


# def send_request(request, price):
#     Order(user=request.user, price=price).save()  # creates a new order which is not verified (is_verified = False)

#     user_email, user_phone = get_user_email_and_phone(request)

#     description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
#     callback_URL = f"{request.get_host()}/coin/verify/"

#     result = client.service.PaymentRequest(MERCHANT,
#                                            price,
#                                            description,
#                                            user_email,
#                                            user_phone,
#                                            callback_URL)
#     if result.Status == 100:
#         return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
#     else:
#         return HttpResponse('Error code: ' + str(result.Status))


# def verify(request):
#     if request.GET.get('Status') == 'OK':
#         last_order_price = Order.objects.filter(user=request.user).last().price

#         result = client.service.PaymentVerification(MERCHANT,
#                                                     request.GET['Authority'],
#                                                     last_order_price)
#         if result.Status == 100:
#             last_order = Order.objects.filter(user=request.user).last()
#             last_order.is_verified = True
#             last_order.save()
#             return HttpResponse('Transaction success')
#         elif result.Status == 101:
#             return HttpResponse('Transaction submitted : ' + str(result.Status))
#         else:
#             return HttpResponse('Transaction failed' + str(result.Status))
#     else:
#         return HttpResponse('Transaction failed or canceled by user')
