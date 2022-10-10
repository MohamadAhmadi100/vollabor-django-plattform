from django.shortcuts import render, redirect,get_object_or_404
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from datetime import timedelta
import datetime
import pytz
from django.utils import timezone
from django.http import Http404
from seo.models import UserFootprint
from Q_And_A.models import QuestionAnswerManager, Question, Answer
from coin.models import PersonExperienceBadge, ExperienceBadge
from dashboard.project_request_handler import *
from ivc_website.forms import ProjectForm, ProjectContractReplyForm, ProjectProposalForm, EventForm, ProjectInfoForm, NewsForm, CategoryForm
from ivc_website.models import Visitor, project_type_choices, project_classes,NewsManager, News, Event
from join.models import Applicant, LegalApplicant
from users.forms import PhoneNumberForm, SkypeForm, PreferenceForm
from users.models import Role
from .forms import EditProjectForm, AnnouncementForm, MeetingForm, UploadMemberContractForm, ChangeDeadLineResearch, DeleteRequestForm, AcceptCommentResearch, RejectCommentResearch
from .models import Announcement, AnnouncementView, WeeklyMeetingTime, WeeklyMeetingAttendee, CompanyCollaboration, \
    ProjectRating, UserEmail, ProjectContractItem, ApplicantManager, ProjectExpertAreaItem, \
    ExpertAreaItem, ProposalComment, AdFormWS
from users.models import interest_choices, field_of_study_choices, degree_choices, status_choices, Expert, ExpertArea, \
    ResearchExpert, CompanyMail, Interviewer
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from dashboard.utils.research_expert_utility import *
from .utilities import *
from django.db.models import ObjectDoesNotExist

from .utils.contract_handler import send_contract_to_owner_and_wait_for_signature, save_contract_response, \
    accept_contract, \
    is_user_eligible_to_send_contract, change_state_after_contract_if_necessary, inform_superuser_if_necessary
from .utils.contract_pdf_handler import create_contract
from .utils.new_industrial_projects_handlers import *
from .utils.notification_handlers import *
from .utils.project_management_handler import get_average_of_proposal_score, \
    send_notification_to_collaborators_below_the_coin
from .utils.proposal_handler import *
from .utils.search_handlers import *
from .utils.form_submission_handlers import *
from .utils.project_request_page_handlers import *
from .utils.projects_page_handlers import *
from ivc_project.email_sender import send_new_email
from forum.models import Postes, Category, MainCategory
from django.views.generic import ListView
from django.core.mail import EmailMessage
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from cartable.models import Staff
from django.contrib.auth.models import User
from workshop.models import Guarante, Comment, AcceptReject, Workshop
from research.models import *
from research.mixins import SecurityClientDetail, SecurityExpertDetail, SecuritySupervisorDetail, SecurityProjectResearchDetail

from forum.forms import (
    SendComment, SendReplyComment, CreateTopic, CreateCategoryForm, EditForm, 
    DeleteTopicForm, DeleteCommentForm, DeleteReplyCommentForm, DeleteCategory, 
    DeleteSubCategory, EditCategory, EditSubCategory, CreateSubCategoryForm
    )

from research.forms import *
from django.views.generic import ListView, DetailView
from datetime import date
from request.models import (
    BadgeRequest, BadgeInterviewReview, SupervisorRequest, SupervisorReview, InterviewSession, 
    WorkshopRequest, WorkshopReview, BadgeExpert, 
    )

from payment_stripe.models import Dollar
from accounting.models import Service, Invoice

def is_mentor_or_supervisor(user):
    return user.is_authenticated and user_has_memberprofile(user) and (user.memberprofile.position == "Mentor" or
                                                                       user.memberprofile.position == "Supervisor")


def is_superuser(user):
    return user.is_superuser


def is_mentor_or_supervisor_or_superuser(user):
    return is_mentor_or_supervisor(user) or is_superuser(user)


def has_member_access(user):
    return MemberProfile.objects.filter(user=user, position='Supervisor').count() or \
           user.memberprofile.special_member_access or \
           Expert.objects.filter(user=user).count() or user.is_superuser


def user_has_memberprofile(given_user):
    return MemberProfile.objects.filter(user=given_user).count() == 1


def notification(request):
    """
    NOTIFICATION CONTEXT PROCESSOR
    this is a context processor that django executes on every page load and when user is logged in, it gets his requests
    * notice that we have to import it on project settings/TEMPLATES/OPTIONS/context_processors
    """
    if request.user.is_anonymous:  # if user is not logged in
        return {}

    notif_dictionary = {
        "notifications": {
            "first_five": Notification.objects.filter(target=request.user)[:5],
            'count': Notification.objects.filter(target=request.user, seen=False).count()
        }
    }

    if request.POST and 'notif-pk' in request.POST:  # if user has clicked to open a notification
        notification_link = make_notification_seen(notification_pk=int(request.POST['notif-pk']))
        return redirect(notification_link)

    return notif_dictionary


def notification_page(request):
    """
    A page that shows all notifications for a request.user
    user can filter notifications to seen and unseen and mark them all as read
    """
    if request.POST:
        if 'notif-page-pk' in request.POST:  # user selects to see a new notif
            notification_link = make_notification_seen(notification_pk=int(request.POST['notif-page-pk']))
            return redirect(notification_link)
        if 'mark-seen' in request.POST:  # mark all notification of the user as seen
            Notification.objects.filter(seen=False, target=request.user).update(seen=True)
        if 'delete-all' in request.POST:
            Notification.objects.filter(target=request.user).delete()

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    page_notification = get_notification_of_user(request)
    filters = ['all', 'unseen']
    context = {
        'filters': filters,
        'page_notification': page_notification
    }

    return render(request, 'dashboard/notification.html', context)


@login_required
def unsubscribe(request, project_pk):
    project = Project.objects.get(pk=project_pk)
    if UnSubscriber.objects.filter(user=request.user, project=project).count() == 0:
        UnSubscriber(user=request.user, project=project).save()
        messages.success(request, 'Project has been unsbscribed successfully')

    return redirect(reverse('dashboard-page'))


@login_required
def dashboard(request):
    user_obj = request.user
    if user_obj.memberprofile.image is None and user_obj.memberprofile.field_of_study is None and user_obj.memberprofile.status is None and user_obj.memberprofile.degree is None and \
    user_obj.memberprofile.interest is None and user_obj.memberprofile.about_me is None and user_obj.memberprofile.birthday is None and user_obj.memberprofile.gender is None and \
    user_obj.memberprofile.time_can_spend_per_day is None and user_obj.memberprofile.phone is None and user_obj.memberprofile.university is None and user_obj.memberprofile.city is None and \
    user_obj.memberprofile.country is None and user_obj.memberprofile.cv_file is None and user_obj.memberprofile.skype is None :
        user_obj.memberprofile.check_all = False
    else:
        user_obj.memberprofile.check_all = True
        
    # return HttpResponse(user_obj.memberprofile.check_all)
        
    user_obj.memberprofile.save()
    
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all is False:  # user has to complete his/her profile to see this page
              messages.error(request,'Please fillout your profile')
    #         return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    #         return redirect("dashboard-page")

    # elif request.user.legalprofile.work_area is None:
    #     return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    #     return redirect("dashboard-page")

    if request.method == "POST":
        if 'seen-email-info' in request.POST:
            mail = CompanyMail.objects.get(user=request.user)
            mail.has_seen = True
            mail.save()
        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context = {}
    


    x = timezone.now()
    roles = ResearchRole.objects.all()
    review = IndustryReviewer.objects.filter(status='new_project')
    for r in review:
        if x > r.create + timedelta(2):
            if r.object_client:
                r.status = 'not_see_project'
                r.object_client.status = 'reject_reviewer'
                r.save()
                r.object_client.save()
                for i in roles:
                    if i.director == True:
                        e_subject = "TECVICO Research (Project ID: {})".format(r.object_client.id_project)
                        e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer's confirmation namely {} has expired and no response has been received from him. For this reason, the project was returned.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(i.user.get_full_name(), r.reviewer.get_full_name())
                        e_destination = obj_expert.user.email
                        send_new_email(e_subject,e_content,e_destination)

                        
                
            if r.object_expert:
                r.status = 'not_see_project'
                r.object_expert.formclint.status = 'reviewer_special_expert'
                r.save()
                r.object_expert.formclint.save()

                e_subject = "TECVICO Research (Project ID: {})".format(r.object_expert.formclint.id_project)
                e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer's confirmation namely {} has expired and no response has been received from him. For this reason, the project was returned.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(r.object_expert.expert.get_full_name(), r.reviewer.get_full_name())
                e_destination = r.object_expert.expert.email
                send_new_email(e_subject,e_content,e_destination)

            e_subject = "TECVICO Research (Project ID: {})".format(r.object_client.id_project)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your confirmation has expired and no response has been received from you, the project has been withdrawn from you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
            e_destination = r.reviewer.email
            send_new_email(e_subject,e_content,e_destination)



    review = IndustryReviewer.objects.filter(status='accept_project')
    for r in review:
        if x > r.create + timedelta(8):
            if r.object_client:
                r.status = 'breach_of_promis'
                r.object_client.status = 'reject_reviewer'
                r.save()
                r.object_client.save()

                r.reviewer.researchrole.count_breach_of_promis_reviewer += 1
                r.reviewer.researchrole.save()
                for i in roles:
                    if i.director == True:
                        e_subject = "TECVICO Research (Project ID: {})".format(r.object_client.id_project)
                        e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer/interviewer's evaluation namely {} has expired and no response has been received from him. For this reason, the project was returned and a negative point considered for him/her.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(i.user.get_full_name(), r.reviewer.get_full_name())
                        e_destination = obj_expert.user.email
                        send_new_email(e_subject,e_content,e_destination)

            if r.object_expert:
                r.status = 'breach_of_promis'
                r.object_expert.formclint.status = 'reviewer_special_expert'
                r.save()
                r.object_expert.formclint.save()

                r.reviewer.researchrole.count_breach_of_promis_reviewer += 1
                r.reviewer.researchrole.save()

                e_subject = "TECVICO Research (Project ID: {})".format(r.object_expert.formclint.id_project)
                e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer/interviewer's evaluation namely {} has expired and no response has been received from him. For this reason, the project was returned and a negative point considered for him/her.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(r.object_expert.expert.get_full_name(), r.reviewer.get_full_name())
                e_destination = r.object_expert.expert.email
                send_new_email(e_subject,e_content,e_destination)

            e_subject = "TECVICO Research (Project ID: {})".format(r.object_client.id_project)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your evaluation has expired and no response has been received from you, the project has been withdrawn from you and considered a negative point for you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
            e_destination = r.reviewer.email
            send_new_email(e_subject,e_content,e_destination)
            
            
        if x > r.create + timedelta(6):
            if r.object_client:
                e_subject = "TECVICO Research (Project ID: {})".format(r.object_client.id_project)
                e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nYou have two days until your deadline to send the evaluation expires, please send the evaluation as soon as possible. The consequences of not sending it are up to you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
                e_destination = r.reviewer.email
                send_new_email(e_subject,e_content,e_destination)


            if r.object_expert:
                e_subject = "TECVICO Research (Project ID: {})".format(r.object_expert.formclint.id_project)
                e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nYou have two days until your deadline to send the evaluation expires, please send the evaluation as soon as possible. The consequences of not sending it are up to you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
                e_destination = r.reviewer.email
                send_new_email(e_subject,e_content,e_destination)



    review = IndustryReviewer.objects.filter(status='n')
    for r in review:
        if x > r.create + timedelta(2):
            r.status = 's'
            r.object_supervisor.status = 'v'
            r.object_supervisor.client_form.status = 'review'
            r.save()
            r.object_supervisor.save()
            r.object_supervisor.client_form.save()

            e_subject = "TECVICO Research (Project ID: {})".format(r.client_form.formclint.id_project)
            e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer's confirmation namely {} has expired and no response has been received from him. For this reason, the project was returned.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(r.client_form.expert.get_full_name(), r.reviewer.get_full_name())
            e_destination = r.client_form.expert.email
            send_new_email(e_subject,e_content,e_destination)

            e_subject = "TECVICO Research (Project ID: {})".format(r.client_form.formclint.id_project)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your confirmation has expired and no response has been received from you, the project has been withdrawn from you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
            e_destination = r.reviewer.email
            send_new_email(e_subject,e_content,e_destination)
            
            
    review = IndustryReviewer.objects.filter(status='a')
    for r in review:
        if x > r.create + timedelta(8):
            r.status = 'breach_of_promis_p'
            r.object_supervisor.status = 'v'
            r.object_supervisor.client_form.status = 'review'
            r.save()
            r.object_supervisor.save()
            r.object_supervisor.client_form.save()

            r.reviewer.researchrole.count_breach_of_promis_reviewer += 1
            r.reviewer.researchrole.save()

            e_subject = "TECVICO Research (Project ID: {})".format(r.client_form.formclint.id_project)
            e_content = "Dear {}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer/interviewer's evaluation namely {} has expired and no response has been received from him. For this reason, the project was returned and a negative point considered for him/her.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(r.client_form.expert.get_full_name(), r.reviewer.get_full_name())
            e_destination = r.client_form.expert.email
            send_new_email(e_subject,e_content,e_destination)

            e_subject = "TECVICO Research (Project ID: {})".format(r.client_form.formclint.id_project)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your evaluation has expired and no response has been received from you, the project has been withdrawn from you and considered a negative point for you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
            e_destination = r.reviewer.email
            send_new_email(e_subject,e_content,e_destination)
            
            
        if x > r.create + timedelta(6):
            e_subject = "TECVICO Research (Project ID: {})".format(r.client_form.formclint.id_project)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nYou have two days until your deadline to send the evaluation expires, please send the evaluation as soon as possible. The consequences of not sending it are up to you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.reviewer.get_full_name())
            e_destination = r.reviewer.email
            send_new_email(e_subject,e_content,e_destination)


            
    table_time_programming = TimeProgramming.objects.all()
    for i in table_time_programming:
        if i.status !='end_of_report' and i.end_date == date.today():
            i.status = 'send_report'
            i.save()


    table_time_programming = TimeProgramming.objects.all()
    for i in table_time_programming:
        if i.status in ['none', 'send_report'] and i.end_date < date.today():
            i.status = 'unanswered'
            i.save()
            e_subject = "TECVICO Research (Project ID: {})".format(i.sub.client_form.formclint.id_project)
            e_content = "Dear {supervisor}\n\nHello\nHope you are going well.\nYour time to submit a progress report has expired and you have been denied the opportunity to submit a report. Contact the expert to coordinate to resolve the block through {email_expert}.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(supervisor = i.sub.supervisor.get_full_name(), email_expert = i.sub.client_form.expert.email)
            e_destination = i.sub.supervisor.email
            send_new_email(e_subject,e_content,e_destination)



    super_visor = IndustryExpertForSupervisor.objects.filter(status='u')
    for s in super_visor:
        if s.client_form.deadline:
            if date.today() > s.client_form.deadline :
                s.status = 'not_see'
                s.save()
        # if date.today() ==  s.client_form.deadline - timedelta(1):
        #     e_subject = "TECVICO Research (Project ID: {})".format(s.client_form.formclint.id_project)
        #     e_content = "Dear {supervisor}\n\nHello\nHope you are going well.\nYou have 24 hours to send your proposal, please send it as soon as possible. The consequences of not sending it are up to you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(supervisor = s.supervisor.get_full_name())
        #     e_destination = s.supervisor.email
        #     send_new_email(e_subject,e_content,e_destination)
    
    
    

    # Deadline revised supervisor
    obj_supervisors = IndustryExpertForSupervisor.objects.filter(status='b')
    for i in obj_supervisors:
        if i.deadline:
            if date.today() > i.deadline :
                i.status = 'not_response_proposal'
                i.client_form.formclint.follow_project = 'p_main_not_response_revised_proposal'
                i.save()
                i.client_form.formclint.save()

                    
                if i.client_form.formclint.main_supervisor:
                    create_obj_tracing = Tracing.objects.create(
                        position='Supervisor', user=i.supervisor, status="not response", event_date=timezone.now(), tracing_project=i.client_form.formclint)
                    
    review_badge = BadgeInterviewReview.objects.filter(accept_reject='new')
    for r in review_badge:
        if x > r.created + timedelta(2):
            id_request = r.badge
            r.accept_reject = 'not_see'
            r.badge.status = 'decline-review-interview'

            r.save()
            r.badge.save()

            obj_expert = BadgeExpert.objects.get(badge=id_request)

            e_subject = "TECVICO request (ID: {u_id})".format(u_id = r.badge.unique_id)
            e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your confirmation has expired and no response has been received from you, the project has been withdrawn from you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = r.user.get_full_name())
            e_destination = r.user.email
            send_new_email(e_subject,e_content,e_destination)

            Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = r.badge.unique_id),
                description = "Due to the fact that the deadline for sending your confirmation has expired and no response has been received from you, the project has been withdrawn from you.",
                target = r.user,
                link = reverse('notification-page'))


            e_subject = "TECVICO request (ID: {u_id})".format(u_id = r.badge.unique_id)
            e_content = "Dear {expert}\n\nHello\nHope you are going well.\nDue to the fact that the deadline for sending your confirmation has expired and no response has been received from you, the project has been withdrawn from you.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = r.user.get_full_name())
            e_destination = obj_expert.user.email
            send_new_email(e_subject,e_content,e_destination)


            Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = r.badge.unique_id),
                description = "The deadline for sending the reviewer's confirmation namely {} has expired and no response has been received from him. For this reason, the project was returned.".format(r.user.get_full_name()),
                target = obj_expert.user,
                link=reverse('request:select-interviewer-or-reviewer', args=[r.badge.pk])).save()


    review_badge = BadgeInterviewReview.objects.filter(accept_reject='approve')
    for r in review_badge:
        if x > r.created + timedelta(8):
            id_request = r.badge
            r.accept_reject = 'breach_of_promis'
            r.badge.status = 'decline-review-interview'
            r.user.researchrole.count_breach_of_promis_reviewer_request += 1
            r.user.researchrole.count_evaluated_reviewer_request - 1
            r.save()
            r.badge.save()
            r.user.researchrole.save()

            obj_expert = BadgeExpert.objects.get(badge=id_request)

            e_subject = "TECVICO request (ID: {u_id})".format(u_id = r.badge.unique_id)
            e_content = "Due to the fact that the deadline for sending your evaluation has expired and no response has been received from you, the project has been withdrawn from you and a negative point considered for you."
            e_destination = r.user.email
            send_new_email(e_subject,e_content,e_destination)


            Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = r.badge.unique_id),
                description = "Due to the fact that the deadline for sending your evaluation has expired and no response has been received from you, the project has been withdrawn from you and a negative point considered for you.",
                target = r.user,
                link = reverse('notification-page'))



            e_subject = "TECVICO request (ID: {u_id})".format(u_id = r.badge.unique_id)
            e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe deadline for sending the reviewer/interviewer's evaluation namely {reviewer} has expired and no response has been received from him. For this reason, the project was returned and a negative point considered for him/her.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_expert.user.get_full_name(), reviewer = r.user.get_full_name())
            e_destination = obj_expert.user.email
            send_new_email(e_subject,e_content,e_destination)


            Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = r.badge.unique_id),
                description = "The deadline for sending the reviewer/interviewer's evaluation namely {} has expired and no response has been received from him. For this reason, the project was returned and a negative point considered for him/her.".format(r.user.get_full_name()),
                target = obj_expert.user,
                link=reverse('request:select-interviewer-or-reviewer', args=[r.badge.pk])).save()
                
                
                
    context['research_review_count'] = IndustryReviewer.objects.filter(status__in=['n', 'a', 'new_project', 'accept_project', 'revise_by_expert', 'revise_by_director' 'revise_by_expert_p', 'revise_by_director_p'], reviewer=request.user).count()
    context['superuser_research_review_count'] = IndustryReviewer.objects.filter(status='n').count()


    # under process
    context['count_all_director'] = IndustryFormClient.objects.filter(
    project_created=False, 
    status__in=['n', 'e', 's', 'm', 'd', 'accept_or_reject_expert', 'created', 'hidden', 'accept_reviewer', 'reject_reviewer', 'expert_reviewer']
    ).count()
    """
    gets request numbers: number of projects that their mentors or supervisors want our user to be part of their project 
    """
    context['research_request_numbers'] = get_research_request_numbers(request.user)
    context['industrial_request_numbers'] = get_industrial_request_numbers(request.user)
    context['competition_request_numbers'] = get_competition_request_numbers(request.user)
    context['total_request_numbers'] = context['industrial_request_numbers'] + context['research_request_numbers'] \
                                       + context['competition_request_numbers']

    """
    collaborated project numbers
    """
    context['research_collaborated_numbers'] = Project.objects.filter(
        Q(project_type='Research', main_supervisor=request.user) |
        Q(project_type='Research', projectsupervisor__supervisor=request.user,
          projectsupervisor__state='Collaborator') |
        Q(project_type='Research', projectmentor__mentor=request.user, projectmentor__state='Collaborator') |
        Q(project_type='Research', projectmember__member=request.user, projectmember__state='Collaborator') |
        Q(project_type='Research', projectlearner__learner=request.user, projectlearner__state='Collaborator')) \
        .distinct().count()

    context['competition_collaborated_numbers'] = Project.objects.filter(
        Q(project_type='Competition', main_supervisor=request.user) |
        Q(project_type='Competition', projectsupervisor__supervisor=request.user,
          projectsupervisor__state='Collaborator') |
        Q(project_type='Competition', projectmentor__mentor=request.user, projectmentor__state='Collaborator') |
        Q(project_type='Competition', projectmember__member=request.user, projectmember__state='Collaborator') |
        Q(project_type='Competition', projectlearner__learner=request.user, projectlearner__state='Collaborator')) \
        .distinct().count()

    context['industrial_collaborated_numbers'] = Project.objects.filter(
        Q(project_type='Industrial', main_supervisor=request.user) |
        Q(project_type='Industrial', projectsupervisor__supervisor=request.user,
          projectsupervisor__state='Collaborator') |
        Q(project_type='Industrial', projectmentor__mentor=request.user, projectmentor__state='Collaborator') |
        Q(project_type='Industrial', projectmember__member=request.user, projectmember__state='Collaborator') |
        Q(project_type='Industrial', projectlearner__learner=request.user, projectlearner__state='Collaborator')) \
        .distinct().count()
    context['total_collaborated_numbers'] = context['research_collaborated_numbers'] + \
                                            context['competition_collaborated_numbers'] + \
                                            context['industrial_collaborated_numbers']

    """
    get announcement numbers: number of announcement that user hasn't seen them
    """
    context['announcement_numbers'] = Announcement.objects.exclude(
        announcementview__user=request.user).count()

    """
    Contract numbers
    """
    context['total_contract_numbers'] = ProjectContract.objects.filter(user=request.user, valid=True).count()
    context['unseen_contract_numbers'] = ProjectContract.objects.filter(user=request.user,
                                                                        reply_has_been_sent=False, valid=True).count()

    is_applicant = ApplicantManager.objects.filter(user=request.user).count()
    context['is_applicant'] = is_applicant
    if is_applicant:
        pass
        # context['applicant_numbers'] = Applicant.objects.filter(is_valid=True).count() + \
        #                               LegalApplicant.objects.filter(is_valid=True).count()

    """
    for superusers
    """
    if request.user.is_superuser:
        # Visitors :
        week_list = []
        visitor_list = []
        for i in reversed(range(7)):
            week = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(i), '%a')
            exact_date = datetime.date.today() - datetime.timedelta(i)
            visitor_list.append(Visitor.objects.filter(visit_date=exact_date).count())
            week_list.append(week)
        context['week_list'] = week_list
        context['visitor_list'] = visitor_list

    is_expert = Expert.objects.filter(user=request.user).count()
    if is_expert:
        context['industrial_numbers'] = get_new_industrial_projects(request.user).count()
        context['recently_added_expertises_numbers'] = IndustrialArea.objects.filter(
            ~Q(expertarea__expert__user=request.user) & Q(confirmed=True)).count()
        context['project_corresponding_expert_numbers'] = Project.objects.filter(Q(expert=request.user,
                                                                                   project_type="Industrial")
                                                                                 & ~Q(status="Rejected")).count()
    is_research_expert = ResearchExpert.objects.filter(user=request.user).count()

    if is_research_expert:
        context['project_research_expert_numbers'] = Project.objects.filter(Q(expert=request.user,
                                                                              project_type="Research")
                                                                            & ~Q(status="Rejected")).count()

    if is_research_expert or is_expert:
        context['project_reviewers'] = Reviewer.objects.filter(user=request.user).count()
        context['unseen_proposal_numbers'] = get_unseen_proposal_numbers(request.user)

    context['is_question_answer_manager'] = QuestionAnswerManager.objects.filter(user=request.user).count()
    if context['is_question_answer_manager']:
        context['unverified_question_numbers'] = Question.objects.filter(is_verified=None).count()
        context['unverified_answer_numbers'] = Answer.objects.filter(is_verified=None).count()
    context['count_report_by_director'] = IndustryExpertForSupervisor.objects.filter(status='report_d').count()
    context['has_not_seen_email'] = CompanyMail.objects.filter(user=request.user, has_seen=False).count()
    if context['has_not_seen_email']:
        context['email_info'] = CompanyMail.objects.get(user=request.user)

    context['is_interviewer'] = Interviewer.objects.filter(user=request.user).count()
    user = request.user
    context['user'] = user
    roles = Role.objects.filter(user=user)
    staff = Staff.objects.all()
    context['staff'] = staff
    context['roles'] = roles
    guarante = Guarante.objects.all()
    context['guarante'] = guarante
    news_manager = NewsManager.objects.all()
    manager_list = []
    for item in news_manager:
        manager_list.append(item.manager)
    context['news_manager'] = manager_list
    user_role = []
    for role in roles:
        user_role.append(role.position)
    context['user_role'] = user_role
    
    
