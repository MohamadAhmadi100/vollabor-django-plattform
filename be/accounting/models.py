from time import time
from django.db import models
from workshop.models import Workshop
from research.models import IndustryFormClient
from request.models import BadgeRequest,SupervisorRequest,WorkshopRequest
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect,HttpResponseRedirect,get_object_or_404
from django.urls import reverse
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from datetime import datetime
from workshop.models import Users_Workshops
from payment_stripe.models import *
from django.utils.translation import gettext_lazy as _
# from virtual_event.models import VirtualEvent,VirtualEventMemebers

from xhtml2pdf import pisa


User=get_user_model()

# Create your models here.


service_name = (
    ("UN", 'unknow'),
    ("V", 'virtual-event'),
    ("P", 'project'),
    ("W", 'workshop'),
    ("BR", 'badgerequest'),
    ("SR", 'supervisorrequest'),
    ("WR", 'workshoprequest'),
    
)


class Service(models.Model):
     
     service_name=models.CharField(max_length=100,default='UN',choices=service_name)
     workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE,blank=True,null=True)
     project=models.ForeignKey(IndustryFormClient,on_delete=models.CASCADE,blank=True,null=True)
     badge=models.ForeignKey(BadgeRequest,on_delete=models.CASCADE,blank=True,null=True)
     badgesupervisor=models.ForeignKey(SupervisorRequest,on_delete=models.CASCADE,blank=True,null=True)
     badgeworkshop=models.ForeignKey(WorkshopRequest,on_delete=models.CASCADE,blank=True,null=True)
    #  virtual_event=models.ForeignKey(VirtualEvent,on_delete=models.CASCADE,blank=True,null=True)
     user=models.ForeignKey(User,on_delete=models.CASCADE,null=True)
     balance_value=models.IntegerField()
     action=models.CharField(max_length=200,null=True)


     def __str__(self):
         return f'{self.user.username}-{self.service_name}'



