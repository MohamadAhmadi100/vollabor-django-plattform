from datetime import datetime, timedelta
from pydoc import describe
from django.db.models.expressions import F
from django.forms import NullBooleanField
from django.http import request, HttpResponseRedirect
from django.shortcuts import render
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from .models import *
from django.http.response import HttpResponse, JsonResponse
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from django.core.mail import send_mail
from ivc_project.settings import EMAIL_HOST_USER
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from seo.models import UserFootprint
# from suds import Client
from django.core.paginator import Paginator
from django.utils import timezone
from users.models import Role
from ivc_project.email_sender import send_new_email
from users.models import MemberProfile
from .forms import WorkshopTempForm, Landingpageform ,Advertisingform
from .utils import render_to_pdf
import pytz,os
from dashboard.models import Notification
from django.template.loader import get_template, render_to_string
from accounting.models import PaymentProtocol,Invoice,Service,RejectProtocol
from django.views.decorators.cache import never_cache
import mimetypes
# from forum.models import Category, MainCategory
# Create your views here.


###############pay
# MERCHANT = '123456788-1234-1234-1234-123456789101'
# client = Client('https://www.zarinpal.com/pg/services/WebGate/wsdl')

# def strtime_to_seconds(str_time):
#     date=datetime.strptime(str_time.strip(), '%H:%M:%S')
#     h,m,s=str(date.time()).split(':')
#     h=int(h)*3600
#     m=int(m)*60
#     seconds=h+m+int(s)
#     return seconds
# def  seconds_to_time(seconds):
#     m,s=divmod(seconds,60)
#     h,m=divmod(m,60)
#     return '%d:%02d'%(h,m)

# def check_role(request):
#     is_manager=Role.objects.filter(user=request.user,position='workshop manager').first()
#     is_expert=Role.objects.filter(user=request.user,position='workshop expert').first()
#     if is_manager:
#         manager=True
#     else:
#         manager=False
#     if is_expert:
#         expert=True
#     else:
#         expert=False
#     return manager,expert

# def download_file(request,path,filename):
#     fl = open(path, 'rb').read()
#     mime_type, _ = mimetypes.guess_type(path)
#     response = HttpResponse(fl, content_type=mime_type)
#     response['Content-Disposition'] = "attachment; filename=%s" % filename
#     return response


# def send_request(request, pk):
#     Users_Workshops(user=request.user, workshop_id=pk).save()  # creates a new order which is not verified (is_verified = False)
#     workshop = Workshop.objects.get(pk=pk)
#     user_email = request.user.email
#     user_phone = request.user.memberprofile.phone
#     description = "توضیحات مربوط به تراکنش را در این قسمت وارد کنید"
#     callback_URL = f"{request.get_host()}/workshop/verify/"
#     # callback_URL = "http://127.0.0.1:8000/workshop/verify/"
#     result = client.service.PaymentRequest(MERCHANT,
#                                            workshop.price,
#                                            description,
#                                            user_email,
#                                            user_phone,
#                                            callback_URL)
#     if result.Status == 100:
#         return redirect('https://www.zarinpal.com/pg/StartPay/' + str(result.Authority))
#     else:
#         print(result.Status)
#         return HttpResponse('Error code: ' + str(result.Status))


# def verify(request):
#     if request.GET.get('Status') == 'OK':
#         last_order = Users_Workshops.objects.filter(user=request.user).last()
#         last_order_workshop = Workshop.objects.get(pk=last_order.workshop_id)
#         result = client.service.PaymentVerification(MERCHANT,
#                                                     request.GET['Authority'],
#                                                     last_order_workshop.price)
#         if result.Status == 100:
#             last_order.is_paid = True
#             last_order.save()
#             redir = reverse("add-workshop-for-user", args=[workshop.id])
#             return HttpResponseRedirect(redir)
#             return HttpResponse('Transaction success')
#         elif result.Status == 101:
#             return HttpResponse('Transaction submitted : ' + str(result.Status))
#         else:
#             return HttpResponse('Transaction failed' + str(result.Status))
#     else:
#         return HttpResponse('Transaction failed or canceled by user')
###############end pay
@login_required
def checked_list(request):
    # comments = Comment.objects.filter(is_checked=True)
    # acc_rej = AcceptReject.objects.all()
    # works = []
    # for acc in acc_rej:
    #     works.append(acc.workshop)
    # context = {
    #     "comments":comments,
    #     "works":works
    # }
    # return render(request,"workshop/checked.html",context)
    comments = Comment.objects.filter(is_checked=True)
    acc_rej = AcceptReject.objects.all()
    accept_reject = AcceptReject.objects.filter(is_edited = True, is_accept = False)
    works = []
    for acc in acc_rej:
        works.append(acc.workshop)
    reject = []
    for obj in accept_reject:
        reject.append(obj.workshop)
    context = {
        "comments":comments,
        "works":works,
        "accept_reject":reject
    }
    return render(request,"workshop/checked.html",context)
@login_required
def accept_reject(request, pk):
    if request.method == "GET":
        comment = Comment.objects.get(pk=pk)
        workshop_time_table = TimeTable.objects.filter(workshop_id = comment.workshop.id)
        context = {
            "comment":comment,
            "time_table":workshop_time_table,
        }
        return render(request,"workshop/accept_reject.html",context)

@login_required
def list_expert(request):
    if request.method=="GET":
        comments = Comment.objects.filter(expert=request.user, is_checked=False)
        accept_reject = AcceptReject.objects.filter(is_accept=False)
        context = {
            "accept_reject":accept_reject,
            "comments":comments
        }
        return render(request, "workshop/list_for_expert.html", context)

@login_required
def add_comment_expert(request, pk):
    if request.method=="GET":
        user = request.user
        comment = Comment.objects.get(pk=pk)
        workshop_time_table = TimeTable.objects.filter(workshop_id = comment.workshop.id)
        if AcceptReject.objects.filter(workshop=comment.workshop).exists():
            accept_reject=AcceptReject.objects.filter(workshop=comment.workshop).first()
        else:
            accept_reject=None
        context = {
            "comment":comment,
            "user":user,
            'time_table':workshop_time_table,
            'accept_reject':accept_reject
        }
        return render(request, "workshop/add_expert_comment.html",context)
        
    if request.method =="POST":
        roles = Role.objects.filter(position = 'workshop manager')
        comment = Comment.objects.get(pk=pk)
        workshop = Workshop.objects.get(id = comment.workshop.id)
        comment.comment = request.POST.get("comment")
        workshop_time_table = TimeTable.objects.filter(workshop_id = comment.workshop.id)
        total_price=0
        if workshop_time_table:
            for timetable in workshop_time_table:
                price=request.POST.get(f'timtable_price_{timetable.id}')
                total_price+=int(price)
                timetable.expert_price=price
                timetable.save()
        comment.expert_price = total_price
        comment.is_checked = True
        comment.save()
        workshop.status = "Manager_check"
        workshop.save()
        if Workshop_log.objects.filter(workshop=workshop,status='Revise',is_done=False).exists():
            log=Workshop_log.objects.filter(workshop=workshop,status='Revise',is_done=False).first()
            log.is_done=True;log.save()
        if Workshop_log.objects.filter(workshop=workshop,status='Expert_comment',is_done=False).exists():
            log=Workshop_log.objects.filter(workshop=workshop,status='Expert_comment',is_done=False).first()
            log.is_done=True;log.save()
        Workshop_log.objects.create(workshop=workshop,status='Manager_check',position='director'
                                    ,desc=Workshop_log.description.Manager_check)
        
        
        # Notif
        """Notification.objects.create(title = "Workshop",description = "{workshop} , in this step, the manager will review your workshop request".format(workshop = workshop.title),
                                    target = workshop.top_user,
                                    link = reverse('my-workshop-status'))"""

        for role in roles:
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The workshop expert has assessed the workshop, please make final desicion.\nClick on this message to see the project",
                                        target = role.user,
                                        link = reverse('manager-workshop'))
            
            # Email for manager
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
            for user_role in comment.expert.role.all():
                    if user_role.position == 'workshop expert':
                        e_content = "Dear {manager}\nHello\nHope you are going well.\nThe expert, {expert}, has investigated the martial of the request for the workshop '{title}' Submitted on '{date}'\nThe comment(s) are listed as follows:\n'{comment}'.\nFor more information, please go to your dashboard to see the comment(s) and finalize the workshop request.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(expert_email = user_role.email,title = workshop.title, date = workshop.created.date(), expert = comment.expert, comment = comment.comment, manager = role.user.get_full_name())
            e_destination = role.user.email
            send_new_email(e_subject,e_content,e_destination)
        
        messages.success(request, "Your comment (s) has been saved successfully.")
        """comments = Comment.objects.filter(is_checked=True)
        context = {
            "comments":comments
        }
        return render(request,"workshop/list_for_expert.html",context)"""
        return redirect(reverse("expert-workshop"))

@login_required
def add_expert(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        ##################################################expert users for choose
        roles = Role.objects.filter(position="workshop expert")
        users = []
        for role in roles:
            users.append(role.user)
        # show time table
        workshop_time_table = TimeTable.objects.filter(workshop_id = workshop.id)
        comment=Comment.objects.filter(workshop=workshop).last()
            
        context = {
            "workshop":workshop,
            "users":users,
            "time_table": workshop_time_table,
            'comment':comment
        }
        return render(request, "workshop/add_expert.html", context)
    if request.method == "POST":
        expert_id = request.POST.get("expert")
        expert_access = request.POST.get("AccPerm")
        if expert_access == 'true':
            access = True
        else:
            access = False
        expert = User.objects.get(pk=expert_id)
        workshop = Workshop.objects.get(pk=pk)
        comment = Comment(expert=expert, workshop=workshop, comment="",access = access)
        comment.save()
        workshop.status = "Expert_decide"
        workshop.save()


        log=Workshop_log.objects.filter(workshop=workshop,status='Guarante_accept',is_done=0).first()
        if log:
            log.is_done=1;log.save()
        reject_expert_log=Workshop_log.objects.filter(workshop=workshop,status='reject_expert',is_done=0).first()
        if reject_expert_log:
            reject_expert_log.is_done=1;reject_expert_log.save()
        Workshop_log.objects.create(workshop=workshop,position='expert',status='Expert_decide',
                                            desc=Workshop_log.description.Expert_decide)
        
        # Notif
        """Notification.objects.create(title = "Workshop",description = "{workshop} , An expert was selected\nNow Your workshop is being reviewed by an expert".format(workshop = workshop.title),
                                    target = workshop.top_user,
                                    link = reverse('my-workshop-status'))
        # Email for clients
        e_subject = "TECVICO workshop"
        e_content = "Dear {creator}\nHello\nHope you are going well.\nA workshop expert has been associated with your request. The expert will carefully review the material of you request. Thus, we will inform you if any modification is required or if we need more information. You can contact the workshop expert via 'workshopexpert@tecvico.com'.\nTitle: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company: workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = workshop.top_user.get_full_name())
        e_destination = workshop.top_user.email
        send_new_email(e_subject,e_content,e_destination)"""

        # Notif for expert
        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "A new workshop has been assigned to you.\nClick on this message to see the workshop information.",
                                    target = comment.expert,
                                    link = reverse('expert-workshop'))
        
        """# Email for expert
        e_subject = "TECVICO workshop"
        e_content = "Dear {expert}\nHello\nHope you are going well.\nYou as a workshop expert are requested to undertake this project.\nWorkshop title: {title}\nSubmitted date: {date}\nYou are requested to observe progress of the workshop and do the assigned tasks on it. You must observe on how well the steps of the workshop are going forward. You should solve some issues which you can resolve.\nIf the problem is difficult, you should transfer it to the workshop director. You are also expected to give weekly report on this project to the director.\nDo not reply to this Email. If you have any questions or concerns, please contact to the workshop director through workshopdirector@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), expert = comment.expert.get_full_name())
        e_destination = comment.expert.email
        send_new_email(e_subject,e_content,e_destination)"""
        
        # Email for expert
        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
        e_content = "Dear {expert}\nHello\nHope you are going well.\nYou have been requested to uncertake the below peoject. You should confirm if you would like to undertake this project. The request will be canceled in 2 days if the director doesn’t receive any noftification from you and a negative point will be considered for you.\nWorkshop title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the workshop director through workshopdirector@tecvico.com.\n\nThank you\nSincerely,s\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), expert = comment.expert.get_full_name())
        e_destination = comment.expert.email
        send_new_email(e_subject,e_content,e_destination)
        
        messages.success(request, "The workshop expert has been selected successfully.")
        redir = reverse("manager-workshop")
        return HttpResponseRedirect(redir)

