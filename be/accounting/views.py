import os
import json
import xlwt
import random
from .forms import *
from .models import *
from time import time
from users.models import Role
from .models import html_to_pdf
from django.utils import timezone
from  ivc_project import settings
from django.contrib import messages
from django.http import HttpResponse
from django.views.generic import View,CreateView,ListView,UpdateView
from request.models import BadgeRequest
from payment_stripe.models import Payment
from dashboard.models import Notification
from datetime import date,datetime,timedelta
from django.http import Http404, JsonResponse
from research.models import IndustryFormClient
from ivc_project.email_sender import send_new_email
from workshop.models import Workshop,Users_Workshops
from django.core.files.storage import default_storage
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect
from .functions import *
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from .mixins import *


    

# ........................................................................
#import pyautogui                                                        |
#from django.conf import settings                                        |
#  def screenshot(request):                                              |
#     ss = pyautogui.screenshot()                                        |
#     img = f'myimg{random.randint(1000,9999)}.png'                      |
#     ss.save(f'{settings.MEDIA_ROOT}/10.png')                           |
#     messages.success(request,'screenshot has been taken')              |
#     return redirect('/dashboard')                                      |
# ........................................................................

class GeneratePdf(View):
     def get(self, request, *args, **kwargs):
        invoive=Invoice.objects.get(id=self.kwargs.get('pk'))
         
        # getting the template
        pdf = html_to_pdf('invoice-detail.html',{'invoce':invoive})
         
         # rendering the template
        return HttpResponse(pdf, content_type='application/pdf')
  

# Create your views here.



            # .........Ajax..........
@login_required
def generate_code(request):
    if request.method=="POST":
        code_chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        code = ''
        for i in range(0,7):
            slice_start = random.randint(0, len(code_chars) - 1)
            code += code_chars[slice_start: slice_start + 1]
        response=({'code':f'TEC{code}'})
    return JsonResponse(response)

# Panel.......................................................................................

