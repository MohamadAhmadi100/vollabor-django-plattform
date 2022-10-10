import pytz
import math
import datetime
from django.db.models import Q
from django.urls import reverse
from django.http import Http404
from django.db.models import Sum
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from users.models import MemberProfile
from django.core.mail import EmailMessage
from django.contrib.auth.models import User
from ivc_project.email_sender import send_new_email
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, FormView, DetailView, UpdateView, DeleteView
from .forms import *
from .models import *
from .mixins import *

from datetime import date
from datetime import datetime
from request.models import BadgeRequest
from datetime import timedelta
from forum.models import Category, MainCategory
from workshop.models import MainField, SubField
from users.models import MemberProfile
from dashboard.models import Notification
from accounting.models import *
from research.formula import calculate_ResponsiveFee
# Create your views here.
from django.utils.html import format_html
from seo.models import UserFootprint


def user_has_memberprofile(given_user):
    return MemberProfile.objects.filter(user=given_user).count() == 1

#------------Form Client------------#
@login_required
def create_form_clint(request, **kwargs):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.about_me == '':  # user has to complete his/her profile to see this page
            messages.error(request, format_html("<h6>Error: You cannot define a new project because your profile is incomplete. Please go to your ptofile and complete it. <a href='http://127.0.0.1:8000/members/profile/'>Go to your profile</a></h6> "),)
            # return HttpResponseRedirect(request.path_info)
            return redirect('dashboard-page')
        else:
            roles = ResearchRole.objects.all()
            user_id = request.user.id
            user = User.objects.get(id=user_id)
            if request.method == 'POST':
                form = CreateForm(request.POST, request.FILES)
                if form.is_valid():
                    name = form.cleaned_data.get("name")
                    title = form.cleaned_data.get("title")
                    abstrack = form.cleaned_data.get("abstrack")
                    start_date = form.cleaned_data.get("start_date")
                    end_date = form.cleaned_data.get("end_date")
                    data_set_link = form.cleaned_data.get("data_set_link")
                    equipment = form.cleaned_data.get("equipment")
                    requirement = form.cleaned_data.get("requirement")
                    main_supervisor = form.cleaned_data.get("main_supervisor")
                    pri_file = form.cleaned_data.get("pri_file")
                    fund = form.cleaned_data.get("fund")
                    question_1 = form.cleaned_data.get("question_1")
                    question_2 = form.cleaned_data.get("question_2")
                    question_3 = form.cleaned_data.get("question_3")
                    question_4 = form.cleaned_data.get("question_4")
                    question_5 = form.cleaned_data.get("question_5")
                    question_6 = form.cleaned_data.get("question_6")
                    question_7 = form.cleaned_data.get("question_7")
                    main_field = form.cleaned_data.get("main_field")
                    sub_field = form.cleaned_data.get("sub_field")
                    add_sub_field = form.cleaned_data.get("add_sub_field")
                    
                    if add_sub_field:
                        Sub_field_objects = SubField.objects.all(),
                        Sub_field_objects_count = SubField.objects.all().count(),
                        add_sub = ''
                        for i in add_sub_field:
                            if i == ' ':
                                i = '_'
                            add_sub += i

                        Sub_field_objects_count = str(Sub_field_objects_count)
                        add_sub += Sub_field_objects_count

                        new_sub_field = SubField.objects.create(parent_id=main_field, title=add_sub_field, slug=add_sub)

                        sub_field_research = SubField.objects.get(slug=add_sub)
                    else:
                        sub_field_research = SubField.objects.get(id=sub_field)



                    projects = IndustryFormClient.objects.all()
                    count = 0
                    for i in projects:
                        created_date = i.created
                        created_date = str(created_date)
                        created_date = created_date.split(" ")
                        created_date = created_date[0]
                
                        to_day = date.today()
                        to_day = str(to_day)
                        to_day = to_day.split(" ")
                        to_day = to_day[0]
                        
                
                        if created_date == to_day:
                            count += 1
                
                    date_ = str(timezone.now().date())
                    new_date = date_.split('-')
                    my_date = ""
                    my_date = int(my_date.join(new_date))
                    my_date = my_date * 10000
                    my_date += (count + 1)
                
                    id_p = "P{num}".format(num = my_date)

                    new_from = IndustryFormClient.objects.create(
                        name=request.user.get_full_name(), title=title, start_date=start_date, end_date=end_date, 
                        abstrack=abstrack, data_set_link=data_set_link, equipment=equipment, requirement=requirement, 
                        main_supervisor=main_supervisor, pri_file=pri_file, fund=fund, user=user, question_1=question_1, 
                        question_2=question_2, question_3=question_3, question_4=question_4, question_5=question_5, question_6=question_6, 
                        question_7=question_7, main_field_id=main_field, sub_field=sub_field_research, id_project=id_p,status='not-pay')


                    return PaymentProtocol(request,'P',new_from, 150,action='create')
                    
            else:
                form = CreateForm
            
            is_supervisour = MemberProfile.objects.get(user=request.user)
            position = is_supervisour.position
            context = {
            "form": form,
            "date": date.today(),
            'mainfield' : MainField.objects.all(),
            'subfield' : SubField.objects.filter(parent=None),
            'position' : position
            }

            return render(request, 'industry/formclint.html', context)

def again_pay_project(user, pk):
    obj_project = get_object_or_404(IndustryFormClient, pk=pk)
    roles = ResearchRole.objects.all()
    obj_project.status = 'n'
    obj_project.follow_project='new'
    obj_project.save()
    
    # if obj_project.main_supervisor:
    create_obj_tracing = Tracing.objects.create(
        position='Client', user=user, status="The client defined a new project", event_date=timezone.now(), tracing_project=obj_project)
        
    create_obj_tracing = Tracing.objects.create(
        position='You', user=user, status="You defined a new project", event_date=timezone.now(), tracking_client=obj_project)
    
    for i in roles:
        if i.director == True:
            
            e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
            e_content ="Dear {} \nHello\nHope you are going well. \nA new project has been recently submitted. To observe it, you can go to your dashboard.\nTitle: {} \n Abstract: {} \nFund: ${}\n Submitted date: {} \nDo not reply to this Email. This Email has been sent automatically. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_project.title, obj_project.abstrack, obj_project.fund, date.today() )
            e_destination = i.user.email
            send_new_email(e_subject,e_content,e_destination)
            
            
    
            Notification(title='Project (ID: {})'.format(obj_project.id_project), 
                description='A new project has been added to your list. For more information, go to your dashboard.', target=i.user, 
                link=reverse('industry:industry-view-edit', args=[obj_project.pk])).save()

    Notification(title='Project (ID: {})'.format(obj_project.id_project), 
        description='Your project has been submitted successfully. For more information, go to your dashboard.', target=obj_project.user, 
        link=reverse('industry:client-detail', args=[obj_project.pk])).save()
    
    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
    e_content ="Dear {}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with us. Your project has been submitted successfully. \n Title: {}\nFund: ${}\n Submitted date: {}\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(user.get_full_name(), obj_project.title, obj_project.fund, date.today())
    e_destination =user.email
    send_new_email(e_subject,e_content,e_destination)

@login_required
def load_field(request):
    main_field = request.GET.get('main_field')
    if main_field != "":
        sub_field = SubField.objects.filter(parent_id=main_field)
    else:
        sub_field = SubField.objects.none()
    return render(request, 'workshop/field_dropdown_list_options.html', {'sub_field': sub_field})

@login_required
def contract_client_list(request):
    template_name = 'industry/contract-client-list.html'
    context = {
        'contract_new': IndustryFormClient.objects.filter(status='send-contract-to-client', user=request.user),
        'contract_new_count': IndustryFormClient.objects.filter(status='send-contract-to-client', user=request.user).count(),
        'contract_revised': IndustryFormClient.objects.filter(status='revised-contract', user=request.user),
        'contract_revised_count': IndustryFormClient.objects.filter(status='revised-contract', user=request.user).count(),
    }
    return render(request, template_name, context)

#------------Director------------#
class ResearchDirectorPanel(LoginRequiredMixin, SecurityDirector, ListView):
    queryset = IndustryFormClient.objects.filter(status='n').order_by('-created')
    template_name = 'industry/director/director-panel.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['coun_new_priject_industry'] = IndustryFormClient.objects.filter(status='n').count()

        # resubmition
        context['check_score'] = IndustryFormExpert.objects.filter(status='chek_score').order_by("-created")
        context['count_resubmition_cart'] = IndustryExpertForSupervisor.objects.filter(status='resubmition-to-director').count() + IndustryFormExpert.objects.filter(status='resubmited_project_send_to_director').count()


        # filter evaluated count
        check_score_span = IndustryExpertForSupervisor.objects.filter(status='d').count()
        suggest_reviewer_count = IndustryFormExpert.objects.filter(status='expert_send_scores_to_director').count()
        context['filter_evlaluated'] = check_score_span + suggest_reviewer_count
        
        count_speical_expert_main = IndustryExpertForSupervisor.objects.filter(status='special_expert',).count()
        count_speical_expert_review = IndustryExpertForSupervisor.objects.filter(status='special_expert_review',).count()
        count_speical_expert_create = IndustryExpertForSupervisor.objects.filter(status='special_expert_create_project',).count()
        count_speical_expert_a_or_r = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert',).order_by("-created").count()
        context['count_special_cart'] = count_speical_expert_main + count_speical_expert_review + count_speical_expert_create + count_speical_expert_a_or_r 


        # Contract
        context['count_cart_contract'] = IndustryFormClient.objects.filter(status='send-contract-to-director').count() + IndustryExpertForSupervisor.objects.filter(status='z').count()


        # under process
        context['under_process_list'] = IndustryFormClient.objects.filter(
        project_created=False, 
        status__in=['n', 'e', 's', 'm', 'd', 'accept_or_reject_expert', 'created', 'hidden', 'accept_reviewer', 'reject_reviewer', 'expert_reviewer']
        ).order_by("-created")

        context['under_process_count'] = IndustryFormClient.objects.filter(
        project_created=False, 
        status__in=['n', 'e', 's', 'm', 'd', 'accept_or_reject_expert', 'created', 'hidden', 'accept_reviewer', 'reject_reviewer', 'expert_reviewer']
        ).count()


        context['history_not_created_list'] = IndustryFormClient.objects.filter(~Q(status__in=["d", 'not-pay']), project_created=False,).order_by("-created")

        history_not_created_count= IndustryFormClient.objects.filter(
        project_created=False, 
        status__in=['n', 'r', 'rejected_by_expert', 'withdrew', 'e', 's', 'm', 'd', 'accept_or_reject_expert', 'created', 'hidden', 'accept_reviewer', 'reject_reviewer', 'expert_reviewer', 'send-contract-to-client', 'send-signed-contract', 'revised-contract', 'send-contract-to-director', 'revise-contract-by-director', 'accept-contract-by-director', 'not-response-contract']
        ).count()


        context['history_created_list'] = ResearchProject.objects.filter(
            project__client_form__formclint__project_created=True).order_by("-created")

        history_created_count = ResearchProject.objects.filter(
            project__client_form__formclint__project_created=True).order_by("-created").count()

        history_rejected_count_expert = IndustryFormExpert.objects.filter(formclint__status='rejected_by_expert').count()
        history_rejected_count_director = IndustryFormClient.objects.filter(status='r').count()


        context['history_list_count'] = history_created_count + history_not_created_count + history_rejected_count_expert + history_rejected_count_director
        
        # Withdrew
        context['projejct_withdrew'] = IndustryFormClient.objects.filter(status='withdrew')
        context['projejct_withdrew_count'] = IndustryFormClient.objects.filter(status='withdrew').count()

        context['request_review'] = IndustryFormExpert.objects.filter(expert=self.request.user, status__in=['review', 'view_projects', 'chek_score'], ).order_by("-created")
        context['count_not_response_proposal'] = IndustryExpertForSupervisor.objects.filter(status='not_response_proposal_send_to_director', client_form__expert=self.request.user).order_by("-created").count()
        
        return context
#detail list resubmition
class DirectorListResubmition(LoginRequiredMixin, SecurityDirector, DetailView):
    template_name = 'industry/director/director-list-resubmition.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryExpertForSupervisor.objects.filter(status='resubmition-to-director', client_form_id=pk)
        return context

