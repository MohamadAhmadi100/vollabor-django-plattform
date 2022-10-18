from enum import unique
from time import strftime
from urllib import request
from django.contrib import messages
from django.shortcuts import render,redirect,get_object_or_404
from django.http import HttpResponse,JsonResponse
from django.views.generic import View,DetailView,ListView
from .mixins import ManagerMixin,ExpertManagerMixin
from dashboard.models import ContractItem, Notification
from workshop.views import view_contract_supervisor
from .models import *
from users.models import Role
import pytz
from django.utils.translation import gettext_lazy as _
from .emails import virtualevent_Send_NotifEmail
from django.utils import timezone
import datetime
from accounting.models import PaymentProtocol,Invoice
from django.contrib.auth.decorators import login_required
from .functions import html_to_pdf
from django.views.decorators.cache import cache_control




#ROLES IN VIRTUAL EVENT
""" Manager:virtual manager
    Expert:virtual expert
"""


# Create your views here.
def load_field(request):
    main_field = request.GET.get('main_field')
    if main_field != "":
        sub_field = SubField.objects.filter(parent_id=main_field)
    else:
        sub_field = SubField.objects.none()
    return render(request, 'forms/field_dropdown_list_options.html', {'sub_field': sub_field})

def Mainfield_adding(request):
    if request.method=="POST":
        mainfield_id=int(request.POST.get('main_id'))
        main_title=request.POST.get('main_title')
        sub_title=request.POST.get('sub_title')
        if mainfield_id == -100 :
            newmainfield=MainField.objects.create(title=main_title,user_add=True)
            newsubfield=SubField.objects.create(title=sub_title,user_add=True,parent=newmainfield) 
            result={'main_id':newmainfield.id,'sub_id':newsubfield.id}
        else:
            mainfield=MainField.objects.filter(id=mainfield_id).first()
            if not mainfield:
                result={'error':'There is no mainfield with id'}
            else:
                newsubfield=SubField.objects.create(title=sub_title,user_add=True,parent=mainfield)
                result={'main_id':mainfield.id,'sub_id':newsubfield.id}
        return JsonResponse(result)   

#----------------------------------------------Create virtual event----------------------------------------------------------------------------
class ContractAccept(View):
    template_name='contract/show_contract.html'

    @cache_control(no_cache=True, must_revalidate=True)
    def get(self, request,*args,**kwargs):
        virtual_event=get_object_or_404(VirtualEvent,id=kwargs['pk'])
        if virtual_event.type == 'course':
            virtual_event.object=Course.objects.get(unique_id=virtual_event.unique_id)
        elif virtual_event.type == 'workshop':
            virtual_event.object=Workshop.objects.get(unique_id=virtual_event.unique_id)
        elif virtual_event.type == 'webinar':
            virtual_event.object=Seminar.objects.get(unique_id=virtual_event.unique_id)
        virtual_event.time_table=Timetable.objects.filter(vitual_event=virtual_event.id)
        return render(request,self.template_name,{'object':virtual_event})

    def post(self,request,*args,**kwargs):
        virtual_event=get_object_or_404(VirtualEvent,pk=int(request.POST.get('id')))
        if virtual_event.contract:
            messages.success(request,'You have already accepted this agreement.')
        else: 
            if virtual_event.type == 'course':
                virtual_event.object=Course.objects.get(unique_id=virtual_event.unique_id)
            elif virtual_event.type == 'workshop':
                virtual_event.object=Workshop.objects.get(unique_id=virtual_event.unique_id)
            elif virtual_event.type == 'webinar':
                virtual_event.object=Seminar.objects.get(unique_id=virtual_event.unique_id)
            virtual_event.time_table=Timetable.objects.filter(vitual_event=virtual_event.id)             
            context_dict={'object':virtual_event}
            # pdf = html_to_pdf('contract/contract.html',context_dict)
            pdf=html_to_pdf('contract/contract.html',context_dict,virtual_event.unique_id)               
            virtual_event.contract=pdf
            virtual_event.status='Select_expert'
            virtual_event.save()

            managers=Role.objects.filter(position='virtual manager')
            for manager in managers:
                virtualevent_Send_NotifEmail(virtual_event,manager.user,'director')

        return redirect('presenter')
        