@login_required
def accounting_dashboard(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='accounting-panel.html'
        context={
            'roles':Role.objects.filter(user=request.user)
        }

        return render(request,template_name,context)
    # else:
    #     return HttpResponseRedirect(request.path_info)


# Invoice.......................................................................................

def invoice_detail(request,pk):
    template_name='invoice/invoice-detail.html'
    current_invoice=get_object_or_404(Invoice,id=pk)
    discount_code=current_invoice.session_discount.split('-')[0]
    payment=Payment.objects.filter(invoice=current_invoice).first()
    if payment:
        current_invoice.payment=payment

    #check membership and discount
    if check_discount_aftertimes(request,current_invoice):
        pass
    else:
        messages.error(request,'Sorry! The code has already been used and you are not allowed to use it longer.')
        return redirect('accounting:invoice-detail', pk=current_invoice.id)
    if check_membership_aftertimes(request,current_invoice):
        pass
    else:
        messages.error(request,'Your membership point has been expired.')
        return redirect('accounting:invoice-detail', pk=current_invoice.id)
    
    check_amount_membership(current_invoice)
    check_amount_discount(current_invoice)


    session_discount_amount=int(float(current_invoice.session_discount.split('-')[1]))
    is_membership_code=(lambda data:True if (len(data)>2) else False)(current_invoice.session_membership.split('-')[0])
    session_membership_amount=int(float(current_invoice.session_membership.split('-')[1]))
    if current_invoice.amount < session_discount_amount + session_membership_amount:
        amount_with_discount=0
        session_discount=current_invoice.amount
    else:
        amount_with_discount=current_invoice.amount - session_discount_amount - session_membership_amount
        session_discount=session_discount_amount - session_membership_amount
    membership=membership_user.objects.filter(user=request.user,is_active=True,is_pay=True).first()
    membership_show=(lambda data:False if data == 0 else True)(get_amount_membership(request,current_invoice.service.service_name,current_invoice.amount))
    context={
        'invoice':current_invoice,
        'amount_with_discount':amount_with_discount,
        'session_discount':session_discount,
        'is_membership_code':is_membership_code,
        'membership':membership,
        'membership_show':membership_show
    }
    return render(request,template_name,context)

@login_required
def remove_invoice(request,pk):
    select_invoice=Invoice.objects.get(id=pk,user=request.user)
    select_service=select_invoice.service
    if select_service.service_name == 'P':
        pass
    elif select_service.service_name == 'W':
        if select_service.action == 'create':
            workshop_object=select_service.workshop
            workshop_object.status='trash'
            workshop_object.save()
            select_invoice.delete()
            select_service.delete()
        elif select_service.action == 'buy':
            workshop_object=select_service.workshop
            userworkshop=Users_Workshops.objects.filter(user=request.user,workshop=workshop_object).first()
            userworkshop.delete()
            select_invoice.delete()
            select_service.delete()
    elif select_service.service_name == 'BR':
        if select_service.action == 'request':
            badge_request=select_service.badge
            badge_request.status='trash'
            badge_request.save()
            select_invoice.delete()
            select_service.delete()
    elif select_service.service_name == 'SR':
        if select_service.action == 'request':
            supervisor_request=select_service.badgesupervisor
            supervisor_request.status='trash'
            supervisor_request.save()
            select_invoice.delete()
            select_service.delete()
    elif select_service.service_name == 'WR':
        if select_service.action == 'request':
            workshop_request=select_service.badgeworkshop
            workshop_request.status='trash'
            workshop_request.save()
            select_invoice.delete()
            select_service.delete()
    messages.error(request,'Your invoice has been deleted intentionally.')
    return redirect('/dashboard')
 



# Discount.......................................................................................

@login_required
def create_discount(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='discounting/create-discount.html'
        allprojects=IndustryFormClient.objects.all()
        allworkshop=Workshop.objects.all()
        allbadges=BadgeRequest.objects.all()

        if request.method=="POST":
            name=request.POST.get('name')
            use_status=request.POST.get('use_status')
            discount_code=request.POST.get('discount_code')
            amount=request.POST.get('amount')
            max_uses=request.POST.get('max_uses')
            exp_date=request.POST.get('exp_date')
            is_all=request.POST.get('is_all')
            is_all_project=request.POST.get('is_all_project')
            is_all_badge=request.POST.get('is_all_badge')
            is_all_workshop=request.POST.get('is_all_workshop')
            is_all_workshoprequest=request.POST.get('is_all_workshoprequest')
            is_all_supervisorrequests=request.POST.get('is_all_supervisorrequest')
            project_input_list=request.POST.get('project_input_list')
            workshop_input_list=request.POST.get('workshop_input_list')
            data={
                'project':project_input_list,
                'workshop':workshop_input_list,

            }
            data=json.dumps(data)

            new_coupon=Discount.objects.create(
                name=name,use_status=use_status,discount_code=discount_code,amount=amount,max_uses=max_uses,exp_date=exp_date,
                is_all=is_all,is_all_project=is_all_project,is_all_badge=is_all_badge,is_all_workshop=is_all_workshop,
                is_all_workshoprequest=is_all_workshoprequest,is_all_supervisorrequests=is_all_supervisorrequests,data=data,
                user=request.user,uses_count=0
            )
            messages.success(request,'Your discount code has been created successfully.')

        context={
            'projects':allprojects,
            'workshops':allworkshop,
            'badges':allbadges,
            'roles':Role.objects.filter(user=request.user)

        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)


@login_required
def list_discount(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='discounting/discount-list.html'
        discounts=Discount.objects.all()
        discountproject=[]
        discountworkshop=[]
        for discount in discounts:
            od={}      
            datas=json.loads(discount.data)
            plist=datas['project'].split(',')
            od['dis']=discount.id
            od['plist']=plist
            discountproject.append(od)

        for discount in discounts:
            od={}      
            datas=json.loads(discount.data)
            plist=datas['workshop'].split(',')
            od['dis']=discount.id
            od['plist']=plist
            discountworkshop.append(od)


        if request.method=="POST":
            object_id=request.POST.get('object_id')
            delete_discount=Discount.objects.filter(id=object_id).first()
            delete_discount.delete()
            return redirect('accounting:list-discount')
        context={
            'discounts':discounts,
            'discountproject':discountproject,
            'discountworkshop':discountworkshop,
            'projects':IndustryFormClient.objects.all(),
            'workshop':Workshop.objects.all(),
            'roles':Role.objects.filter(user=request.user)
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)


@login_required
def check_discount(request):
    template_name='invoice/invoice-detail.html'
    if request.method=='POST':
        invoice_id=request.POST.get('invoice_id')
        discount_code=request.POST.get('discount_code')
        discount=Discount.objects.filter(discount_code=discount_code).first()
        invoice=Invoice.objects.get(id=int(invoice_id),user=request.user)
        if discount is None:
            response=({'msg':'Sorry!Your code is invalid','amount':0})
        else:
            service_name=invoice.service.service_name
            data=json.loads(discount.data)
            projectslist=data['project'].split(',')
            workshopslist=data['workshop'].split(',')
            if discount.use_status=='percent':
                discount_amount=(discount.amount/100)*invoice.amount
            else:
                discount_amount=discount.amount
            if discount is None:
                response=({'msg':'Sorry! Your code is invalid','amount':0})
            else:
                # selectservice=invoice.service.service_name
                # exp_date=discount.exp_date
                # print(exp_date.timetuple())
                # print(datetime.datetime(exp_date.timetuple()))
                # print(datetime.datetime.now())
                # check expire date
                if True :
                    # check use_count
                    if discount.uses_count < discount.max_uses:

                        # check code is general
                        if discount.is_all:
                            response=({'msg':'The code is valid','amount':discount_amount})

                        else:
                            # check code is for projects
                            if invoice.service.service_name=='P':
                                if discount.is_all_project:
                                    response=({'msg':'The code is valid','amount':discount_amount})
                                else:
                                    if projectslist[0]=='':
                                        response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})
                                    else:
                                        response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})
                                    for p in projectslist:
                                        if int(p)==invoice.service.project.id:
                                            response=({'msg':'The code is valid','amount':discount_amount})
                                        else:
                                            pass

                            # check code is for workshop
                            elif invoice.service.service_name=='W':                           
                                if discount.is_all_workshop:
                                    response=({'msg':'The code is valid','amount':discount_amount})
                                else:
                                    if workshopslist[0]=='':
                                        response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})
                                    else:
                                        response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})
                                        for w in workshopslist:
                                            if int(w)==invoice.service.workshop.id:
                                                response=({'msg':'The code is valid','amount':discount_amount})
                                            else:
                                                pass


                            # check code is for badgerequest
                            elif invoice.service.service_name=='BR':
                                if discount.is_all_badge:
                                    response=({'msg':'The code is valid','amount':discount_amount})
                                else:
                                    response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})
 
                        
                            # check code is for supervisorrequest
                            elif invoice.service.service_name=='SR':
                                if discount.is_all_supervisorrequests:
                                    response=({'msg':'The code is valid','amount':discount_amount})
                                else:
                                    response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})

                            # check code is for workshoprequest
                            elif invoice.service.service_name=='WR':
                                if discount.is_all_workshoprequest:
                                    response=({'msg':'The code is valid','amount':discount_amount})
                                else:
                                    response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer','amount':0})

                        

                        # return JsonResponse(response)
                    else:
                        response=({'msg':'Sorry! The code has already been used and you are not allowed to use it longer.','amount':0})
                    # return JsonResponse(response)
                else:
                    response=({'msg':'Sorry! The code has been expired.'})

                # return JsonResponse(response)
        invoice.session_discount=f'{discount_code}-{response["amount"]}'
        invoice.save()
    context={
        'invoice':invoice,
        'amount_with_discount': invoice.amount -  int(float(response["amount"])),
        'msg':response['msg'],
        'session_discount':int(float(response["amount"])),
        'discount_code':discount_code
    }
    if 'Sorry' in response['msg']:
        # messages.error(request,response['msg'])
        pass
    else:
        messages.success(request,response['msg'])
    return redirect(f'/accounting/invoice/{invoice.id}')