def contract_client_detail(request, pk):
    template_name = 'industry/director/director-contract-detail.html'
    obj_project = IndustryFormClient.objects.get(id=pk)
    if obj_project.status == 'send-contract-to-director' and request.user.researchrole.director == True:
        
        if request.method == 'POST':
            status = request.POST.get('status')
            comment = request.POST.get('comment')

            if status == 'revise-contract':
                obj_project.status = 'revise-contract-by-director'
                obj_project.reason_rejectd = comment
                obj_project.save()


                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the signed contract", event_date=timezone.now(), tracing_project=obj_project)

                for i in obj_project.forms_client.filter(~Q(status="is_change")):
                    i.status = 'revise-contract-by-director'
                    i.save()

                    Notification(title='Project (ID: {})'.format(obj_project.id_project),
                    description='The director has revised the signed contract. For more information, go to your dashboard.', target=i.expert,
                    link='').save()
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well. \nThe director has revised the signed contract. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards \nTECVICO Corp.".format(i.expert.get_full_name())
                    e_destination = i.expert.researchrole.expert_email_address
                    send_new_email(e_subject,e_content,e_destination)
                    
                messages.success(request,'You revised the signed contract')

            elif status == 'accept-contract':
                obj_project.status = 'accept-contract-by-director'
                obj_project.save()
                
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director accepted the signed contract", event_date=timezone.now(), tracing_project=obj_project)

                for i in obj_project.forms_client.filter(~Q(status="is_change")):
                    i.status = 'accept-contract-by-director'
                    i.save()
                    
                    status_grade = ''
                    if i.status_value == 'gold':
                        status_grade = 'hard'
                    if i.status_value == 'silver':
                        status_grade = 'normal'
                    if i.status_value == 'bronze':
                        status_grade = 'easy'

                    value_respi = calculate_ResponsiveFee(obj_project.fund, i.valeu)

                    create_obj = ResearchProject.objects.create(
                        proposal_supervisor=i, status_value=status_grade, 
                        status='under_process_supervisor', value_supervisor=value_respi[4], 
                        value_mentor=value_respi[5], value_mmber=value_respi[6], value_lerner=value_respi[7],)

                    Notification(title='Project (ID: {})'.format(obj_project.id_project),
                    description='The director accepted the signed contract. For more information, go to your dashboard.', target=i.expert,
                    link='').save()
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well. \n The director accepted the signed contract. For more information, go to your dashboard.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards \nTECVICO Corp.".format(i.expert.get_full_name())
                    e_destination = i.expert.researchrole.expert_email_address
                    send_new_email(e_subject,e_content,e_destination)
                messages.success(request,'You revised the signed contract')

                    
            return redirect('industry:industry-director')

        context = {
            'object': obj_project
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")


def director_filter_evaluated(request):
    if request.user.researchrole.director == True :
        template_name = 'industry/director/director-filter-evaluated.html'

        context = {
            'check_score': IndustryFormExpert.objects.filter(status='chek_score').order_by("-created"),
            'check_score_span': IndustryExpertForSupervisor.objects.filter(status='d').count(),

            'suggest_reviewer': IndustryFormExpert.objects.filter(~Q(status="is_change"), status='expert_send_scores_to_director'),
            'suggest_reviewer_count': IndustryFormExpert.objects.filter(~Q(status="is_change"), status='expert_send_scores_to_director').count(),
        }
        
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


def director_filter_resubmition(request):
    if request.user.researchrole.director == True :
        template_name = 'industry/director/director-filter-resubmition.html'

        context = {
            'check_score': IndustryFormExpert.objects.filter(status='chek_score').order_by("-created"),
            'check_score_span': IndustryExpertForSupervisor.objects.filter(status='resubmition-to-director').count(), 

            'projects_resubmition': IndustryFormExpert.objects.filter(status='resubmited_project_send_to_director').order_by("-created"),
            'projects_resubmition_count': IndustryFormExpert.objects.filter(status='resubmited_project_send_to_director').order_by("-created").count(),

        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


def director_filter_contract(request):
    if request.user.researchrole.director == True :
        template_name = 'industry/director/director-filter-contract.html'


        context = {}
        context['contract_client'] = IndustryFormClient.objects.filter(status='send-contract-to-director')
        context['contract_client_count'] = IndustryFormClient.objects.filter(status='send-contract-to-director').count()
        context['main_super_visor'] = IndustryExpertForSupervisor.objects.filter(status='z')
        context['count_main_super_visor'] = IndustryExpertForSupervisor.objects.filter(status='z').count()

        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")



#detail review for expert
@login_required
def director_see_score_project(request, pk):
    expert_obj = get_object_or_404(IndustryFormExpert, pk=pk)
    user_role = ResearchRole.objects.filter(user=request.user).count()
    if user_role != 0 and expert_obj.status == 'expert_send_scores_to_director' or expert_obj.status == 'resubmited_project_send_to_director' and request.user.researchrole.director == True:

        if request.method == 'POST':
            status = request.POST.get('status')
            comment = request.POST.get('comment')
            value = request.POST.get('value')
            status_value = request.POST.get('status_value')



            if status == 'revise-to-expert':
                expert_obj.status = 'revise_director_to_expert'
                expert_obj.formclint.status = 'revise_director_to_expert'
                expert_obj.description_forum = comment
                expert_obj.save()
                expert_obj.formclint.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the project to the expert", event_date=timezone.now(), tracing_project=expert_obj.formclint)

                Notification(title='Project (ID: {})'.format(expert_obj.formclint.id_project),
                description='The project has been revised by the director. For more information, go to your dashboard.', target=expert_obj.expert,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(expert_obj.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been revised by the director. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(expert_obj.expert.get_full_name(), )
                e_destination = expert_obj.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                messages.success(request,'The project has been revised.')

            if status == 'revise-to-client':
                expert_obj.status = 'revise_director_to_client'
                expert_obj.deadline = timezone.now() + timedelta(3)
                expert_obj.formclint.rejected_date = timezone.now()
                
                expert_obj.formclint.reason_rejectd = comment
                expert_obj.formclint.status = 'revise_director_to_client'
                expert_obj.save()
                expert_obj.formclint.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the project to the client", event_date=timezone.now(), tracing_project=expert_obj.formclint)

                # Expert
                Notification(title='Project (ID: {})'.format(expert_obj.formclint.id_project),
                description='The project has been revised by the director. For more information, go to your dashboard.', target=expert_obj.expert,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(expert_obj.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been revised by the director. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(expert_obj.expert.get_full_name(), )
                e_destination = expert_obj.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)

                # Client
                Notification(title='Project (ID: {})'.format(expert_obj.formclint.id_project),
                description='The project has been revised. For more information, go to your dashboard.', target=expert_obj.formclint.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(expert_obj.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been revised. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(expert_obj.formclint.user.get_full_name(), expert_obj.expert.researchrole.expert_email_address)
                e_destination = expert_obj.formclint.user.email
                send_new_email(e_subject,e_content,e_destination)
                messages.success(request,'The project has been revised.')


            if status == 'accept-the-project':
                expert_obj.status = 'accept_project_pending_send_contarct_client'
                expert_obj.valeu = int(value)
                expert_obj.status_value = status_value
                expert_obj.formclint.status = 'accept_project_pending_send_contarct_client'
                expert_obj.save()
                expert_obj.formclint.save()
                


                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director accepted the project", event_date=timezone.now(), tracing_project=expert_obj.formclint)

                # Expert
                Notification(title='Project (ID: {})'.format(expert_obj.formclint.id_project),
                description='The project has been accepted successfully. For more information, go to your dashboard.', target=expert_obj.expert,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(expert_obj.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been accepted successfully. Go to your dashboard and send the contract to the client. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(expert_obj.expert.get_full_name(), )
                e_destination = expert_obj.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                
                messages.success(request,'The project has been accepted successfully.')
                
            return redirect("industry:industry-director")

        context = {
            'object': expert_obj,
            'reviewers': IndustryReviewer.objects.filter(status__in=['cancel_by_expert_p', 'automatically_cancel_p', 'send_director_project', 'not_see_project', 'breach_of_promis'], object_expert=expert_obj)
        }
        
        return render(request, 'industry/director/director-see-score-project.html', context)

    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-director')


@login_required
def director_history_not_created_detail(request, pk):
    template_name = 'industry/director/history-not-created-detail.html'
    project_obj = get_object_or_404(IndustryFormClient, pk=pk)

    object_expert = ''
    if IndustryFormExpert.objects.filter(formclint=project_obj):
        object_expert = IndustryFormExpert.objects.get(~Q(status="is_change"), formclint=project_obj)

    context = {
        'object': project_obj,
        'object_expert': object_expert,
        "experts": ResearchRole.objects.filter(expert=True),
    }
    return render(request, template_name, context)



@login_required
def director_history_created_detail(request, pk):
    template_name = 'industry/director/history-created-detail.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)

    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user)

    context = {
        'wbs_list': wbs_list,
        'project_obj': project_obj,
        "experts": ResearchRole.objects.filter(expert=True),
    }
    return render(request, template_name, context)

def change_expert(request):
    if request.method == 'POST':
        position = request.POST.get("position")
        id_obj = int(request.POST.get("id_obj"))
        id_project = int(request.POST.get("id_project"))
        expert_id = int(request.POST.get("expert_id"))

        obj_expert = IndustryFormExpert.objects.get(~Q(status="is_change"), id=id_obj)


        

        # Last expert
        Notification(title='Project (ID: {})'.format(obj_expert.formclint.id_project),
        description='You was replaced with a new expert. For more information, go to your dashboard.', target=obj_expert.expert,
        link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(obj_expert.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYou was replaced with a new expert. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_expert.expert.get_full_name(), )
        e_destination = obj_expert.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        create_obj = IndustryFormExpert.objects.create(expert=obj_expert.expert, formclint=obj_expert.formclint, status='is_change')
        
        # obj_expert.expert.researchrole.count_expert_change += 1
        obj_expert.expert.researchrole.save()
        last_expert = obj_expert.expert
        new_expert = User.objects.get(id=expert_id)



        obj_expert.expert = new_expert
        obj_expert.save()



        # New expert
        Notification(title='Project (ID: {})'.format(obj_expert.formclint.id_project),
        description='A new project has been assigned to you. For more information, go to your dashboard.', target=obj_expert.expert,
        link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(obj_expert.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYou are selected to undertake this project as a project expert.\nProject title: {} \nFund: ${} \nsubmitted in {}\nYou are expected to observe progress of the project and do the assigning tasks on it. You must observe on how well the steps of the project are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the director. You are also expected to give regular report on this project to the director. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp.".format(obj_expert.expert.get_full_name(), obj_expert.formclint.title, obj_expert.formclint.fund, date.today())
        e_destination = obj_expert.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request, 'The expert has been replaced with a new expert successfully.')

        if position == 'phase1':
            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director Changed the expert (the previous epxert: {} to new expert: {})".format(last_expert.get_full_name(), new_expert.get_full_name(), event_date=timezone.now(), tracing_project=obj_expert.formclint))
            
            return redirect("industry:project-director-history-not-created-detail", obj_expert.formclint.pk)
        else:
            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director Changed the expert (the previous epxert: {} to new expert: {})".format(last_expert.get_full_name(), new_expert.get_full_name(), event_date=timezone.now(), tracing_project_phase_2_id=id_project))
            
            return redirect("industry:project-director-history-created-detail", id_project)
            
def change_permissions_expert(request):
    if request.method == 'POST':
        position = request.POST.get('position')
        id_expert = int(request.POST.get('id_expert'))
        id_project = int(request.POST.get('id_project'))
        change_status = request.POST.get('change_status')
        remove_applicant = request.POST.get('remove_applicant')
        applicant_contract = request.POST.get('applicant_contract')
        directo_see_reviewer = request.POST.get('directo_see_reviewer')
        directo_create_project = request.POST.get('directo_create_project')
        director_reject_proposal = request.POST.get('director_reject_proposal')
        directo_a_or_r_mainsupervisor = request.POST.get('directo_a_or_r_mainsupervisor')


        obj_expert = IndustryFormExpert.objects.get(~Q(status="is_change"), id=id_expert)


        text_directo_a_or_r_mainsupervisor = ''
        text_directo_see_reviewer = ''
        text_directo_create_project = ''
        text_director_reject_proposal = ''

        if directo_a_or_r_mainsupervisor == 'on':
            text_directo_a_or_r_mainsupervisor = 'Access to accept ot reject the request, '

        if directo_see_reviewer == 'on':
            text_directo_see_reviewer = 'The reviewer scores, '

        if directo_create_project == 'on':
            text_directo_create_project = 'Access to create a project, '

        if director_reject_proposal == 'on':
            text_director_reject_proposal = 'Access to reject the proposal, '
            
        if directo_a_or_r_mainsupervisor == 'on' or directo_see_reviewer == 'on' or directo_create_project == 'on' or director_reject_proposal == 'on' :
            create_obj_tracing = Tracing.objects.create(position='The director gave the access(es) to the expert', user=request.user, 
                status="The director gave {}{}{}{} access to the expert".format(text_directo_a_or_r_mainsupervisor, text_directo_see_reviewer, text_directo_create_project, text_director_reject_proposal), event_date=timezone.now(), tracing_project=obj_expert.formclint)


        if change_status == 'on':
            obj_expert.change_status = True
        else:
            obj_expert.change_status = False

        if remove_applicant == 'on':
            obj_expert.remove_applicant = True
        else:
            obj_expert.remove_applicant = False

        if applicant_contract == 'on':
            obj_expert.contract_applicant = True
        else:
            obj_expert.contract_applicant = False

        if directo_see_reviewer == 'on':
            obj_expert.directo_see_reviewer = True
        else:
            obj_expert.directo_see_reviewer = False

        if directo_create_project == 'on':
            obj_expert.directo_create_project = True
        else:
            obj_expert.directo_create_project = False

        if director_reject_proposal == 'on':
            obj_expert.director_reject_proposal = True
        else:
            obj_expert.director_reject_proposal = False

        if directo_a_or_r_mainsupervisor == 'on':
            obj_expert.directo_a_or_r_mainsupervisor = True
        else:
            obj_expert.directo_a_or_r_mainsupervisor = False

        obj_expert.save()

        messages.success(request,'The access has been saved successfully.')

        if position == 'phase2':
            project_obj = get_object_or_404(ResearchProject, pk=id_project)
            return redirect('industry:project-director-history-created-detail', project_obj.pk)
        else:
            return redirect('industry:project-director-history-not-created-detail', obj_expert.formclint.pk)

class ReseachDirectorManageProject(LoginRequiredMixin, SecurityDirector, ListView):
    queryset = IndustryExpertForSupervisor.objects.all().order_by('-created')
    template_name = 'industry/director/director-management-project.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report_project'] = ResearchProject.objects.filter(status="on_going", project__status='report_d').order_by('-created')
        context['report_project_count'] = ResearchProject.objects.filter(status="on_going", project__status='report_d', project__view_report=False).order_by('-created').count()

        context['change_status'] = ResearchProject.objects.filter(status_change='send_to_director').order_by('-created')
        context['change_status_count'] = ResearchProject.objects.filter(status_change='send_to_director').order_by('-created').count()

        # Applicant
        advisor_count = SuperVizor.objects.filter(status__in=['send-to-director'],).count()
        mentor_count = Mentor.objects.filter(status__in=['send-to-director'],).count()
        member_count = Member.objects.filter(status__in=['send-to-director'],).count()
        learner_count = Lerner.objects.filter(status__in=['send-to-director'], ).count()

        advisor_obj = SuperVizor.objects.filter(status__in=['send-to-director'],)
        mentor_obj = Mentor.objects.filter(status__in=['send-to-director'],)
        member_obj = Member.objects.filter(status__in=['send-to-director'],)
        learner_obj = Lerner.objects.filter(status__in=['send-to-director'], )

        context['applicant_cart_count'] = advisor_count + mentor_count + member_count + learner_count 

        # context['applicant_list'] = ResearchProject.objects.filter(status='new').order_by("-created")


        applicant_list = []
        for i in advisor_obj:
            applicant_list.append(i.research)
            
        for i in mentor_obj:
            applicant_list.append(i.research)
            
        for i in member_obj:
            applicant_list.append(i.research)
            
        for i in learner_obj:
            applicant_list.append(i.research)

        applicant_list = set(applicant_list)
        applicant_list = list(applicant_list)
        context['applicant_list'] =applicant_list

        # Applicant remove

        advisor_remove_count = SuperVizor.objects.filter(status_remove='request-remove-send-to-the-director').count()
        mentor_remove_count = Mentor.objects.filter(status_remove='request-remove-send-to-the-director').count()
        member_remove_count = Member.objects.filter(status_remove='request-remove-send-to-the-director').count()
        learner_remove_count = Lerner.objects.filter(status_remove='request-remove-send-to-the-director' ).count()

        advisor__remove_obj = SuperVizor.objects.filter(status_remove='request-remove-send-to-the-director')
        mentor__remove_obj = Mentor.objects.filter(status_remove='request-remove-send-to-the-director')
        member__remove_obj = Member.objects.filter(status_remove='request-remove-send-to-the-director')
        learner__remove_obj = Lerner.objects.filter(status_remove='request-remove-send-to-the-director' )

        context['applicant_remove_cart_count'] = advisor_remove_count + mentor_remove_count + member_remove_count + learner_remove_count

        # context['applicant_remove_list'] = ResearchProject.objects.filter(status__in=['on_going', 'pending', 'on_hold']).order_by("-created")



        applicant_remove_list = []
        for i in advisor__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in mentor__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in member__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in learner__remove_obj:
            applicant_remove_list.append(i.research)

        applicant_remove_list = set(applicant_remove_list)
        applicant_remove_list = list(applicant_remove_list)
        context['applicant_remove_list'] = applicant_remove_list


        # History
        context['history_list'] = ResearchProject.objects.filter(
            project__client_form__formclint__project_created=True).order_by("-created")

        context['history_list_count'] = ResearchProject.objects.filter( 
            project__client_form__formclint__project_created=True).order_by("-created").count()


        # Temporal history
        context['temporal_history_count'] = ResearchProject.objects.filter(
            ~Q(status__in=["on_hold", "done", 'delete'])).order_by("-created").count()

        context['temporal_history_list'] = ResearchProject.objects.filter(
            ~Q(status__in=["on_hold", "done", 'delete'])).order_by("-created")

        return context



def director_Manageproject_applicant_detail(request, pk):
    template_name = 'industry/director/director-management-project-applicant-detail.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)
    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user)

    if request.method == 'POST':
        form_send_contract = SendContractApplicantForm(request.POST, request.FILES)
        if form_send_contract.is_valid():
            obj_id = form_send_contract.cleaned_data.get('obj_id')
            status = form_send_contract.cleaned_data.get('status')
            contract = form_send_contract.cleaned_data.get('contract')
            position_user = form_send_contract.cleaned_data.get('position_user')
            reason_rejection = form_send_contract.cleaned_data.get('reason_rejection')
            
            if position_user == 'advisor':
                obj_applicant = SuperVizor.objects.get(id=obj_id)

            elif position_user == 'mentor':
                obj_applicant = Mentor.objects.get(id=obj_id)

            elif position_user == 'member':
                obj_applicant = Member.objects.get(id=obj_id)

            elif position_user == 'learner':
                obj_applicant = Lerner.objects.get(id=obj_id)


            if status == 'revise_contract-applincat':
                obj_applicant.status = 'revised-director-to-expert'
                obj_applicant.reason_rejection = reason_rejection
                obj_applicant.deadline = timezone.now() + timedelta(2)
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the applicant`s contract ({}) and sent it to the expert".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                    

                
                messages.success(request,'You have revised the signed contract to the applicant successfully.')
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='The signed contract needs a revision. Go to your dashboard and revise it to the applicant to modify.', target=project_obj.project.client_form.expert,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe signed contract needs a revision. Go to your dashboard and proceed with it. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name())
                e_destination = project_obj.project.client_form.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have revised the signed contract to the expert.')

            if status == 'accept-applicant':
                obj_applicant.status = 'confirmed'
                # obj_applicant.reason_rejection = reason_rejection
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director accepted the applicant({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                

                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Congrats. Your request to join the project has been accepted. For more information, go to your dashboard.', target=obj_applicant.user,
                link='').save()


                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='The company accepted the signed contract sent by {}. For more information, go to your dashboard.'.format(obj_applicant.user.get_full_name()), target=project_obj.main_supervisor,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nCongrats. Your request to join the project has been accepted. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)



                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\nThe company accepted the signed contract sent by {}.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(), obj_applicant.user.get_full_name(). project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have accepeted the signed contract successfully.')

            return redirect("industry:director-applicant-detail", project_obj.pk)



    context = {
        'wbs_list': wbs_list,
        'project_obj': project_obj,
    }
    return render(request, template_name, context)


def director_Manageproject_applicant_remove(request, pk):
    template_name = 'industry/director/director-management-project-applicant-remove.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)
    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user)

    if request.method == 'POST':
        form_send_contract = SendContractApplicantForm(request.POST, request.FILES)
        if form_send_contract.is_valid():
            obj_id = form_send_contract.cleaned_data.get('obj_id')
            status = form_send_contract.cleaned_data.get('status')
            contract = form_send_contract.cleaned_data.get('contract')
            position_user = form_send_contract.cleaned_data.get('position_user')
            comment = form_send_contract.cleaned_data.get('reason_rejection')


            if position_user == 'advisor':
                obj_applicant = SuperVizor.objects.get(id=obj_id)

            elif position_user == 'mentor':
                obj_applicant = Mentor.objects.get(id=obj_id)

            elif position_user == 'member':
                obj_applicant = Member.objects.get(id=obj_id)

            elif position_user == 'learner':
                obj_applicant = Lerner.objects.get(id=obj_id)


            if status == 'request-reject-by-director':
                obj_applicant.status_remove = 'request-reject-by-director'
                obj_applicant.event_date = timezone.now()
                obj_applicant.comment = comment
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director rejected the request to remove the applicant({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                

                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Your request to remove the applicant from the project was rejected. For more information, go to your dashboard.', target=project_obj.main_supervisor,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYour request to remove the applicant from the project was rejected. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You rejected the applicant removal request.')

            if status == 'request-accpet-by-director':
                obj_applicant.status_remove = 'request-accpet-by-director'
                obj_applicant.event_date = timezone.now()
                obj_applicant.comment = comment
                obj_applicant.save()

                print('obj_applicant.comment', obj_applicant.comment)

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director rejected the request to remove the applicant({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)


                for i in RequestUserForProject.objects.filter(project_request=project_obj, user=obj_applicant.user):
                    i.status = 'remove'
                    i.save()



                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Your applicant removal request was accepted. For more information, go to your dashboard.', target=project_obj.main_supervisor,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYour request to remove the applicant from the project was accepted. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='You were removed from the project. For more information, go to your dashboard.', target=obj_applicant.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nTECVICO is sorry to inform you that you were removed from the project because: {}\nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), obj_applicant.comment, project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have accepted applicant removal request.')

            return redirect("industry:director-applicant-remove", project_obj.pk)



    context = {
        'wbs_list': wbs_list,
        'project_obj': project_obj,
    }
    return render(request, template_name, context)



@login_required
def director_statuschange_detail(request, pk):
    status_ch = get_object_or_404(ResearchProject, pk=pk)

    form_reject_status = SendRejectForm(request.POST)
    if form_reject_status.is_valid():

        status = form_reject_status.cleaned_data.get("status")
        reason_rejectd = form_reject_status.cleaned_data.get("reason_rejectd")

        status_ch.reason_reject_expert = reason_rejectd
        status_ch.status_change = status
        status_ch.save()

        create_obj_tracing = Tracing.objects.create(
            position='Director', user=request.user, status="The director rejected the request to change the project status from the supervisor", event_date=timezone.now(), tracing_project_phase_2=status_ch)
       

        Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project), 
            description='Your request to change the project status was rejected. For more information, go to your dashboard.', target=status_ch.main_supervisor, 
            link='').save()

        if status_ch.status == 'new':
            new_status = 'New'

        elif status_ch.status == 'on_going':
            new_status = 'Ongoing'

        elif status_ch.status == 'pending':
            new_status = 'Pending'

        elif status_ch.status == 'on_hold':
            new_status = 'On hold'

        elif status_ch.status == 'done':
            new_status = 'Done'

        if status_ch.status_change_choices == 'new':
            new_request_status = 'New'

        elif status_ch.status_change_choices == 'on_going':
            new_request_status = 'Ongoing'

        elif status_ch.status_change_choices == 'pending':
            new_request_status = 'Pending'

        elif status_ch.status_change_choices == 'on_hold':
            new_request_status = 'On hold'

        elif status_ch.status_change_choices == 'done':
            new_request_status = 'Done'

        e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYour status change request from {} to {} was rejected.\n For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(status_ch.main_supervisor.get_full_name(), new_status, new_request_status, status_ch.project.client_form.expert.researchrole.expert_email_address)
        e_destination = status_ch.main_supervisor.email
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request,'You rejected status change request.')
        return redirect("industry:research-director-manage-project")

    form_accept_status = FormStatus(request.POST)
    if form_accept_status.is_valid():

        status = form_accept_status.cleaned_data.get("status")

        status_ch.status_change = status
        status_ch.status = status_ch.status_change_choices
        status_ch.save()


        if status_ch.status == 'new':
            new_status = 'New'

        elif status_ch.status == 'on_going':
            new_status = 'Ongoing'

        elif status_ch.status == 'pending':
            new_status = 'Pending'

        elif status_ch.status == 'on_hold':
            new_status = 'On hold'

        elif status_ch.status == 'done':
            new_status = 'Done'

        if status_ch.status_change_choices == 'new':
            new_request_status = 'New'

        elif status_ch.status_change_choices == 'on_going':
            new_request_status = 'Ongoing'

        elif status_ch.status_change_choices == 'pending':
            new_request_status = 'Pending'

        elif status_ch.status_change_choices == 'on_hold':
            new_request_status = 'On hold'

        elif status_ch.status_change_choices == 'done':
            new_request_status = 'Done'

            
        for i in RequestUserForProject.objects.filter(project_request=status_ch, status='request'):
            i.status = 'reject'
            i.save()
                
        create_obj_tracing = Tracing.objects.create(
            position='Director', user=request.user, status="The director accepted the request to change the project status to {}".format(status_ch.status), event_date=timezone.now(), tracing_project_phase_2=status_ch)
        

        Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project), 
            description='Your request to change the project status has been accepted. For more information, go to your dashboard.', target=status_ch.main_supervisor, 
            link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYour status change request from {} to {} has been accepted.\n For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}.  \n\nThank you \nBest regards \nTECVICO Corp.".format(status_ch.main_supervisor.get_full_name(), new_status, new_request_status, status_ch.project.client_form.expert.researchrole.expert_email_address)
        e_destination = status_ch.main_supervisor.email
        send_new_email(e_subject,e_content,e_destination)


        for i in status_ch.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
            e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been changed to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status)
            e_destination = i.user.email
            send_new_email(e_subject,e_content,e_destination)

            Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project,), 
                description='The project has been changed to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                link=reverse('industry:industry-view-edit', args=[status_ch.pk])).save()


        for i in status_ch.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
            e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been changed to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status)
            e_destination = i.user.email
            send_new_email(e_subject,e_content,e_destination)

            Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project,), 
                description='The project has been changed to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                link=reverse('industry:industry-view-edit', args=[status_ch.pk])).save()


        for i in status_ch.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
            e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been changed to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status)
            e_destination = i.user.email
            send_new_email(e_subject,e_content,e_destination)

            Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project,), 
                description='The project has been changed to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                link=reverse('industry:industry-view-edit', args=[status_ch.pk])).save()


        for i in status_ch.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
            e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been changed to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status)
            e_destination = i.user.email
            send_new_email(e_subject,e_content,e_destination)

            Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project,), 
                description='The project has been changed to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                link=reverse('industry:industry-view-edit', args=[status_ch.pk])).save()


        e_subject ="TECVICO Project (Project ID: {})".format(status_ch.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nThe director accepted the status change request. Thus, the project has been changed to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.  \n\nThank you \nBest regards \nTECVICO Corp.".format(status_ch.project.client_form.expert.get_full_name(), new_status)
        e_destination = status_ch.project.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        Notification(title='Project (ID: {})'.format(status_ch.project.client_form.formclint.id_project,), 
            description='The director accepted the status change request. Thus, the project has been changed to {} status. For more information, go to your dashboard.'.format(new_status), target=status_ch.project.client_form.expert, 
            link=reverse('industry:industry-view-edit', args=[status_ch.pk])).save()



        messages.success(request,'You have accepeted status change request successfully.')
        return redirect("industry:research-director-manage-project")

    context = {
        'change_status': status_ch,
        'form_reject_status': form_reject_status,
        'form_accept_status': form_accept_status,
    }
    return render(request, 'industry/director/research-change-status.html', context)


# class ReseachDirectorReportDeteail(LoginRequiredMixin, SecurityDirector, DetailView):
#     template_name = 'industry/director/research-director-report-detail.html'
#     def get_object(self):
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(IndustryExpertForSupervisor, pk=pk)

@login_required
def director_project_report(request, pk):
    template_name = 'industry/director/research-director-report-detail.html'
    obj_project = ResearchProject.objects.get(id=pk)

    obj_project.project.view_report = True
    obj_project.project.save()

    context = {
        'object': obj_project,
        "wbs_list": TimeProgramming.objects.filter(sub=obj_project.project),
        'today': date.today()
    }
    return render(request, template_name,context)
        

class ReseachDirectorReportTimePro(LoginRequiredMixin, SecurityDirector, DetailView):
    template_name = 'industry/director/research-director-time-pro-detail.html'
    def get_object(self):
        global report_detail
        pk = self.kwargs.get('pk')
        report_detail = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
        return report_detail
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['report'] = TimeProgramming.objects.filter(sub=report_detail)
        return context
        
@login_required
def reseach_director_WBS(request, pk):
    template_name = 'industry/director/research-director-time-pro-detail.html'
    report_detail = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    form = SeeReportForm(request.POST or None)
    if form.is_valid():
        report_detail.view_report = True
        report_detail.save()

    context = {
        'object': report_detail,       
        'report': TimeProgramming.objects.filter(sub=report_detail)
    }
    return render(request, template_name, context)


@login_required
def director_detail_createproject(request, pk):
    template_name = 'industry/director/director-detail-mainsupervisor.html'
    create_p = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    if create_p.status == 'z' and request.user.researchrole.director == True:
    
        if request.method == 'POST':
            form = CreateNewProject(request.POST, request.FILES)
            if form.is_valid():
                status = form.cleaned_data.get("status")
                change_status = request.POST.get("change_status")
                applicant_contract = request.POST.get("applicant_contract")
                remove_applicant = request.POST.get("remove_applicant")
    
    
                if create_p.client_form.formclint.main_supervisor:
                    create_obj_tracing = Tracing.objects.create(
                        position='Director', user=request.user, status="The director moved the project to new status", event_date=timezone.now(), tracing_project=create_p.client_form.formclint)
    
    
                if change_status == 'on':
                    create_p.client_form.change_status = True
                else:
                    create_p.client_form.change_status = False
    
                if remove_applicant == 'on':
                    create_p.client_form.remove_applicant = True
                else:
                    create_p.client_form.remove_applicant = False
    
                if applicant_contract == 'on':
                    create_p.client_form.contract_applicant = True
                else:
                    create_p.client_form.contract_applicant = False
    
    
                create_p.status = 'n'
                create_p.follow_project = 'create_project'
                create_p.client_form.status='hidden'
                create_p.client_form.formclint.project_created=True
                create_p.client_form.formclint.created_date=timezone.now()
                create_p.client_form.formclint.status = 'created'
                create_p.save()
                create_p.client_form.save()
                create_p.client_form.formclint.save()
    
                value_respi = calculate_ResponsiveFee(create_p.client_form.formclint.fund, create_p.client_form.valeu)
    
                status_grade = ''
                if create_p.client_form.status_value == 'gold':
                    status_grade = 'hard'
                if create_p.client_form.status_value == 'silver':
                    status_grade = 'normal'
                if create_p.client_form.status_value == 'bronze':
                    status_grade = 'easy'
                    
                is_project = ResearchProject.objects.filter(proposal_supervisor=create_p.client_form, status='under_process_supervisor')
    
                if is_project:
                    obj_project = ResearchProject.objects.get(proposal_supervisor=create_p.client_form, status='under_process_supervisor')
                    obj_project.status = 'new'
                    obj_project.project = create_p
                    obj_project.main_supervisor = create_p.supervisor
                    obj_project.value_supervisor = value_respi[4]
                    obj_project.value_mentor = value_respi[5]
                    obj_project.value_mmber = value_respi[6]
                    obj_project.value_lerner = value_respi[7]
                    obj_project.status_value = status_grade
                    obj_project.save()
                    
                    create_obj_tracing = Tracing.objects.create(
                        position='Director', user=request.user, status="The director moved the project to new status", event_date=timezone.now(), tracing_project_phase_2=obj_project)
                else:
                    new_from = ResearchProject.objects.create(project=create_p, main_supervisor=create_p.supervisor, 
                        status='new', value_supervisor=value_respi[4], value_mentor=value_respi[5], 
                        value_mmber=value_respi[6], value_lerner=value_respi[7], status_value=status_grade)
    
                    create_obj_tracing = Tracing.objects.create(
                        position='Director', user=request.user, status="The director moved the project to new status", event_date=timezone.now(), tracing_project_phase_2=new_from)
    
    
                forum_cat = MainCategory.objects.get(slug='project') 
                create_forum_cat = Category.objects.create(
                    sub_category=forum_cat,
                    img = create_p.upload_pictures, slug="project-{}".format(create_p.client_form.formclint.id),
                    title=create_p.client_form.formclint.title) 
    
                if create_p.client_form.formclint.main_supervisor is None:
                    # Supervisor
                    e_subject ="TECVICO Project (Project ID: {})".format(create_p.client_form.formclint.id_project, ) 
                    e_content ="Dear{}\nHello\nHope you are going well. \nTitle:{} \nSubmitted date: {}\n Congrats! TECVICO is writing this letter with reference to the proposal Submitted. The proposal has been reviewed and we are informing you that your proposal fully fits with our criteria and therefore we have accepted it. The state of project has been changed to new status. You are allowed to arrange your team. It will be a pleasure for our company to work with you. \n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {} \n\nThank you for your efforts and time. \nBest regards \nTECVICO Corp.".format(create_p.supervisor.get_full_name(), create_p.client_form.formclint.title, date.today(), create_p.client_form.expert.researchrole.expert_email_address)
                    e_destination =create_p.supervisor.email
                    send_new_email(e_subject,e_content,e_destination)
                
                # Expert
                e_subject ="TECVICO Project (Project ID: {})".format(create_p.client_form.formclint.id_project, ) 
                e_content ="Dear {} \nHello\nHope you are going well. \n \nDo not reply to this Email \n\nThank you \nBest regards \nTECVICO Corp.".format(create_p.client_form.expert.get_full_name(),)
                e_destination = create_p.client_form.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                
                # Client
                e_subject ="TECVICO Project (Project ID: {})".format(create_p.client_form.formclint.id_project, ) 
                e_content ="Dear {} \nHello\nHope you are going well. \nCongrats. Your project has been moved to new status. For more information, go to your dashboard. \nTitle: {}\nDescription (Abstract): {}\nFund: ${}\nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(create_p.client_form.formclint.user.get_full_name(), create_p.client_form.formclint.title, create_p.client_form.formclint.abstrack, create_p.client_form.formclint.fund, create_p.client_form.expert.researchrole.expert_email_address)
                e_destination =create_p.client_form.formclint.user.email
                send_new_email(e_subject,e_content,e_destination)
        
                
                if is_project:
                    pass
                else:
                    if new_from is not None:
                        supervisors = IndustryExpertForSupervisor.objects.filter(client_form=create_p.client_form)
                        for i in supervisors:
                            if i.status != 'n' :
                                i.status = 'h'
                                i.save()
                                
                        messages.success(request,'The project has been changed to new status successfully.')
                        if request.user.researchrole.director == True:
                            return redirect("industry:industry-director")
                        else:
                            return redirect("industry:industry-expert-list")
                        
        else:
            form = CreateNewProject
        context = {
            'object': create_p,
            'form': form
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")

#selection expert

def director_revise_contract(request):
    if request.method == 'POST':
        obj_id = int(request.POST.get('obj_id'))
        revision_reason = request.POST.get('revision_reason')

        obj_supervisor = IndustryExpertForSupervisor.objects.get(id=obj_id)

        obj_supervisor.status = 'director_revise_contract'
        obj_supervisor.reason_reject = revision_reason
        if obj_supervisor.client_form.formclint.main_supervisor:
            obj_supervisor.client_form.formclint.follow_project = 'p_main_contract_revise_by_director'
            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director revised the contract", event_date=timezone.now(), tracing_project=obj_supervisor.client_form.formclint)

        obj_supervisor.save()
        obj_supervisor.client_form.formclint.save()
        

                
        Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
        description='The director has revised the contract. You must go to your dashboad and proceed with it.', target=obj_supervisor.client_form.expert,
        link='').save()
        

        e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
        e_content = "Dear {}\nHello\nHope you are going well.\n The director has revised the signed contact. Go to your dashboard and proceed with it.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_supervisor.client_form.expert.get_full_name())
        e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)


        messages.success(request,'You have revised the contract.')
        return redirect("industry:industry-director")


@login_required
def direcotr_select_expert(request, pk):
    users = User.objects.filter(researchrole__expert=True)
    form_client = IndustryFormClient.objects.get(pk=pk)
    user_role = ResearchRole.objects.filter(user=request.user).count()
    if form_client.status == 'n' or form_client.status == 'accept_reviewer' or form_client.status == 'reject_reviewer' and user_role != 0 and request.user.researchrole.director == True:

        form = SendExpertForm(request.POST or None, initial={"name": form_client.name, "fund": form_client.fund,  
                            "title": form_client.title, "abstrack": form_client.abstrack, 
                            "data_set_link": form_client.data_set_link,  "start_date": form_client.start_date,
                            "end_date": form_client.end_date, 
                            "equipment": form_client.equipment, "requirement": form_client.requirement})
        if form.is_valid():
            name = form.cleaned_data.get("name")
            fund = form.cleaned_data.get("fund")
            title = form.cleaned_data.get("title")
            abstrack = form.cleaned_data.get("abstrack")
            data_set_link = form.cleaned_data.get("data_set_link")
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")
            equipment = form.cleaned_data.get("equipment")
            requirement = form.cleaned_data.get("requirement")
            user_list = form.cleaned_data.get("user_list")
            

            directo_a_or_r_mainsupervisor = form.cleaned_data.get("directo_a_or_r_mainsupervisor")
            directo_see_reviewer = form.cleaned_data.get("directo_see_reviewer")
            directo_create_project = form.cleaned_data.get("directo_create_project")
            director_reject_proposal = form.cleaned_data.get("director_reject_proposal")
            
            form_client.name = name
            form_client.fund = fund
            form_client.title = title
            form_client.abstrack = abstrack
            form_client.data_set_link = data_set_link
            form_client.start_date = start_date
            form_client.end_date = end_date
            form_client.equipment = equipment
            form_client.requirement = requirement 
            form_client.follow_project = 'send_contract_to_client' 

            form_client.save()
            
            if directo_a_or_r_mainsupervisor == True:
                email_directo_a_or_r_mainsupervisor = 'Accept or reject projec, '
            else:
                email_directo_a_or_r_mainsupervisor=''
                
            if directo_see_reviewer == True:
                email_directo_see_reviewer = 'Select the best supervior based on reviewrs evaluation, '
            else:
                email_directo_see_reviewer=''
                
            if directo_create_project == True:
                email_directo_create_project = 'Change project status, '
            else:
                email_directo_create_project=''
                
            if director_reject_proposal == True:
                email_director_reject_proposal = 'Reject proposal, '
            else:
                email_director_reject_proposal=''

            expert_user = User.objects.get(username=user_list)
            

            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director selected an expert", event_date=timezone.now(), tracing_project=form_client)

            
            if form_client.main_supervisor:
                if directo_a_or_r_mainsupervisor == True:
                    form_client.status = 'hidden'
                    form_client.save()
                    
                    create_expert = IndustryFormExpert.objects.create(expert=expert_user, formclint=form_client, status='h', 
                    directo_a_or_r_mainsupervisor=directo_a_or_r_mainsupervisor, directo_see_reviewer=directo_see_reviewer, 
                    directo_create_project=directo_create_project, director_reject_proposal=director_reject_proposal, 
                    )
                    IndustryExpertForSupervisor.objects.create(client_form=create_expert, main_supervisor=True, status='special_expert', supervisor=create_expert.formclint.user)
                    
                else:
                    form_client.status = 'm'
                    form_client.follow_project = 'p_main_new'
                    form_client.save()
                    
                    create_expert = IndustryFormExpert.objects.create(expert=expert_user, formclint=form_client, status='h', 
                    directo_a_or_r_mainsupervisor=directo_a_or_r_mainsupervisor, directo_see_reviewer=directo_see_reviewer, 
                    directo_create_project=directo_create_project, director_reject_proposal=director_reject_proposal, 
                    )
                    IndustryExpertForSupervisor.objects.create(client_form=create_expert, main_supervisor=True, status='m', supervisor=create_expert.formclint.user)
                    
            else:
                if directo_a_or_r_mainsupervisor == True:
                    form_client.status = 'accept_or_reject_expert'
                    form_client.save()
                    
                    IndustryFormExpert.objects.create(expert=expert_user, formclint=form_client, status='h', 
                    directo_a_or_r_mainsupervisor=directo_a_or_r_mainsupervisor, directo_see_reviewer=directo_see_reviewer, 
                    directo_create_project=directo_create_project, director_reject_proposal=director_reject_proposal, 
                    )
                    
                else:
                    form_client.status= 'e'
                    form_client.save()
                    IndustryFormExpert.objects.create(expert=expert_user, formclint=form_client, status='n', 
                    directo_a_or_r_mainsupervisor=directo_a_or_r_mainsupervisor, directo_see_reviewer=directo_see_reviewer, 
                    directo_create_project=directo_create_project, director_reject_proposal=director_reject_proposal, 
                    )
            expert_user.researchrole.ongoing_project_expert += 1
            expert_user.researchrole.ongoing_detail_project_expert += str(form_client.id)
            expert_user.researchrole.ongoing_detail_project_expert += ' ,'
            expert_user.researchrole.save()

            text_directo_a_or_r_mainsupervisor = ''
            text_directo_see_reviewer = ''
            text_directo_create_project = ''
            text_director_reject_proposal = ''

            if directo_a_or_r_mainsupervisor == True:
                text_directo_a_or_r_mainsupervisor = 'Access to accept ot reject the request, '

            if directo_see_reviewer == True:
                text_directo_see_reviewer = 'The reviewer scores, '

            if directo_create_project == True:
                text_directo_create_project = 'Access to create a project, '

            if director_reject_proposal == True:
                text_director_reject_proposal = 'Access to reject the proposal, '
            
            if directo_a_or_r_mainsupervisor == True or directo_see_reviewer == True or directo_create_project == True or director_reject_proposal == True :
                
                create_obj_tracing = Tracing.objects.create(position='Director', user=request.user, 
                    status="The director gave access(es) such as {}{}{}{} to the expert".format(text_directo_a_or_r_mainsupervisor, text_directo_see_reviewer, text_directo_create_project, text_director_reject_proposal), event_date=timezone.now(), tracing_project=form_client)

                e_subject ="TECVICO Project (Project ID: {})".format(form_client.id_project, ) 
                e_content ="Dear {}\nHello\nHope you are going well.\nYou are selected to undertake this project as a project expert .\nTitle: {} \nFund: ${} \nSubmitted in {}\nMeanwhile, you have been given director’s access(es) such as: \n{}\n{}\n{}\n{}.\nYou are expected to observe progression of the project and do the assigning tasks on it. You must observe on how well the steps of the project are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the director. You are also requested to give regular report on this project to the director. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert_user.get_full_name(), form_client.title, form_client.fund, date.today(), email_directo_a_or_r_mainsupervisor, email_directo_see_reviewer, email_directo_create_project, email_director_reject_proposal)
                e_destination =expert_user.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                
            else:
                
                e_subject ="TECVICO Project (Project ID: {})".format(form_client.id_project, )  
                e_content ="Dear {}\nHello\nHope you are going well.\nYou are selected to undertake this project as a project expert.\nProject title: {} \nFund: ${} \nsubmitted in {}\nYou are expected to observe progress of the project and do the assigning tasks on it. You must observe on how well the steps of the project are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the director. You are also expected to give regular report on this project to the director. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp.\n".format(expert_user.get_full_name(), form_client.title, form_client.fund, date.today())
                e_destination =expert_user.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                
            Notification(title='Research (ID: {})'.format(form_client.id_project), 
            description='A new project has been assigned to you. For more information, go to your dashboard.', target=expert_user, 
            link=reverse('industry:industry-expert-detail', args=[form_client.pk])).save()
                
            reviewers = IndustryReviewer.objects.filter(object_client=form_client, status__in=['new_project', 'accept_project', 'revise_by_director_p'])
            for i in reviewers:
                i.status = 'cancel_by_director'
                i.save()
            messages.success(request,'An expert has been assigned or given the access successfully.')
            return redirect("industry:industry-director")
            
            
        context = {
            "form": form,
            "users": users,
            "form_client": form_client,
        }

        
        
        return render(request, 'industry/director/industry-select-expert.html', context)

    else:

        if user_role == 0 :
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-director')
        
        

def direcotr_reject_project(request):
    if request.method == 'POST':
        id_project = int(request.POST.get("id_project"))
        rejetion_reason = request.POST.get("rejetion_reason")
        #main supervisor
        id_obj_supervisor = int(request.POST.get("id_obj_supervisor"))

        obj_project = IndustryFormClient.objects.get(id=id_project)

        obj_project.status = 'r'
        obj_project.reason_rejectd = rejetion_reason
        obj_project.rejected_date = timezone.now()
        obj_project.save()


        
        if obj_project.main_supervisor :
            RejectProtocol(request, 'P', obj_project, obj_project.fund)
        else:
            RejectProtocol(request, 'P', obj_project, obj_project.fund)

        # if obj_project.main_supervisor :
        create_obj_tracing = Tracing.objects.create(
            position='Director', user=request.user, status="The director rejected the project", event_date=timezone.now(), tracing_project=obj_project)


        if id_obj_supervisor != 0:
            obj_supervisor = IndustryExpertForSupervisor.objects.get(id=id_obj_supervisor)

            obj_supervisor.status = 'h'
            obj_supervisor.reason_reject = rejetion_reason
            obj_supervisor.client_form.status = 'h'
            obj_supervisor.follow_project = 'reject_by_director'

            obj_supervisor.save()
            obj_supervisor.client_form.save()


            Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                description='The director rejected the project. For more information, go to your dashboard.', target=obj_supervisor.client_form.expert, 
                link='industry:industry-supervisor-list').save()




            e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, )
            e_content ="Dear {} \nHello\nHope you are going well. \nThe director rejected the project. \n Title: “{}” \n Submitted on “{}”. \nDo not reply to this Email. If you have more questions or concerns, plaese contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \n TECVICO Corp.".format(obj_supervisor.client_form.expert.get_full_name(), obj_supervisor.client_form.formclint.title, date.today())
            e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)



            Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                description='Your propposal has been rejected. For more information, go to your dashboard.', target=obj_project.user, 
                link='industry:industry-supervisor-list').save()
        else:
            Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                description='Your project has been rejected. For more information, go to your dashboard.', target=obj_project.user, 
                link='industry:industry-supervisor-list').save()

        e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
        e_content ="Dear {} \nHello\nHope you are going well.\nThe company has reviewed your project.\nTitle: {}\nSubmitted date: {} \nTECVICO is very grateful to you that you considered it worthy of the new project. With the help of this letter, TECVICO is feeling very sorry to decline to work on this project offer because:\n “{}”, \nAs you can completely see those comments on your dashboard. You will also be able to re-submit this project based on considering those comments. \nWe welcome you to submit other projects in the future.Thank you for your efforts and time. We hope to work with you in the near future. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com \n\nThank you\n Best regards\n TECVICO Corp.".format(obj_project.user.get_full_name(), obj_project.title, date.today(), obj_project.reason_rejectd)
        e_destination =obj_project.user.email
        send_new_email(e_subject,e_content,e_destination)
        
        messages.error(request,'You rejected the project.')
        return redirect("industry:industry-director")


@login_required
def form_reject_special_expert(request, pk):
    form_client = IndustryFormExpert.objects.get(~Q(status="is_change"), pk=pk)
    form = SendRejectForm(request.POST, initial={"status": form_client.formclint.status, "form_client": form_client.formclint.reason_rejectd, })
    if form.is_valid():
        status = form.cleaned_data.get("status")
        reason_rejectd = form.cleaned_data.get("reason_rejectd")
        
        form_client.formclint.status= 'r'
        form_client.formclint.reason_rejectd= reason_rejectd
        form_client.formclint.save()
        
        e_subject ="TECVICO Project (Project ID: {})".format(form_client.formclint.id_project, )  
        e_content ="Dear {} \nHello\nHope you are going well.\nThe company has reviewed your project.\nTitle: {}\nSubmitted date: {} \nTECVICO is very grateful to you that you considered it worthy of the new project. With the help of this letter, I am feeling very sorry to decline to work on this project offer because:\n “{}”, as you can see those comments on your dashboard completely. \nYou will also be able to re-submit this project based on considering those comments. \nWe welcome you to submit other projects in the future.Thank you for your efforts and time. We hope to work with you in the near future. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com \n\nThank you \nBest regards \nTECVICO Corp.".format(form_client.formclint.user.get_full_name(), form_client.formclint.title, date.today(), form_client.formclint.reason_rejectd)
        e_destination =form_client.formclint.user.email
        send_new_email(e_subject,e_content,e_destination)
        

        form_client.delete()
        
        return redirect("dashboard-page")
    context = {
        "form": form,
        'form_client': form_client
    }

    return render(request, 'industry/director/industry-reject.html', context) 


class DirectorListScoresAndSupervisor(LoginRequiredMixin, SecurityDirector, DetailView):
    template_name = 'industry/director/director-list-supervisor.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='d', client_form_id=pk)
        return context

#detail review for expert
@login_required
def director_see_score(request, pk):
    director_score = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    user_role = ResearchRole.objects.filter(user=request.user).count()
    if user_role != 0 and director_score.status == 'resubmition-to-director' or director_score.status == 'd' and request.user.researchrole.director == True:
        roles = ResearchRole.objects.all() 
        form_reject = FormRejectDirector(request.POST,  request.FILES, initial={"status": director_score.status,
            "reason_reject": director_score.reason_reject,})
        if form_reject.is_valid():
            status = form_reject.cleaned_data.get("status")
            reason_reject = form_reject.cleaned_data.get("reason_reject")
            
            if director_score.client_form.formclint.main_supervisor:
                director_score.client_form.formclint.user.memberprofile.balance += director_score.client_form.formclint.fund
                director_score.client_form.formclint.user.memberprofile.save()
            
            director_score.status = 'h'
            director_score.reason_reject = reason_reject
            director_score.rejected_date = timezone.now()
            director_score.follow_project = 'reject_by_director'
            director_score.client_form.formclint.follow_project = 'under_process_by_expert'
            director_score.save()
            director_score.client_form.formclint.save()


            if director_score.client_form.formclint.main_supervisor:
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director rejected the proposal", event_date=timezone.now(), tracing_project=director_score.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director rejected the proposal", event_date=timezone.now(), tracing_supervisor=director_score)
            



            e_subject ="TECVICO Project (Project ID: {})".format(director_score.client_form.formclint.id_project, )
            e_content ="Dear {}\nHello \nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with us. Unfortunately, your project was rejected by our board of directors because of: \n“{}”, as you can see those comments on your dashboard completely. We welcome you to submit other projects in the future.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com \n\n Thank you \nSincerely \nTECVICO Corp.".format(director_score.supervisor.get_full_name(), director_score.client_form.formclint.title, director_score.reason_reject)
            e_destination = director_score.supervisor.email
            send_new_email(e_subject,e_content,e_destination)


            e_subject ="TECVICO Project (Project ID: {})".format(director_score.client_form.formclint.id_project, ) 
            e_content = "Dear {}\nHello\nHope you are going well. \nThe director rejected the project because of:\n “{}”, as you can see those comments on your dashboard completely. TECVICO hopes to see you as a project expert in other projects in the future.\nDon’t reply to this Email.\nIf you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com \n\nThank you \nSincerely\nTECVICO Corp.".format(director_score.client_form.expert.get_full_name(), director_score.client_form.formclint.title, director_score.reason_reject)
            e_destination = director_score.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
                
            messages.error(request,'The proposal was rejected.')
            return redirect("industry:industry-director")


        form_accept = StatusAcceptDirectorFrom(request.POST,  request.FILES, )
        if form_accept.is_valid():
            value = form_accept.cleaned_data.get("value")
            status_d = form_accept.cleaned_data.get("status_d")
            status_value = form_accept.cleaned_data.get("status_value")
            
            director_score.client_form.valeu= value
            director_score.client_form.status_value= status_value
            director_score.status= 'x'
            director_score.follow_project= 'accept_by_director'
            director_score.save()
            director_score.client_form.save()
            if director_score.client_form.formclint.main_supervisor:
                director_score.client_form.formclint.follow_project = 'p_main_accept_proposal_director'

                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director accepted the proposal and sent it to the expert for contract", event_date=timezone.now(), tracing_project=director_score.client_form.formclint)

            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director accepted the proposal and sent it to the expert for contract", event_date=timezone.now(), tracing_supervisor=director_score)

            director_score.client_form.formclint.save()


            e_subject ="TECVICO Project (Project ID: {})".format(director_score.client_form.formclint.id_project, )
            e_content ="Dear {} \nHello\nHope you are going well. \nThe director accepted the project. \n Title: “{}” \n Submitted on “{}”. \nYou must go to your dashboard and send the contract to the supervisor. \nDo not reply to this Email. This email has been sent automatically. If you have more questions or concerns, plaese contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \n TECVICO Corp.".format(director_score.client_form.expert.get_full_name(), director_score.client_form.formclint.title, date.today())
            e_destination = director_score.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            messages.success(request,'The proposal has been sent to the expert successfully.')
            return redirect("industry:industry-director")


        supervisors = IndustryExpertForSupervisor.objects.filter(
            client_form=director_score.client_form, status__in=['t', 'z', 'g', 'n', 'x']).count()

        if supervisors == 0:
            is_project = False
        else:
            is_project = True

        context = {
            'object': director_score,
            'is_project': is_project,
            'form_accept': form_accept,
            'form_reject': form_reject,
            'reviewer': IndustryReviewer.objects.filter(status='e', object_supervisor=director_score)
        }
        
        return render(request, 'industry/director/director-see-score.html', context)

    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-director')

def revise_proposal_to_expert(request):
    if request.method == 'POST':
        revision_reason = request.POST.get('revision_reason')
        id_supervisor = int(request.POST.get('id_supervisor'))

        obj_supervisor = IndustryExpertForSupervisor.objects.get(id=id_supervisor)

        obj_supervisor.reason_reject = revision_reason
        obj_supervisor.status = 'revise-proposal-to-expert'
        obj_supervisor.client_form.status = 'view_projects'
        


        Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
        description='The proposal has been revised by the director. For more information, go to your dashboard.', target=obj_supervisor.client_form.expert,
        link='').save()
        

        e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nThe proposal has been revised by the director. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to contact the director projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_supervisor.client_form.expert.get_full_name(),)
        e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        if obj_supervisor.client_form.formclint.main_supervisor:
            obj_supervisor.client_form.formclint.follow_project = 'p_main_revise_project_director'

            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director revised the project to the expert", event_date=timezone.now(), tracing_project=obj_supervisor.client_form.formclint)
        else:
            create_obj_tracing = Tracing.objects.create(
                position='Director', user=request.user, status="The director revised the project to the expert", event_date=timezone.now(), tracing_supervisor=obj_supervisor)

        obj_supervisor.save()
        obj_supervisor.client_form.save()
        obj_supervisor.client_form.formclint.save()

        messages.error(request,'The proposal has been revised to the expert.')
        return redirect("industry:industry-director")

    
#director see total score
class DirectorSeeTotalScore(LoginRequiredMixin, SecuritySpecialExpertReview, DetailView):
    template_name = 'industry/director/director-see-total-score.html'
    def get_object(self):
        global obj_supervisor
        pk = self.kwargs.get('pk')
        obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
        return obj_supervisor
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryReviewer.objects.filter(status='e', object_supervisor=obj_supervisor)
        return context
 
    
#director reject project
class DirectorRejectProjectSupervisor(LoginRequiredMixin, SecurityDirector, UpdateView):
    template_name = 'industry/director/director-reject-project-supervisor.html'
    model = IndustryExpertForSupervisor
    fields = ['status']
    success_url = reverse_lazy('industry:industry-director')



#------------Reject------------#

#detal reject
@login_required
def reject_detail(request, pk):
    template_name = 'industry/reject/reject-detail.html'
    reject = get_object_or_404(IndustryFormClient, pk=pk)

    if request.user.is_superuser or reject.user == request.user and reject.status == 'r' or request.user.researchrole.director == True:
        form = DeleteProjectUser(request.POST or None, )
        if form.is_valid():
            status = form.cleaned_data.get("status")   

            reject.status= 'd'
            reject.save()

            messages.error(request,'The project was deleted')
            return redirect("dashboard-page")

        context = {
            'object': reject,
            "form": form,
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


#------------Expert#------------#
#list experts
class ExpertProjectList(LoginRequiredMixin, SecurityExpert, ListView):
    template_name = 'industry/expert/expert-list.html'
    def get_queryset(self):
        return IndustryFormExpert.objects.filter(~Q(status="is_change"), status__in=['m', 'n'] ,expert=self.request.user).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['superuser_count_expert_priject_industry'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='n').count()

        # filter new project
        # new_project_count = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='accept-contract-by-director', expert=self.request.user,).count()
        new_project_count = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='n', expert=self.request.user,).count()
        new_project_main_count = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='m', client_form__expert=self.request.user).count()
        context['new_projects_count'] = new_project_count + new_project_main_count

        # suervisor's request
        context['request_supervisor'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=self.request.user, status__in=['view_projects', 'v', 'review'], ).order_by("-created")
        context['count_request_supervisor'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='a', main_supervisor=False, client_form__expert=self.request.user).order_by("-created").count()

        # revise
        context['count_revise_proposal'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='revise-proposal-to-expert', client_form__expert=self.request.user).order_by("-created").count() + IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_expert', expert=self.request.user).order_by("-created").count()

        # send project to supervisors
        context['send_project_to_supervisor'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='accept-contract-by-director', expert=self.request.user).order_by("-created")
        context['count_send_project_to_supervisor'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='accept-contract-by-director', expert=self.request.user).count()


        count_contract_supervisor = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status__in=['x', 'g', 'director_revise_contract'], client_form__expert=self.request.user).order_by("-created").count()
        count_contract_client = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status__in=['accept_project_pending_send_contarct_client', 'revise-contract-to-director', 'send-signed-contract', 'not-response-contract', 'revise-contract-by-director'], expert=self.request.user).order_by("-created").count()
        context['count_contract_cart'] = count_contract_supervisor + count_contract_client

        # request main superuser
        context['superuser_request_main_supervisor'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='m',).order_by("-created")
        context['request_main_supervisor'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='m', client_form__expert=self.request.user).order_by("-created")
        context['count__superuser_request_main__supervisor'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='m',).order_by("-created").count()
        context['count__request__main_supervisor'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='m', client_form__expert=self.request.user).order_by("-created").count()

        # reviewer projects
        reviewer_project_count = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status='expert_reviewer' ,expert=self.request.user).order_by("-created").count()
        count_request_reviewer = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='v', client_form__expert=self.request.user).order_by("-created").count()
        context['filter_evaluate_count'] = reviewer_project_count + count_request_reviewer
        

        # Report project
        context['superuser_report_projects_object'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='report',).order_by("-created")
        context['report_projects_object'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='report', client_form__expert=self.request.user).order_by("-created")
        context['count_superuser_report_projects_object'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='report',).order_by("-created").count()
        context['count_report_projects_object'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='report', client_form__expert=self.request.user).order_by("-created").count()
        context['badge_report'] = 0
        
        
        # Count specail cart
        count_speical_expert_main = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='special_expert', client_form__expert=self.request.user).count()
        count_speical_expert_review = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='special_expert_review', client_form__expert=self.request.user).count()
        count_speical_expert_create = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='special_expert_create_project', client_form__expert=self.request.user).count()
        count_speical_expert_a_or_r = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created").count()
        context['count_special_cart'] = count_speical_expert_main + count_speical_expert_review + count_speical_expert_create + count_speical_expert_a_or_r 

        #resubmition
        context['count_request_reviewer'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='resubmition', client_form__expert=self.request.user).count() + IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=self.request.user, formclint__status='resubmited_project', ).count()
        context['request_review'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=self.request.user, status__in=['review', 'view_projects', 'chek_score'], ).order_by("-created")

        # Not response proposal
        context['count_not_response_proposal'] = IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='not_response_proposal', client_form__expert=self.request.user).order_by("-created").count()
    

        context['under_process_list'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), 
        ~Q(formclint__status__in=["r", "rejected_by_expert", 'withdrew']), expert=self.request.user, formclint__project_created=False).order_by("-created")

        under_process_count= IndustryFormExpert.objects.filter(~Q(status="is_change"), 
            ~Q(formclint__status__in=["r", "rejected_by_expert", 'withdrew']), expert=self.request.user, formclint__project_created=False).count()


        context['history_not_created_list'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), 
        expert=self.request.user, formclint__project_created=False).order_by("-created")

        history_not_created_count= IndustryFormExpert.objects.filter(~Q(status="is_change"), 
            expert=self.request.user, formclint__project_created=False).count()


        context['history_created_list'] = ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), 
            project__client_form__expert=self.request.user, 
            project__client_form__formclint__project_created=True).order_by("-created")

        history_created_count = ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), 
            project__client_form__expert=self.request.user, 
            project__client_form__formclint__project_created=True).order_by("-created").count()

        context['history_list_count'] = history_created_count + history_not_created_count
        context['under_process_count'] = under_process_count

        # Withdrew
        context['projejct_withdrew'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status='withdrew')
        context['projejct_withdrew_count'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status='withdrew').count()
 

        # Withdrew
        context['projejct_withdrew'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status='withdrew')

        # Change expert
        context['projejct_change_expert'] = IndustryFormExpert.objects.filter(status="is_change", expert=self.request.user)

        return context


def expert_filter_resubmition(request):
    template_name = "industry/expert/expert-filter-resubmition.html"

    context = {

        'projects_resubmition': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=request.user, formclint__status='resubmited_project',).order_by("-created"),
        'projects_resubmition_count': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=request.user, formclint__status='resubmited_project',).count(),

        'request_review': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=request.user, status__in=['review', 'view_projects', 'chek_score'], ).order_by("-created"),
        'count_request_reviewer': IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='resubmition', client_form__expert=request.user).order_by("-created").count(),

    }
    return render(request, template_name, context)


def expert_filter_revise(request):
    template_name = "industry/expert/expert-filter-revise.html"


    context = {
        'request_supervisor': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=request.user, status__in=['view_projects', 'v', 'review'], ).order_by("-created"),
        'count_revise_proposal': IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status='revise-proposal-to-expert', client_form__expert=request.user).order_by("-created").count(),

        'revise_projects' : IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_expert', expert=request.user).order_by("-created"),
        'count_revise_projects': IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_expert', expert=request.user).order_by("-created").count(),
    }
    return render(request, template_name, context)

def expert_filter_contract(request):
    template_name = "industry/expert/expert-filter-contract.html"

    context = {
        'count_client_contract' : IndustryFormExpert.objects.filter(~Q(status="is_change"), formclint__status__in=['accept_project_pending_send_contarct_client', 'revise-contract-to-director', 'send-signed-contract', 'not-response-contract', 'revise-contract-by-director'], expert=request.user).order_by("-created").count(),
        'count_supervisor_contract': IndustryExpertForSupervisor.objects.filter(~Q(client_form__status="is_change"), status__in=['x', 'g', 'director_revise_contract'], client_form__expert=request.user).order_by("-created").count(),
    }
    return render(request, template_name, context)


# filter new project
def expert_filter_newproject(request):
    if request.user.is_superuser or request.user.researchrole.director == True or \
    request.user.researchrole.expert == True :
        template_name = 'industry/expert/expert-filter-newproject.html'

        context = {
            # 'new_projects': IndustryFormExpert.objects.filter(status='accept-contract-by-director' ,expert=request.user).order_by("-created"),
            # 'new_projects_count': IndustryFormExpert.objects.filter(status='accept-contract-by-director', expert=request.user,).count(),
            'new_projects': IndustryFormExpert.objects.filter(status='n' ,expert=request.user).order_by("-created"),
            'new_projects_count': IndustryFormExpert.objects.filter(status='n', expert=request.user,).count(),

            'new_project_main': IndustryExpertForSupervisor.objects.filter(status='m', client_form__expert=request.user).order_by("-created"),
            'new_project_main_count': IndustryExpertForSupervisor.objects.filter(status='m', client_form__expert=request.user).order_by("-created").count(),
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")
    




def revised_proposal(request):
    if request.method == 'POST':
        reason_reject = request.POST.get('reason_reject')
        id_supervisor = int(request.POST.get('id_supervisor'))

        obejct_supervisor = IndustryExpertForSupervisor.objects.get(id=id_supervisor)
        status_obj = obejct_supervisor.status
        obejct_supervisor.status= 'b'
        obejct_supervisor.deadline = timezone.now() + timedelta(2)
        obejct_supervisor.rejected_date= timezone.now()
        obejct_supervisor.reason_reject = reason_reject
        obejct_supervisor.follow_project = 'reject_by_expert'
        if status_obj == 'd':
            if obejct_supervisor.client_form.formclint.main_supervisor:
                obejct_supervisor.client_form.formclint.follow_project = 'p_main_revise_proposal_by_director'
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the proposal to the supervisor ", event_date=timezone.now(), tracing_project=obejct_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Director', user=request.user, status="The director revised the proposal to the supervisor ", event_date=timezone.now(), tracing_supervisor=obejct_supervisor)
        else:

            if obejct_supervisor.client_form.formclint.main_supervisor:
                obejct_supervisor.client_form.formclint.follow_project = 'p_main_revise_proposal_by_expert'
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert revised the proposal", event_date=timezone.now(), tracing_project=obejct_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert revised the proposal", event_date=timezone.now(), tracing_supervisor=obejct_supervisor)

        obejct_supervisor.client_form.formclint.save()
        obejct_supervisor.save()



        reviewers = IndustryReviewer.objects.filter(object_supervisor=obejct_supervisor, status__in=['n', 'a'])
        for i in reviewers:
            i.status = 'automatically_cancel'
            i.event_date = timezone.now()
            i.save()

            if i.object_supervisor.client_form.formclint.main_supervisor :
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=i.reviewer, status="The proposal review request was automatically canceled", event_date=timezone.now(), tracing_project=i.object_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=i.reviewer, status="The proposal review request was automatically canceled", event_date=timezone.now(), tracing_supervisor=i.object_supervisor)

            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=i.reviewer, status="The proposal was automatically canceled", event_date=timezone.now(), tracing_reviewer=i)

    

        Notification(title='Project (ID: {})'.format(obejct_supervisor.client_form.formclint.id_project),
        description='There is a revision for your proposal. You are strongly recommend to resubmit your proposal according to the comments by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(obejct_supervisor.deadline.strftime('%Y/%m/%d %H:%M')), target=obejct_supervisor.supervisor,
        link='').save()
        
        e_subject ="TECVICO Project (Project ID: {})".format(obejct_supervisor.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYour proposal needs a revision. You are strongly recommend to resubmit your proposal according to the comments by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obejct_supervisor.supervisor.get_full_name(), obejct_supervisor.deadline.strftime('%Y/%m/%d %H:%M'), obejct_supervisor.client_form.expert.researchrole.expert_email_address)
        e_destination = obejct_supervisor.supervisor.email
        send_new_email(e_subject,e_content,e_destination)
        
        
        messages.error(request,'The proposal has been revised to the supervisor.')
        if status_obj == 'd':
            return redirect("industry:industry-director")
        else:
            return redirect("industry:industry-expert-list")






# filter evaluate
def expert_filter_evaluate(request):
    if request.user.is_superuser or request.user.researchrole.director == True or \
    request.user.researchrole.expert == True :
        template_name = 'industry/expert/expert-filter-evaluate.html'

        context = {
            'reviewer_project_count': IndustryFormExpert.objects.filter(status='review_project' ,expert=request.user).order_by("-created").count(),
            'count_request_reviewer': IndustryExpertForSupervisor.objects.filter(status='v', client_form__expert=request.user).order_by("-created").count(),
            'request_review': IndustryFormExpert.objects.filter(expert=request.user, status__in=['review', 'view_projects', 'chek_score'], ).order_by("-created"),
            'reviewer_project': IndustryFormExpert.objects.filter(status='review_project' ,expert=request.user).order_by("-created"),


        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")
        
def revise_filter_applicant(request):
    template_name = 'industry/project/revised_page_filter.html'
    context = {}
    context['revised_proposal_list'] = IndustryExpertForSupervisor.objects.filter(status='b', supervisor=request.user).order_by("-created")
    context['revised_project_list'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_client').order_by("-created")
    context['revised_proposal_count'] = IndustryExpertForSupervisor.objects.filter(status='b', supervisor=request.user).count()
    context['revised_project_count'] = IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_client').count()
    return render(request, template_name, context)
        
def rejected_filter_applicant(request):
    template_name = 'industry/project/rejected_page_filter.html'
    context = {}
    context['rejected_project_list'] = IndustryFormClient.objects.filter(status='r', user=request.user).order_by("-created")
    context['rejected_project_count'] = IndustryFormClient.objects.filter(status='r', user=request.user).order_by("-created").count()
    context['rejected_proposal_list'] = IndustryExpertForSupervisor.objects.filter(status='h', supervisor=request.user).order_by("-created")
    context['rejected_proposal_count'] = IndustryExpertForSupervisor.objects.filter(status='h', supervisor=request.user).count()
    return render(request, template_name, context)
    
# History expert detail
@login_required
def expert_history_notcreated_detail(request, pk):
    template_name = 'industry/expert/expert-history-notcreated-detail.html'
    obj_expert = get_object_or_404(IndustryFormExpert, pk=pk)

    if request.user.is_superuser or request.user.researchrole.expert == True and obj_expert.expert == request.user or \
        request.user.researchrole.director == True :

        if request.method == 'POST':
            deadline = request.POST.get("deadline")
            obj_expert.deadline = deadline
            obj_expert.save()
            
            supervisors_email = IndustryExpertForSupervisor.objects.filter(client_form=obj_expert, status='u')
            for i in supervisors_email:
                e_subject ="TECVICO project (Project ID: {})".format(obj_expert.formclint.id_project)
                e_content = "Dear {} \nHello\nHope you are going well.\n Good news for TECVICO supervisors!\n\n The deadline of submitting the proposal has been extended by {} (Coordinated Universal Time (UTC)).\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you.\n Best regards\n TECVICO CORP".format(i.supervisor.get_full_name(), obj_expert.deadline, obj_expert.expert.researchrole.expert_email_address)
                e_destination = i.supervisor.email
                send_new_email(e_subject,e_content,e_destination)
                
                

                Notification(title='Project (ID: {})'.format(obj_expert.formclint.id_project), 
                    description='The deadline of submitting the proposal has been extended by {} (Coordinated Universal Time (UTC)).'.format(obj_expert.deadline), 
                    target=i.supervisor, 
                    link='notification-page').save()

            return redirect('industry:research-expert-history-detail', obj_expert.pk)

        context = {
            'object': obj_expert,
            'supervisors': IndustryExpertForSupervisor.objects.filter(~Q(status__in=["u", "not-pay"]), client_form_id=pk),
            'to_day': date.today(),
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")
    


@login_required
def expert_history_created_detail(request, pk):
    template_name = 'industry/expert/expert-history-created-detail.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)
    count = 0

    count_meesage_applicant = ApplicantComment.objects.filter(position='send_to_expert', seen=False, project__project__client_form__expert=request.user).count()

    for i in ApplicantComment.objects.filter(position='send-to-applicant'):
        for e in i.comments.filter(seen=False):
            if i.project.project.client_form.expert == request.user:
                count += 1
    applicant_comment_count = count_meesage_applicant + count

    if request.method == 'POST':
        change_status = request.POST.get("change_status")
        applicant_contract = request.POST.get("applicant_contract")

        return redirect('industry:project-expert-history-created-detail', project_obj.pk)

    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user, sub=project_obj.project)

    context = {
        'today': date.today(),
        'wbs_list': wbs_list,
        'project_obj': project_obj,
        'applicant_comment_count': applicant_comment_count,
    }
    return render(request, template_name, context)

class ExpertSendOrChekContract(LoginRequiredMixin, SecurityExpert, ListView):
    template_name = 'industry/expert/expert-list-contract.html'
    def get_queryset(self):
        if self.request.user.is_superuser:
            return IndustryExpertForSupervisor.objects.filter(status='x', ).order_by("-created")
        else:
            return IndustryExpertForSupervisor.objects.filter(status='x', client_form__expert=self.request.user).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chek_send_contract_for_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='g', client_form__expert=self.request.user).order_by("-created")
        context['count_chek_send_contract_for_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='g', client_form__expert=self.request.user).order_by("-created").count()

        context['revised_contract_list'] = IndustryExpertForSupervisor.objects.filter(status='director_revise_contract', client_form__expert=self.request.user).order_by("-created")
        context['revised_contract_count'] = IndustryExpertForSupervisor.objects.filter(status='director_revise_contract', client_form__expert=self.request.user).order_by("-created").count()

        context['count_send_send_contract_for_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='x', client_form__expert=self.request.user).order_by("-created").count()
        return context



def expert_list_contract_client(request):
    template_name = 'industry/expert/expert-list-contract-client.html'


    context = {
        'new_contract_list': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='accept_project_pending_send_contarct_client', status='accept_project_pending_send_contarct_client'),
        'new_contract_list_count': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='accept_project_pending_send_contarct_client', status='accept_project_pending_send_contarct_client').count(),

        'signed_contract_list': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='send-signed-contract'),
        'signed_contract_list_count': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='send-signed-contract').count(),

        'revised_contract_list': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='revise-contract-by-director'),
        'revised_contract_list_count': IndustryFormExpert.objects.filter(expert=request.user, formclint__status='revise-contract-by-director').count(),
    }
    return render(request, template_name, context)



class SpecialExpertPanel(LoginRequiredMixin, SecurityExpert, ListView):
    template_name = 'industry/expert/special/expert-special-panel.html'
    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            return IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,).order_by("-created")
        else:
            return IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # accept or reject
        
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            accept_reject_project_count_ = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,).order_by("-created").count()
            project_reviewer = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,).order_by("-created").count()
            accept_or_reject_main_supervisor_count = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,).order_by("-created").count()
        else:
            accept_reject_project_count_ = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created").count()
            project_reviewer = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created").count()
            accept_or_reject_main_supervisor_count = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,client_form__expert=self.request.user).order_by("-created").count()
        context['accept_reject_project_count'] = accept_reject_project_count_ + accept_or_reject_main_supervisor_count + project_reviewer
        
        # review scores
        context['special_expert_see_review'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_review' ,client_form__expert=self.request.user).order_by("-created")
        context['superuser_special_expert_see_review'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_review').order_by("-created")
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            context['special_expert_see_review_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_review' ,).order_by("-created").count()
        else:
            context['special_expert_see_review_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_review' ,client_form__expert=self.request.user).order_by("-created").count()

        # create project
        context['special_expert_create_project'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_create_project' ,client_form__expert=self.request.user).order_by("-created")
        context['superuser_special_expert_create_project'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_create_project').order_by("-created")
        
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            context['special_expert_create_project_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_create_project' ,).order_by("-created").count()
        else:
            context['special_expert_create_project_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert_create_project' ,client_form__expert=self.request.user).order_by("-created").count()
        return context
        

class ExpertReviseList(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/expert/expert-list-revise.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['revise_list'] = IndustryExpertForSupervisor.objects.filter(status='revise-proposal-to-expert', client_form_id=pk)
        return context
        

@login_required
def expert_review_project_detail(request, pk):
    obj_expert = get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)

    if request.method == 'POST':
        value = request.POST.get('value')
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        status_value = request.POST.get('status_value')

        if status == 'send-to-the-director':

            if obj_expert.formclint.status == 'resubmited_project':
                obj_expert.status = 'resubmited_project_send_to_director'
                obj_expert.formclint.status = 'resubmited_project_send_to_director'
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert sent the resubmitted proposal to the director", event_date=timezone.now(), tracing_project=obj_expert.formclint)

            else:
                obj_expert.status = 'expert_send_scores_to_director'
                obj_expert.formclint.status = 'expert_send_scores_to_director'
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert sent the project evaluation to the director", event_date=timezone.now(), tracing_project=obj_expert.formclint)


            obj_expert.description_forum = comment
            obj_expert.status_value = status_value
            obj_expert.valeu = value

            obj_expert.save()
            obj_expert.formclint.save()


            for i in ResearchRole.objects.filter(director=True):
                e_subject ="TECVICO Project (Project ID: {})".format(obj_expert.formclint.id_project)  
                e_content ="Dear {} \nHello\nHope you are going well. \nThe expert {} has investigated the material of the request for the project. \nThe comment(s) are listed as follows: {} \nFor more information, please go to your dashboard and look at the comment(s) and finalize the request.  \n\nThank you \nBest regards \nTECVICO Corp.".format( i.user.get_full_name(), obj_expert.expert.get_full_name(), comment, )
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)
                    
                
                Notification(title='Project (ID: {})'.format(obj_expert.formclint.id_project), 
                    description='The expert {} has investigated the material of the request for the project. For more information, go to your dashboard.'.format(obj_expert.expert.get_full_name(),), target=i.user, 
                    link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()

            for i in obj_expert.object_experts.filter(status__in=['revise_by_expert_p', 'accept_project', 'new_project']):
                i.status = 'automatically_cancel_p'
                i.event_date = timezone.now()
                i.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=i.reviewer, status="The project review request was automatically canceled", event_date=timezone.now(), tracing_project=obj_expert.formclint)

                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=i.reviewer, status="The project review request was automatically canceled", event_date=timezone.now(), tracing_reviewer=i)
                
                
                Notification(title='Project (ID: {})'.format(obj_expert.formclint.id_project), 
                    description='The review request was canceled automatically. For more information, go to your dashboard.', target=i.reviewer, 
                    link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()
                
                    
                e_subject ="TECVICO Project (Project ID: {})".format(obj_expert.formclint.id_project, )
                e_content ="Dear {}\nHello\nHope you are going well.\nThe review request was canceled automatically. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(i.reviewer.get_full_name(), obj_expert.expert.researchrole.expert_email_address)
                e_destination = i.reviewer.email
                send_new_email(e_subject,e_content,e_destination)


            messages.success(request,'The project assessment has been sent to the director successfully.')
        return redirect('industry:industry-expert-list')

    context = {
        'reviewers': obj_expert.object_experts.filter(status__in=['new_project', 'reject_project', 'accept_project', 'not_see_project', 'send_director_project', 'revise_by_expert_p', 'cancel_by_expert_p', 'automatically_cancel_p']),
        'object': obj_expert,
    }
    return render(request, 'industry/expert/expert-review-project-detail.html', context)
        
        


@login_required
def view_add_time_programming(request, pk):
    form_client = IndustryExpertForSupervisor.objects.get(pk=pk)
    if request.user.is_superuser or request.user.memberprofile.position == 'Supervisor' and  form_client.supervisor == request.user \
        or request.user.researchrole.director == True:


        form_report = SendRepoertByMainSupervisorForm(request.POST, )
        if form_report.is_valid():

            id_pr = form_report.cleaned_data.get("id_pr")
            status = form_report.cleaned_data.get("status")
            report = form_report.cleaned_data.get("report")

            report_main_supervisor = get_object_or_404(TimeProgramming, id=id_pr)
            report_main_supervisor.report = report
            report_main_supervisor.status = 'end_of_report'
            report_main_supervisor.save()

            report_main_supervisor.sub.status = 'report'
            report_main_supervisor.sub.save()
            
            # report for time programing

            for i in form_client.projects.all():
                create_obj_tracing = Tracing.objects.create(
                    position='Main supervisor', user=request.user, status="The Supervisor sent her/his report", event_date=timezone.now(), tracing_project_phase_2=i)

            # e_subject = ""
            # e_content = ""
            # e_destination = report_main_supervisor.sub.client_form.expert.researchrole.expert_email_address
            # send_new_email(e_subject,e_content,e_destination)

            return redirect('industry:industry-view-add-time-programming', report_main_supervisor.sub.pk)


        form = FormTimeProgramming(request.POST or None,    )
        if form.is_valid():
            topic = form.cleaned_data.get("topic")
            start_date = form.cleaned_data.get("start_date")
            end_date = form.cleaned_data.get("end_date")

            TimeProgramming.objects.create(sub=form_client, topic=topic, start_date=start_date, end_date=end_date)
        context = {
            "form": form,
            'form_report': form_report,
            "prog": form_client.time_programmins.all(),
            "form_client": form_client,
            'date_today': date.today()
        }

        return render(request, 'industry/project/view-addtime-programming.html', context)
    else:
        raise Http404("You can't see this page.")
        

@login_required
def expert_send_to_reviewer(request, **kwargs):
    template_name = 'industry/expert/special/expert-send-reviewer.html'
    form_id = kwargs["form_id"]
    form_client = IndustryFormExpert.objects.get(~Q(status="is_change"), id=form_id)
    if request.user == form_client.expert :
        users = User.objects.filter(researchrole__reviewer= True)
        form = Reviewer(request.POST or None,)
        if form.is_valid():
            form_id = form.cleaned_data.get("form_id")
            status = form.cleaned_data.get("status")
            user_list = form.cleaned_data.get("user_list")
            user_list = user_list.split(",")
            
            form_client.formclint.status = 'expert_reviewer'
            form_client.formclint.save()

            form_client.status = 'review_project'
            form_client.save()
            for user in user_list:
                user = int(user)
                user = User.objects.get(id=user)
                deadline = timezone.now() + timedelta(2)
                email_7_day = timezone.now() + timedelta(7)
                new_reject = IndustryReviewer.objects.create(object_expert_id=form_client.id, reviewer=user, status='new_project', deadline=deadline)
                
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status=" The expert sent the project review request to the reviewer", event_date=timezone.now(), tracing_project=form_client.formclint)

                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert sent the project review request to the reviewer", event_date=timezone.now(), tracing_reviewer=new_reject)
                
                
                
                e_subject ="TECVICO Project (Project ID: {})".format(form_client.formclint.id_project, )  
                e_content ="Dear {} \nHello\nHope you are going well. \nYou have been invited to review this project. The evaluation form and full information of the project will be available on your dashboard. The reviewer should notify her/his assent to the company to review the project by {} (Coordinated Universal Time (UTC)). The system will remove the reviewer if confirmation is not recorded automatically. Furthermore, the deadline of review will be 1 week after the request on {}. \nTitle «{}» \nFund «${}» \nAbstract «{}» \nIf you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you\nSincerely\nTECVICO Corp.".format(user.get_full_name(), new_reject.deadline.strftime('%Y/%m/%d %H:%M'), email_7_day.strftime('%Y/%m/%d %H:%M'), form_client.formclint.title, form_client.formclint.fund, form_client.formclint.abstrack, form_client.expert.researchrole.expert_email_address)
                e_destination = user.email
                send_new_email(e_subject,e_content,e_destination)
                
                
            
            messages.success(request,'The project has been sent to the reviewer successfully.')
            return redirect("industry:research-access-expert-detail", form_client.pk)

        context = {
            "form" : form,
            "form_client": form_client,
            "users": users,
            "history_reviewer_accept": IndustryReviewer.objects.filter(status='e'),
            "history_reviewer_reject": IndustryReviewer.objects.filter(status__in=['r', ]),
            "history_reviewer_accept_count": IndustryReviewer.objects.filter(status='e').count(),
            "history_reviewer_reject_count": IndustryReviewer.objects.filter(status__in=['r', ]).count(),
        }
        
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


#detail list supervisor
class ExpertListSupervisor(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/expert/expert-list-supervisor.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['request_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='a', client_form_id=pk)
        return context

#detail list review
class ExpertListResubmition(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/expert/expert-list-resubmition.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryExpertForSupervisor.objects.filter(status='resubmition', client_form_id=pk)
        return context

class ExpertListReviewer(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/expert/expert-list-review.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryExpertForSupervisor.objects.filter(status='v', client_form_id=pk)
        return context


@login_required
def expert_view_table_timeprogramming(request, pk):
    form_client = IndustryExpertForSupervisor.objects.get(pk=pk)
    context = {
        "prog": form_client.time_programmins.all(),
        "form_client": form_client,
    }
    return render(request, 'industry/expert/expert-view-table-timeprogramming.html', context)

#detail review for expert
@login_required
def expert_review_detail(request, pk):
    template_name = 'industry/expert/expert-reviewer-detail.html'
    expert_review = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    roles = ResearchRole.objects.all() 
    user_role = ResearchRole.objects.filter(user=request.user).count()
    
    if user_role != 0 and expert_review.status == 'resubmition' or expert_review.status == 'revise-proposal-to-expert' or expert_review.status == 'v' and request.user.researchrole.expert == True and expert_review.client_form.expert == request.user:

        reviewer = IndustryReviewer.objects.filter(object_supervisor=expert_review)
        reviewer_count_expert = IndustryReviewer.objects.filter(status='e',object_supervisor=expert_review).count()
        reviewer_count = IndustryReviewer.objects.filter(status='a',object_supervisor=expert_review).count()
        # reviewers = IndustryReviewer.objects.filter(status__in=['n', 'r', 'a'], object_supervisor=expert_review)

        form_comment = SendScoreForDirector(request.POST,  request.FILES, initial={"status": expert_review.status, "text": expert_review.text})
        if form_comment.is_valid():
            text = form_comment.cleaned_data.get("text")
            value = form_comment.cleaned_data.get("value")
            status = form_comment.cleaned_data.get("status")
            status_value = form_comment.cleaned_data.get("status_value")

            if expert_review.client_form.formclint.main_supervisor:
                expert_review.client_form.formclint.follow_project = 'check_score'
                if expert_review.status == 'revise-proposal-to-expert':
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=expert_review.client_form.expert, status="The expert sent the resubmitted proposal to the director", event_date=timezone.now(), tracing_project=expert_review.client_form.formclint)

                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=expert_review.client_form.expert, status="The expert sent the resubmitted proposal to the director", event_date=timezone.now(), tracing_project=expert_review.client_form.formclint)
                
            else:
                if expert_review.status == 'revise-proposal-to-expert':
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=expert_review.client_form.expert, status="The expert sent the resubmitted proposal to the director", event_date=timezone.now(), tracing_supervisor=expert_review)

                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=expert_review.client_form.expert, status="The expert sent the resubmitted proposal to the director", event_date=timezone.now(), tracing_supervisor=expert_review)


            expert_review.status = status
            expert_review.follow_project = 'send_to_director'
            expert_review.client_form.status_value = status_value
            expert_review.client_form.valeu = value
            expert_review.client_form.status = 'chek_score'
            expert_review.text = text

            # if expert_review.client_form.directo_see_reviewer == False:
            #     expert_review.client_form.formclint.follow_project = 'p_main_send_proposal_director'

            expert_review.client_form.formclint.save()

            expert_review.client_form.save()
            expert_review.save()


            reviewers = IndustryReviewer.objects.filter(object_supervisor=expert_review, status__in=['n', 'a'])
            for i in reviewers:
                i.status = 'automatically_cancel'
                i.event_date = timezone.now()
                i.save()

                if i.object_supervisor.client_form.formclint.main_supervisor :
                    create_obj_tracing = Tracing.objects.create(
                        position='Reviewer', user=i.reviewer, status="The proposal review request was automatically canceled", event_date=timezone.now(), tracing_project=i.object_supervisor.client_form.formclint)

                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=i.reviewer, status="The proposal review request was automatically canceled", event_date=timezone.now(), tracing_reviewer=i)
                
                
                Notification(title='Project (ID: {})'.format(i.object_supervisor.client_form.formclint.id_project), 
                    description='The review request was canceled automatically. For more information, go to your dashboard.', target=i.reviewer, 
                    link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()
                
                    
                e_subject ="TECVICO Project (Project ID: {})".format(i.object_supervisor.client_form.formclint.id_project, )
                e_content ="Dear {}\nHello\nHope you are going well.\nThe review request was canceled automatically. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(i.reviewer.get_full_name(), i.object_supervisor.client_form.expert.researchrole.expert_email_address)
                e_destination = i.reviewer.email
                send_new_email(e_subject,e_content,e_destination)


            for i in roles:
                if i.director == True:
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(expert_review.client_form.formclint.id_project)  
                    e_content ="Dear {} \nHello\nHope you are going well. \nThe expert {} has investigated the material of the request for the proposal. \nThe comment(s) are listed as follows: {} \nFor more information, please go to your dashboard and look at the comment(s) and finalize the request. \n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format( i.user.get_full_name(), expert_review.client_form.expert.get_full_name(), expert_review.text, expert_review.client_form.expert.researchrole.expert_email_address)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)
                    
            messages.success(request,'The proposal assessment has been sent to the director successfully.')
            return redirect('industry:industry-expert-list')


        context = {
        'reviewer': reviewer,
        'object': expert_review,
        'form_comment': form_comment,
        'reviewer_count': reviewer_count,
        'reviewer_count_expert': reviewer_count_expert,
        "users": User.objects.filter(researchrole__reviewer= True)
        }

        return render(request, template_name, context)
    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-expert-list')

def expert_send_reviewer(request):
    if request.method == 'POST':
        obj_id = int(request.POST.get("obj_id"))
        reviewer_id = int(request.POST.get("reviewer_id"))

        supervisor_obj = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
        

        user_list = form.cleaned_data.get("user_list")
        user_list = user_list.split(",")
        supervisor_obj.follow_project = 'send_to_reviewer'
        supervisor_obj.status = 'v'
        supervisor_obj.status_review = 'Pending for reviewerʼs approval'
        supervisor_obj.client_form.status = 'review'
        supervisor_obj.client_form.formclint.follow_project = 'p_main_send_review'
        supervisor_obj.client_form.formclint.save()
        supervisor_obj.client_form.save()
        supervisor_obj.save()

        for user in user_list:
            user = int(user)
            user = User.objects.get(id=user)
            deadline = timezone.now() + timedelta(2)
            new_reject = IndustryReviewer.objects.create(object_supervisor_id=supervisor_obj.id, reviewer=user, deadline=deadline)
            
            email_2_day = date.today() + timedelta(2)
            email_7_day = date.today() + timedelta(7)
            
            
            e_subject ="TECVICO Project (Project ID: {})".format(supervisor_obj.client_form.formclint.id_project, )  
            e_content ="Dear {} \nHello\nHope you are going well. \nYou have been invited to review this proposal.The evaluation form and full information of the proposal will be available on your dashboard.The reviewer should notify her/his assent to the company to review the proposal by {} (Coordinated Universal Time (UTC)). The system will remove the reviewer if confirmation is not recorded automatically. Furthermore, the deadline of review will be 1 week after the request on {} of final deadline. \nTitle «{}» \nFund «${}» \nAbstract «{}» \nIf you have any questions or concerns, please feel free to contact the expert through {} \n\nThank you\nSincerely\nTECVICO Corp.".format(user.get_full_name(), email_2_day, email_7_day, supervisor_obj.client_form.formclint.title, supervisor_obj.client_form.formclint.fund, supervisor_obj.client_form.formclint.abstrack, supervisor_obj.client_form.expert.researchrole.expert_email_address)
            e_destination = user.email
            send_new_email(e_subject,e_content,e_destination)
            
            
            
        messages.success(request,'The proposal has been sent to the reviewer(s) successfully.')
        return redirect("industry:industry-expert-list")




def cancel_request_reviewer(request):
    position = request.POST.get("position")
    model = request.POST.get("model")
    id_obj = int(request.POST.get("id_obj"))
    id_review = int(request.POST.get("id_review"))

    obj_review = IndustryReviewer.objects.get(id=id_review)
 
    if model == 'project-supervisor':
        obj_review.status = 'cancel_by_expert'
    else:
        obj_review.status = 'cancel_by_expert_p'
    obj_review.event_date = timezone.now()

    obj_review.save()

    messages.error(request,'The request was canceled.')



                
    if model == 'project-supervisor':
        Notification(title='Research (ID: {})'.format(obj_review.object_supervisor.client_form.formclint.id_project), 
            description='The review request has been canceled. For more information, go to your dashboard.', target=obj_review.reviewer, 
            link=reverse('industry:industry-reviewer-detail', args=[obj_review.pk])).save()
            
            
        e_subject ="TECVICO Project (Project ID: {})".format(obj_review.object_supervisor.client_form.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nThe review request has been canceled. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_review.reviewer.get_full_name())
        e_destination = obj_review.reviewer.email
        send_new_email(e_subject,e_content,e_destination)

    elif model == 'project-expert':
        Notification(title='Research (ID: {})'.format(obj_review.object_expert.formclint.id_project), 
            description='The review request has been canceled. For more information, go to your dashboard.', target=obj_review.reviewer, 
            link=reverse('industry:industry-reviewer-detail', args=[obj_review.pk])).save()
            
            
        e_subject ="TECVICO Project (Project ID: {})".format(obj_review.object_expert.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nThe review request has been canceled. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_review.reviewer.get_full_name())
        e_destination = obj_review.reviewer.email
        send_new_email(e_subject,e_content,e_destination)


    if model == 'project-supervisor':
        if obj_review.object_supervisor.client_form.formclint.main_supervisor :
            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert canceled the proposal review request", event_date=timezone.now(), tracing_project=obj_review.object_supervisor.client_form.formclint)
        else:
            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert canceled the proposal review request", event_date=timezone.now(), tracing_supervisor=obj_review.object_supervisor)


        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=obj_review.object_supervisor.client_form.expert, status="The expert canceled the proposal review request", event_date=timezone.now(), tracing_reviewer=obj_review)

        obj_supervisor = IndustryExpertForSupervisor.objects.get(id=id_obj)
        return redirect('industry:industry-expert-reviewer-detail', obj_supervisor.pk)

    elif model == 'project-expert':
        obj_expert = IndustryFormExpert.objects.get(~Q(status="is_change"), id=id_obj)
        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=request.user, status="The expert canceled the project review request", event_date=timezone.now(), tracing_project=obj_review.object_expert.formclint)
            
        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=request.user, status="The expert canceled the project review request", event_date=timezone.now(), tracing_reviewer=obj_review)
            

        return redirect('industry:research-access-expert-detail', obj_expert.pk)

def revise_request_reviewer(request):
    position = request.POST.get("position")
    model = request.POST.get("model")
    id_obj = int(request.POST.get("id_obj"))
    id_review = int(request.POST.get("id_review"))
    reason = request.POST.get("reason")

    obj_review = IndustryReviewer.objects.get(id=id_review)
 
    if position == 'expert':
        if model == 'project-supervisor':
            obj_review.status = 'revise_by_expert'
        else:
            obj_review.status = 'revise_by_expert_p'


    deadline = timezone.now() + timedelta(3)
    obj_review.deadline = deadline
    obj_review.text = reason
    obj_review.save()
              
    messages.error(request,'You have revised the assessment.')

    if model == 'project-supervisor':
        Notification(title='Research (ID: {})'.format(obj_review.object_supervisor.client_form.formclint.id_project), 
            description='There is a revision for your assessment. You are strongly recommended to re-submit the assessment by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(obj_review.deadline.strftime('%Y/%m/%d %H:%M')), target=obj_review.reviewer, 
            link=reverse('industry:industry-reviewer-detail', args=[obj_review.pk])).save()
            
            
        e_subject ="TECVICO Project (Project ID: {})".format(obj_review.object_supervisor.client_form.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nYour assessment needs a revision. You are strongly recommended to re-send the assessment by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_review.reviewer.get_full_name(), obj_review.deadline.strftime('%Y/%m/%d %H:%M'), obj_review.object_supervisor.client_form.expert.researchrole.expert_email_address)
        e_destination = obj_review.reviewer.email
        send_new_email(e_subject,e_content,e_destination)

        if obj_review.object_supervisor.client_form.formclint.main_supervisor :
            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=obj_review.object_supervisor.client_form.expert, status="The expert revised the proposal evaluation", event_date=timezone.now(), tracing_project=obj_review.object_supervisor.client_form.formclint)
        else:
            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=obj_review.object_supervisor.client_form.expert, status="The expert revised the proposal evaluation", event_date=timezone.now(), tracing_supervisor=obj_review.object_supervisor)

        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=obj_review.object_supervisor.client_form.expert, status="The expert revised the proposal evaluation", event_date=timezone.now(), tracing_reviewer=obj_review)

        return redirect('industry:industry-expert-reviewer-detail', obj_review.object_supervisor.pk)

    elif model == 'project-expert':
        Notification(title='Research (ID: {})'.format(obj_review.object_expert.formclint.id_project), 
            description='There is a revision for your assessment. You are strongly recommended to re-submit the assessment by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(obj_review.deadline.strftime('%Y/%m/%d %H:%M')), target=obj_review.reviewer, 
            link=reverse('industry:industry-reviewer-detail', args=[obj_review.pk])).save()
            
            
        e_subject ="TECVICO Project (Project ID: {})".format(obj_review.object_expert.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nYour assessment needs a revision. You are strongly recommended to re-send the assessment by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_review.reviewer.get_full_name(), obj_review.deadline.strftime('%Y/%m/%d %H:%M'), obj_review.object_expert.expert.researchrole.expert_email_address)
        e_destination = obj_review.reviewer.email
        send_new_email(e_subject,e_content,e_destination)


        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=request.user, status="The expert revised the project evaluation", event_date=timezone.now(), tracing_project=obj_review.object_expert.formclint)
            
        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=request.user, status="The expert revised the project evaluation", event_date=timezone.now(), tracing_reviewer=obj_review)
            
        return redirect('industry:research-access-expert-detail', obj_review.object_expert.pk)


# # detail total score
# class ExpertSeeTotalScore(LoginRequiredMixin, SecurityExpertSub, DetailView):
#     template_name = 'industry/expert/expert-reviewer-total-score.html'
#     def get_object(self):
#         global pk
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(IndustryExpertForSupervisor, pk=pk)
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['reviewer'] = IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk)
#         return context

def expert_see_totoal_score(request, pk):
    template_name = 'industry/expert/expert-reviewer-total-score.html'
    obj_superivsor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    if obj_superivsor.status == 'resubmition' or obj_superivsor.status == 'revise-proposal-to-expert' or obj_superivsor.status == 'v' and request.user.researchrole.expert == True and obj_superivsor.client_form.expert == request.user:

        context = {
            'object': obj_superivsor,
            'reviewer': IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk),
        }

        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


@login_required
def expert_detail(request, pk):
    form_client = get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    if request.user.is_superuser or request.user.researchrole.expert == True and form_client.expert == request.user or \
        request.user.researchrole.director == True :
        users = User.objects.filter(memberprofile__position='Supervisor')

        form = ExpertSendSupervisor(request.POST or None, )
        if form.is_valid():
            form_id = form.cleaned_data.get("form_id")
            deadline = form.cleaned_data.get("deadline")

            total = 5000

            supervisor_share = 50 / 100
            supervisor_importance_value = 100
            money = math.log(total) * supervisor_share  *supervisor_importance_value
            money = int(money)
            form_client.deadline = deadline
            form_client.formclint.follow_project = 'under-process-by-expert'
            # form_client.status = 's'
            form_client.formclint.status = 'hidden'
            form_client.status = 'view_projects'


            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert sent the project to the supervisors", event_date=timezone.now(), tracing_project=form_client.formclint)

            # create_obj = ResearchProject.objects.create(proposal_supervisor=form_client, status='send_proposal')
            form_client.save()
            form_client.formclint.save()
            for user in users:
                new_reject = IndustryExpertForSupervisor.objects.create(client_form=form_client, supervisor=user)
                
                e_subject ="TECVICO Project (Project ID: {})".format(form_client.formclint.id_project) 
                e_content ="Dear {}\nHello\nHope you are going well.\n Good news to TECVICO supervisors \nTECVICO has recently accepted a project and is offering it to you. If you are interested in undertaking this project, you can go to your dashboard and look it at. You are allowed to submit your proposal by {} (Coordinated Universal Time (UTC)). Your proposal will be reviewed by at least 2 reviewers and research team will inform final decision to you after collecting reviewers’ evaluation. \nTitle:{} \nDescription:{} \nFund:${} \n TECVICO looks forward to seeing your valuable proposal. Do not reply to this Email. If you have any questions or concerns, please feel free to contact the the expert through {}. \n\nThank you \n Best regards \nTECVICO Corp.".format(user.get_full_name(), form_client.deadline, form_client.formclint.title, form_client.formclint.abstrack,  form_client.formclint.fund, form_client.expert.researchrole.expert_email_address)
                e_destination = user.email
                send_new_email(e_subject,e_content,e_destination)
                    
                Notification(title='Project (ID: {})'.format(form_client.formclint.id_project), 
                    description='Good news to TECVICO supervisors \nTECVICO has recently accepted a project and is offering it to you. If you are interested in undertaking this project, you can go to your dashboard and look it at. You are allowed to submit your proposal by {} (Coordinated Universal Time (UTC)).'.format(form_client.deadline), target=user, 
                    link=reverse('industry:industry-supervisor-detail', args=[form_client.pk])).save()
                
            messages.success(request,'Your project has been submitted successfully.')


            return redirect("industry:industry-expert-list")

        form_contract = SendContractForSupervisor(request.POST or None, request.FILES)
        if form_contract.is_valid():
            Contract = form_contract.cleaned_data.get("Contract")
            status = form_contract.cleaned_data.get("status")


            form_client.formclint.contract = Contract
            form_client.formclint.status = 'send-contract-to-client'
            form_client.formclint.follow_project = 'sent_contract_to_client'
            form_client.status = 'send-contract-to-client'
            form_client.formclint.deadline = timezone.now() + timedelta(3)
            form_client.save()
            form_client.formclint.save()

            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert sent the contract to the client", event_date=timezone.now(), tracing_project=form_client.formclint)


            Notification(title='Project (ID: {})'.format(form_client.formclint.id_project),
            description='You must sign the contact and submit it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(form_client.formclint.deadline.strftime('%Y/%m/%d %H:%M')), target=form_client.formclint.user,
            link='').save()
            

            e_subject ="TECVICO Project (Project ID: {})".format(form_client.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe contract is now available on your dashboard. Your submission will be completed while you sign and then upload the contract. If you do not send the signed contract by {} (Coordinated Universal Time (UTC)), the proposal will be rejected automatically. \nWe will inform you if we need more information. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(form_client.formclint.user.get_full_name(), form_client.formclint.deadline.strftime('%Y/%m/%d %H:%M'), form_client.expert.researchrole.expert_email_address)
            e_destination = form_client.formclint.user.email
            send_new_email(e_subject,e_content,e_destination)

            messages.success(request,'The contract has been sent to the client successfully.')
            return redirect("industry:industry-expert-list")

        form_revise_contract = ReviseContract(request.POST or None, request.FILES)
        if form_revise_contract.is_valid():
            Contract = form_revise_contract.cleaned_data.get("Contract")
            comment = form_revise_contract.cleaned_data.get("comment")
            
            if Contract:
                form_client.formclint.contract = Contract
            form_client.formclint.reason_rejectd = comment
            form_client.formclint.status = 'revised-contract'
            form_client.formclint.follow_project = 'revised_contract'
            form_client.formclint.deadline = timezone.now() + timedelta(3)
            form_client.status = 'revised-contract'
            form_client.save()
            form_client.formclint.save()

            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert revised the signed contract and sent it to the client", event_date=timezone.now(), tracing_project=form_client.formclint)

            Notification(title='Project (ID: {})'.format(form_client.formclint.id_project),
            description='Your contract needs a revision. You are strongly recommended to modify the contact and then submit it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(form_client.formclint.deadline.strftime('%Y/%m/%d %H:%M')), target=form_client.formclint.user,
            link='').save()
            

            e_subject ="TECVICO Project (Project ID: {})".format(form_client.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYour contract needs a revision. You are strongly recommended to re-send the modified contract by {} (Coordinated Universal Time (UTC)). \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(form_client.formclint.user.get_full_name(), form_client.formclint.deadline.strftime('%Y/%m/%d %H:%M'), form_client.expert.researchrole.expert_email_address)
            e_destination = form_client.formclint.user.email
            send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request,'The contract has been revised.')
            return redirect("industry:industry-expert-list")
        context = {
            'object': form_client,
            'form': form
        }

        return render(request, 'industry/expert/expert-detail.html', context)

    else:
        raise Http404("You can't see this page.")


def action_contract_client(request):
    if request.method == "POST":
        status = request.POST.get('status')
        comment = request.POST.get('comment')
        id_project = int(request.POST.get('id_project'))

        obj_project = IndustryFormClient.objects.get(id=id_project)

        if status  == 'send-contract-to-director':
            obj_project.reason_rejectd = comment
            obj_project.status = 'send-contract-to-director'
            obj_project.save()

            for i in obj_project.forms_client.filter(~Q(status="is_change")):
                i.status = 'send-contract-to-director'
                i.save()
                
            for i in ResearchRole.objects.filter(director=True):
                
                Notification(title='Project (ID: {})'.format(obj_project.id_project),
                description='The expert has sent the signed contract to you. For more information, go to your dashboard.', target=i.user,
                link='').save()
                
                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \n The expert has sent the signed contract to you. Go to your dashboard and proceed with it. \nDo not reply to this Email.\n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name())
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)


            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert sent the signed contract to the director", event_date=timezone.now(), tracing_project=obj_project)

            messages.success(request,'Your project has been submitted successfully.')
            return redirect('industry:industry-expert-list')



class ExpertSupervisorDetail(LoginRequiredMixin, SecurityExpertSub, DetailView):
    template_name = 'industry/expert/expert-detail-supervisor.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        obejct_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
        return obejct_supervisor
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryReviewer.objects.filter(object_supervisor_id=pk)
        context['reviewer_count'] = IndustryReviewer.objects.filter(object_supervisor_id=pk).count()
        return context



@login_required
def expert_supervisor_detail(request, pk):
    template_name = 'industry/expert/expert-detail-supervisor.html'
    obejct_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    user_role = ResearchRole.objects.filter(user=request.user).count()
    if obejct_supervisor.status == 'm' or obejct_supervisor.status == 'a' and user_role != 0 and request.user.researchrole.expert == True and obejct_supervisor.client_form.expert == request.user:
        reviewer = IndustryReviewer.objects.filter(object_supervisor=obejct_supervisor)

        form_reject = ReturnedProjectForSupervisor(request.POST or None, initial={"status": obejct_supervisor.status, "reason_reject": obejct_supervisor.reason_reject,})
        if form_reject.is_valid():
            status = form_reject.cleaned_data.get("status")
            reason_reject = form_reject.cleaned_data.get("reason_reject")
            
            obejct_supervisor.status= status
            obejct_supervisor.reason_reject= reason_reject
            obejct_supervisor.follow_project = 'reject_by_expert'
            obejct_supervisor.save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(obejct_supervisor.client_form.formclint.id_project)  
            e_content ="Dear {} \nHello\nHope you are going well.\nThe company has reviewed your project.\n“Title: {}”\n“Submitted date: {}” \nTECVICO is very grateful to you that you considered it worthy of the new project. \nWith the help of this letter, TECVICO is feeling very sorry to decline to work on this project offer because of:\n “{}”, as you can see those comments on your dashboard completely. \nYou will also be able to re-submit this project based on considering those comments. \nWe welcome you to submit other projects in the future. We hope to work with you in the near future. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you  \nBest regards \nTECVICO Corp.".format(obejct_supervisor.supervisor.get_full_name(), obejct_supervisor.client_form.formclint.title, date.today(), obejct_supervisor.reason_reject, obejct_supervisor.client_form.expert.researchrole.expert_email_address)
            e_destination = obejct_supervisor.supervisor.email
            send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request,'The proposal has been revised to the supervisor.')
            return redirect("industry:industry-expert-list")

        context = {
        'object': obejct_supervisor, 
        'reviewer': reviewer,
        'form_reject': form_reject
        }

        return render(request, template_name, context)
    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-expert-list')



#detail send contract for supervisor

@login_required
def expert_contract_detail(request, pk):
    template_name = 'industry/expert/expert-contract-detail.html'
    roles = ResearchRole.objects.all() 
    expert_contract =  get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    if expert_contract.status == 'x' or expert_contract.status == 'director_revise_contract' or expert_contract.status == 'g' and request.user.researchrole.expert == True and expert_contract.client_form.expert == request.user:
        form_reject = ReturnedProjectForSupervisor(request.POST or None, initial={"status": expert_contract.status, "reason_reject": expert_contract.reason_reject,})
        if form_reject.is_valid():
            status = form_reject.cleaned_data.get("status")
            reason_reject = form_reject.cleaned_data.get("reason_reject")
            
            expert_contract.status= status
            expert_contract.reason_reject= reason_reject
            expert_contract.deadline = timezone.now() + timedelta(3)

            if expert_contract.client_form.formclint.main_supervisor:
                expert_contract.client_form.formclint.follow_project = 'p_main_contract_revise'
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert revised the signed contract and sent it to the supervisor", event_date=timezone.now(), tracing_project=expert_contract.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert revised the signed contract and sent it to the supervisor", event_date=timezone.now(), tracing_supervisor=expert_contract)

            expert_contract.client_form.formclint.save()

            expert_contract.follow_project = 'reject_by_expert'
            expert_contract.save()
            

            Notification(title='Project (ID: {})'.format(expert_contract.client_form.formclint.id_project), 
                description='Your contract needs a revision. You are strongly recommended to modify the contact and then submit it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(expert_contract.deadline.strftime('%Y/%m/%d %H:%M')), target=expert_contract.supervisor, 
                link=reverse('industry:industry-supervisor-see-contract', args=[expert_contract.pk])).save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(expert_contract.client_form.formclint.id_project, )
            e_content = "Dear {} \nHello\nHope you are going well.\n Your contract needs a revision. You are strongly recommended to re-send the modified contract by {} (Coordinated Universal Time (UTC)).\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(expert_contract.supervisor.get_full_name(), expert_contract.deadline.strftime('%Y/%m/%d %H:%M'), expert_contract.client_form.expert.researchrole.expert_email_address)
            e_destination = expert_contract.supervisor.email
            send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request,'The contract has been revised.')
            return redirect("industry:industry-expert-list")

        form_contract = SendContractForSupervisor(request.POST,  request.FILES, initial={"status": expert_contract.status, 
            "Contract": expert_contract.Contract, "status_value": expert_contract.client_form.status_value, 
            "valeu": expert_contract.client_form.valeu,})
        if form_contract.is_valid():
            status = form_contract.cleaned_data.get("status")
            Contract = form_contract.cleaned_data.get("Contract")

            if expert_contract.client_form.formclint.main_supervisor:
                if status == 'z':
                    expert_contract.client_form.formclint.follow_project = 'p_main_change_to_new_to_status'
                    if expert_contract.status == 'director_revise_contract':
                        create_obj_tracing = Tracing.objects.create(
                            position='Expert', user=request.user, status="The expert sent the resubmitted contract to the director", event_date=timezone.now(), tracing_project=expert_contract.client_form.formclint)
                    else:
                        create_obj_tracing = Tracing.objects.create(
                            position='Expert', user=request.user, status="The expert sent the resubmitted contract to the director", event_date=timezone.now(), tracing_project=expert_contract.client_form.formclint)
                else:
                    expert_contract.client_form.formclint.follow_project = 'p_main_contract_sent_supervisor'
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the contract to the supervisor", event_date=timezone.now(), tracing_project=expert_contract.client_form.formclint)

            else:

                if status == 'z':
                    if expert_contract.status == 'director_revise_contract':
                        create_obj_tracing = Tracing.objects.create(
                            position='Expert', user=request.user, status="The expert sent the resubmitted contract to the director", event_date=timezone.now(), tracing_supervisor=expert_contract)
                    else:
                        create_obj_tracing = Tracing.objects.create(
                            position='Expert', user=request.user, status="The expert sent the resubmitted contract to the director", event_date=timezone.now(), tracing_supervisor=expert_contract)
                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the contract to the supervisor", event_date=timezone.now(), tracing_supervisor=expert_contract)
            
            expert_contract.status= status
            expert_contract.Contract= Contract
            expert_contract.client_form.deadline = timezone.now() + timedelta(3)
                
            expert_contract.client_form.formclint.save()
            expert_contract.save()
            expert_contract.client_form.save()
            if expert_contract.contract_supervisor:
                for i in roles:
                    if i.director == True:
                        
                        e_subject ="TECVICO Project (Project ID: {})".format(expert_contract.client_form.formclint.id_project,)  
                        e_content ="Dear{}\nHello\nHope you are going well. \n The signed contract sent by the supervisor is reviewed and acceptable. Please go to your dashboard and observe and proceed with it. \nDo not reply to this Email. \n\nThank you \nBest regards\n TECVICO Corp.".format(i.user.get_full_name(),expert_contract.client_form.formclint.title, date.today(), )
                        e_destination = i.user.email
                        send_new_email(e_subject,e_content,e_destination)
                        

                pk_slug = pk
                pk_slug = str(pk_slug)
                title_slug = expert_contract.client_form.formclint.title
                slug_forum = title_slug + pk_slug
                


                messages.success(request,'The signed contract has been sent to the director successfully.')
            else:
                
                e_subject ="TECVICO Project (Project ID: {})".format(expert_contract.client_form.formclint.id_project, )  
                e_content ="Dear {}\nHello\nHope you are going well.\n Thank you for your contribution. \nCongrat! Your proposal has been accepted. The contract is now available on your dashboard. Your submission will be completed while you sign and then upload the contract. If you do not send the signed contract by {} (Coordinated Universal Time (UTC)), the proposal will be rejected automatically. \nWe will inform you if we need more information. \nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the expert throug {}. \n\nThank you\nSincerely, \nTECVICO Corp.".format(expert_contract.supervisor.get_full_name(), expert_contract.client_form.deadline.strftime('%Y/%m/%d %H:%M'), expert_contract.client_form.expert.researchrole.expert_email_address)
                e_destination = expert_contract.supervisor.email
                send_new_email(e_subject,e_content,e_destination)
                
                messages.success(request,'The contract has been sent to the supervisor successfully.')
            return redirect("industry:industry-expert-list")



        context = {
            'object': expert_contract,
            'form_contract': form_contract,
            'form_reject': form_reject
        }
    
        return render(request, template_name,context)

    else:
        raise Http404("You can't see this page.")

#send reviewer
@login_required
def sepervisor_send_review(request, **kwargs):
    template_name = 'industry/expert/expert-send-reviewer.html'
    form_id = kwargs["form_id"]
    user_role = ResearchRole.objects.filter(user=request.user).count()
    form_client = IndustryExpertForSupervisor.objects.get(id=form_id)
    if user_role != 0 and form_client.status == 'resubmition' or form_client.status == 'v' or form_client.status == 'm' or form_client.status == 'a' or form_client.status == 'revise-proposal-to-expert' and request.user.researchrole.expert == True and form_client.client_form.expert == request.user:

        users = User.objects.filter(researchrole__reviewer= True)
        form = Reviewer(request.POST or None, initial={"form_id":form_client.id, "status": form_client.status,})
        if form.is_valid():
            form_id = form.cleaned_data.get("form_id")
            status = form.cleaned_data.get("status")
            user_list = form.cleaned_data.get("user_list")
            user_list = user_list.split(",")
            form_client.follow_project = 'send_to_reviewer'
            form_client.status = 'v'
            form_client.status_review = 'Pending for reviewer approval'
            form_client.client_form.status = 'review'
            
            if form_client.client_form.formclint.main_supervisor :
                form_client.client_form.formclint.follow_project = 'p_main_send_review'
            form_client.client_form.formclint.save()
            form_client.client_form.save()
            form_client.save()

            for user in user_list:
                user = int(user)
                user = User.objects.get(id=user)
                deadline = timezone.now() + timedelta(2)
                new_reject = IndustryReviewer.objects.create(object_supervisor_id=form_client.id, event_date=timezone.now(), reviewer=user, deadline=deadline)
                
                email_2_day = date.today() + timedelta(2)
                email_7_day = date.today() + timedelta(7)



                if form_client.client_form.formclint.main_supervisor :
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the proposal review request to the reviewer", event_date=timezone.now(), tracing_project=form_client.client_form.formclint)
                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the proposal review request to the reviewer", event_date=timezone.now(), tracing_supervisor=form_client)

                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert sent the proposal review request to the reviewer", event_date=timezone.now(), tracing_reviewer=new_reject)
            
                
                e_subject ="TECVICO Project (Project ID: {})".format(form_client.client_form.formclint.id_project, )  
                e_content ="Dear {} \nHello\nHope you are going well. \nYou have been invited to review this proposal. The evaluation form and full information of the proposal will be available on your dashboard. The reviewer should notify her/his assent to the company to review the proposal by {} (Coordinated Universal Time (UTC)). The system will remove the reviewer if confirmation is not recorded automatically. Furthermore, the deadline of review will be 1 week after the request on {}. \nTitle «{}» \nFund «${}» \nAbstract «{}» \nIf you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you\nSincerely\nTECVICO Corp.".format(user.get_full_name(), new_reject.deadline.strftime('%Y/%m/%d %H:%M'), email_7_day, form_client.client_form.formclint.title, form_client.client_form.formclint.fund, form_client.client_form.formclint.abstrack, form_client.client_form.expert.researchrole.expert_email_address)
                e_destination = user.email
                send_new_email(e_subject,e_content,e_destination)
                
                
                
            messages.success(request,'The proposal has been sent to the reviewer(s) successfully.')
            return redirect("industry:industry-expert-reviewer-detail", form_client.pk)

        context = {
            "form" : form,
            "form_client": form_client,
            "users": users,
            "history_reviewer": IndustryReviewer.objects.filter(status__in=['r', 'e', 's', 'breach_of_promis_p']),
            "history_reviewer_accept_count": IndustryReviewer.objects.filter(status='e').count(),
            "history_reviewer_reject_count": IndustryReviewer.objects.filter(status__in=['r', ]).count(),
        }

        return render(request, template_name, context)
    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-expert-list')

    

class SpecialExpertAcceptOrRejectPage(LoginRequiredMixin, SecurityExpert, ListView):
    template_name = 'industry/expert/special/expert-special-accept-reject.html'
    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            return IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created")
        else:
            return IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            context['accept_reject_project_count'] = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,).order_by("-created").count()
        else:
            context['accept_reject_project_count'] = IndustryFormExpert.objects.filter(formclint__status='accept_or_reject_expert' ,expert=self.request.user).order_by("-created").count()

        context['accept_or_reject_main_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,client_form__expert=self.request.user).order_by("-created")
        context['superuser_accept_or_reject_main_supervisor'] = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,).order_by("-created")

        if self.request.user.is_superuser or self.request.user.researchrole.director == True:
            context['accept_or_reject_main_supervisor_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,).order_by("-created").count()
        else:
            context['accept_or_reject_main_supervisor_count'] = IndustryExpertForSupervisor.objects.filter(status='special_expert' ,client_form__expert=self.request.user).order_by("-created").count()
        return context


@login_required
def special_expert_detail_mainsupervisor(request, pk):
    special_expert = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    context = {
        'object': special_expert
    }
    return render(request, 'industry/expert/special/expert-special-detail_main.html', context)


@login_required
def special_expert_detail_see_review(request, pk):
    roles = ResearchRole.objects.all()
    special_expert = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    form_accept = RejectReviewForm(request.POST,  request.FILES, initial={"status_r": special_expert.status,})
    if form_accept.is_valid():
        status_r = form_accept.cleaned_data.get("status_r")
        
        special_expert.status= 'x'
        special_expert.follow_project= 'accept_by_director'
        special_expert.client_form.formclint.save()
        special_expert.save()
        
        e_subject ="TECVICO Project (Project ID: {})".format(special_expert.client_form.formclint.id_project, )  
        e_content ="Dear{}\nHello\n Hope you are going well. \n You accepted the proposal. Please go to your dashboard and send the contract to the supervisor.\nIf you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(special_expert.client_form.expert.get_full_name(), special_expert.reason_reject)
        e_destination = special_expert.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)
            
        messages.success(request,'The proposal has been sent to the expert successfully.')
        return redirect("dashboard-page")

    form_reject = FormRejectDirector(request.POST,  request.FILES, initial={"status": special_expert.status,
        "reason_reject": special_expert.reason_reject,})
    if form_reject.is_valid():
        status = form_reject.cleaned_data.get("status")
        reason_reject = form_reject.cleaned_data.get("reason_reject")
        
        special_expert.status= 'h'
        special_expert.reason_reject= reason_reject
        special_expert.follow_project= 'reject_by_director'
        special_expert.save()

        if special_expert.client_form.directo_see_reviewer == True:
            for i in roles:
                if i.director == True:
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(special_expert.client_form.formclint.id_project, ) 
                    e_content ="Dear {}\nHello\nHope you are going well.\nThe expert, namely {}, has rejected the proposal because of:\n “{}”.\n Title: {}\n Submitted date: {} \nIf you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \n TECVICO Corp.".format(i.user.get_full_name(), special_expert.client_form.expert.get_full_name(), reason_reject, special_expert.client_form.formclint.title, special_expert.client_form.formclint.created, special_expert.client_form.expert.researchrole.expert_email_address)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)
                
            
            e_subject ="TECVICO Project (Project ID: {})".format(special_expert.client_form.formclint.id_project, )  
            e_content ="Dear {}\nHello\nHope you are going well.\n TECVICO is writing this letter to thank you for showing interest in working with us. Unfortunately, your proposal has been rejected by our board of directors because of:\n “{}”, as you can see those comments on your dashboard completely. We welcome you to submit other proposasls in the future.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com. \n\nThank you \nSincerely\nTECVICO Corp.".format(special_expert.supervisor.get_full_name(), reason_reject)
            e_destination = special_expert.supervisor.email
            send_new_email(e_subject,e_content,e_destination)
            
        else:
            e_subject ="TECVICO Project (Project ID: {})".format(special_expert.client_form.formclint.id_project, ) 
            e_content ="Dear {}\nHello\nHope you are going well.\n TECVICO is writing this letter to thank you for showing interest in working with us. Unfortunately, your proposal has been rejected by our board of directors because “{}”, as you can see those comments on your dashboard completely. We welcome you to submit other proposasls in the future.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nSincerely\nTECVICO Corp.".format( special_expert.supervisor.get_full_name(), special_expert.reason_reject, special_expert.client_form.expert.researchrole.expert_email_address)
            e_destination = special_expert.supervisor.email
            send_new_email(e_subject,e_content,e_destination)

            
            e_subject ="TECVICO Project (Project ID: {})".format(special_expert.client_form.formclint.id_project, )
            e_content ="Dear {}\nHello\nHope you are going well.\n Unfortunately, The director has rejected the proposal because “{}”, as you can see those comments on your dashboard completely. We hope to see you as a research expert in other projects in the future.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nSincerely\nTECVICO Corp.".format(special_expert.client_form.expert.get_full_name(), special_expert.reason_reject)
            e_destination = special_expert.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
        messages.error(request,'The proposal was rejected.')
        return redirect("dashboard-page")

    context = {
        'object': special_expert, 
        'form_accept': form_accept,
        'form_reject': form_reject,
        'reviewer' : IndustryReviewer.objects.filter(status__in=['n', 'r', 'a', 'e'], object_supervisor=special_expert)
    }
    return render(request, 'industry/expert/special/expert-special-detail-see-review.html', context)


class ExpertManageProject(LoginRequiredMixin, SecurityExpert, ListView):
    template_name = 'industry/expert/expert-manage-project.html'
    def get_queryset(self):
        return ResearchProject.objects.filter( project__client_form__expert=self.request.user).order_by("-created")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Report project
        context['count_report_projects_object'] = ResearchProject.objects.filter(status="on_going", project__client_form__expert=self.request.user).order_by("-created").count()
        context['badge_report'] = 0

        # Manage project
        context['project_change_status'] = ResearchProject.objects.filter(status_change='send_to_expert', project__client_form__expert=self.request.user).order_by("-created")
        context['count_project_change_status'] = ResearchProject.objects.filter(status_change='send_to_expert', project__client_form__expert=self.request.user).order_by("-created").count()

        # Applicants
        advisor_count = SuperVizor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user).count()
        mentor_count = Mentor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user).count()
        member_count = Member.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user).count()
        learner_count = Lerner.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user).count()

        context['applicant_cart_count'] = advisor_count + mentor_count + member_count + learner_count 

        advisor_obj = SuperVizor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user)
        mentor_obj = Mentor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user)
        member_obj = Member.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user)
        learner_obj = Lerner.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=self.request.user)

        applicant_list = []
        for i in advisor_obj:
            applicant_list.append(i.research)
            
        for i in mentor_obj:
            applicant_list.append(i.research)
            
        for i in member_obj:
            applicant_list.append(i.research)
            
        for i in learner_obj:
            applicant_list.append(i.research)

        applicant_list = set(applicant_list)
        applicant_list = list(applicant_list)
        context['applicant_list'] =applicant_list



        # Applicant remove
        advisor__remove_count = SuperVizor.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user).count()
        mentor__remove_count = Mentor.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user).count()
        member__remove_count = Member.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user).count()
        learner__remove_count = Lerner.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user).count()

        advisor__remove_obj = SuperVizor.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user)
        mentor__remove_obj = Mentor.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user)
        member__remove_obj = Member.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user)
        learner__remove_obj = Lerner.objects.filter(status_remove='request-remove', research__project__client_form__expert=self.request.user)


        context['applicant_remove_cart_count'] = advisor__remove_count + mentor__remove_count + member__remove_count + learner__remove_count

        applicant_remove_list = []

        applicant_remove_list = []
        for i in advisor__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in mentor__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in member__remove_obj:
            applicant_remove_list.append(i.research)
            
        for i in learner__remove_obj:
            applicant_remove_list.append(i.research)

        applicant_remove_list = set(applicant_remove_list)
        applicant_remove_list = list(applicant_remove_list)
        context['applicant_remove_list'] =applicant_remove_list



        # Comment applicant
        count = 0

        count_meesage_applicant = ApplicantComment.objects.filter(position='send_to_expert', seen=False, project__project__client_form__expert=self.request.user).count()

        for i in ApplicantComment.objects.filter(position='send-to-applicant'):
            for e in i.comments.filter(seen=False):
                if i.project.project.client_form.expert == self.request.user:
                    count += 1
        context['applicant_comment_count'] = count_meesage_applicant + count

        project_expert = ResearchProject.objects.filter(project__client_form__expert=self.request.user, status__in=["new", 'on_going', 'pending', 'on_hold'] ).order_by("-created")
        applicant_comment_list = []
        for i in project_expert:
            if i.comment_project.all():
                applicant_comment_list.append(i)
        context['applicant_comment_list'] = applicant_comment_list

        # History
        context['history_list'] = ResearchProject.objects.filter(
            project__client_form__expert=self.request.user, 
            project__client_form__formclint__project_created=True).order_by("-created")

        context['history_list_count'] = ResearchProject.objects.filter(
            project__client_form__expert=self.request.user, 
            project__client_form__formclint__project_created=True).order_by("-created").count()


        # Temporal history
        context['temporal_history_count'] = ResearchProject.objects.filter(
            ~Q(status__in=["on_hold", "done", 'delete']), project__client_form__expert=self.request.user).order_by("-created").count()

        context['temporal_history_list'] = ResearchProject.objects.filter(
            ~Q(status__in=["on_hold", "done", 'delete']), project__client_form__expert=self.request.user).order_by("-created")

        return context



@login_required
def expert_view_change_status(request, pk):
    template_name = 'industry/expert/expert-manage-project-change-status.html'
    change_status = get_object_or_404(ResearchProject, pk=pk)

    form_reject_status = SendRejectForm(request.POST)
    if form_reject_status.is_valid():

        status = form_reject_status.cleaned_data.get("status")
        reason_rejectd = form_reject_status.cleaned_data.get("reason_rejectd")
        
        change_status.reason_reject_expert = reason_rejectd
        change_status.status_change = status
        change_status.save()


        if change_status.status == 'new':
            new_status = 'New'

        elif change_status.status == 'on_going':
            new_status = 'Ongoing'

        elif change_status.status == 'pending':
            new_status = 'Pending'

        elif change_status.status == 'on_hold':
            new_status = 'On hold'

        elif change_status.status == 'done':
            new_status = 'Done'

        if change_status.status_change_choices == 'new':
            new_request_status = 'New'

        elif change_status.status_change_choices == 'on_going':
            new_request_status = 'Ongoing'

        elif change_status.status_change_choices == 'pending':
            new_request_status = 'Pending'

        elif change_status.status_change_choices == 'on_hold':
            new_request_status = 'On hold'

        elif change_status.status_change_choices == 'done':
            new_request_status = 'Done'


        create_obj_tracing = Tracing.objects.create(
            position='Expert', user=request.user, status="The expert rejected the status change request from the supervisor", event_date=timezone.now(), tracing_project_phase_2=change_status)
            
        Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project), 
            description='Your request to change the project status was rejected. For more information, go to your dashboard.', target=change_status.main_supervisor, 
            link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nYour request to change the project status from {} to {} was rejected because of: \n{}.\n For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(change_status.main_supervisor.get_full_name(), new_status, new_request_status, change_status.text_change_status, change_status.project.client_form.expert.researchrole.expert_email_address)
        e_destination = change_status.main_supervisor.email
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request,'You rejected the status change request.')
        return redirect("industry:research-expert-manage-project")


    form_accept_status = ChangeStatusForm(request.POST)
    if form_accept_status.is_valid():

        status = form_accept_status.cleaned_data.get("status")
        comment = form_accept_status.cleaned_data.get("comment")

        if status == 'send_to_director':
            change_status.status_change = 'send_to_director'
            change_status.reason_reject_expert = comment
            change_status.save()

            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert sent a request to the director to change the status of the project", event_date=timezone.now(), tracing_project_phase_2=change_status)
            

            for i in ResearchRole.objects.filter(director=True):
                Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project), 
                    description='A new request to change the project status is available on your list. For more information, go to your dashboard.', target=i.user, 
                    link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nA supervisor has requested to change the project status.\nTitle: {}\n Please go to your dashboard and proceed with it. \nDo not reply to this Email.If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), change_status.project.client_form.formclint.title, change_status.project.client_form.expert.researchrole.expert_email_address)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)


            messages.success(request,'The status change request has been sent to the director successfully.')

        elif status == 'accept':
            change_status.status_change = 'accept'
            change_status.status = change_status.status_change_choices
            change_status.save()
            
            for i in RequestUserForProject.objects.filter(project_request=change_status, status='request'):
                i.status = 'reject'
                i.save()

            create_obj_tracing = Tracing.objects.create(
                position='Expert', user=request.user, status="The expert accepted the status change request from the supervisor and the project was moved to {} status".format(change_status.status), event_date=timezone.now(), tracing_project_phase_2=change_status)
                


            Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project), 
                description='Your request to change the project status has been accepted. For more information, go to your dashboard.', target=change_status.main_supervisor, 
                link='').save()

            e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYour request to change the project status has been accepted. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(change_status.main_supervisor.get_full_name(), change_status.project.client_form.expert.researchrole.expert_email_address)
            e_destination = change_status.main_supervisor.email
            send_new_email(e_subject,e_content,e_destination)


            if change_status.status == 'new':
                new_status = 'New'

            elif change_status.status == 'on_going':
                new_status = 'Ongoing'

            elif change_status.status == 'pending':
                new_status = 'Pending'

            elif change_status.status == 'on_hold':
                new_status = 'On hold'

            elif change_status.status == 'done':
                new_status = 'Done'
                
            email_name = 'expert'
            email_address = change_status.project.client_form.expert.researchrole.expert_email_address
            if change_status.status == 'done':
                email_name = 'company'
                email_address = 'project@tecvico.com'

            for i in change_status.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been moved to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the {} through {}.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status, email_name, email_address)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project,), 
                    description='The project has been moved to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                    link=reverse('industry:industry-view-edit', args=[change_status.pk])).save()


            for i in change_status.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been moved to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the {} through {}.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status, email_name, email_address)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project,), 
                    description='The project has been moved to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                    link=reverse('industry:industry-view-edit', args=[change_status.pk])).save()


            for i in change_status.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been moved to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the {} through {}.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status, email_name, email_address)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project,), 
                    description='The project has been moved to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                    link=reverse('industry:industry-view-edit', args=[change_status.pk])).save()


            for i in change_status.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                e_subject ="TECVICO Project (Project ID: {})".format(change_status.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe project has been moved to {} status. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the {} through {}.  \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_status, email_name, email_address)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(change_status.project.client_form.formclint.id_project,), 
                    description='The project has been moved to {} status. For more information, go to your dashboard.'.format(new_status), target=i.user, 
                    link=reverse('industry:industry-view-edit', args=[change_status.pk])).save()


            messages.success(request,'You have accpeted the status change request successfully.')

        return redirect("industry:research-expert-manage-project")


    context = {
        'change_status': change_status,
        'form_reject_status': form_reject_status,
        'form_accept_status': form_accept_status,
    }
    return render(request, template_name, context)
#------------Supervisor------------#
#list supervisor
class SupervisorPanel(LoginRequiredMixin, SecuritySupervisor, ListView):
    template_name = 'industry/supervisor/supervisor-list.html'
    def get_queryset(self):
        return IndustryExpertForSupervisor.objects.filter(status='u', supervisor=self.request.user).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        #accpet project
        context['count_contract_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status__in=['t', 'reject_contract'], supervisor=self.request.user).order_by("-created").count()

        #new
        context['count_new_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='u', supervisor=self.request.user).count()

        #reject proposal
        context['count_returned_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status__in=['b', 'h'], supervisor=self.request.user).count()
        
        # new prject
        context['new_projects'] = IndustryExpertForSupervisor.objects.filter(status='u', supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created")
        context['new_projects_count'] = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created").count()

        context['history_list'] = IndustryExpertForSupervisor.objects.filter(
            deleted=False,
            supervisor=self.request.user).order_by("-created")

        context['history_list_count'] = IndustryExpertForSupervisor.objects.filter(
            deleted=False,
            supervisor=self.request.user).order_by("-created").count()
        return context

# class SupervisoeRejectsList(LoginRequiredMixin, SecuritySupervisor, ListView):
#     template_name = 'industry/supervisor/supervisor-rejects-list.html'
#     def get_queryset(self):
#         return IndustryExpertForSupervisor.objects.filter(status='b', supervisor=self.request.user).order_by("-created")
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['superuser_count_returned_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='b').count()
#         context['count_returned_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='b', supervisor=self.request.user).count()

#         #reject project
#         context['reject_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='h', supervisor=self.request.user).order_by("-created")
#         context['count_reject_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='h', is_new_reject=0, supervisor=self.request.user).order_by("-created").count()
#         return context

@login_required
def reject_supervisor_reject(request, pk):
    template_name = 'industry/supervisor/reject-supervisor-detail.html'
    supevisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    if request.method == 'POST':
        supevisor.status = "deleted"
        supevisor.save()
        return redirect("industry:industry-supervisor-rejects-list")
    context = {
        'object': supevisor
    }
    return render(request, template_name, context)


class SupervisorContractList(LoginRequiredMixin, SecuritySupervisor, ListView):
    template_name = 'industry/supervisor/supervisor-list-contract.html'
    def get_queryset(self):
        return IndustryExpertForSupervisor.objects.filter(status='t', supervisor=self.request.user).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #accpet project
        context['reject_contract_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='reject_contract', supervisor=self.request.user).order_by("-created")
        context['count_reject_contract_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='reject_contract', supervisor=self.request.user).order_by("-created").count()


        context['count_contract_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='t', supervisor=self.request.user).order_by("-created").count()


        return context

#filter new project
class SupervisoeFilterNewProjectList(LoginRequiredMixin, SecuritySupervisor, ListView):
    template_name = 'industry/supervisor/supervisor-filter-list.html'
    def get_queryset(self):
        return IndustryExpertForSupervisor.objects.filter(status='u', supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # filter not fund
        context['filter_not_fund'] = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=self.request.user, client_form__formclint__fund__lte=0).order_by("-created")
        context['count_filter_not_fund'] = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=self.request.user, client_form__formclint__fund=0).order_by("-created").count()
        # filter fund
        context['count_filter_fund'] = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created").count()
        return context

class SupervisorDetailRejectProject(LoginRequiredMixin, SecuritySupervisorDetail, DetailView):
    template_name = 'industry/supervisor/supervisor-detail-reject-project.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reviewer'] = IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk)
        return context
        
#detail supervisor
@login_required
def supervisor_form_detail(request, pk):
    template_name = 'industry/supervisor/supervisor-detail.html'
    roles = ResearchRole.objects.all()
    supervisor_detail = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    supervisor_objs = IndustryExpertForSupervisor.objects.filter(~Q(status=["u", "not-pay"]), client_form=supervisor_detail.client_form, supervisor=request.user)
    is_supervisor = False
    if supervisor_objs:
        is_supervisor = True
    if request.user.is_superuser or request.user.memberprofile.position == 'Supervisor' and  supervisor_detail.supervisor == request.user \
    or request.user.researchrole.director == True :

        form_accept = FormSupervisorAccept(request.POST,  request.FILES, initial={"status": supervisor_detail.status, "propzar": supervisor_detail.propzar,})
        form_decline = FormDeclineRequestSupervisor(request.POST) 
        if request.method == 'POST':
            if form_accept.is_valid():
                status = form_accept.cleaned_data.get("status")
                propzar = form_accept.cleaned_data.get("propzar")
    
                if supervisor_detail.status == 'u':
                    if request.user.memberprofile.balance > 150:
                        final_balance = request.user.memberprofile.balance - 150
                        request.user.memberprofile.balance = final_balance
                        request.user.memberprofile.save()
                    else:
                        return redirect('create-checkout-session')
    
                if supervisor_detail.client_form.formclint.main_supervisor:
                    supervisor_detail.client_form.formclint.follow_project = 'p_main_resubmition_proposal'
                    supervisor_detail.client_form.formclint.save()
    
                if supervisor_detail.status == 'b':
                    supervisor_detail.status= 'resubmition'
                    create_obj_tracing = Tracing.objects.create(
                        position='Supervisor', user=request.user, status="A supervisor, namely {}, resubmitted the revised proposal ".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_supervisor=supervisor_detail)
                else:
                    if supervisor_detail.client_form.formclint.main_supervisor:
                        supervisor_detail.status= 'm'
                    else:
                        supervisor_detail.status= 'a'
                        create_obj_tracing = Tracing.objects.create(
                            position='Supervisor', user=request.user, status="A supervisor, namely {}, submitted a proposal ".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_supervisor=supervisor_detail)

                if propzar:
                    supervisor_detail.propzar= propzar
                supervisor_detail.save()
                fund = supervisor_detail.client_form.formclint.fund
                
                e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, ) 
                e_content ="Dear {} \nHello\nHope you are going well. \nYour proposal has been sent to TECVICO in order to be assessed by reviewers successfully. We will inform the response of the reviewers to you in 2 weeks. \nTitle: {} \nSubmitted date: {} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(supervisor_detail.supervisor.get_full_name(), supervisor_detail.client_form.formclint.title, date.today(), supervisor_detail.client_form.expert.researchrole.expert_email_address)
                e_destination = supervisor_detail.supervisor.email
                send_new_email(e_subject,e_content,e_destination)
                
    
                
                e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, )  
                e_content ="Dear {}\nHello\nHope you are going well. \nA supervisor submitted a proposal for the below project successfully. Please go to your dashboard and observe it.\nTitle: {}\nSubmitted date: {}\nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp.\n".format(supervisor_detail.client_form.expert.get_full_name(), supervisor_detail.client_form.formclint.title, date.today())
                e_destination = supervisor_detail.client_form.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                
                messages.success(request,'The proposal has been submitted successfully.')
                
    
            if form_decline.is_valid():
                status = form_decline.cleaned_data.get("status_d")
                supervisor_detail.status = 'r'
                supervisor_detail.save()
            
                messages.success(request,'You declined to submit your proposal to this project.')
                return redirect("dashboard-myprojects-reserach")
            
        context = {
         'object': supervisor_detail,
         'form_accept': form_accept,
         'is_supervisor': is_supervisor,
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")

@login_required
def supervisor_detail_revise(request, pk):
    template_name = 'industry/supervisor/supervisor-detail-revise.html'
    roles = ResearchRole.objects.all()
    supervisor_detail = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    if request.user.is_superuser or request.user.memberprofile.position == 'Supervisor' and  supervisor_detail.supervisor == request.user \
    or request.user.researchrole.director == True :

        form_accept = FormSupervisorAccept(request.POST,  request.FILES, initial={"status": supervisor_detail.status, "propzar": supervisor_detail.client_form.formclint.main_supervisor,})
        if form_accept.is_valid():
            status = form_accept.cleaned_data.get("status")
            propzar = form_accept.cleaned_data.get("propzar")
            
            title = request.POST.get("title")
            fund = int(request.POST.get("fund"))
            end_date = request.POST.get("end_date")
            start_date = request.POST.get("start_date")
            data_set_link = request.POST.get("data_set_link")
            abstrack = request.POST.get("abstrack")
            equipment = request.POST.get("equipment")
            
            
            last_fund = supervisor_detail.client_form.formclint.fund    
            
            supervisor_detail.client_form.formclint.title = title
            # supervisor_detail.client_form.formclint.fund = fund
            supervisor_detail.client_form.formclint.end_date = end_date
            supervisor_detail.client_form.formclint.start_date = start_date
            supervisor_detail.client_form.formclint.data_set_link = data_set_link
            supervisor_detail.client_form.formclint.abstrack = abstrack
            supervisor_detail.client_form.formclint.equipment = equipment
            
            if supervisor_detail.client_form.formclint.main_supervisor:
                supervisor_detail.client_form.formclint.main_supervisor= propzar
            else:
                supervisor_detail.propzar= propzar
            
            supervisor_detail.save()
            supervisor_detail.client_form.formclint.save()

            if fund > last_fund:
                new_fund = fund - supervisor_detail.client_form.formclint.fund
                return PaymentProtocol(request, 'P', supervisor_detail.client_form.formclint, new_fund, action='increase_fund -{}'.format(supervisor_detail.id))
                
            
            supervisor_detail.status= 'resubmition'

            if supervisor_detail.client_form.formclint.main_supervisor:
                supervisor_detail.client_form.formclint.follow_project = 'p_main_resubmition_proposal'
                supervisor_detail.client_form.formclint.save()
                create_obj_tracing = Tracing.objects.create(
                    position='Client', user=request.user, status="The supervisor, namely {}, resubmitted the proposal".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_project=supervisor_detail.client_form.formclint)

            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Supervisor', user=request.user, status="The supervisor, namely {}, resubmitted the proposal".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_project=supervisor_detail.client_form.formclint)
                supervisor_detail.propzar= propzar
                
            supervisor_detail.save()
            supervisor_detail.client_form.formclint.save()
            
            
            Notification(title='Project (ID: {})'.format(supervisor_detail.client_form.formclint.id_project),
            description='You resubmitted the proposal successfully. For more information, go to your dashboard.', target=supervisor_detail.supervisor,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYou resubmitted the proposal successfully. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(supervisor_detail.supervisor.get_full_name(), supervisor_detail.client_form.expert.researchrole.expert_email_address)
            e_destination = request.user.email
            send_new_email(e_subject,e_content,e_destination)
            

            Notification(title='Project (ID: {})'.format(supervisor_detail.client_form.formclint.id_project),
            description='The supervisor resubmitted the proposal. Go to your dashboard and proceed with it.', target=supervisor_detail.client_form.expert,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe supervisor resubmitted the proposal. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(supervisor_detail.client_form.expert.get_full_name())
            e_destination = supervisor_detail.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            messages.success(request,'The proposal has been resubmitted successfully.')
            return redirect("dashboard-myprojects-reserach")
            
            

        context = {
         'object': supervisor_detail,
         'form_accept': form_accept
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


def agian_resubmit_supervisor(user, pk, fund):
    roles = ResearchRole.objects.all()
    supervisor_detail = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
            
    supervisor_detail.status= 'resubmition'
    
    supervisor_detail.client_form.formclint.fund = fund
    supervisor_detail.client_form.formclint.save()

    if supervisor_detail.client_form.formclint.main_supervisor:
        supervisor_detail.client_form.formclint.follow_project = 'p_main_resubmition_proposal'
        supervisor_detail.client_form.formclint.save()
        create_obj_tracing = Tracing.objects.create(
            position='Client', user=user, status="The supervisor, namely {}, resubmitted the proposal".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_project=supervisor_detail.client_form.formclint)
    else:
        create_obj_tracing = Tracing.objects.create(
            position='Supervisor', user=user, status="The supervisor, namely {}, resubmitted the proposal".format(supervisor_detail.supervisor.get_full_name()), event_date=timezone.now(), tracing_project=supervisor_detail.client_form.formclint)
        supervisor_detail.propzar= propzar
        
    supervisor_detail.save()
    supervisor_detail.client_form.formclint.save()
    
            
    Notification(title='Project (ID: {})'.format(supervisor_detail.client_form.formclint.id_project),
    description='Thank you for increasing the funds. You resubmitted the proposal successfully. For more information, go to your dashboard.', target=supervisor_detail.supervisor,
    link='').save()
    
    e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, ) 
    e_content = "Dear {} \nHello\nHope you are going well. \nThank you for increasing the funds. You resubmitted the proposal successfully. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(supervisor_detail.supervisor.get_full_name(), supervisor_detail.client_form.expert.researchrole.expert_email_address)
    e_destination = user.email
    send_new_email(e_subject,e_content,e_destination)
    

    Notification(title='Project (ID: {})'.format(supervisor_detail.client_form.formclint.id_project),
    description='The supervisor resubmitted the proposal. Go to your dashboard and proceed with it.', target=supervisor_detail.client_form.expert,
    link='').save()
    
    e_subject ="TECVICO Project (Project ID: {})".format(supervisor_detail.client_form.formclint.id_project, ) 
    e_content = "Dear {} \nHello\nHope you are going well. \nThe supervisor resubmitted the proposal. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(supervisor_detail.client_form.expert.get_full_name())
    e_destination = supervisor_detail.client_form.expert.researchrole.expert_email_address
    send_new_email(e_subject,e_content,e_destination)


def withdraw_project(request):
    if request.method == 'POST':
        reason = request.POST.get("reason")
        position = request.POST.get("position")
        obj_id = int(request.POST.get("obj_id"))
        obj_supervisor = IndustryExpertForSupervisor.objects.get(id=obj_id)
        
        if position == 'main-supervisor':
            obj_supervisor.text = reason
            obj_supervisor.status = 'withdrew'
            obj_supervisor.client_form.formclint.status = 'withdrew'
            obj_supervisor.client_form.formclint.rejected_date = timezone.now()
            obj_supervisor.client_form.status = 'h'
            obj_supervisor.client_form.formclint.user.memberprofile.balance += obj_supervisor.client_form.formclint.fund
            obj_supervisor.client_form.formclint.user.memberprofile.save()
            obj_supervisor.client_form.formclint.save()
            obj_supervisor.client_form.save()
            obj_supervisor.save()
            create_obj_tracing = Tracing.objects.create(
                position='Client', user=request.user, status="The supervisor withdrew", event_date=timezone.now(), tracing_project=obj_supervisor.client_form.formclint)

            Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
            description='The supervisor withdrew to resubmit the proposal. For more information, go to your dashboard.', target=obj_supervisor.client_form.expert,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe supervisor withdrew to resubmit the proposal. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_supervisor.client_form.expert.get_full_name())
            e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            # supervisor
            Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
            description='You withdrew to resubmit the proposal. For more information, go to your dashboard.', target=request.user,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYou withdrew to resubmit the proposal. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through projec@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(request.user.get_full_name())
            e_destination = request.user.email
            send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request,'You withdrew to resubmit the proposal.')
            return redirect("dashboard-myprojects-reserach")

        if position == 'supervisor':
            obj_supervisor.text = reason
            obj_supervisor.status = 'withdrew'
            obj_supervisor.save()
            
            
            create_obj_tracing = Tracing.objects.create(
                position='Supervisor', user=request.user, status="The supervisor withdrew", event_date=timezone.now(), tracing_supervisor=obj_supervisor)
            

            Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
            description='The supervisor withdrew to resubmit the proposal for the project. For more information, go to your dashboard.', target=obj_supervisor.client_form.expert,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nThe supervisor withdrew to resubmit the proposal for the project. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_supervisor.client_form.expert.get_full_name())
            e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            # supervisor
            Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
            description='You withdrew to resubmit the proposal. For more information, go to your dashboard.', target=request.user,
            link='').save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYou withdrew to resubmit the proposal. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through projec@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(request.user.get_full_name())
            e_destination = request.user.email
            send_new_email(e_subject,e_content,e_destination)
            
            messages.error(request,'You withdrew to resubmit the proposal.')
            return redirect("dashboard-myprojects-reserach")

            
            
#detail reject supervisor
class SupervisoeRejectDetail(LoginRequiredMixin, SecuritySupervisorDetail, DetailView):
    template_name = 'industry/supervisor/supervisor-reject-detail.html'
    def get_object(self):
        pk = self.kwargs.get('pk')
        project = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
        project.is_new_reject + 1
        project.save()
        return project



@login_required
def delete_supervisor(request):
    id_supervisor = int(request.POST.get('id_supervisor'))
    
    
    
    obj_supervisor = IndustryExpertForSupervisor.objects.get(pk=id_supervisor)
    obj_supervisor.deleted = True
    obj_supervisor.save()
    
    
    
    return redirect("dashboard-myprojects-reserach")

# #supervisor accept project form director
# class SupervisorDetailContract(LoginRequiredMixin, SecuritySupervisor, DetailView):
#     template_name = 'industry/supervisor/supervisor-see-send-contract.html'
#     def get_object(self):
#         global pk
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(IndustryExpertForSupervisor, pk=pk)
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['reviewer'] = IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk)
#         return context

def supervisor_detail_contract(request, pk):
    template_name = 'industry/supervisor/supervisor-see-send-contract.html'
    obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    if obj_supervisor.status == 't' or obj_supervisor.status == 'reject_contract' and obj_supervisor.supervisor == request.user:

        context = {
            'object': obj_supervisor,
            'reviewer': IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk),
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")

#supervisor accept project form director see total score
# class SupervisorDetailContractTotal(LoginRequiredMixin, SecuritySupervisor, DetailView):
#     template_name = 'industry/supervisor/supervisor-see-send-contract-total.html'
#     def get_object(self):
#         global pk
#         pk = self.kwargs.get('pk')
#         return get_object_or_404(IndustryExpertForSupervisor, pk=pk)
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['reviewer'] = IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk)
#         return context

def supervisor_detail_contract_total(request, pk):
    template_name = 'industry/supervisor/supervisor-see-send-contract-total.html'
    obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)

    if obj_supervisor.status == 't' or obj_supervisor.status == 'reject_contract' and obj_supervisor.supervisor == request.user:

        context = {
            'object': obj_supervisor,
            'reviewer': IndustryReviewer.objects.filter(status='e', object_supervisor_id=pk),
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")


#send contract from supervisor
@login_required
def supervisor_send_contract(request, pk):
    sup = IndustryExpertForSupervisor.objects.get(pk=pk)
    if sup.status == 't' or sup.status == 'reject_contract' and request.user.memberprofile.position == 'Supervisor' and  sup.supervisor == request.user:
        value = sup.client_form.valeu
        total = value + 3000

        supervisor_share = 50 / 100
        supervisor_importance_value = 100
        if sup.client_form.formclint.main_supervisor and sup.client_form.formclint.fund >= 1500:
            value_supervisor = 0
        else:
            value_supervisor = calculate_ResponsiveFee(sup.client_form.formclint.fund, sup.client_form.valeu)
            value_supervisor = value_supervisor[3]
        
        form = FormSupervisorSendContract(request.POST,  request.FILES, initial={"status": sup.status, "contract_supervisor": sup.contract_supervisor,})
        if form.is_valid():
            status = form.cleaned_data.get("status")
            contract_supervisor = form.cleaned_data.get("contract_supervisor")
            
            sup.contract_supervisor= contract_supervisor
            sup.save()
    
            if sup.status != 'reject_contract':
                if sup.client_form.formclint.main_supervisor and sup.client_form.formclint.fund != 0:
                    if sup.client_form.formclint.fund >= 2000:
                        return PaymentProtocol(request, 'P', sup.client_form.formclint, sup.client_form.formclint.fund, action='send-contract - {}'.format(sup.pk))
                        view_value = sup.client_form.formclint.fund
                    else:
                        return PaymentProtocol(request, 'P', sup.client_form.formclint, sup.client_form.formclint.fund + value_supervisor, action='send-contract - {}'.format(sup.pk))
                        view_value = sup.client_form.formclint.fund + value_supervisor
                else:
                    return PaymentProtocol(request, 'P', sup.client_form.formclint, value_supervisor, action='send-contract - {}'.format(sup.pk))
                    view_value = value_supervisor
            else:
                Notification(title='Project (ID: {})'.format(sup.client_form.formclint.id_project), 
                    description='Your revised contract has been sent successfully. For more information, go to your dashboard.', target=sup.supervisor, 
                    link=reverse('industry:industry-expert-contract', args=[sup.pk])).save()
                
                e_subject ="TECVICO Project (Project ID: {})".format(sup.client_form.formclint.id_project, )
                e_content = "Dear {} \nHello\nHope you are going well.\n Your revised contract has been sent successfully. For more information, go to your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {} \n\nThank you \nBest regards \nTECVICO Corp.".format(sup.supervisor.get_full_name(), sup.client_form.expert.researchrole.expert_email_address)
                e_destination = sup.supervisor.email
                send_new_email(e_subject,e_content,e_destination)


            if sup.client_form.formclint.main_supervisor:
                sup.client_form.formclint.follow_project = 'p_main_contract_sent_to_expert'
                create_obj_tracing = Tracing.objects.create(
                    position='Client', user=request.user, status="The Client sent the resubmitted contract", event_date=timezone.now(), tracing_project=sup.client_form.formclint)

            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Supervisor', user=request.user, status="The supervisor resubmitted the revised contract", event_date=timezone.now(), tracing_project=sup.client_form.formclint)

            sup.client_form.formclint.save()
            
            sup.status= 'g'
            sup.save()
            
            e_subject ="TECVICO Project (Project ID: {})".format(sup.client_form.formclint.id_project, )
            e_content ="Dear {} \nHello\nHope you are going well. \n A supervisor signed and sent a contact. Please go your dashboard and proceed with it.\nTitle: “{}“ \nSubmitted date: “{}”. \nPlease go to your dashboard and observe it. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards \n TECVICO Corp.".format(sup.client_form.expert.get_full_name(), sup.client_form.formclint.title, date.today())
            e_destination = sup.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            
                    
            messages.success(request,'The signed contract has been sent successfully.')
            return redirect("dashboard-myprojects-reserach")



        if sup.client_form.formclint.main_supervisor and sup.client_form.formclint.fund != 0:
            if sup.client_form.formclint.fund >= 2000:
                view_value = sup.client_form.formclint.fund
            else:
                view_value = sup.client_form.formclint.fund + value_supervisor
        else:
            view_value = value_supervisor

            
        context = {
            "form": form,
            'object': sup,
            'view_value': view_value
        }

        return render(request, 'industry/supervisor/supervisor-send-contract-from-supervisor.html', context)
    else:
        raise Http404("You can't see this page.")
        
        
        
def again_supervisor_send_contract(user, pk):
    sup = IndustryExpertForSupervisor.objects.get(pk=pk)
    
    if sup.client_form.formclint.main_supervisor:
        sup.client_form.formclint.follow_project = 'p_main_contract_sent_to_expert'

        create_obj_tracing = Tracing.objects.create(
            position='Client', user=user, status="The Client sent the signed contract", event_date=timezone.now(), tracing_project=sup.client_form.formclint)

        create_obj_tracing = Tracing.objects.create(
            position='You', user=user, status="You sent the signed contract", event_date=timezone.now(), tracking_client=sup.client_form.formclint)

    else:
        create_obj_tracing = Tracing.objects.create(
            position='Supervisor', user=user, status="The Supervisor sent the submitted signed contract", event_date=timezone.now(), tracing_supervisor=sup)
            
        create_obj_tracing = Tracing.objects.create(
            position='You', user=user, status="You sent the submitted signed contract", event_date=timezone.now(), tracking_supervisor=sup)


    sup.client_form.formclint.save()

                
    if sup.status == 'reject_contract':
        Notification(title='Project (ID: {})'.format(sup.client_form.formclint.id_project), 
            description='Your revised contract has been sent successfully. For more information, go to your dashboard.', target=sup.supervisor, 
            link=reverse('industry:industry-expert-contract', args=[sup.pk])).save()
        
        e_subject ="TECVICO Project (Project ID: {})".format(sup.client_form.formclint.id_project, )
        e_content = "Dear {} \nHello\nHope you are going well.\n Your revised contract has been sent successfully. For more information, go to your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(sup.supervisor.get_full_name(), sup.client_form.expert.researchrole.expert_email_address)
        e_destination = sup.supervisor.email
        send_new_email(e_subject,e_content,e_destination)
    else:

        Notification(title='Project (ID: {})'.format(sup.client_form.formclint.id_project), 
            description='Your signed contract has been sent successfully. For more information, go to your dashboard.', target=sup.supervisor, 
            link=reverse('industry:industry-expert-contract', args=[sup.pk])).save()
        
        e_subject ="TECVICO Project (Project ID: {})".format(sup.client_form.formclint.id_project, )
        e_content = "Dear {} \nHello\nHope you are going well.\n Your signed contract has been sent successfully. For more information, go to your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(sup.supervisor.get_full_name(), sup.client_form.expert.researchrole.expert_email_address)
        e_destination = sup.supervisor.email
        send_new_email(e_subject,e_content,e_destination)

    sup.status= 'g'
    sup.save()
    
    e_subject ="TECVICO Project (Project ID: {})".format(sup.client_form.formclint.id_project, )
    e_content ="Dear {} \nHello\nHope you are going well. \n A supervisor signed and sent a contract. Please go to your dashboard and proceed with it.\nTitle: “{}“ \nSubmitted date: “{}”. \nPlease go to your dashboard and observe it. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards \n TECVICO Corp.".format(sup.client_form.expert.get_full_name(), sup.client_form.formclint.title, date.today())
    e_destination = sup.client_form.expert.researchrole.expert_email_address
    send_new_email(e_subject,e_content,e_destination)



@login_required
def send_form_adverstiment(request, pk):
    sup = IndustryExpertForSupervisor.objects.get(pk=pk)
    if sup.status == 't' and sup.supervisor == request.user:

        form = FormAdvestiment(request.POST,  request.FILES, initial={"grade": sup.grade, 
            "skills_required": sup.skills_required, "project_ponsored": sup.project_ponsored, 
            "informative_bullets": sup.informative_bullets, "social_platforms": sup.social_platforms, 
            "fruitful_countries": sup.fruitful_countries, "motivating_keywords": sup.motivating_keywords, 
            "upload_pictures": sup.upload_pictures, "benefit_of_members": sup.benefit_of_members,
            "supervisor_information": sup.supervisor_information})
        if form.is_valid():
            grade = form.cleaned_data.get("grade")
            skills_required = form.cleaned_data.get("skills_required")
            project_ponsored = form.cleaned_data.get("project_ponsored")
            informative_bullets = form.cleaned_data.get("informative_bullets")
            social_platforms = form.cleaned_data.get("social_platforms")
            fruitful_countries = form.cleaned_data.get("fruitful_countries")
            motivating_keywords = form.cleaned_data.get("motivating_keywords")
            upload_pictures = form.cleaned_data.get("upload_pictures")
            benefit_of_members = form.cleaned_data.get("benefit_of_members")
            supervisor_information = form.cleaned_data.get("supervisor_information")
            
            sup.grade = grade
            sup.skills_required = skills_required
            sup.project_ponsored = project_ponsored
            sup.informative_bullets = informative_bullets
            sup.social_platforms = social_platforms
            sup.fruitful_countries = fruitful_countries
            sup.motivating_keywords = motivating_keywords
            sup.upload_pictures = upload_pictures
            sup.benefit_of_members = benefit_of_members
            sup.supervisor_information = supervisor_information

            sup.save()
            messages.success(request,'The advertisement form has been completed successfully.')
            return redirect("industry:industry-time-programming", sup.pk)
        context = {
            "form": form,
            'sup': sup
        }

        return render(request, 'industry/supervisor/supervisor-create-form-ad.html', context)
    else:
        raise Http404("You can't see this page.")


@login_required
def create_time_programming(request, pk):
    form_client = IndustryExpertForSupervisor.objects.get(pk=pk)
    if form_client.status == 't' or form_client.status == 'reject_contract' and form_client.supervisor == request.user:
    
        if request.method == 'POST':
            topic = request.POST.get('title')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            TimeProgramming.objects.create(sub=form_client, topic=topic, start_date=start_date, end_date=end_date)
            messages.success(request,'The WBS has been saved successfully')

        context = {
            # "form": form,
            "prog": form_client.time_programmins.all(),
            "prog_count": form_client.time_programmins.all().count(),
            "form_client": form_client,
            "prog_count": form_client.time_programmins.filter(sub=form_client).count(),
            "date": date.today(),
        }

        return render(request, 'industry/supervisor/supervisor-create-time-programming.html', context)

    else:
        raise Http404("You can't see this page.")


@login_required
def deletetimeprogramming(request, pk):
    obj = get_object_or_404(TimeProgramming, pk=pk)
    if request.user.is_superuser or request.user.memberprofile.position == 'Supervisor' and  obj.sub.supervisor == request.user \
    or request.user.researchrole.director == True :

        if request.method =="POST":
            obj.delete()

            return redirect('industry:industry-time-programming', obj.sub.pk)
    
        context ={
            'obj' : get_object_or_404(TimeProgramming, pk=pk)
        }

        return render(request, "industry/supervisor/supervisor-delete-time-programming.html", context)
    else:
        raise Http404("You can't see this page.")

    
@login_required
def delete_time_programming_project(request, pk):
    obj = get_object_or_404(TimeProgramming, pk=pk)
    if request.user.memberprofile.position == 'Supervisor' and  obj.sub.supervisor == request.user \
    or request.user.researchrole.director == True or request.user.is_superuser:

        if request.method =="POST":
            obj.delete()

            return redirect('industry:industry-view-add-time-programming', obj.sub.pk)
    
        context ={
            'obj' : get_object_or_404(TimeProgramming, pk=pk)
        }

        return render(request, "industry/supervisor/supervisor-delete-time-programming.html", context)
    else:
        raise Http404("You can't see this page.")
    
    
def view_adverstiment(request, pk):
    sup = IndustryExpertForSupervisor.objects.get(pk=pk)
    form = FormViewAdvestiment(request.POST,  request.FILES, initial={"grade": sup.grade, 
        "skills_required": sup.skills_required, "project_ponsored": sup.project_ponsored, 
        "informative_bullets": sup.informative_bullets, "social_platforms": sup.social_platforms, 
        "fruitful_countries": sup.fruitful_countries, "motivating_keywords": sup.motivating_keywords, 
        "upload_pictures": sup.upload_pictures, "benefit_of_members": sup.benefit_of_members, 
        "title": sup.client_form.formclint.title, "start_date": sup.client_form.formclint.start_date, 
        "end_date": sup.client_form.formclint.end_date, "email": sup.supervisor.email, 
        "phone": sup.supervisor.memberprofile.phone, 'supervisor_information': sup.supervisor_information})
    if form.is_valid():
        title = form.cleaned_data.get("title")
        start_date = form.cleaned_data.get("start_date")
        end_date = form.cleaned_data.get("end_date")
        email = form.cleaned_data.get("email")
        phone = form.cleaned_data.get("phone")

        grade = form.cleaned_data.get("grade")
        skills_required = form.cleaned_data.get("skills_required")
        project_ponsored = form.cleaned_data.get("project_ponsored")
        informative_bullets = form.cleaned_data.get("informative_bullets")
        social_platforms = form.cleaned_data.get("social_platforms")
        fruitful_countries = form.cleaned_data.get("fruitful_countries")
        motivating_keywords = form.cleaned_data.get("motivating_keywords")
        upload_pictures = form.cleaned_data.get("upload_pictures")
        benefit_of_members = form.cleaned_data.get("benefit_of_members")
        supervisor_information = form.cleaned_data.get("supervisor_information")
        
        sup.grade = grade
        sup.skills_required = skills_required
        sup.project_ponsored = project_ponsored
        sup.informative_bullets = informative_bullets
        sup.social_platforms = social_platforms
        sup.fruitful_countries = fruitful_countries
        sup.motivating_keywords = motivating_keywords
        sup.upload_pictures = upload_pictures
        sup.benefit_of_members = benefit_of_members
    context = {
        "form": form,
        'sup': sup,
        "prog": sup.time_programmins.all(),
    }

    return render(request, 'industry/supervisor/supervisor-veiw-form-ad.html', context)
#------------Reviewer------------#

@login_required

@login_required
def reviewer_list(request):
    template_name = 'industry/reviewer/reviewer-list.html'

    context = {
        'count_project_proposal': IndustryReviewer.objects.filter(status__in=['n', 'a', 'revise_by_expert', 'revise_by_director'], reviewer=request.user,).count(),
        'count_project_project': IndustryReviewer.objects.filter(status__in=['new_project', 'accept_project', 'revise_by_expert_p', 'revise_by_director_p'], reviewer=request.user,).count(),

    }

    return render(request, template_name, context)
    
@login_required
def reviewer_proposal_list(request):
    template_name = 'industry/reviewer/reviewer-proposal-list.html'


    context = {
        'object_list': IndustryReviewer.objects.filter(status='n', reviewer=request.user, ).order_by("-create"),
        'reviewer_request_count': IndustryReviewer.objects.filter(status='n', reviewer=request.user,).order_by("-create").count(),

        'reviewer_project': IndustryReviewer.objects.filter(status='a', reviewer=request.user,).order_by("-create"),
        'reviewer_project_count': IndustryReviewer.objects.filter(status='a', reviewer=request.user,).order_by("-create").count(),

        'reviewer_revised': IndustryReviewer.objects.filter(status__in=['revise_by_expert', 'revise_by_director'], reviewer=request.user,).order_by("-create"),
        'reviewer_revised_count': IndustryReviewer.objects.filter(status__in=['revise_by_expert', 'revise_by_director'], reviewer=request.user,).order_by("-create").count(),

        'reviewer_evaluted': IndustryReviewer.objects.filter(deleted=False, status__in=['n', 'a', 'r', 's', 'breach_of_promis_p', 'e', 'revise_by_expert', 'revise_by_director', 'cancel_by_expert', 'automatically_cancel'], reviewer=request.user,).order_by("-create"),
        'reviewer_evaluted_count': IndustryReviewer.objects.filter(deleted=False, status__in=['n', 'a', 'r', 's', 'breach_of_promis_p', 'e', 'revise_by_expert', 'revise_by_director'], reviewer=request.user,).order_by("-create").count(),
    }

    return render(request, template_name, context)


@login_required
def reviewer_project_list(request):
    template_name = 'industry/reviewer/reviewer-project-list.html'

    context = {
        'object_list': IndustryReviewer.objects.filter(status='new_project', reviewer=request.user, ).order_by("-create"),
        'reviewer_request_count': IndustryReviewer.objects.filter(status='new_project', reviewer=request.user,).order_by("-create").count(),

        'reviewer_project': IndustryReviewer.objects.filter(status='accept_project', reviewer=request.user,).order_by("-create"),
        'reviewer_project_count': IndustryReviewer.objects.filter(status='accept_project', reviewer=request.user,).order_by("-create").count(),

        'reviewer_revised': IndustryReviewer.objects.filter(status__in=['revise_by_expert_p', 'revise_by_director_p'], reviewer=request.user,).order_by("-create"),
        'reviewer_revised_count': IndustryReviewer.objects.filter(status__in=['revise_by_expert_p', 'revise_by_director_p'], reviewer=request.user,).order_by("-create").count(),

        'reviewer_evaluted': IndustryReviewer.objects.filter(status__in=['accept_project', 'new_project', 'reject_project', 'send_director_project', 'not_see_project', 'breach_of_promis', 'revise_by_expert_p', 'revise_by_director_p'], deleted=False, reviewer=request.user,).order_by("-create"),
        'reviewer_evaluted_count': IndustryReviewer.objects.filter(status__in=['accept_project', 'new_project', 'reject_project', 'send_director_project', 'not_see_project', 'breach_of_promis', 'revise_by_expert_p', 'revise_by_director_p'], deleted=False, reviewer=request.user,).order_by("-create").count(),
    }

    return render(request, template_name, context)
# Detail Review

@login_required
def reviewer_detail(request, pk):
    template_name = 'industry/reviewer/reviewer-detail.html'
    review_detail = get_object_or_404(IndustryReviewer, pk=pk)
    if request.user.is_superuser or review_detail.reviewer == request.user and request.user.researchrole.reviewer == True \
        or request.user.researchrole.director == True :


        form_accept = FormStatus(request.POST,  request.FILES, initial={"status": review_detail.status,})
        if form_accept.is_valid():
            status = form_accept.cleaned_data.get("status")
            
            date = review_detail.create + timedelta(7)
            review_detail.status= 'a'
            review_detail.event_date = timezone.now()
            review_detail.object_supervisor.status_review= 'Under review'
            review_detail.deadline = timezone.now() + timedelta(7)
            review_detail.date= date
            review_detail.save()
            review_detail.object_supervisor.save()
            
            e_subject = "TECVICO Project (Project ID: {})".format(review_detail.object_supervisor.client_form.formclint.id_project, )  
            e_content ="Dear {} \nHello\nHope you are going well. \nTECVICO writes this letter to thank you for approving the review request, you are given one week by {} (Coordinated Universal Time (UTC)) to send the evaluation. \nIf you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you\nSincerely\nTECVICO Corp.".format(review_detail.reviewer.get_full_name(), review_detail.deadline.strftime('%Y/%m/%d %H:%M'), review_detail.object_supervisor.client_form.expert.researchrole.expert_email_address)
            e_destination = review_detail.reviewer.email
            send_new_email(e_subject,e_content,e_destination)

            
            e_subject ="TECVICO Project (Project ID: {})".format(review_detail.object_supervisor.client_form.formclint.id_project, )  
            e_content ="Dear {} \nHello\nHope you are going well. \nThe reviewer, {}, has approved the review request. For more information, go to your dashboard. \nIf you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nSincerely\nTECVICO Corp.".format(review_detail.object_supervisor.client_form.expert.get_full_name(), review_detail.reviewer.get_full_name())
            e_destination = review_detail.object_supervisor.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
			
            if review_detail.object_supervisor.client_form.formclint.main_supervisor :
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer approved the proposal review request", event_date=timezone.now(), tracing_project=review_detail.object_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer approved the proposal review request", event_date=timezone.now(), tracing_supervisor=review_detail.object_supervisor)

            create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer approved the proposal review request", event_date=timezone.now(), tracing_reviewer=review_detail)

            messages.success(request,'You have approved the review request.')
            return redirect("industry:industry-reviewer-list")


        form_reject = DeclineReviewerForm(request.POST,  request.FILES, initial={"status_r": review_detail.status,})
        if form_reject.is_valid():
            status_r = form_reject.cleaned_data.get("status_r")
            comment = form_reject.cleaned_data.get("comment")
            review_detail.object_supervisor.status = 'v'
            review_detail.event_date = timezone.now()
            review_detail.object_supervisor.status_review= 'The reviewer declined the request'
            review_detail.object_supervisor.save()
            review_detail.object_supervisor.client_form.status = 'review'
            review_detail.object_supervisor.client_form.save()
            review_detail.status= 'r'
            review_detail.text= comment
            review_detail.save()
            
            review_detail.reviewer.researchrole.count_rejected_reviewer += 1 
            review_detail.reviewer.researchrole.save()
            


            if review_detail.object_supervisor.client_form.formclint.main_supervisor :
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer declined the proposal review request", event_date=timezone.now(), tracing_project=review_detail.object_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer declined the proposal review request", event_date=timezone.now(), tracing_supervisor=review_detail.object_supervisor)


            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=review_detail.reviewer, status="The reviewer declined the proposal review request", event_date=timezone.now(), tracing_reviewer=review_detail)

            
            e_subject ="TECVICO Project (Project ID: {})".format(review_detail.object_supervisor.client_form.formclint.id_project, ) 
            e_content ="Dear {} \nHello\nHope you are going well.\n The reviewer, namely {}, declined to review the proposal. \nPlease go to your dashboard and replace this reviewer with another one. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards\nTECVICO Corp.".format(review_detail.object_supervisor.client_form.expert.get_full_name(), review_detail.reviewer.get_full_name(), review_detail.reviewer.get_full_name())
            e_destination = review_detail.object_supervisor.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            
            
            messages.error(request,'You declined the review request.')
            return redirect("industry:industry-reviewer-list")

        form_delete = DeleteProjectReviewer(request.POST,  request.FILES, )
        if form_delete.is_valid():
            status_delete = form_delete.cleaned_data.get("status_delete")
            
            review_detail.deleted = True
            review_detail.save()
            messages.error(request,'You deleted the project.')
            return redirect("industry:industry-reviewer-list")

        context = {
            'object': review_detail,
            'form_accept': form_accept,
            'form_reject': form_reject,
            'form_delete': form_delete,
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")
        


@login_required
def reviewer_project_detail(request, pk):
    roles = ResearchRole.objects.filter(director=True)
    template_name = 'industry/reviewer/reviewer-project-detail.html'
    review_detail = get_object_or_404(IndustryReviewer, pk=pk)
    if request.user.is_superuser or review_detail.reviewer == request.user and request.user.researchrole.reviewer == True \
        or request.user.researchrole.director == True :


        form_accept = FormStatus(request.POST,  request.FILES, )
        if form_accept.is_valid():
            status = form_accept.cleaned_data.get("status")
            date = review_detail.create + timedelta(7)
            deadline = timezone.now() + timedelta(7)
            review_detail.status= 'accept_project'
            review_detail.date= date
            review_detail.deadline = deadline
            review_detail.event_date = timezone.now()
            review_detail.save()


            
            e_subject = "TECVICO Project (Project ID: {})".format(review_detail.object_expert.formclint.id_project, )  
            e_content ="Dear {} \nHello\nHope you are going well. \nTECVICO writes this letter to thank you for approving the review request, you are given one week by {} (Coordinated Universal Time (UTC)) to send the evaluation. \nIf you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you\nSincerely\nTECVICO Corp.".format(review_detail.reviewer.get_full_name(), review_detail.deadline.strftime('%Y/%m/%d %H:%M'), review_detail.object_expert.expert.researchrole.expert_email_address)
            e_destination = review_detail.reviewer.email
            send_new_email(e_subject,e_content,e_destination)

            
            e_subject ="TECVICO Project (Project ID: {})".format(review_detail.object_expert.formclint.id_project, )  
            e_content ="Dear {} \nHello\nHope you are going well. \nThe reviewer, {}, has approved the project review request. For more information, go to your dashboard. \nIf you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nSincerely\nTECVICO Corp.".format(review_detail.object_expert.expert.get_full_name(), review_detail.reviewer.get_full_name())
            e_destination = review_detail.object_expert.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
        
        
            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=review_detail.reviewer, status="The reviewer approved the project review request", event_date=timezone.now(), tracing_project=review_detail.object_expert.formclint
                )

            create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer approved the project review request", event_date=timezone.now(), tracing_reviewer=review_detail)


            messages.success(request,'You have approved the review request.')
            return redirect("industry:research-reviewer-list-project")


        form_reject = RejectReviewForm(request.POST,  request.FILES, )
        if form_reject.is_valid():
            status_r = form_reject.cleaned_data.get("status_r")

            review_detail.event_date = timezone.now()
            review_detail.status= 'reject_project'
            review_detail.save()
                
            e_subject ="TECVICO Project (Project ID: {})".format(review_detail.object_expert.formclint.id_project, )
            e_content ="Dear {} \nHello\nHope you are going well.\n The reviewer, namely {}, declined to review the following project:\nTitle: {}\nPlease go to your dashboard and replace this reviewer with another one. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards \nTECVICO Corp.".format(review_detail.object_expert.expert.get_full_name(), review_detail.reviewer.get_full_name(), review_detail.object_expert.formclint.title, )
            e_destination = review_detail.object_expert.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=review_detail.reviewer, status="The reviewer decliend the project review request", event_date=timezone.now(), tracing_project=review_detail.object_expert.formclint
                )

            create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_detail.reviewer, status="The reviewer decliend the project review request", event_date=timezone.now(), tracing_reviewer=review_detail)   
            
            messages.error(request,'You declined the review request.')
            return redirect("industry:research-reviewer-list-project")

        form_delete = DeleteProjectReviewer(request.POST,  request.FILES, )
        if form_delete.is_valid():
            status_delete = form_delete.cleaned_data.get("status_delete")

            review_detail.deleted = True
            review_detail.save()
            messages.error(request,'You deleted the project.')
            return redirect("industry:research-reviewer-list-project")
        context = {
            'object': review_detail,
            'form_accept': form_accept,
            'form_reject': form_reject,
            'form_delete': form_delete,
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")
        



@login_required
def reviewer_send_score_project(request, pk):
    roles = ResearchRole.objects.all()
    review_score = IndustryReviewer.objects.get(pk=pk)
    form = SendScoreReview(request.POST,  request.FILES)
    if form.is_valid():
        score = form.cleaned_data.get("score")
        score_1 = form.cleaned_data.get("score_1")
        score_2 = form.cleaned_data.get("score_2")
        score_3 = form.cleaned_data.get("score_3")
        score_4 = form.cleaned_data.get("score_4")
        score_5 = form.cleaned_data.get("score_5")
        score_6 = form.cleaned_data.get("score_6")
        status = form.cleaned_data.get("status")

        review_score.score = score
        review_score.score_1 = score_1
        review_score.score_2 = score_2
        review_score.score_3 = score_3
        review_score.score_4 = 0
        review_score.score_5 = 0
        review_score.score_6 = 0
        review_score.save()
        
                    
        messages.success(request,'The Project scores saved successfully.')
        return redirect('industry:research-reviewer-project-detail', review_score.pk)
    context = {
        'object': review_score,
        'form': form
    }
    return render(request, 'industry/reviewer/reviewer-send-score_project.html', context)


def reviewer_send_score_director(request):
    if request.method == 'POST':
        roles = ResearchRole.objects.all()

        id_obj = int(request.POST.get('id_obj'))
        comment = request.POST.get('comment')

        review_score = IndustryReviewer.objects.get(id=id_obj)

        review_score.text = comment
    
        review_score.object_expert.formclint.status = 'expert_reviewer'
        review_score.object_expert.formclint.save()
            
        review_score.event_date = timezone.now()
        review_score.status= 'send_director_project'
        review_score.save()
        
                
        if review_score.object_expert:
            
            e_subject ="TECVICO Project (Project ID: {})".format(review_score.object_expert.formclint.id_project, )
            e_content ="Dear {}\nHello\nHope you are going well.\nA reviewer, namely {}, sent the project assessment. Please go to your dashboard and proceed with it.\nTitle: {}\nSubmitted date: {}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.".format(review_score.object_expert.expert.get_full_name(), review_score.reviewer.get_full_name(), review_score.object_expert.formclint.title, date.today())
            e_destination = review_score.object_expert.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            
            e_subject ="TECVICO Project (Project ID: {})".format(review_score.object_expert.formclint.id_project, ) 
            e_content ="Dear {}\nHello\nHope you are going well.\nTECVICO is writing this letter to thank you for assessing this project. Your assessment has been sent successfully.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.".format(request.user.get_full_name(), review_score.object_expert.expert.researchrole.expert_email_address)
            e_destination = request.user.email
            send_new_email(e_subject,e_content,e_destination)


        messages.success(request,'The project has been assessed successfully.')
        return redirect('industry:research-reviewer-list-project')


#Accept Review
@login_required
def accept_project_review(request, pk):
    review = IndustryReviewer.objects.get(pk=pk)
    form = FormStatus(request.POST,  request.FILES, initial={"status": review.status,})
    if form.is_valid():
        status = form.cleaned_data.get("status")
        
        date = review.create + timedelta(7)
        review.status= 'a'
        review.date= date
        review.save()


        return redirect("industry:industry-reviewer-list")
    context = {
        "form": form,
        'review': review
    }

    return render(request, 'industry/reviewer/reviewer-accept.html', context)




@login_required
def reviewer_send_score(request, pk):
    review_score = IndustryReviewer.objects.get(pk=pk)
    form = SendScoreReview(request.POST,  request.FILES)
    if form.is_valid():
        score = form.cleaned_data.get("score")
        score_1 = form.cleaned_data.get("score_1")
        score_2 = form.cleaned_data.get("score_2")
        score_3 = form.cleaned_data.get("score_3")
        score_4 = form.cleaned_data.get("score_4")
        score_5 = form.cleaned_data.get("score_5")
        score_6 = form.cleaned_data.get("score_6")
        # text = form.cleaned_data.get("text")
        status = form.cleaned_data.get("status")

        review_score.score = score
        review_score.score_1 = score_1
        review_score.score_2 = score_2
        review_score.score_3 = score_3
        review_score.score_4 = score_4
        review_score.score_5 = score_5
        review_score.score_6 = score_6
        review_score.save()
        
        
        
        messages.success(request,'The proposal has been assessed successfully and you should send it to the expert.')
        return redirect('industry:industry-reviewer-detail', review_score.pk)
    context = {
        'object': review_score,
        'form': form
    }
    return render(request, 'industry/reviewer/reviewer-send-score.html', context)





def proposal_send_score_score(request):
    if request.method == 'POST':
        roles = ResearchRole.objects.all()

        id_obj = int(request.POST.get('id_obj'))
        comment = request.POST.get('comment')

        review_score = IndustryReviewer.objects.get(id=id_obj)


        if review_score.object_supervisor.client_form.formclint.main_supervisor :
            if review_score.status == "revise_by_expert":
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_score.reviewer, status="The reviewer sent the revised evaluation to the expert", event_date=timezone.now(), tracing_project=review_score.object_supervisor.client_form.formclint)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_score.reviewer, status="The reviewer sent the evaluation to the expert", event_date=timezone.now(), tracing_project=review_score.object_supervisor.client_form.formclint)
        else:
            if review_score.status == "revise_by_expert":
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_score.reviewer, status="The reviewer sent the revised evaluation to the expert", event_date=timezone.now(), tracing_supervisor=review_score.object_supervisor)
            else:
                create_obj_tracing = Tracing.objects.create(
                    position='Reviewer', user=review_score.reviewer, status="The reviewer sent the evaluation to the expert", event_date=timezone.now(), tracing_supervisor=review_score.object_supervisor)        


        if review_score.status == "revise_by_expert":
            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=review_score.reviewer, status="The reviewer sent the revised evaluation to the expert", event_date=timezone.now(), tracing_reviewer=review_score)
        else:
            create_obj_tracing = Tracing.objects.create(
                position='Reviewer', user=review_score.reviewer, status="The reviewer sent the evaluation to the expert", event_date=timezone.now(), tracing_reviewer=review_score)

        review_score.text = comment
        review_score.status= 'e'
        review_score.event_date= timezone.now()
        review_score.object_supervisor.status_review= 'Evaluated'
        review_score.object_supervisor.save()
        review_score.save()
        


        
        e_subject ="TECVICO Project (Project ID: {})".format(review_score.object_supervisor.client_form.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nA reviewer, namely {}, sent the assessment. Please go to your dashboard and proceed with it.\nTitle: {}\nSubmitted date: {}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.".format(review_score.object_supervisor.client_form.expert.get_full_name(), review_score.reviewer.get_full_name(), review_score.object_supervisor.client_form.formclint.title, date.today())
        e_destination = review_score.object_supervisor.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)
        

        
        e_subject ="TECVICO Project (Project ID: {})".format(review_score.object_supervisor.client_form.formclint.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\nTECVICO is writing this letter to thank you for assessing the proposal. Your assessment has been submitted successfully.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.".format(request.user.get_full_name(), review_score.object_supervisor.client_form.expert.researchrole.expert_email_address)
        e_destination = review_score.reviewer.email
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request,'You have sent the assessment to the expert successfully.')
        return redirect('industry:industry-reviewer-list')


#------------Project------------#




@login_required
def applyproject(request, pk):
    form_client = get_object_or_404(ResearchProject , pk=pk)
    request_p = RequestUserForProject.objects.all()
    if request.user.is_authenticated:
        create_user_footprint = UserFootprint.objects.create(user=request.user, url=request.path)
    if request.method == 'POST':
        if user_has_memberprofile(request.user):
            if request.user.memberprofile.about_me is None:  # user has to complete his/her profile to see this page
                messages.error(request,'Error: You cannot apply for this project because your profile is incomplete. Please go to your ptofile and complete it.')
                return HttpResponseRedirect(request.path_info)
            else:
                form = ApplyProjectForm(request.POST, request.FILES)
                if form.is_valid():
                    status = form.cleaned_data.get("status")
                    position = form.cleaned_data.get("position")
                    member = form.cleaned_data.get("member")
                    mentor = form.cleaned_data.get("mentor")
                    learner = form.cleaned_data.get("learner")
                    supervisor = form.cleaned_data.get("supervisor")
                    
                    if position == 'not-mainsupervisor':
                        obj_client = form_client.proposal_supervisor.formclint
                    else:
                        obj_client = form_client.project.client_form.formclint
                        
                    new_from = RequestUserForProject.objects.create(
                        project_request=form_client, user=request.user, status='not-pay', 
                        supervisor=supervisor, mentor=mentor, member=member, learner=learner)
                        
                    if form_client.project.client_form.formclint.fund == 0:          
                                            
                        obj_request = new_from              
                        obj_request.status = 'request'
                        obj_request.save()
                        
                        if obj_request.supervisor == True:
                            supervisor_email = 'advisor, '
                        else:
                            supervisor_email=''
                            
                        if obj_request.mentor == True:
                            mentor_email = 'mentor, '
                        else:
                            mentor_email=''
                            
                        if obj_request.member == True:
                            member_email = 'member, '
                        else:
                            member_email=''
                            
                        if obj_request.learner == True:
                            learner_email = 'learner'
                        else:
                            learner_email=''
                    
                        if obj_request.project_request.project:
                            create_obj_tracing = Tracing.objects.create(
                                position='Applicant', user=request.user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project_phase_2=obj_request.project_request)\
                                
                            create_obj_tracing = Tracing.objects.create(
                                position='Applicant', user=request.user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_main_supervisor=obj_request.project_request)
                            
                            Notification(title='Project (ID: {})'.format(obj_request.project_request.project.client_form.formclint.id_project), 
                                    description='Your request to join this project has been submitted successfully. For more information, go to your dashboard.', target=obj_request.user, 
                                    link='').save()
                                    
                            Notification(title='Project (ID: {})'.format(obj_request.project_request.project.client_form.formclint.id_project), 
                                description='An applicant is interested in joining your project, please go your dashboard and see it.', target=obj_request.project_request.project.supervisor, 
                                link=reverse('industry:industry-project-edit-request-detail', args=[obj_request.pk])).save()
                            
                        
                            e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.project.client_form.formclint.id_project)
                            e_content ="Dear {} \nHello\nHope you are going well.\n  Your request, as {}{}{}{} on this project, has been received successfully. The main supervisor will review your request and send the decision to you soon. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(request.user.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.project.client_form.expert.researchrole.expert_email_address)
                            e_destination = request.user.email
                            send_new_email(e_subject,e_content,e_destination)
                            
                            
                            e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.project.client_form.formclint.id_project)
                            e_content ="Dear {} \nHello\nHope you are going well.\nAn applicant has requested to be as {}{}{}{} on your project. Please go to your dashboard and proceed with it. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_request.project_request.project.supervisor.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.project.client_form.expert.researchrole.expert_email_address)
                            e_destination = obj_request.project_request.project.supervisor.email 
                            send_new_email(e_subject,e_content,e_destination)
                            
                        else:
                            create_obj_tracing = Tracing.objects.create(
                                position='Applicant', user=request.user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project_phase_2=obj_request.project_request)
                                
                            create_obj_tracing = Tracing.objects.create(
                                position='Applicant', user=request.user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project=obj_request.project_request.proposal_supervisor.formclint)
                            
                            Notification(title='Project (ID: {})'.format(obj_request.project_request.proposal_supervisor.formclint.id_project), 
                                    description='Your request to join this project has been submitted successfully. For more information, go to your dashboard.', target=obj_request.user, 
                                    link='').save()
                                    
                        
                            e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.proposal_supervisor.formclint.id_project)
                            e_content ="Dear {} \nHello\nHope you are going well.\n  Your request, as {}{}{}{} on this project, has been received successfully. The main supervisor will review your request and send the decision to you soon. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(request.user.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.proposal_supervisor.expert.researchrole.expert_email_address)
                            e_destination = request.user.email
                            send_new_email(e_subject,e_content,e_destination)
                        
                                
                        messages.success(request,'Your request has been submitted successfully.')
                        
                        return redirect('dashboard-myprojects-reserach')
                                            
                        
                        
                        
                        
                    else:
                        if supervisor == True:
                            return PaymentProtocol(request,'P', obj_client, form_client.value_supervisor, action='apply-applicant - {}'.format(new_from.pk))
    
                        elif mentor == True:
                            return PaymentProtocol(request,'P', obj_client, form_client.value_mentor, action='apply-applicant - {}'.format(new_from.pk))
    
    
                        elif member == True:
                            return PaymentProtocol(request,'P', obj_client, form_client.value_mmber, action='apply-applicant - {}'.format(new_from.pk))
    
    
                        elif learner == True:
                            return PaymentProtocol(request,'P', obj_client, form_client.value_lerner, action='apply-applicant - {}'.format(new_from.pk))
                            
                            
    else:
        form = ApplyProjectForm
    
    requests = RequestUserForProject.objects.filter(status__in=['accept', 'request'], user=request.user, project_request=form_client)
    
    if requests:
        is_request = True
    else:
        is_request = False
    context = {
    "form": form,
    "request_p": request_p,
    'is_request': is_request,
    "form_client": form_client
    }

    return render(request,'industry/project/project-apply.html', context)




def again_applyproject(user, pk):
    obj_request = get_object_or_404(RequestUserForProject, pk=pk)
    
    obj_request.status = 'request'
    obj_request.save()
    
    if obj_request.supervisor == True:
        supervisor_email = 'advisor, '
    else:
        supervisor_email=''
        
    if obj_request.mentor == True:
        mentor_email = 'mentor, '
    else:
        mentor_email=''
        
    if obj_request.member == True:
        member_email = 'member, '
    else:
        member_email=''
        
    if obj_request.learner == True:
        learner_email = 'learner'
    else:
        learner_email=''

    if obj_request.project_request.project:
        create_obj_tracing = Tracing.objects.create(
            position='Applicant', user=user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project_phase_2=obj_request.project_request)\
            
        create_obj_tracing = Tracing.objects.create(
            position='Applicant', user=user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_main_supervisor=obj_request.project_request)
        
        Notification(title='Project (ID: {})'.format(obj_request.project_request.project.client_form.formclint.id_project), 
                description='Your request to join this project has been submitted successfully. For more information, go to your dashboard.', target=obj_request.user, 
                link='').save()
                
        Notification(title='Project (ID: {})'.format(obj_request.project_request.project.client_form.formclint.id_project), 
            description='An applicant is interested in joining your project, please go your dashboard and see it.', target=obj_request.project_request.project.supervisor, 
            link=reverse('industry:industry-project-edit-request-detail', args=[obj_request.pk])).save()
        
    
        e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.project.client_form.formclint.id_project)
        e_content ="Dear {} \nHello\nHope you are going well.\n  Your request, as {}{}{}{} on this project, has been received successfully. The main supervisor will review your request and send the decision to you soon. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(user.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.project.client_form.expert.researchrole.expert_email_address)
        e_destination = user.email
        send_new_email(e_subject,e_content,e_destination)
        
        
        e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.project.client_form.formclint.id_project)
        e_content ="Dear {} \nHello\nHope you are going well.\nAn applicant has requested to be as {}{}{}{} on your project. Please go to your dashboard and proceed with it. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_request.project_request.project.supervisor.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.project.client_form.expert.researchrole.expert_email_address)
        e_destination = obj_request.project_request.project.supervisor.email 
        send_new_email(e_subject,e_content,e_destination)
        
    else:
        create_obj_tracing = Tracing.objects.create(
            position='Applicant', user=user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project_phase_2=obj_request.project_request)
            
        create_obj_tracing = Tracing.objects.create(
            position='Applicant', user=user, status="The applicant applied for {}{}{}{} position(s)".format(supervisor_email, mentor_email, member_email, learner_email), event_date=timezone.now(), tracing_project=obj_request.project_request.proposal_supervisor.formclint)
        
        Notification(title='Project (ID: {})'.format(obj_request.project_request.proposal_supervisor.formclint.id_project), 
                description='Your request to join this project has been submitted successfully. For more information, go to your dashboard.', target=obj_request.user, 
                link='').save()
                
    
        e_subject ="TECVICO Project (Project ID: {})".format(obj_request.project_request.proposal_supervisor.formclint.id_project)
        e_content ="Dear {} \nHello\nHope you are going well.\n  Your request, as {}{}{}{} on this project, has been received successfully. The main supervisor will review your request and send the decision to you soon. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(user.get_full_name(), supervisor_email, mentor_email, member_email, learner_email, obj_request.project_request.proposal_supervisor.expert.researchrole.expert_email_address)
        e_destination = user.email
        send_new_email(e_subject,e_content,e_destination)





# class PageEditProject(LoginRequiredMixin, SecurityProjectEdit, DetailView):
#     template_name = 'industry/project/project-page-edit.html'
#     def get_object(self):
#         pk = self.kwargs.get('pk')
#         global x
#         x = get_object_or_404(ResearchProject, pk=pk)
#         return x
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         if self.request.user.is_superuser or self.request.user.researchrole.director == True:
#             context['count_request_apply'] = RequestUserForProject.objects.filter(status='request', project_request=x, ).count()
#         else:
#             context['count_request_apply'] = RequestUserForProject.objects.filter(status='request', project_request=x, project_request__main_supervisor=self.request.user).count()
#         return context

class EditProjectRequest(LoginRequiredMixin, ListView):
    template_name = 'industry/project/project-edit-request.html'
    def get_queryset(self):
        if self.request.user.is_superuser:
            rpro = RequestUserForProject.objects.filter(project_request=x, status='request',)
            return rpro
        else:
            rpro = RequestUserForProject.objects.filter(project_request=x, status='request', project_request__main_supervisor=self.request.user)
            return rpro
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

@login_required
# def edit_project_request(request, pk):
#     template_name = 'industry/project/project-edit-request.html'
#     obj_request = get_object_or_404(ResearchProject, pk=pk)
    
#     if request.user.is_superuser or request.user.researchrole.director == True:
#         object_list = RequestUserForProject.objects.filter(project_request=obj_request, status='request').order_by("created")
#     else:
#         object_list = RequestUserForProject.objects.filter(project_request=obj_request, status='request', project_request__main_supervisor=request.user).order_by("created")
#     context = {
#         'object_list': object_list,
#     }
#     return render(request, template_name, context)

@login_required
def detail_request_project(request, pk):
    rproject = get_object_or_404(RequestUserForProject, pk=pk)
    form_reject = RejectApplicantForm(request.POST, )
    if form_reject.is_valid():
        status = form_reject.cleaned_data.get("status")
        reason_for_rejection = form_reject.cleaned_data.get("reason_for_rejection")

        rproject.status = 'reject'
        rproject.reason_for_rejection = reason_for_rejection
        rproject.save()
        
        supervisor_name = ''
        mentor_name = ''
        member_name = ''
        learner_name = ''
        if rproject.supervisor == True:
            value_request = rproject.project_request.value_supervisor
            supervisor_name = "advisor, "
            
        elif rproject.mentor == True:
            value_request = rproject.project_request.value_mentor
            mentor_name = "mentor, "
            
        elif rproject.member == True:
            value_request = rproject.project_request.value_mmber
            member_name = "member, "
            
        elif rproject.learner == True:
            value_request = rproject.project_request.value_lerner
            learner_name = "learner"
            
        
        final_value = value_request

        final_balance = rproject.user.memberprofile.balance + final_value
        rproject.user.memberprofile.balance = final_balance
        rproject.user.memberprofile.save()
        


        create_obj_tracing = Tracing.objects.create(
            position='Main-supervisor', user=request.user, status="The Supervisor rejected the applicant`s request ({}) to join the project".format(rproject.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=rproject.project_request)

    
        e_subject ="TECVICO Project (Project ID: {})".format(rproject.project_request.project.client_form.formclint.id_project) 
        e_content ="Dear {}\nHello\n Hope you are going well.\nThank you for your request.\nWith the help of this letter, TECVICO is feeling very sorry to inform you that your request to join this project as {}{}{}{} was rejected. Meanwhile, the responsibility fee has been returned to your account. TECVICO looks forward to seeing you on other project.\nDon’t reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com. \n\nThank you\nSincerely\nTECVICO Corp.".format(rproject.user.get_full_name(), supervisor_name, mentor_name, member_name, learner_name,)
        e_destination = rproject.user.email
        send_new_email(e_subject,e_content,e_destination)
        
        
        
        messages.error(request,'The request was rejected.')
        return redirect("industry:mainsupervisor-detail", rproject.project_request.pk)

    form_accept = ApplyProjectForm(request.POST, initial={
        'status': rproject.status, 'supervisor': rproject.supervisor, 
        'mentor': rproject.mentor, 'member': rproject.member, 
        'learner': rproject.learner, 
        })
    if form_accept.is_valid():

        status = form_accept.cleaned_data.get("status")
        supervisor = form_accept.cleaned_data.get("supervisor")
        mentor = form_accept.cleaned_data.get("mentor")
        member = form_accept.cleaned_data.get("member")
        learner = form_accept.cleaned_data.get("learner")


        rproject.status = 'accept'
        rproject.save()
        
        if supervisor == True:
            new = SuperVizor.objects.create(research=rproject.project_request ,user=rproject.user)
            e_subject ="TECVICO Project (Project ID: {})".format(rproject.project_request.project.client_form.formclint.id_project)
            e_content ="Dear {} \nHello\nHope you are going well\nThank you for your request.\nGood news! Your request has been accepted to join the project as an advisor. Please wait for contract.\nDo not reply to this Email. If you have any concerns or questions, please contact the main supervisor or expert through {}, {}, recpectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(rproject.user.get_full_name(), rproject.project_request.main_supervisor.email, rproject.project_request.project.client_form.expert.researchrole.expert_email_address)
            e_destination = rproject.user.email
            send_new_email(e_subject,e_content,e_destination)

            create_obj_tracing = Tracing.objects.create(
                position='Main-supervisor', user=request.user, status="The Supervisor accepted the applicant`s request ({}) as advisor to join the project".format(rproject.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=rproject.project_request)

            


        if mentor == True:
            new = Mentor.objects.create(research=rproject.project_request ,user=rproject.user)
            e_subject ="TECVICO Project (Project ID: {})".format(rproject.project_request.project.client_form.formclint.id_project) 
            e_content ="Dear {} \nHello\nHope you are going well\nThank you for your request.\nGood news! Your request has been accepted to join the project as a mentor. Please wait for contract.\nDo not reply to this Email. If you have any concerns or questions, please contact the main supervisor or expert through {}, {}, recpectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(rproject.user.get_full_name(), rproject.project_request.main_supervisor.email, rproject.project_request.project.client_form.expert.researchrole.expert_email_address)
            e_destination = rproject.user.email
            send_new_email(e_subject,e_content,e_destination)

            create_obj_tracing = Tracing.objects.create(
                position='Main-supervisor', user=request.user, status="The Supervisor accepted the applicant`s request ({}) as mentor to join the project".format(rproject.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=rproject.project_request)



        if  member == True:
            new = Member.objects.create(research=rproject.project_request ,user=rproject.user)
            e_subject ="TECVICO Project (Project ID: {})".format(rproject.project_request.project.client_form.formclint.id_project) 
            e_content ="Dear {} \nHello\nHope you are going well\nThank you for your request.\nGood news! Your request has been accepted to join the project as a member. Please wait for contract.\nDo not reply to this Email. If you have any concerns or questions, please contact the main supervisor or expert through {}, {}, recpectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(rproject.user.get_full_name(), rproject.project_request.main_supervisor.email, rproject.project_request.project.client_form.expert.researchrole.expert_email_address)
            e_destination = rproject.user.email
            send_new_email(e_subject,e_content,e_destination)

            create_obj_tracing = Tracing.objects.create(
                position='Main-supervisor', user=request.user, status="The Supervisor accepted the applicant`s request ({}) as member to join the project".format(rproject.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=rproject.project_request)

            


        if  learner == True:
            new = Lerner.objects.create(research=rproject.project_request ,user=rproject.user)
            e_subject ="TECVICO Project (Project ID: {})".format(rproject.project_request.project.client_form.formclint.id_project)
            e_content ="Dear {} \nHello\nHope you are going well\nThank you for your request.\nGood news! Your request has been accepted to join the project as a learner. Please wait for contract.\nDo not reply to this Email. If you have any concerns or questions, please contact the main supervisor or expert through {}, {}, recpectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(rproject.user.get_full_name(), rproject.project_request.main_supervisor.email, rproject.project_request.project.client_form.expert.researchrole.expert_email_address)
            e_destination = rproject.user.email
            send_new_email(e_subject,e_content,e_destination)

            create_obj_tracing = Tracing.objects.create(
                position='Main-supervisor', user=request.user, status="The Supervisor accepted the applicant`s request ({}) as learner to join the project".format(rproject.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=rproject.project_request)



        if rproject.supervisor == True:
            value_request = rproject.project_request.value_supervisor

        elif rproject.mentor == True:
            value_request = rproject.project_request.value_mentor

        elif rproject.member == True:
            value_request = rproject.project_request.value_mmber

        elif rproject.learner == True:
            value_request = rproject.project_request.value_lerner



        if supervisor == True:
            value_applicant = rproject.project_request.value_supervisor

        elif mentor == True:
            value_applicant = rproject.project_request.value_mentor

        elif member == True:
            value_applicant = rproject.project_request.value_mmber

        elif learner == True:
            value_applicant = rproject.project_request.value_lerner


        final_value = value_request - value_applicant

        final_balance = rproject.user.memberprofile.balance + final_value
        rproject.user.memberprofile.balance = final_balance
        rproject.user.memberprofile.save()
        
        messages.success(request,'The request has been accepted.')
        return redirect("industry:mainsupervisor-detail", rproject.project_request.pk)




    context = {
        'rp': rproject,
        'form_reject': form_reject,
        'form_accept': form_accept,
        'badges': BadgeRequest.objects.filter(user=rproject.user)
    }

    return render(request, 'industry/project/project-detail-request.html', context)
    
    
@login_required
def applicant_information_remove(request):
    if request.method == 'POST':
        obj_id = int(request.POST.get('obj_id'))
        project_id = int(request.POST.get('project_id'))
        position_user = request.POST.get('position_user')
        reason_rejection = request.POST.get('reason_rejection')

        obj_project = get_object_or_404(ResearchProject, pk=project_id)

        if position_user == 'Advisor':
            obj_applicant = SuperVizor.objects.get(id=obj_id)

        elif position_user == 'Mentor':
            obj_applicant = Mentor.objects.get(id=obj_id)

        elif position_user == 'Member':
            obj_applicant = Member.objects.get(id=obj_id)

        elif position_user == 'Learner':
            obj_applicant = Lerner.objects.get(id=obj_id)

        obj_applicant.status_remove = 'request-remove'
        obj_applicant.reason_rejection = reason_rejection
        obj_applicant.save()


        create_obj_tracing = Tracing.objects.create(
            position='Main supervisor', user=request.user, status="The Supervisor requested to remove the applicant,namely {}, from the project.".format(obj_applicant.user), event_date=timezone.now(), tracing_project_phase_2=obj_project)


        Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
            description='A request to remove a applivant from the project is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
            link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nA request to remove a applivant from the project is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you \nBest regards \nTECVICO Corp.".format(obj_project.project.client_form.expert.get_full_name())
        e_destination = obj_project.project.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request,'Your request of removing the applicant from the preject has been sent successfully.')

        return redirect("industry:mainsupervisor-detail", obj_project.pk)


class DeleteProject(LoginRequiredMixin, SecurityDirector, UpdateView):
    model = ResearchProject
    fields = ['status', ]
    success_url = reverse_lazy('dashboard-projects-page')
    template_name = 'industry/project/project-delete.html'
    
class ListSreach(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'industry/project/project-search-list.html'
    def get_queryset(self):
        search = self.request.GET.get('q')
        
        return ResearchProject.objects.filter(project__client_form__formclint__title__icontains=search)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search'] = self.request.GET.get('q')
        return context
        
        
@login_required
def detail_expert_report(request, pk):
    roles = ResearchRole.objects.filter(director=True)
    expert_report = get_object_or_404(ResearchProject, pk=pk)

    if request.method == 'POST':
        report = request.POST.get("report")

        print('report', expert_report.project.status)

        expert_report.project.report = report
        expert_report.project.status = 'report_d'
        expert_report.project.save()
        print('report', expert_report.project.status)

        # for i in roles:
        #     e_subject = ""
        #     e_content = ""
        #     e_destination = i.user.email
        #     send_new_email(e_subject,e_content,e_destination)

        return redirect('industry:research-expert-manage-project')
    context = {
        'object': expert_report,
        "wbs_list": TimeProgramming.objects.filter(sub=expert_report.project),
        'today': date.today()
    }
    return render(request, 'industry/expert/report/detail.html', context)


@login_required
def create_edit_metting(request):
    if request.method == 'POST':
        position_metting = request.POST.get("position_metting") 
        id_project = request.POST.get("id_project") 

        obj_project = ResearchProject.objects.get(id=id_project)
        supervisors = SuperVizor.objects.filter(research=obj_project)
        mentors = Mentor.objects.filter(research=obj_project)
        members = Member.objects.filter(research=obj_project)
        lerners = Lerner.objects.filter(research=obj_project)


        if position_metting == 'create':
            time_zone = request.POST.get("time_zone") 
            link_meeting = request.POST.get("link_meeting") 
            date_meeting = request.POST.get("date_meeting")
            time_meeting = request.POST.get("time_meeting")


            new_from = ResearchMeeting.objects.create(
                project_research=obj_project, link_meeting=link_meeting, 
                date_meeting=date_meeting, time_meeting=time_meeting, time_zone=time_zone
                )


            # Advisor
            for i in obj_project.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='A new appointment has been set for your project. For more information, go to your dashboard.', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\nA new appointment has been set for your project. For more information, go to your dashboard. \nLink: {} \nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_from.link_meeting, new_from.date_meeting, new_from.time_meeting, new_from.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Mentor
            for i in obj_project.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='A new appointment has been set for your project. For more information, go to your dashboard.', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\nA new appointment has been set for your project. For more information, go to your dashboard. \nLink: {} \nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_from.link_meeting, new_from.date_meeting, new_from.time_meeting, new_from.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Member
            for i in obj_project.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='A new appointment has been set for your project. For more information, go to your dashboard.', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\nA new appointment has been set for your project. For more information, go to your dashboard. \nLink: {} \nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_from.link_meeting, new_from.date_meeting, new_from.time_meeting, new_from.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Learner
            for i in obj_project.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='A new appointment has been set for your project. For more information, go to your dashboard.', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\nA new appointment has been set for your project. For more information, go to your dashboard. \nLink: {} \nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), new_from.link_meeting, new_from.date_meeting, new_from.time_meeting, new_from.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)


            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The Supervisor set a new meeting", event_date=timezone.now(), tracing_project_phase_2=obj_project)

            messages.success(request,'Your meeting has been set successfully.')
        elif position_metting == 'edit':
        # Edit meeting
            id_edit = request.POST.get("id_edit") 
            time_zone = request.POST.get("time_zone") 
            edit_link_meeting = request.POST.get("edit_link_meeting") 
            edit_date_meeting = request.POST.get("edit_date_meeting") 
            edit_time_meeting = request.POST.get("edit_time_meeting") 

            object_edit_mertting = ResearchMeeting.objects.get(id=id_edit)

            object_edit_mertting.time_zone = time_zone
            object_edit_mertting.link_meeting = edit_link_meeting
            object_edit_mertting.date_meeting = edit_date_meeting
            object_edit_mertting.time_meeting = edit_time_meeting
            object_edit_mertting.save()




            # Advisor
            for i in obj_project.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\n The meeting information has been updated. For more information, go to your dashboard.\nLink: {}\nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(),object_edit_mertting.link_meeting, object_edit_mertting.date_meeting, object_edit_mertting.time_meeting, object_edit_mertting.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Mentor
            for i in obj_project.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\n The meeting information has been updated. For more information, go to your dashboard.\nLink: {}\nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(),object_edit_mertting.link_meeting, object_edit_mertting.date_meeting, object_edit_mertting.time_meeting, object_edit_mertting.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Member
            for i in obj_project.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\n The meeting information has been updated. For more information, go to your dashboard.\nLink: {}\nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(),object_edit_mertting.link_meeting, object_edit_mertting.date_meeting, object_edit_mertting.time_meeting, object_edit_mertting.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)

            # Learner
            for i in obj_project.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                
                Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                description='', target=i.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well.\n The meeting information has been updated. For more information, go to your dashboard.\nLink: {}\nDate: {}\nTime: {}\nTime zone: {} \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(),object_edit_mertting.link_meeting, object_edit_mertting.date_meeting, object_edit_mertting.time_meeting, object_edit_mertting.time_zone, obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                e_destination = i.user.email
                send_new_email(e_subject,e_content,e_destination)



            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor edited the meeting information", event_date=timezone.now(), tracing_project_phase_2=obj_project)

            messages.success(request,'The meeting information has been updated successfully.')
        if position_metting == 'delete':
        # Edit meeting
            id_edit = request.POST.get("id_edit") 

            object_edit_mertting = ResearchMeeting.objects.get(id=id_edit)

            object_edit_mertting.status = 'deleted'
            object_edit_mertting.save()

            if object_edit_mertting.date_meeting > date.today():
                # Advisor
                for i in obj_project.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                    
                    Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                    description='The meeting information has not existed longer. For more information, go to your dashboard.', target=i.user,
                    link='').save()

                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well.\nThe meeting information has not existed longer. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

                # Mentor
                for i in obj_project.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                    
                    Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                    description='The meeting information has not existed longer. For more information, go to your dashboard.', target=i.user,
                    link='').save()

                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well.\nThe meeting information has not existed longer. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

                # Member
                for i in obj_project.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                    
                    Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                    description='The meeting information has not existed longer. For more information, go to your dashboard.', target=i.user,
                    link='').save()

                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well.\nThe meeting information has not existed longer. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

                # Learner
                for i in obj_project.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert']):
                    
                    Notification(title='Project (ID: {})'.format(obj_project.project.client_form.formclint.id_project),
                    description='The meeting information has not existed longer. For more information, go to your dashboard.', target=i.user,
                    link='').save()

                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well.\nThe meeting information has not existed longer. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert or supervisor through {} or {}, respectively. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_project.project.client_form.expert.researchrole.expert_email_address, obj_project.project.main_supervisor.email)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor removed the meeting information", event_date=timezone.now(), tracing_project_phase_2=obj_project)


            messages.success(request,'The meeting information has been deleted.')
        return redirect("industry:mainsupervisor-detail", obj_project.pk)
    


    
@login_required
def expert_information(request):
    template_name = 'industry/director/information-expert.html'

    context = {
        'experts': ResearchRole.objects.filter(expert=True),
    }

    return render(request, template_name, context)

    
    
@login_required
def expert_information_ajax(request):
    if request.method == 'POST':
        template_name = 'industry/director/information-expert-ajax.html'
        expert_id = request.POST.get('expert_id')
        print('expert_id', expert_id)
        print('expert_id', expert_id)
        print('expert_id', expert_id)


        context = {
            'expert_obj': User.objects.get(id=expert_id),
            'expert_projects': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert_id=expert_id,).count(),
            'expert_projects_new': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), project__client_form__expert_id=expert_id, status='new').count(),
            'expert_projects_ongoing': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), project__client_form__expert_id=expert_id, status='on_going').count(),
            'expert_projects_pending': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), project__client_form__expert_id=expert_id, status='pending').count(),
            'expert_projects_onhold': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), project__client_form__expert_id=expert_id, status='on_hold').count(),
            'expert_projects_done': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), project__client_form__expert_id=expert_id, status='done').count(),
            'experts': ResearchRole.objects.filter(expert=True),


            'expert_list_created': ResearchProject.objects.filter(~Q(project__client_form__status="is_change"), 
                project__client_form__expert=request.user, 
                project__client_form__formclint__project_created=True).order_by("-created"),

            'expert_list_notcreated': IndustryFormExpert.objects.filter(~Q(status="is_change"), expert=request.user, 
                formclint__project_created=True).order_by("-created"),
        }

        return render(request, template_name, context)