def workshops_list(requset):
    workshops = Workshop.objects.filter(status = "Guarante_accept")
    comments = Comment.objects.all()
    works = []
    for com in comments:
        works.append(com.workshop)
    
    accept_rejects = AcceptReject.objects.filter(is_edited=True)
    workshop_edited = []
    for acc in accept_rejects:
        workshop_edited.append(acc.workshop)
    context = {
        'works':works,
        'workshops': workshops,
        'workshop_edited' : workshop_edited
    }
    return render(requset, "workshop/list.html", context)


#def list_for_all(request):
 #   if request.method == 'GET':
  #      acc_rejs = AcceptReject.objects.filter(is_accept=True)
  #      workshops = []
  #      now_time = timezone.localdate()
  #      for acc in acc_rejs:
  #          workshops.append(acc.workshop)
  #      # workshops = Workshop.objects.all().order_by("-id")[:3]
  #      dones = False
  #      context = {
  #          "workshops":workshops,
  #          "dones":dones,
  #          "time":now_time
  #      }
  #      return render(request, "workshop/list-for-all.html", context)
  
  
def list_for_all(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        accepted = Workshop.objects.filter(status = "Accept").order_by('-created')       
        now_time = timezone.localdate()
        main_fields = MainField.objects.all()
        sub_fields = SubField.objects.none()
        dones = False
        # get all the lang
        workshop_lang = set()
        for work in accepted:
            # add lang
            start_date=TimeTable.objects.filter(workshop=work).first().start_date
            work.date=start_date
            work.save()
        accepted = Workshop.objects.filter(status = "Accept").order_by('-date')
        for work in accepted:
            workshop_lang.add(work.language)
            end_time=TimeTable.objects.filter(workshop=work).last().start_date
            start_time=TimeTable.objects.filter(workshop=work).first().start_time
            work.start_time=start_time
            work.speaker=work.speaker.split(',')
            if len(work.speaker)==1:
                work.speaker=work.speaker[0].split(':')
                work.speaker[0]='Speaker:'
                work.speaker=[work.speaker[0]+work.speaker[1]]
            if datetime.now().date() > end_time:
                work.expire=1
        paginator = Paginator(accepted, 8)
        page = request.GET.get('page')
        workshops = paginator.get_page(page)
        
        # make a dictionary for main field
        main_list = dict()
        i = 1
        for field in main_fields:
            main_list[i] = field
            i += 1

        # make a dictionary for lang field
        lang_list = dict()
        i = 1
        for lang in workshop_lang:
            lang_list[i] = lang
            i += 1
        context = {
            'workshops':workshops,
            "dones" : dones,
            "time" : now_time,
            "main_field" : main_list,
            "sub_fields": sub_fields,
            "workshop_lang" : lang_list,
             'salam':'SALAM'
        }
        return render(request, "workshop/list-for-all.html", context)
        
def workshop_main_field_filter(request):
    accepted = Workshop.objects.filter(status = "Accept").order_by('-created')
    for work in accepted:
        end_time=TimeTable.objects.filter(workshop=work).last().start_date
        if datetime.now().date() > end_time:
            work.expire=1
    main_fields = request.POST.getlist('main_list[]')
    sub_fields = request.POST.getlist('sub_list[]')
    workshop_lang = request.POST.getlist('lang_list[]')
    workshop_time = request.POST.get('date_time')
    search_word = request.POST.get('search_word')

    if search_word:
        accepted = Workshop.objects.filter(status = "Accept", title__contains = search_word)

    if main_fields or workshop_lang or workshop_time or sub_fields:
        selected_workshop = list(accepted)
        if main_fields:
            help_list = []
            for item in selected_workshop:
                if str(item.main_field) not in main_fields:
                    help_list.append(item)
            for i in help_list:
                if i in selected_workshop:
                    selected_workshop.remove(i)

        if sub_fields:
            help_list = []
            for item in selected_workshop:
                if str(item.sub_field) not in sub_fields:
                    help_list.append(item)
            for i in help_list:
                if i in selected_workshop:
                    selected_workshop.remove(i)

        if workshop_lang:
            help_list = []
            for item in selected_workshop:
                if item.language not in workshop_lang:
                    help_list.append(item)
            for i in help_list:
                if i in selected_workshop:
                    selected_workshop.remove(i)

        if workshop_time:
            if workshop_time ==   "Next week":
                start_time = timezone.now().date()
                new_time = start_time + timedelta(days=7)
                delta = new_time - start_time  # as timedelta
                days = [start_time + timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_workshop:
                    if item.date not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_workshop:
                        selected_workshop.remove(i)

            elif workshop_time == "Next month":
                start_time = timezone.now().date()
                new_time = start_time + timedelta(days=30)
                delta = new_time - start_time  # as timedelta
                days = [start_time + timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_workshop:
                    if item.date not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_workshop:
                        selected_workshop.remove(i)

            elif workshop_time == "Next two month":
                start_time = timezone.now().date()
                new_time = start_time + timedelta(days=60)
                delta = new_time - start_time  # as timedelta
                days = [start_time + timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_workshop:
                    if item.date not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_workshop:
                        selected_workshop.remove(i)

            elif workshop_time == "Last week":
                start_time = timezone.now().date()
                new_time = start_time - timedelta(days=7)
                delta = start_time - new_time  # as timedelta
                days = [start_time - timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_workshop:
                    if item.date not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_workshop:
                        selected_workshop.remove(i)

            elif workshop_time == "Last month":
                start_time = timezone.now().date()
                new_time = start_time - timedelta(days=30)
                delta = start_time - new_time  # as timedelta
                days = [start_time - timedelta(days=i) for i in range(delta.days + 1)]
                help_list = []
                for item in selected_workshop:
                    if item.date not in days:
                        help_list.append(item)
                for i in help_list:
                    if i in selected_workshop:
                        selected_workshop.remove(i)
        for work in selected_workshop:
            start_time=TimeTable.objects.filter(workshop=work).first().start_time
            work.start_time=start_time
            work.speaker=work.speaker.split(',')
            if len(work.speaker)==1:
                work.speaker=work.speaker[0].split(':')
                work.speaker[0]='Speaker:'
                work.speaker=[work.speaker[0]+work.speaker[1]]
        context = {
            'workshops': set(selected_workshop),
        }
    else:
        for work in accepted:
            start_time=TimeTable.objects.filter(workshop=work).first().start_time
            work.start_time=start_time
            work.speaker=work.speaker.split(',')
            if len(work.speaker)==1:
                work.speaker=work.speaker[0].split(':')
                work.speaker[0]='Speaker:'
                work.speaker=[work.speaker[0]+work.speaker[1]]
        context = {
            'workshops': accepted,
        }
    

    return render(request, 'workshop/workshop_main_field_filter.html', context)

def load_subfield(request):
    accepted = Workshop.objects.filter(status = "Accept")
    main_fields = request.POST.getlist('main_list[]')
    sub_field = set()
    if main_fields != []:
        for work in accepted:
            if str(work.main_field) in main_fields:
                sub_field.add(work.sub_field)
        sub_list = dict()
        i = 1
        for field in sub_field:
            sub_list[i] = field
            i += 1
    else:
        sub_list = SubField.objects.none()
    return render(request, 'workshop/subfield_dropdown_list.html', {'sub_field': sub_list})

##############add workshop
@login_required
@never_cache
def add_workshop(request):

    if request.method == "POST":

        data = request.POST.copy()
        # check image
        if 'demoImage' in request.POST:
            if request.POST.get('demoImage') != "":
                data['image'] = request.POST.get('demoImage')

        # check sub field
        if data['sub_field'] == '0':
            data['sub_field'] = None
        # add top user
        data['top_user'] = request.user
        workshop_form = WorkshopTempForm(data, request.FILES)
        if workshop_form.is_valid():
            workshop = workshop_form.save(commit=False)


            # check image format
            if request.POST.get('demoImage') != "":
                name = request.POST['demoImage']
                img_url = name.split('/')
                workshop.image = "workshop/demoImage/{name}".format(name = img_url[-1])
                print(workshop.image.url)
            else:
                image_name = workshop.image.name
                if image_name.endswith(".png") or image_name.endswith(".PNG") or image_name.endswith(".jpg")or image_name.endswith(".jpeg"):
                    pass
                else:
                    messages.error(request, "Your image format is invalid.")
                    return HttpResponseRedirect(request.path_info)
            
            # check file format
            """file_name = workshop.load_pdf.name
            if file_name.endswith(".docx") or file_name.endswith(".pptx") or file_name.endswith(".pdf"):
                pass
            else:
                messages.error(request, "Your file format is invalid, only use docx , pdf and pptx format.")
                return HttpResponseRedirect(request.path_info)"""
            
            # sub field handler
            sub_field = workshop.sub_field
            if sub_field == None:
                new_field = request.POST.get('add_field')
                workshop.add_field = new_field
            
            # add unique id
            #today_workshop = Workshop.objects.filter(created = timezone.now().date()).count()
            today_workshops = Workshop.objects.all()
            today_number = 0
            for item in today_workshops:
                if item.created.date() == timezone.now().date():
                    today_number += 1
            date = str(timezone.now().date())
            new_date = date.split('-')
            my_date = ""
            my_date = int(my_date.join(new_date))
            my_date = my_date * 10000
            my_date += (today_number + 1)
            workshop.unique_id = "W{num}".format(num = my_date)
            
            workshop.save()
            # set time table
            if request.POST.get('set_now') == "true":
                table_list = request.POST.getlist('tblList')[0].split(',')
                print(table_list)
                count=0
                while count < len(table_list):
                    if count == 0:
                        workshop.date=table_list[count+2]
                        workshop.save()
                    title=table_list[count+1]
                    start_date=table_list[count+2]
                    start_time=table_list[count+3]
                    end_time=table_list[count+4]
                    duration=table_list[count+5]
                    price=int(table_list[count+6])
                    TimeTable.objects.create(title=title,start_date=start_date,start_time=start_time,price=price,
                                            end_time=end_time,duration=duration,workshop_id = workshop.id)
                    count=count+7

                workshop_price=0
                timetables=TimeTable.objects.filter(workshop=workshop)
                for time in timetables:
                    workshop_price+=time.price
                

                workshop.price=workshop_price    

                if workshop.guaranteed == None:
                    workshop.status = 'pay_guarante'
                else:
                    workshop.status = 'New'
                
                workshop.save()
                Workshop_log.objects.create(workshop=workshop,position='supervisor',status='pay_guarante',
                                            desc=Workshop_log.description.pay_guarante,is_done=0)
                
                # Email
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {creator}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with it. Your request has successfully been submitted.\n\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = workshop.top_user.get_full_name())
                e_destination = workshop.top_user.email
                send_new_email(e_subject,e_content,e_destination)
                
                # Notif
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Thank you for your submission.\nThe submission will carefully be reviewd by workshop expert.",
                                            target = workshop.top_user,
                                            link = reverse('my-workshop-status'))
                
                if workshop.status == 'pay_guarante':
                    # Notif
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Pending for paying responsibility fee.",
                                                target = workshop.top_user,
                                                link = reverse('my-workshop-status'))
                    # Email
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = "Dear {creator}\nHello\nHope you are going well\nYou must pay $100 as responsibility fee if you would like to launch your workshop\nTitle: {title}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, creator = workshop.top_user.get_full_name())
                    e_destination = workshop.top_user.email
                    send_new_email(e_subject,e_content,e_destination)
                    
                elif workshop.status == 'New':
                    # Notif User
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Pending for guarantor's approval.",
                                                target = workshop.top_user,
                                                link = reverse('my-workshop-status'))
                    # Email User
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = "Dear {creator}\nHello\nHope you are going well.\nYour request has successfully been sent to {name} in order to guarantee you. If the guarantor declines your request, you must pay responsibility fee to hold the workshop.\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), name = workshop.guaranteed, creator = workshop.top_user.get_full_name())
                    e_destination = workshop.top_user.email
                    send_new_email(e_subject,e_content,e_destination)
                    
                    
                    # Notif Guarantor
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "You have been requested as a guarantor for the workshop.",
                                                target = workshop.guaranteed.user,
                                                link = reverse('guarante-request'))
                    
                    # Email Guarantor
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = "Dear {guarantor}\nHello\nHope you are going well\nYou are selected as a guarantor for this workshop.\n\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director\nworkshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), guarantor = workshop.guaranteed)
                    e_destination = workshop.guaranteed.user.email
                    send_new_email(e_subject,e_content,e_destination)
                
                
                messages.success(request, 'Your request has been submitted successfully.')
                return redirect(reverse('my-workshop-status'))
            else:
                # Email
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {creator}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with it. Your request has successfully been saved.\nTo launch the workshop, you need to set the timetable.\n\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = workshop.top_user.get_full_name())
                e_destination = workshop.top_user.email
                send_new_email(e_subject,e_content,e_destination)
                
                # Notif
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Thank you for your submission.\nYour request has successfully been saved.\nTo launch the workshop, you need to set the timetable.",
                                            target = workshop.top_user,
                                            link = reverse('my-workshop-status'))
                
                messages.success(request, "Your workshop has been saved successfully, please set timetable soon.")
                return redirect(reverse('my-workshop-status'))

        else:
            messages.error(request, workshop_form.errors)
            return HttpResponseRedirect(request.path_info)

    if request.method == "GET":
        member_profile = MemberProfile.objects.get(user=request.user)
        time_zone = pytz.all_timezones
        nowDate = timezone.now()
        context = {
            'user':request.user,
            'member_profile':member_profile,
            'workshop': WorkshopTempForm(),
            'time_zone': time_zone,
            'date': nowDate,
            'user_balance':request.user.memberprofile.balance,
        }
        return render(request,"workshop/workshop.html", context)