class CreateVirtualEventView(View):
    template_name='forms/create.html'

    def get(self,request):
        type=request.GET.get('type')
        if type == None:
            type='workshop'
        context={
            'mainfields':MainField.objects.filter(user_add=False),
            'subfields':SubField.objects.filter(user_add=False),
            'time_zone':pytz.all_timezones,
            'type':type
        }
        return render(request,self.template_name,context)

    def post(self,request):
        # result=[]
        # for r in request.POST:
        #     s=request.POST.get(r)
        #     result.append(f"{r}:{s}")
        # return render(request,'forms/response.html',{"response":result,'image':request.FILES['image']})
        

    #Get all data
        request.user.memberprofile.birthday=request.POST.get('birthday')
        request.user.memberprofile.phone=request.POST.get('phone')
        request.user.memberprofile.gender=request.POST.get('gender')
        request.user.memberprofile.country=request.POST.get('country')
        request.user.memberprofile.city=request.POST.get('city')
        request.user.memberprofile.skype=request.POST.get('skype')
        request.user.memberprofile.save()
        type=request.POST.get('type')


        title=request.POST.get('title')
        price=request.POST.get('price').split('$')
        price=float(price[1])
        main_field=request.POST.get('Mfields').split(',')      
        sub_field=request.POST.get('Sfields').split(',')
        tblList=request.POST.get('tblList')
        sign_image=request.POST.get('sign_image')
        

    # Create unique id for virtual event
        virtual_events = VirtualEvent.objects.all()
        today_number = 0
        for item in virtual_events:
            if str(item.created).split(' ')[0] ==str(datetime.date.today()):
                today_number += 1
        date = str(timezone.now().date())
        new_date = date.split('-')
        my_date = ""
        my_date = int(my_date.join(new_date))
        my_date = my_date * 10000
        my_date += (today_number + 1)
        if type == 'workshop':
            unique_id="W{num}".format(num = my_date)
        elif type == 'course':
            unique_id="C{num}".format(num = my_date)
        elif type == 'webinar':
            unique_id="S{num}".format(num = my_date)

    # create virtual event       
        virtual_event=VirtualEvent.objects.create(
            title=title,price=int(price),type=type,top_user=request.user,unique_id=unique_id,sign=sign_image
        )
        [virtual_event.main_field.add(get_object_or_404(MainField,pk=int(id))) for id in main_field]
        [virtual_event.sub_field.add(get_object_or_404(SubField,pk=int(id))) for id in sub_field]
        virtual_event.save()

    #Create timetable for virtual event
        table_list = tblList.split(',')
        count=0
        allduration=0
        while count < len(table_list):
            if count == 0:
                virtual_event.start_date=table_list[count+2]
                virtual_event.save()
            title=table_list[count+1]
            start_date=table_list[count+2]
            start_time=table_list[count+3]
            start=start_time.split(':')
            end_time=table_list[count+4]
            end=end_time.split(':')
            duration_second=(int(end[0])*3600+int(end[1])*60)-(int(start[0])*3600+int(start[1])*60)
            duration=str(datetime.timedelta(seconds=duration_second))
            # duration=table_list[count+5]
            price=int(float(table_list[count+5].split('$')[1]))
            document=request.FILES.get(title)
            # alltime=duration.split(':')
            # allduration +=(int(alltime[0])*3600)+(int(alltime[1])*60)+(int(alltime[2]))
            allduration+=duration_second
            Timetable.objects.create(title=title,start_date=start_date,start_time=start_time,price=price,
                                    end_time=end_time,duration=duration,vitual_event = virtual_event,document=document)
            count=count+7
        allduration=str(datetime.timedelta(seconds=allduration))
        virtual_event.duration=allduration
        virtual_event.save()


    
    #create virtual event type
        if type == 'workshop':
            language=request.POST.get('language')
            time_zone=request.POST.get('time_zone')
            description=request.POST.get('description')
            skills=request.POST.get('skills')
            keyword=request.POST.get('keyword')
            speaker=request.POST.get('speaker_total')
            image=request.FILES.get('image')
            Workshop.objects.create(
                image=image,description=description,language=language,speaker=speaker,unique_id=unique_id,
                keyword=keyword,skills=skills,time_zone=time_zone
            )            
        elif type == 'course':
            language=request.POST.get('language')
            time_zone=request.POST.get('time_zone')
            description=request.POST.get('description')
            skills=request.POST.get('skills')
            keyword=request.POST.get('keyword')
            speaker=request.POST.get('speaker_total')
            image=request.FILES.get('image')
            Course.objects.create(
                image=image,description=description,language=language,speaker=speaker,unique_id=unique_id,
                keyword=keyword,skills=skills,time_zone=time_zone
            ) 
        elif type == 'webinar':
            language=request.POST.get('language')
            time_zone=request.POST.get('time_zone')
            description=request.POST.get('description')
            skills=request.POST.get('skills')
            keyword=request.POST.get('keyword')
            speaker=request.POST.get('speaker_total')
            image=request.FILES.get('image')
            Seminar.objects.create(
                image=image,description=description,language=language,speaker=speaker,unique_id=unique_id,
                keyword=keyword,skills=skills,time_zone=time_zone
            ) 

    #to do email notif (managers and presenter)
        virtualevent_Send_NotifEmail(virtual_event,request.user,'presenter')

    #to do create tracking
        new_track=VirtualEventTracking.objects.create(
            status="Select_expert",vitual_event=virtual_event,position='director',desc=VirtualEventTracking.description.Select_expert
            )

        messages.success(request,f'The {type} has been created.')
        return redirect('accept-contract' , pk=virtual_event.id)
      
#----------------------------------------------Modify virtual event----------------------------------------------------------------------------
      