# workshop card counter number
    #director
    workshops_status=['Guarante_accept','Send_contract_to_director']
    workshops = Workshop.objects.filter(status__in = workshops_status).count()
    pending = []
    pending_list = Comment.objects.all()
    for item in pending_list:
        if item.workshop.status == 'Expert_comment' or item.workshop.status == 'Expert_decide':
            pending.append(item)
        elif item.workshop.status == 'Guarante_accept' and item.status == 'Decline':
            pending.append(item)

    acc_rej = Comment.objects.filter(workshop__status = "Manager_check", status = 'Approve').count()
    
    context['director_workshop_number'] = workshops + acc_rej + len(pending)
    
    #expert
    comments = Comment.objects.filter(expert=request.user)
    comment_workshop = []
    #add_video = []
    accept_reject = []
    for cm in comments:
        # if cm.is_checked == False and cm.status != 'Decline':
        #     comment_workshop.append(cm)
        # if cm.workshop.status == 'Revise_to_expert' or cm.workshop.status == 'Approve_contract' or cm.workshop.status == 'Send_contract_by_supervisor' and cm.workshop.status == 'Revise_contract_to_expert' :
        #     comment_workshop.append(cm)
        """if cm.workshop.status == "Accept" and cm.status == "Approve":
            #acc_work_ex.append(cm.workshop)
            if cm.workshop.date <= timezone.now().date():
                add_video.append(cm.workshop)"""
        if cm.access == True and cm.status == "Approve":
            if cm.workshop.status == "Manager_check":
                accept_reject.append(cm)
  

    all_workshop_expert_status=['Expert_decide','reject_expert','Expert_comment','Revise_to_expert','Approve_contract','Send_contract_by_supervisor','Revise_contract_to_expert','send_contract_to_supervisor']
    all_workshop_expert=Workshop.objects.filter(status__in=all_workshop_expert_status)
    for w in all_workshop_expert:
        comments = Comment.objects.filter(workshop=w).first()
        if comments.expert == request.user:
            comment_workshop.append(comments)

    
    context['expert_workshop_number'] = len(comment_workshop) + len(accept_reject)
    
    #supervisor
    context['supervisor_workshop_number'] =  Workshop.objects.filter(top_user = request.user).count()
    
    
    # end

  
    
    # ----> Dorector management <---- #

    # Report
    report_project_count = ResearchProject.objects.filter(~Q(status__in=["done", 'delete']), project__status='report_d', project__view_report=False).order_by('-created').count()

    # Change status
    change_status_count = ResearchProject.objects.filter(status_change='send_to_director').order_by('-created').count()


    # Applicant contract
    advisor_count = SuperVizor.objects.filter(status__in=['send-to-director'],).count()
    mentor_count = Mentor.objects.filter(status__in=['send-to-director'],).count()
    member_count = Member.objects.filter(status__in=['send-to-director'],).count()
    learner_count = Lerner.objects.filter(status__in=['send-to-director'], ).count()
    applicant_cart_count = advisor_count + mentor_count + member_count + learner_count 


    # Applicant removal
    advisor_remove_count = SuperVizor.objects.filter(status_remove='request-remove-send-to-the-director').count()
    mentor_remove_count = Mentor.objects.filter(status_remove='request-remove-send-to-the-director').count()
    member_remove_count = Member.objects.filter(status_remove='request-remove-send-to-the-director').count()
    learner_remove_count = Lerner.objects.filter(status_remove='request-remove-send-to-the-director' ).count()
    applicant_remove_cart_count = advisor_remove_count + mentor_remove_count + member_remove_count + learner_remove_count

    context['count_manage_project_director'] = report_project_count + change_status_count + applicant_cart_count + applicant_remove_cart_count

    # ----> Expert management <---- #

    # comments
    count = 0
    count_meesage_applicant = ApplicantComment.objects.filter(position='send_to_expert', seen=False).count()

    for i in ApplicantComment.objects.filter(position='send-to-applicant'):
        for e in i.comments.filter(seen=False):
            if i.project.project.client_form.expert == request.user:
                count += 1
    applicant_comment_count = count_meesage_applicant + count

    # Applicant removal
    advisor__remove_count = SuperVizor.objects.filter(status_remove='request-remove', research__project__client_form__expert=request.user).count()
    mentor__remove_count = Mentor.objects.filter(status_remove='request-remove', research__project__client_form__expert=request.user).count()
    member__remove_count = Member.objects.filter(status_remove='request-remove', research__project__client_form__expert=request.user).count()
    learner__remove_count = Lerner.objects.filter(status_remove='request-remove', research__project__client_form__expert=request.user).count()
    applicant_remove_cart_count = advisor__remove_count + mentor__remove_count + member__remove_count + learner__remove_count


    # Applicant contract
    advisor_count = SuperVizor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=request.user).count()
    mentor_count = Mentor.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=request.user).count()
    member_count = Member.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=request.user).count()
    learner_count = Lerner.objects.filter(status__in=['new', 'revised-director-to-expert', 'send-contract-to-expert', 'not-response'], research__project__client_form__expert=request.user).count()
    applicant_contract_count = advisor_count + mentor_count + member_count + learner_count 

    # Report
    count_report_projects_object = ResearchProject.objects.filter(~Q(status__in=["done", 'delete']), project__status='report', project__client_form__expert=request.user).order_by("-created").count()

    # Change status
    count_project_change_status = ResearchProject.objects.filter(status_change='send_to_expert', project__client_form__expert=request.user).order_by("-created").count()

    context['count_manage_project_expert'] = applicant_comment_count + applicant_remove_cart_count + applicant_contract_count + count_report_projects_object + count_project_change_status


    
    
    #---- count expert ----#
    context['count_expert_cart'] = IndustryFormExpert.objects.filter(
        ~Q(formclint__status__in=["r", "rejected_by_expert", 'withdrew']), expert=request.user, formclint__project_created=False).count()
            
        
    context['count_comment_research'] = CommentProject.objects.filter(status='new').count()


    context['count_activity_all'] = Postes.objects.all().count()
    context['count_activity'] = Postes.objects.filter(author=request.user).count()

    request_suervisor_e_count = SupervisorRequest.objects.filter(expert=request.user).count()
    request_workshop_e_count = WorkshopRequest.objects.filter(expert=request.user).count()
    request_badge_e_count = BadgeExpert.objects.filter(user=request.user).count()

    request_suervisor_r_count = SupervisorReview.objects.filter(user=request.user).count()
    request_workshop_r_count = WorkshopReview.objects.filter(user=request.user).count()
    request_badge_r_count = BadgeInterviewReview.objects.filter(user=request.user).count()
    

    request_suervisor_m_count = WorkshopRequest.objects.all().count()
    request_workshop_m_count = SupervisorRequest.objects.all().count()
    request_badge_m_count = BadgeRequest.objects.all().count()
    

    context['request_expert_count'] = request_suervisor_e_count + request_workshop_e_count + request_badge_e_count
    context['request_reviewer_count'] = request_suervisor_r_count + request_workshop_r_count + request_badge_r_count
    context['request_manager_count'] = request_suervisor_m_count + request_workshop_m_count + request_badge_m_count
     

    suggestion_cart_count = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=request.user, client_form__formclint__fund__gt=0).order_by("-created").count()
    revise_cart_count = IndustryExpertForSupervisor.objects.filter(status__in=['b', 'h'], supervisor=request.user).count()
    contract_cart_count = IndustryExpertForSupervisor.objects.filter(status__in=['t', 'reject_contract'], supervisor=request.user).order_by("-created").count()

    new_contract_advisor_count = SuperVizor.objects.filter(user=request.user, status='send-contract').count()
    new_contract_mentor_count = Mentor.objects.filter(user=request.user, status='send-contract').count()
    new_contract_member_count = Member.objects.filter(user=request.user, status='send-contract').count()
    new_contract_learner_count = Lerner.objects.filter(user=request.user, status='send-contract').count()
    revise_contract_advisor_count = SuperVizor.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_mentor_count = Mentor.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_member_count = Member.objects.filter(user=request.user, status='revised_by_expert').count()
    revise_contract_learner_count = Lerner.objects.filter(user=request.user, status='revised_by_expert').count()

    contract_cart_count = IndustryExpertForSupervisor.objects.filter(status__in=['t', 'reject_contract'], supervisor=request.user).order_by("-created").count() + + new_contract_advisor_count + new_contract_mentor_count + new_contract_member_count + new_contract_learner_count + revise_contract_advisor_count + revise_contract_mentor_count + revise_contract_member_count + revise_contract_learner_count
    context['myp_project_count'] = suggestion_cart_count + revise_cart_count + contract_cart_count 
        
        
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def research_director_panel(request):
    if not user_has_memberprofile(request.user) or not request.user.memberprofile.is_research_director:
        return render(request, 'ivc_website/403.html')

    if request.method == "POST":
        if 'accept-contract-to-be-main-supervisor' in request.POST:
            project_is_not_elected_in_front_end = not 'project' in request.GET
            if project_is_not_elected_in_front_end:  # SECURITY CHECK
                return HttpResponseRedirect(request.path_info)

            project_pk = request.GET.get('project')
            project = Project.objects.get(pk=project_pk)

            user_pk = request.POST.get('accept-contract-to-be-main-supervisor')
            user = User.objects.get(pk=user_pk)

            project.main_supervisor = user
            project.save()

            project_supervisor = ProjectSupervisor.objects.get(supervisor=user, project=project)
            project_supervisor.state = "Idle"
            project_supervisor.save()

            messages.success(request, "Main supervisor has been assigned successfully.")

            return HttpResponseRedirect(request.path_info)

        if 'accept-project-after-review' in request.POST:
            project_is_not_elected_in_front_end = not 'project' in request.GET
            if project_is_not_elected_in_front_end:  # SECURITY CHECK
                return HttpResponseRedirect(request.path_info)

            try:
                project_value = float(request.POST.get('project-value'))
            except ValueError:
                messages.error(request, 'Project value is invalid')
                return HttpResponseRedirect(request.path_info)  # redirect to the same page

            """
            ---- Assign project-class for each proposal ----
            For each proposal, we send a project-proposal-pk-x from the frontend, which x is just a number.
            then we send project-proposal-class-x at the same time and then here we assign the given class to the given
            proposal.
            """
            for key in request.POST:
                if 'project-proposal-pk' in key:
                    proposal_number = key.split('-')[-1]
                    project_proposal_class = 'project-proposal-class-' + proposal_number
                    project_proposal_pk = request.POST.get(key)
                    selected_project_proposal = ProjectProposal.objects.get(pk=project_proposal_pk)
                    selected_project_proposal.project_class = request.POST.get(project_proposal_class)
                    selected_project_proposal.save()

            """send contract to selected main supervisor"""
            main_supervisor_pk = request.POST.get('chosen_main_supervisor')
            main_supervisor = User.objects.get(pk=main_supervisor_pk)

            project_pk = request.GET.get('project')
            project = Project.objects.get(pk=project_pk)

            """Assign project value"""
            project.project_value = project_value
            project.save()
            send_notification_to_collaborators_below_the_coin(project)

            previous_contract = ProjectContract.objects.filter(project=project, contract_type='Collaborator')
            if previous_contract:
                previous_project_supervisor = ProjectSupervisor.objects.get(project=project,
                                                                            supervisor=previous_contract[0].user)
                if previous_project_supervisor.supervisor == previous_project_supervisor.project.owner:
                    previous_project_supervisor.state = 'Waiting for Research Director Acceptance'
                else:
                    previous_project_supervisor.state = 'Accepted Pending'
                previous_project_supervisor.save()
                previous_contract.delete()

            current_project_supervisor = ProjectSupervisor.objects.get(project=project, supervisor=main_supervisor)
            current_project_supervisor.state = "Waiting For Signature"
            current_project_supervisor.save()
            ProjectContract(project=project, user=main_supervisor, contract_type='Collaborator',
                            contract_file='Supervisor-contract.pdf').save()

            messages.success(request, "A contract has been sent to the main supervisor.")

        elif 'reject-project' in request.POST:
            project_reason_reject = request.POST.get('reject-reason')
            if project_reason_reject is None:
                messages.error(request, f'Reject reason should not be empty')
            else:
                project_pk = request.POST.get('project-pk')
                user_project = Project.objects.get(pk=project_pk)
                reject_the_project_and_inform_the_owner(user_project, project_reason_reject)

                messages.success(request, f'Project has been rejected successfully')

        response = HttpResponseRedirect(request.path_info)  # redirect to the same page
        response['Location'] += request.get_full_path().split('/')[-1]
        return response

    context = {
        'new_research_project_numbers': Project.objects.filter(expert=None, status='Inspecting',
                                                               project_type='Research').count(),
        'main_supervisor_approval_numbers': Project.objects.filter(Q(project_type='Research', main_supervisor=None)
                                                                   & ~Q(final_comment=None)).count()
    }

    if 'filter' in request.GET:
        selected_filter = request.GET.get('filter')
        if selected_filter == "new_research_projects":
            context['new_research_projects'] = Project.objects.filter(expert=None, status='Inspecting',
                                                                      project_type='Research')
        elif selected_filter == 'main_supervisor_approval':
            context['projects'] = Project.objects.filter(Q(project_type='Research', main_supervisor=None)
                                                         & ~Q(final_comment=None))
            if 'project' in request.GET:
                primary_key = request.GET.get('project')
                if primary_key is not None:
                    selected_project = Project.objects.get(pk=primary_key)
                    context['selected_project'] = selected_project
                    context['project_reviewers'] = Reviewer.objects.filter(project=selected_project)
                    context['total_submitted_proposals'] = ProjectProposal.objects.filter(
                        project_supervisor__project=selected_project)

                    contract_exists = ProjectContract.objects.filter(
                        user__in=User.objects.filter(projectsupervisor__project=selected_project),
                        project=selected_project).count()
                    if contract_exists:
                        context['main_supervisor_contract'] = ProjectContract.objects.get(
                            user__in=User.objects.filter(projectsupervisor__project=selected_project),
                            project=selected_project)
                        if context['main_supervisor_contract'].reply_has_been_sent:
                            context['main_supervisor_contract_reply'] = \
                                ProjectContractReply.objects.get(
                                    user__in=User.objects.filter(
                                        projectsupervisor__project=selected_project),
                                    project=selected_project)

    return render(request, 'dashboard/research_director_panel.html', context)