@login_required
def upload_paper(request, pk):
    obj_wbs = get_object_or_404(TimeProgramming, pk=pk)
    if request.method == 'POST':
        question_1 = request.POST.get('question_1')
        question_2 = request.POST.get('question_2')
        question_3 = request.POST.get('question_3')
        question_4 = request.POST.get('question_4')
        question_5 = request.POST.get('question_5')
        question_6 = request.POST.get('question_6')
        question_7 = request.POST.get('question_7')
        question_8 = request.POST.get('question_8')
        upload_file = request.POST.get('upload_file')
        upload_pictures = request.POST.get('upload_pictures')

        obj_wbs.question_1 = obj_wbs.sub.grade
        obj_wbs.question_2 = question_2
        obj_wbs.question_3 = question_3
        obj_wbs.question_4 = question_4
        obj_wbs.question_5 = question_5
        obj_wbs.question_6 = question_6
        obj_wbs.question_7 = question_7
        obj_wbs.question_8 = question_8
        obj_wbs.upload_file = upload_file
        obj_wbs.upload_pictures = upload_pictures

        obj_wbs.save()

        Notification(title='Research (ID: {})'.format(obj_wbs.sub.client_form.formclint.id_project), 
            description='A new report of project progress is available on your list. For more information, go to your dashboard.', target=obj_wbs.sub.client_form.expert, 
            link='').save()

        e_subject = "TECVICO Project (Project ID: {})".format(obj_wbs.sub.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well. \nA new report of project progress is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to director the supervisor through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(obj_wbs.sub.client_form.expert.get_full_name(), obj_wbs.sub.supervisor.email)
        e_destination = obj_wbs.sub.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        for i in obj_wbs.sub.projects.all():
            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor submitted a progress report(or product)", event_date=timezone.now(), tracing_project_phase_2=i)

            return redirect("industry:mainsupervisor-detail", i.pk)

    context = {
        'object': obj_wbs
    }
    return render(request, 'industry/project/page-paper-conference.html', context)


def report_applicant_wbs(request):
    if request.method == 'POST':
        wbs_id = int(request.POST.get('wbs_id'))
        obj_id = int(request.POST.get('obj_id'))
        position = request.POST.get('position')
        id_project = int(request.POST.get('id_project'))
        question_1 = request.POST.get('question_1')
        question_2 = request.POST.get('question_2')
        question_3 = request.POST.get('question_3')
        question_4 = request.POST.get('question_4')

        obj_wbs = TimeProgramming.objects.get(id=wbs_id)
        project_obj = ResearchProject.objects.get(id=id_project)


        create_obj = ReportApplicant.objects.create(
            applicant=request.user, project_id=id_project, wbs_obj=obj_wbs, question_1=question_1, question_2=question_2, 
            question_3=question_3, question_4=question_4, position=position
            )


        Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
        description='The applicant sent an evaluation of the project to you. For more information, go to your dashboard.', target=project_obj.project.client_form.expert,
        link='').save()

        e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
        e_content = "Dear {} \nHello\nHope you are going well.\nThe applicant sent an evaluation of the project to you. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to director the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.project.client_form.expert.get_full_name(), )
        e_destination = project_obj.project.client_form.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

        messages.success(request,'Your report has been sent successfully.')
        
        if position == 'Advisor':
            return redirect('industry:applicant-supervisor-detail', obj_id)

        elif position == 'Mentor':
            return redirect('industry:applicant-mentor-detail', obj_id)

        elif position == 'Member':
            return redirect('industry:applicant-member-detail', obj_id)

        elif position == 'Learner':
            return redirect('industry:applicant-learner-detail', obj_id)