class ModifyVirtualEventView(View):
    template_name='forms/edit.html'
    def setup(self, request, *args, **kwargs):
        self.pk = kwargs['pk']
        self.virtual_event=get_object_or_404(VirtualEvent,pk=self.pk)
        if self.virtual_event.type == 'workshop':
            self.virtual_event.object=Workshop.objects.get(unique_id=self.virtual_event.unique_id)
        elif self.virtual_event.type == 'course':
            self.virtual_event.object=Course.objects.get(unique_id=self.virtual_event.unique_id)
        elif self.virtual_event.type == 'seminar':
            self.virtual_event.object=Seminar.objects.get(unique_id=self.virtual_event.unique_id)
        self.virtual_event.timetables=Timetable.objects.filter(vitual_event=self.virtual_event)
        return super().setup(request, *args, **kwargs)

    def get(self,request,*args,**kwargs):
        context={
            'mainfields':MainField.objects.filter(user_add=False),
            'subfields':SubField.objects.filter(user_add=False),
            'time_zone':pytz.all_timezones,
            'type':self.virtual_event.type,
            'object':self.virtual_event
        }
        return render(request,self.template_name,context)
    

    def post(self,request,*args,**kwargs):

        # result=[]
        # for r in request.POST:
        #     s=request.POST.get(r)
        #     result.append(f"{r}:{s}")
        # return render(request,'forms/response.html',{"response":result,'image':request.FILES['image']})

         #Get all data
        # type=request.POST.get('type')
        # title=request.POST.get('title')
        # price=request.POST.get('price')
        # main_field=request.POST.getlist('Mfields[]')       
        # sub_field=request.POST.getlist('Sfields[]')
        # tblList=request.POST.get('tblList')

        # self.virtual_event.title=title
        # self.virtual_event.price=price
        # if len(main_field) > 0:
        #     [self.virtual_event.main_field.add(get_object_or_404(MainField,pk=int(id))) for id in main_field]
        #     [self.virtual_event.sub_field.add(get_object_or_404(SubField,pk=int(id))) for id in sub_field]
        # self.virtual_event.save()

        # #Edite timetable for virtual event
        # if not tblList == '':
        #     table_list = tblList.split(',')
        #     count=0
        #     allduration=0
        #     while count < len(table_list):
        #         if count == 0:
        #             self.virtual_event.start_date=table_list[count+2]
        #             self.virtual_event.save()
        #         title=table_list[count+1]
        #         start_date=table_list[count+2]
        #         start_time=table_list[count+3]
        #         end_time=table_list[count+4]
        #         duration=table_list[count+5]
        #         price=int(table_list[count+6])
        #         alltime=duration.split(':')
        #         allduration +=(int(alltime[0])*3600)+(int(alltime[1])*60)+(int(alltime[2]))
        #         [t.delete()for t in Timetable.objects.filter(vitual_event=self.virtual_event)]
        #         Timetable.objects.create(title=title,start_date=start_date,start_time=start_time,price=price,
        #                                 end_time=end_time,duration=duration,vitual_event = self.virtual_event)
        #         count=count+7
        #     allduration=str(datetime.timedelta(seconds=allduration))
        #     self.virtual_event.duration=allduration
        #     self.virtual_event.save()

        #Edite virtual event type
        # if type == 'workshop':
        #     language=request.POST.get('language')
        #     time_zone=request.POST.get('time_zone')
        #     description=request.POST.get('description')
        #     skills=request.POST.get('skills')
        #     keyword=request.POST.get('keyword')
        #     speaker=request.POST.get('speaker')
        #     suggest_country=request.POST.get('suggest_country')
        #     image=request.FILES.get('image')
        #     workshop=get_object_or_404(Workshop,unique_id=self.virtual_event.unique_id)
        #     workshop.save()
        

        messages.success(request,'Your virtual event has been resubmitted for review.')
        return ChangeStatusVirtualEvent(request,self.virtual_event,'1')

#----------------------------------------------Presenter dashboard----------------------------------------------------------------------------

class PresenterView(View):
    template_name='presenter/dashboard.html'
    PERESENTER_STATUS={
        'Create':_('To continue, you should complete the submission '),
        'Reject':_('Rejected'),
        'Revise':_('Revised '),
        'Remove':_('Deleted'),
        'Select_expert':_('Under process'),
        'Expert_decide':_('Under process'),
        'Resubmit_to_expert':_('Under process'),
        'Resubmit_to_director':_('Under process'),
        'Published':_('Accepted and published'),
    }

    def get(self,request):
        context={}            
        type=request.GET.get('type')
        if request.GET.get('filter') == 'Pending':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status__in=['Select_expert','Expert_decide','Resubmit_to_expert','Resubmit_to_director','Create'])           
        elif request.GET.get('filter') == 'Published':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Published')
            for ve in context['virtual_events']:
                ve.edit_request=EditRequest.objects.filter(virtual_event=ve,is_accept=False).first()
                ve.time_table=Timetable.objects.filter(vitual_event=ve)
        elif request.GET.get('filter') == 'Rejected':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Reject')
        elif request.GET.get('filter') == 'Revise':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Revise')
        elif request.GET.get('filter') == 'Upload':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Published')
            context['today']=datetime.date.today()
            for ve in context['virtual_events']:
                ve.time_table=Timetable.objects.filter(vitual_event=ve)
        else:
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status__in=['Select_expert','Expert_decide','Resubmit_to_expert','Resubmit_to_director','Create'])           

        context['publish_count']=VirtualEvent.objects.filter(type=type,status='Published').count()
        context['pending_count']=VirtualEvent.objects.filter(type=type,status__in=['Select_expert','Expert_decide','Resubmit_to_expert','Resubmit_to_director','Create']).count()
        context['reject_count']=VirtualEvent.objects.filter(type=type,status='Reject').count()
        context['revise_count']=VirtualEvent.objects.filter(type=type,status='Revise').count()
        for ve in context['virtual_events']:
                ve.statuspreview=self.PERESENTER_STATUS[ve.status]
        return render(request,self.template_name,context)