##############end add workshop

def set_time_table(request, pk):
    the_workshop = Workshop.objects.get(pk = pk)
    if request.method == "GET":
        context = {
            'workshop': the_workshop,
        }
        return render(request, 'workshop/time_table_form.html', context)
    elif request.method == "POST":
        
        my_list = []
        for i in range(int(request.POST.get('list_size'))):
            my_list.append(request.POST.getlist('json[{i}][]'.format(i = i)))

        with open('/home/tecvicoc/public_html/media/workshop/time_table/{name}.txt'.format(name = str(the_workshop.id) + '_time'),'w') as f:
            for time in my_list:
                for item in time:
                    f.write(item + ",")
                f.write('\n')
            f.close()
        time_file = 'workshop/time_table/{name}.txt'.format(name = str(the_workshop.id) + '_time')
        TimeTable.objects.create(workshop_id = the_workshop.id, information = time_file)
        if the_workshop.guaranteed == None:
            the_workshop.status = 'pay_guarante'
        else:
            the_workshop.status = 'New'
        the_workshop.save()
        messages.success(request, 'Timetable has been set successfully.')
        return JsonResponse({
                'success': True,
                'url': reverse('my-workshop-status'),
        })



def load_field(request):
    main_field = request.GET.get('main_field')
    if main_field != "":
        sub_field = SubField.objects.filter(parent_id=main_field)
    else:
        sub_field = SubField.objects.none()
    return render(request, 'workshop/field_dropdown_list_options.html', {'sub_field': sub_field})
    
@login_required
def show_workshops_to_user(request):
    if request.method == "GET":
        workshops = Workshop.objects.filter(status = 'Accept').order_by('-created')
        for work in workshops:
            end_time=TimeTable.objects.filter(workshop=work).last().start_date
            if datetime.now().date() > end_time:
                work.expire=1
        user_workshops = Users_Workshops.objects.filter(user = request.user,is_paid=True)
        user_workshop=[]
        certificates=[]
        count=0
        for item in user_workshops:
            if not item.certificate == None  and item.certificate != "deleted" and item.certificate != "":
                certificates.append({'workshop':item.workshop,'certificate':item.certificate})
            if not count == 0:
                if  not item.workshop==user_workshops[count-1].workshop:
                    user_workshop.append(item)
            else:
                user_workshop.append(item)
            count+=1        
        Notpay_workshop = Users_Workshops.objects.filter(user = request.user,is_paid=False)
        Notpay_workshop_count = Users_Workshops.objects.filter(user = request.user,is_paid=False).count()

        context = {
            "workshops":workshops,
            "workshops_number":workshops.count(),
            "Notpay_workshop":Notpay_workshop,
            "user_workshop": user_workshop,
            "user_number": len(user_workshop),
            'Notpay_workshop_count':Notpay_workshop_count,
            'certificates':certificates
        }
        return render(request, "workshop/workshop-user-list.html", context)

@login_required
def is_workshop_accept(request, pk):
    if request.method == "POST":
        workshop = Workshop.objects.get(pk=pk)
        if workshop.status == "Manager_check":
            if request.POST.get("is_accept") == "1":
                if AcceptReject.objects.filter(workshop=workshop).exists():
                    accept_reject = AcceptReject.objects.get(workshop=workshop)
                    if accept_reject.is_edited == True:
                        accept_reject.is_accept=True
                        accept_reject.is_edited=False
                        accept_reject.user = request.user
                        accept_reject.save()
                else:
                    accept_reject = AcceptReject.objects.create(user = request.user ,workshop=workshop, is_accept=True)
    
                workshop.status = "Accept"
                workshop.price = request.POST.get("price")
                workshop.save()

                #workshop_log
                if Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).first()
                    log.is_done=True;log.save()
                Workshop_log.objects.create(workshop=workshop,status='Accept',position='expert'
                                            ,desc=Workshop_log.description.Accept)

                messages.success(request, 'The workshop request has been accepted.')

            elif request.POST.get("is_accept") == "approve_contract":
                workshop_timetable=TimeTable.objects.filter(workshop=workshop).all()
                total_price=0
                for table in workshop_timetable:
                    price=request.POST.get(f'timetable_price_{table.id}')
                    total_price+=int(price)
                    table.price=price
                    table.save()
                if AcceptReject.objects.filter(workshop=workshop).exists():
                    accept_reject = AcceptReject.objects.get(workshop=workshop)
                    if accept_reject.is_edited == True:
                        accept_reject.approve_contract=True
                        accept_reject.is_edited=False
                        accept_reject.user = request.user
                        accept_reject.save()
                else:
                    accept_reject = AcceptReject.objects.create(user = request.user ,workshop=workshop, approve_contract=True)

                comment=Comment.objects.filter(workshop=workshop,status='Approve').first()
                comment.status="Approve_contract";comment.save()
    
                workshop.status = "Approve_contract"
                workshop.price = total_price
                workshop.save()

                #workshop_log
                if Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).first()
                    log.is_done=True;log.save()
                Workshop_log.objects.create(workshop=workshop,status='Approve_contract',position='expert'
                                            ,desc=Workshop_log.description.Approve_contract)

                messages.success(request, 'The workshop request has been accepted.')


                
            elif request.POST.get('is_accept') == 'revise':
                revise_comment=request.POST.get('revise_comment')
                if AcceptReject.objects.filter(workshop=workshop).exists():
                    accept_reject = AcceptReject.objects.get(workshop=workshop)
                    if accept_reject.is_edited == True:
                        accept_reject.is_accept=False
                        accept_reject.is_edited=True
                        accept_reject.comment=revise_comment
                        accept_reject.user = request.user
                        accept_reject.save()
                else:
                    accept_reject = AcceptReject.objects.create(user = request.user ,workshop=workshop, is_accept=False,
                                                                comment=revise_comment,is_edited=True)
    
                workshop.status = "Revise_to_expert"
                workshop.save()

                #workshop_log
                if Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).first()
                    log.is_done=True;log.save()
                Workshop_log.objects.create(workshop=workshop,status='Revise',position='expert'
                                            ,desc=Workshop_log.description.Revise_to_expert)

                messages.success(request, 'The workshop request has been revise.')

            else:
                comment = request.POST.get("comment")
                if AcceptReject.objects.filter(workshop=workshop).exists():
                    accept_reject = AcceptReject.objects.get(workshop=workshop)
                    accept_reject.is_edited = False
                    accept_reject.is_accept = False
                    accept_reject.comment = comment
                    accept_reject.user = request.user
                    accept_reject.save()
                else:
                    accept_reject = AcceptReject.objects.create(user = request.user, workshop=workshop, is_accept=False, comment=comment)
                
                workshop.status = "Reject"
                workshop.save()

                #workshop_log
                if Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Manager_check',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Revise_to_expert',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='ReRevise_to_expertvise',is_done=False).first()
                    log.is_done=True;log.save()
                if Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).first()
                    log.is_done=True;log.save()
                Workshop_log.objects.create(workshop=workshop,status='Reject',position='supervisor'
                                            ,desc=Workshop_log.description.Reject)

                messages.success(request, 'The workshop request has been rejected.')
        else:
            messages.error(request, 'This workshop request has already been assessed.')
        
        comment = Comment.objects.filter(workshop = workshop, status__in=['Approve','Approve_contract']).first()
        accept_reject=AcceptReject.objects.filter(workshop=workshop).first()
        roles = Role.objects.filter(position="Advertisement manager")
        manager_list = Role.objects.filter(position = "workshop manager")
        user_manager = []
        for item in manager_list:
            user_manager.append(item.user)
        expert_list = Role.objects.filter(position = "workshop expert")
        user_expert = []
        for item in expert_list:
            user_expert.append(item.user)
        
        if workshop.status == "Reject":
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Your workshop has been rejected.\nClick on this massage to see the rejection reasons.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
            for user_role in comment.expert.role.all():
                    if user_role.position == 'workshop expert':
                        e_content = "Dear {creator}\nHello\nHope you are going well.\nThe workshop team has reviewed your workshop request.\nTitle: '{title}' Submitted on '{date}'\nTECVICO writes this letter to thank you for showing interest in working with it. Unfortunately, your workshop request has been rejected by our board of directors because '{manager_comment}', as you can completely see those comments on your dashboard. We welcome you to submit other workshops in the future.\nThank you for your efforts and time. We hope to work with you in the near future.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date() ,expert_email = user_role.email, manager_comment = accept_reject.comment, creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            
            if accept_reject.user == comment.expert:
                for role in manager_list:
                    # email for  manager
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = "Dear {expert}\nHello\nHope you are going well.\nThe workshop expert, namely {expert_name},has rejected the workshop\nTitle: '{title}' Submitted on '{date}'\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, expert_name = comment.expert.get_full_name(),date = workshop.created.date(), expert = role.user.get_full_name())
                    e_destination = role.user.email
                    send_new_email(e_subject,e_content,e_destination)
            else:
                # email for expert
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {expert}\nHello\nHope you are going well.\nThe workshop director has rejected the workshop\nTitle: '{title}' Submitted on '{date}'\nTECVICO writes this letter to thank you for your efforts and time.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), expert = comment.expert.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)
        elif workshop.status == "Accept":
            
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Congratulations, your workshop has been accepted.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
            for user_role in comment.expert.role.all():
                    if user_role.position == 'workshop expert':
                        e_content = "Dear {creator}\nHello\nHope you are going well.\n\nCongrats! Your request for holding the workshop '{title}' Submitted on '{date}' has been accepted. To hold your workshop, you must follow the workshop steps as below:\n1. You must prepare and finalize your content and upload it in two weeks after acceptance.\n2. You must record a video and upload it in two weeks after acceptance.\nNote: The advertisement team will start advertising after receiving the mention requirements.\n\n Please go to your dashboard and follow the workshop steps. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, expert_email =  user_role.email ,date = workshop.created.date(), creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            
            
            if accept_reject.user == comment.expert:
                for role in manager_list:
                    # Notif
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The workshop has been accepted by the expert.",
                                                target = role.user,
                                                link = reverse('my-workshop-status'))
                    
                    # Email for expert or manager
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = ""
                    for user_role in accept_reject.user.role.all():
                        if user_role.position == 'workshop expert': 
                            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'has been accepted by the expert.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(expert_email = user_role.email, title = workshop.title, date = workshop.created.date(), user_email = workshop.top_user.email, creator = role.user.get_full_name())
                    e_destination = role.user.email
                    send_new_email(e_subject,e_content,e_destination)
            else:
                # Notif
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The workshop has been accepted by the director.",
                                            target = comment.expert,
                                            link = reverse('my-workshop-status'))
                
                # Email for expert or manager
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'has been accepted by the workshop director.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), user_email = workshop.top_user.email, creator = comment.expert.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)
            
            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "A new workshop has been added to your list.\nClick on this message to see the information.",
                                            target = role.user,
                                            link = reverse('ad-form', args=[workshop.pk]))
                
                # Email for advertisement
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = ""
                for user_role in comment.expert.role.all():
                    if user_role.position == 'workshop expert':
                        e_content = "Dear {ad_manager}\nHello\nHope you are going well. A new workshop has been accepted by workshop team on {acc_date}. You are requested to proceed it. The company expects your team to do the best.\nYou should announce the interested people to participate in this workshop. If you need more information, you can contact the workshop expert with {expert_email}.\nYou also can go to your dashboard and see some information you need to advertise from this workshop.\n\nTitle: {title}\nSubmitted date: {date}\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(expert_email = user_role.email, title = workshop.title, acc_date = timezone.now().date() ,date = workshop.created.date(), ad_manager = role.user.get_full_name())
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)

        elif workshop.status == "Revise_to_expert":
            if accept_reject.user == comment.expert:
                for role in manager_list:
                    # Notif
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Director wants you to revise the workshop.\nClick on this message to see the information",
                                                target = role.user,
                                                link = reverse('my-workshop-status'))
                    
                    # Email for expert or manager
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = ""
                    for user_role in accept_reject.user.role.all():
                        if user_role.position == 'workshop expert': 
                            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'Director wants you to revise the workshop.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(expert_email = user_role.email, title = workshop.title, date = workshop.created.date(), user_email = workshop.top_user.email, creator = role.user.get_full_name())
                    e_destination = role.user.email
                    send_new_email(e_subject,e_content,e_destination)
            else:
                # Notif
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Director wants you to revise the workshop.\nClick on this message to see the information",
                                            target = comment.expert,
                                            link = reverse('my-workshop-status'))
                
                # Email for expert or manager
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'Director wants you to revise the workshop.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), user_email = workshop.top_user.email, creator = comment.expert.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)

        elif workshop.status == "Approve_contract":
            if accept_reject.user == comment.expert:
                for role in manager_list:
                    # Notif
                    Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Director agrees to send the contract to the supervisor.\nClick on this message to see the information",
                                                target = comment.expert,
                                                link = reverse('my-workshop-status'))
                    
                    # Email for expert or manager
                    e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                    e_content = ""
                    for user_role in accept_reject.user.role.all():
                        if user_role.position == 'workshop expert': 
                            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'Director agrees to send the contract to the supervisor.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(expert_email = comment.expert.email, title = workshop.title, date = workshop.created.date(), creator = role.user.get_full_name())
                    e_destination = role.user.email
                    send_new_email(e_subject,e_content,e_destination)
            else:
                # Notif
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Director agrees to send the contract to the supervisor.\nClick on this message to see the information",
                                            target = comment.expert,
                                            link = reverse('my-workshop-status'))
                
                # Email for expert or manager
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'Director agrees to send the contract to the supervisor.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = comment.expert.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)    
            
                   
        #return redirect("manager-workshop")
        """for role in user_manager:
            if role.user == accept_reject.user:
                return redirect("manager-workshop")
        
        user_manager
        user_expert"""
        return redirect("dashboard-page")