class Invoice(models.Model):
    user_balance=models.IntegerField()
    amount=models.IntegerField()
    discount=models.IntegerField(default=0)
    create_date=models.DateTimeField(auto_now=True)
    service=models.ForeignKey(Service,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    is_paid=models.BooleanField(default=False)
    pay_date=models.DateTimeField(null=True,blank=True)
    fallow_code=models.CharField(max_length=100)
    session_discount=models.CharField(max_length=30, default='0-0',null=True,blank=True)
    session_membership=models.CharField(max_length=30, default='0-0',null=True,blank=True)


    def __str__(self):
        return f'{self.id}-{self.create_date}'




use_status=(
    ('percent','percent'),
    ('real','real')
)
class Discount(models.Model):
    name=models.CharField(max_length=50)
    use_status=models.CharField(max_length=10,default='real',choices=use_status)
    discount_code=models.CharField(max_length=20)
    amount=models.IntegerField()
    max_uses=models.IntegerField(null=True)
    create_date=models.DateTimeField(auto_now=True)
    exp_date=models.DateTimeField(blank=True,null=True)
    uses_count=models.IntegerField(null=True,blank=True)
    is_all=models.BooleanField(default=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    data=models.TextField(null=True,blank=True)
    is_all_project=models.BooleanField(default=False)
    is_all_badge=models.BooleanField(default=False)
    is_all_supervisorrequests=models.BooleanField(default=False)
    is_all_workshoprequest=models.BooleanField(default=False)
    is_all_workshop=models.BooleanField(default=False)


# membership..................................................
membership_type=(
    ('real','real'),
    ('percent','percent')
)

class Membership(models.Model):
    name=models.CharField(max_length=50)
    membership_code=models.CharField(max_length=100)
    created=models.DateTimeField(auto_now=True)
    duration=models.IntegerField()
    amount=models.IntegerField(default=0,blank=True)
    type=models.CharField(max_length=10,choices=membership_type,default='real')
    is_all=models.BooleanField(default=True)
    usabel_number_all=models.IntegerField(default=1,blank=True)
    is_workshop=models.BooleanField(default=False)
    workshop_amount=models.IntegerField(default=0,blank=True)
    usabel_number_workshop=models.IntegerField(default=0,blank=True)
    is_project=models.BooleanField(default=False)
    project_amount=models.IntegerField(default=0,blank=True)
    usabel_number_project=models.IntegerField(default=0,blank=True)
    is_badge_request=models.BooleanField(default=False)
    badge_request_amount=models.IntegerField(default=0,blank=True)
    usabel_number_badge_rquest=models.IntegerField(default=0,blank=True)
    thumbnail=models.ImageField(blank=True)
    icon=models.ImageField(blank=True)

    def __str__(self):
        return self.name


class membership_user(models.Model):
    membership=models.ForeignKey(Membership,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now=True)
    is_active=models.BooleanField(default=False)
    is_pay=models.BooleanField(default=False)
    project_count=models.IntegerField(default=0)
    workshop_count=models.IntegerField(default=0)
    badge_request_count=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

# Financial...................................................
class Agency(models.Model):
    name=models.CharField(max_length=30)
    info=models.TextField(max_length=300)
    location=models.TextField(max_length=300)
    country=models.CharField(max_length=10)
    created=models.DateTimeField(auto_now=True)
    expert=models.ForeignKey(User,on_delete=models.CASCADE)
    input=models.IntegerField(null=True,default=0)
    output=models.IntegerField(null=True,default=0)

    def __str__(self):
        return self.country
    

class CentralRequestPayment(models.Model):
    origin_agency=models.ForeignKey(Agency,on_delete=models.CASCADE,related_name='origin')
    destination_agency=models.ForeignKey(Agency,on_delete=models.CASCADE,related_name='destination')
    amount=models.IntegerField()
    status=models.CharField(max_length=100)
    is_do=models.BooleanField(default=0)
    is_do_time=models.DateTimeField(null=True)
    created=models.DateTimeField(auto_now=True)


class WithdrawalBox(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    amount=models.IntegerField()
    service=models.ForeignKey(Service,on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now=True)
    requested=models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class User_bank_info(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE,unique=True,null=True)
    firstname=models.CharField(max_length=50)
    lastname=models.CharField(max_length=50)
    shaba_acoount=models.CharField(max_length=100)
    account_number=models.CharField(max_length=50)
    card_number=models.CharField(max_length=50)

    def __str__(self):
        return self.user.username


class Request_money(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    bank_info=models.ForeignKey(User_bank_info,on_delete=models.CASCADE)
    amount=models.IntegerField()
    created=models.DateTimeField(auto_now=True)
    is_done=models.BooleanField(default=0)
    position=models.CharField(max_length=30,default='expert',null=True)
    expert_approve=models.BooleanField(default=False,null=True)
    manager_approve=models.BooleanField(default=False,null=True)
    status=models.CharField(max_length=50,null=True,default='expert_decide')
    witdrawalbox=models.ForeignKey(WithdrawalBox,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.user.username

MANAGER_DESC=[
    {'status':'expert_decide','msg':_('Pending for expert decision')},
    {'status':'manager_decide','msg':_('Pending for Your decision')},
    {'status':'Confirm the operation','msg':_('Waiting for the operation to be performed by the expert')},
    {'status':'Complete','msg':_('Done')},

    ]
EXPERT_DESC=[
    {'status':'expert_decide','msg':_('Pending for your decision')},
    {'status':'manager_decide','msg':_('Pending for manager decision')},
    {'status':'Confirm the operation','msg':_('Waiting for the operation to be performed by you')},
    {'status':'Complete','msg':_('Done')},

    ]
CLIENT_DESC=[
    {'status':'expert_decide','msg':_('Pending for expert decision')},
    {'status':'manager_decide','msg':_('Pending for manager decision')},
    {'status':'Confirm the operation','msg':_('Waiting for the operation to be performed by the expert')},
    {'status':'Complete','msg':_('Done')},

    ]






# class AccountingNotif(models.Model):
#     section=models.CharField(max_length=30)
#     number=models.IntegerField()

# Functions...................................................
def html_to_pdf(template_src, context_dict={}):
     template = get_template(template_src)
     html  = template.render(context_dict)
     result = BytesIO()
     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
     if not pdf.err:
         return HttpResponse(result.getvalue(), content_type='application/pdf')
     return None

def PaymentProtocol(request,service_name,object,value,action='create'):
    balance=request.user.memberprofile.balance
    if service_name == 'W':
        service=Service.objects.filter(workshop=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True
    if service_name == 'V':
        service=Service.objects.filter(virtual_event=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True
    elif service_name == 'P':
        service=Service.objects.filter(project=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True
    elif service_name == 'BR':
        service=Service.objects.filter(badge=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True

    elif service_name == 'SR':
        service=Service.objects.filter(badgesupervisor=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True

    elif service_name == 'WR':
        service=Service.objects.filter(badgeworkshop=object,user=request.user,action=action).first()
        if service is None:
            check_invoice=False
        else:
            invoice_search=Invoice.objects.filter(service=service,amount=value,user=request.user).first()
            if invoice_search is None:
                check_invoice=False
            else:
                check_invoice=True


    if check_invoice:
        new_invoice=invoice_search

    else:

        new_service=Service.objects.create(
            service_name=service_name,balance_value=value,user=request.user,action=action
        )

        if service_name == 'W':
            new_service.workshop=object
        elif service_name == 'V':
            new_service.virtual_event=object
        elif service_name == 'P':
            new_service.project=object
        elif service_name == 'BR':
            new_service.badge=object
        elif service_name == 'SR':
            new_service.badgesupervisor=object
        elif service_name == 'WR':
            new_service.badgeworkshop=object
        
        new_service.save()

        new_invoice=Invoice.objects.create(
            user_balance=balance,amount=value,service=new_service,user=request.user,
            fallow_code='',session_discount='0-0',session_membership='0-0'
        )

    # return reverse('accounting:invoice-detail', kwargs={'pk': new_invoice.id})  
    # return redirect(f'accounting/invoice/{new_invoice.id}') 
    return redirect('accounting:invoice-detail',pk=new_invoice.id)       

    
def check_discount_for_reject(request,service_name,object):
    if service_name=='P':
        pay_service=Service.objects.filter(user=request.user,service_name='P',project=object,action='create').first()
        if pay_service is None:
            discount_value=0
        else:
            pay_invoice=Invoice.objects.filter(user=request.user,service=pay_service).first()
            if pay_invoice is None:
                discount_value=0
            else:
                discount_value=pay_invoice.discount
    elif service_name=='W':
        pay_service=Service.objects.filter(user=request.user,service_name='W',workshop=object).first()
        if pay_service is None:
            discount_value=0
        else:
            pay_invoice=Invoice.objects.filter(user=request.user,service=pay_service).first()
            if pay_invoice is None:
                discount_value=0
            else:
                discount_value=pay_invoice.discount
    elif service_name=='BR':
        pay_service=Service.objects.filter(user=request.user,service_name='BR',badge=object).first()
        if pay_service is None:
            discount_value=0
        else:
            pay_invoice=Invoice.objects.filter(user=request.user,service=pay_service).first()
            if pay_invoice is None:
                discount_value=0
            else:
                print(pay_invoice.discount)
                discount_value=pay_invoice.discount
    elif service_name=='SR':
        pay_service=Service.objects.filter(user=request.user,service_name='SR',badgesupervisor=object).first()
        if pay_service is None:
            discount_value=0
        else:
            pay_invoice=Invoice.objects.filter(user=request.user,service=pay_service).first()
            if pay_invoice is None:
                discount_value=0
            else:
                discount_value=pay_invoice.discount
    elif service_name=='WR':
        pay_service=Service.objects.filter(user=request.user,service_name='WR',badgeworkshop=object).first()
        if pay_service is None:
            discount_value=0
        else:
            pay_invoice=Invoice.objects.filter(user=request.user,service=pay_service).first()
            if pay_invoice is None:
                discount_value=0
            else:
                discount_value=pay_invoice.discount
    return discount_value
        

def RejectProtocol(request,service_name,object,value):
    balance=request.user.memberprofile.balance
    new_service=Service.objects.create(
            service_name=service_name,balance_value=value,user=object.user,action='reject'
        )
    if service_name == 'P':
        new_service.project=object
        dsicount_value=check_discount_for_reject(request,'P',object)
        origin_invoice=Invoice.objects.filter(service__project=object,service__action='create').first()
        # object.user.memberprofile.balance+=value - dsicount_value
    elif service_name == 'W':
        new_service.workshop=object
        dsicount_value=check_discount_for_reject(request,'W',object)
        origin_invoice=Invoice.objects.filter(service__workshop=object,service__action='create').first()
        # if object.top_user:
        #     object.user.memberprofile.balance+=value - dsicount_value
        # else:
        #     workshop_user=Users_Workshops.objects.filter(workshop=object)
        #     workshop_user.user.memberprofile.balance+=value - dsicount_value
    elif service_name == 'BR':
        new_service.badge=object
        dsicount_value=check_discount_for_reject(request,'BR',object)
        # origin_invoice=Invoice.objects.filter(service__badgerequest=object,service__action='create').first()
        # object.user.memberprofile.balance+=value - dsicount_value
    elif service_name == 'SR':
        new_service.badgesupervisor=object
        dsicount_value=check_discount_for_reject(request,'SR',object)
        # origin_invoice=Invoice.objects.filter(service__workshop=object,service__action='create').first()
        # object.user.memberprofile.balance+=value - dsicount_value
    elif service_name == 'WR':
        new_service.badgeworkshop=object
        dsicount_value=check_discount_for_reject(request,'WR',object)
        # origin_invoice=Invoice.objects.filter(service__workshop=object,service__action='create').first()
        # object.user.memberprofile.balance+=value - dsicount_value
    new_service.save()
    # new_invoice=Invoice.objects.create(
    #         user_balance=balance,discount=dsicount_value,amount=-value,service=new_service,user=request.user,
    #         fallow_code='TEC-REJECT',is_paid=True,pay_date=datetime.now()
    #     )
    new_withdrawalbox=WithdrawalBox.objects.create(user=request.user,service=new_service,amount=value - dsicount_value)
    origin_agency=get_object_or_404(Payment,invoice=origin_invoice)
    origin_agency=origin_agency.agency
    origin_agency.output=value - dsicount_value
    origin_agency.save
    