def Manageproject_applicant_detail(request, pk):
    template_name = 'industry/expert/expert-manage-project-applicant-detail.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)
    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user)
    roles = ResearchRole.objects.filter(director=True)
    
    if request.method == 'POST':
        form_send_contract = SendContractApplicantForm(request.POST, request.FILES)
        if form_send_contract.is_valid():
            obj_id = form_send_contract.cleaned_data.get('obj_id')
            status = form_send_contract.cleaned_data.get('status')
            contract = form_send_contract.cleaned_data.get('contract')
            position_user = form_send_contract.cleaned_data.get('position_user')
            reason_rejection = form_send_contract.cleaned_data.get('reason_rejection')

            if position_user == 'advisor':
                obj_applicant = SuperVizor.objects.get(id=obj_id)

            elif position_user == 'mentor':
                obj_applicant = Mentor.objects.get(id=obj_id)

            elif position_user == 'member':
                obj_applicant = Member.objects.get(id=obj_id)

            elif position_user == 'learner':
                obj_applicant = Lerner.objects.get(id=obj_id)


            if status == 'send-contract-to-applicant':
                obj_applicant.status = 'send-contract'
                obj_applicant.contract = contract
                obj_applicant.deadline = timezone.now() + timedelta(2)
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()


                messages.success(request,'You sent the contract to the applicant successfully.')
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='A contract is available on your dashboard. To join the project, you must sign and send it back to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(obj_applicant.deadline.strftime('%Y/%m/%d %H:%M')), target=obj_applicant.user,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nA contract is available on your dashboard. To join the project, you must sign and send back it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), obj_applicant.deadline.strftime('%Y/%m/%d %H:%M'), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)

            if status == 'revise_contract-applincat':
                obj_applicant.status = 'revised_by_expert'
                if contract:
                    obj_applicant.contract = contract
                obj_applicant.reason_rejection = reason_rejection
                obj_applicant.deadline = timezone.now() + timedelta(2)
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()
                
                messages.success(request,'You have revised the signed contract to the applicant successfully.')
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Your signed contract needs a revision. You must modify and submit it by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(obj_applicant.deadline.strftime('%Y/%m/%d %H:%M')), target=obj_applicant.user,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYour signed contract needs a revision. You must modify the contract and send it by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), obj_applicant.deadline.strftime('%Y/%m/%d %H:%M'), project_obj.project.client_form.expert.researchrole.expert_email_address )
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)
                 
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert revised the applivant`s signed contract, namely ({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)


            if status == 'rejected-applicant':
                obj_applicant.status = 'reject'
                obj_applicant.reason_rejection = reason_rejection
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Because TECVICO has not recieved any signed contract from you yet, TECVICO is sorry to reject your request to join the project. For more information, go to your dashboard.', target=obj_applicant.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \n Because TECVICO has not recieved any signed contract from you yet, TECVICO is sorry to reject your request to join the project. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the company through project@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name())
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)

                for i in RequestUserForProject.objects.filter(project_request=project_obj, user=obj_applicant.user):
                    i.status = 'rejection-contract'
                    i.save()
                    
                messages.success(request,'You rejected the applicant.')
                
                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert rejected the applicant, namely ({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)



            if status == 'send-to-the-director':
                if obj_applicant.status == 'revised-director-to-expert':
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the resubmitted applicant`s contract, namely ({}), to the director".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Expert', user=request.user, status="The expert sent the applicant`s signed contract, namely ({}), to the director".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)

                obj_applicant.status = 'send-to-director'
                obj_applicant.reason_rejection = reason_rejection
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()
                
                for i in roles:
                    Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                    description='The epxert, {}, sent a signed contract to you. For more information, go to your dashboard.'.format(project_obj.project.client_form.expert.get_full_name()), target=i.user,
                    link='').save()

                    e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well. \nThe epxert sent a signed contract to you. For more information, go to your dashboard. \nDo not reply to this Email. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), )
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have sent the signed contract to the director successfully.')

            if status == 'accept-applicant':
                obj_applicant.status = 'confirmed-by-expert'
                # obj_applicant.reason_rejection = reason_rejection
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert accepted the applicant`s contract, namely ({})".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                    
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Congrats. Your request to join the project has been accepted. For more information, go to your dashboard.', target=obj_applicant.user,
                link='').save()


                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='The company accepted the signed contract sent by the applicant, namely {}. For more information, go to your dashboard.'.format(obj_applicant.user.get_full_name()), target=project_obj.main_supervisor,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nCongrats. Your request to join the project has been accepted. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address )
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)


                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe company accepted the signed contract sent by the applicant, namely {}. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(), obj_applicant.user.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have accpeted the applicant.')

            return redirect("industry:manageproject-applicant-detail", project_obj.pk)



    context = {
        'wbs_list': wbs_list,
        'project_obj': project_obj,
    }
    return render(request, template_name, context)