class VirtualEventDetailePersenterView(DetailView):
    template_name='presenter/detail.html'
    model=VirtualEvent
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object'].type == 'course':
            context['object'].object=Course.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'workshop':
            context['object'].object=Workshop.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'seminar':
            context['object'].object=Seminar.objects.get(unique_id=context['object'].unique_id)
        context['object'].time_table=Timetable.objects.filter(vitual_event=context['object'].id)
        context['object'].tracking=VirtualEventTracking.objects.filter(vitual_event=context['object'])
        return context

class UploadFileView(View):
    def post(self,request):
        file_type=request.POST.get('file_type')
        virtual_event=get_object_or_404(VirtualEvent,pk=int(request.POST.get('id')))
        if file_type == 'file':
            for time in Timetable.objects.filter(vitual_event=virtual_event):
                time.document=request.FILES.get(f'document_{time.id}')
                time.save()

        #Send notif and email 
            for member in VirtualEventMemebers.objects.filter(virtual_event=virtual_event):
                virtualevent_Send_NotifEmail(virtual_event,member.user,virtual_event.id,'Upload_file')

            messages.success(request,'Files has been uploaded.')


        elif file_type == 'video':
            for time in Timetable.objects.filter(vitual_event=virtual_event):
                time.video_link=request.POST.get(f'video_{time.id}')
                time.save()

        #Send notif and email 
            for member in VirtualEventMemebers.objects.filter(virtual_event=virtual_event):
                virtualevent_Send_NotifEmail(virtual_event,member.user,virtual_event.id,'Upload_video')

            messages.success(request,'Video link has been set.')


        return redirect('presenter')

#----------------------------------------------Expert dashboard----------------------------------------------------------------------------
    
class ExpertView(ExpertManagerMixin,View):
    permission_required=""
    template_name='Expert/dashboard.html'
    Expert_STATUS={
        'Reject':_('Rejected'),
        'Revise':_('Revised'),
        'Remove':_('Deleted'),
        #'Select_expert':_('Pending for director decide'),
        'Resubmit_to_expert':_('Resubmitted and pending for your decision'),
        'Expert_decide':_('Pending for your decision'),
        'Published':_('Accepyted and published'),
       # 'Resubmit_to_director':_('The virtual event has been submitted'),
    }

    def get(self,request):
        type=request.GET.get('type')
        context={}
        if request.GET.get('filter') == 'Evaluate' :
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Expert_decide',expert=request.user).order_by('-created') 
        elif request.GET.get('filter') == 'Resubmit' :
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Resubmit_to_expert',expert=request.user).order_by('-created') 
        elif request.GET.get('filter') == 'History':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,expert=request.user).order_by('-created')
        elif request.GET.get('filter') == 'Requests':
            context['virtual_events']=[]
            [context['virtual_events'].append(re.virtual_event) for re in EditRequest.objects.filter(virtual_event__type=type,virtual_event__expert=request.user,to_director=False,is_accept=False,rejected=False)]        
            for ve in context['virtual_events']:
                    ve.time_table=Timetable.objects.filter(vitual_event=ve)
                    ve.suggest_time_table=EditTimetableRequest.objects.filter(editrequest__virtual_event=ve,editrequest__is_accept=False)

                
        else:
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Expert_decide',expert=request.user).order_by('-created')          
        context['evaluate_count']=VirtualEvent.objects.filter(type=type,status='Expert_decide',expert=request.user).count()
        context['resubmit_count']=VirtualEvent.objects.filter(type=type,status='Resubmit_to_expert',expert=request.user).count()
        context['history_count']=VirtualEvent.objects.filter(type=type,expert=request.user).count()
        context['request_count']=EditRequest.objects.filter(virtual_event__type=type,virtual_event__expert=request.user,to_director=False,is_accept=False,rejected=False).count        
        for ve in context['virtual_events']:
                ve.statuspreview=self.Expert_STATUS[ve.status]
        return render(request,self.template_name,context)


class VirtualEventDetaileExpertView(ExpertManagerMixin,DetailView):
    permission_required=""
    template_name='Expert/detail.html'
    model=VirtualEvent
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object'].type == 'course' :
            context['object'].object=Course.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'workshop':
            context['object'].object=Workshop.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'seminar':
            context['object'].object=Seminar.objects.get(unique_id=context['object'].unique_id)
        context['object'].time_table=Timetable.objects.filter(vitual_event=context['object'].id)
        context['object'].tracking=VirtualEventTracking.objects.filter(vitual_event=context['object'])
        return context

#----------------------------------------------Director dashboard----------------------------------------------------------------------------
    