def view_workshop(request, pk):
    if request.method  == "GET":
        if request.user.is_authenticated:
            create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
        workshop = Workshop.objects.get(pk=pk)
        
        workshop_time_table = TimeTable.objects.filter(workshop_id = workshop.id)
        end_time=workshop_time_table.last().start_date
        if datetime.now().date() > end_time:
                workshop.expire=1

        # get workshop duration
        seconds=0
        duration=0
        if request. user. is_authenticated:
            user_workshops=Users_Workshops.objects.filter(user=request.user,workshop=workshop,is_paid=True).exclude(section='All')
            for time_table in workshop_time_table:
                    for uw in user_workshops:
                        if uw.section == time_table.title:
                            time_table.buy=True
                    if time_table.duration:
                        time=strtime_to_seconds(time_table.duration)
                        seconds+=time
        duration=seconds_to_time(seconds)




        workshop_speaker = workshop.speaker
        speakers = workshop_speaker.split(',')
            
        registrants = Users_Workshops.objects.filter(workshop = workshop).count()
        context = {
            "workshop":workshop,
            "time_table": workshop_time_table,
            "speakers":speakers,
            "registrants":registrants,
            'duration':duration,
            'buyall':False
           
        }
        if request. user. is_authenticated:
            buyall=Users_Workshops.objects.filter(user=request.user,workshop=workshop,is_paid=True,section='All')
            if not len(buyall) == 0:
               context['buyall']=True            
        return render(request,"workshop/view-workshop.html",context)

@login_required
def accepted_list(request):
    if request.method == "GET":
        accepteds = AcceptReject.objects.filter(is_accept=True)
        workshops = []
        for acc in accepteds:
            workshops.append(Workshop.objects.get(pk=acc.workshop_id))
        context = {
            "workshops":workshops
        }
        return render(request,"workshop/accepted_list.html",context)

@login_required
def my_workshops_status(request):
    if request.method == "GET":
        exclude=['Notpay','Reject','Delete']
        include_all=['New','pay_guarante','Notpay','Guarante_accept','Expert_decide','Expert_comment','Manager_check']
        include_contract=['Upload_contract',
        'Send_contract_by_supervisor',
        'Revise_contract_to_supervisor',
        'Send_contract_to_director',
        'Revise_contract_to_expert',
        'Reject_contract_to_supervisor']
        exclude_accept_reject=include_all+include_contract

        accept_reject = AcceptReject.objects.filter(workshop__top_user=request.user).exclude(workshop__status__in=exclude_accept_reject)
        accept_reject_count=AcceptReject.objects.filter(workshop__top_user=request.user).exclude(workshop__status__in=exclude_accept_reject).count()

        all_workshop = Workshop.objects.filter(top_user = request.user,status__in=include_all).order_by('-created')
        all_workshop.count = Workshop.objects.filter(top_user = request.user,status__in=include_all).count()

        contract= AcceptReject.objects.filter(workshop__top_user=request.user,workshop__status__in=include_contract)
        contract_count=AcceptReject.objects.filter(workshop__top_user=request.user,workshop__status__in=include_contract).count()
        for c in contract:
            if not c.workshop.status == 'Reject_contract_to_supervisor':
                for comment in Comment.objects.filter(workshop=c.workshop,status='Revise_contract_to_supervisor'):
                    c.comment=comment.comment
            



        for i in all_workshop:
            i.count=Users_Workshops.objects.filter(workshop=i,is_paid=1).count()

        Notpay_workshop = Workshop.objects.filter(top_user = request.user,status="Notpay")
        services=Service.objects.filter(user=request.user,service_name='W',action='create')
        invoicelist=[]
        for invoice in Invoice.objects.filter(user=request.user).all():
            for service in services:
                if invoice.service==service:
                    invoicelist.append(invoice)
        
        user = request.user.memberprofile.balance

        context = {
            "all_workshop":all_workshop,
            "Notpay_workshop":Notpay_workshop,
            "accept_reject":reversed(accept_reject),
            "accept_reject_count":accept_reject_count,
            "user":user,
            'invoces':invoicelist,
            'contracts':reversed(contract),
            'contracts_count':contract_count,
            'status':SUPERVISOR_STATUS
        }
        return render(request, "workshop/my_workshop_status.html",context)


@login_required
def delete_workshop(request, pk):
    workshop = Workshop.objects.get(pk=pk)
    workshop.status="Delete"
    workshop.user=workshop.top_user
    RejectProtocol(request,'W',workshop,100)
    workshop.save()
    messages.error(request, "your workshop request has been deleted.")
    return redirect("my-workshop-status")



@login_required
def edit_workshop(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        work_form = WorkshopTempForm(instance = workshop)
        time_zone = pytz.all_timezones
        context = {
            "workshop":work_form,
            "the_workshop":workshop,
            'time_zone': time_zone,
            'user_balance':request.user.memberprofile.balance,
            'time_table':TimeTable.objects.filter(workshop=workshop).all()
        }
        if workshop.add_field != "":
            context['add_field'] = workshop.add_field
        return render(request, "workshop/edit_workshop.html",context)
    elif request.method == "POST":
        workshop = Workshop.objects.get(pk=pk)
        """if 'skills' in request.POST:
            return HttpResponse('hi')
        else:
            return HttpResponse('bye')"""
        data = request.POST.copy()
        # check image
        if 'demoImage' in request.POST:
            if request.POST.get('demoImage') != "":
                data['image'] = request.POST.get('demoImage')

        # check sub field
        if data['sub_field'] == '0':
            data['sub_field'] = None
        # add top user
        data['top_user'] = request.user
        workshop_form = WorkshopTempForm(data, request.FILES, instance=workshop)
        if workshop_form.is_valid():
            workshop = workshop_form.save(commit=False)

            # check image format
            if request.POST.get('demoImage') != None:
                return HttpResponse(request.POST.get('demoImage'))
                name = request.POST['demoImage']
                img_url = name.split('/')
                workshop.image = "workshop/demoImage/{name}".format(name = img_url[-1])
                print(workshop.image.url)
            else:
                image_name = workshop.image.name
                if image_name.endswith(".png") or image_name.endswith(".PNG") or image_name.endswith(".jpg")or image_name.endswith(".jpeg"):
                    pass
                else:
                    messages.error(request, "Your image format is invalid.")
                    return HttpResponseRedirect(request.path_info)
            
            # check file format
            """file_name = workshop.load_pdf.name
            if file_name.endswith(".docx") or file_name.endswith(".pptx") or file_name.endswith(".pdf"):
                pass
            else:
                messages.error(request, "Your file format is invalid, only use docx , pdf and pptx format.")
                return HttpResponseRedirect(request.path_info)"""
            
            # sub field handler
            sub_field = workshop.sub_field
            if sub_field == None:
                new_field = request.POST.get('add_field')
                workshop.add_field = new_field
            
            if workshop.status != 'Set_time_table':
                # change accept reject status
                accept_reject = AcceptReject.objects.get(workshop=workshop)
                accept_reject.is_edited = True
                accept_reject.save()

                # change workshop status
                workshop.status = "Manager_check"


                if request.POST.get('set_now') == "true":
                    for table in TimeTable.objects.filter(workshop=workshop).all():
                        table.delete()
                    table_list = request.POST.getlist('tblList')[0].split(',')
                    count=0
                    while count < len(table_list):
                        if count == 0:
                            workshop.date=table_list[count+2]
                            workshop.save()
                        title=table_list[count+1]
                        start_date=table_list[count+2]
                        start_time=table_list[count+3]
                        end_time=table_list[count+4]
                        duration=table_list[count+5]
                        price=int(table_list[count+6])
                        TimeTable.objects.create(title=title,start_date=start_date,start_time=start_time,price=price,
                                                end_time=end_time,duration=duration,workshop_id = workshop.id)
                        count=count+7


                #workshop log
                if Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).exists():
                    log=Workshop_log.objects.filter(workshop=workshop,status='Reject',is_done=False).first()
                    log.is_done=True;log.save()
                Workshop_log.objects.create(workshop=workshop,status='Manager_check',position='director'
                                            ,desc=Workshop_log.description.Manager_check_from_supervisor)
            else:
                if request.POST.get('set_now') == "true":
                    table_list = request.POST.getlist('tblList')[0].split(',')
                    my_list = []
                    list_size = len(table_list)
                    for i in range(0,list_size,6):
                        my_list.append(table_list[i:i+6])
                        
                        
                    # set date, time_to_start & duration
                    work_date = "{d} {t}".format(d = my_list[0][2], t = my_list[0][3])
                    
                    final_date = datetime.strptime(work_date, '%Y-%m-%d %H:%M')
                    workshop.date = final_date.date()
                    workshop.time_to_start = final_date.time()
                    
                    # duration part
                    timeList = []
                    for time in my_list:
                        timeList.append(time[5])
                    
                    mysum = timedelta()
                    for i in timeList:
                        (h, m, s) = i.split(':')
                        d = timedelta(hours=int(h), minutes=int(m), seconds=int(s))
                        mysum += d
                    workshop.duration = str(mysum)
                    
                    # end    
                    
            
                    # with open('/home/tecvicoc/public_html/media/workshop/time_table/{name}.txt'.format(name = str(workshop.id) + '_time'),'w') as f:
                    #     for time in my_list:
                    #         for item in time:
                    #             f.write(item + ",")
                    #         f.write('\n')
                    #     f.close()
                    # time_file = 'workshop/time_table/{name}.txt'.format(name = str(workshop.id) + '_time')
                    # TimeTable.objects.create(workshop_id = workshop.id, information = time_file)
                    if workshop.guaranteed == None:
                        workshop.status = 'pay_guarante'
                    else:
                        workshop.status = 'New'
                    workshop.save()
                    
                    if workshop.status == 'pay_guarante':
                        # Notif
                        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Pending for paying responsibility fee.",
                                                    target = workshop.top_user,
                                                    link = reverse('my-workshop-status'))
                        # Email
                        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                        e_content = "Dear {creator}\nHello\nHope you are going well\nYou must pay $100 as responsibility fee if you would like to launch your workshop\nTitle: {title}\nDate: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, creator = workshop.top_user.get_full_name(), date = timezone.now().date())
                        e_destination = workshop.top_user.email
                        send_new_email(e_subject,e_content,e_destination)
                        
                    elif workshop.status == 'New':
                        # Notif User
                        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Pending for guarantor's approval.",
                                                    target = workshop.top_user,
                                                    link = reverse('my-workshop-status'))
                        # Email User
                        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                        e_content = "Dear {creator}\nHello\nHope you are going well.\nYour request has successfully been sent to {name} in order to guarantee you. If the guarantor declines your request, you must pay responsibility fee to hold the workshop.\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), name = workshop.guaranteed, creator = workshop.top_user.get_full_name())
                        e_destination = workshop.top_user.email
                        send_new_email(e_subject,e_content,e_destination)
                        
                        
                        # Notif Guarantor
                        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "You are requested as a guarantor for this workshop.",
                                                    target = workshop.guaranteed.user,
                                                    link = reverse('guarante-request'))
                        
                        # Email Guarantor
                        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                        e_content = "Dear {guarantor}\nHello\nHope you are going well\nYou are selected as a guarantor for this workshop.\n\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), guarantor = workshop.guaranteed)
                        e_destination = workshop.guaranteed.user.email
                        send_new_email(e_subject,e_content,e_destination)
                    
                    messages.success(request, 'Your workshop request has been submitted successfully.')
                    return redirect(reverse('my-workshop-status'))
                else:
                    workshop.save()
                    messages.success(request, "Your workshop has been saved successfully, please set timetable soon.")
                    return redirect(reverse('my-workshop-status'))

            workshop.save()
            messages.success(request, "Your workshop has been edited successfully.")
            return redirect("my-workshop-status")
        else:
            print(workshop_form.errors)
            messages.error(request, workshop_form.errors)
            return HttpResponseRedirect(request.path_info)