def Manageproject_applicant_detail_remove(request, pk):
    template_name = 'industry/expert/expert-manage-project-applicant-remove.html'
    project_obj = get_object_or_404(ResearchProject, pk=pk)
    wbs_list = TimeProgramming.objects.filter(sub__client_form__expert=request.user)
    roles = ResearchRole.objects.filter(director=True)

    if request.method == 'POST':
        form_send_contract = SendContractApplicantForm(request.POST, request.FILES)
        if form_send_contract.is_valid():
            obj_id = form_send_contract.cleaned_data.get('obj_id')
            status = form_send_contract.cleaned_data.get('status')
            position_user = form_send_contract.cleaned_data.get('position_user')
            comment = form_send_contract.cleaned_data.get('reason_rejection')

            if position_user == 'advisor':
                obj_applicant = SuperVizor.objects.get(id=obj_id)

            elif position_user == 'mentor':
                obj_applicant = Mentor.objects.get(id=obj_id)

            elif position_user == 'member':
                obj_applicant = Member.objects.get(id=obj_id)

            elif position_user == 'learner':
                obj_applicant = Lerner.objects.get(id=obj_id)


            if status == 'send-to-the-director':
                obj_applicant.status_remove = 'request-remove-send-to-the-director'
                obj_applicant.comment = comment
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert sent the request to remove the applicant, namely ({}), to the director".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                    
                for i in roles:
                    # messages.success(request,'You sent the contract to the applicant successfully.')
                    Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                    description='An applicant removal request has been sent to you. For more information, go to your dashboard.', target=i.user,
                    link='').save()
                    

                    e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well. \nThe expert,namely {}, sent the main supervisor‘s request to remove the applicant from the project. For more information, go to your dashboard. \nDo not reply to this Email. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(),project_obj.project.client_form.expert.get_full_name(), )
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have sent the applicant removal request to the director successfully.')

            if status == 'request-reject-by-expert':
                obj_applicant.status_remove = 'request-reject-by-expert'
                obj_applicant.comment = comment
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert rejected the request to remove the applicant, namely ({}) from the project".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)
                
                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Your request to remove the applicant from the project was rejected. For more information, go to your dashboard.', target=project_obj.main_supervisor,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYour request to remove the applicant from the project was rejected because of: \n{}. For more information, go to your dashboard.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(),obj_applicant.comment ,project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You rejected the applicant removal request.')

            if status == 'request-accpet-by-expert':
                obj_applicant.status_remove = 'request-accpet-by-expert'
                obj_applicant.event_date = timezone.now()
                obj_applicant.comment = comment
                obj_applicant.save()


                create_obj_tracing = Tracing.objects.create(
                    position='Expert', user=request.user, status="The expert accepted the request to remove the applicant, namely ({}), from the project".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=project_obj)


                for i in RequestUserForProject.objects.filter(project_request=project_obj, user=obj_applicant.user):
                    i.status = 'remove'
                    i.save()

                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='Your request to remove the applicant from the project has been accepted. For more information, go to your dashboard.', target=project_obj.main_supervisor,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYour request to remove the applicant from the project has been accepted. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(project_obj.main_supervisor.get_full_name(), project_obj.project.client_form.expert.researchrole.expert_email_address)
                e_destination = project_obj.main_supervisor.email
                send_new_email(e_subject,e_content,e_destination)

                Notification(title='Project (ID: {})'.format(project_obj.project.client_form.formclint.id_project),
                description='You was removed from the project. For more information, go to your dashboard.', target=obj_applicant.user,
                link='').save()

                e_subject ="TECVICO Project (Project ID: {})".format(project_obj.project.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nTECVICO is sorry to inform you that You was removed from the project because of: \n{}. \ntitle:{}. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the company through project@tecvico.com.\n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(),  obj_applicant.comment_rejection, project_obj.project.client_form.formclint.title,)
                e_destination = obj_applicant.user.email
                send_new_email(e_subject,e_content,e_destination)

                messages.success(request,'You have accepted the applicant removal request.')

            return redirect("industry:manageproject-applicant-remove", project_obj.pk)



    context = {
        'wbs_list': wbs_list,
        'project_obj': project_obj,
    }
    return render(request, template_name, context)