class DirectorView(ManagerMixin,View):
    permission_required=""
    template_name='Director/dashboard.html'
    Director_STATUS={
        'Reject':_('Rejected'),
        'Revise':_('Revise'),
        'Remove':_('Deleted'),
        'Select_expert':_('Select an expert'),
        'Expert_decide':_('Under process'),
        'Published':_('Accepted and published'),
        #'Resubmit_to_expert':_('The virtual event has been submitted to expert'),
        'Resubmit_to_director':_('Resubmitted and pending for your decision'),
        

    }

    def get(self,request):
        type=request.GET.get('type')
        context={}
        if request.GET.get('filter') == 'All' :
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status="Published").order_by('-created')          
        elif request.GET.get('filter') == 'Select-Expert':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Select_expert').order_by('-created')
        elif request.GET.get('filter') == 'Resubmit':
            context['virtual_events']=VirtualEvent.objects.filter(type=type,status='Resubmit_to_director').order_by('-created')       
        elif request.GET.get('filter') == 'History':
            context['virtual_events']=VirtualEvent.objects.filter(type=type).order_by('-created')
            context['experts']=Role.objects.filter(position='virtual expert')
        elif request.GET.get('filter') == 'Requests':
            context['virtual_events']=[]
            [context['virtual_events'].append(re.virtual_event) for re in EditRequest.objects.filter(virtual_event__type=type,to_director=True,is_accept=False,rejected=False)]   
            for ve in context['virtual_events']:
                    ve.time_table=Timetable.objects.filter(vitual_event=ve)
                    ve.suggest_time_table=EditTimetableRequest.objects.filter(editrequest__virtual_event=ve,editrequest__is_accept=False)
        else:
            context['virtual_events']=VirtualEvent.objects.filter(status='Select_expert').order_by('-created')

        context['select_expert_count']=VirtualEvent.objects.filter(type=type,status='Select_expert').count()
        context['resubmit_count']=VirtualEvent.objects.filter(type=type,status='Resubmit_to_director').count()
        context['all_count']=VirtualEvent.objects.filter(type=type,status="Published").count()
        context['history_count']=VirtualEvent.objects.filter(type=type).count()
        context['request_count']=EditRequest.objects.filter(virtual_event__type=type,to_director=True,is_accept=False,rejected=False).count()        
        for ve in context['virtual_events']:
            ve.statuspreview=self.Director_STATUS[ve.status]
        return render(request,self.template_name,context)

class VirtualEventDetaileDirectorView(ManagerMixin,DetailView):
    permission_required=""
    template_name='Director/detail.html'
    model=VirtualEvent
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object'].type == 'course':
            context['object'].object=Course.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'workshop':
            context['object'].object=Workshop.objects.get(unique_id=context['object'].unique_id)
        elif context['object'].type == 'seminar':
            context['object'].object=Seminar.objects.get(unique_id=context['object'].unique_id)
        context['object'].time_table=Timetable.objects.filter(vitual_event=context['object'].id)
        context['experts']=Role.objects.filter(position='virtual expert')
        context['object'].tracking=VirtualEventTracking.objects.filter(vitual_event=context['object'])
    

        return context
#----------------------------------------------Changing status in virtual event----------------------------------------------------------------------------
@login_required
def ChangeStatusVirtualEvent(request,virtual_event=None,decide=None):
    if request.method == "POST":
        #get all managers in virtual events
        managers=Role.objects.filter(position='virtual manager')
        if decide:
            pass
        else:
            decide=request.POST.get('decide')
        if virtual_event:
            pass
        else:
            virtual_event=get_object_or_404(VirtualEvent,pk=int(request.POST.get('id')))


#---------STEP1---------------------------------       
        if virtual_event.status == 'Select_expert' or virtual_event.status == 'Resubmit_to_director':
            if VirtualEventTracking.objects.filter(status=virtual_event.status,vitual_event=virtual_event).exists():
                    prev_track=VirtualEventTracking.objects.filter(status=virtual_event.status,vitual_event=virtual_event).first()
                    prev_track.is_done=True;prev_track.save()
            
            if decide == '1':
                expert=User.objects.get(id=int(request.POST.get('expert_id')))
                virtual_event.status = 'Expert_decide'
                virtual_event.expert = expert
                virtual_event.save()

                # to do create tracking                
                new_track=VirtualEventTracking.objects.create(
                    status="Expert_decide",vitual_event=virtual_event,position='expert',desc=VirtualEventTracking.description.Expert_decide
                    )

                #to do email notif (expert)
                virtualevent_Send_NotifEmail(virtual_event,expert,'expert')
                messages.success(request,'The virtual event sent to expert.')

            elif decide == 'Reject':
                comment=request.POST.get('comment')
                virtual_event.status='Reject'
                virtual_event.save()

                #to do create tracking
                new_track=VirtualEventTracking.objects.create(comment=comment,
                    status="Reject",vitual_event=virtual_event,position='presenter',desc=VirtualEventTracking.description.Reject
                    )

                #to do email notif  (presenter)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')
                messages.error(request,'The virtual event revise to presenter.')

            else:
                comment=request.POST.get('comment')
                virtual_event.status='Revise'
                virtual_event.save()

                #to do create tracking
                new_track=VirtualEventTracking.objects.create(comment=comment,
                    status="Revise",vitual_event=virtual_event,position='presenter',desc=VirtualEventTracking.description.Revise
                    )

                #to do email notif  (presenter)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')
                messages.error(request,'The virtual event revise to presenter.')

            return redirect('director')