def research_expert_panel(request):
    projects = Project.objects.filter(Q(expert=request.user, expert_is_accepted=True,
                                        project_type='Research') & ~Q(status="Rejected"))
    request_projects = Project.objects.filter(expert=request.user, expert_is_accepted=False, project_type='Research')
    context = {
        'projects': projects,
        'request_projects': request_projects,
    }

    # GET REQUESTS
    if 'project' in request.GET:
        primary_key = request.GET.get('project')
        project_is_accessible = Project.objects.filter(pk=primary_key, expert=request.user)
        if project_is_accessible:
            selected_project = Project.objects.get(pk=primary_key)
            context['selected_project'] = selected_project
            """
            All experts except:
            - the current research expert that is selecting them
            - the ones who requested to be main supervisor for this particular project
            """
            context['experts'] = ResearchExpert.objects.all().exclude(user=request.user) \
                .exclude((Q(user__projectsupervisor__project=selected_project) &
                          Q(user__projectsupervisor__projectproposal__isnull=False)) |
                         Q(user__reviewer__project=selected_project))

            context['total_submitted_proposal_numbers'] = ProjectProposal.objects.filter(
                project_supervisor__project=selected_project).count()
            context['project_reviewers'] = Reviewer.objects.filter(project=selected_project)
            context['has_every_reviewer_scored'] = has_every_reviewer_scored(selected_project)
            context['total_submitted_proposals'] = ProjectProposal.objects.filter(
                project_supervisor__project=selected_project)
        else:
            return render(request, 'ivc_website/403.html')

    if request.method == "POST":

        """
        In case when we want to assign reviewer(s) to a project
        Limitations:
          1. There should be at least one supervisor with proposal for the project otherwise it is irrational to assign
        a reviewer for a project without a proposal!
          2. reviewers should be at least 2.
        """
        if 'assign-reviewer' in request.POST:
            project_pk = request.GET.get('project')

            has_supervisor_with_proposal = ProjectProposal.objects. \
                                               filter(project_supervisor__project__pk=project_pk).count() >= 1

            number_of_assign_reviewer = get_total_number_of_reviewers(project_pk, request)

            number_of_assign_reviewer_is_valid = number_of_assign_reviewer >= 2
            if number_of_assign_reviewer_is_valid and has_supervisor_with_proposal:
                assign_reviewers_to_the_project(project_pk, request)
            elif not number_of_assign_reviewer_is_valid:
                messages.error(request, f"The number of reviewers must be more than two ")
            else:
                messages.error(request, f"There aren't any supervisors yet")

        if 'remove-reviewer' in request.POST:
            project_reviewer_pk = request.POST.get('remove-reviewer')
            project_reviewer = Reviewer.objects.get(pk=project_reviewer_pk)
            if request.user == selected_project.expert:  # security check
                scored_numbers = ProjectProposal.objects.filter(proposalopinion__reviewer=project_reviewer).count()
                if scored_numbers >= 1:
                    messages.error(request, 'It is not possible to remove a reviewer since has scored proposal(s)')
                else:
                    project_reviewer.delete()
                    messages.success(request, 'removed successfully')

        if 'final-comment' in request.POST:
            project_pk = request.GET.get("project")
            selected_project = Project.objects.get(pk=project_pk)
            if has_every_reviewer_scored(selected_project):
                selected_project.final_comment = request.POST.get('final-comment')
                selected_project.save()

                messages.success(request, 'Final comment saved successfully')

            else:
                messages.error(request, 'Not all reviewers scored')

        response = HttpResponseRedirect(request.path_info)  # redirect to the same page
        response['Location'] += f'?my_projects=1&project={request.GET.get("project")}'
        return response

    return render(request, 'dashboard/research_expert_panel.html', context)


@login_required
def technical_manager(request):
    if not request.user.memberprofile.is_technical_manager:
        return render(request, 'ivc_website/403.html')

    context = {}

    # GET REQUESTS
    if 'filter' in request.GET:
        given_filter = request.GET.get('filter')
        if given_filter == 'new_industrial_projects':
            context['new_industrial_projects'] = Project.objects.filter(Q(project_type="Industrial", expert=None,
                                                                          status='Inspecting'))
            context['experts'] = Expert.objects.all()
        if given_filter == 'report_of_evaluation':
            context['evaluation_projects'] = Project.objects.filter(~Q(projectarea__projectexpertareaitem__agree=None)
                                                                    & ~Q(status="Rejected") & ~Q(is_valid=True))
        if given_filter == 'main_supervisor_approval':
            context['chosen_main_supervisors'] = ProjectSupervisor.objects.filter(state='Waiting for Technical'
                                                                                        ' Manager Acceptance')
        if given_filter == 'contracts':
            context['contracts'] = ProjectContractReply.objects.filter(contract_type="Collaborator",
                                                                       project__main_supervisor=None)

    if 'project' in request.GET:
        in_report_of_evaluation_page = 'filter' in request.GET \
                                       and request.GET.get('filter') == 'report_of_evaluation'
        if in_report_of_evaluation_page:
            project_pk = request.GET.get('project')
            evaluation_project = Project.objects.get(pk=project_pk)

            if evaluation_project.status == "Rejected" or evaluation_project.is_valid:  # Security check
                return render(request, 'ivc_website/403.html')

            project_areas = ProjectArea.objects.filter(project=evaluation_project)
            context['evaluation_project_areas'] = project_areas
        else:
            return render(request, 'ivc_website/403.html')

    if 'area' in request.GET:
        in_report_of_evaluation_page = 'filter' in request.GET \
                                       and request.GET.get('filter') == 'report_of_evaluation'
        project_is_already_chosen = 'project' in request.GET
        if in_report_of_evaluation_page and project_is_already_chosen:
            selected_area = request.GET.get('area')
            evaluation_project_area = ProjectArea.objects.get(project=evaluation_project,
                                                              area=IndustrialArea.objects.get(area=selected_area))
            evaluation_project_area_items = ProjectExpertAreaItem.objects.filter(project_area=evaluation_project_area)

            context['evaluation_project_area'] = evaluation_project_area
            context['evaluation_project_area_items'] = evaluation_project_area_items
        else:
            return render(request, 'ivc_website/403.html')

    if 'main_supervisor_project' in request.GET:
        in_main_supervisor_approval_page = 'filter' in request.GET \
                                           and request.GET.get('filter') == 'main_supervisor_approval'
        if in_main_supervisor_approval_page:
            main_supervisor_pk = request.GET.get('main_supervisor_project')
            selected_main_supervisor = ProjectSupervisor.objects.get(pk=main_supervisor_pk)

            if selected_main_supervisor.state != 'Waiting for Technical Manager Acceptance':  # SECURITY CHECK
                return render(request, 'ivc_website/403.html')
            else:
                context['selected_main_supervisor'] = selected_main_supervisor
                context['project_reviewers'] = Reviewer.objects.filter(project=selected_main_supervisor.project)
                context['total_submitted_proposals'] = ProjectProposal.objects.filter(
                    project_supervisor__project=selected_main_supervisor.project)
        else:
            return render(request, 'ivc_website/403.html')

    if 'chosen_contract' in request.GET:
        in_contracts_page = 'filter' in request.GET \
                            and request.GET.get('filter') == 'contracts'
        if in_contracts_page:
            contract_pk = request.GET.get('chosen_contract')
            contract = ProjectContractReply.objects.get(pk=contract_pk)

            if contract.project.main_supervisor is None:  # Security check
                context['chosen_contract'] = contract
            else:
                return render(request, 'ivc_website/403.html')
        else:
            return render(request, 'ivc_website/403.html')

    # POST REQUESTS
    if request.method == "POST":
        """Report of Evaluation Tab"""
        if 'accept-project-to-be-new' in request.POST:
            if 'project' in request.GET:
                accept_industrial_project_and_email_the_owner_and_corresponding_expert(evaluation_project)

        if 'reject-project-to-be-new' in request.POST:
            if 'project' in request.GET:
                reject_reason = request.POST.get('reject-reason')
                if len(reject_reason.strip()) > 0:
                    reject_the_project_and_inform_the_owner(evaluation_project, reject_reason)
                    return HttpResponseRedirect(request.path_info)  # redirect to the same page
                else:
                    response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                    response['Location'] += request.get_full_path().split('/')[-1]
                    return response

        """Main Supervisor Approval Tab"""
        if 'accept-main-supervisor' in request.POST:
            main_supervisor_pk = request.POST.get('accept-main-supervisor')
            main_supervisor = ProjectSupervisor.objects.get(pk=main_supervisor_pk)

            accept_main_supervisor_and_send_contract(request.user, main_supervisor)
            messages.success(request, "Main supervisor is accepted successfully")
        if 'reject-main-supervisor' in request.POST:
            main_supervisor_pk = request.POST.get('reject-main-supervisor')
            main_supervisor = ProjectSupervisor.objects.get(pk=main_supervisor_pk)
            reject_reason = request.POST.get('reject-reason')
            if len(reject_reason.strip()) > 0:
                reject_main_supervisor_and_inform_expert(request.user, main_supervisor, reject_reason)
                messages.success(request, "Main supervisor is rejected successfully")
            else:
                response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                response['Location'] += request.get_full_path().split('/')[-1]
                return response

        """ Contracts Tab """
        if 'accept-contract' in request.POST:
            contract_pk = request.POST.get('accept-contract')
            contract = ProjectContractReply.objects.get(pk=contract_pk)
            project_supervisor_pk = ProjectSupervisor.objects.get(project=contract.project, supervisor=contract.user).pk
            make_user_collaborator("Supervisor", project_supervisor_pk)
            messages.success(request, "The person has become the project main supervisor successfully.")
            # TODO: Tell corresponding expert about this (just to make sure their performance is ok)

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context['new_industrial_project_numbers'] = Project.objects.filter(Q(project_type="Industrial", expert=None,
                                                                         status='Inspecting')).count()
    context['unconfirmed_industrial_area_numbers'] = IndustrialArea.objects.filter(confirmed=False).count()
    context['report_of_evaluation_numbers'] = Project.objects.filter(
        ~Q(projectarea__projectexpertareaitem__agree=None) & ~Q(status="Rejected") & ~Q(is_valid=True)).count()
    context['main_supervisor_approval_numbers'] = ProjectSupervisor.objects.filter(state='Waiting for Technical'
                                                                                         ' Manager Acceptance').count()
    context['contract_numbers'] = ProjectContractReply.objects.filter(contract_type="Collaborator",
                                                                      project__main_supervisor=None).count()
    return render(request, 'dashboard/technical_manager.html', context)


@login_required
def corresponding_expert_panel(request):
    projects = Project.objects.filter(Q(expert=request.user, expert_is_accepted=True,
                                        project_type='Industrial') & ~Q(status="Rejected"))
    request_projects = Project.objects.filter(expert=request.user, expert_is_accepted=False, project_type='Industrial')
    context = {
        'projects': projects,
        'request_projects': request_projects,
    }

    # GET REQUESTS
    if 'project' in request.GET:
        primary_key = request.GET.get('project')
        project_is_accessible = Project.objects.filter(pk=primary_key, expert=request.user)
        if project_is_accessible:
            selected_project = Project.objects.get(pk=primary_key)
            context['selected_project'] = selected_project

            if selected_project.is_valid:
                context['is_waiting_for_technical_manager'] = ProjectSupervisor.objects.filter(
                    Q(project=selected_project,
                      state="Waiting for "
                            "Technical "
                            "Manager "
                            "Acceptance") |
                    Q(project=selected_project,
                      state="Waiting For "
                            "Signature") |
                    Q(project=selected_project,
                      state="Inspecting "
                            "Signature")
                ).count()
                context['it_is_approved_main_supervisor'] = ProjectSupervisor.objects.filter(
                    project=selected_project,
                    state="Collaborator").count()

                if not context['is_waiting_for_technical_manager'] and not context['it_is_approved_main_supervisor']:
                    context['reviewers'] = Expert.objects.all() \
                        .exclude(
                        user__in=Reviewer.objects.filter(project=selected_project).values_list('user', flat=True)) \
                        .exclude(user=request.user)
                    context['project_reviewers'] = Reviewer.objects.filter(project=selected_project)
                    context['total_submitted_proposals'] = ProjectProposal.objects.filter(
                        project_supervisor__project=selected_project)
                    context['project_supervisors'] = ProjectSupervisor.objects.filter(project=selected_project)
            else:  # then we have to assign some experts to some areas
                context['experts'] = Expert.objects.all().exclude(user=request.user)
                context['project_areas'] = ProjectArea.objects.filter(project=selected_project, is_confirmed=True)
        else:
            return render(request, 'ivc_website/403.html')
    else:
        selected_project = None

    # POST REQUESTS
    if request.method == "POST" and selected_project is not None:
        if 'my_projects' in request.GET:
            location = f'?my_projects=1&project={selected_project.pk}'
        else:
            location = f'?project={selected_project.pk}'

        if 'add-reviewer' in request.POST:
            reviewer_pk = request.POST.get('chosen-reviewer')
            reviewer = User.objects.get(pk=reviewer_pk)

            already_exists = Reviewer.objects.filter(user=reviewer, project=selected_project).count()
            if not already_exists and request.user == selected_project.expert:  # Security check
                Reviewer(user=reviewer, project=selected_project).save()
        if 'remove-reviewer' in request.POST:
            project_reviewer_pk = request.POST.get('remove-reviewer')
            project_reviewer = Reviewer.objects.get(pk=project_reviewer_pk)

            if request.user == selected_project.expert:  # security check
                scored_numbers = ProjectProposal.objects.filter(proposalopinion__reviewer=project_reviewer).count()
                if scored_numbers >= 1:
                    messages.error(request, 'It is not possible to remove a reviewer since has scored proposal(s)')
                else:
                    project_reviewer.delete()
                    messages.success(request, 'removed successfully')

        if 'remove-expert-from-area' in request.POST:
            project_area = ProjectArea.objects.get(pk=request.POST.get('remove-expert-from-area'))
            form_is_not_completed = project_area.projectexpertareaitem_set.filter(agree=None).count()

            if form_is_not_completed and project_area.project.expert == request.user:  # Security check
                project_area.projectexpertareaitem_set.filter(agree=None).delete()
                project_area.expert = None
                project_area.save()

            # step
            empty_project_experts = selected_project.projectarea_set.filter(~Q(expert=None)).count() == 0
            if empty_project_experts:
                selected_project.step = 1
                selected_project.save()

        if 'assign-expert-to-area' in request.POST:
            expert_pk = request.POST.get('chosen-expert')
            project_area_pk = request.POST.get('assign-expert-to-area')

            expert = User.objects.get(pk=expert_pk)
            project_area = ProjectArea.objects.get(pk=project_area_pk)

            if project_area.is_confirmed:  # security check
                project_area.expert = expert
                project_area.save()

                # step
                selected_project.step = 2
                selected_project.save()

                for area_item in ExpertAreaItem.objects.all().values_list('item', flat=True):
                    ProjectExpertAreaItem(project_area=project_area, item=area_item).save()

                messages.success(request, f'Expert is assigned on the area')
            else:
                messages.success(request, f'Area is not confirmed!')

        if 'accept-main-supervisor' in request.POST:
            project_main_supervisor_pk = request.POST.get('chosen-supervisor')
            accept_reason = request.POST.get('accept-proposal-reason')
            if len(accept_reason.strip()) > 0:
                project_main_supervisor = ProjectSupervisor.objects.get(pk=project_main_supervisor_pk)
                project_main_supervisor.accept_reason = accept_reason
                project_main_supervisor.state = "Waiting for Technical Manager Acceptance"
                project_main_supervisor.save()
            else:
                response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                response['Location'] += request.get_full_path().split('/')[-1]
                return response

        response = HttpResponseRedirect(request.path_info)  # redirect to the same page
        response['Location'] += location
        return response

    return render(request, 'dashboard/corresponding_expert.html', context)


@login_required
def new_industrial_areas(request):
    if Expert.objects.filter(user=request.user).count() == 0:
        return render(request, 'ivc_website/403.html')

    context = {'project_items': get_new_industrial_projects(user=request.user)}

    # GET REQUESTS
    if 'project' in request.GET:
        primary_key = request.GET.get('project')
        the_project = Project.objects.get(pk=primary_key)
        project_is_accessible = ProjectArea.objects.filter(Q(project=the_project, expert=request.user,
                                                             project__is_valid=False) & ~Q(
            project__status="Rejected")).count()
        if project_is_accessible:
            project_areas = ProjectArea.objects.filter(project=the_project, expert=request.user)
            context['project_areas'] = project_areas
        else:
            return render(request, 'ivc_website/403.html')

    if 'area' in request.GET:
        the_area = request.GET.get('area')
        industrial_area = IndustrialArea.objects.get(area=the_area)
        if 'project' in request.GET:
            project_area = ProjectArea.objects.get(project=the_project, area=industrial_area)
            expert_is_different = project_area.expert != request.user

            if expert_is_different:  # SECURITY CHECK
                return render(request, 'ivc_website/403.html')

            form_questions = ProjectExpertAreaItem.objects.filter(project_area=project_area)
            context['form_questions'] = form_questions
            context['comment'] = project_area.comment

        else:
            return render(request, 'ivc_website/403.html')

    # POST REQUESTS
    if request.method == "POST":
        if 'form-items-has-been-submitted' in request.POST:
            if 'project' not in request.GET and 'area' not in request.GET:  # SECURITY CHECK
                return render(request, 'ivc_website/403.html')

            for key in request.POST:
                if 'question' in key:
                    pk = key.split('-')[1]
                    project_expert_area = ProjectExpertAreaItem.objects.get(pk=pk)

                    opinion = request.POST.get(key)
                    if opinion == 'agree':
                        project_expert_area.agree = True
                    else:
                        project_expert_area.agree = False
                    project_expert_area.save()
                if key == 'comment':
                    comment = request.POST.get('comment')
                    if comment != "":
                        project_area.comment = comment
                        project_area.save()

            messages.success(request, "Form is completed successfully")

            # step
            report_of_evaluation_is_ready = the_project.projectarea_set.filter(projectexpertareaitem__agree=None) \
                                                .count() == 0
            if report_of_evaluation_is_ready:
                the_project.step = 3
                the_project.save()

        location = f'?project={the_project.pk}'
        response = HttpResponseRedirect(request.path_info)  # redirect to the same page
        response['Location'] += location
        return response

    #
    # response = HttpResponseRedirect(request.path_info)  # redirect to the same page
    # response['Location'] += location
    # return response
    # the_project.is_valid = True
    return render(request, 'dashboard/new_industrial_areas.html', context=context)