"""@login_required
def edit_workshop(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        context = {
            "workshop":workshop,
        }
        return render(request, "workshop/edit_my_workshop.html",context)
    
    if request.method == "POST":
        new_workshop = Workshop.objects.get(pk=pk)
        if request.POST.get('title') is None or request.POST.get('title').strip() == "":
            messages.error(request, "error: Title is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.title = request.POST.get('title')

        if request.POST.get('price') is None or request.POST.get('price').strip() == "":
            messages.error(request, "error: price is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.price = request.POST.get('price')

        if request.POST.get('date') is None:
            messages.error(request, "error: date is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.date = request.POST.get('date')

        if request.POST.get('duration') is None or request.POST.get('duration').strip() == "":
            messages.error(request, "error: duration is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.duration = request.POST.get('duration')

        if request.POST.get('time_to_start') is None or request.POST.get('time_to_start').strip() == "":
            messages.error(request, "error: time_to_start is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.time_to_start = request.POST.get('time_to_start')

        if request.POST.get('address') is None:
            messages.error(request, "error: address is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.address = request.POST.get('address')

        if request.POST.get('description') is None or request.POST.get('description').strip() == "":
            messages.error(request, "error: description is empty.")
            return HttpResponseRedirect(request.path_info)
        else:
            new_workshop.description = request.POST.get('description')

        if request.POST.get('demoImgUrl'):
            imageNameList = request.POST.get('demoImgUrl').split("/")
            imageName=imageNameList[-1]
            new_workshop.image =  "workshop/demoImage/" +imageName
        elif request.FILES.get('image'):
            file = request.FILES['image']
            name = file.name
            if name.endswith(".png") or name.endswith(".jpg")or name.endswith(".jpeg"):
                path = f"media/workshop/{file.name}"
                with open(path,"wb+") as dest:
                   for chunk in file.chunks():
                       dest.write(chunk)
                new_workshop.image = f"workshop/{file.name}"
            else:
                messages.error(request, "error: image format is invalid.")
                return HttpResponseRedirect(request.path_info)
        else:
            pass
        
        if request.FILES.get('load_pdf'):
            file = request.FILES['load_pdf']
            name = file.name
            if name.endswith(".pdf") or name.endswith(".pptx"):
                path = f"media/workshop/{file.name}"
                with open(path,"wb+") as dest:
                    for chunk in file.chunks():
                        dest.write(chunk)
                new_workshop.load_pdf = f"workshop/{file.name}"
            else:
                messages.error(request, "error: document is invalid.")
                return HttpResponseRedirect(request.path_info)
        else:
            pass

        accept_reject = AcceptReject.objects.get(workshop=new_workshop)
        accept_reject.is_edited = True
        accept_reject.save()
        new_workshop.status = "Manager_check"
        new_workshop.save()
        # re_submission email
        e_subject = "TECVICO workshop"
        e_content = "Dear {creator}\nHello\nHope you are going well.\nThe workshop manager will be reviewed your workshop request.\nTitle: '{title}' Submitted on '{date}'\nI write this letter to thank you for showing interest in working with us. Your workshop request needs a revision because “Please put revision.We will consider you request after resubmission.\nThank you for your efforts and time. We hope to work with you on this workshop.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nWorkshop director".format(title = new_workshop.title, date = new_workshop.created.date(), creator = new_workshop.top_user)
        e_destination = new_workshop.top_user.email
        send_new_email(e_subject,e_content,e_destination)
        messages.success(request, "Your workshop request has been edited successfully.")
        return redirect('my-workshop-status')"""

@login_required
def expert_approve_decline(request, pk):
    if request.method == 'POST':
        comment = Comment.objects.get(expert = request.user, pk = pk)
        workshop = Workshop.objects.get(id = comment.workshop.id)
        roles = Role.objects.filter(position = 'workshop manager')
        status = request.POST.get('status')
        if status == 'Decline':
            comment.status = 'Decline'
            comment.comment = request.POST.get('comment')
            comment.save()
            workshop.status = 'Guarante_accept'
            workshop.save()
            log=Workshop_log.objects.filter(workshop=workshop,status='Expert_decide',is_done=0).first()
            log.is_done=1;log.save()
            Workshop_log.objects.create(workshop=workshop,position='director',status='reject_expert',
                                            desc=Workshop_log.description.reject_expert,is_done=0)
            
            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The expert, namely {expert}, has declined your request to undertake the project.\nClick on this message to see the information.".format(expert = comment.expert.get_full_name()),
                                            target = role.user,
                                            link = reverse('manager-workshop'))
    
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = ""
                for user_role in comment.expert.role.all():
                    if user_role.position == 'workshop expert': 
                        e_content = "Dear {manager}\nHello\nHope you are going well.\n\nThe expert, {expert}, has unfortunately declined your request to undertake this workshop.\nTitle: {title}\nSubmitted date: {date}\nExpert's comment(s): {expert_comment}. \nIf you have more questions or concerns, contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, expert_email = user_role.email ,expert = comment.expert.get_full_name(), expert_comment = comment.comment , date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request, 'The workshop request has been declined.')
            return redirect('expert-workshop')
            
        elif status == 'Approve':
            comment.status = 'Approve'
            comment.save()
            workshop.status = 'Expert_comment'
            workshop.save()
            log=Workshop_log.objects.filter(workshop=workshop,status='Expert_decide',is_done=0).first()
            if log:
                log.is_done=1;log.save()
            Workshop_log.objects.create(workshop=workshop,position='expert',status='Expert_comment',
                                            desc=Workshop_log.description.Expert_comment,is_done=0)
            
            # for manager
            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The expert, {expert}, has approved your request to undertake the project.\nClick on this message to see the information.".format(expert = comment.expert.get_full_name()),
                                            target = role.user,
                                            link = reverse('manager-workshop'))
    
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {manager}\nHello\nHope you are going well.\n\nThe expert, {expert}, has approved your request to undertake this workshop.\nTitle: {title}\nSubmitted date: {date}\n\nThank you.\n\nSincerely,\n\nTECVICO Corp".format(title = workshop.title, expert = comment.expert.get_full_name(), date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)
            
            # for expert
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Thank you for accepting workshop director's request.\nWe are looking forward to see your evaluation in 2 days.\nClick on this message to see the information.",
                                        target = role.user,
                                        link = reverse('expert-workshop'))
            
            if comment.access == False:
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {expert}\nHello\nHope you are going well.\n\nThank you for accepting workshop director's request.\nYou are selected as a workshop expert on this project. We are looking forward to see your evaluation in 2 days.\nTitle: {title}\nSubmitted date: {date}\n\nYou are also  requested to observe progress of the workshop and do the assigned tasks on it. You must observe on how well the steps of the workshop are going forward. You should solve some issues which you can do\nIf the problem is difficult, you should transfer it to the workshop director. You are also expected to give the regular report on this project to the director.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nSincerely,\n\nTECVICO Corp".format(title = workshop.title, expert = comment.expert.get_full_name(), date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)
            else:
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {expert}\nHello\nHope you are going well.\n\nThank you for accepting workshop director's request.\nYou are selected as a workshop expert on this project. We are looking forward to see your evaluation in 2 days.\nTitle: {title}\nSubmitted date: {date}\n\nYou are also  requested to observe progress of the workshop and do the assigned tasks on it. You must observe on how well the steps of the workshop are going forward. You should solve some issues which you can do\nIf the problem is difficult, you should transfer it to the workshop director. You are also expected to give the regular report on this project to the director.\nMeanwhile, you are given an access to accept or reject the workshop.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nSincerely,\n\nTECVICO Corp".format(title = workshop.title, expert = comment.expert.get_full_name(), date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)

            messages.success(request, 'The workshop request has been approved.')
            return redirect('expert-workshop')
        else:
            messages.error(request, 'Something wrong!!')
            return HttpResponseRedirect(request.path_info)