def applicant_send_contract_to_expert(request):
    if request.method == 'POST':
        form_send_contract = SendContractApplicantForm(request.POST, request.FILES)
        if form_send_contract.is_valid():
            obj_id = form_send_contract.cleaned_data.get('obj_id')
            status = form_send_contract.cleaned_data.get('status')
            contract = form_send_contract.cleaned_data.get('contract')
            position_user = form_send_contract.cleaned_data.get('position_user')


            if position_user == 'Advisor':
                obj_applicant = SuperVizor.objects.get(id=obj_id)

            elif position_user == 'Mentor':
                obj_applicant = Mentor.objects.get(id=obj_id)

            elif position_user == 'Member':
                obj_applicant = Member.objects.get(id=obj_id)

            elif position_user == 'Learner':
                obj_applicant = Lerner.objects.get(id=obj_id)

            if status == 'send-contract-to-expert':

                if obj_applicant.status == 'revise_contract-applincat':
                    create_obj_tracing = Tracing.objects.create(
                        position='Applicant', user=request.user, status="The applicant, namely ({}), sent the revised contract to the expert".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=obj_applicant.research)
                else:
                    create_obj_tracing = Tracing.objects.create(
                        position='Applicant', user=request.user, status="The applicant, namely ({}), sent the signed contract to the expert".format(obj_applicant.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=obj_applicant.research)

                obj_applicant.status = 'send-contract-to-expert'
                obj_applicant.contract_applicant = contract
                obj_applicant.event_date = timezone.now()
                obj_applicant.save()

            Notification(title='Project (ID: {})'.format(obj_applicant.research.project.client_form.formclint.id_project),
            description='A signed contract is available on your list. You must go to your dashboard and proceed with it.', target=obj_applicant.research.project.client_form.expert,
            link='').save()
            

            Notification(title='Project (ID: {})'.format(obj_applicant.research.project.client_form.formclint.id_project),
            description='Your signed contract has been sent successfully. For more information, please go to your dashboard.', target=obj_applicant.user,
            link='').save()

            e_subject ="TECVICO Project (Project ID: {})".format(obj_applicant.research.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA signed contract is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.research.project.client_form.expert.get_full_name(), )
            e_destination = obj_applicant.research.project.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            

            e_subject ="TECVICO Project (Project ID: {})".format(obj_applicant.research.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nYour signed contract has been sent successfully. For more information, please go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_applicant.user.get_full_name(), obj_applicant.research.project.client_form.expert.researchrole.expert_email_address)
            e_destination = obj_applicant.user.email
            send_new_email(e_subject,e_content,e_destination)
                
            messages.success(request,'Your signed contract has been sent successfully.')


            if position_user == 'Advisor':
                return redirect("industry:applicant-supervisor-detail", obj_applicant.pk)

            elif position_user == 'Mentor':
                return redirect("industry:applicant-mentor-detail", obj_applicant.pk)

            elif position_user == 'Member':
                return redirect("industry:applicant-member-detail", obj_applicant.pk)

            elif position_user == 'Learner':
                return redirect("industry:applicant-learner-detail", obj_applicant.pk)

def contract_list_applicant(request):
    template_name = 'industry/project/contract-list-applicant.html'

    # New contract
    new_contract_advisor_count = SuperVizor.objects.filter(user=request.user, status='send-contract').count()
    new_contract_mentor_count = Mentor.objects.filter(user=request.user, status='send-contract').count()
    new_contract_member_count = Member.objects.filter(user=request.user, status='send-contract').count()
    new_contract_learner_count = Lerner.objects.filter(user=request.user, status='send-contract').count()

    # Revise contract
    revise_contract_advisor_count = SuperVizor.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_mentor_count = Mentor.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_member_count = Member.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_learner_count = Lerner.objects.filter(user=request.user, status='revised_by_expert').count()

    context = {
        # New contract
        'new_contract_count' : new_contract_advisor_count + new_contract_mentor_count + new_contract_member_count + new_contract_learner_count,
        'new_contract_advisor_list': SuperVizor.objects.filter(user=request.user, status='send-contract'),
        'new_contract_mentor_list': Mentor.objects.filter(user=request.user, status='send-contract'),
        'new_contract_member_list': Member.objects.filter(user=request.user, status='send-contract'),
        'new_contract_learner_list': Lerner.objects.filter(user=request.user, status='send-contract'),

        'revise_contract_count' : revise_contract_advisor_count + revise_contract_mentor_count + revise_contract_member_count + revise_contract_learner_count,
        'revise_contract_advisor_list': SuperVizor.objects.filter(user=request.user, status='revised_by_expert'),
        'revise_contract_mentor_list': Mentor.objects.filter(user=request.user, status='revised_by_expert'),
        'revise_contract_member_list': Member.objects.filter(user=request.user, status='revised_by_expert'),
        'revise_contract_learner_list': Lerner.objects.filter(user=request.user, status='revised_by_expert'),

    }
    return render(request, template_name, context)




@login_required
def evaluation_applicant(request, pk):
    applicant = get_object_or_404(ResearchProject, pk=pk)

    if request.method == 'POST':
        obj_id = request.POST.get('obj_id')
        position = request.POST.get('position')
        question_1 = request.POST.get('question_1')
        question_2 = request.POST.get('question_2')
        question_3 = request.POST.get('question_3')
        question_4 = request.POST.get('question_4')


        
        if position == 'advisor':
            applicant_obj = SuperVizor.objects.get(id=obj_id)

        elif position == 'mentor':
            applicant_obj = Mentor.objects.get(id=obj_id)

        elif position == 'member':
            applicant_obj = Member.objects.get(id=obj_id)

        elif position == 'learner':
            applicant_obj = Lerner.objects.get(id=obj_id)

        applicant_obj.question_1 = question_1
        applicant_obj.question_2 = question_2
        applicant_obj.question_3 = question_3
        applicant_obj.question_4 = question_4
        applicant_obj.save()

        create_obj_tracing = Tracing.objects.create(
            position='Main supervisor', user=request.user, status="The supervisor evaluated the applicant, namely ({}) within the project".format(applicant_obj.user.get_full_name()), event_date=timezone.now(), tracing_project_phase_2=applicant)


        return redirect("industry:evaluation-applicant-page", applicant.pk)

    count = 0
    for i in applicant.supervisors_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=applicant):
        if i.question_1 == None:
            count += 1

    for i in applicant.mentor_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=applicant):
        if i.question_1 == None:
            count += 1

    for i in applicant.mmber_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=applicant):
        if i.question_1 == None:
            count += 1

    for i in applicant.lerner_project.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=applicant):
        if i.question_1 == None:
            count += 1

    context = {
        'count': count,
        'applicant': applicant,
    }
    return render(request, 'industry/project/applicant-evaluation.html', context)