@login_required
def review(request):
    is_not_industrial_expert = Expert.objects.filter(user=request.user).count() == 0
    is_not_research_expert = ResearchExpert.objects.filter(user=request.user).count() == 0
    if is_not_industrial_expert and is_not_research_expert:
        return render(request, 'ivc_website/403.html')

    projects_pk = Reviewer.objects.filter(user=request.user).values_list('project', flat=True)
    projects = Project.objects.filter(pk__in=projects_pk)

    context = {
        'project_items': projects
    }

    if 'project' in request.GET:
        project_pk = request.GET.get('project')
        project = Project.objects.get(pk=project_pk)
        project_proposals = ProjectProposal.objects.filter(project_supervisor__project=project)
        context['project_proposals'] = project_proposals

        if 'proposal' in request.GET:
            proposal_pk = request.GET.get('proposal')
            selected_project_proposal = ProjectProposal.objects.get(pk=proposal_pk)
            context['selected_project_proposal'] = selected_project_proposal

            """ POST REQUEST """
            if request.method == "POST":
                response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                response['Location'] += f"?project={project_pk}&proposal={proposal_pk}"

                """
                Reviewer comment
                """
                reviewer_comment = request.POST.get('reviewer-comment')
                if reviewer_comment is None or reviewer_comment.strip() == "":
                    messages.error(request, "Reviewer comment should not be empty")
                    return response
                add_reviewer_comment_to_proposal(request.user, reviewer_comment, selected_project_proposal)

                if 'submit-new-proposal-opinion' in request.POST:
                    submit_new_proposal_score(project, request, selected_project_proposal)

                elif 'submit-proposal-opinion':
                    submit_proposal_score(project, request, selected_project_proposal)

                return response
            """ END OF POST REQUEST """

            reviewer_already_scored = ProposalOpinion.objects.filter(proposal=selected_project_proposal,
                                                                     reviewer__user=request.user).count()
            if reviewer_already_scored:
                context['proposal_opinions'] = ProposalOpinion.objects.filter(proposal=selected_project_proposal,
                                                                              reviewer__user=request.user)
                context['reviewer_comment'] = ProposalComment.objects.get(proposal=selected_project_proposal,
                                                                          reviewer__user=request.user)
            else:
                context['proposal_opinions'] = ProposalOpinionItem.objects.filter(project_type=project.project_type)

    return render(request, 'dashboard/review.html', context)


@login_required
def review_in_detail(request, proposal_pk, reviewer_pk):
    reviewer = Reviewer.objects.get(pk=reviewer_pk)
    proposal = ProjectProposal.objects.get(pk=proposal_pk)

    proposal_opinions = ProposalOpinion.objects.filter(proposal=proposal, reviewer=reviewer)
    context = {
        'proposal_opinions': proposal_opinions,
        'reviewer_comment': ProposalComment.objects.get(proposal=proposal, reviewer=reviewer).comment
    }

    return render(request, 'dashboard/review_detail.html', context)


@login_required
def recently_added_expertises(request):
    industrial_areas = IndustrialArea.objects.filter(~Q(expertarea__expert__user=request.user) & Q(confirmed=True)
                                                     & ~Q(area='Other'))

    if Expert.objects.filter(user=request.user).count() == 0:
        return render(request, 'ivc_website/403.html')

    expert = Expert.objects.get(user=request.user)

    if request.method == "POST":
        for key in request.POST:
            if 'expertise' in key:
                industrial_area_pk = int(key.split('-')[1])
                expertise = IndustrialArea.objects.get(pk=industrial_area_pk)

                expert_opinion = request.POST.get(key)
                if expert_opinion == 'agree':
                    ExpertArea(expert=expert, area=expertise, agree=True, disagree=False).save()
                elif expert_opinion == 'disagree':
                    ExpertArea(expert=expert, area=expertise, agree=False, disagree=True).save()

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    return render(request, 'dashboard/recently_added_expertises.html', context={
        'expertises': industrial_areas
    })


@login_required
def define_project(request):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    context = {"project_form": ProjectForm(),
               'areas': IndustrialArea.objects.filter(confirmed=True).exclude(area="Other").values_list('area',
                                                                                                        flat=True),
               'supervisors': User.objects.filter(memberprofile__position="Supervisor")}

    user_is_supervisor = user_has_memberprofile(request.user) and request.user.memberprofile.position == "Supervisor"
    if user_is_supervisor:
        context["proposal_form"] = ProjectProposalForm()

    if not user_has_memberprofile(request.user):
        context["phone_number_form"] = PhoneNumberForm(instance=request.user.legalprofile)
        context["skype_form"] = SkypeForm(instance=request.user.legalprofile)
        context["preference_form"] = PreferenceForm(instance=request.user.legalprofile)
        context["info_form"] = ProjectInfoForm()

    if request.method == "POST":
        context["project_form"] = ProjectForm(request.POST, request.FILES)
        if not user_has_memberprofile(request.user):
            context["phone_number_form"] = PhoneNumberForm(request.POST)
            context["skype_form"] = SkypeForm(request.POST)
            context["preference_form"] = PreferenceForm(request.POST)
            context["info_form"] = ProjectInfoForm(request.POST, request.FILES)

        if context['project_form'].is_valid():
            if user_has_memberprofile(request.user):
                added_successfully, response, project_pk = try_to_add_new_project(request, context['project_form'])
            else:
                added_successfully, response, project_pk = try_to_add_new_project(request, context['project_form'],
                                                                                  context['info_form'])

            if added_successfully:
                if not user_has_memberprofile(request.user):
                    if context["preference_form"].is_valid():
                        contact_preference = context["preference_form"].cleaned_data.get('contact_preference')
                        request.user.legalprofile.contact_preference = contact_preference

                        if contact_preference == "Phone Number":
                            if context["phone_number_form"].is_valid():
                                request.user.legalprofile.phone_region = context["phone_number_form"] \
                                    .cleaned_data.get('phone_region')
                                request.user.legalprofile.phone = context["phone_number_form"].cleaned_data.get('phone')

                        if contact_preference == "Skype":
                            if context["skype_form"].is_valid():
                                request.user.legalprofile.skype = context["skype_form"].cleaned_data.get('skype')
                        request.user.legalprofile.save()

                    save_the_project_area(request, project_pk)
                elif user_is_supervisor and request.POST.get('want-to-be-main-supervisor') == '1':
                    selected_project = Project.objects.get(pk=project_pk)
                    proposal = ProjectProposalForm(request.POST, request.FILES)
                    if proposal.is_valid():
                        submitted_proposal = proposal.save(commit=False)
                        action = request_or_withdraw_a_project(project_pk, request.user, "Supervisor")
                        if action == "REQUEST":
                            project_supervisor = ProjectSupervisor.objects.get(project=selected_project,
                                                                               supervisor=request.user)
                            project_supervisor.state = "Collaborator"
                            project_supervisor.priority = 0
                            project_supervisor.save()

                            submitted_proposal.project_supervisor = project_supervisor
                            submitted_proposal.save()
                            messages.success(request, f'Your Proposal has been submitted successfully.')

                        else:
                            messages.error(request,
                                           'Your Proposal has been failed. please contact our team and report the '
                                           'problem.')
                    else:
                        selected_project.delete()
                        messages.error(request, 'Your proposal format should be PDF')
                        return render(request, 'dashboard/define_new_project.html', context)

                Log(user=request.user, log="has defined a project.").save()
                messages.success(request, response)
                return redirect('dashboard-page')  # Redirect to the main dashboard page after submission with success
            else:
                messages.error(request, response)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

        else:
            messages.error(request, f"Error: Scroll down to see what's wrong")

    return render(request, 'dashboard/define_new_project.html', context)


@login_required
def contract_list(request):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    return render(request, "dashboard/contract_list.html", context={
        'contracts': ProjectContract.objects.filter(user=request.user, valid=True).order_by('reply_has_been_sent', '-date_created')
    })


@login_required
def project_contract(request, project_pk, contract_type):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    selected_project = Project.objects.get(pk=project_pk)

    project_contract_doesnt_exist = ProjectContract.objects.filter(project=selected_project, user=request.user,
                                                                   contract_type=contract_type).count() == 0
    if project_contract_doesnt_exist and (not request.user.is_superuser or contract_type == "Collaborator"):
        return render(request, 'ivc_website/403.html')
    else:
        if contract_type == "Ownership" and request.user.is_superuser:
            contract = ProjectContract.objects.get(project=selected_project, contract_type="Ownership")
        else:
            contract = ProjectContract.objects.get(project=selected_project, user=request.user,
                                                   contract_type=contract_type)

    if ProjectContractReply.objects.filter(project=selected_project, user=request.user,
                                           contract_type=contract_type).count() != 0:
        contract_response = ProjectContractReply.objects.get(project=selected_project, user=request.user,
                                                             contract_type=contract_type)
    else:
        contract_response = None

    if request.method == "POST":

        if contract_type == "Ownership":
            if not user_has_memberprofile(request.user):  # owner
                reply_form_is_sent = False
                post_keys = request.POST.keys()
                for key in post_keys:
                    if 'mandatory' in key:
                        item_pk = key.split('-')[-1]
                        project_contract_item = ProjectContractItem.objects.get(pk=item_pk)
                        project_contract_item.agree = True
                        project_contract_item.save()
                    if 'optional' in key:
                        item_pk = key.split('-')[-1]
                        project_contract_item = ProjectContractItem.objects.get(pk=item_pk)
                        user_decision = request.POST.get(key)
                        if user_decision == 'agree':
                            project_contract_item.agree = True
                            project_contract_item.disagree = False
                        if user_decision == 'disagree':
                            project_contract_item.disagree = True
                            project_contract_item.agree = False
                        project_contract_item.save()
                    if 'term' in key:
                        term = request.POST.get(key)
                        ProjectContractItem(project=selected_project, item=term, item_type='Optional',
                                            from_item='Company') \
                            .save()
                    if 'owner-send-contract-reply' in key:
                        reply_form = ProjectContractReplyForm(request.POST, request.FILES)
                        reply_form_is_sent = True
                        if reply_form.is_valid():
                            save_contract_response(request, selected_project, reply_form, contract, contract_type)

                            inform_the_superusers(selected_project, "Owner sent contract file",
                                                  reverse('new-projects-page'))
                            messages.success(request, "Contract file has been sent successfully. it's going to be "
                                                      "start within 24 hours.")

                if not reply_form_is_sent:
                    inform_the_superusers(selected_project, "Owner submitted the contract",
                                          reverse('project-contract-page', args=[project_pk, contract_type]))
                    messages.success(request,
                                     "Your changes has been submitted successfully, now wait for our managers to "
                                     "respond within 24 hours")
            else:  # superuser
                post_keys = request.POST.keys()
                for key in post_keys:
                    if 'company-item' in key:
                        item_pk = key.split("-")[-1]
                        project_contract_item = ProjectContractItem.objects.get(pk=item_pk)
                        superuser_decision = request.POST.get(key)
                        if superuser_decision == 'agree':
                            project_contract_item.agree = True
                            project_contract_item.disagree = False
                        if superuser_decision == 'disagree':
                            project_contract_item.agree = False
                            project_contract_item.disagree = True
                            disagreement_reason = request.POST.get(f'disagreement-{item_pk}')
                            project_contract_item.disagreement_reason = disagreement_reason
                        project_contract_item.save()

                success, file_directory = create_contract(client_name=contract.user.legalprofile.company_name,
                                                          project=selected_project)
                if success:
                    contract.contract_file.name = file_directory
                    contract.ready_to_be_printed = True
                    contract.save()
                    send_notification(selected_project.title,
                                      "A contract file has been provided. please read it carefully and put your "
                                      "signature", selected_project.owner,
                                      reverse('project-contract-page', args=[project_pk, contract_type]))
                    email_subject = "A contract file has been provided"
                    email_content = f'A contract file has been provided for the project "{selected_project.title}".\n' + \
                                    'Please read the contract carefully and put your signature at the end.\n' + \
                                    'In case if you have any questions, you can email admin@tecvico.com\n\nRegards.\n' + \
                                    'Tecvico'
                    threading.Thread(target=send_new_email,
                                     args=(email_subject, email_content, selected_project.owner.email)).start()
                    messages.success(request, "Your changes has been submitted successfully")
                else:
                    messages.error(request, "An internal error is occurred")

            return HttpResponseRedirect(request.path_info)  # redirect to the same page

        elif contract_type == "Collaborator":
            project_contract_reply_form = ProjectContractReplyForm(request.POST, request.FILES)
            if project_contract_reply_form.is_valid() and is_user_eligible_to_send_contract(request.user,
                                                                                            selected_project,
                                                                                            contract_type):
                save_contract_response(request, selected_project, project_contract_reply_form, contract, contract_type)
                if contract_type == "Collaborator":
                    change_state_after_contract_if_necessary(request, selected_project)
                    inform_superuser_if_necessary(request, selected_project)
                messages.success(request, 'Contract has been uploaded successfully')
                return HttpResponseRedirect(request.path_info)  # redirect to the same page
            else:
                messages.error(request, 'Contract format should be PDF')

    project_contract_reply_form = ProjectContractReplyForm()

    context = {
        "selected_project": selected_project,
        "contract": contract,
        'contract_type': contract_type,
        "reply_form": project_contract_reply_form,
        "contract_response": contract_response,
        'eligible_to_send_contract': is_user_eligible_to_send_contract(request.user, selected_project, contract_type)
    }
    if contract_type == "Ownership":
        context['mandatory_items'] = ProjectContractItem.objects.filter(project=selected_project, from_item="Tecvico",
                                                                        item_type="Mandatory")
        context['optional_items'] = ProjectContractItem.objects.filter(project=selected_project, from_item="Tecvico",
                                                                       item_type="Optional")
        context['company_items'] = ProjectContractItem.objects.filter(project=selected_project, from_item='Company')
    return render(request, "dashboard/contract.html", context)


@login_required
def dashboard_request(request):
    if request.POST:
        if 'accept-project-pk' in request.POST:
            accept_requested_collaboration(request)
            messages.success(request, "Project is Accepted successfully, now go to contract page")
            return redirect(reverse('dashboard-page'))

        if 'reject-project-pk' in request.POST:
            reject_requested_collaboration(request)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context = {}

    """
    My Projects: if request.user is mentor or supervisor, he can see who wants to be a part of project
    request_dictionary will contain all of that information
    """
    if is_mentor_or_supervisor(request.user):
        context['request_dictionary'] = get_users_who_want_to_be_part_of_my_projects(request)

    """
    Requested Projects: if a mentor or supervisor wants our request.user to be a part of their project, he would see that
    based on the query below:
    """
    context['requested_projects'] = get_projects_that_want_me_to_be_part_of_them(request)

    return render(request, 'dashboard/request.html', context)


@login_required
def dashboard_request_with_contract(request, project_type):
    if request.POST:
        if 'accept-project-pk' in request.POST:
            accept_industrial_requested_collaboration(request)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

        if 'reject-project-pk' in request.POST:
            reject_requested_collaboration(request)
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    if project_type != "Industrial" and project_type != "Competition":
        return render(request, 'ivc_website/404.html')

    context = {'project_type': project_type}

    """
    My Projects: if request.user is mentor or supervisor, he can see who wants to be a part of project
    request_dictionary will contain all of that information
    """
    user_is_expert = Expert.objects.filter(user=request.user).count()
    if user_has_memberprofile(request.user) and request.user.memberprofile.position == "Supervisor" or user_is_expert:
        context['request_dictionary'] = get_users_who_want_to_be_part_of_my_projects_with_contract(request,
                                                                                                   project_type)

    """
    Requested Projects: if a mentor or supervisor wants our request.user to be a part of their project, he would see that
    based on the query below:
    """
    if user_has_memberprofile(request.user):
        context['requested_projects'] = get_projects_with_contract_that_want_me_to_be_part_of_them(request,
                                                                                                   project_type)
        context['inspecting_signature_projects'] = get_projects_that_collaborator_has_signed_the_signature(request,
                                                                                                           project_type)

    context['ownership_contract_items'] = ProjectContract.objects.filter(user=request.user, reply_has_been_sent=False,
                                                                         project__project_type=project_type,
                                                                         ready_to_be_printed=False,
                                                                         contract_type='Ownership').distinct()
    context['project_contracts'] = get_project_contracts(request, project_type)

    return render(request, 'dashboard/project_requests_with_contract.html', context)


@login_required
def project_detail(request, pk): 
    template_name = 'dashboard/projects-research-detai.html'
    detail_research_pr =  get_object_or_404(ResearchProject, pk=pk)
    

    if request.method == 'POST':
        comment = request.POST.get('comment')
        email = request.POST.get('email')
        id_project = request.POST.get('id_project')
            
        comment = CommentProject.objects.create(comment=comment, email=email, user=request.user, status='new', commentproject_id=id_project)
        
        users = ResearchRole.objects.filter(comment_management=True)
        
        for i in users:
            Notification(title='Research (ID: {})'.format(detail_research_pr.project.client_form.formclint.id_project), 
                description='A comment has been added to your list. Go to your dashboard and observe it.', target=i.user, 
                link='research-comment-management').save()

        messages.success(request,'Your comment has been submitted successfully.')
        return redirect('project-detail-research', pk)


    context = {
        'object': detail_research_pr,
        'products': TimeProgramming.objects.filter(confirm=True, sub=detail_research_pr.project),
        'comments': CommentProject.objects.filter(status='accepted', commentproject=detail_research_pr),
        'Lerner': Lerner.objects.filter(~Q(status_remove__in=['request-accpet-by-expert', 'request-accpet-by-director']), research=detail_research_pr, status__in=['confirmed', 'confirmed-by-expert']),
        'Member': Member.objects.filter(~Q(status_remove__in=['request-accpet-by-expert', 'request-accpet-by-director']), research=detail_research_pr, status__in=['confirmed', 'confirmed-by-expert']),
        'Mentor': Mentor.objects.filter(~Q(status_remove__in=['request-accpet-by-expert', 'request-accpet-by-director']), research=detail_research_pr, status__in=['confirmed', 'confirmed-by-expert']),
        'supervisor': SuperVizor.objects.filter(~Q(status_remove__in=['request-accpet-by-expert', 'request-accpet-by-director']), research=detail_research_pr, status__in=['confirmed', 'confirmed-by-expert']),
        
        'simila_projects': ResearchProject.objects.filter(~Q(id=detail_research_pr.id), project__client_form__formclint__main_field=detail_research_pr.project.client_form.formclint.main_field, status__in=['new', 'on_going', 'done']),
    }
    return render(request, template_name, context)