@login_required
def show_supervisor_detail(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        accept_reject=AcceptReject.objects.filter(workshop=workshop,approve_contract=True).first()
        comment=Comment.objects.filter(workshop=workshop,status="Revise_contract_to_supervisor").first()
        if Adverstiment.objects.filter(workshop=workshop).exists():
            adverstiment=Adverstiment.objects.filter(workshop=workshop).first()
            if adverstiment.contracts:
                workshop.contract=adverstiment.contracts

        context = {
            "workshop":workshop,
            'accept_reject':accept_reject,
            'comment':comment
        }
        
        if workshop.status != 'Set_time_table':
            # show time table
            workshop_time_table = TimeTable.objects.filter(workshop_id = workshop.id)
            context["time_table"] = workshop_time_table
        
        return render(request, "workshop/show_supervisor_detail.html", context)


@login_required
def add_workshop_for_user(request, pk):
    if request.method == "GET":
        workshopss = Workshop.objects.all()
        user = request.user
        try:
            user_work = Users_Workshops.objects.get(workshop_id=pk, user=user)
        except:
            user_workshop = Users_Workshops(workshop_id=pk, user=user, is_paid=False).save()
        
        workshops_idies = Users_Workshops.objects.filter(user=user)
        workshops = []
        """for item in workshops_idies:
            for workshop in workshopss:
                if id.workshop_id == workshop.id:
                    workshops.append(workshop)"""
        for item in workshops_idies:
            workshops.append(item.workshop)
        context = {
            "workshops":workshops
        }
        return render(request, "workshop/my_workshop_signuped.html", context)


@login_required
def my_workshop_signuped(request):
    if request.method == "GET":
        workshopss = Workshop.objects.all()
        user = request.user
        workshops_idies = Users_Workshops.objects.filter(user=user)
        workshops = []
        """for id in workshops_idies:
            for workshop in workshopss:
                if id.workshop_id == workshop.id:
                    workshops.append(workshop)"""
        for item in workshops_idies:
            workshops.append(item.workshop)
        now_time = timezone.localdate()
        context = {
            "workshops":workshops,
            "time":now_time
        }
        return render(request, "workshop/my_workshop_signuped.html", context)

@login_required
def show_workshop_video(request, pk, number):
    if request.method == "GET":
        link = ""
        workshop = Workshop.objects.get(pk=pk)
        workshop_time_table = TimeTable.objects.get(workshop_id = workshop.id)
        with open('/home/tecvicoc/public_html/media/' + str(workshop_time_table.information),'r') as f:
            final_list = []
            my_list = f.read().splitlines()
            for items in my_list:
                final_list.append(items.split(','))
            f.close()
        for item in final_list:
            if int(item[0]) == int(number):
                link = item[6]
                break
        context = {
            "video_link":link,
        }
        return render(request, "workshop/show_workshop_video.html", context)

@login_required
def is_login(request, pk):
    if request.method == "GET":
        balance = request.user.memberprofile.balance 
        workshop = Workshop.objects.get(pk=pk)
        # return HttpResponse(request.GET)
        if request.GET:
            section=request.GET['section']
            user_workshop=Users_Workshops.objects.filter(user=request.user, workshop_id=workshop.id,section=section).first()
            if user_workshop is None:
                Users_Workshops.objects.create(user=request.user, workshop_id=workshop.id, is_paid=False,section=section)
            workshop_Section=TimeTable.objects.filter(workshop=workshop,title=section).first()
            price=workshop_Section.price
            action='buy-{}'.format(section)
        else:
            user_workshop=Users_Workshops.objects.filter(user=request.user, workshop_id=workshop.id,section='All').first()
            if user_workshop is None:
                Users_Workshops.objects.create(user=request.user, workshop_id=workshop.id, is_paid=False,section='All')
            price=workshop.price
            action='buy-All'
        return PaymentProtocol(request,'W',workshop,price,action)
        # context = {
        #     "balance":balance,
        #     "workshop":workshop
        # }
        # return render(request, "workshop/payment.html", context)


@login_required
def show_workshops_for_expert(request):
    expert_workshop = Comment.objects.filter(expert = request.user)
    workshops = []
    for work in expert_workshop:
        if work.workshop.status == "Accept":
            workshops.append(work.workshop)
    context = {
        "workshops":workshops
    }
    return render(request, "workshop/show_workshop_for_expert.html", context)

@login_required
def view_registrants_workshop(request, pk):
    user_workshops = Users_Workshops.objects.filter(workshop_id=pk)
    workshop = Workshop.objects.get(pk = pk)
    timetable=TimeTable.objects.filter(workshop=workshop)
    if request.method == "GET":
        users = []
        for item in user_workshops:
            users.append(item)
        context = {
            "users":users,
            "workshop": workshop,
            'timetable':timetable
        }
        return render(request, "workshop/view_registrants_workshop.html", context)
    if request.method == "POST":
        e_subject = request.POST.get('subject')
        e_content = request.POST.get('description')
        for item in user_workshops:
            e_destination = item.user.email
            send_new_email(e_subject,e_content,e_destination)
        messages.success(request, 'Email has been sent successfully.')
        return HttpResponseRedirect(request.path_info)

@login_required
def pay(request, pk):
    if request.method == "POST":
        workshop = Workshop.objects.get(pk=pk)
        member = MemberProfile.objects.get(user = request.user)
        if Users_Workshops.objects.filter(user=request.user, workshop_id=workshop.id, is_paid=True).exists():
            messages.error(request, "You already paied the attendence fee.")
            return redirect(reverse('is-login', args=[workshop.pk]))
        else:
            if member.balance < int(workshop.price):
                return redirect('create-checkout-session')
            else:
                member.balance -= int(workshop.price)
                member.save()
            Users_Workshops.objects.create(user=request.user, workshop_id=workshop.id, is_paid=True)
        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Your payment for this workshop was successful.",target = request.user,link = reverse('show-workshops-to-users'))
        # Email
        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
        e_content = "Dear {creator}\nHello\nHope you are going well.\n\nTitle: '{title}' Submitted on '{date}'\n\nYou used '{price}' of your balance. Here is the invoice for your payment.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through payment@tecvico.com.\n\nThank you for your trust.\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = request.user, price = workshop.price)
        e_destination = request.user.email
        send_new_email(e_subject,e_content,e_destination)
        
        messages.success(request, 'The payment has been recieved successfully.')
        url = reverse("show-workshops-to-users") + "?filter=my-workshop"
        return redirect(url)
        #return redirect(reverse("show-workshops-to-users"))


def done_workshops(request):
    if request.method == "GET":
        acc_rejs = AcceptReject.objects.filter(is_accept=True)
        workshops = []
        for acc in acc_rejs:
            workshops.append(acc.workshop)
        dones = True
        now_time = timezone.localdate()
        context = {
            "workshops":workshops[:4],
            "dones":dones,
            "time":now_time,
           
        }
        return render(request, "workshop/list-for-all.html", context)

@login_required
def done_workshops_for_expert(request):
    if request.method == "GET":
        acc_rejs = AcceptReject.objects.filter(is_accept=True)
        workshops = []
        for acc in acc_rejs:
            workshops.append(acc.workshop)
        now_time = timezone.localdate()
        context = {
            "workshops":workshops,
            "time":now_time
        }
        return render(request, "workshop/done_workshops_for_expert.html", context)


@login_required
def upload_video(request, pk):
    workshop = Workshop.objects.get(pk=pk)
    if request.method == "POST":
        workshop.video = request.POST.get('video_link')
        workshop.save()
        messages.success(request, "A video has been added successfully.")
        #return HttpResponseRedirect(request.path_info)
        url = reverse("expert-workshop") + '?filter=add-video'
        return redirect(url)


def add_video_workshop(request, pk):
    workshop = Workshop.objects.get(pk=pk)
    if request.method == "GET":
        # show time table
        workshop_time_table = TimeTable.objects.filter(workshop_id = workshop.id)
        context = {
            "workshop":workshop,
            "time_table": workshop_time_table,
        }
        return render(request, "workshop/add_workshop_video.html", context)
    if request.method == "POST":
        video_link = request.POST.get('video_link')
        video_id = request.POST.get('video_id')
        workshop_time_table = TimeTable.objects.get(id=video_id,workshop_id = workshop.id)
        workshop_time_table.video_link=video_link
        workshop_time_table.save()
        # with open('/home/tecvicoc/public_html/media/' + str(workshop_time_table.information),'r') as f:
        #     time_list = []
        #     my_list = f.read().splitlines()
        #     for item in my_list:
        #         time_list.append(item.split(','))
        #     #return HttpResponse(time_list)
        #     for item in time_list:
        #         if item[0] == video_id:
        #             item[6] = video_link
        #     f.close()
        # #return HttpResponse(time_list)
        # with open('/home/tecvicoc/public_html/media/' + str(workshop_time_table.information),'w') as f:
        #     for time in time_list:
        #         for item in time:
        #             f.write(item+",")
        #         f.write('\n')
        #     workshop_time_table.information = f
        #     f.close()
            
            
                
        
        messages.success(request, "The video(s) have been added successfully.")
        url = reverse("expert-workshop") + '?filter=add-video'
        return redirect(url)

@login_required
def completing_my_workshop(request):
    if request.method=="GET":
        workshops = Workshop.objects.filter(top_user=request.user)
        now_time = timezone.localdate()
        context = {
            "time":now_time,
            "workshops":workshops
        }
        return render(request, "workshop/completing_list.html", context)


@login_required
def add_workshop_file(request, pk):
    if request.method == "POST":
        workshop = Workshop.objects.get(pk=pk)
        if request.FILES.get("file"):
            file = request.FILES['file']
            path = f"media/workshop/{file.name}"
            with open(path,"wb+") as dest:
                for chunk in file.chunks():
                    dest.write(chunk)
            workshop.load_pdf = f"workshop/{file.name}"
            workshop.save()
        else:
            messages.error(request, "Error: Unable to upload the file.")

        redir = reverse("completing-my-workshop")
        return HttpResponseRedirect(redir)

def Guarante_request(request):
    guarante = Guarante.objects.get(user = request.user)
    workshop = Workshop.objects.filter(guaranteed = guarante, status = "New")
    context = {
        "workshops" : workshop,
    }
    return render(request, "workshop/guarante_request.html", context)

def guarante_accept_reject(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        context = {
            "work": workshop,
        }
        return render(request,"workshop/guarante_accept_reject.html",context)
    
    elif request.method == "POST":
        workshop = Workshop.objects.get(pk=pk)
        roles = Role.objects.filter(position = 'workshop manager')
        if request.POST.get("status") == "Guarante_accept":
            workshop.status = "Guarante_accept"
            
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Your guarantee request has been approved.\nYour workshop is under proccess.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nGood news! Your guarantee request has been approved by '{guarantor}'. The workshop team will review your request and inform you.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), guarantor = workshop.guaranteed, creator = workshop.top_user.get_full_name())
            #e_content = "Dear {creator}\nHello\nHope you are going well.\n\nGood news! Your guarantee request has been accepted . The workshop team will review your request and inform you.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), creator = instance.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            
            # Notif guarantor
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "You approved the workshop as a guarantor.",
                                        target = workshop.guaranteed.user,
                                        link = '')
            
            # Email for guarantor
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = "Dear {guarantor}\nHello\nHope you are going well.\n\nThank you for accepting the guatrantee request. We hope the workshop is being gone well.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), guarantor = workshop.guaranteed)
            e_destination = workshop.guaranteed.user.email
            send_new_email(e_subject,e_content,e_destination)

            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "A new workshop has been added to your list.\nClick on this message to see the information.",
                                            target = role.user,
                                            link = reverse('manager-workshop'))

                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {manager}\nHello\nHope you are going well.\n\nThe guarantee request from '{creator}' on workshop '{title}' submitted in '{date}' has been accepted by '{guarantor}'. Please go to your dashboard and associate an expert with this workshop.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, creator = workshop.top_user.get_full_name(), guarantor = workshop.guaranteed, date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)
        else:
            workshop.status = "pay_guarante"
            
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Your Guarantee request has been declined.\nYou must pay responsibility fee to launch.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = "Dear {creator}\nHello\nHope you are going well.\nTitle: '{title}'\nSubmitted on '{date}'\n\nThank you for requesting to the guarantor. I regret to inform you that the guarantor has declined your request.\nTo continue your workshop submission, please go to your dashboard and pay the responsibility fee.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nWorkshop director".format(title = workshop.title, date = workshop.created.date(), creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            
            #Notif for guarantor
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "You declined the request to be as a guarantor.",
                                        target = workshop.guaranteed.user,
                                        link = '')

            # email for guarantor
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = e_content = "Dear {guarantor}\nHello\nHope you are going well.\n\nYou has declined the workshop gaurantor request. Thank you.\n\nTitle: '{title}'\nSubmitted date: '{date}'. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), guarantor = workshop.guaranteed)
            e_destination = workshop.guaranteed.user.email
            send_new_email(e_subject,e_content,e_destination)
            
        workshop.save()
        return redirect('guarante-request')


def guarante_pay(request, pk):
    if request.method == "GET":
        workshop = Workshop.objects.get(pk=pk)
        context = {
            "work": workshop,
        }
        return render(request,"workshop/guarante_pay.html",context)
    
    elif request.method == "POST":
        roles = Role.objects.filter(position = 'workshop manager')
        workshop = Workshop.objects.get(pk=pk)
        member = MemberProfile.objects.get(user = request.user)
        workshop.status='Notpay'
        workshop.save()
        log=Workshop_log.objects.filter(workshop=workshop,status='pay_guarante').first()
        log.is_done=1;log.save()
        Workshop_log.objects.create(workshop=workshop,position='supervisor',status='Notpay',
                                            desc=Workshop_log.description.Notpay,is_done=0)
        return PaymentProtocol(request,'W',workshop,100,action='create')
        
        