#---------STEP2---------------------------------      

        elif virtual_event.status == 'Revise':
            if VirtualEventTracking.objects.filter(status='Revise',vitual_event=virtual_event,is_done=False).exists():
                    prev_track=VirtualEventTracking.objects.filter(status='Revise',vitual_event=virtual_event,is_done=False).first()
                    prev_track.is_done=True;prev_track.save()

            if decide == '1':
                if virtual_event.expert:
                    virtual_event.status="Resubmit_to_expert"
                    virtual_event.save()

                #to do email notif (expert and presenter)
                    virtualevent_Send_NotifEmail(virtual_event,virtual_event.expert,'expert')
                    virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')

                #to do create tracking
                    new_track=VirtualEventTracking.objects.create(
                    status="Resubmit_to_expert",vitual_event=virtual_event,position='expert',desc=VirtualEventTracking.description.Resubmit_to_expert,
                    )

                else:
                    virtual_event.status="Resubmit_to_director"
                    virtual_event.save()
                #to do email notif (manager and presenter)
                    for manager in managers:
                        virtualevent_Send_NotifEmail(virtual_event,manager.user,'director')
                    virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')

                #to do create tracking
                    new_track=VirtualEventTracking.objects.create(
                    status="Resubmit_to_director",vitual_event=virtual_event,position='director',desc=VirtualEventTracking.description.Resubmit_to_director,
                    )
                
            else:

                virtual_event.status = 'Remove'
                virtual_event.save()

                # to do create tracking (presenter)               
                new_track=VirtualEventTracking.objects.create(
                    status="Remove",vitual_event=virtual_event,position='---',desc=VirtualEventTracking.description.Remove,is_done=True
                    )

                #to do email notif (managers and expert)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')

                messages.error(request,'The virtual event removed.')
            return redirect('presenter')
#---------STEP3---------------------------------      

        elif virtual_event.status == 'Reject':
            if VirtualEventTracking.objects.filter(status='Reject',vitual_event=virtual_event).exists():
                    prev_track=VirtualEventTracking.objects.filter(status='Reject',vitual_event=virtual_event).first()
                    prev_track.is_done=True;prev_track.save()
            if decide == '1':
                virtual_event.status='Select_expert'
                #to do email notif (manager and presenter)
                #to do create tracking
            else:

                virtual_event.status = 'Remove'
                virtual_event.save()

                # to do create tracking (presenter)               
                new_track=VirtualEventTracking.objects.create(
                    status="Remove",vitual_event=virtual_event,position='---',desc=VirtualEventTracking.description.Remove
                    )

                #to do email notif (managers and expert)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')
                # virtual_event.delete()
                messages.error(request,'The virtual event removed.')
            return redirect('presenter')

#---------STEP4--------------------------------- 

        elif virtual_event.status == 'Expert_decide' or virtual_event.status == 'Resubmit_to_expert':
            if VirtualEventTracking.objects.filter(status=virtual_event.status,vitual_event=virtual_event).exists():
                    prev_track=VirtualEventTracking.objects.filter(status=virtual_event.status,vitual_event=virtual_event).first()
                    prev_track.is_done=True;prev_track.save()
            if decide == '1':
                virtual_event.status='Published'
                virtual_event.save()

                #to do create tracking
                new_track=VirtualEventTracking.objects.create(
                    status="Published",vitual_event=virtual_event,position='---',desc=VirtualEventTracking.description.Published,
                    is_done=True
                    )

                #to do email notif (presenter)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')

                messages.success(request,'The virtual event published.')

            elif decide=="Reject":
                comment=request.POST.get('comment')
                virtual_event.status='Reject'
                virtual_event.save()

                #to do create tracking
                new_track=VirtualEventTracking.objects.create(comment=comment,
                    status="Reject",vitual_event=virtual_event,position='presenter',desc=VirtualEventTracking.description.Reject
                    )

                #to do email notif  (presenter)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')
                messages.error(request,'The virtual event revise to presenter.')



            else:
                comment=request.POST.get('comment')
                virtual_event.status='Revise'
                virtual_event.save()

                #to do create tracking
                new_track=VirtualEventTracking.objects.create(
                    status="Revise",vitual_event=virtual_event,position='presenter',desc=VirtualEventTracking.description.Revise,
                    comment=comment 
                    )

                #to do email notif (presenter)
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter')

                messages.error(request,'The virtual event revised to presenter.')
            
            return redirect('expert')


class ChangeExpetview(ManagerMixin,View):
    permission_required=""
    def post(self,request):
        virtual_event=get_object_or_404(VirtualEvent,pk=int(request.POST.get('id')))
        selected_expert=User.objects.get(id=int(request.POST.get('expert_id')))
        current_expert=virtual_event.expert
        virtual_event.expert=selected_expert
        virtual_event.save()

        #to do email notif (expert)
        virtualevent_Send_NotifEmail(virtual_event,selected_expert,'expert')
        virtualevent_Send_NotifEmail(virtual_event,current_expert,'expert','change_expert')
        messages.success(request,'Expert changed by you.')
        return redirect ('director')

#----------------------------------------------Front and Registrant ----------------------------------------------------------------------------