def project_filter(request):
    projects = ResearchProject.objects.all()
    project_status = request.POST.get('status')
    project_grade = request.POST.get('grade')

    if project_status:
        if project_status == 'all':
            projects = ResearchProject.objects.filter(status__in=['new', 'on_going', 'pending', 'on_hold', 'done', ]).order_by('-created')
        else:
            projects = ResearchProject.objects.filter(status= project_status).order_by('-created')
            
    if project_grade:
        if project_grade == 'all':
            projects = ResearchProject.objects.filter(status_value__in = ['hard', 'normal', 'easy']).order_by('-created')
        else:
            projects = ResearchProject.objects.filter(status_value = project_grade).order_by('-created')


    if project_status and project_grade:
        if project_status == 'all' and project_grade == 'all':
            projects = ResearchProject.objects.filter(~Q(status="delete"),).order_by('-created')
        
        elif project_status == 'all':
            projects = ResearchProject.objects.filter(status__in=['new', 'on_going', 'pending', 'on_hold', 'done', ], status_value = project_grade).order_by('-created')
        
        elif project_grade == 'all':
            projects = ResearchProject.objects.filter(status= project_status, status_value__in = ['hard', 'normal', 'easy']).order_by('-created')
        else: 
            projects = ResearchProject.objects.filter(status= project_status, status_value = project_grade).order_by('-created')
        

    context = {
        'object_list':projects,
    }
    return render(request, 'dashboard/projects-research-filter-ajax.html', context)


def dashboard_projects(request):
    template_name = 'dashboard/projects-research.html'
    projects = ResearchProject.objects.filter(status__in=['new', 'on_going', 'pending', 'on_hold', 'done', 'under_process_supervisor']).order_by('-created')

    if request.method == 'GET':
        context = {
            'projects': projects,
            'today': timezone.now()
        }
        return render(request, template_name, context)

    elif request.method == 'POST':
        search = request.POST.get('q')
        projects = ResearchProject.objects.filter(project__client_form__formclint__title__icontains=search)

        context = {
            'projects': projects,
            'today': timezone.now()
        }
        return render(request, template_name, context)


class DashboardMyProjectResearch(LoginRequiredMixin, ListView):
    paginate_by = 10
    template_name = 'dashboard/my-projects-research.html'
    def get_queryset(self):
            return IndustryFormClient.objects.filter(~Q(status__in=['r', 'rejected_by_expert', 'withdrew']), user=self.request.user, project_created=False).order_by('-created')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Defined project cart
        context['project_list_created'] = ResearchProject.objects.filter(~Q(status='done'), project__client_form__formclint__user=self.request.user, ).order_by('-created')
        project_list_created_count = ResearchProject.objects.filter(~Q(status='done'), project__client_form__formclint__user=self.request.user, ).order_by('-created').count()
        project_list_notcreated_count = IndustryFormClient.objects.filter(~Q(status__in=['r', 'rejected_by_expert', 'withdrew']), user=self.request.user, project_created=False).order_by('-created').count()
        context['count_defined_cart'] = project_list_created_count + project_list_notcreated_count
        
        # revised cart
        context['count_revised_cart'] = IndustryExpertForSupervisor.objects.filter(status__in=['b', 'h'], supervisor=self.request.user).count() + IndustryFormExpert.objects.filter(~Q(status="is_change"), status='revise_director_to_client').count()
        context['count_rejected_cart'] = IndustryFormClient.objects.filter(status='r', user=self.request.user).count()
        # context['count_returned_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status='b', supervisor=self.request.user).count()
            

        # applicant
        context['project_apply_supervisor'] = SuperVizor.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,).order_by('-created')
        context['project_apply_mentor'] = Mentor.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,).order_by('-created')
        context['project_apply_member'] = Member.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,).order_by('-created')
        context['project_apply_lerner'] = Lerner.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,).order_by('-created')
        
        context['project_request'] = RequestUserForProject.objects.filter(user=self.request.user, status__in=['request', 'not-pay']).order_by('-created')
        project_request_count = RequestUserForProject.objects.filter(user=self.request.user, status__in=['request', 'not-pay']).count()

        project_apply_supervisor_count = SuperVizor.objects.filter(user=self.request.user,).count()
        project_apply_mentor_count = Mentor.objects.filter(user=self.request.user,).count()
        project_apply_member_count = Member.objects.filter(user=self.request.user,).count()
        project_apply_lerner_count = Lerner.objects.filter(user=self.request.user,).count()
        project_applicant_count = project_apply_supervisor_count + project_apply_mentor_count + project_apply_member_count + project_apply_lerner_count + project_request_count
        context['project_applicant_count'] = project_applicant_count
        

        # Main supervisor
        context['main_supervisor_list'] = ResearchProject.objects.filter(~Q(status='done'), main_supervisor=self.request.user).order_by("-created")
        context['main_supervisor_list_count'] = ResearchProject.objects.filter(~Q(status='done'), main_supervisor=self.request.user).order_by("-created").count()


        # Count contract
        new_contract_advisor_count = SuperVizor.objects.filter(user=self.request.user, status='send-contract').count()
        new_contract_mentor_count = Mentor.objects.filter(user=self.request.user, status='send-contract').count()
        new_contract_member_count = Member.objects.filter(user=self.request.user, status='send-contract').count()
        new_contract_learner_count = Lerner.objects.filter(user=self.request.user, status='send-contract').count()
        revise_contract_advisor_count = SuperVizor.objects.filter(user=self.request.user, status='revised_by_expert').count()
        revise_contract_mentor_count = Mentor.objects.filter(user=self.request.user, status='revised_by_expert').count()
        revise_contract_member_count = Member.objects.filter(user=self.request.user, status='revised_by_expert').count()
        revise_contract_learner_count = Lerner.objects.filter(user=self.request.user, status='revised_by_expert').count()

        context['count_contract_supervisor_project_industry'] = IndustryExpertForSupervisor.objects.filter(status__in=['t', 'reject_contract'], supervisor=self.request.user).order_by("-created").count() + + new_contract_advisor_count + new_contract_mentor_count + new_contract_member_count + new_contract_learner_count + revise_contract_advisor_count + revise_contract_mentor_count + revise_contract_member_count + revise_contract_learner_count + IndustryFormClient.objects.filter(status__in=['send-contract-to-client', 'revised-contract', ], user=self.request.user).count()

        
        # new prject
        context['new_projects'] = IndustryExpertForSupervisor.objects.filter(status='u', supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created")
        context['new_projects_count'] = IndustryExpertForSupervisor.objects.filter(status='u',  supervisor=self.request.user, client_form__formclint__fund__gt=0).order_by("-created").count()
        
        # history
        context['history_project_list_created'] = ResearchProject.objects.filter(project__client_form__formclint__user=self.request.user, ).order_by('-created')
        context['history_project_list_not_created'] = IndustryFormClient.objects.filter(user=self.request.user, project_created=False).order_by('-created')
        context['history_main_supervisor_list'] = ResearchProject.objects.filter(~Q(status='done'), main_supervisor=self.request.user).order_by("-created")
        context['history_project_request'] = RequestUserForProject.objects.filter(user=self.request.user, status__in=['reject', 'request', 'not-pay'])

        context['history_project_apply_supervisor'] = SuperVizor.objects.filter(user=self.request.user,)
        context['history_project_apply_mentor'] = Mentor.objects.filter(user=self.request.user,)
        context['history_project_apply_member'] = Member.objects.filter(user=self.request.user,)
        context['history_project_apply_lerner'] = Lerner.objects.filter(user=self.request.user,)

        # context['project_list_created_history'] = ResearchProject.objects.filter(status="done", project__client_form__formclint__user=self.request.user, ).order_by('-created')
        # context['project_list_not_created_history'] = IndustryFormClient.objects.filter(status__in=['r', 'rejected_by_expert', 'withdrew'], user=self.request.user, project_created=False).order_by('-created')
        # context['project_request_rejected'] = RequestUserForProject.objects.filter(user=self.request.user, status='reject')


        project_apply_supervisor = SuperVizor.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,)
        project_apply_mentor = Mentor.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,)
        project_apply_member = Member.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,)
        project_apply_lerner = Lerner.objects.filter(~Q(status='reject'), ~Q(status_remove__in=['request-accpet-by-director', 'request-accpet-by-expert']), user=self.request.user,)
        
        count = 0

        #--- Advisor ---#
        for i in project_apply_supervisor:
            for r in ApplicantComment.objects.filter(project_id=i.research, sender_id=i.user, position='send_to_expert'):
                for e in r.comments.filter(seen=False):
                    count += 1

        for i in project_apply_supervisor:
            count += ApplicantComment.objects.filter(project_id=i.research, recipient_id=i.user, sender=i.research.project.client_form.expert, position='send-to-applicant', seen=False).count()

        #--- Mentor ---#
        for i in project_apply_mentor:
            for r in ApplicantComment.objects.filter(project_id=i.research, sender_id=i.user, position='send_to_expert'):
                for e in r.comments.filter(seen=False):
                    count += 1

        for i in project_apply_mentor:
            count += ApplicantComment.objects.filter(project_id=i.research, recipient_id=i.user, sender=i.research.project.client_form.expert, position='send-to-applicant', seen=False).count()

        #--- Member ---#
        for i in project_apply_member:
            for r in ApplicantComment.objects.filter(project_id=i.research, sender_id=i.user, position='send_to_expert'):
                for e in r.comments.filter(seen=False):
                    count += 1

        for i in project_apply_member:
            count += ApplicantComment.objects.filter(project_id=i.research, recipient_id=i.user, sender=i.research.project.client_form.expert, position='send-to-applicant', seen=False).count()

        #--- Learner ---#
        for i in project_apply_lerner:
            for r in ApplicantComment.objects.filter(project_id=i.research, sender_id=i.user, position='send_to_expert'):
                for e in r.comments.filter(seen=False):
                    count += 1

        for i in project_apply_lerner:
            count += ApplicantComment.objects.filter(project_id=i.research, recipient_id=i.user, sender=i.research.project.client_form.expert, position='send-to-applicant', seen=False).count()

        context['cart_cuntribution_count'] = count
        return context


def myproject_mainsupervisor_detail(request, pk):
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
                messages.error(request,'You must compelete the advertisement form.')
                    
                return redirect('industry:form-request-change-status-done', obj_project.pk)

            create_obj_tracing = Tracing.objects.create(
                position='Main supervisor', user=request.user, status="Main Supervisor requested status({})".format(status), event_date=timezone.now(), tracing_project_phase_2=obj_project)
            
            create_obj_tracing = Tracing.objects.create(
                position="{}".format(status), user=request.user, status="{}".format(description), event_date=timezone.now(), tracing_main_supervisor=obj_project)
           
            obj_project.status_change_choices = status
            obj_project.status_change = 'send_to_expert'
            obj_project.save()

            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A status change request is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA status change request is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_project.project.client_form.expert.get_full_name())
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
                position='Main supervisor', user=request.user, status="Main Supervisor sent a good report", event_date=timezone.now(), tracing_project_phase_2=obj_project)


            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A new progress report is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            
            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA new progress report is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. If you have any questions or concerns, please feel free to director the company through mailto:projectdirector@tecvico.com.".format(obj_project.project.client_form.expert.get_full_name())
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
                position='Main supervisor', user=request.user, status="Main Supervisor uploaded the progress report", event_date=timezone.now(), tracing_project_phase_2=obj_project)
            

            Notification(title='Research (ID: {})'.format(obj_project.project.client_form.formclint.id_project), 
                description='A new project middle report is available on your list. For more information, go to your dashboard.', target=obj_project.project.client_form.expert, 
                link='').save()

            e_subject = "TECVICO Project (Project ID: {})".format(obj_project.project.client_form.formclint.id_project, ) 
            e_content = "Dear {} \nHello\nHope you are going well. \nA new project middle report is available on your list. For more information, go to your dashboard. \nDo not reply to this Email. This Email has been sent automatically. \n\nThank you \nBest regards \nTECVICO Corp.".format(obj_project.project.client_form.expert.get_full_name())
            e_destination = obj_project.project.client_form.expert.researchrole.expert_email_address
            send_new_email(e_subject,e_content,e_destination)

            
            messages.success(request,'Your document has been sent successfully.')
        return redirect("myprojects-research-mainsupervisor", obj_project.pk)

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

        
def myproject_contract_list(request):
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
        'count_contract_supervisor_project_industry' : IndustryExpertForSupervisor.objects.filter(status__in=['t', 'reject_contract'], supervisor=request.user).order_by("-created").count(),
        'count_contract_applicant' : new_contract_advisor_count + new_contract_mentor_count + new_contract_member_count + new_contract_learner_count + revise_contract_advisor_count + revise_contract_mentor_count + revise_contract_member_count + revise_contract_learner_count,
        'count_contract_client': IndustryFormClient.objects.filter(status__in=['send-contract-to-client', 'revised-contract', ], user=request.user).count()
    }
    return render(request, 'dashboard/my-projects-contract-list.html', context)

def myproject_request_project_detail(request, pk):
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

def myproject_applicant_advisor(request, pk):
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

def myproject_applicant_mentor(request, pk):
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


def myproject_applicant_member(request, pk):
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

def myproject_applicant_learner(request, pk):
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
    
    

class MyprojecDetailClient(LoginRequiredMixin, SecurityClientDetail, DetailView):
    template_name = 'industry/project/myproject/client_detail.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormClient, pk=pk)

        
        
def myproject_detail_client(request, pk):
    template_name = 'industry/project/myproject/client_detail.html'
    project_obj = get_object_or_404(IndustryFormClient, pk=pk)
    
    service = Service.objects.filter(user=request.user, service_name='p', project=project_obj).first()
    
    
    
    context = {
        'object': project_obj,
        'inv': Invoice.objects.filter(user=request.user, service=service).first()
    }
    return render(request, template_name, context)

class MyprojecDetailExpert(LoginRequiredMixin, SecurityExpertDetail, DetailView):
    template_name = 'industry/project/myproject/expert_detail.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryFormExpert, pk=pk)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supervisors'] = IndustryExpertForSupervisor.objects.filter(client_form_id=pk)
        return context
ChangeDeadLineResearch
def myprojec_detail_expert(request, pk):
    template_name = 'industry/project/myproject/expert_detail.html'
    obj_expert = get_object_or_404(IndustryFormExpert, pk=pk)
    
    if request.method == 'POST':
        form = ChangeDeadLineResearch(request.POST or None, )
        if form.is_valid():
            deadline = form.cleaned_data.get("deadline")
            obj_expert.deadline = deadline
            obj_expert.save()
            
            supervisors_email = IndustryExpertForSupervisor.objects.filter(client_form=obj_expert, status='u')
            for user in supervisors_email:
                email = EmailMessage("TECVICO Research (Project ID: {})".format(obj_expert.formclint.id_project), 
                            "Dear {} \nHello\nHope you are going well.\nThe deadline for sending the proposal until {} has increased. Please send your proposal by the announced time. If you do not send, the company is not responsible.\n Do not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {} \nThank you.\n Best regards\n TECVICO CORP".
                            format(user.get_full_name(), client_form.deadline, obj_expert.expert.researchrole.expert_email_address),
                            to=[user.email]
                )
                email.send()         
    
            return redirect("myprojects-research-detail-expert", obj_expert.pk)
    else:
        form = ChangeDeadLineResearch
    
    supervisors_list = IndustryExpertForSupervisor.objects.filter(client_form=obj_expert)
    supervisors = []
    for i in supervisors_list:
        if i.status not in ['u', 'not_see']:
            supervisors.append(i)
    

    context = {
        'form': form,
        'object': obj_expert,
        'supervisors': supervisors,
        
    }
    
    return render(request, template_name, context)

class MyprojecDetailSupervisor(LoginRequiredMixin, SecuritySupervisorDetail, DetailView):
    template_name = 'industry/project/myproject/supervisor_detail.html'
    def get_object(self):
        global pk
        pk = self.kwargs.get('pk')
        return get_object_or_404(IndustryExpertForSupervisor, pk=pk)

class MyprojecDetailProjectResearch(LoginRequiredMixin, SecurityProjectResearchDetail, DetailView):
    template_name = 'industry/project/myproject/projects_research_detail.html'
    def get_object(self):
        global project
        pk = self.kwargs.get('pk')
        project = get_object_or_404(ResearchProject, pk=pk)
        return project
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['supervisor'] = project.supervisors_project.all()
        context['mentor'] = project.mentor_project.all()
        context['member'] = project.mmber_project.all()
        context['leaner'] = project.lerner_project.all()
        return context