def view_expert_workshop(request):
    comments = Comment.objects.filter(expert=request.user)
    comment_workshop = []
    acc_work_ex = []
    add_video = []
    accept_reject = []
    ws_accp_contr=[]
    contracts=[]
    for cm in comments:
        if cm.status == "Approve" or "Approve_contract":
            if cm.workshop not in acc_work_ex:
                acc_work_ex.append(cm.workshop)
            if cm.workshop.status == 'Revise_to_expert' and cm.is_checked:
               comment_workshop.append(cm) 

        if cm.status == "Approve" or "Approve_contract" and cm.workshop.status != 'Accept':
            if cm.workshop not in ws_accp_contr:
                ws_accp_contr.append(cm.workshop)


        if (cm.is_checked==False and cm.status != 'Decline'
            and cm.status !='Approve_contract'
            and cm.status!='Revise_contract_to_supervisor'
            and cm.status!='Revise_contract_to_expert'):
            comment_workshop.append(cm)
        if cm.workshop.status == "Accept" and cm.status == "Approve":
            #acc_work_ex.append(cm.workshop)
            if cm.workshop.date <= timezone.now().date():
                add_video.append(cm.workshop)
        if cm.access == True and cm.status == "Approve":
            if cm.workshop.status == "Manager_check" :
                accept_reject.append(cm)

    for landingpage in LandingPage.objects.all():
        for workshop in acc_work_ex:
            if workshop == landingpage.workshop:
                workshop.landing_page=landingpage

    for wp in ws_accp_contr:
        if AcceptReject.objects.filter(workshop=wp,approve_contract=True).exists():
            contracts.append(AcceptReject.objects.filter(workshop=wp,approve_contract=True).first())


    context = {
        "add_comment": reversed(comment_workshop),
        "comment_number": len(comment_workshop),
        
        "accept_reject": reversed(accept_reject),
        "accept_reject_number": len(accept_reject),

        "accepted": reversed(acc_work_ex),
        "acc_number": len(acc_work_ex),

        "add_video": reversed(add_video),
        "add_video_number": len(add_video),

        "contracts":reversed(contracts),
        "contracts_number":len(contracts),

        'status':EXPERT_STATUS
    }
    return render(request, "workshop/view_expert_workshop.html", context)


def view_manager_workshop(request):
    workshops = Workshop.objects.filter(status = "Guarante_accept")
    """decline_workshop = Comment.objects.filter(workshop__status = "Expert_decide", status = "Decline")
    new_list = []
    for item in new_workshops:
        new_list.append(item)
    decline_list = []
    for item in decline_workshop:
        decline_list.append(item.workshop)
    workshops = new_list + decline_list"""
    
    pending = []
    pending_list = Comment.objects.all()
    for item in pending_list:
        if item.workshop.status == 'Expert_comment' or item.workshop.status == 'Expert_decide':
            pending.append(item)
        elif item.workshop.status == 'Guarante_accept' and item.status == 'Decline':
            pending.append(item)

    acc_rej = Comment.objects.filter(workshop__status = "Manager_check", status = 'Approve')
    accept = Workshop.objects.all().order_by('-created')

    for i in accept:
        i.count=0
        i.count=Users_Workshops.objects.filter(workshop=i,is_paid=1).count()
        print(i.count)
    

    #For Landingpage Cart
    for landingpage in LandingPage.objects.all():
        for workshop in accept:
            if workshop == landingpage.workshop:
                workshop.landing_page=landingpage


    #For Contract Cart 

    include=['Approve_contract','Upload_contract','revise_contract_to_expert','send_contract_to_supervisor'
    ,'Revise_contract_to_supervisor','Send_contract_to_director','Send_contract_by_supervisor','Reject_contract_to_supervisor']            
    contracts=Workshop.objects.filter(status__in=include).all().order_by('-created')
    for contract in contracts:            
        for comment in Comment.objects.filter(workshop=contract,status="Approve").all():
            contract.expert=comment.expert


    context = {
        "new_workshop": workshops,
        "workshop_number": workshops.count(),
        
        "pending":pending,
        "pending_number": len(pending),

        "acc_rej":acc_rej,
        "acc_rej_number": acc_rej.count(),

        "accepted": accept,
        "accept_number": accept.count(),
        
        "contracts":contracts,
        "contracts_number":len(contracts),

        "status":DIRECTOR_STATUS
    }
    return render(request, "workshop/view_manager_workshop.html", context)


def generate_pdf(request):
    pk = request.POST.get('pk')
    if pk:
        form = Workshop.objects.get(pk = pk)
        user_phone = MemberProfile.objects.get(user = form.top_user)
        context = {
            "form":form,
            "user_phone": user_phone,
        }
        pdf = render_to_pdf('workshop/invoice.html', context)
        return HttpResponse(pdf, content_type='application/pdf')
    else:
        return HttpResponse("<h4>you came from a wrong way</h4>")

def show_ad_form(request, pk):
    workshop = Workshop.objects.get(pk = pk)
    user_phone = MemberProfile.objects.get(user = workshop.top_user)
    final_list = TimeTable.objects.filter(workshop_id = workshop.id)
    context = {
        "WorkForm": workshop,
        "user_phone": user_phone,
        "time_table": final_list,
    }
    return render(request, "workshop/ShowAdForm.html", context)



# ........lotfi


@login_required
def view_contract_supervisor(request,pk):
    template_name='workshop/view_contract_supervisor.html'
    workshop=get_object_or_404(Workshop,pk=pk)
    timetable=TimeTable.objects.filter(workshop=workshop).all()
    adverstiment=None
    if request.GET.get('filter') == 'edit':
        form =Advertisingform(request.POST or None,instance=Adverstiment.objects.filter(workshop=workshop).first())
        adverstiment=Adverstiment.objects.filter(workshop=workshop).first()
    else:
        if not Adverstiment.objects.filter(workshop=workshop).exists():
            form =Advertisingform()
        else:
            form=None

    if request.POST or request.FILES :
        if request.GET.get('filter') == 'edit':
            form=Advertisingform(instance=Adverstiment.objects.filter(workshop=workshop).first())
            title=request.POST.get('title')
            coursetitles=request.POST.get('coursetitles')
            courseclients=request.POST.get('courseclients')
            certificatedesc=request.POST.get('certificatedesc')
            formcontent=request.POST.get('content')
            coursespeakers=request.POST.get('coursespeakers')
            logo_image=request.FILES.get('logo_image')
            contracts=request.FILES.get('contracts')
            update_adverstiment=Adverstiment.objects.filter(workshop=workshop).first()
            update_adverstiment.title=title;update_adverstiment.coursetitles=coursetitles;update_adverstiment.courseclients=courseclients;      
            update_adverstiment.certificatedesc=certificatedesc;update_adverstiment.formcontent=formcontent;update_adverstiment.coursespeakers=coursespeakers;      
            if logo_image != None:
                update_adverstiment.logo_image=logo_image
            if contracts != None:
                update_adverstiment.contracts=contracts
            update_adverstiment.save()
        else:
            form=Advertisingform(request.POST)
            if form.is_valid():
                content=form.save()
                logo=request.FILES.get('logo_image')
                contract=request.FILES.get('contracts')
                content.workshop_id=request.POST.get('workshop_id')
                content.logo_image=logo
                content.contracts=contract
                content.save()
            else:
                print(form.errors)

        workshop.status="Send_contract_by_supervisor"
        workshop.save()
        expert=Comment.objects.filter(workshop=workshop,status='Approve_contract').first().expert

        #workshop_log
        if Workshop_log.objects.filter(workshop=workshop,status="Upload_contract",is_done=False).exists():
            log=Workshop_log.objects.filter(workshop=workshop,status="Upload_contract",is_done=False).first()
            log.is_done=True;log.save()

        if Workshop_log.objects.filter(workshop=workshop,status="Reject_contract_to_supervisor",is_done=False).exists():
            log=Workshop_log.objects.filter(workshop=workshop,status="Reject_contract_to_supervisor",is_done=False).first()
            log.is_done=True;log.save()

        if Workshop_log.objects.filter(workshop=workshop,status="Revise_contract_to_supervisor",is_done=False).exists():
            log=Workshop_log.objects.filter(workshop=workshop,status="Revise_contract_to_supervisor",is_done=False).first()
            log.is_done=True;log.save()

        Workshop_log.objects.create(workshop=workshop,status="Send_contract_by_supervisor",position='expert'
                                    ,desc=Workshop_log.description.Send_contract_by_supervisor)

        # Notif & Emaile To expert
        # Notif
        Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The Supervisor sent you the contract, Please review the contract and take the necessary actions .\nClick on this massage to see the rejection reasons.",
                                    target = expert,
                                    link = reverse('expert-workshop'))
        # Email
        e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)        
        e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'The Supervisor sent you the contract, Please review the contract and take the necessary actions.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), user_email = workshop.top_user.email, creator =expert.get_full_name())
        e_destination = expert.email
        send_new_email(e_subject,e_content,e_destination)  


        messages.success(request,'contract has been uploaded.')
        return redirect('my-workshop-status')

            
            

    context={
        'workshop':workshop,
        'time_table':timetable,
        'form':form,
        'adverstiment':adverstiment
    }

    return render(request,template_name,context)



@login_required
def view_contract_manager(request,pk):
    template_name="workshop/view_contract_manager.html"
    workshop=get_object_or_404(Workshop,pk=pk)
    if Adverstiment.objects.filter(workshop=workshop).exists():
        advrstiment=Adverstiment.objects.filter(workshop=workshop).first()
        workshop.contract=advrstiment.contracts
    timetable=TimeTable.objects.filter(workshop=workshop).all()

    if request.method == "POST":
        status=request.POST.get('status')
        if status == 'approve':

            workshop.status='Accept'
            workshop.save()

            #workshop log
            if Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').exists():
                log=Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').first()
                log.is_done=True;log.save() 
 
            Workshop_log.objects.create(workshop=workshop,status='Accept',position='---'
                                        ,desc=Workshop_log.description.Accept,is_done=True)
            #forum
            # create_forum_cat = Category.objects.create(
            # sub_category=MainCategory.objects.get(slug='workshop'),
            # img = workshop.image, slug="workshop-{}".format(workshop.id),
            # title=workshop.title)

            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Congratulations, your workshop has been accepted.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
            expert=Comment.objects.filter(workshop=workshop,status='Approve_contract').first().expert

            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nCongrats! Your request for holding the workshop '{title}' Submitted on '{date}' has been accepted. To hold your workshop, you must follow the workshop steps as below:\n1. You must prepare and finalize your content and upload it in two weeks after acceptance.\n2. You must record a video and upload it in two weeks after acceptance.\nNote: The advertisement team will start advertising after receiving the mention requirements.\n\n Please go to your dashboard and follow the workshop steps. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, expert_email =  expert.email ,date = workshop.created.date(), creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            messages.success(request,'Contract has been sent to supervisor')
            return redirect('manager-workshop')

        elif status == 'revise':

            comment=request.POST.get('revise_comment')
            expert=Comment.objects.filter(workshop=workshop,status='Approve_contract').first().expert
            Comment.objects.create(workshop=workshop,status='Revise_contract_to_expert',comment=comment,expert=expert)


            workshop.status='Revise_contract_to_expert'
            workshop.save()

            #workshop log
            if Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').exists():
                log=Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').first()
                log.is_done=True;log.save() 

            Workshop_log.objects.create(workshop=workshop,status='Revise_contract_to_expert',position='expert'
                                        ,desc=Workshop_log.description.REVISE_CONTRACT_TO_EXPERT)

            # Notif & Emaile To expert
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The Workshop manager sent you the contract for revise .\nClick on this massage to see the rejection reasons.",
                                        target = expert,
                                        link = reverse('expert-workshop'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)        
            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'The Workshop manager sent you the contract for revise.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(),  creator =expert.get_full_name())
            e_destination = expert.email
            send_new_email(e_subject,e_content,e_destination)

            messages.error(request,'Contract has been revised')
            return redirect('manager-workshop')
        
        elif status == 'reject':
    
            comment=request.POST.get('reject_comment')
            accept_reject=AcceptReject.objects.filter(workshop=workshop,approve_contract=True).first()
            accept_reject.comment=comment
            accept_reject.save()


            workshop.status='Reject_contract_to_supervisor'
            workshop.save()

            #workshop log
            if Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').exists():
                log=Workshop_log.objects.filter(workshop=workshop,is_done=False,status='Send_contract_to_director').first()
                log.is_done=True;log.save() 

            Workshop_log.objects.create(workshop=workshop,status='Reject_contract_to_supervisor',position='supervisor'
                                        ,desc=Workshop_log.description.Reject_contract_to_supervisor)

            # Notif & Emaile To supervisor
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The Workshop manager rejected contract to you .\nClick on this massage to see the rejection reasons.",
                                        target = workshop.top_user,
                                        link = reverse('expert-workshop'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)        
            e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'The Workshop manager rejected contract to you.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the workshop director through workshopdirector@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(),  creator =workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)

            messages.error(request,'Contract has been revised')
            return redirect('manager-workshop')

    context={
        'workshop':workshop,
        'time_table':timetable,
    }


    return render(request,template_name,context)




