import json
import xlwt
import random
from .forms import *
from .models import *
from users.models import Role
from .models import html_to_pdf
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from payment_stripe.models import Payment
from datetime import date,datetime,timedelta
from django.shortcuts import get_object_or_404
from dashboard.models import Notification
from workshop.views import send_notif_email
from request.views import sendemailnotifbadgerequest,sendemailnotifsupervisorrequest,sendemailnotifworkshoprequest
from research.views import again_pay_project, agian_resubmit_supervisor, again_supervisor_send_contract, again_applyproject#,pay_contract_client,pay_proposal_supervisor
# from virtual_event.models import VirtualEventMemebers

# Functions.......................................................................................


def check_role(request):
    for role in Role.objects.filter(user=request.user):
        if role.position == 'accounting manager' :
            manager=True
            expert=False
            break
        elif role.position == 'accounting expert':
            expert=True
            manager=False
            break
        else:
            manager=False
            expert=False
    return manager,expert

def select_service_for_report_filter(pay_action,service_name,list=[]):
    if pay_action == 'all':
        if service_name == 'P':
            if list==[]:
                service=Service.objects.filter(service_name=service_name)
            else:
                service=Service.objects.filter(service_name=service_name,project__in=list)
        elif service_name == 'W':
            if list ==[]:
                service=Service.objects.filter(service_name=service_name)
            else:
                service=Service.objects.filter(service_name=service_name,workshop__in=list)
        else:
            service=Service.objects.filter(service_name=service_name)
    elif pay_action == 'pay':
        if service_name == 'P':
            if list == []:
                service=Service.objects.filter(service_name=service_name,project__in=list).exclude(action='reject')
            else:
                service=Service.objects.filter(service_name=service_name).exclude(action='reject')
        elif service_name == 'W':
            if list == []:
                service=Service.objects.filter(service_name=service_name).exclude(action='reject')
            else:
                service=Service.objects.filter(service_name=service_name,workshop__in=list).exclude(action='reject')
        else:
            service=Service.objects.filter(service_name=service_name).exclude(action='reject')
    elif pay_action == 'reject':
        if service_name == 'P':
            if list ==[]:
                service=Service.objects.filter(service_name=service_name,action='reject')
            else:
                service=Service.objects.filter(service_name=service_name,project__in=list,action='reject')
        elif service_name == 'W':
            if list ==[]:
                service=Service.objects.filter(service_name=service_name,action='reject')
            else:
                service=Service.objects.filter(service_name=service_name,workshop__in=list,action='reject')
        else:
            service=Service.objects.filter(service_name=service_name,action='reject')
    return service