@login_required
def project_view(request, project_primary_key):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    selected_project = Project.objects.get(pk=project_primary_key)

    if request.method == "POST":
        is_technical_manager = request.user.memberprofile.is_technical_manager
        is_research_director = request.user.memberprofile.is_research_director

        """
        After project definition:
          Technical manager have the following options:
          - assign-project-corresponding-expert: assign corresponding expert to the project
          - reject-project: reject project with reason
          - reject-area: reject an area that client suggested (when client clicks other)
          - accept-area: accept an area that client suggested (when client clicks other)
          
          Research Director has the following option:
          - assign-project-research-expert: assign a research expert to the project
        """
        if 'assign-project-research-expert' in request.POST:
            has_permission = is_research_director
            if has_permission:
                selected_research_expert_pk = request.POST.get('assign-project-research-expert')
                selected_research_expert = ResearchExpert.objects.get(pk=selected_research_expert_pk)
                selected_project.expert = selected_research_expert.user
                selected_project.save()
                messages.success(request, "Research expert is assigned successfully")
                return redirect('research-director-panel')

        if 'assign-project-corresponding-expert' in request.POST:
            there_is_unconfirmed_area = ProjectArea.objects.filter(project=selected_project,
                                                                   area__confirmed=False).count()
            has_permission = is_technical_manager and selected_project.expert is None and not there_is_unconfirmed_area
            if has_permission:
                selected_expert_pk = request.POST.get('assign-project-corresponding-expert')
                selected_expert = Expert.objects.get(pk=selected_expert_pk)
                selected_project.expert = selected_expert.user
                selected_project.save()
                messages.success(request, "Corresponding expert is assigned successfully")

        if 'reject-project' in request.POST:
            has_permission = is_technical_manager or is_research_director
            if has_permission:
                reject_reason = request.POST.get('reject-reason')
                if len(reject_reason.strip()) > 0:
                    reject_the_project_and_inform_the_owner(selected_project, reject_reason)
                else:
                    response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                    response['Location'] += request.get_full_path().split('/')[-1]
                    return response

        if 'reject-area' in request.POST:
            has_permission = is_technical_manager
            if has_permission:
                success, message = reject_industrial_area(request, selected_project)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

        if 'reject-project-area' in request.POST:
            has_permission = is_technical_manager
            if has_permission:
                success, message = reject_project_area(request, selected_project)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

        if 'accept-project-area' in request.POST:
            has_permission = is_technical_manager
            if has_permission:
                success, message = accept_project_area(request, selected_project)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

        if 'accept-area' in request.POST:
            has_permission = is_technical_manager
            if has_permission:
                success, message = accept_industrial_area(request, selected_project)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)

        """
        Both technical managers and experts have the following options:
        - remove-area: remove an area from the project (with reason)
        - add-industrial-area: add an area to the project (with reason)
        """
        if 'remove-area' in request.POST:
            project_area = ProjectArea.objects.get(pk=request.POST.get('remove-area'))
            user_is_project_expert = request.user == selected_project.expert and selected_project.expert_is_accepted
            has_permission = is_technical_manager or user_is_project_expert
            if has_permission:
                if project_area.expert is None:
                    success, message = remove_project_area(request, selected_project, user_is_project_expert)
                    if success:
                        messages.success(request, message)
                    else:
                        messages.error(request, message)
                else:
                    messages.error(request,
                                   "Action is not possible because an expert is assigned to it by the research expert")

        if 'add-industrial-area' in request.POST:
            user_is_project_expert = request.user == selected_project.expert and selected_project.expert_is_accepted
            has_permission = is_technical_manager or user_is_project_expert

            """
            Adding area after completing form should not be possible, so we have conditions below
            """
            if has_permission and \
                    (selected_project._state == 'Pending' or
                     selected_project._state == 'Accepted Pending' or
                     selected_project._state == 'Waiting for Technical Manager Acceptance' or
                     selected_project._state == 'Waiting for Research Director Acceptance'):
                success, message = add_industrial_area_to_project(request, selected_project, user_is_project_expert)
                if success:
                    messages.success(request, message)
                else:
                    messages.error(request, message)
            else:
                messages.error(request,
                               "Action is not denied due to sending the report of evaluation to the technical manager")

        """
        Corresponding/Research expert before becoming the corresponding/research expert:
         he can either accept or reject (reject with reason)
        """
        if 'accept-being-in-the-project' in request.POST:
            has_permission = request.user == selected_project.expert and not selected_project.expert_is_accepted
            if has_permission:
                selected_project.expert_is_accepted = True
                selected_project.save()

                if selected_project.project_type == "Industrial":
                    selected_project.step = 1
                    selected_project.save()

                    for a_technical_manager in MemberProfile.objects.filter(is_technical_manager=True):
                        Notification(title='Corresponding expert request is accepted',
                                     description=f'{request.user.first_name} accepted to be the corresponding expert',
                                     target=a_technical_manager.user, link=reverse('dashboard-project-view-page',
                                                                                   args=[selected_project.pk])).save()

                    Log(user=request.user,
                        log="CORRESPONDING EXPERT: user accepted to be the corresponding expert").save()

                    return redirect(reverse('corresponding-expert-page'))

                elif selected_project.project_type == "Research":
                    selected_project.status = "New"
                    selected_project.is_valid = True
                    selected_project.save()

                    for a_research_director in MemberProfile.objects.filter(is_research_director=True):
                        Notification(title='Research expert request is accepted',
                                     description=f'{request.user.first_name} accepted to be the research expert',
                                     target=a_research_director.user, link=reverse('notification-page')).save()

                    return redirect(reverse('research-expert-panel'))

        if 'reject-being-in-the-project' in request.POST:
            has_permission = request.user == selected_project.expert and not selected_project.expert_is_accepted
            if has_permission:
                selected_project.expert = None
                selected_project.save()

                reject_reason = request.POST.get('reject-being-in-the-project')
                if len(reject_reason.strip()) > 0:
                    if selected_project.project_type == "Industrial":
                        notification_description = f'<p style="overflow:hidden">{request.user.first_name} rejected to be ' \
                                                   f'the corresponding expert in project {selected_project.title}.\n' \
                                                   f' <b>Reason:</b> {reject_reason} </p>'
                        for a_technical_manager in MemberProfile.objects.filter(is_technical_manager=True):
                            Notification(title='Corresponding expert request is denied',
                                         description=notification_description,
                                         target=a_technical_manager.user, link=reverse('dashboard-project-view-page',
                                                                                       args=[
                                                                                           project_primary_key])).save()
                        Log(user=request.user,
                            log="CORRESPONDING EXPERT: user rejected to be the corresponding expert").save()

                        return redirect(reverse('corresponding-expert-page'))

                    elif selected_project.project_type == "Research":
                        notification_description = f'<p style="overflow:hidden">{request.user.first_name} rejected to be ' \
                                                   f'the research expert in project {selected_project.title}.\n' \
                                                   f' <b>Reason:</b> {reject_reason} </p>'
                        for a_research_director in MemberProfile.objects.filter(is_research_director=True):
                            Notification(title='Research expert request is denied',
                                         description=notification_description,
                                         target=a_research_director.user, link=reverse('dashboard-project-view-page',
                                                                                       args=[
                                                                                           project_primary_key])).save()
                        return redirect(reverse('research-expert-panel'))
                else:
                    response = HttpResponseRedirect(request.path_info)  # redirect to the same page
                    response['Location'] += request.get_full_path().split('/')[-1]
                    return response

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context = {
        "selected_project": selected_project
    }

    user_is_technical_manager = user_has_memberprofile(request.user) and request.user.memberprofile.is_technical_manager
    user_is_research_director = user_has_memberprofile(request.user) and request.user.memberprofile.is_research_director
    user_is_project_expert = request.user == selected_project.expert

    if user_has_memberprofile(request.user):
        if user_is_technical_manager:
            context['unconfirmed_industrial_areas'] = IndustrialArea.objects.filter(confirmed=False,
                                                                                    projectarea__project=selected_project)
            context['unconfirmed_project_areas'] = ProjectArea.objects.filter(project=selected_project,
                                                                              is_confirmed=False)
            context['accept_area_reasons'] = AreaReason.objects.filter(type='accept')
            context['reject_area_reasons'] = AreaReason.objects.filter(type='reject')
            if selected_project.expert is None:
                context['experts'] = Expert.objects.all()

        if user_is_research_director:
            if selected_project.expert is None:
                context['research_experts'] = ResearchExpert.objects.all()

        if user_is_project_expert or user_is_technical_manager:
            context['add_area_reasons'] = AreaReason.objects.filter(type='add')
            context['remove_area_reasons'] = AreaReason.objects.filter(type='remove')

            context['histories'] = ProjectAreaOpinion.objects.filter(project=selected_project)
            context['industrial_areas'] = IndustrialArea.objects.filter(confirmed=True).values_list('area',
                                                                                                    flat=True) \
                .exclude(projectarea__project=selected_project)

    if selected_project.project_type == "Industrial":
        context['project_areas'] = ProjectArea.objects.filter(project=selected_project)
        context['there_is_unconfirmed_area'] = ProjectArea.objects.filter(project=selected_project,
                                                                          area__confirmed=False).count()
    return render(request, 'dashboard/project_view.html', context)


@login_required
def project_management(request, project_primary_key):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    selected_project = Project.objects.get(pk=project_primary_key)
    context = {
        'selected_project': selected_project,
        'main_supervisor_accepted_by_expert': ProjectSupervisor.objects.filter(project=selected_project,
                                                                               state="Waiting for Admin Acceptance").first(),
        'contract_has_been_sent_to_owner': ProjectContract.objects.filter(project=selected_project,
                                                                          user=selected_project.owner,
                                                                          contract_type='Ownership').count(),
        'upload_contract_form': UploadMemberContractForm()
    }
    """
    Security Check
    """
    user_is_project_learner = ProjectLearner.objects.filter(project=selected_project, learner=request.user).count() == 1

    if request.user.is_superuser:
        permission_denied = False
    else:
        if not selected_project.is_valid:
            permission_denied = True
        elif selected_project.project_type == "Competition" and is_competition_manager(request.user) \
                and competition_manager_eligible_to_see(selected_project):
            permission_denied = False
        elif request.user not in get_project_collaborators(selected_project):
            permission_denied = True
        elif user_is_project_learner or is_project_member(selected_project, request.user):
            permission_denied = True
        else:
            permission_denied = False

    if permission_denied:
        return render(request, 'ivc_website/403.html')

    supervisor_or_mentor = is_project_supervisor(selected_project, request.user) or \
                           is_project_mentor(selected_project, request.user) or \
                           selected_project.main_supervisor == request.user

    if supervisor_or_mentor or request.user.is_superuser or request.user == selected_project.expert or \
            is_competition_manager(request.user):
        """
        we add a collaborator key in a context which shows the user's task on the templates
        """
        if is_project_supervisor(selected_project, request.user):
            context['collaborator'] = ProjectSupervisor.objects.filter(project=selected_project,
                                                                       supervisor=request.user)[0]
        elif is_project_mentor(selected_project, request.user):
            context['collaborator'] = ProjectMentor.objects.filter(project=selected_project,
                                                                   mentor=request.user)[0]

        if selected_project.main_supervisor is not None:
            context['average_of_proposal_score'] = get_average_of_proposal_score(selected_project.main_supervisor,
                                                                                 selected_project)

        if request.method == "POST":
            """
            for security check
            """
            is_user_project_supervisor = ProjectSupervisor.objects.filter(supervisor=request.user,
                                                                          project=selected_project).count()
            is_user_project_mentor = ProjectMentor.objects.filter(mentor=request.user,
                                                                  project=selected_project).count()
            is_user_project_main_supervisor = selected_project.main_supervisor == request.user
            is_expert = request.user == selected_project.expert
            without_main_supervisor = selected_project.main_supervisor is None

            if selected_project.status == 'New' or selected_project.status == "Pending":
                """
                remove post requests: only main supervisor, expert (without supervisor), and superuser has access to these features
                """
                if 'team-has-been-gathered-up' in request.POST:
                    contract_exists = ProjectContract.objects.filter(project=selected_project,
                                                                     user=selected_project.owner,
                                                                     contract_type='Ownership').count()
                    if request.user == selected_project.main_supervisor and not contract_exists:
                        send_contract_to_owner_and_wait_for_signature(selected_project)
                        messages.success(request, "Request has been submitted successfully")
                        return redirect(reverse('dashboard-projects-page', args=['Industrial']))

                if 'collaborator-remove-pk' in request.POST:
                    if is_user_project_main_supervisor or request.user.is_superuser or \
                            (is_expert and without_main_supervisor):
                        user_to_delete = User.objects.get(pk=request.POST.get('collaborator-remove-pk'))
                        requested_position = request.POST['collaborator-remove-position']
                        delete_collaborator_from_project(user_to_delete, selected_project, requested_position)
                        Log(user=request.user, log=f'Deleted {user_to_delete} from project "{selected_project}"').save()

                access_permitted = (selected_project.main_supervisor is None and is_expert) \
                                   or is_user_project_main_supervisor or request.user.is_superuser
                if 'accept-signature' in request.POST:
                    if access_permitted:
                        position = request.POST['position']
                        collaborator_pk = request.POST['accept-signature']
                        make_user_collaborator(position, collaborator_pk)
                        return HttpResponseRedirect(request.path_info)  # redirect to the same page

                """
                supervisor post requests: only main supervisor and superuser has access to these features:
                - supervisor-profile: when main supervisor or superuser wants to add a supervisor
                - accept-supervisor: in this case, we accept the supervisor
                - reject-supervisor: in this case, we reject him by deleting him from project supervisor schema
                """
                access_permitted = is_user_project_main_supervisor or request.user.is_superuser
                if 'supervisor-profile' in request.POST:
                    if access_permitted:
                        if ProjectSupervisor.objects.filter(project=selected_project).count() <= 5:
                            added_successfully, error = add_supervisor(request, selected_project)
                            if not added_successfully:
                                messages.error(request, error)
                        else:
                            messages.error(request, "Supervisor limit has exceeded (Only 5 supervisors are allowed "
                                                    "to be added)")
                if 'accept-supervisor' in request.POST:
                    if access_permitted:
                        contract_form = UploadMemberContractForm(request.POST, request.FILES)
                        if contract_form.is_valid():
                            supervisor_primary_key = request.POST.get('accept-supervisor')
                            selected_supervisor = ProjectSupervisor.objects.get(pk=supervisor_primary_key)
                            Log(user=request.user,
                                log=f'Accepted {selected_supervisor.supervisor} to be the supervisor of project "{selected_project.title}"').save()
                            accept_supervisor(selected_supervisor, selected_project, request.FILES['contract'])

                if 'accept-main-supervisor' in request.POST:
                    if request.user.is_superuser or is_expert or is_competition_manager(request.user):
                        supervisor_primary_key = request.POST.get('accept-main-supervisor')
                        selected_supervisor = ProjectSupervisor.objects.get(pk=supervisor_primary_key)
                        main_supervisor_user = selected_supervisor.supervisor
                        accept_main_supervisor(selected_supervisor, selected_project)
                        if is_expert or is_competition_manager(request.user):
                            messages.success(request,
                                             'Main supervisor has been accepted successfully, now superusers should check that out')
                            if is_expert:
                                return redirect(reverse('dashboard-projects-page', args=['Industrial']))
                            else:
                                return redirect(reverse('dashboard-projects-page', args=['Competition']))
                        Log(user=request.user,
                            log=f'Accepted {main_supervisor_user} to be the main supervisor of project "{selected_project.title}"').save()

                if 'reject-supervisor' in request.POST:
                    if access_permitted or \
                            (is_expert or is_competition_manager(request.user) and
                             selected_project.main_supervisor is None):
                        mentor_primary_key = request.POST.get('reject-supervisor')
                        selected_supervisor = ProjectSupervisor.objects.get(pk=mentor_primary_key)
                        selected_user = selected_supervisor.supervisor
                        selected_supervisor.delete()
                        Log(user=request.user,
                            log=f"rejected {selected_user} on project {selected_project.title}").save()

                """
                mentor post requests: supervisors and superusers have access to these
                - mentor-profile: when clicked someone's name on autocomplete. in this case we add him as
                 a pending mentor
                - accept-mentor: accept him by changing pending to False
                - reject-mentor: reject him by deleting from project mentor schema
                """
                access_permitted = is_user_project_main_supervisor or is_user_project_supervisor or request.user.is_superuser
                if 'mentor-profile' in request.POST:
                    if access_permitted:
                        added_successfully, added_mentor = add_mentor(request, selected_project)
                        if not added_successfully:
                            messages.error(request, "ERROR, the collaborator is either already a member or mentor")

                    else:
                        return render(request, 'ivc_website/403.html')

                if 'accept-mentor' in request.POST:
                    if access_permitted:
                        mentor_primary_key = request.POST.get('accept-mentor')
                        """
                        here we have two options:
                        try section: user has select option (so he's either superuser or main supervisor) and selects a
                        supervisor for him

                        except ObjectDoesNotExist: in case user is a normal supervisor and in this case he doesn't have 
                        any select option and when he accept a mentor, then he's his own supervisor
                        """
                        try:
                            selected_supervisor = User.objects.get(pk=request.POST.get('select-supervisor'))
                        except (ObjectDoesNotExist, ValueError):  # in case there is no select option
                            selected_supervisor = request.user

                        contract_form = UploadMemberContractForm(request.POST, request.FILES)
                        if contract_form.is_valid():
                            selected_mentor = ProjectMentor.objects.get(pk=mentor_primary_key)
                            selected_mentor.project_supervisor = selected_supervisor
                            selected_mentor.save()
                            Log(user=request.user,
                                log=f'Accepted {selected_mentor.mentor} to be the mentor of project "{selected_project.title}"').save()
                            accept_mentor(selected_project, selected_mentor, request.FILES['contract'])

                if 'reject-mentor' in request.POST:
                    if access_permitted:
                        mentor_primary_key = request.POST.get('reject-mentor')
                        selected_mentor = ProjectMentor.objects.get(pk=mentor_primary_key)
                        selected_user = selected_mentor.mentor
                        selected_mentor.delete()

                        Log(user=request.user,
                            log=f"rejected {selected_user} on project {selected_project.title}").save()

                """
                Learner post requests:
                - learner-profile: add a learner to pending learners
                - accept-learner: accept him by changing pending to false
                - reject-learner: reject a learner by deleting him from project learner schema
                """
                access_permitted = is_user_project_main_supervisor or is_user_project_supervisor or is_user_project_mentor \
                                   or request.user.is_superuser
                if 'learner-profile' in request.POST:
                    if access_permitted:
                        added_successfully, added_learner = add_learner(request, selected_project)
                        if not added_successfully:
                            messages.error(request,
                                           "ERROR, the collaborator is already a learner, or the value entered is incorrect")
                    else:
                        return render(request, 'ivc_website/403.html')

                if 'accept-learner' in request.POST:
                    if access_permitted:
                        learner_primary_key = request.POST.get('accept-learner')
                        """
                        here we have two options:
                        try section: user has select option (so he's either superuser, mentor or main supervisor) and
                         selects a supervisor for him
                        except ObjectDoesNotExist: in case user is a normal supervisor (or mentor) and in this case he
                         doesn't have  any select option and when he accept a learner, then he's his own mentor
                        """
                        try:
                            selected_mentor = User.objects.get(pk=request.POST.get('select-mentor'))
                        except (ObjectDoesNotExist, ValueError):  # in case there is no select option
                            selected_mentor = request.user

                        contract_form = UploadMemberContractForm(request.POST, request.FILES)
                        if contract_form.is_valid():
                            selected_learner = ProjectLearner.objects.get(pk=learner_primary_key)
                            selected_learner.project_mentor = selected_mentor
                            selected_learner.save()

                            Log(user=request.user,
                                log=f'Accepted {selected_learner.learner} to be the learner of project "{selected_project.title}"').save()
                            accept_learner(selected_learner, selected_project, request.FILES['contract'])

                if 'reject-learner' in request.POST:
                    if access_permitted:
                        learner_primary_key = request.POST.get('reject-learner')
                        selected_learner = ProjectLearner.objects.get(pk=learner_primary_key)
                        selected_user = selected_learner.learner
                        selected_learner.delete()
                        Log(user=request.user,
                            log=f"rejected {selected_user} on project {selected_project.title}").save()

                """
                member post requests: everyone whom they're not ordinary member and assigned to this project has access
                to these requests

                - member-profile: when clicked someone's name on autocomplete. in this case we add him as
                 a pending member
                - accept-collaborator: accept him by changing pending to False
                - reject-reject: reject him by deleting from project mentor schema
                """
                access_permitted = is_user_project_main_supervisor or is_user_project_supervisor or is_user_project_mentor \
                                   or request.user.is_superuser
                if 'member-profile' in request.POST:  # in case when mentor wants to add a collaborator
                    if access_permitted:
                        parent = request.user
                        added_successfully, added_member = add_pending_member(request, selected_project, parent)
                        if not added_successfully:
                            messages.error(request, f"Selected member is already a collaborator, or the value entered "
                                                    f"is incorrect")
                    else:
                        return render(request, 'ivc_website/403.html')

                if 'accept-collaborator' in request.POST:  # in case when mentor wants to accept a collaborator
                    if access_permitted:
                        try:  # to check if request.user has option to select mentor or not
                            selected_member = User.objects.get(pk=request.POST.get('select-mentor'))
                        except (ObjectDoesNotExist, ValueError):  # in case there is no select option
                            selected_member = request.user

                        contract_form = UploadMemberContractForm(request.POST, request.FILES)
                        if contract_form.is_valid():
                            Log(user=request.user,
                                log=f'Accepted {selected_member} to be the member of project "{selected_project.title}"').save()
                            accepted_successfully, error, selected_member = accept_collaborator(request.POST,
                                                                                                selected_member,
                                                                                                request.FILES[
                                                                                                    'contract'])
                            if not accepted_successfully:
                                messages.error(request, error)
                        return HttpResponseRedirect(request.path_info)  # redirect to the same page
                    else:
                        return render(request, 'ivc_website/403.html')

                if 'reject-collaborator' in request.POST:  # in case when mentor wants to reject a collaborator:
                    if access_permitted:
                        selected_member = reject_collaborator(request)
                    else:
                        return render(request, 'ivc_website/403.html')

                """
                in case when user wants to send email to collaborator and inform him that he requested him to be on the project
                """
                if 'email-learner-pk' in request.POST:
                    primary_key = int(request.POST['email-learner-pk'])
                    selected_project_learner = ProjectLearner.objects.get(pk=primary_key)
                    if not selected_project_learner.is_email_sent:
                        selected_project_learner.is_email_sent = True
                        selected_project_learner.save()

                        email_the_collaborator("Member", selected_project_learner.project_mentor, selected_project,
                                               selected_project_learner.learner.email,
                                               selected_project_learner.state)

                if 'email-member-pk' in request.POST:
                    primary_key = int(request.POST['email-member-pk'])
                    selected_project_member = ProjectMember.objects.get(pk=primary_key)
                    if not selected_project_member.is_email_sent:
                        selected_project_member.is_email_sent = True
                        selected_project_member.save()

                        email_the_collaborator("Member", selected_project_member.project_mentor, selected_project,
                                               selected_project_member.member.email,
                                               selected_project_member.state)

                if 'email-mentor-pk' in request.POST:
                    primary_key = int(request.POST['email-mentor-pk'])
                    selected_project_mentor = ProjectMentor.objects.get(pk=primary_key)
                    if not selected_project_mentor.is_email_sent:
                        selected_project_mentor.is_email_sent = True
                        selected_project_mentor.save()

                        email_the_collaborator("Mentor", selected_project_mentor.project_supervisor, selected_project,
                                               selected_project_mentor.mentor.email,
                                               selected_project_mentor.state)

                if 'email-supervisor-pk' in request.POST:
                    primary_key = int(request.POST['email-supervisor-pk'])
                    selected_project_supervisor = ProjectSupervisor.objects.get(pk=primary_key)
                    if not selected_project_supervisor.is_email_sent:
                        selected_project_supervisor.is_email_sent = True
                        selected_project_supervisor.save()

                        if selected_project.main_supervisor is None:
                            position = "Main Supervisor"
                        else:
                            position = "Supervisor"

                        email_the_collaborator(position, selected_project.main_supervisor, selected_project,
                                               selected_project_supervisor.supervisor.email,
                                               selected_project_supervisor.state)

            if 'new-task' in request.POST:  # when we want to assign a new task(s) to someone
                task_primary_key = request.POST['task-pk']
                task_position = request.POST['task-position']
                new_task = request.POST['new-task']
                if task_position == 'Supervisor':
                    selected_project_collaborator = ProjectSupervisor.objects.get(pk=task_primary_key)
                elif task_position == 'Mentor':
                    selected_project_collaborator = ProjectMentor.objects.get(pk=task_primary_key)
                else:
                    selected_project_collaborator = ProjectMember.objects.get(pk=task_primary_key)
                selected_project_collaborator.tasks = new_task
                selected_project_collaborator.save()

            if 'agent-choose' in request.POST:  # when main-supervisor wants to assign an agent
                if selected_project.main_supervisor == request.user:
                    chosen_agent = request.POST['agent-choose']
                    if chosen_agent == "---":
                        selected_project.agent = None
                        selected_project.save()
                    else:
                        agent_id = int(chosen_agent.split("(")[1].split(")")[0])
                        agent = User.objects.get(id=agent_id)
                        selected_project.agent = agent
                        selected_project.save()

            if 'agent-permission' in request.POST:  # in case we want to give permission to agent for editing meetings
                # or withdraw one
                if selected_project.main_supervisor == request.user:
                    if selected_project.agent_permission:
                        selected_project.agent_permission = False
                    else:
                        selected_project.agent_permission = True
                    selected_project.save()
            if 'urgent-project' in request.POST:  # To make a new project urgent or vice versa
                if selected_project.main_supervisor == request.user or request.user.is_superuser:
                    if selected_project.is_urgent:
                        selected_project.is_urgent = False
                    else:
                        selected_project.is_urgent = True
                    selected_project.save()

            return HttpResponseRedirect(request.path_info)  # redirect to the same page

        if 'from-sort-priority' in request.GET:
            response = change_sort(request.GET, selected_project)
            if 'SUCCESS' not in response:
                messages.error(request, response)
            return JsonResponse({'response': response}, safe=False)

    add_members_to_context(context, selected_project)
    return render(request, 'dashboard/project_management.html', context)