@login_required
def view_contract_expert(request,pk):
    template_name="workshop/view_contract_expert.html"
    workshop=get_object_or_404(Workshop,pk=pk)
    adverstiment=Adverstiment.objects.filter(workshop=workshop).first()
    timetabel=TimeTable.objects.filter(workshop=workshop).all()
    accept_reject=AcceptReject.objects.filter(workshop=workshop,approve_contract=True).first()

    if request.method == "POST":
        if request.POST.get('status') == 'revise_to_supervisor':
            comment=request.POST.get('revise_comment')
            contract=request.FILES.get('revise_contract')
            accept_reject.contract=contract
            accept_reject.save()

            workshop.status='Revise_contract_to_supervisor'
            
            if not  Comment.objects.filter(workshop=workshop,status="Revise_contract_to_supervisor").first():
                Comment.objects.create(status='Revise_contract_to_supervisor',comment=comment,workshop=workshop,expert=request.user,is_checked=True)
               
            else:
                comment_obj= Comment.objects.filter(workshop=workshop,status="Revise_contract_to_supervisor").first()
                comment_obj.comment=comment
                comment_obj.is_checked=True
                comment_obj.save()
            workshop.save()
            
            #workshop_log
            if Workshop_log.objects.filter(workshop=workshop,status='Send_contract_by_supervisor',is_done=False).exists():
                log=Workshop_log.objects.filter(workshop=workshop,status='Send_contract_by_supervisor',is_done=False).first()
                log.is_done=True;log.save()
            Workshop_log.objects.create(workshop=workshop,status='Revise_contract_to_supervisor',position='supervisor',
                                        desc=Workshop_log.description.Revise_contract_to_supervisor)

            # Notif & Emaile To Supervisor
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The expert sent you the contract for revise, please read it and send it after confirmation and signing .\nClick on this massage to see the rejection reasons.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
        
            e_content = "Dear {creator}\nHello\nHope you are going well.\nThe workshop team has reviewed your workshop request.\nTitle: '{title}' Submitted on '{date}'\nTECVICO writes this letter to thank you for showing interest in working with it. The expert wants the revising the contract, please read it and send it after confirmation and signing .\nThank you for your efforts and time. We hope to work with you in the near future.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date() ,expert_email = request.user.email, creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)


            messages.success(request,'contract has been sent for revising.')
            return redirect('expert-workshop')

        elif request.POST.get('status') == 'send_to_director':
            workshop.status='Send_contract_to_director'
            workshop.save()

            #workshop_log
            if Workshop_log.objects.filter(workshop=workshop,status='Send_contract_by_supervisor',is_done=False).exists():
                log=Workshop_log.objects.filter(workshop=workshop,status='Send_contract_by_supervisor',is_done=False).first()
                log.is_done=True;log.save()
            Workshop_log.objects.create(workshop=workshop,status='Send_contract_to_director',position='director',
                                        desc=Workshop_log.description.Send_contract_to_director)
            
            # Notif & Emaile To Supervisor
            # Notif
            roles = Role.objects.filter(position = 'workshop manager')
            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The expert sent to you the contract , please read it and if  confirmation changing status the workshop.\nClick on this message to see the information.",
                                            target = role.user,
                                            link = reverse('manager-workshop'))
                # Email
                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {manager}\nHello\nHope you are going well.\n\nThe expert called {{expert}} sent to you the contract , please read it and if  confirmation changing status the workshop.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format( manager = role.user.get_full_name(),expert=request.user)
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)

            messages.success(request,'contract has been sent to director.')
            return redirect('expert-workshop')

        elif request.POST.get('status') == 'send_to_supervisor':
            contract=request.FILES.get('contract')
            
            accept_reject.contract=contract
            accept_reject.save()

            workshop.status="Upload_contract"
            workshop.save()

            #workshop log
            if Workshop_log.objects.filter(workshop=workshop,status='Approve_contract',is_done=False).exists():
                log=Workshop_log.objects.filter(workshop=workshop,status='Approve_contract',is_done=False).first()
                log.is_done=True;log.save()

            Workshop_log.objects.create(workshop=workshop,status="Upload_contract",position='supervisor'
                                        ,desc=Workshop_log.description.Upload_contract)


            manager_list = Role.objects.filter(position = "workshop manager")
            user_manager = []
            for item in manager_list:
                user_manager.append(item.user)
            expert=Comment.objects.filter(workshop=workshop,status="Approve_contract").first().expert
            expert_email=expert.email
            # Notif & Emaile To Supervisor
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "The expert sent you the contract, please read it and send it after confirmation and signing .\nClick on this massage to see the rejection reasons.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = ""
        
            e_content = "Dear {creator}\nHello\nHope you are going well.\nThe workshop team has reviewed your workshop request.\nTitle: '{title}' Submitted on '{date}'\nTECVICO writes this letter to thank you for showing interest in working with it.  The expert sent you the contract, please read it and send it after confirmation and signing .\nThank you for your efforts and time. We hope to work with you in the near future.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date() ,expert_email = expert_email, creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)


            messages.success(request,'contract has been uploaded.')
            return redirect('expert-workshop')
            
    context={
        'workshop':workshop,
        'time_table':timetabel,
        'accept_reject':accept_reject,
        'adverstiment':adverstiment
    }

    return render(request,template_name,context)

def send_notif_email(pk,is_pay):
        roles = Role.objects.filter(position = 'workshop manager')
        workshop = Workshop.objects.get(pk=pk)
        if is_pay:
            workshop.status="Guarante_accept"
            workshop.save()
            log=Workshop_log.objects.filter(workshop=workshop,status='Notpay').first()
            log.is_done=1;log.save()
            Workshop_log.objects.create(workshop=workshop,position='director',status='Guarante_accept',
                                            desc=Workshop_log.description.Guarante_accept,is_done=0)
            # Notif
            Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "Thank you for paying the responsibility fee.\nWe will review your request and inform you soon.",
                                        target = workshop.top_user,
                                        link = reverse('my-workshop-status'))
            # Email            
            for role in roles:
                Notification.objects.create(title = "Workshop (ID: {u_id})".format(u_id = workshop.unique_id),description = "A new workshop has been added to your list.\nClick on this message to see the information.",
                                            target = role.user,
                                            link = reverse('add_expert', args=[workshop.pk]))

                e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
                e_content = "Dear {manager}\nHello\nHope you are going well.\n\nA new workshop '{title}' submitted in '{date}' has been created by '{creator}'. Please go to your dashboard and associate an expert with this workshop.\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, creator = workshop.top_user.get_full_name(), date = workshop.created.date(), manager = role.user.get_full_name())
                e_destination = role.user.email
                send_new_email(e_subject,e_content,e_destination)
                
            # email
            e_subject = "TECVICO workshop (ID: {u_id})".format(u_id = workshop.unique_id)
            e_content = "Dear {creator}\nHello\nHope you are going well.\nThank you for the payment of $100. We hope that you enjoy our Products/services! \nThe workshop team will review your request and inform you soon\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through workshop@tecvico.com.\n\nThank you\n\nBest regards\n\nTECVICO Corp".format(title = workshop.title, date = workshop.created.date(), creator = workshop.top_user.get_full_name())
            e_destination = workshop.top_user.email
            send_new_email(e_subject,e_content,e_destination)
            
def view_workshop_persian(request):
        return render(request,"workshop/view-workshop-persian.html")


@login_required
def create_landingpage(request,pk):
    manager,expert=check_role(request)
    if manager==True or expert == True:
        workshop=Workshop.objects.get(id=pk)
        template_name='workshop/create-landingpage.html'
        form=Landingpageform()
        if request.method == 'POST':
            title=request.POST.get('title')
            direction=request.POST.get('direction')
            coursetitles_title=request.POST.get('coursetitles_title')
            coursetitles=request.POST.get('coursetitles')
            courseclients_title=request.POST.get('courseclients_title')
            courseclients=request.POST.get('courseclients')
            certificate_title=request.POST.get('certificate_title')
            certificatedesc=request.POST.get('certificatedesc')
            content=request.POST.get('content')
            coursespeakers_title=request.POST.get('coursespeakers_title')
            coursespeakers=request.POST.get('coursespeakers')
            registeration_title=request.POST.get('registeration_title')
            registeration_content=request.POST.get('registeration_content')
            logo_image=request.FILES.get('logo_image')
            banner_image=request.FILES.get('banner_image')

            new_landingpage=LandingPage.objects.create(
                direction=direction,title=title,coursetitles_title=coursetitles_title,coursetitles=coursetitles,courseclients_title=courseclients_title,courseclients=courseclients,
                certificate_title=certificate_title,certificatedesc=certificatedesc,content=content,coursespeakers_title=coursespeakers_title,
                coursespeakers=coursespeakers,registeration_title=registeration_title,registeration_content=registeration_content,
                logo_image=logo_image,banner_image=banner_image, workshop=workshop,
            )

            messages.success(request,'Landingpage has been created')
            return redirect('view-workshop',pk=pk)



        context={
            'form':form
        }
        return render(request,template_name,context)
    else:
        return render(request,'workshop/access-denied.html')


@login_required
def delete_landingpage(request):
    manager,expert=check_role(request)
    if manager==True or expert == True:
        if request.method=='POST':
            id=request.POST.get('id')
            landing_page=LandingPage.objects.filter(pk=id).first()
            if landing_page:
                landing_page.delete()
                messages.error(request,'Landing page has been deleted')
        return redirect(request.META.get('HTTP_REFERER'))
        # return redirect('../../../workshop/manager/?filter=workshop-advertisement')
    else:
        return render(request,'workshop/access-denied.html')


@login_required
def edit_landingpage(request,pk):
    manager,expert=check_role(request)
    if manager==True or expert == True:
        landingpage=get_object_or_404(LandingPage,pk=pk)
        template_name='workshop/edit-landingpage.html'
        form=Landingpageform(request.POST or None,instance=landingpage)
        if request.POST or request.FILES  and form.is_valid():
            form.save()
            logo_image=request.FILES.get('logo_image')
            banner_image=request.FILES.get('banner_image')
            if logo_image:
                landingpage.logo_image=logo_image
                landingpage.save()
            if banner_image:
                landingpage.banner_image=banner_image
                landingpage.save()
            messages.success(request,'Landingpage has been updated')
            return redirect(request.META.get('HTTP_REFERER'))
        context={
            'landing_page':landingpage,
            'form':form
        }
        return render(request,template_name,context)
    else:
        return render(request,'workshop/access-denied.html')


def view_landingpage(request,pk):
    template_name='workshop/landingpage.html'
    context={
        'content':get_object_or_404(LandingPage,id=pk),       
    }

    return render(request,template_name,context)


@login_required
def upload_certificate(request,pk):
    manager,expert=check_role(request)
    if manager==True or expert == True:

        if request.method=="GET":
            user_workshop=get_object_or_404(Users_Workshops,pk=pk)
            if request.GET.get('delete'):
                if os.path.isfile(user_workshop.certificate.path):
                    os.remove(user_workshop.certificate.path)
                user_workshop.certificate='deleted'
                user_workshop.save()
                messages.error(request,'Certificate has been deleted')
            return redirect(request.META.get('HTTP_REFERER'))


        if request.method == "POST":
            user_workshop=get_object_or_404(Users_Workshops,pk=pk)
            certificate=request.FILES.get('certificate')
            user_workshop.certificate=certificate
            user_workshop.save()
            messages.success(request,'Certificate has been uploaded')
            return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request,'workshop/access-denied.html')




def download_certificate(request,pk):
    # fill these variables with real values
    user_workshop=get_object_or_404(Users_Workshops,pk=pk)
    path = user_workshop.certificate.path
    return download_file(request,path,'certificate.jpeg')



def workshop_history(request,pk):
    manager,expert=check_role(request)
    if manager == True or expert == True:
        template_name='workshop/workshop_history.html'
        workshop=get_object_or_404(Workshop,pk=pk)
        time_table=TimeTable.objects.filter(workshop=workshop)
        log=Workshop_log.objects.filter(workshop=workshop).order_by('created')
        context={
            'time_table':time_table,
            'workshop':workshop,
            'log':log
        }
        return render(request,template_name,context)
    else:
        return render(request,'workshop/access-denied.html')