def change_status(request):
    if request.method == 'POST':
        id_project = int(request.POST.get('id_project'))

        project_obj = get_object_or_404(ResearchProject, pk=id_project)

        project_obj.status_change_choices = 'done'
        project_obj.status_change = 'send_to_expert'
        project_obj.save()

        return redirect("industry:industry-project-edit-edit", id_project)
        
        

def change_status_to_home(request):
    if request.method == 'POST':
        id_project = int(request.POST.get('id_project'))
        status = request.POST.get('status')

        project_obj = get_object_or_404(ResearchProject, pk=id_project)

        if status == 'on':
            project_obj.view_project_home = True
        else:
            project_obj.view_project_home = False
        project_obj.save()

        return redirect('dashboard-projects-page')



def confirm_produc(request, pk):
    if request.method == 'POST':
        position = request.POST.get('position')
        status = request.POST.get('status')
        id_wbs = int(request.POST.get('id_wbs'))
        
        

        wbs_obj = TimeProgramming.objects.get(id=id_wbs)
        project_obj = get_object_or_404(ResearchProject, pk=pk)

        if status == 'True':
            wbs_obj.confirm = True
        else:
            wbs_obj.confirm = False
        wbs_obj.save()

        if position == 'report-expert':
            return redirect('industry:project-expert-history-created-detail', project_obj.pk)
        else:
            return redirect('industry:project-expert-history-created-detail', project_obj.pk)