# Reporting.......................................................................................

@login_required
def reporting_balance(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True:
        template_name='reporting/reporting.html'
        badge_request={}
        supervisor_request={}
        workshop_request={}
        projects={}
        workshops={}

        if request.method == "POST":
            # Recent history
            section_date=request.POST.get('section-date')
            start_date=request.POST.get('start_date')
            end_date=request.POST.get('end_date')
            # Type
            only_pay=request.POST.get('only_pay')
            only_reject=request.POST.get('only_reject')
            # Including	
            all_projects=request.POST.get('all_projects')
            all_workshops=request.POST.get('all_workshops')
            # All requests	
            badge_request=request.POST.get('badge_request')
            supervisor_request=request.POST.get('supervisor_request')
            workshop_request=request.POST.get('workshop_request')
            # Specifically included	
            workshop_list=[int(w) for w in request.POST.get('workshop_list').split(',')]
            project_list=[int(p) for p in request.POST.get('project_list').split(',')]
            # User list
            user_list=[int(p) for p in request.POST.get('user_list').split(',')]

            #users
            if user_list[0] == False:
                filter_user='all'
            else:
                users=User.objects.filter(id__in=user_list)
                filter_user='list'

            # datetime
            if start_date is '' or end_date is '':
                if section_date == 'last-day':
                    days=24
                    time_threshold = datetime.now(timezone.utc) - timedelta(hours=days)

                elif section_date == 'last-week':
                    days=7*24
                    time_threshold = datetime.now(timezone.utc) - timedelta(hours=days)
                elif section_date == 'last-month':
                    days=30*24
                    time_threshold = datetime.now(timezone.utc) - timedelta(hours=days)
            else:
                time_threshold=get_days(start_date,end_date)
         
            # Payment
            if int(only_reject) == False:
                if  int(only_pay) == False:
                    pay_action='all'
                else:
                    pay_action='pay'
            else:
                if int(only_pay) == False:
                    pay_action='reject'
                else:
                    pay_action='all'



            # Requests
            if int(badge_request) == False:
                badge_request={}
            else:
                service=select_service_for_report_filter(pay_action,'BR')
                if filter_user == 'all':
                    badge_request=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                else:
                    badge_request=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)

            if int(supervisor_request) == False:
                supervisor_request={}
            else:
                service=select_service_for_report_filter(pay_action,'SR')
                if filter_user == 'all':
                    supervisor_request=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)

                else:
                    supervisor_request=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)

            if int(workshop_request) == False:
                workshop_request={}
            else:
                service=select_service_for_report_filter(pay_action,'WR')
                if filter_user == 'all':
                    workshop_request=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                else:
                    workshop_request=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)




            # projects
            if int(all_projects) == False:
                if(project_list[0] == False):
                    projects={}
                else:
                    
                    projects=IndustryFormClient.objects.filter(id__in=project_list)
                    service=select_service_for_report_filter(pay_action,'P',projects)
                    if filter_user == 'all':
                        projects=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                    else:
                        projects=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)
            else:
                service=select_service_for_report_filter(pay_action,'P')
                if filter_user == 'all':
                    projects=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                else:
                    projects=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)

            # workshops
            if int(all_workshops) == False:
                if(workshop_list[0] == False):
                    workshops={}
                else:
                    workshops=Workshop.objects.filter(id__in=workshop_list)
                    service=select_service_for_report_filter(pay_action,'W',workshops)
                    if filter_user == 'all':
                        workshops=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                    else:
                        workshops=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)
            else:
                service=select_service_for_report_filter(pay_action,'W')
                if filter_user == 'all':
                    workshops=Invoice.objects.filter(service__in=service,is_paid=True,pay_date__gt=time_threshold)
                else:
                    workshops=Invoice.objects.filter(user__in=users,service__in=service,is_paid=True,pay_date__gt=time_threshold)
            
            

        context={
            "workshops":Workshop.objects.all(),
            "projects":IndustryFormClient.objects.all(),
            "users":User.objects.all(),
            'f_projects':projects,
            'f_badge_request':badge_request,
            'f_supervisor_request':supervisor_request,
            'f_workshop_request':workshop_request,
            'f_workshops':workshops,
            'roles':Role.objects.filter(user=request.user)
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)