@login_required()
def edit_project(request, project_pk):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    given_project = Project.objects.get(pk=project_pk)
    permission_denied = True
    if given_project.is_valid:
        if given_project.owner == request.user or given_project.main_supervisor == request.user:
            permission_denied = False
    if request.user.is_superuser:
        permission_denied = False

    if permission_denied:
        return render(request, 'ivc_website/403.html')

    if request.POST:
        edit_form = EditProjectForm(request.POST, request.FILES, instance=given_project)
        if edit_form.is_valid():
            edit_form.save()
            messages.success(request, f'Project {given_project.title} has updated')
            return redirect(reverse('dashboard-projects-page', args=[given_project.project_type]))
    else:
        edit_form = EditProjectForm(instance=given_project)

    return render(request, 'dashboard/edit_project.html', {'project': given_project, 'form': edit_form})


@user_passes_test(has_member_access)
def dashboard_members(request):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    """
    At first we prepare the url filters
    """
    url_filters = ""
    for parameter in request.GET:
        if parameter == 'page':
            continue
        for value in request.GET.getlist(parameter):
            url_filters += f"{parameter}={value}&"
    url_filters = url_filters[:-1]  # removes & at the end

    """
    Then we get filters and number of people included in that filter to show on result filtering section
    """
    filter_numbers = {}
    if request.user.is_superuser:
        filter_numbers['Without Images'] = User.objects.filter(Q(memberprofile__image='default_profile.jpg') |
                                                               Q(legalprofile__image='default_legal.png')).count()
        filter_numbers['Incomplete Profile'] = User.objects.filter(Q(memberprofile__about_me=None) |
                                                                   Q(legalprofile__isnull=False,
                                                                     legalprofile__work_area=None)).count()

    for interest in interest_choices:
        filter_numbers[interest[0]] = User.objects.filter(memberprofile__interest__contains=interest[0]).count()
    filter_numbers['Supervisor'] = User.objects.filter(memberprofile__position="Supervisor").count()
    filter_numbers['Mentor'] = User.objects.filter(memberprofile__position="Mentor").count()
    filter_numbers['Member'] = User.objects.filter(memberprofile__position="Member").count()
    filter_numbers['Internship'] = User.objects.filter(memberprofile__is_internship=True).count()

    if request.method == "POST":
        if 'send-user-email' in request.POST:
            if request.user.is_superuser:
                user_primary_key = request.POST['send-user-email']
                selected_user = User.objects.get(pk=user_primary_key)
                email_subject = request.POST['email-subject']
                email_content = request.POST['email-content']
                send_new_email(email_subject, email_content, selected_user.email)
                UserEmail(email_subject=email_subject, email_content=email_content, sender=request.user,
                          receiver=selected_user).save()

        elif 'send-all-email' in request.POST:
            if request.user.is_superuser:
                selected_users = User.objects.none()
                email_subject = request.POST['email-subject']
                email_content = request.POST['email-content']
                for parameter in request.GET:
                    if parameter == 'filter':
                        for value in request.GET.getlist(parameter):
                            if value == 'Without Images':
                                selected_users |= User.objects.filter(Q(memberprofile__image='default_profile.jpg') |
                                                                      Q(legalprofile__image='default_legal.png'))
                            if value == 'Incomplete Profile':
                                selected_users |= User.objects.filter(Q(memberprofile__about_me=None) |
                                                                      Q(legalprofile__isnull=False,
                                                                        legalprofile__work_area=None))
                            if value == 'Supervisor':
                                selected_users |= User.objects.filter(memberprofile__position="Supervisor")
                            if value == 'Mentor':
                                selected_users |= User.objects.filter(memberprofile__position="Mentor")
                            if value == 'Member':
                                selected_users |= User.objects.filter(memberprofile__position="Member")
                            interests = [tuple[0] for tuple in list(interest_choices)]
                            if value in interests:
                                selected_users |= User.objects.filter(memberprofile__interest__contains=value)

                for selected_user in selected_users:
                    send_new_email(email_subject, email_content, selected_user.email)
                    UserEmail(email_subject=email_subject, email_content=email_content, sender=request.user,
                              receiver=selected_user).save()
        else:
            chosen_members = User.objects.get_queryset().order_by('id')
    else:
        # getting all members by default based on their id
        if 'search' in request.GET:  # if user searched someone
            searched_str = request.GET.get('search')
            # get results based on search, we check that search content is matched with first or last name of
            # profile models or not:
            chosen_members = User.objects.none()
            for searched_substring in searched_str.split():
                chosen_members = User.objects.filter(first_name__istartswith=searched_substring)
                chosen_members |= User.objects.filter(last_name__istartswith=searched_substring)
                chosen_members |= User.objects.filter(legalprofile__company_name__istartswith=searched_substring)
            if searched_str == "":  # if user enter nothing, get all members
                chosen_members = User.objects.all()
        else:
            chosen_members = User.objects.all()

    if request.GET.get('filter'):  # if user filtered our search:
        # filter the result by interest:
        filter_result = User.objects.none()
        for user_filter in request.GET.getlist('filter'):
            if user_filter == 'Supervisor':
                filter_result |= chosen_members.filter(memberprofile__position="Supervisor")
            elif user_filter == 'Mentor':
                filter_result |= chosen_members.filter(memberprofile__position="Mentor")
            elif user_filter == 'Member':
                filter_result |= chosen_members.filter(memberprofile__position="Member")
            elif user_filter == 'Internship':
                filter_result |= chosen_members.filter(memberprofile__is_internship=True)
            elif user_filter == 'Without Images':
                if request.user.is_superuser:
                    filter_result |= chosen_members.filter(Q(memberprofile__image='default_profile.jpg') |
                                                           Q(legalprofile__image='default_legal.png'))
            elif user_filter == 'Incomplete Profile':
                if request.user.is_superuser:
                    filter_result |= chosen_members.filter(Q(memberprofile__about_me=None) |
                                                           Q(legalprofile__work_area=None))
            else:
                filter_result |= chosen_members.filter(memberprofile__interest__contains=user_filter)  # union
                # this result with previous ones
        chosen_members = filter_result
    chosen_members = handle_advanced_search(request, chosen_members)
    if request.GET.get('sort') is not None:
        chosen_members = handle_sort(request, chosen_members)

    # we use django paginator to show 7 person per age instead of all persons in one page
    paginator = Paginator(chosen_members, 7)
    current_page_number = request.GET.get('page')
    page_obj = paginator.get_page(current_page_number)

    context = {
        'chosen_members': page_obj,
        'filters': filter_numbers,
        'total_results': chosen_members.count(),
        'url_filters': url_filters,
        'degree_choices': degree_choices,
        'field_of_study_choices': field_of_study_choices,
        'status_choices': status_choices
    }

    return render(request, 'dashboard/members.html', context)


@user_passes_test(has_member_access)
def dashboard_profile(request, user_id):
    if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    opening_profile = User.objects.get(id=user_id)
    if request.method == "POST":
        if 'assign-new-collaboration' in request.POST:
            if request.user.is_superuser:
                title = request.POST.get('title')
                task = request.POST.get('content')
                section = request.POST.get('section')
                if len(title.strip()) > 0 and len(task.strip()) > 0 and len(section.strip()) > 0:
                    CompanyCollaboration(user=opening_profile, content=task, title=title, section=section).save()
                    return JsonResponse({"success": True}, safe=True)

        if 'rating' in request.POST:
            project_pk = request.POST['project-pk']
            project = Project.objects.get(pk=project_pk)
            rating = int(request.POST['rating'])
            if 0 < rating <= 5 and request.user in get_project_collaborators(project):
                ProjectRating(project=project, collaborator=opening_profile, reviewer=request.user,
                              rating=rating).save()
                return JsonResponse({"success": True}, safe=True)

            return JsonResponse({"success": False}, safe=True)

        if 'new-position' in request.POST:
            if request.user.is_superuser:
                new_position = request.POST['new-position']
                profile_member_profile = opening_profile.memberprofile
                profile_member_profile.position = new_position
                profile_member_profile.save()
                return JsonResponse({"success": True}, safe=True)
            return JsonResponse({"success": False}, safe=True)

    """
    NOTE: Since collaborated projects tab requires lots of queries, we have two context key with same values:
    - total_projects_collaborated: for project scores.
    - projects_collaborated: for collaborated projects tab which is paged 7 items per page to increase loading speed
    """

    context = {
        'profile': opening_profile,
        'total_projects_collaborated': get_all_collaborated_projects(opening_profile),
        "company_collaborations": CompanyCollaboration.objects.filter(user=opening_profile),
        'experience_badges': PersonExperienceBadge.objects.filter(user=opening_profile)
    }

    is_expert = Expert.objects.filter(user=opening_profile).count()
    if is_expert:
        expert = Expert.objects.get(user=opening_profile)
        context['expertises'] = ExpertArea.objects.filter(expert=expert, agree=True)

    projects_collaborated = get_all_collaborated_projects(opening_profile)
    page = request.GET.get('page', 1)
    paginator = Paginator(projects_collaborated, 7)
    try:
        context['projects_collaborated'] = paginator.page(page)
    except PageNotAnInteger:
        context['projects_collaborated'] = paginator.page(1)
    except EmptyPage:
        context['projects_collaborated'] = paginator.page(paginator.num_pages)

    return render(request, 'dashboard/profile.html', context)


@login_required
def announcement(request):
    if user_has_memberprofile(request.user):
        if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
            return redirect(f"{reverse('profile-page')}?next=/dashboard/")
    elif request.user.legalprofile.work_area is None:
        return redirect(f"{reverse('profile-page')}?next=/dashboard/")

    if request.POST:
        user_is_supervisor = user_has_memberprofile(
            request.user) and request.user.memberprofile.position == "Supervisor"
        request_is_accepted = request.user.is_superuser or user_is_supervisor
        if request_is_accepted:
            form = AnnouncementForm(request.POST)

            if 'title' in request.POST:  # new announcement
                if form.is_valid():
                    form.save()
                    announcement_title = form.cleaned_data.get('title')  # get announcement title from title
                    new_announcement = Announcement.objects.filter(title=announcement_title)[0]  # get the announcement
                    new_announcement.owner = request.user
                    new_announcement.save()
                    messages.success(request, f'Announcement added successfully')
                else:
                    messages.error(request, f"Announcement title already exists, please enter a new one")
            elif 'data-pk' in request.POST:  # removing announcement
                selected_announcement = Announcement.objects.get(pk=request.POST['data-pk'])
                if selected_announcement.owner == request.user:  # if request is valid (for security reason)
                    selected_announcement.delete()
        return HttpResponseRedirect(request.path_info)  # redirect to the same page
    else:
        form = AnnouncementForm()
    announcements = Announcement.objects.all().order_by('-creation_time')

    unseen_announcements = Announcement.objects.exclude(announcementview__user=request.user)
    for unseen_announcement in unseen_announcements:
        if unseen_announcement in announcements:
            new_announcement_view = AnnouncementView(announcement=unseen_announcement,
                                                     user=request.user)
            new_announcement_view.save()

    return render(request, 'dashboard/announcement.html', {'announcements': announcements, 'form': form})


@login_required
def weekly_meeting_page(request, project_pk):
    selected_project = Project.objects.get(pk=project_pk)
    permission_denied = request.user != selected_project.main_supervisor and \
                        (selected_project.agent != request.user or not selected_project.agent_permission)
    if permission_denied:
        return render(request, 'ivc_website/403.html')

    if request.POST:
        if 'time-pk' in request.POST:  # when we want to check or uncheck an attendee
            time_pk = request.POST['time-pk']
            collaborator_pk = request.POST['collaborator-pk']
            value_selected = request.POST['value-selected']

            selected_weekly_meeting = WeeklyMeetingTime.objects.get(pk=time_pk)
            selected_attendee = User.objects.get(pk=collaborator_pk)

            attendee_has_set_before = WeeklyMeetingAttendee.objects.filter(weekly_meeting=selected_weekly_meeting,
                                                                           attendee=selected_attendee).count()
            if value_selected == 'Absence':
                if attendee_has_set_before:
                    WeeklyMeetingAttendee.objects.filter(weekly_meeting=selected_weekly_meeting,
                                                         attendee=selected_attendee).delete()
            elif value_selected == 'Presence':
                if attendee_has_set_before:
                    WeeklyMeetingAttendee.objects.filter(weekly_meeting=selected_weekly_meeting,
                                                         attendee=selected_attendee).update(acceptable_absence=False)
                else:
                    WeeklyMeetingAttendee(weekly_meeting=selected_weekly_meeting, attendee=selected_attendee).save()
            elif value_selected == "Acceptable Absence":
                if attendee_has_set_before:
                    WeeklyMeetingAttendee.objects.filter(weekly_meeting=selected_weekly_meeting,
                                                         attendee=selected_attendee).update(acceptable_absence=True)
                else:
                    WeeklyMeetingAttendee(weekly_meeting=selected_weekly_meeting, attendee=selected_attendee,
                                          acceptable_absence=True).save()

        if 'remove-time-pk' in request.POST:  # if we want to delete a row
            time_pk = request.POST['remove-time-pk']
            WeeklyMeetingTime.objects.get(pk=time_pk).delete()
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

        if 'add-next' in request.POST:  # when we want to add a new row to the table
            weekday_dict = {
                "Monday": 0,
                "Tuesday": 1,
                "Wednesday": 2,
                "Thursday": 3,
                "Friday": 4,
                "Saturday": 5,
                "Sunday": 6,
            }
            project_weekday = selected_project.week_day
            project_time = selected_project.meeting_time

            if project_weekday is None:
                messages.error(request, "You have to set a week day for the project meeting first!")
                return HttpResponseRedirect(request.path_info)  # redirect to the same page
            if project_time is None:
                messages.error(request, "You have to set a time for the project meeting first!")
                return HttpResponseRedirect(request.path_info)  # redirect to the same page

            if WeeklyMeetingTime.objects.filter(project=selected_project).count():  # if at least one time exists
                offset_day = WeeklyMeetingTime.objects.filter(project=selected_project).latest(
                    'weekly_meeting_time').weekly_meeting_time
            else:
                offset_day = datetime.datetime.now().replace(hour=project_time.hour, minute=project_time.minute)
            next_time = next_weekday(offset_day, weekday_dict[project_weekday])

            new_weekly_meeting_time = WeeklyMeetingTime(project=selected_project, weekly_meeting_time=next_time)
            new_weekly_meeting_time.save()
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    collaborators = get_project_collaborators(selected_project)
    weekly_meeting_times = WeeklyMeetingTime.objects.filter(project=selected_project)

    context = {
        'selected_project': selected_project,
        'collaborators': collaborators,
        'times': weekly_meeting_times
    }

    return render(request, 'dashboard/weekly_meeting_attendees.html', context)