def export_invoice_xls(request,ids):
        ids=ids.split(',')
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Invoices.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Invoice Data') # this will make a sheet named Users Data

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['Invoice number', 'User', 'Reason','Discount','Amount','Pay date' ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

        invoices=Invoice.objects.filter(id__in=ids)
        font_style = xlwt.XFStyle()
        for b in invoices:
            row_num += 1
            ws.write(row_num, 0, f'TEC-000{b.id}', font_style)
            ws.write(row_num, 1, b.user.email, font_style)
            ws.write(row_num, 2, b.service.action, font_style)
            ws.write(row_num, 3, b.discount, font_style)
            ws.write(row_num, 4, b.amount, font_style)
            ws.write(row_num, 5,str( b.pay_date), font_style)

        wb.save(response)
        return response
    
def export_payment_xls(request,ids):
        ids=ids.split(',')
        response = HttpResponse(content_type='application/ms-excel')
        response['Content-Disposition'] = 'attachment; filename="Invoices.xls"'

        wb = xlwt.Workbook(encoding='utf-8')
        ws = wb.add_sheet('Invoice Data') # this will make a sheet named Users Data

        # Sheet header, first row
        row_num = 0

        font_style = xlwt.XFStyle()
        font_style.font.bold = True

        columns = ['ID number', 'Date', 'Country','Amount','Gsp','Pst' ]

        for col_num in range(len(columns)):
            ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

        invoices=Payment.objects.filter(id__in=ids)
        font_style = xlwt.XFStyle()
        for b in invoices:
            row_num += 1
            ws.write(row_num, 0,b.id_pay , font_style)
            ws.write(row_num, 1, str(b.success_date), font_style)
            ws.write(row_num, 2, b.country, font_style)
            ws.write(row_num, 3, b.amount, font_style)
            ws.write(row_num, 4, b.gsp, font_style)
            ws.write(row_num, 5,b.pst, font_style)



        wb.save(response)
        return response

def get_days(start_date,end_date):
    start_date=start_date.split('-')
    start_date[2]=start_date[2].split('T',1)[0]
    start_date=int(datetime(int(start_date[0]),int(start_date[1]),int(start_date[2]),0,0).timestamp()/3600)
    end_date=end_date.split('-')
    end_date[2]=end_date[2].split('T',1)[0]
    end_date=int(datetime(int(end_date[0]),int(end_date[1]),int(end_date[2]),0,0).timestamp()/3600)
    days=end_date - start_date
    time_threshold = datetime.now(timezone.utc) - timedelta(hours=days)
    return time_threshold

def filter_payment(request,payment_method):
    # Recent history
    section_date=request.POST.get('section-date')
    start_date=request.POST.get('start_date')
    end_date=request.POST.get('end_date')
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
    
    if filter_user == 'all':
        invoices=Payment.objects.filter(pymeny_method=payment_method,success_date__gt=time_threshold,paymented=True)
    else:
        invoices=Payment.objects.filter(user__in=user_list,pymeny_method=payment_method,success_date__gt=time_threshold,paymented=True)
    
    return invoices

def check_user_members(membership,service_name):
    start_date=str(membership.created).split('-')
    start_date[2]=start_date[2].split(' ',1)[0]
    start_date=datetime(int(start_date[0]),int(start_date[1]),int(start_date[2]),0,0).timestamp()
    end_date=time()
    passed_days=(float((int(float(end_date)) - start_date))/(24*3600))    
    if not membership.is_active:
        return False
    else:
        if not membership.is_pay:
            return False
        else:         
            if passed_days > membership.membership.duration:
                return False
            else:
                if membership.membership.is_all:
                    is_all_count=membership.project_count+membership.workshop_count+membership.badge_request_count
                    if membership.membership.usabel_number_all <= is_all_count :
                        if membership.membership.usabel_number_all == -1:
                            return True
                        else:
                            if service_name=='P':
                                if membership.membership.is_project:
                                    if membership.membership.usabel_number_project <= membership.project_count:
                                        if  membership.membership.usabel_number_project == -1:
                                            return True
                                        else:
                                            return False
                                    else:
                                        return True
                                else:
                                    return False
                            elif service_name=='W':
                                if membership.membership.is_workshop:
                                    if membership.membership.usabel_number_workshop <= membership.workshop_count:
                                        if  membership.membership.usabel_number_workshop == -1:
                                            return True
                                        else:
                                            return False
                                    else:
                                        return True
                                else:
                                    return False
                            elif service_name=='BR':
                                if membership.membership.is_badge_request:
                                    if membership.membership.usabel_number_badge_rquest <= membership.badge_request_count:
                                        if  membership.membership.usabel_number_badge_rquest == -1:
                                            return True
                                        else:
                                            return False
                                    else:
                                        return True
                                else:
                                    return False 
                            else:
                                return True
                    else:
                        return True
                else:
                    if service_name=='P':
                        if membership.membership.is_project:
                            if membership.membership.usabel_number_project <= membership.project_count:
                                if  membership.membership.usabel_number_project == -1:
                                    return True
                                else:
                                    return False
                            else:
                                return True
                        else:
                            return False
                    elif service_name=='W':
                        if membership.membership.is_workshop:
                            if membership.membership.usabel_number_workshop <= membership.workshop_count:
                                if  membership.membership.usabel_number_workshop == -1:
                                    return True
                                else:
                                    return False
                            else:
                                return True
                        else:
                            return False
                    elif service_name=='BR':
                        if membership.membership.is_badge_request:
                            if membership.membership.usabel_number_badge_rquest <= membership.badge_request_count:
                                if  membership.membership.usabel_number_badge_rquest == -1:
                                    return True
                                else:
                                    return False
                            else:
                                return True
                        else:
                            return False 
                    else:
                        return True

def get_amount_membership(request,service_name,pay_amount):
    membership=membership_user.objects.filter(user=request.user).first()
    if membership is None:
        amount=0
    else:
        allow=check_user_members(membership,service_name)
        if allow:
            if membership.membership.type=="percent":
                 constnumber=(pay_amount/100)
            else:
                constnumber=1
            if service_name=='P':
                amount=constnumber*membership.membership.project_amount
            elif service_name=='W':
                amount=constnumber*membership.membership.workshop_amount
            elif service_name=='BR':
                amount=constnumber*membership.membership.badge_request_amount
            else:
                amount=constnumber*membership.membership.badge_request_amount
        else:
            amount=0
    return amount

def check_membership_aftertimes(request,select_invoice):
    membership_code=select_invoice.session_membership.split('-')[0]
    check=True
    if membership_code == '0':
        pass
    else:
        check_membership=get_amount_membership(request,select_invoice.service.service_name,select_invoice.amount)
        if check_membership == 0 :
                check=False
        else:
            pass
    if check is False:
        select_invoice.session_membership='0-0'
        select_invoice.save()
    return check
        
def check_discount_aftertimes(request,invoice):
    discount_code=invoice.session_discount.split('-')[0]
    check=True
    if discount_code == '0':
        check=True
    else:
        discount=Discount.objects.filter(discount_code=discount_code).first()
        if discount:
            data=json.loads(discount.data)
            projectslist=data['project'].split(',')
            workshopslist=data['workshop'].split(',')
            if discount_code == '0':
                check=True
            else:
                # check use_count
                if discount.uses_count < discount.max_uses:

                    # check code is general
                    if discount.is_all:
                        check=True
                    else:
                        # check code is for projects
                        if invoice.service.service_name=='P':
                            if discount.is_all_project:
                                check=True
                            else:
                                if projectslist[0]=="":
                                    check=False
                                else:
                                    check=False
                                    for p in projectslist:
                                        if int(p)==invoice.service.project.id:
                                            check=True  
                                        else:
                                            pass                                  
                        # check code is for workshop
                        elif invoice.service.service_name=='W':                           
                            if discount.is_all_workshop:
                                check=True
                            else:
                                if workshopslist[0]=="":
                                    check=False
                                else:
                                    check=False
                                    for w in workshopslist:
                                        if int(w)==invoice.service.workshop.id:
                                            check=True  
                                        else:
                                            pass




                        # check code is for badgerequest
                        elif invoice.service.service_name=='BR':
                            if discount.is_all_badge:
                                check=True
                            else:
                                check=False

                    
                        # check code is for supervisorrequest
                        elif invoice.service.service_name=='SR':
                            if discount.is_all_supervisorrequests:
                                check=True
                            else:
                                check=False

                        # check code is for workshoprequest
                        elif invoice.service.service_name=='WR':
                            if discount.is_all_workshoprequest:
                                check=True
                            else:
                                check=False
                    
                else:
                    check=False
        else:
            check=False
        if check is False:
            invoice.session_discount='0-0'
            invoice.save()

    return check

def check_amount_discount(invoice):
    discount_code=invoice.session_discount.split('-')[0]
    discount_amount=invoice.session_discount.split('-')[1]
    discount=Discount.objects.filter(discount_code=discount_code).first()
    amount=0
    if discount is None:
        invoice.session_discount='0-0'
    else:
        if discount.use_status == 'percent':
            amount=(invoice.amount/100)*discount.amount
        else:
            amount=discount.amount
    if discount_amount == amount:
        pass
    else:
        invoice.session_discount=f"{discount_code}-{amount}"
    invoice.save()
    
def check_amount_membership(invoice):
    membership_amount=invoice.session_membership.split('-')[1]
    amount=get_amount_membership(invoice,invoice.service.service_name,invoice.amount)
    if membership_amount == '0':
        pass
    else:
        if int(float(membership_amount) )== amount:
            pass
        else:
            invoice.session_membership=f"{invoice.session_membership.split('-')[0]}-{amount}"
        invoice.save()
    
def invoice_pay(pk):
        template_name='invoice/invoice-detail.html'
        select_invoice=get_object_or_404(Invoice,id=pk)
        user=select_invoice.user
        select_invoice.is_paid=True
        select_invoice.pay_date=datetime.now()   
        discount_code=select_invoice.session_discount.split('-')[0]
        discount_amount=select_invoice.session_discount.split('-')[1]
        membership_code=select_invoice.session_membership.split('-')[0]  
        user_membership=membership_user.objects.filter(user=user).first()
        discount_object=Discount.objects.filter(discount_code=discount_code).first()

    # .........send Email & Notif & change status in objects

    ##############################-----PROJECT-----##########################################################

        if select_invoice.service.service_name == 'P':
            reason=f'Project (ID:{select_invoice.service.project.id_project})'
            service_id=select_invoice.service.project.id_project
            if select_invoice.service.action == 'create':
                again_pay_project(user,select_invoice.service.project.id)
                pass
                
            elif 'increase_fund' in select_invoice.service.action :
                pk=int(select_invoice.service.action.split('-')[1])
                agian_resubmit_supervisor(user, pk, select_invoice.service.project.fund + select_invoice.amount)
                
            elif 'send-contract' in select_invoice.service.action :
                pk=int(select_invoice.service.action.split('-')[2])
                again_supervisor_send_contract(user, pk)
                
            elif 'apply-applicant' in select_invoice.service.action :
                pk=int(select_invoice.service.action.split('-')[2])
                again_applyproject(user, pk)

            elif 'contract-client' in select_invoice.service.action :
                pk=select_invoice.service.project.id
                # pay_contract_client(request, pk)
            
            elif 'proposal-supervisor' in select_invoice.service.action :
                pk=int(select_invoice.service.action.split('-')[2])
                # pay_proposal_supervisor(request, pk)
                
            if user_membership is not None:
                user_membership.project_count=user_membership.project_count+1



    ##############################-----WORKSHOP-----##########################################################

        if select_invoice.service.service_name == 'W':
            if select_invoice.service.action=='create':
                send_notif_email(select_invoice.service.workshop.id,True)
                pass

            elif 'buy' in select_invoice.service.action:
                action=select_invoice.service.action
                section=action.split('-')[1]
                user_workshop=Users_Workshops.objects.get(user=user, workshop_id=select_invoice.service.workshop.id, is_paid=False,section=section)
                user_workshop.is_paid=True
                user_workshop.save()

            reason=f'Workshop(ID:{select_invoice.service.workshop.unique_id})'
            service_id=select_invoice.service.workshop.unique_id
            if user_membership is not None:
                user_membership.workshop_count=user_membership.workshop_count+1
    ##############################-----Virtual event-----##########################################################

        # if select_invoice.service.service_name == 'V':

        #     action=select_invoice.service.action
        #     virtualmembers=VirtualEventMemebers.objects.get(user=user, virtual_event=select_invoice.service.virtual_event.id, is_paid=False,section=action)
        #     virtualmembers.is_paid=True
        #     virtualmembers.save()

        #     reason=f'virtual_event(ID:{select_invoice.service.virtual_event.unique_id})'
        #     service_id=select_invoice.service.virtual_event.unique_id
            # if user_membership is not None:
            #     user_membership.workshop_count=user_membership.workshop_count+1



    ##############################-----BADGE-----##########################################################

        if select_invoice.service.service_name == 'BR':
            reason=f'Badge(ID:{select_invoice.service.badge.unique_id})'
            sendemailnotifbadgerequest(user,select_invoice.service.badge.id,True)
            service_id=select_invoice.service.badge.unique_id

            if user_membership is not None:
                user_membership.badge_request_count=user_membership.badge_request_count+1

    ##############################-----BADGESupervisor-----#################################################

        if select_invoice.service.service_name == 'SR':
            reason=f'Badge(ID:{select_invoice.service.badgesupervisor.id_request})'
            sendemailnotifsupervisorrequest(user,select_invoice.service.badgesupervisor.id,True)
            service_id=select_invoice.service.badgesupervisor.id_request


    ##############################-----BADGEWorkshop-----###################################################

        
        
        if select_invoice.service.service_name == 'WR':
            reason=f'Badge(ID:{select_invoice.service.badgeworkshop.id_request})'
            sendemailnotifworkshoprequest(user,select_invoice.service.badgeworkshop.id,True)
            service_id=select_invoice.service.badgeworkshop.id_request



    ########################################################################################################


    # Start.........send Email & Notif
    # .........send Email
        e_subject ="TECVICO payment bill"
        e_content ="Dear {} \nHello\nHope you are going well. \n. The amount of ${} was deducted from your balance for the {} in {}. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the payment sector through payment@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(user.get_full_name(),reason, select_invoice.amount + int(float(discount_amount)),datetime.now())
        e_destination = user.email
        # send_new_email(e_subject,e_content,e_destination)
    # ...........send notif
        Notification(title=reason, 
                    description='The amount of ${} was deducted from your balance for the {} .'.format(select_invoice.amount - int(float(discount_amount)),reason), 
                    target=user, 
                    link='notification-page').save()
    # End.........send Email & Notif


        tracking_id=f'TEC-{select_invoice.service.service_name}-{float(time())}-{service_id}-{select_invoice.user_balance}-{select_invoice.amount}-{user.id}'
        select_invoice.fallow_code=tracking_id
        select_invoice.save()

        if discount_code != '':
            if discount_object is not None:
                discount_object.uses_count= discount_object.uses_count+1
                discount_object.save()

        if user_membership is not None:
                user_membership.save()

        # messages.success(request,'Your payment was done successfully.')

        return redirect(f'/accounting/invoice/{select_invoice.id}')