@login_required
def form_request_status_done(request, pk):
    obj_project = get_object_or_404(ResearchProject, pk=pk)
    if request.method == 'POST':
        question_1 = request.POST.get('question_1')
        # question_2 = request.POST.get('question_2')
        # question_3 = request.POST.get('question_3')
        # question_4 = request.POST.get('question_4')
        # question_5 = request.POST.get('question_5')
        # question_6 = request.POST.get('question_6')
        # question_7 = request.POST.get('question_7')
        # question_8 = request.POST.get('question_8')
        # upload_file = request.POST.get('upload_file')
        # upload_pictures = request.POST.get('upload_pictures')

        # obj_project.question_1 = question_1
        # obj_project.question_2 = question_2
        # obj_project.question_3 = question_3
        # obj_project.question_4 = question_4
        # # obj_project.question_5 = question_5
        # obj_project.question_6 = question_6
        # obj_project.question_7 = question_7
        # obj_project.question_8 = question_8
        # obj_project.upload_file = upload_file
        # obj_project.upload_pictures = upload_pictures

        obj_project.save()

        create_obj_tracing = Tracing.objects.create(
            position='Main supervisor', user=request.user, status="The supervisor filled in the advertisement form  for status change request (Move the project to done status)", event_date=timezone.now(), tracing_project_phase_2=obj_project)




        count = 0
        for i in obj_project.supervisors_project.filter(status__in=['confirmed-by-expert', 'confirmed']):
            if i.question_1 == None:
                count += 1
        for i in obj_project.mentor_project.filter(status__in=['confirmed-by-expert', 'confirmed']):
            if i.question_1 == None:
                count += 1
        for i in obj_project.mmber_project.filter(status__in=['confirmed-by-expert', 'confirmed']):
            if i.question_1 == None:
                count += 1
        for i in obj_project.lerner_project.filter(status__in=['confirmed-by-expert', 'confirmed']):
            if i.question_1 == None:
                count += 1
        if count > 0:
            messages.error(request,'Error: You must first evaluate the members and then request the change status.')
            return redirect('industry:evaluation-applicant-page', obj_project.pk)
        else:

            obj_project.status = 'done'
            obj_project.status_change = 'send_to_expert'
            obj_project.save()       
            return redirect("industry:mainsupervisor-detail", obj_project.pk)

    context = {
        'object': obj_project
    }
    return render(request, 'industry/project/form-request-change-status-done.html', context)

# def seen_expert_comments(request):
#     if request.method == 'POST':
#         id_project = int(request.POST.get('id_project'))
#         commentIDs1 = request.POST.get('commentIDs1')
#         commentIDs2 = request.POST.get('commentIDs2')

#         comment_list = []
#         commentIDs1 = commentIDs1.split('"')
#         for i in commentIDs1:
#             if i != '[' and i != ']' and i != ',':
#                 comment_list.append(int(i))


#         reply_comment_list = []
#         commentIDs2 = commentIDs2.split('"')
#         for i in commentIDs2:
#             if i != '[' and i != ']' and i != ',':
#                 reply_comment_list.append(int(i))

#         comments = ApplicantComment.objects.filter(seen=False)
#         reply_comments = ApplicantReplyComment.objects.filter(seen=False)

#         for i in comment_list:
#             for e in comments:
#                 if i == e.id:
#                     comment_id = ApplicantComment.objects.get(id=i)
#                     comment_id.seen = True
#                     comment_id.save()

#         for i in reply_comment_list:
#             for e in reply_comments:
#                 if i == e.id:
#                     reply_comment_obj = ApplicantReplyComment.objects.get(id=i)
#                     reply_comment_obj.seen = True
#                     reply_comment_obj.save()



#         return redirect('industry:expert-applicant-comment', id_project)
        
        


#detail list review
class ExpertListNotResponseProposal(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/expert/expert-list-not-response-proposal.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proposals'] = IndustryExpertForSupervisor.objects.filter(status='not_response_proposal', client_form_id=pk)
        return context
        
        


#detail not response proposal
@login_required
def expert_notresponse_proposal_detail(request, pk):
    template_name = 'industry/expert/expert-notresponse-proposal-detail.html'
    obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    roles = ResearchRole.objects.all() 
    user_role = ResearchRole.objects.filter(user=request.user).count()

    if user_role != 0 and obj_supervisor.status == 'not_response_proposal' and request.user.researchrole.expert == True and obj_supervisor.client_form.expert == request.user:
        if request.method == 'POST':
            status = request.POST.get('status')
            comment = request.POST.get('comment')


            if status == 'reject':
                obj_supervisor.client_form.formclint.status = 'rejected_by_expert'
                obj_supervisor.client_form.formclint.reason_rejectd = comment
                obj_supervisor.client_form.status = 'h'
                obj_supervisor.status = 'reject_proposal_by_expert'


                obj_supervisor.client_form.formclint.save()
                obj_supervisor.client_form.save()
                obj_supervisor.save()


                messages.success(request,'You have sent the contract to the applicant successfully.')
                Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
                description='Because TECVICO has not recieved any response to proposal revisoin request from you yet, TECVICO is sorry to inform you that your proposal was rejected. For more information, go to your dashboard.', target=obj_supervisor.client_form.formclint.user,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nBecause TECVICO has not recieved any response to proposal revisoin request from you yet, TECVICO is sorry to inform you that your proposal was rejected.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the company through project@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_supervisor.client_form.formclint.user.get_full_name(), )
                e_destination = obj_supervisor.client_form.formclint.user.email
                send_new_email(e_subject,e_content,e_destination)

            elif status == 'send-to-director':
                obj_supervisor.client_form.formclint.follow_project = 'p_main_not_response_revised_proposal_send_to_director'
                obj_supervisor.status = 'not_response_proposal_send_to_director'
                obj_supervisor.text = comment
                obj_supervisor.save()

                for i in ResearchRole.objects.filter(director=True):
                    messages.success(request,'You have sent the contract to the applicant successfully.')
                    Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
                    description='Since the supervisor has not responded to the proposal revisoin request yet, we are allowed to reject the proposal or extend the deadline. Go to your dashboard and proceed with it.', target=i.user,
                    link='').save()
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
                    e_content = "Dear {} \nHello\nHope you are going well. \n Since the supervisor has not responded to the proposal revisoin request yet, we are allowed to reject the proposal or extend the deadline. Go to your dashboard and proceed with it.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_supervisor.client_form.researchrole.expert.expert_email_address)
                    e_destination = i.user.email
                    send_new_email(e_subject,e_content,e_destination)

            return redirect('industry:industry-expert-list')


        context = {
        'object': obj_supervisor,
        'reviewer': IndustryReviewer.objects.filter(object_supervisor=obj_supervisor),
        'reviewer_count': IndustryReviewer.objects.filter(status='a',object_supervisor=obj_supervisor).count(),
        'reviewer_count_expert': IndustryReviewer.objects.filter(status='e',object_supervisor=obj_supervisor).count(),
        }

        return render(request, template_name, context)
    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-expert-list')
            
            
            


# Director list not response proposal
class ExpertListNotResponseProposalDirector(LoginRequiredMixin, SecurityDirector, DetailView):
    template_name = 'industry/expert/expert-list-not-response-proposal.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, ~Q(status="is_change"), pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['proposals'] = IndustryExpertForSupervisor.objects.filter(status='not_response_proposal_send_to_director', client_form_id=pk)
        return context
        
        

# Director detail not response proposal
@login_required
def director_notresponse_proposal_detail(request, pk):
    template_name = 'industry/director/director-notresponse-proposal-detail.html'
    obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    roles = ResearchRole.objects.all() 
    user_role = ResearchRole.objects.filter(user=request.user).count()

    if user_role != 0 and obj_supervisor.status == 'not_response_proposal_send_to_director':
        if request.method == 'POST':
            status = request.POST.get('status')
            comment = request.POST.get('comment')

            if status == 'reject':
                obj_supervisor.client_form.formclint.status = 'r'
                obj_supervisor.client_form.formclint.reason_rejectd = comment
                obj_supervisor.client_form.status = 'h'
                obj_supervisor.status = 'h'


                obj_supervisor.client_form.formclint.save()
                obj_supervisor.client_form.save()
                obj_supervisor.save()


                messages.success(request,'You have sent the contract to the applicant successfully.')
                Notification(title='Project (ID: {})'.format(obj_supervisor.client_form.formclint.id_project),
                description='Because TECVICO has not recieved any response to proposal revisoin request from you yet, TECVICO is sorry to inform you that your proposal was rejected. For more information, go to your dashboard.', target=obj_supervisor.client_form.formclint.user,
                link='').save()
                

                e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \n Because TECVICO has not recieved any response to proposal revisoin request from you yet, TECVICO is sorry to inform you that your proposal was rejected.\nDo not reply to this Email. If you have any question or concern, please feel free to contact the company through project@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_supervisor.client_form.formclint.user.get_full_name(), )
                e_destination = obj_supervisor.client_form.formclint.user.email
                send_new_email(e_subject,e_content,e_destination)

            return redirect('industry:industry-director')


        context = {
        'object': obj_supervisor,
        'reviewer': IndustryReviewer.objects.filter(object_supervisor=obj_supervisor),
        'reviewer_count': IndustryReviewer.objects.filter(status='a',object_supervisor=obj_supervisor).count(),
        'reviewer_count_expert': IndustryReviewer.objects.filter(status='e',object_supervisor=obj_supervisor).count(),
        }

        return render(request, template_name, context)
    else:
        if user_role == 0:
            raise Http404("You can't see this page.")
        else:
            return redirect('industry:industry-director')

@login_required
def messenger_page(request, pk):
    template_name = 'industry/project/messenger-page.html'
    obj_project = ResearchProject.objects.get(pk=pk)

    if request.method == 'POST':
        message = request.POST.get('message')
        recipient = request.POST.get('recipient')
        status = request.POST.get('status')

        if status == 'applicant-to-expert':
            create_obj = ApplicantComment.objects.create(sender=request.user, recipient_id=obj_project.project.client_form.expert.id, project=obj_project, position='expert-applicant', comment=message)

            messages.success(request,'Your message has been sent successfully.')

            return redirect('industry:messenger-page', obj_project.id)

        elif status == 'expert-to-applicant':
            create_obj = ApplicantComment.objects.create(sender=request.user, recipient_id=int(recipient), project=obj_project, position='expert-applicant', comment=message)

            messages.success(request,'Your message has been sent successfully.')

            return redirect('industry:messenger-page', obj_project.id)

        elif status == 'to-director':
            create_obj = ApplicantComment.objects.create(sender=request.user, project=obj_project, position='to-director', comment=message)

            messages.success(request,'Your message has been sent successfully.')

            return redirect('industry:messenger-page', obj_project.id)


    context = {
       'obj_project': obj_project, 
       'advisors': SuperVizor.objects.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=obj_project), 
       'mentors': Mentor.objects.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=obj_project), 
       'members': Member.objects.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=obj_project), 
       'learners': Lerner.objects.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], research=obj_project), 

       'expert_applicant_comment': ApplicantComment.objects.filter(project=obj_project, ).order_by('created'),
       'director_comment': ApplicantComment.objects.filter(project=obj_project, position='to-director').order_by('created'),
    }
    return render(request, template_name, context)



        #### ------> Applicant, Client, ... <------ ####

# Client     
def detail_client(request, pk):
    template_name = 'industry/project/myproject/client_detail.html'
    obj_project = get_object_or_404(IndustryFormClient, pk=pk)
    if request.user == obj_project.user:
        service = Service.objects.filter(user=request.user, service_name='p', project=obj_project).first()
        
        if request.method == 'POST':
            form_contract = SendContractForSupervisor(request.POST or None, request.FILES)
            if form_contract.is_valid():
                Contract = form_contract.cleaned_data.get("Contract")
                status = form_contract.cleaned_data.get("status")
                
                obj_project.signed_contract = Contract
                obj_project.save()
                

                if obj_project.status == 'send-contract-to-client':
                    return PaymentProtocol(request, 'P', obj_project, obj_project.fund , action='contract-client')
        
                obj_project.status = 'send-signed-contract'
                obj_project.follow_project = 'send_signed_contract'
                obj_project.save()
    
                    
                Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                    description='Your signed contract has been sent successfully. For more information, go to your dashboard.', target=request.user, 
                    link=reverse('industry:industry-reviewer-detail', args=[obj_project.pk])).save()
                    
                    
               
    
                for i in obj_project.forms_client.filter(~Q(status="is_change")):
                    i.status = 'send-signed-contract'
                    i.save()
                    
                    Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                        description='The client sent the signed contract to you. For more information, go to your dashboard. For more information, go to your dashboard.', target=i.expert, 
                        link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()
                        
                        
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
                    e_content ="Dear {}\nHello\nHope you are going well.\n. The client sent the signed contract to you. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(i.expert.get_full_name(),)
                    e_destination = i.expert.researchrole.expert_email_address
                    send_new_email(e_subject,e_content,e_destination)
                    
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
                    e_content ="Dear {}\nHello\nHope you are going well.\n Your signed contract has been sent successfully. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(request.user.get_full_name(), i.expert.researchrole.expert_email_address)
                    e_destination = request.user.email
                    send_new_email(e_subject,e_content,e_destination)
                
        
                create_obj_tracing = Tracing.objects.create(
                    position='Client', user=request.user, status="The client sent the signed contract to the expert", event_date=timezone.now(), tracing_project=obj_project)
        
                messages.success(request,'The signed contract has been submitted successfully')
                return redirect('industry:client-detail', obj_project.pk)
                
                
            

            form_withdraw = FormWithdrew(request.POST or None, request.FILES)
            if form_withdraw.is_valid():
                status = form_withdraw.cleaned_data.get("status")
                reason = form_withdraw.cleaned_data.get("reason")
                
                obj_project.status = 'withdrew'
                obj_project.rejected_date = timezone.now()
                obj_project.save()
                
                create_obj_tracing = Tracing.objects.create(
                    position='Client', user=request.user, status="The client withdrew to continue the project", event_date=timezone.now(), tracing_project=obj_project)
    
                
                RejectProtocol(request, 'P', obj_project, obj_project.fund)
        
                Notification(title='Project (ID: {})'.format(obj_project.id_project),
                description='You withdrew to continue the project with us. For more information, go to your dashboard.', target=request.user,
                link='').save()
                
                e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYou withdrew to continue the project with us. TECVICO looks forward to seeing you in the feuture. For more information, go to your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through projec@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(request.user.get_full_name())
                e_destination = request.user.email
                send_new_email(e_subject,e_content,e_destination)
            
                for i in obj_project.forms_client.filter(~Q(status="is_change")):
                    i.status = 'h'
                    i.save()
                    
                    Notification(title='Research (ID: {})'.format(obj_project.id_project), 
                        description='The client withdrew to continue the project with us. For more information, go to your dashboard.', target=i.expert, 
                        link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()
                        
                        
                    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
                    e_content ="Dear {}\nHello\nHope you are going well.\n. The client withdrew to continue the project with us. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(i.expert.get_full_name(),)
                    e_destination = i.expert.researchrole.expert_email_address
                    send_new_email(e_subject,e_content,e_destination)
                    
                messages.error(request,'You withdrew to resubmit the project.')
                return redirect('dashboard-myprojects-reserach')
            
            
        context = {
            'object': obj_project,
            'inv': Invoice.objects.filter(user=request.user, service=service).first()
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")





def pay_contract_client(user, pk):
    obj_project = get_object_or_404(IndustryFormClient, pk=pk)
    
        
    obj_project.status = 'send-signed-contract'
    obj_project.follow_project = 'send_signed_contract'
    obj_project.save()

        
    Notification(title='Project (ID: {})'.format(obj_project.id_project), 
        description='Your signed contract has been sent successfully. For more information, go to your dashboard.', target=user, 
        link=reverse('industry:industry-reviewer-detail', args=[obj_project.pk])).save()
        
        
    e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
    e_content ="Dear {}\nHello\nHope you are going well.\n. Your signed contract has been sent successfully. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the company through project@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(user.get_full_name(),)
    e_destination = user.email
    send_new_email(e_subject,e_content,e_destination)

    for i in obj_project.forms_client.filter(~Q(status="is_change")):
        i.status = 'send-signed-contract'
        i.save()
        
        Notification(title='Project (ID: {})'.format(obj_project.id_project), 
            description='Your signed contract has been sent successfully. For more information, go to your dashboard.', target=i.expert, 
            link=reverse('industry:industry-reviewer-detail', args=[i.pk])).save()
            
            
        e_subject ="TECVICO Project (Project ID: {})".format(obj_project.id_project, )
        e_content ="Dear {}\nHello\nHope you are going well.\n. The client sent the signed contract to you. For more information, go to your dashboard.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projectdirector@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(i.expert.get_full_name(),)
        e_destination = i.expert.researchrole.expert_email_address
        send_new_email(e_subject,e_content,e_destination)

    create_obj_tracing = Tracing.objects.create(
        position='Client', user=user, status="The client sent the signed contract to the expert", event_date=timezone.now(), tracing_project=obj_project)

    create_obj_tracing = Tracing.objects.create(
        position='You', user=user, status="You the signed contract to company", event_date=timezone.now(), tracking_client=obj_project)



def detail_client_revised(request, pk):
    template_name = 'industry/project/myproject/applicant_client_revised.html'
    obj_client = IndustryFormClient.objects.get(id=pk)
    if obj_client.user == request.user or obj_client.status == 'revise_director_to_client':
        if request.method == 'POST':
            title = request.POST.get('title')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            fund = request.POST.get('fund')
            data_set_link = request.POST.get('data_set_link')
            abstrack = request.POST.get('abstrack')
            equipment = request.POST.get('equipment')
            requirement = request.POST.get('requirement')

            last_fund = obj_client.fund

            obj_client.title = title
            obj_client.start_date = start_date
            obj_client.end_date = end_date
            obj_client.fund = fund
            obj_client.data_set_link = data_set_link
            obj_client.abstrack = abstrack
            obj_client.equipment = equipment
            obj_client.requirement = requirement
            obj_client.status = 'resubmited_project'

            obj_client.save()

            # if int(obj_client.fund) > int(last_fund):
            #     new_fund = obj_client.fund - last_fund
            #     request.user.memberprofile.balance - new_fund
            #     request.user.memberprofile.save()


            create_obj_tracing = Tracing.objects.create(
                position='Client', user=request.user, status="The client resubmitted the project", event_date=timezone.now(), tracing_project=obj_client)


            
            Notification(title='Project (ID: {})'.format(obj_client.id_project),
            description='You resubmitted the project successfully. For more information, go to your dashboard.', target=obj_client.user,
            link='').save()
            
          
            
            for i in obj_client.forms_client.filter(~Q(status="is_change"), ):
                Notification(title='Project (ID: {})'.format(obj_client.id_project),
                description='The client resubmitted the project. Go to your dashboard and proceed with it.', target=i.expert,
                link='').save()
                
                e_subject ="TECVICO Project (Project ID: {})".format(obj_client.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nYou resubmitted the project successfully. For more information, go to your dashboard. \nDo not reply to this Email. If you have any question or concern, please feel free to contact the expert through {}.\n\nThank you \nBest regards \nTECVICO Corp.".format(obj_client.user.get_full_name(), i.expert.researchrole.expert_email_address)
                e_destination = obj_client.user.email
                send_new_email(e_subject,e_content,e_destination)
                
                
                e_subject ="TECVICO Project (Project ID: {})".format(obj_client.id_project, ) 
                e_content = "Dear {} \nHello\nHope you are going well. \nThe client resubmitted the project. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.expert.get_full_name())
                e_destination = i.expert.researchrole.expert_email_address
                send_new_email(e_subject,e_content,e_destination)
                i.status = 'resubmited_project'
                i.save()
                
            messages.success(request,'The project has been resubmitted successfully.')
            return redirect("dashboard-myprojects-reserach")

        context = {
            'object': obj_client,
        }
        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")


# def resubmitted_project(request, pk):
        

# Applicant

def applicant_advisor_detail(request, pk):
    template_name = 'industry/project/myproject/applicant_detail.html'
    obj = get_object_or_404(SuperVizor, pk=pk)

    comment_to_expert = ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert', seen=False)
    comment_to_applicant = ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant', seen=False)

    for i in comment_to_expert:
        for r in i.comments.filter(seen=False):
            print('22')
            r.seen = True
            r.save()

    for i in comment_to_applicant:
        i.seen = True
        i.save()

    context = {
        'object': obj,
        'meeting_info': ResearchMeeting.objects.filter(project_research=obj.research, status="visible"),
        'supervisors_info': SuperVizor.objects.filter(research=obj.research, status='confirmed'),
        'mentors_info': Mentor.objects.filter(research=obj.research, status='confirmed'),
        'members_info': Member.objects.filter(research=obj.research, status='confirmed'),
        'learners_info': Lerner.objects.filter(research=obj.research, status='confirmed'),

        'prog': obj.research.project.time_programmins.all(),
        'date_today': date.today(),
        'position': 'Advisor',
        
        'comment_to_expert': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert'),
        'comment_to_applicant': ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant'),
        'comments_to_main_supervisor': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_main_supervisor'),
    }

    return render(request, template_name, context)

def applicant_mentor_detail(request, pk):
    template_name = 'industry/project/myproject/applicant_detail.html'
    obj = get_object_or_404(Mentor, pk=pk)

    comment_to_expert = ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert', seen=False)
    comment_to_applicant = ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant', seen=False)

    for i in comment_to_expert:
        for r in i.comments.filter(seen=False):
            print('22')
            r.seen = True
            r.save()

    for i in comment_to_applicant:
        i.seen = True
        i.save()

    context = {
        'object': obj,
        'meeting_info': ResearchMeeting.objects.filter(project_research=obj.research, status="visible"),
        'supervisors_info': SuperVizor.objects.filter(research=obj.research, status='confirmed'),
        'mentors_info': Mentor.objects.filter(research=obj.research, status='confirmed'),
        'members_info': Member.objects.filter(research=obj.research, status='confirmed'),
        'learners_info': Lerner.objects.filter(research=obj.research, status='confirmed'),

        'prog': obj.research.project.time_programmins.all(),
        'date_today': date.today(),
        'position': 'Mentor',
        
        'comment_to_expert': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert'),
        'comment_to_applicant': ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant'),
        'comments_to_main_supervisor': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_main_supervisor'),
    }

    return render(request, template_name, context)

def applicant_member_detail(request, pk):
    template_name = 'industry/project/myproject/applicant_detail.html'
    obj = get_object_or_404(Member, pk=pk)

    comment_to_expert = ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert', seen=False)
    comment_to_applicant = ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant', seen=False)

    for i in comment_to_expert:
        for r in i.comments.filter(seen=False):
            print('22')
            r.seen = True
            r.save()

    for i in comment_to_applicant:
        i.seen = True
        i.save()

    context = {
        'object': obj,
        'meeting_info': ResearchMeeting.objects.filter(project_research=obj.research, status="visible"),
        'supervisors_info': SuperVizor.objects.filter(research=obj.research, status='confirmed'),
        'mentors_info': Mentor.objects.filter(research=obj.research, status='confirmed'),
        'members_info': Member.objects.filter(research=obj.research, status='confirmed'),
        'learners_info': Lerner.objects.filter(research=obj.research, status='confirmed'),

        'prog': obj.research.project.time_programmins.all(),
        'date_today': date.today(),
        'position': 'Member',
        
        'comment_to_expert': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert'),
        'comment_to_applicant': ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant'),
        'comments_to_main_supervisor': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_main_supervisor'),
    }

    return render(request, template_name, context)

def applicant_learner_detail(request, pk):
    template_name = 'industry/project/myproject/applicant_detail.html'
    obj = get_object_or_404(Lerner, pk=pk)

    comment_to_expert = ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert', seen=False)
    comment_to_applicant = ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant', seen=False)

    for i in comment_to_expert:
        for r in i.comments.filter(seen=False):
            print('22')
            r.seen = True
            r.save()

    for i in comment_to_applicant:
        i.seen = True
        i.save()

    context = {
        'object': obj,
        'meeting_info': ResearchMeeting.objects.filter(project_research=obj.research, status="visible"),
        'supervisors_info': SuperVizor.objects.filter(research=obj.research, status='confirmed'),
        'mentors_info': Mentor.objects.filter(research=obj.research, status='confirmed'),
        'members_info': Member.objects.filter(research=obj.research, status='confirmed'),
        'learners_info': Lerner.objects.filter(research=obj.research, status='confirmed'),

        'prog': obj.research.project.time_programmins.all(),
        'date_today': date.today(),
        'position': 'Learner',
        
        'comment_to_expert': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_expert'),
        'comment_to_applicant': ApplicantComment.objects.filter(project=obj.research, recipient=request.user, sender=obj.research.project.client_form.expert, position='send-to-applicant'),
        'comments_to_main_supervisor': ApplicantComment.objects.filter(project=obj.research, sender=request.user, position='send_to_main_supervisor'),
    }

    return render(request, template_name, context)

def request_project_detail(request, pk):
    template_name = 'industry/project/myproject/request_project_detail.html'
    obj_request = get_object_or_404(RequestUserForProject, pk=pk)
    if request.user == obj_request.user:
        if request.method == 'POST':
            form = DeleteRequestForm(request.POST)
            if form.is_valid():
                status = form.cleaned_data.get('status')
                
                obj_request.status = 'delete'
                obj_request.save()
                return redirect("dashboard-myprojects-reserach")
        service = Service.objects.filter(user=request.user, action='apply-applicant - {}'.format(obj_request.pk), service_name='P').first()
        context = {
            'obj_request': obj_request,
            'inv': Invoice.objects.filter(user=request.user, service=service).first()
        }
        
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")

# Main supervisor


def mainsupervisor_detail(request, pk):
    obj_project = get_object_or_404(ResearchProject, pk=pk)
    template_name = 'industry/project/myproject/main-supervisor-detail.html'


    if request.method == 'POST':

        # Change status
        form_change_status = ChangeStatusProjectForm(request.POST, request.FILES)
        if form_change_status.is_valid():

            final_document = form_change_status.cleaned_data.get("final_document")
            status = form_change_status.cleaned_data.get("status_")
            description = form_change_status.cleaned_data.get("description")

            obj_project.final_document = final_document
            obj_project.text_change_status = description
            obj_project.save()

            if status == 'done':
                messages.error(request,'You must compelete the advertisement form and then continue.')
                    
                return redirect('industry:form-request-change-status-done', obj_project.pk)

            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor requested to move the project to status({})".format(status), event_date=timezone.now(), tracing_project_phase_2=obj_project)
            
            create_obj_tracing = Tracing.objects.create(
                position="{}".format(status), user=request.user, status="{}".format(description), event_date=timezone.now(), tracing_main_supervisor=obj_project)
           
            obj_project.status_change_choices = status
            obj_project.status_change = 'send_to_expert'
            obj_project.save()

            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A status change request is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA status change request is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the director through projecdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_project.project.client_form.expert.get_full_name())
            e_destination = obj_project.project.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
                        
            messages.success(request,'Your request to change the project status has been sent successfully.')
            
        #WBS
        form_report = SendRepoertByMainSupervisorForm(request.POST, )
        if form_report.is_valid():

            id_pr = form_report.cleaned_data.get("id_pr")
            status = form_report.cleaned_data.get("status")
            report = form_report.cleaned_data.get("report")

            report_main_supervisor = get_object_or_404(TimeProgramming, id=id_pr)
            report_main_supervisor.report = report
            report_main_supervisor.status = 'end_of_report'
            report_main_supervisor.save()

            report_main_supervisor.sub.status = 'report'
            report_main_supervisor.sub.save()
            
            # report for time programing

            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor sent her/his report", event_date=timezone.now(), tracing_project_phase_2=obj_project)


            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A new report of project progress is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            
            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA new report of project progress is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to director through projectdirector@tecvico.com.".format(obj_project.project.client_form.expert.get_full_name())
            e_destination = obj_project.project.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)
            
            messages.success(request,'Your report has been sent successfully.')



        # Report project middle
        form_report_project_middle = ProgressReportMiddleProjectForm(request.POST,  request.FILES, )
        if form_report_project_middle.is_valid():
            progress_report_middle_project = form_report_project_middle.cleaned_data.get("progress_report_middle_project")
            
            obj_project.progress_report_middle_project = progress_report_middle_project
            obj_project.save()

            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="The supervisor uploaded the progress report", event_date=timezone.now(), tracing_project_phase_2=obj_project)
            

            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A new project middle report is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA new project middle report is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to director through projectdirector@tecvico.com. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_project.project.client_form.expert.get_full_name())
            e_destination = obj_project.project.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)

            
            messages.success(request,'Your document has been sent successfully.')
        return redirect("industry:mainsupervisor-detail", obj_project.pk)

    context = {
        'obj_project': obj_project,
        'count_request_apply' : RequestUserForProject.objects.filter(status='request', project_request=obj_project, project_request__main_supervisor=request.user).count(),
        'meeting_info': ResearchMeeting.objects.filter(project_research=obj_project, status="visible"),
        "prog": obj_project.project.time_programmins.all(),
        'date_today': date.today(),
        'applicant_list': RequestUserForProject.objects.filter(project_request=obj_project, status='request', project_request__main_supervisor=request.user).order_by("created"),
        'time_zone': pytz.all_timezones,
        
    }
    return render(request, template_name, context)


def detail_send_proposal(request, pk):
    template_name = 'industry/detail-send-proposal.html'
    obj_detail = get_object_or_404(ResearchProject, pk=pk)
    is_supervisor = IndustryExpertForSupervisor.objects.filter(~Q(status="u"), supervisor=request.user, client_form=obj_detail.proposal_supervisor).count()

    if obj_detail.status == 'under_process_supervisor':
        
        form = FormSupervisorAccept(request.POST,  request.FILES, )
        if form.is_valid():
            propzar = form.cleaned_data.get("propzar")
            status = form.cleaned_data.get("status")
    
            if request.user.memberprofile.position != 'Supervisor':
                return redirect("request:supervisor-request")
            else:
                create_obj = IndustryExpertForSupervisor.objects.create(supervisor=request.user, propzar=propzar, client_form=obj_detail.proposal_supervisor, status='not-pay')
                
                return PaymentProtocol(request, 'P', create_obj.client_form.formclint, 150 , action='proposal-supervisor-{}'.format(create_obj.id))
    
                return redirect('industry:detail-send-proposal', obj_detail.pk)

        context = {
            'obj_detail': obj_detail,
            'is_supervisor': is_supervisor,
        }
        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")


def pay_proposal_supervisor(user, pk):
    obj_supervisor = get_object_or_404(IndustryExpertForSupervisor, pk=pk)
    
    obj_supervisor.status = 'a'
    obj_supervisor.save()
    

    e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, ) 
    e_content ="Dear {} \nHello\nHope you are going well. \nYour proposal has been sent to TECVICO in order to be assessed by reviewers successfully. We will inform the response of the reviewers to you in 2 weeks. \nTitle: {} \nSubmitted date: {} \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_supervisor.supervisor.get_full_name(), obj_supervisor.client_form.formclint.title, date.today(), obj_supervisor.client_form.expert.researchrole.expert_email_address)
    e_destination = obj_supervisor.supervisor.email
    send_new_email(e_subject,e_content,e_destination)
    

    
    e_subject ="TECVICO Project (Project ID: {})".format(obj_supervisor.client_form.formclint.id_project, )  
    e_content ="Dear {}\nHello\nHope you are going well. \nA supervisor submitted a proposal for the below project successfully. Please go to your dashboard and observe it.\nTitle: {}\nSubmitted date: {}\nDo not reply to this Email. If you have any question or concern, please feel free to contact the director through projectdirector@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp.\n".format(obj_supervisor.client_form.expert.get_full_name(), obj_supervisor.client_form.formclint.title, date.today())
    e_destination = obj_supervisor.client_form.expert.researchrole.expert_email_address
    send_new_email(e_subject,e_content,e_destination)
                
                
    
def selecting_supervisor_detail(request, pk):
    template_name = 'industry/project/selecting-supervisor-detail.html'
    obj_project = get_object_or_404(ResearchProject, pk=pk)
    context = {
        'obj_project': obj_project,
    }
    return render(request, template_name, context)
    
    
    
    
    
    
    
    
    
    
    
    