@login_required
def dashboard_edit_meeting(request, project_pk):
    """
    View that changes meeting time of a project
    """
    selected_project = Project.objects.get(pk=project_pk)

    permission_denied = request.user != selected_project.main_supervisor and \
                        (request.user != selected_project.agent or (
                            not selected_project.agent_permission))
    if permission_denied:
        return render(request, 'ivc_website/403.html')

    if request.POST:
        given_form = MeetingForm(request.POST, instance=selected_project)
        if given_form.is_valid():
            given_form.save()
            messages.success(request, "Meeting time has changed successfully")

            # email to collaborators
            collaborators = get_project_collaborators(selected_project)

            for collaborator in collaborators:
                email_subject = "A new meeting time has been set"
                email_content = f"""
A new meeting has been set for the project "{selected_project.title}"
Day of the week: {selected_project.week_day}
Time: {selected_project.meeting_time} ({selected_project.meeting_timezone})
"""
                destination_email = collaborator.email
                threading.Thread(target=send_new_email,
                                 args=(email_subject, email_content, destination_email)).start()

            if 'next' in request.GET:
                return redirect(request.GET.get('next'))
            else:
                return redirect(reverse('dashboard-projects-page', args=[selected_project.project_type]))
        else:
            messages.error(request, 'Form is invalid!')
            return HttpResponseRedirect(request.path_info)  # redirect to the same page

    project_meeting_form = MeetingForm(instance=selected_project)

    return render(request, 'dashboard/edit_meeting.html', context={
        'meeting_form': project_meeting_form,
        'project_title': selected_project.title
    })


@login_required
def proposal_page(request, project_pk):
    selected_project = Project.objects.get(pk=project_pk)

    user_is_not_supervisor = request.user.memberprofile.position != "Supervisor"
    project_has_main_supervisor_and_he_is_not_the_user = selected_project.main_supervisor is not None and \
                                                         request.user != selected_project.main_supervisor

    permission_denied = user_has_memberprofile(request.user) and user_is_not_supervisor \
                        or project_has_main_supervisor_and_he_is_not_the_user or request.user == selected_project.expert
    if permission_denied:
        return render(request, 'ivc_website/403.html')

    if request.method == "POST":
        proposal = ProjectProposalForm(request.POST, request.FILES)
        if proposal.is_valid():
            submitted_proposal = proposal.save(commit=False)
            action = request_or_withdraw_a_project(project_pk, request.user, "Supervisor")
            if action == "REQUEST":
                project_supervisor = ProjectSupervisor.objects.get(project=selected_project, supervisor=request.user)
                submitted_proposal.project_supervisor = project_supervisor
                submitted_proposal.save()
                messages.success(request, f'Your application has been submitted successfully.')
            else:
                messages.error(request,
                               'Your application has been failed. please contact our team and report the problem.')
        else:
            messages.error(request, 'Your proposal format should be PDF')

        return redirect('dashboard-projects-page', project_type=selected_project.project_type)

    proposal_exists = ProjectProposal.objects.filter(project_supervisor__project=selected_project,
                                                     project_supervisor__supervisor=request.user).count()
    if proposal_exists:
        proposal = ProjectProposal.objects.get(project_supervisor__project=selected_project,
                                               project_supervisor__supervisor=request.user)
    else:
        proposal = None

    return render(request, 'dashboard/proposal.html', context={
        'selected_project': selected_project,
        'proposal': proposal,
        'form': ProjectProposalForm(),
        'eligible_to_send_proposal': selected_project.main_supervisor is None
    })


@login_required
def question_and_answer_panel(request):
    context = {
        'recently_defined_question_numbers': Question.objects.filter(is_verified=None).count(),
        'recent_answer_numbers': Answer.objects.filter(is_verified=None).count(),
        'rejected_question_numbers': Question.objects.filter(is_verified=False).count(),
        'rejected_answer_numbers': Answer.objects.filter(is_verified=False).count(),
    }

    if request.method == "POST":
        if 'accept-question' in request.POST:
            question_pk = request.POST.get('accept-question')
            the_question = Question.objects.get(pk=question_pk)
            the_question.is_verified = True
            the_question.save()
            messages.success(request, 'Question accepted successfully')

        if 'reject-question' in request.POST:
            question_pk = request.POST.get('reject-question')
            the_question = Question.objects.get(pk=question_pk)
            the_question.is_verified = False
            the_question.save()
            messages.success(request, 'Question rejected successfully')

        if 'accept-answer' in request.POST:
            answer_pk = request.POST.get('accept-answer')
            the_answer = Answer.objects.get(pk=answer_pk)
            the_answer.is_verified = True
            the_answer.save()
            messages.success(request, 'Answer accepted successfully')

        if 'reject-answer' in request.POST:
            answer_pk = request.POST.get('reject-answer')
            the_answer = Answer.objects.get(pk=answer_pk)
            the_answer.is_verified = False
            the_answer.save()
            messages.success(request, 'Answer rejected successfully')

        if 'undo-question' in request.POST:
            question_pk = request.POST.get('undo-question')
            the_question = Question.objects.get(pk=question_pk)
            the_question.is_verified = None
            the_question.save()
            messages.success(request, 'Question undid successfully')

        if 'undo-answer' in request.POST:
            answer_pk = request.POST.get('undo-answer')
            the_answer = Answer.objects.get(pk=answer_pk)
            the_answer.is_verified = None
            the_answer.save()
            messages.success(request, 'Answer undid successfully')

        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    if 'filter' in request.GET:
        given_filter = request.GET.get('filter')
        if given_filter == 'recently_defined_questions':
            context['recently_defined_questions'] = Question.objects.filter(is_verified=None)
        if given_filter == 'recent_answers':
            context['recent_answers'] = Answer.objects.filter(is_verified=None)
        elif given_filter == 'rejected_questions':
            context['rejected_questions'] = Question.objects.filter(is_verified=False)
        elif given_filter == 'rejected_answers':
            context['rejected_answers'] = Answer.objects.filter(is_verified=False)

    return render(request, 'dashboard/question_and_answer.html', context)


@login_required
def interviewer_panel(request):
    is_interviewer = Interviewer.objects.filter(user=request.user).count()
    if not is_interviewer:
        return render(request, 'ivc_website/403.html')

    users_without_badges = User.objects.filter(legalprofile__isnull=True,
                                               personexperiencebadge__isnull=True,
                                               projectsupervisor__isnull=True,
                                               project_mentor_mentor__isnull=True,
                                               project_member_member__isnull=True,
                                               project_learner_learner__isnull=True,
                                               project_main_supervisor__isnull=True).order_by('-date_joined')

    if 'search' in request.GET:
        search_value = request.GET.get('search')
        users_without_badges = users_without_badges.filter(Q(first_name__icontains=search_value)
                                                           | Q(last_name__icontains=search_value))

    paginator = Paginator(users_without_badges, 20)
    current_page_number = request.GET.get('page')
    page_obj = paginator.get_page(current_page_number)
    context = {
        'users_without_badges': page_obj
    }

    return render(request, 'dashboard/interviewer.html', context)


@login_required
def change_experience_badges(request, user_pk):
    is_interviewer = Interviewer.objects.filter(user=request.user).count()
    if not is_interviewer:
        return render(request, 'ivc_website/403.html')

    selected_user = User.objects.get(pk=user_pk)

    if request.method == "POST":
        # remove previous settings
        PersonExperienceBadge.objects.filter(user=selected_user).delete()

        # add new settings
        for key in request.POST:
            if 'chosen-badge' in key:
                number = key.split('-')[-1]
                badge_pk = request.POST.get(key)

                score = request.POST.get(f"score-{number}")
                badge = ExperienceBadge.objects.get(pk=badge_pk)

                badge_already_exists = PersonExperienceBadge.objects.filter(badge=badge, user=selected_user).count()
                if badge_already_exists:
                    person_badge = PersonExperienceBadge.objects.get(badge=badge, user=selected_user)
                    person_badge.score = score
                    person_badge.save()
                else:
                    PersonExperienceBadge(badge=badge, user=selected_user, score=score).save()

        messages.success(request, "Changes have been submitted successfully")
        return HttpResponseRedirect(request.path_info)  # redirect to the same page

    context = {
        'selected_user': selected_user,
        'experience_badges': ExperienceBadge.objects.all(),
        'current_badges': PersonExperienceBadge.objects.filter(user=selected_user)
    }
    return render(request, 'dashboard/change_experience_badges.html', context)


def forum_list(request):
    template_name = 'dashboard/forum.html'
    if request.user.is_superuser or request.user.forumrole.is_staff == True:
        object_list = Postes.objects.all()
    else:
        object_list = Postes.objects.filter(author=request.user)

    if request.method == 'POST':
        # Delete topic
        form_delete_topic = DeleteTopicForm(request.POST, request.FILES)
        if form_delete_topic.is_valid():
            topic_id = form_delete_topic.cleaned_data.get("topic_id")

            obj_topic = Postes.objects.get(id=topic_id)
            obj_topic.deleted = True
            obj_topic.save()
            return redirect("forum",)



        # Edit category
        form_edit_category = EditCategory(request.POST, request.FILES)
        if form_edit_category.is_valid():
            title = form_edit_category.cleaned_data.get("text")
            img = form_edit_category.cleaned_data.get("img")
            status = form_edit_category.cleaned_data.get("status")
            category_id = form_edit_category.cleaned_data.get("category_id")

            obj_category = MainCategory.objects.get(id=category__id)

            if img:
                obj_category.img = img
            obj_category.title = title
            obj_category.status = status
            obj_category.save()
            return redirect("forum")

        # Edit sub category
        form_edit_sub_category = EditSubCategory(request.POST, request.FILES)
        if form_edit_sub_category.is_valid():
            title = form_edit_sub_category.cleaned_data.get("title")
            img = form_edit_sub_category.cleaned_data.get("img")
            status = form_edit_sub_category.cleaned_data.get("status")
            subcategory_id = form_edit_sub_category.cleaned_data.get("subcategory_id")
            obj_sub_category = Category.objects.get(id=subcategory__id)

            if img:
                obj_sub_category.img = img
            obj_sub_category.title = title
            obj_sub_category.status = status
            obj_sub_category.save()
            return redirect("forum")

        # Delete category
        form_delete_category = DeleteCategory(request.POST)
        if form_delete_category.is_valid():
            category_id = form_delete_category.cleaned_data.get("category_id")

            obj_category = MainCategory.objects.get(id=category_id)
            obj_category.delete()
            return redirect("forum")


        # Delete sub category
        form_delete_sub_category = DeleteSubCategory(request.POST)
        if form_delete_sub_category.is_valid():
            subcategory_id = form_delete_sub_category.cleaned_data.get("subcategory_id")

            obj_sub_category = Category.objects.get(id=subcategory_id)

            obj_sub_category.delete()
            return redirect("forum")



        # Create category
        form_create_category = CreateCategoryForm(request.POST, request.FILES)
        if form_create_category.is_valid():
            img = form_create_category.cleaned_data.get("img")
            title = form_create_category.cleaned_data.get("title_")
            status = form_create_category.cleaned_data.get("status")
            main_categorys = str(MainCategory.objects.all().count())

            slug = 'main-' + title + main_categorys
            slug = slug.split(' ')
            slug = ''.join(slug)

            create_category = MainCategory.objects.create(
                title=title, slug=slug, img=img)
            return redirect("forum")


        # Create sub category
        form_create_sub_category = CreateSubCategoryForm(request.POST, request.FILES)
        if form_create_sub_category.is_valid():
            img = form_create_category.cleaned_data.get("img")
            c_title = form_create_sub_category.cleaned_data.get("c_title")
            c_status = form_create_sub_category.cleaned_data.get("c_status")
            c_category_id = form_create_sub_category.cleaned_data.get("c_category_id")


            obj_sub_category = MainCategory.objects.get(id=c_category_id)
            categorys = str(Category.objects.all().count())

            slug = 'sub-' + c_title + categorys
            slug = slug.split(' ')
            slug = ''.join(slug)

            create_category = Category.objects.create(
                title=c_title, slug=slug, img=img, sub_category=obj_sub_category)

            return redirect("forum")
    context = {
        'object_list': object_list,
        'sub_categories': Category.objects.all(), 
        'categories': MainCategory.objects.all(), 
        'categories_work_research': Category.objects.filter(workshop_and_research=True)
    }
    return render(request, template_name, context)
        
        
@login_required
def admin_news(request):
    manager = NewsManager.objects.get(manager = request.user)
    category = Category.objects.all()
    if manager.is_super_author:
        news = News.objects.all()
    else:
        news = News.objects.filter(author = manager)
    
    context = {
        "news" : news,
        "author": manager,
        "category": category,
    }

    return render(request, "dashboard/news_author_list.html", context)


@login_required
def news_update(request, pk):
    news = News.objects.get(pk=pk)
    author = NewsManager.objects.get(manager = request.user)
    if request.method == "GET":
        if news.author == author and news.status in ['b','d'] or author.is_super_author:
            news_form = NewsForm(instance = news)
            context = {
                "news" : news_form,
                "author" : author,
            }
            return render(request, "dashboard/news_create_update.html", context)
        else:
            raise Http404("You can't see this page")
    elif request.method == "POST":
        if not author.is_super_author:
            data = request.POST.copy()
            data['author'] = author
            news_form = NewsForm(data, request.FILES, instance=news)
        else:
            news_form = NewsForm(request.POST, request.FILES, instance=news)

        if news_form.is_valid():
            news_form.save()
            return redirect("news-view")
        else:
            return redirect("news-view")

@login_required
def create_news(request):
    author = NewsManager.objects.get(manager = request.user)
    if request.method == "GET":
        news = NewsForm()
        context = {
            'news': news,
            "author" : author,
        }
        return render(request, 'dashboard/news_create_update.html', context)
    elif request.method == "POST":
        if not author.is_super_author:
            data = request.POST.copy()
            data['author'] = author
            news_form = NewsForm(data, request.FILES)
        else:
            news_form = NewsForm(request.POST, request.FILES)

        if news_form.is_valid():
            news_form.save()
            return redirect(reverse('news-view'))
        else:
            print (news_form.errors)
            messages.error(request, "An error has been occurred")
            return redirect(reverse('news-view'))


def delete_news(request, pk):
    news = News.objects.get(pk=pk)
    author = NewsManager.objects.get(manager = request.user)
    if request.method == 'GET':
        if author.is_super_author:
            context = {
            "news" : news,
            }
            return render(request, "dashboard/news_delete.html", context)
        else:
            raise Http404("You can't see this page")
    elif request.method == 'POST':
        news.delete()
        return redirect('news-view')

def news_preview(request, pk):
    news = News.objects.get(pk=pk)
    context = {
        "news":news,
    }
    return render(request, 'ivc_website/news_detail.html',context)


@login_required
def create_category(request):
    if request.method == "GET":
        category = CategoryForm()
        context = {
            'category': category,
        }
        return render(request, 'dashboard/news_category_create_update.html', context)
    elif request.method == "POST":
        category = CategoryForm(request.POST)
        if category.is_valid():
            category.save()
            return redirect(reverse('news-view'))
        else:
            print (category.errors)
            messages.error(request, "An error has been occurred")
            return redirect(reverse('news-view'))
            
@login_required
def admin_event(request):
    manager = NewsManager.objects.get(manager = request.user)
    if manager.is_super_author:
        event = Event.objects.all()
    else:
        event = Event.objects.filter(author = manager)
    
    context = {
        "event" : event,
        "author": manager,
    }

    return render(request, "dashboard/event_author_list.html", context)


@login_required
def create_event(request):
    author = NewsManager.objects.get(manager = request.user)
    if request.method == "GET":
        event = EventForm()
        context = {
            'event': event,
            "author" : author,
        }
        return render(request, 'dashboard/event_create_update.html', context)
    elif request.method == "POST":
        if not author.is_super_author:
            data = request.POST.copy()
            data['author'] = author
            event_form = EventForm(data, request.FILES)
        else:
            event_form = EventForm(request.POST, request.FILES)

        if event_form.is_valid():
            event_form.save()
            return redirect(reverse('event-view'))
        else:
            print (event_form.errors)
            messages.error(request, "An error has been occurred")
            return redirect(reverse('event-view'))


@login_required
def event_update(request, pk):
    event = Event.objects.get(pk=pk)
    author = NewsManager.objects.get(manager = request.user)
    if request.method == "GET":
        if event.author == author and event.status in ['b','d'] or author.is_super_author:
            event_form = EventForm(instance = event)
            context = {
                "event" : event_form,
                "author" : author,
            }
            return render(request, "dashboard/event_create_update.html", context)
        else:
            raise Http404("You can't see this page")
    elif request.method == "POST":
        if not author.is_super_author:
            data = request.POST.copy()
            data['author'] = author
            event_form = EventForm(data, request.FILES, instance=event)
        else:
            event_form = EventForm(request.POST, request.FILES, instance=event)

        if event_form.is_valid():
            event_form.save()
            return redirect("event-view")
        else:
            return redirect("event-view")



def delete_event(request, pk):
    event = Event.objects.get(pk=pk)
    author = NewsManager.objects.get(manager = request.user)
    if request.method == 'GET':
        if author.is_super_author:
            context = {
            "news" : event,
            }
            return render(request, "dashboard/news_delete.html", context)
        else:
            raise Http404("You can't see this page")
    elif request.method == 'POST':
        event.delete()
        return redirect('event-view')

def event_preview(request, pk):
    event = Event.objects.get(pk=pk)
    context = {
        "news":event,
    }
    return render(request, 'ivc_website/news_detail.html',context)
    


@login_required
def research_comment_management(request):
    template_name = 'dashboard/research-comment-management.html'
    if request.user.researchrole.comment_management == True:

        if request.method == 'POST':
            status = request.POST.get("status")
            id_comment = request.POST.get("id_comment")
            obj_comment = CommentProject.objects.get(id=id_comment)


            if status == 'accepted':
                obj_comment.status = 'accepted'
                messages.success(request,'The project has been accepted successfully.')

            elif status == 'rejected':
                obj_comment.status = 'rejected'
                messages.success(request,'The project has been rejected.')
            obj_comment.save()

            return redirect('research-comment-management')

        context = {
            'comments': CommentProject.objects.filter(status='new')
        }

        return render(request, template_name, context)

    else:
        raise Http404("You can't see this page.")



@login_required
def change_status_dollar(request):
    if request.user.is_superuser :
        template_name = 'payment_stripe/dollarPrice.html'
        if request.method == 'POST':
            # method = request.POST.get('method')
            price = int(request.POST.get('price'))


            # if method == 'on':
            create_dollar = Dollar.objects.create(Automatically=False, price=price, last_editor=request.user)


            return redirect('change-status-dollar')
        print(Dollar.objects.all().last())

        context = {
            'object_list': Dollar.objects.all().order_by('-created')
        }

        return render(request, template_name, context)
    else:
        raise Http404("You can't see this page.")