class ShowVirtualEventView(DetailView):
    template_name='show/show.html'
    model=VirtualEvent
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if context['object'].type == 'course':
            context['object'].object=Course.objects.get(unique_id=context['object'].unique_id)
            context['object'].object.speaker=context['object'].object.speaker.split(',')
        elif context['object'].type == 'workshop':
            context['object'].object=Workshop.objects.get(unique_id=context['object'].unique_id)
            context['object'].object.speaker=context['object'].object.speaker.split(',')
        elif context['object'].type == 'seminar':
            context['object'].object=Seminar.objects.get(unique_id=context['object'].unique_id)
            context['object'].object.speaker=context['object'].object.speaker.split(',')
        context["timtables"] =Timetable.objects.filter(vitual_event=context['object'])
        context['today']=datetime.date.today()
        if self.request.user.is_authenticated:
            context['buyall']=VirtualEventMemebers.objects.filter(user=self.request.user,section='All',is_paid=1,virtual_event=context['object']) 
            for time in context["timtables"]:
                time.buy =VirtualEventMemebers.objects.filter(user=self.request.user,section=time.title,is_paid=1)
        return context

class Registrant(ManagerMixin,View):
    permission_required=""
    template_name='show/registrant.html'
    def get(self,request,*args,**kwargs):
        virtual_event=get_object_or_404(VirtualEvent,pk=kwargs['pk'])
        context={
            'users':VirtualEventMemebers.objects.filter(virtual_event=virtual_event),
            'virtual_event':virtual_event,
            'timetables':Timetable.objects.filter(vitual_event=virtual_event)
        }
        return render(request,self.template_name,context)

    def post(self,request,*args,**kwargs):
        status=request.POST.get('status')
        record_id=int(request.POST.get('record'))
        if status == 'certificate':
            certificate=request.FILES['certificate']
            record=get_object_or_404(VirtualEventMemebers,pk=record_id)
            record.certificate=certificate
            record.save()
            messages.success(request,'The certificcate has been uploaded')
        elif status == 'delete_certificate':
            record=get_object_or_404(VirtualEventMemebers,pk=record_id)
            record.certificate=None
            record.save()
            messages.error(request,'The certificate has been deleted')
        return redirect('registrant',pk=kwargs['pk'])

class VirtualEventShowToUsersView(View):
    template_name='show/show-to-users.html'
    def get(self,request):
        context={}
        if request.GET.get('filter') == 'All' or request.GET.get('filter') == None:
            context['virtual_events']=VirtualEvent.objects.filter(status='Published')           
        elif request.GET.get('filter') == 'My-virtual-events':
            context['virtual_events']=VirtualEventMemebers.objects.filter(user=request.user,is_paid=True)
        elif request.GET.get('filter') == 'Unpaid':
            context['virtual_events']=VirtualEventMemebers.objects.filter(user=request.user,is_paid=False)
            for ve in context['virtual_events']:
                ve.invoice=Invoice.objects.filter(user=request.user,service__service_name="V",service__action=ve.section).first()
        context['all_count']=VirtualEvent.objects.filter(status='Published').count()
        context['mylist_count']=VirtualEventMemebers.objects.filter(user=request.user,is_paid=True).count()
        context['Unpaid_count']=VirtualEventMemebers.objects.filter(user=request.user,is_paid=False).count()

        return render(request,self.template_name,context)

def BuyVirtuaEventView(request,pk):
    virtual_event=get_object_or_404(VirtualEvent,pk=pk)
    action=request.GET.get('action')
    VirtualEventMemebers.objects.create(user=request.user,section=action,virtual_event=virtual_event)
    return PaymentProtocol(request,'V',virtual_event,virtual_event.price,action=action)

class VirtualEventListView(View):
    template_name='show/list.html'
    def get(self,request):
        context={}
        type=request.GET.get('type')
        if type== 'workshop' or type == None:
            context['virtual_events']=VirtualEvent.objects.filter(type='workshop',status='Published')
            for ve in context['virtual_events']:
                ve.object=get_object_or_404(Workshop,unique_id=ve.unique_id)
                ve.start_time=Timetable.objects.filter(vitual_event=ve).first().start_time
        elif type == 'course':
            context['virtual_events']=VirtualEvent.objects.filter(type='course',status='Published')
            for ve in context['virtual_events']:
                ve.object=get_object_or_404(Course,unique_id=ve.unique_id)
                ve.start_time=Timetable.objects.filter(vitual_event=ve).first().start_time
        elif type == 'webinar':
            context['virtual_events']=VirtualEvent.objects.filter(type='seminar',status='Published')
            for ve in context['virtual_events']:
                ve.object=get_object_or_404(Seminar,unique_id=ve.unique_id)
                ve.start_time=Timetable.objects.filter(vitual_event=ve).first().start_time

        for ve in context['virtual_events']:
            ve.skills=ve.object.skills.split(',')
            speakers=ve.object.speaker.split(';')
            if len(speakers) == 1:
                ve.speakers=ve.object.speaker.replace('Speaker','Speaker1')
            else:
                ve.speakers=ve.object.speaker.split(';')
        context['type']=type
        context['today']=datetime.date.today()
        return render(request,self.template_name,context)