def reporting_zarinpal(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True:
        template_name='reporting/zarinpal-reporting.html'
        invoices={}
        if request.method == "POST":
             invoices=filter_payment(request,'zarinpal')         
        context={
            "invoices":invoices,
            "users":User.objects.all(),
            'roles':Role.objects.filter(user=request.user)
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)



def reporting_strip(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True:
        template_name='reporting/strip-reporting.html'
        invoices={}
        if request.method == "POST":
             invoices=filter_payment(request,'stripe')         
        context={
            "invoices":invoices,
            "users":User.objects.all(),
            'roles':Role.objects.filter(user=request.user)
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)



def reporting_paypal(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True:
        template_name='reporting/paypal-reporting.html'
        invoices={}
        if request.method == "POST":
             invoices=filter_payment(request,'paypal')         
        context={
            "invoices":invoices,
            "users":User.objects.all(),
            'roles':Role.objects.filter(user=request.user)
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)
    


def create_exel(request):
    if request.method == "POST":
        ids=request.POST.get('ids')
        if len(ids) == 0:
            messages.error(request,'No data already existed to create an exell file.')
            return redirect(request.META.get('HTTP_REFERER'))
        else:
            if 'balance' in request.META.get('HTTP_REFERER'):
                response=export_invoice_xls(request,ids)
            else:
               response=export_payment_xls(request,ids)       
            return response



# Membership.......................................................................................

def membership_check(request):
    if request.method == "POST":
        membership_id=request.POST.get('membership_id')
        invoice_id=request.POST.get('invoice_id')
        action=request.POST.get('action')
        invoice=Invoice.objects.filter(id=invoice_id,user=request.user).first()
        membership=membership_user.objects.filter(id=membership_id,user=request.user).first()
        if int(action) == 0 :
            invoice.session_membership='0-0'
            invoice.save()
            messages.error(request,'Yoy are not allowed to use your membership point to buy the product.')
        else:  
            membership_discount_amount=get_amount_membership(request,invoice.service.service_name,invoice.amount)
            if membership_discount_amount == 0:
                messages.error(request,'Your membership point has been run out.')
            else:
                invoice.session_membership=f'{membership.membership.membership_code}-{membership_discount_amount}'
                invoice.save()
                messages.success(request,'Your membership point has been applied successfully.')
    response=({
        'msg':True,
    })
    return JsonResponse(response)


@login_required
def create_membership(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='membership/create.html'
        images = os.listdir('media/membership/icons')
        thumbnails = os.listdir('media/membership/thumbnails')

        if request.method=="POST" or request.FILES :
            name=request.POST.get('name')
            membership_code=request.POST.get('membership_code')
            duration=request.POST.get('duration')
            amount=request.POST.get('amount')
            type=request.POST.get('type')
            is_all=request.POST.get('is_all')
            usabel_number_all=request.POST.get('usabel_number_all')
            is_workshop=request.POST.get('is_workshop')
            workshop_amount=request.POST.get('workshop_amount')
            usabel_number_workshop=request.POST.get('usabel_number_workshop')
            is_project=request.POST.get('is_project')
            project_amount=request.POST.get('project_amount')
            usabel_number_project=request.POST.get('usabel_number_project')
            is_badge_request=request.POST.get('is_badge_request')
            badge_request_amount=request.POST.get('badgerequest_amount_amount')
            usabel_number_badge_rquest=request.POST.get('usabel_number_badge_rquest')
            icon=request.POST.get('membership_image')
            thumbnail=request.POST.get('membership_thumbnail')
            # upload_image=request.FILES['upload_image']
            # base_name=os.path.basename(upload_image)
            # name,ext=os.path.split(base_name)
            # return HttpResponse(ext)
            # print(upload_image)
            # print(upload_image)
            # print(upload_image)
            # if upload_image is '':
            #     thumbnail=thumbnail
            # else:
            #     thumbnail=upload_image

            new_membership=Membership.objects.create(
                name=name,membership_code=membership_code,duration=duration,type=type,is_all=is_all,usabel_number_all=usabel_number_all,
                is_workshop=is_workshop,usabel_number_workshop=usabel_number_workshop,is_project=is_project,usabel_number_project=usabel_number_project,
                is_badge_request=is_badge_request,usabel_number_badge_rquest=usabel_number_badge_rquest,icon=icon,thumbnail=thumbnail,workshop_amount=workshop_amount,
                project_amount=project_amount,badge_request_amount=badge_request_amount,amount=amount
            )
            messages.success(request,'You created a membership category successfully.')
        context={
                'images':images,
                'thumbnails':thumbnails
                }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)



@login_required
def list_membership(request):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='membership/membership-list.html'
        memberships=Membership.objects.all()


        if request.method=="POST":
                object_id=request.POST.get('object_id')
                delete_membership=Membership.objects.filter(id=object_id).first()
                delete_membership.delete()
                messages.error(request,'The membership category has been deleted.')
                return redirect('accounting:list-membership')


        context={
            'memberships':memberships
        }

        return render (request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)

@login_required
def edit_membership(request,pk):
    manager,expert=check_role(request)
    if request.user.is_superuser == True or manager==True or expert == True:
        template_name='membership/edit.html'
        membership=get_object_or_404(Membership,id=pk)
        images = os.listdir('media/membership/icons')
        thumbnails = os.listdir('media/membership/thumbnails')
        if request.method=="POST":
            membership.name=request.POST.get('name')
            membership.membership_code=request.POST.get('membership_code')
            membership.duration=request.POST.get('duration')
            membership.amount=request.POST.get('amount')
            membership.type=request.POST.get('type')
            membership.is_all=request.POST.get('is_all')
            membership.usabel_number_all=request.POST.get('usabel_number_all')
            membership.is_workshop=request.POST.get('is_workshop')
            membership.workshop_amount=request.POST.get('workshop_amount')
            membership.usabel_number_workshop=request.POST.get('usabel_number_workshop')
            membership.is_project=request.POST.get('is_project')
            membership.project_amount=request.POST.get('project_amount')
            membership.usabel_number_project=request.POST.get('usabel_number_project')
            membership.is_badge_request=request.POST.get('is_badge_request')
            membership.badge_request_amount=request.POST.get('badgerequest_amount_amount')
            membership.usabel_number_badge_rquest=request.POST.get('usabel_number_badge_rquest')
            membership.icon=request.POST.get('membership_image')
            membership.thumbnail=request.POST.get('membership_thumbnail')
            membership.save()
            messages.success(request,'You modified the membership category successfully.')

        context={
            'membership':membership,
            'images':images,
            'thumbnails':thumbnails
        }
        return render(request,template_name,context)
    else:
        return HttpResponseRedirect(request.path_info)



# Financial.......................................................................................

class CompleteBankInfoView(View):
    template_name='financial/request-money.html'
    def get(self,request):
        bank_info=User_bank_info.objects.filter(user=request.user).first() 
        if bank_info:
            return redirect('request-money')
        else:
            form=SelectCountry()
            context={'form':form,}
            return render(request,self.template_name,context)

    def post(self,request):
        country=request.POST.get('country') 
        if country == 'iran':
            return redirect('accounting:IR-bank-info-submited')
        else:
            form="EMPTY"
            context={'form':form,}
            return render(request,self.template_name,context)

class IR_bank_info_submited(View):
    template_name='financial/bank-info-submited.html'
    def get(self,request):
        if request.GET.get('edit') == 'true':
            form=BankInfoForm(instance=User_bank_info.objects.filter(user=request.user).first())
        else:
            form=BankInfoForm()
        context={'form':form}
        return render(request,self.template_name,context)
    def post(self,request):
        firstname=request.POST.get('firstname')
        lastname=request.POST.get('lastname')
        shaba_acoount=request.POST.get('shaba_acoount')
        account_number=request.POST.get('account_number')
        card_number=request.POST.get('card_number')
        bankinfo=User_bank_info.objects.filter(user=request.user).first()
        if bankinfo:
            bankinfo.firstname=firstname
            bankinfo.lastname=lastname
            bankinfo.shaba_acoount=shaba_acoount
            bankinfo.account_number=account_number
            bankinfo.card_number=card_number
        else:
            bankinfo=User_bank_info.objects.create(firstname=firstname,lastname=lastname,
            shaba_acoount=shaba_acoount,account_number=account_number,card_number=card_number,
            )
            bankinfo.user=request.user
        bankinfo.save()
        return redirect('accounting:request-money')

class request_money(View):
    template_name='financial/request-money.html'
    def get(self,request):
        # bank_info=get_object_or_404(User_bank_info,user=request.user)
        bank_info=User_bank_info.objects.filter(user=request.user).first()
        if bank_info:
            witdrawalbox=WithdrawalBox.objects.filter(user=request.user,requested=False).order_by('-created')
            witdrawalbox_value=0
            for w in witdrawalbox:
                witdrawalbox_value+=w.amount
            context={
            'info':bank_info,
            'withdrawals':witdrawalbox,
            'witdrawalbox_value':witdrawalbox_value
            }
            return render(request,self.template_name,context)

        else:
            return redirect('accounting:bank-info')
    
    def post(self,request):
        withdrawal_id=request.POST.get('id')
        withdrawalbox=get_object_or_404(WithdrawalBox,pk=withdrawal_id)
        withdrawalbox.requested=True
        withdrawalbox.save()
        bank_info=get_object_or_404(User_bank_info,user=request.user)
        Request_money.objects.create(user=request.user,witdrawalbox=withdrawalbox,bank_info=bank_info,amount=withdrawalbox.amount)
        messages.success(request,'Your request has been sent')
        return redirect('accounting:request-money')


@login_required
def submit_request(request):
    if request.method == 'POST':
        amount=request.POST.get('amount')
        if int(amount) > request.user.memberprofile.balance:
            messages.error(request,'The requested amount is more than your balance.')          
            return redirect('accounting:request-money')
        else:
            bank_info=get_object_or_404(User_bank_info,id=request.POST.get('bank_info'))
            requested=Request_money.objects.create(user=request.user,bank_info=bank_info,amount=amount,)
            request.user.memberprofile.balance -= int(amount)
            request.user.memberprofile.save()
            messages.success(request,'Your request has been successfully registered.')
            return redirect('accounting:request-money')

@login_required
def financial_page(request):
    template_name='financial/financial.html'
    if request.GET.get('filter') == 'Balance' or request.GET.get('filter') == None:
        datas=Invoice.objects.filter(user=request.user)
    elif request.GET.get('filter') == 'Request':
        datas=Request_money.objects.filter(user=request.user)

    elif request.GET.get('filter') == 'Financial':
        datas=Payment.objects.filter(paymented=True,user=request.user)

    context={
        'datas':datas
        }
    

    
    return render(request,template_name,context)

class RequestListView(View):
    template_name='financial/request_money_list.html'
    
    def get(self,request):
        manager,expert=check_role(request)
        if manager == True:
            context={
                "requests":Request_money.objects.filter().order_by('-created'),
                'status':MANAGER_DESC,
                'role':'manager'
                }
        elif expert == True:
            context={
                "requests":Request_money.objects.filter(position__in=['expert','Complete']).order_by('-created'),
                'status':EXPERT_DESC,
                'role':'expert'
                }
        else:
            context={}
        return render(request,self.template_name,context)
    
    def post(self,request):
        id=request.POST.get('id')
        request_money=Request_money.objects.filter(id=int(id)).first()
        if request.POST.get('action'):
            if request.POST.get('action') == 'Approve':
                request_money.manager_approve=True
                request_money.position='expert'
                request_money.status='Confirm the operation'
                request_money.save()
                messages.success(request,'The request was approved')
            elif request.POST.get('action') == 'Complete':
                request_money.is_done=True
                request_money.position='Complete'
                request_money.status='Complete'
                request_money.save()
                messages.success(request,'The request was completed')

        else:
            request_money.expert_approve=True
            request_money.position='manager'
            request_money.status='manager_decide'
            request_money.save()
            messages.success(request,'Request has been send to manager')
    

    
        
        return redirect('accounting:request-list')





#Agency...............................

#List & Delete
class AgencyListview(ManagerMixin,View):
    permission_required=''
    permission_denied_message="Access Denaid"
    login_url='/accounting'
    def get(self,request):
        template_name='financial/agency_list.html'
        context={'object_list':Agency.objects.all()}
        return render(request,template_name,context)
    def post(self,request):
        id=request.POST.get('id')
        agency=Agency.objects.get(pk=id).delete()
        messages.error(request,'The agency deleted')
        return redirect('accounting:agency-list')
#Create
class AgencyCreateView(ManagerMixin,SuccessMessageMixin,CreateView):
    permission_required=''
    permission_denied_message="Access Denaid"
    login_url='/accounting'
    model=Agency
    template_name='financial/create_agency.html'
    form_class=CreateAgencyForm
    success_message='The agency created'
    success_url = reverse_lazy('accounting:agency-list')
#Update
class AgencyEditView(ManagerMixin,SuccessMessageMixin,UpdateView):
    permission_required=''
    permission_denied_message="Access Denaid"
    login_url='/accounting'
    model=Agency
    template_name='financial/create_agency.html'
    form_class=CreateAgencyForm
    success_message='The agency updated'
    success_url = reverse_lazy('accounting:agency-list')


class AgencyManageView(ManagerMixin,ListView):
    permission_required=''
    permission_denied_message="Access Denaid"
    login_url='/accounting'
    model=Agency
    template_name='financial/agency_manage_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for obj in context['object_list']:
            obj.total=obj.input - obj.output
            obj.open_request=CentralRequestPayment.objects.filter(origin_agency=obj,is_do=False).count()
        context['agency']=Agency.objects.all()
        return context


    def post(self,request):
        origin_agency_id=request.POST.get('origin_agency')
        destination_agency=get_object_or_404(Agency,country=request.POST.get('destination_agency'))
        origin_agency=get_object_or_404(Agency,pk=origin_agency_id)
        amount=request.POST.get('amount')
        CentralRequestPayment.objects.create(
            amount=amount,destination_agency=destination_agency,origin_agency=origin_agency,
            status="send_request")
        messages.success(request,'Your request sent to agency')

        ''''
        to do email and notification for destination expert
        '''

        return redirect('accounting:agency-manage')
    