class ManagerPanelView(ManagerMixin,View):
    permission_required=""
    template_name='show/manager-panel.html'
    def get(self,request):
        context={}
        if request.GET.get('filter') == 'All' or request.GET.get('filter') == None:
            context['virtual_events']=VirtualEvent.objects.filter(status='Published')
            for ve in context['virtual_events']:
                ve.members=VirtualEventMemebers.objects.filter(virtual_event=ve)
        elif request.GET.get('filter') == 'Experts':
            context['experts']=Role.objects.filter(position='virtual expert')
            context['users']=User.objects.all()
            for user in context['users']:
                if Role.objects.filter(user=user,position='virtual expert'):
                    user.ok =True
        context['all_count']=VirtualEvent.objects.filter(status='Published').count()
        context['experts_count']=Role.objects.filter(position='virtual expert').count()
        return render(request,self.template_name,context)

    def post(self,request):
        action=request.POST.get('action')
        user=User.objects.filter(id=request.POST.get('user_id')).first()
        if Role.objects.filter(user=user,position='virtual expert'):
            role=Role.objects.filter(user=user,position='virtual expert')
            role.delete()
        else:
            Role.objects.create(user=user,position='virtual expert')
        return JsonResponse({'result':'ok'})

#----------------------------------------------Request edit start time ----------------------------------------------------------------------------

class EditTimeRequest(View):
    def post(self,request):
        if request.FILES.get('document'):
            document=request.FILES.get('document')
        else:
            document=None
        virtual_event=get_object_or_404(VirtualEvent,pk=int(request.POST.get('id')))
        editrequest=EditRequest.objects.create(virtual_event=virtual_event,reason=request.POST.get('reason'),document=document)
        for time in Timetable.objects.filter(vitual_event=virtual_event):
            EditTimetableRequest.objects.create(start_date=request.POST.get(f'start_date_{time.id}'),time_table=time,
            start_time=request.POST.get(f'start_time_{time.id}'),end_time=request.POST.get(f'end_time_{time.id}'),editrequest=editrequest,
            )
        virtualevent_Send_NotifEmail(virtual_event,virtual_event.expert,'expert','Edit_time')
        messages.success(request,"Yor request has been sent to virtual event's expert")
        return redirect('presenter')

class DecideForEditTimeView(ExpertManagerMixin,View):
    permission_required=""
    def post(self,request):
        editrequest=get_object_or_404(EditRequest,pk=int(request.POST.get('request_id')))
        editrequest.comment=request.POST.get('comment')
        virtual_event=editrequest.virtual_event
        if request.POST.get('decide') == 'accept':
                editrequest.is_accept=True
                duration_seconds=0
                for time in Timetable.objects.filter(vitual_event=virtual_event):
                    suggest_time=EditTimetableRequest.objects.get(time_table=time,editrequest__is_accept=False)
                    time.start_date=suggest_time.start_date
                    time.start_time=suggest_time.start_time
                    time.end_time=suggest_time.end_time
                    end_time=time.end_time.strftime("%H:%M:%S").split(':')
                    start_time=time.start_time.strftime("%H:%M:%S").split(':')
                    seconds=((int(end_time[0])*3600)+(int(end_time[1])*60)+(int(end_time[2]))) -((int(start_time[0])*3600)+(int(start_time[1])*60)+(int(start_time[2])))
                    duration_seconds+=seconds
                    time.duration=datetime.timedelta(seconds=seconds)                      
                    time.save()
                virtual_event.duration=datetime.timedelta(seconds=duration_seconds)
                virtual_event.save()
                editrequest.save()

                #Send notif and email 
                for member in VirtualEventMemebers.objects.filter(virtual_event=virtual_event):
                    virtualevent_Send_NotifEmail(virtual_event,member.user,virtual_event.id,'Send_to_members')
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter','Edit_time_accept')

                messages.success(request,'Virtual event schedule changed successfully')
                
        elif request.POST.get('decide') == 'reject':
                editrequest.rejected=True
                editrequest.save()
                virtualevent_Send_NotifEmail(virtual_event,virtual_event.top_user,'presenter','Edit_time_reject')
                messages.error(request,'Request for virtual event"s schedule rejected')

        elif request.POST.get('decide') == 'director':
                editrequest.to_director=True
                editrequest.save()
                managers=Role.objects.filter(position='virtual manager')
                for manager in managers:
                    virtualevent_Send_NotifEmail(virtual_event,manager.user,'director','Edit_time')
                messages.error(request,'Request for virtual event"s send to director')
        
        if request.POST.get('decider') == 'expert':
            return redirect('expert')
        elif request.POST.get('decider') == 'director':
            return redirect('director')



#----------------------------------------------Automate emails ----------------------------------------------------------------------------

def AutomateEmails(request):
    from .emails import AutomateSendingEmail
    AutomateSendingEmail()
    return HttpResponse("ok")


#to do
# Complete edit virtual event and submited and edit contract



# Done
# Complete virtual event front page and show workshops page for director with registrant page and upload certificate for client
# Complete permision for director and expert in dashboard and views 
# Correct virtual event number in manager dashboard
#Fixed Mainfield and subfield problems ...
# Complete email and Notification
#complete fase2
# Complete counter for dashboard
#prevent back
#automatic email
#Complate email and notif and status and message exel
