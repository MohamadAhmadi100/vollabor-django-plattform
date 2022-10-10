from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User
from users.models import Role
from django.contrib.auth.decorators import login_required
import json
from ivc_project.email_sender import send_new_email
from dashboard.models import Notification
import pytz
from datetime import timedelta
from research.models import ResearchRole
import random
from accounting.models import PaymentProtocol,Service,Invoice,RejectProtocol
from .forms import (
	BadgeForm, SessionForm, SupervisorForm, WorkshopRequestForm, 
	SelectReviewer, DeclineReviewerForm, ApproveReviewerForm,
	ReviewerSendForExpertForm, ChangeExpertManager 
	)
from .models import (
	BadgeRequest, InterviewSession, SupervisorRequest, WorkshopRequest, 
	BadgeInterviewReview, SupervisorReview, BadgeExpert, WorkshopReview, 
	)
from datetime import date
from datetime import timedelta
from research.models import ResearchRole
from users.models import MemberProfile

def user_has_memberprofile(given_user):
    return MemberProfile.objects.filter(user=given_user).count() == 1
@login_required
# Create your views here.
def request(request):
	context = {
		'user':request.user,
	}
	excludes=['Notpay','trash']
	if BadgeRequest.objects.filter(user = request.user).exclude(status__in =excludes ).exists():
		context['badges'] = BadgeRequest.objects.filter(user = request.user).exclude(status__in =excludes).order_by('-created')
	if SupervisorRequest.objects.filter(user = request.user).exclude(status__in = excludes).exists():
		context['supervisor'] = SupervisorRequest.objects.filter(user = request.user).exclude(status__in = excludes ).order_by('-created')
	if WorkshopRequest.objects.filter(user = request.user).exclude(status__in = excludes).exists():
		context['workshop'] = WorkshopRequest.objects.filter(user = request.user).exclude(status__in = excludes).order_by('-created')
	if BadgeRequest.objects.filter(user = request.user,status = 'Notpay').exists():
		context['unpaid_badges'] = BadgeRequest.objects.filter(user = request.user,status = 'Notpay').order_by('-created')
	if SupervisorRequest.objects.filter(user = request.user,status = 'Notpay').exists():
		context['unpaid_supervisor'] = SupervisorRequest.objects.filter(user = request.user,status = 'Notpay').order_by('-created')
	if WorkshopRequest.objects.filter(user = request.user,status = 'Notpay').exists():
		context['unpaid_workshop'] = WorkshopRequest.objects.filter(user = request.user,status = 'Notpay').order_by('-created')
	services=Service.objects.filter(user=request.user,action='request')
	invoicelist=[]
	for invoice in Invoice.objects.filter(user=request.user).all():
		for service in services:
			if invoice.service==service:
				invoicelist.append(invoice)
	context['invoces']=invoicelist

	return render(request, 'request/request.html', context)


def request_manager(request):
	badges = BadgeRequest.objects.all()

	badge_new_count = BadgeRequest.objects.filter(status='New').count()
	badge_interview_review_count = BadgeRequest.objects.filter(status__in=['Review','Set-session','Approve-decline','Interview','Expert-view','send_manager','decline-review-interview','Reject', 'revise_by_manager']).count()

	supervisor_new_count = SupervisorRequest.objects.filter(status='New').count()
	supervisor_reviewe_count = SupervisorRequest.objects.filter(status__in=['Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', 'revise_by_manager', 'revise_by_expert']).count()

	workshop_new_count = WorkshopRequest.objects.filter(status='New').count()
	workshop_reviewe_count = WorkshopRequest.objects.filter(status__in=['Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', 'revised_by_manager', 'revised_by_expert']).count()
	context = {
		'badges': badges,
		'badges_count': badge_new_count + badge_interview_review_count,

		'badge_new_count': badge_new_count,
		'badge_interview_review_count': badge_interview_review_count,

		'supervisor_form': SupervisorRequest.objects.all(),
		'supervisor_new_count': supervisor_new_count,
		'supervisor_reviewe_count': supervisor_reviewe_count,
		'supervisor_form_count': supervisor_new_count + supervisor_reviewe_count,
		'workshop_form': WorkshopRequest.objects.all(),
		'workshop_new_count': workshop_new_count,
		'workshop_reviewe_count': workshop_reviewe_count,
		'workshop_form_count': workshop_new_count + workshop_reviewe_count,
		# 'supervisor_form': SupervisorRequest.objects.filter(status="send_to_manager"),
	}
	return render(request, 'request/request-manager-list.html', context)


def manager_detail_supervisor(request, pk):
	obj_supervisor = get_object_or_404(SupervisorRequest, pk=pk)
	obj_review = get_object_or_404(SupervisorReview, supervisor=obj_supervisor, status='evaluated')

	if request.method == "POST":
		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')
			obj_supervisor.status = 'accepted_by_manager'
			obj_supervisor.accepted_date = timezone.now()
			obj_supervisor.user.memberprofile.position = 'Supervisor' 
			obj_supervisor.save()
			obj_supervisor.user.memberprofile.save()
			
			obj_review.status = 'done'
			obj_review.save()
			
			
			e_subject="TECVICO Request (ID: {})".format(obj_supervisor.id_request, )
			e_content = "Dear {}\nHope you are going well.\nCongratulations! Your supervisor request has been accepted. For more information, please go your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_supervisor.user.get_full_name(),)
			e_destination = obj_supervisor.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request, 'The supervisor request has been accepted.')
			return redirect('request:manager-list')

	context = {
		'obj_supervisor' : obj_supervisor,
		'obj_reviewer' : SupervisorReview.objects.get(supervisor=obj_supervisor, status='evaluated'),
	}
	return render(request, 'request/manager-detail-supervisor.html', context)

def reject_supervisor(request):
	comment = request.POST.get('comment')
	position = request.POST.get('position')
	id_request = int(request.POST.get('id_request'))

	obj_supervisor = get_object_or_404(SupervisorRequest, pk=id_request)
	obj_reviewer = SupervisorReview.objects.filter(supervisor=obj_supervisor, status='evaluated')
	
	for i in obj_reviewer:
	    i.status = 'done'
	    i.save()

	if position == 'manager':
		obj_supervisor.status = 'rejected_by_manager'
	else:
		obj_supervisor.status = 'rejected_by_expert'
	obj_supervisor.comment = comment
	obj_supervisor.rejected_date = timezone.now()
	obj_supervisor.save()
	RejectProtocol(request,'SR',obj_supervisor,50)
	
	e_subject="TECVICO Request (ID: {})".format(obj_supervisor.id_request, )
	e_content = "Dear {}\nHope you are going well.\nThank you for your supervisor request.\nThe company has reviewed your supervisor request.\nSubmitted date: {}\nTECVICO regrets to inform you that your supervisor request has been rejected. Moreover, the supervisor request fee has been returned to your account. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_supervisor.user.get_full_name(), obj_supervisor.created.date())
	e_destination = obj_supervisor.user.email
	send_new_email(e_subject,e_content,e_destination)

	
	messages.error(request, 'You rejected the supervisor request.')
	if position == 'manager':
		return redirect('request:manager-list')
	else:
		return redirect('request:expert')

def reject_workshop(request):
	comment = request.POST.get('comment')
	position = request.POST.get('position')
	id_request = int(request.POST.get('id_request'))

	print('comment', comment)
	print('position', position)
	print('id_request', id_request)


	obj_workshop = get_object_or_404(WorkshopRequest, pk=id_request)
	obj_reviewer = WorkshopReview.objects.filter(workshop=obj_workshop, status='evaluated')

	for i in obj_reviewer:
		i.status == 'done'
		i.save()

	if position == 'manager':
		obj_workshop.status = 'rejected_by_manager'
	else:
		obj_workshop.status = 'rejected_by_expert'
	obj_workshop.comment = comment
	obj_workshop.rejected_date = timezone.now()
	obj_workshop.save()
	RejectProtocol(request,'WR',obj_workshop,50)


	e_subject="TECVICO Request (ID: {})".format(obj_workshop.id_request, )
	e_content = "Dear {}\nHope you are going well.\nThank you for your workshop presenter request.\nThe company has reviewed your workshop presenter request.\nSubmitted date: {}\nTECVICO regrets to inform you that your workshop presenter request has been rejected. Moreover, the workshop presenter request fee has been returned to your account. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_workshop.user.get_full_name(), obj_workshop.created.date())
	e_destination = obj_workshop.user.email
	send_new_email(e_subject,e_content,e_destination)
	
	
	messages.error(request, 'You rejected the workshop presenter request.')

	if position == 'manager':
		return redirect('request:manager-list')
	else:
		return redirect('request:expert')


def revise_supervisor(request):
	comment = request.POST.get('comment')
	position = request.POST.get('position')
	id_request = int(request.POST.get('id_request'))

	obj_supervisor = get_object_or_404(SupervisorRequest, pk=id_request)
	obj_reviewer = get_object_or_404(SupervisorReview, supervisor=obj_supervisor, status="evaluated")

	if position == 'manager':
		obj_supervisor.status = 'revise_by_manager'
	else:
		obj_supervisor.status = 'revise_by_expert'
	obj_supervisor.revised_date = timezone.now()
	obj_supervisor.save()

	obj_reviewer.comment = comment
	obj_reviewer.status = 'revise'
	obj_reviewer.save()

		
	e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_reviewer.supervisor.id_request)
	e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nThere is a revision for your supervisor assessment. Please go to your dashboard and modify the assessment based on comment(s): \n{comment}.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = obj_reviewer.user.get_full_name(), comment = comment, expert_email = obj_reviewer.supervisor.expert.researchrole.expert_email_address)
	e_destination = obj_reviewer.user.email
	send_new_email(e_subject,e_content,e_destination)
		
	managers = Role.objects.filter(position='Request manager')
	if position == 'manager':
		Notification(title='Request (ID: {})'.format(obj_reviewer.supervisor.id_request), 
			description='There is a revision for your assessment of the supervisor request. Go to your dashboard to see it.', target=obj_reviewer.user, 
			link=reverse('request:reviewer-supervisor-accept', args=[obj_reviewer.pk])).save()
			
		Notification(title='Request (ID: {})'.format(obj_reviewer.supervisor.id_request), 
			description='The manager has revised the workshop presenter request assessment. Go to your dashboard and see it.'.format(obj_reviewer.user.get_full_name()), target=obj_reviewer.supervisor.expert,
			link=reverse('request:expert-send-request-to-manager', args=[obj_reviewer.supervisor.pk])).save() 

	else:
		Notification(title='Request (ID: {})'.format(obj_reviewer.supervisor.id_request), 
			description='There is a revision for your assessment of the supervisor request. Go to your dashboard to see it.', target=obj_reviewer.user, 
			link=reverse('request:reviewer-supervisor-accept', args=[obj_reviewer.pk])).save()
			
		for i in managers:
			Notification(title='Request (ID: {})'.format(obj_reviewer.supervisor.id_request), 
				description='The expert has revised the assessment of the supervisor request. Go to your dashboard to see it.'.format(obj_reviewer.user.get_full_name()), target=i.user,
				link=reverse('request:reviewer-supervisor-accept', args=[obj_reviewer.supervisor.pk])).save() 
			
		
		
	messages.error(request, 'You revised the supervisor request assessment.')
	if position == 'manager':
		return redirect('request:manager-list')
	else:
		return redirect('request:expert')


def revise_workshop(request):
	comment = request.POST.get('comment')
	position = request.POST.get('position')
	id_request = int(request.POST.get('id_request'))

	obj_workshop = get_object_or_404(WorkshopRequest, pk=id_request)
	print('obj_workshop', obj_workshop)
	obj_reviewer = get_object_or_404(WorkshopReview, workshop=obj_workshop, status="evaluated")

	if position == 'manager':
		obj_workshop.status = 'revised_by_manager'
	else:
		obj_workshop.status = 'revised_by_expert'
	obj_workshop.revised_date = timezone.now()
	obj_workshop.save()
	print("obj_workshop.status", obj_workshop.status)

	obj_reviewer.comment = comment
	obj_reviewer.status = 'revise'
	obj_reviewer.save()


	e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_reviewer.workshop.id_request)
	e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nThere is a revision for your workshop presenter assessment. Please go to your dashboard and modify the assessment based on comment(s): \n{comment}.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = obj_reviewer.user.get_full_name(), comment = comment, expert_email = obj_reviewer.workshop.expert.email)
	e_destination = obj_reviewer.user.email
	send_new_email(e_subject,e_content,e_destination)
	
	messages.error(request, 'You revised the workshop presenter request.')
	if position == 'manager':
		return redirect('request:manager-list')
	else:
		return redirect('request:expert')




def manager_detail_workshop(request, pk):
	obj_workshop = get_object_or_404(WorkshopRequest, pk=pk)

	if request.method == "POST":
		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')
			obj_workshop.status = 'accepted_by_manager'
			obj_workshop.accepted_date = timezone.now()
			obj_workshop.save()

			obj_review = get_object_or_404(WorkshopReview, status='evaluated', workshop=obj_workshop)
			obj_review.status = 'done'
			obj_review.save()
			
			e_subject="TECVICO Request (ID: {})".format(obj_workshop.id_request, )
			e_content = "Dear {}\nHope you are going well.\nCongratulations! Your workshop presenter request has been accepted. For more information, please go your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_workshop.user.get_full_name(),)
			e_destination = obj_workshop.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			
			
			Role.objects.create(user=obj_workshop.user, position='supervisor')
			
			messages.success(request, "You accepted workshop presenter request successfully ")
			return redirect('request:manager-list')


	context = {
		'obj_supervisor' : obj_workshop,
		'obj_reviewer' : get_object_or_404(WorkshopReview, status='evaluated', workshop=obj_workshop)
	}
	return render(request, 'request/manager-detail-workshop.html', context)
	
def manager_supervusor_change_expert(request, pk):
	obj_supervisor = get_object_or_404(SupervisorRequest, pk=pk)
  
	form_change = ChangeExpertManager(request.POST)
	if form_change.is_valid():
		id_expert = int(form_change.cleaned_data.get("id_expert"))
		access_accept_reject = form_change.cleaned_data.get("access_accept_reject")

		obj_supervisor.access_accept_reject = access_accept_reject
		obj_supervisor.save()
		
# 		e_subject = "TECVICO request (ID: {})".format(obj_supervisor.id_request)
# 		e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert. \nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_supervisor.expert.get_full_name(), )
# 		e_destination = obj_supervisor.expert.researchrole.expert_email_address
# 		send_new_email(e_subject,e_content,e_destination)

		
		if id_expert != 0:            
			obj_supervisor.expert.researchrole.count_expert_change_request += 1
			obj_supervisor.expert.researchrole.expert_change_request += str(obj_supervisor.id)
			obj_supervisor.expert.researchrole.expert_change_request += ', '
			obj_supervisor.expert.researchrole.save()
			
			

			# email for last expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_supervisor.id_request),description = "You have been replaced with a new expert.",
										target = obj_supervisor.expert,
										link = reverse('request:expert'))
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_supervisor.id_request)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert \nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_supervisor.user.get_full_name())
			e_destination = obj_supervisor.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
			
			
			new_expert = User.objects.get(id=id_expert)
			obj_supervisor.expert = new_expert
			obj_supervisor.save()
		
			
			
			# email for expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_supervisor.id_request),description = "A supervisor request has been added to your list. Please click on this message to see the badge request.",
										target = new_expert,
										link=reverse('request:select-reviewer-supervisor', args=[obj_supervisor.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_supervisor.id_request)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA supervisor request has been added to your list. Please go to your dashboard and observe it.\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp".format(expert = new_expert.get_full_name())
			e_destination = new_expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
		
			
			# email for applicant
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_supervisor.id_request),description = "The expert on your supervisor request has been changed. For more information, please click on this massage.",
										target = obj_supervisor.user,
										link=reverse('request:supervisor-request-detail', args=[obj_supervisor.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_supervisor.id_request)
			e_content = "Dear {applicant}\nHello\nHope you are going well.\n\nThe expert on your supervisor request has been changed. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {email}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = obj_supervisor.user.get_full_name(), email = obj_supervisor.expert.researchrole.expert_email_address)
			e_destination = obj_supervisor.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			
			
			
			
			
		messages.success(request, "The expert has been changed or given a manager access successfully.")
		return redirect('request:manager-list')
	context = {
		'form_change' : form_change,
		'obj_supervisor' : obj_supervisor,
		'experts' : ResearchRole.objects.filter(expert=True),

	}
	return render(request, 'request/manager-change-expert-supervisor.html', context)



def manager_workshop_change_expert(request, pk):
	obj_workshop = get_object_or_404(WorkshopRequest, pk=pk)

	form_change = ChangeExpertManager(request.POST)
	if form_change.is_valid():
		id_expert = int(form_change.cleaned_data.get("id_expert"))
		access_accept_reject = form_change.cleaned_data.get("access_accept_reject")


		obj_workshop.access_accept_reject = access_accept_reject
		obj_workshop.save()
		
# 		e_subject = "TECVICO request (ID: {})".format(obj_workshop.id_request)
# 		e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert. \nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_workshop.expert.get_full_name(), )
# 		e_destination = obj_workshop.expert.researchrole.expert_email_address
# 		send_new_email(e_subject,e_content,e_destination)
		
		if id_expert != 0:
		    


			# email for last expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_workshop.id_request),description = "You have been replaced with a new expert.",
										target = obj_workshop.expert,
										link = reverse('request:expert'))
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_workshop.id_request)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert \nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_workshop.expert.get_full_name(), )
			e_destination = obj_workshop.expert.email
			send_new_email(e_subject,e_content,e_destination)
			
		    
			new_expert = User.objects.get(id=id_expert)
			obj_workshop.expert = new_expert
			obj_workshop.save()
		
# 			e_subject = "TECVICO request (ID: {})".format(obj_workshop.id_request)
# 			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA workshop presenter request has been added to your list. Please go to your dashboard and observe it.\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp.".format(expert = new_expert.get_full_name())
# 			e_destination = new_expert.researchrole.expert_email_address
# 			send_new_email(e_subject,e_content,e_destination)
		
			
			
			
			# email for expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_workshop.id_request),description = "A workshop presenter request has been added to your list. Please click on this message to see the workshop presenter request.",
										target = new_expert,
										link=reverse('request:expert-workshop-detail', args=[obj_workshop.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_workshop.id_request)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA workshop presenter request has been added to your list. Please go to your dashboard and observe it.\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp".format(expert = new_expert.get_full_name())
			e_destination = new_expert.email
			send_new_email(e_subject,e_content,e_destination)
		
			
			# email for applicant
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = obj_workshop.id_request),description = "The expert on your workshop presenter request has been changed. For more information, please click on this massage.",
										target = obj_workshop.user,
										link=reverse('request:workshop-request-detail', args=[obj_workshop.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = obj_workshop.id_request)
			e_content = "Dear {applicant}\nHello\nHope you are going well.\n\nThe expert on your workshop presenter request has been changed. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {email}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = obj_workshop.user.get_full_name(), email = new_expert.researchrole.expert_email_address)
			e_destination = obj_workshop.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			
			
		messages.success(request, "The expert has been changed or given a manager access successfully.")
		return redirect('request:manager-list')
	context = {
		'form_change' : form_change,
		'obj_workshop' : obj_workshop,
		'experts' : Role.objects.filter(position='workshop expert'),

	}
	return render(request, 'request/manager-change-expert-workshop.html', context)


# badge form
@login_required
def the_badge_request(request):
	managers = Role.objects.filter(position='Request manager')
	if request.method == 'GET':
		user = request.user
		with open('request/skills.txt','r') as f:
			my_list = f.read().splitlines()
			f.close()
			
		context = {
			'user':user,
			'skill_list': my_list,
		}
		return render(request, 'request/badge.html', context)
	elif request.method == 'POST':
		if user_has_memberprofile(request.user):
    			
			if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
				messages.error(request,'Please fillout your profile')
				return HttpResponseRedirect(request.path_info)
			else:
				user_badge_request = BadgeRequest.objects.filter(user = request.user, skills = request.POST.get('skills'))
				if user_badge_request.exists():
					messages.error(request, "You have already requested for this badge.")
					return HttpResponseRedirect(request.path_info)
				form = BadgeForm(request.POST)
				if form.is_valid():
					
		# 			if request.user.memberprofile.balance < 50:
		# 				return redirect('create-checkout-session')
		# 			else:
		# 				final_balance = request.user.memberprofile.balance - 50
		# 				request.user.memberprofile.balance = final_balance
		# 				request.user.memberprofile.save()

					badge = form.save(commit=False)
					if badge.skills == '0':
						badge.skills = request.POST.get('others')
						badge.other = True
					badge.user = request.user

					requests_count = BadgeRequest.objects.filter(created__date=datetime.today()).count()
					if requests_count == 0:

						to_day = str(timezone.now().date())
						to_day = to_day.split('-')
						my_date = ''
						my_date = int(my_date.join(to_day))
						badge.unique_id = "BR{}0001".format(my_date)
					else:
						
						# to_day = str(timezone.now().date())
						today_request = BadgeRequest.objects.filter(created__date=datetime.today())
						list_id = []
						for i in today_request:
							list_id.append(i.id)

						today_request = BadgeRequest.objects.get(id=list_id[0])
						str_new_request_id = today_request.unique_id
						lst_new_request_id = str_new_request_id.split('R')
						int_new_request_id = int(lst_new_request_id[1])
						new_request_id = int_new_request_id + 1
						id_r = "SR{}".format(new_request_id)


						today_request = BadgeRequest.objects.get(id=list_id[0])

						str_new_request_id = today_request.unique_id
						lst_new_request_id = str_new_request_id.split('R')
						int_new_request_id = int(lst_new_request_id[1])
						new_request_id = int_new_request_id + 1
						badge.unique_id = "BR{}".format(new_request_id)
						
					badge.status='Notpay'
					badge.save()


					# select expert
					# experts = Role.objects.filter(position = 'research expert')
					experts = ResearchRole.objects.filter(expert = True)
					expert_list = []
					for expert in experts:
						expert_list.append(expert.user)
					badge_experts = BadgeExpert.objects.all()
					if badge_experts.count() < len(expert_list) - 1:
						next_experts = expert_list[badge_experts.count() + 1]
					else:
						last_expert = list(badge_experts)[-1]
						last_expert_number = expert_list.index(last_expert.user)
						if last_expert_number + 1 == len(expert_list):
							next_experts = expert_list[0]
						else:
							next_experts = expert_list[last_expert_number + 1]
					
					the_expert = BadgeExpert.objects.create(user = next_experts, badge_id = badge.id)
					#return PaymentProtocol(request,'BR',badge,50,'request')
					
					# email & notif for user
					Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "Your badge request has been submitted successfully.",
												target = request.user,
												link=reverse('request:badge-request-detail', args=[badge.pk])).save()
					
					e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge.unique_id)
					e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nYour badge request has been submitted successfully. TECVICO will inform you if you need an interview session.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {email}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = request.user.get_full_name(), email=next_experts.researchrole.expert_email_address)
					e_destination = request.user.email
					send_new_email(e_subject,e_content,e_destination)
					
					# email for expert
					Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "A badge request has been added to your list, please click on this message to see the badge request.",
												target = the_expert.user,
												link=reverse('request:select-interviewer-or-reviewer', args=[badge.pk])).save()
					
					# e_subject = "TECVICO request(ID: {u_id})".format(u_id = badge.unique_id)
					# e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA badge request has been added to your list. Please go to your dashboard and observe it.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.".format(expert = the_expert.user.get_full_name())
					# # e_destination = the_expert.user.email
					# e_destination = the_expert.user.researchrole.expert_email_address
					# send_new_email(e_subject,e_content,e_destination)

					
					
					for i in managers:
						Notification(title='Request (ID: {})'.format(badge.unique_id), 
							description='A badge request has been added to your list and automatically assigned to the expert, namely {}. Click on this message to see more information.'.format(the_expert.user.get_full_name()), target=i.user, 
							link=reverse('request:manager-change-expert', args=[badge.pk])).save()

					messages.success(request, "The badge request has been submitted successfully.")
					return PaymentProtocol(request,'BR',badge,50,'request')
		
    					


	else:
		messages.error(request, form.errors)
		return HttpResponseRedirect(request.path_info)


def reject_badge(request):
	id_badge = request.POST.get('id_badge')
	position = request.POST.get('position')
	decline_reason = request.POST.get('decline_reason')

	managers = Role.objects.filter(position='Request manager')
	obj_badge = BadgeRequest.objects.get(id=id_badge)
	obj_expert = BadgeExpert.objects.get(badge=obj_badge)
	
	if position == 'manager':
		obj_badge.status = 'Reject-badge-manager'
	if position == 'expert':
		obj_badge.status = 'Reject-badge-expert'
	RejectProtocol(request,'BR',obj_badge,50)
	obj_badge.reason_reject = decline_reason
	obj_badge.rejected_date = timezone.now()
	obj_badge.save()
	

	
	if position == 'manager':
		Notification(title='Request (ID: {})'.format(obj_badge.unique_id), 
			description='The manager has rejected the badge request. Go to you dashboard and observe it.', target=obj_expert.user, 
			link=reverse('request:select-interviewer-or-reviewer', args=[obj_badge.pk])).save()
	elif position == 'expert':
		for i in managers:
			Notification(title='Request (ID: {})'.format(obj_badge.unique_id), 
				description='The expert, namely {}, has rejected the badge request. Go to you dashboard and observe it.'.format(obj_expert.user.get_full_name()), target=i.user, 
				link=reverse('request:manager-change-expert', args=[obj_badge.pk])).save()
			
		
	Notification(title='Request (ID: {})'.format(obj_badge.unique_id), 
		description='Your badge request has been rejected. Go to you dashboard and observe it.', target=obj_badge.user, 
		link=reverse('request:badge-request-detail', args=[obj_badge.pk])).save()
		
		
	
	

	e_subject="TECVICO Request (ID: {})".format(obj_badge.unique_id, )
	e_content = "Dear {}\nHope you are going well.\nThank you for the badge request.\nThe company has reviewed your badge request.\nBadge: {}\nSubmitted date: {}\nTECVICO regrets to inform you that your badge request has been rejected. Moreover, the badge request fee has been returned to your account. We welcome you to submit new badge requests in the future.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_badge.user.get_full_name(), obj_badge.skills, obj_badge.created.date())
	e_destination = obj_badge.user.email
	send_new_email(e_subject,e_content,e_destination)
	
	messages.error(request, 'You rejected the badge request.')
	
	if position == 'manager':
		return redirect("request:manager-list")
	if position == 'expert':
		return redirect("request:expert")

# Supervisor form

def supervisor_request(request):
	if request.method == "GET":
		requests = SupervisorRequest.objects.all()
		experts = ResearchRole.objects.filter(expert=True)

		is_requests = SupervisorRequest.objects.filter(user=request.user, 
			status__in=['New', 'Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', ]).count()

		if is_requests == 0:
			is_request = False
		else:
			is_request = True
		if request.user.memberprofile.position == 'Supervisor':
		    is_supervisor = True
		else:
		    is_supervisor = False

		context = {
			"is_request":is_request,
			'is_supervisor': is_supervisor, 
			"user":request.user,
		}

		return render(request, "request/supervisor.html", context)

	elif request.method == "POST":
		if user_has_memberprofile(request.user):
        			
			if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
				messages.error(request,'Please fillout your profile')
				return HttpResponseRedirect(request.path_info)
			else:

				experts = ResearchRole.objects.filter(expert=True)
				id_list = []
				for i in experts:
					id_list.append(i.id)
				expert_obj = ResearchRole.objects.get(id=random.choice(id_list))
				form = SupervisorForm(request.POST, request.FILES)
				if form.is_valid():




					supervisor = form.save(commit=False)

					requests_count = SupervisorRequest.objects.filter(created__date=datetime.today()).count()
					if requests_count == 0:

						to_day = str(timezone.now().date())
						to_day = to_day.split('-')
						my_date = ''
						my_date = int(my_date.join(to_day))
						id_r = "SR{}0001".format(my_date)
					else:
						
						# to_day = str(timezone.now().date())
						today_request = SupervisorRequest.objects.filter(created__date=datetime.today())
						list_id = []
						for i in today_request:
							list_id.append(i.id)

						today_request = SupervisorRequest.objects.get(id=list_id[0])
						str_new_request_id = today_request.id_request
						lst_new_request_id = str_new_request_id.split('R')
						int_new_request_id = int(lst_new_request_id[1])
						new_request_id = int_new_request_id + 1
						id_r = "SR{}".format(new_request_id)

					
					supervisor.id_request = id_r
					supervisor.user = request.user
					supervisor.expert = expert_obj.user
					supervisor.save()
					e_subject="TECVICO Request (ID: {})".format(id_r, )
					e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with us. Your supervisor request has been submitted successfully. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {}.\n\nThank you\nBest regards\nTECVICO Corp'.format(request.user.get_full_name(), supervisor.expert.researchrole.expert_email_address)
					e_destination = request.user.email
					send_new_email(e_subject, e_content, e_destination)
					
					
					e_content = "Dear {}\nHello\nHope you are going well.\nYou are requested to undertake this supervisor request as a expert. You are requested to observe progress of the request and do the assigning tasks on it. You must observe on how well the steps of the request are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert_obj.user.get_full_name(), )
					e_destination = expert_obj.user.researchrole.expert_email_address
					send_new_email(e_subject,e_content,e_destination)
					
					managers = Role.objects.filter(position='Request manager')
					for i in managers:
						e_content = "Dear {} \nHello\nHope you are going well. \nA supervisor request has been submitted recently. To observe it, you can go to your dashboard.\nDo not reply to this Email. This Email has been sent automatically. \n\nThank you \nBest regards \nTECVICO Corp".format(i.user.get_full_name(), )
						e_destination = i.user.email
						send_new_email(e_subject,e_content,e_destination)
						
					messages.success(request, "The supervisor request has been submitted successfully.")
					return PaymentProtocol(request,'SR',supervisor,50,'request')
			
		else:
			messages.error(request, form.errors)
			return HttpResponseRedirect(request.path_info)


# workshop form

def workshop_request(request):
	if request.method == "GET":
		form = WorkshopRequestForm()


		is_requests = WorkshopRequest.objects.filter(user=request.user, 
			status__in=['New', 'Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', ]).count()

		if is_requests == 0:
			is_request = False
		else:
			is_request = True
			
		is_supervisor_w = Role.objects.filter(user=request.user, position='supervisor').count()
		if is_supervisor_w == 0:
			is_supervisor = False
		else:
			is_supervisor = True
		context = {
			'is_request': is_request,
			"user":request.user,
			'is_supervisor': is_supervisor,
			"form":form,
		}
		return render(request, "request/workshop.html", context)

	elif request.method == "POST":
		if user_has_memberprofile(request.user):
        			
			if request.user.memberprofile.check_all == False:  # user has to complete his/her profile to see this page
				messages.error(request,'Please fillout your profile')
				return HttpResponseRedirect(request.path_info)
			else:

				experts = ResearchRole.objects.filter(expert=True)
				id_list = []
				for i in experts:
					id_list.append(i.id)
				expert_obj = ResearchRole.objects.get(id=random.choice(id_list))

				form = WorkshopRequestForm(request.POST, request.FILES)
				if form.is_valid():
					


		# 			if request.user.memberprofile.balance < 50:
		# 				return redirect('create-checkout-session')
		# 			else:
		# 				final_balance = request.user.memberprofile.balance - 50
		# 				request.user.memberprofile.balance = final_balance
		# 				request.user.memberprofile.save()

					# projects = WorkshopRequest.objects.all()
					# count = 0
					# for i in projects:
					# 	created_date = i.created
					# 	created_date = str(created_date)
					# 	created_date = created_date.split(" ")
					# 	created_date = created_date[0]
				
					# 	to_day = date.today()
					# 	to_day = str(to_day)
					# 	to_day = to_day.split(" ")
					# 	to_day = to_day[0]
						
				
					# 	if created_date == to_day:
					# 		count += 1

					# date_ = str(timezone.now().date())
					# new_date = date_.split('-')
					# my_date = ""
					# my_date = int(my_date.join(new_date))
					# my_date = my_date * 10000
					# my_date += (count + 1)
				
					# id_r = "WR{num}".format(num = my_date)
					
					# workshop = form.save(commit=False)
					# workshop.user = request.user
					# workshop.id_request = id_r
					# workshop.expert = expert_obj.user



					requests_count = WorkshopRequest.objects.filter(created__date=datetime.today()).count()
					if requests_count == 0:

						to_day = str(timezone.now().date())
						to_day = to_day.split('-')
						my_date = ''
						my_date = int(my_date.join(to_day))
						id_r = "WR{}0001".format(my_date)
					else:
						
						# to_day = str(timezone.now().date())
						today_request = WorkshopRequest.objects.filter(created__date=datetime.today())
						list_id = []
						for i in today_request:
							list_id.append(i.id)

						today_request = WorkshopRequest.objects.get(id=list_id[0])
						str_new_request_id = today_request.id_request
						lst_new_request_id = str_new_request_id.split('R')
						int_new_request_id = int(lst_new_request_id[1])
						new_request_id = int_new_request_id + 1
						id_r = "WR{}".format(new_request_id)


					workshop = form.save(commit=False)
					workshop.user = request.user
					workshop.id_request = id_r
					workshop.expert = expert_obj.user

					workshop.save()
					e_subject="TECVICO Request (ID: {})".format(id_r, )
					e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in workshop presenter with us. Your workshop presenter request has been submitted successfully. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp'.format(request.user.get_full_name(), workshop.expert.email)
					e_destination = request.user.email
					send_new_email(e_subject, e_content, e_destination)
					
					managers = Role.objects.filter(position='Request manager')
					for i in managers:
						e_subject="TECVICO Request (ID: {})".format(id_r, )
						e_content = 'Dear {}\nHello\nHope you are going well.\nA workshop presenter request has been submitted recently.\nDo not reply to this Email. This Email has been sent automatically. \n\nThank you\nBest regards\nTECVICO Corp'.format(i.user.get_full_name(),)
						e_destination = i.user.email
						send_new_email(e_subject, e_content, e_destination)
						
					
					e_content = "Dear {}\nHello\nHope you are going well.\nYou are requested to undertake this workshop request as a expert. You are requested to observe progress of the request and do the assigning tasks on it. You must observe on how well the steps of the request are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert_obj.user.get_full_name(), )
					e_destination = expert_obj.user.researchrole.expert_email_address
					send_new_email(e_subject,e_content,e_destination)
					
					messages.success(request, "The workshop presenter request has been submitted successfully.")
					return PaymentProtocol(request,'WR',workshop,50,'request')
		else:
			messages.error(request, form.errors)
			return HttpResponseRedirect(request.path_info)



def workshop_update(request, pk):
	workshop = WorkshopRequest.objects.get(pk = pk)
	workshop_form = WorkshopRequestForm(instance=workshop)
	if request.method == "GET":
		context = {
			"user":request.user,
			"form":workshop_form,
		}
		return render(request, "request/workshop.html", context)

	elif request.method == "POST":
		form = WorkshopRequestForm(request.POST, request.FILES, instance=workshop)
		if form.is_valid():
			workshop_form = form.save(commit=False)
			workshop_form.user = request.user
			workshop_form.status = 'New'
			workshop_form.save()
			messages.success(request, "The workshop presenter request has been submitted successfully.")
			return redirect(reverse('request:request'))
		else:
			messages.error(request, form.errors)
			return HttpResponseRedirect(request.path_info)

def badge_request_detail(request, pk):
	badge = BadgeRequest.objects.get(user = request.user, pk = pk)
	the_expert = BadgeExpert.objects.get(badge=badge)
	managers = Role.objects.filter(position='Request manager')

	with open('request/skills.txt','r') as f:
		my_list = f.read().splitlines()
		f.close()

	if request.method == "POST":
		skills = request.POST.get('skills')
		other = request.POST.get('others')

		print("skills", skills)
		print("other", other)

		if skills == '0':
			badge.skills = other
			print('111111111111')
		else:
			badge.skills = skills
			print("222222222222")

		badge.status = "New"
		badge.save()


		# email & notif for user
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "Your badge request has been submitted successfully.",
									target = request.user,
									link = reverse('request:request'))
		
		e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge.unique_id)
		e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nYour badge request has been submitted successfully. TECVICO will inform you if you need an interview session.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {email}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = request.user.get_full_name(), email = the_expert.user.researchrole.expert_email_address)
		e_destination = request.user.email
		send_new_email(e_subject,e_content,e_destination)
		
		# email for expert
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "A badge request has been added to your list, please click on this message to see the badge request.",
									target = the_expert.user,
									link=reverse('request:select-interviewer-or-reviewer', args=[badge.pk])).save()
		
		e_subject = "TECVICO request(ID: {u_id})".format(u_id = badge.unique_id)
		e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA badge request has been added to your list. Please go to your dashboard and observe it.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp.".format(expert = the_expert.user.get_full_name())
		# e_destination = the_expert.user.email
		e_destination = the_expert.user.researchrole.expert_email_address
		send_new_email(e_subject,e_content,e_destination)

		
		
		for i in managers:
			Notification(title='Request (ID: {})'.format(badge.unique_id), 
				description='A badge request has been added to your list and automatically assigned to the expert, namely {}. Click on this message to see more information.'.format(the_expert.user.get_full_name()), target=i.user, 
				link=reverse('request:manager-change-expert', args=[badge.pk])).save()

		messages.success(request, "The badge request has been sent successfully.")
		return redirect(reverse('request:request'))
	obj_session = ''
	if badge.status == 'Interview':
		obj_session = InterviewSession.objects.get(sender__badge=badge)
	context = {
		'badge':badge,
		'obj_expert': BadgeExpert.objects.get(badge=badge),
		'obj_session': obj_session,
		'skill_list': my_list,
	}

	if badge.status == "Interview":
		session_info = InterviewSession.objects.get(sender__badge_id = badge.id)
		context['session_info'] = session_info
	return render(request, 'request/user-badge-request-detail.html', context)


def supervisor_request_detail(request, pk):
	supervisor = SupervisorRequest.objects.get(user = request.user, pk = pk)
	context = {
		'supervisor':supervisor,
	}
	return render(request, 'request/user-supervisor-request-detail.html', context)

def workshop_request_detail(request, pk):
	workshop = WorkshopRequest.objects.get(user = request.user, pk = pk)
	context = {
		'workshop':workshop,
	}
	return render(request, 'request/user-workshop-request-detail.html', context)



@login_required
def expert(request):
	if request.method == 'GET':
		if Role.objects.filter(user = request.user, position__contains = 'workshop expert') or request.user.researchrole.expert == True :
			experts_badge = BadgeExpert.objects.filter(user = request.user)
			badge_form = []
			for item in experts_badge:
				badge_form.append(item.badge)
			supervisor_form = SupervisorRequest.objects.filter(expert=request.user)
			workshop_form = WorkshopRequest.objects.filter(expert=request.user)
			
			
			user_role = []
			roles = Role.objects.filter(user=request.user)
			for role in roles:
				user_role.append(role.position)
			
			

			badge_new_count = BadgeExpert.objects.filter(user=request.user, badge__status='New').count()
			badge_accept_count = BadgeExpert.objects.filter(user=request.user, badge__status__in=['Accept-manager', 'Accept']).count()

			# badge interview, review
			badge_interview_review_count = BadgeExpert.objects.filter(user=request.user, 
				badge__status__in=['Review', 'Approve-decline', 'Interview', 'Expert-view', 'decline-review-interview', 'Reject', 'Set-session', 'revise_by_manager', 'send_manager']).count()
				
			context = {
				'user_role': user_role,
				
				'badge_forms': badge_form,
				'badge_forms_count': badge_new_count + badge_interview_review_count ,

				'badge_new_count': badge_new_count,

				# badge interview, review
				'badge_interview_review_count': badge_interview_review_count,
				
				'badge_interview_review': BadgeExpert.objects.filter(user=request.user, 
					badge__status__in=['Review', 'Approve-decline', 'Interview', 'Expert-view', 'decline-review-interview', 'Reject', 'Set-session', 'revise_by_manager', 'send_manager']),

				'supervisor_form': supervisor_form.order_by('-created'),
				'supervisor_new_count': SupervisorRequest.objects.filter(expert=request.user, status='New').count(),
				'supervisor_review_count': SupervisorRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'revise_by_manager', 'revise_by_expert']).count(),
				'supervisor_count': SupervisorRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'New', 'revise_by_manager', 'revise_by_expert']).count(),


				'workshop_form': workshop_form.order_by('-created'),
				'workshop_new_count': WorkshopRequest.objects.filter(expert=request.user, status='New').count(),
				'workshop_reject_review_count': WorkshopRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'revised_by_manager', 'revised_by_expert']).count(),
				'workshop_count': WorkshopRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'New', 'revised_by_manager', 'revised_by_expert']).count(),

			}
		else:
			messages.error(request, 'You have no access to this page.')
			return HttpResponseRedirect(request.path_info)

		return render(request, 'request/expert-request.html', context)



def select_reviewer_supervisor(request, pk):
	form = SupervisorRequest.objects.get(pk = pk)
	if request.method == 'POST':
		form_review = SelectReviewer(request.POST,  request.FILES,)
		if form_review.is_valid():
			reviewer = form_review.cleaned_data.get("reviewer")
			reviewer = int(reviewer)
			reviewer_user = ResearchRole.objects.get(id=reviewer)
			deadlien_reviewer = timezone.now() + timedelta(2)
			create_reviewer = SupervisorReview.objects.create(user=reviewer_user.user, supervisor=form, deadlien=deadlien_reviewer)
			form.status = "Review"
			form.save()
			
			email_2_day = date.today() + timedelta(2)
			email_7_day = date.today() + timedelta(7)

		
			e_subject = "TECVICO Request (ID: {})".format(form.id_request, )
			e_content = 'Dear {} \nHello\nHope you are going well. \nYou have been requested to evaluate the supervisor. The evaluation form and full information of the request will be available on your dashboard.The reviewer should notify her/his assent to the company to review the request by {}. The system will automatically remove the reviewer if confirmation is not recorded. Furthermore, the deadline of review will be 1 week after the request on {}.\nIf you have any questions or concerns, please feel free to contact the expert through {}\n\nThank you\nSincerely\nTECVICO Corp'.format(reviewer_user.user.get_full_name(), email_2_day, email_7_day, form.expert.researchrole.expert_email_address)
			e_destination = reviewer_user.user.email
			send_new_email(e_subject,e_content,e_destination)
	
			messages.success(request, "The supervisor request has been sent to the reviewer successfully.")
			return redirect(reverse('request:expert'))

	# review_object = SupervisorReview.objects.filter(supervisor=form, supervisor__expert= request.user)
	context = {
		'user':request.user,
		'form' : form,
		'reviewer': ResearchRole.objects.filter(reviewer=True),
		# 'review_object': review_object,
	}
	return render(request, 'request/select-reviewer-supervisor.html', context)
	

@login_required
def select_interviewer_or_reviewer(request, pk):
	form = BadgeRequest.objects.get(pk = pk)
	if request.method == 'GET':
		interviewer = ResearchRole.objects.filter(interviewer = True)
		reviewer = ResearchRole.objects.filter(reviewer = True)
		user_cv_file = request.user.memberprofile.cv_file
		context = {
			'user':request.user,
			'form' : form,
			'interviewer': interviewer,
			'reviewer': reviewer,
			'user_cv_file':user_cv_file,
		}
		# 
		if form.status != 'New' and form.status != 'Reject-badge-manager' and form.status != 'Reject-badge-expert' :
			request_view = BadgeInterviewReview.objects.get(badge = form.id)
			context['request_view'] = request_view
		#
		if form.status == 'Interview':
			session_info = InterviewSession.objects.get(target = form.user.id, sender = request_view.id)
			context['session_info'] = session_info

		return render(request, 'request/select-interviewer-reviewer.html', context)
	elif request.method == 'POST':
		if BadgeInterviewReview.objects.filter(badge_id = form.id).exists():
			BadgeInterviewReview.objects.filter(badge_id = form.id).delete()

		if request.POST.get('reviewer'):
			user_view = int(request.POST.get('reviewer'))
			# status = 'reviewer'
		else:
			user_view = int(request.POST.get('interviewer'))


		# status = int(request.POST.get('status'))
		# if status == 1:
		# 	status = 'reviewer'
		# 	form.position = 'Review'
		# elif status == 2:
		# 	status = 'interviewer'
		# 	form.position = 'Interview'


		status = request.POST.get('status')
		if status == 'review':
			status = 'reviewer'
			form.position = 'Review'

		elif status == 'interview':
			status = 'interviewer'
			form.position = 'Interview'

		form.save()

		badge_request_view = BadgeInterviewReview.objects.create(user_id = user_view, status = status, badge_id = form.id)

		if badge_request_view.status == "interviewer":
			
			# email & notif for interviewer
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "You have been invited to interview this badge requester. The evaluation form and full information of the request is available on your dashboard.",
										target = badge_request_view.user,
										link = reverse('request:review-interview'))
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {interviewer}\n\nHello\nHope you are going well.\nYou have been invited to interview a badge requester. The evaluation form and full information of the the request is available on your dashboard. You must send a time and connection way to interview the requester. The system will automatically remove the interviewer after 2 business days if you do not approved the request.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(interviewer = badge_request_view.user.get_full_name(), email_expert = request.user.researchrole.expert_email_address)
			e_destination = badge_request_view.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request, "The interviewer has been assigned successfully.")

		else:
			# email & notif for reviewer
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "You have been invited to review a badge request. The evaluation form and full information of the the request is available on your dashboard.",
										target = badge_request_view.user,
										link=reverse('request:approve-or-decline', args=[form.pk, 'badge'])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {reviwer}\n\nHello\nHope you are going well.\nYou have been invited to review this badge request. The evaluation form and full information of the the request is available on your dashboard. The system will automatically remove the reviewer after 2 business days if the expert revieve no responce.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviwer = badge_request_view.user.get_full_name(), email_expert = request.user.researchrole.expert_email_address)
			e_destination = badge_request_view.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request, "The reviewer has been assigned successfully.")
			
		form.status = 'Approve-decline'
		form.save()
		return redirect(reverse('request:expert'))


def interview_review_approve_decline(request, pk, form_type):
	if form_type == 'badge':
		form = BadgeRequest.objects.get(pk = pk)
		# reviewer_info = BadgeInterviewReview.objects.get(user = request.user, badge = form.id)
		reviewer_info = BadgeInterviewReview.objects.get(badge = form.id)
	elif form_type == 'supervisor':
		form = SupervisorRequest.objects.get(pk = pk)
		# reviewer_info = SupervisorReview.objects.get(user = request.user, supervisor = form.id)
		reviewer_info = SupervisorReview.objects.get(supervisor = form.id)
	if request.method == 'GET':
		user_cv_file = form.user.memberprofile.cv_file
		context = {
			'form':form,
			'reviewer_info': reviewer_info,
			'user_cv_file':user_cv_file,
		}
		return render(request, 'request/interview-review-approve-decline.html', context)
	elif request.method == 'POST':
		if request.POST.get('btn') == 'Approve':
			reviewer_info.accept_reject = 'approve'
			reviewer_info.save()
			if reviewer_info.status == 'interviewer':
				form.status = 'Set-session'
				form.save()
				InterviewSession.objects.create(sender = reviewer_info, target = form.user)
				
				#  email for expert
				Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The interviewer has approved your request.",
											target = form.badge_expert.get().user,
											link=reverse('request:select-interviewer-or-reviewer', args=[form.pk])).save()
				#  email for expert
				Notification.objects.create(
					title = "Request (ID: {u_id})".format(u_id = form.unique_id),
				description = "TECVICO writes this letter to thank you for approving the interview request, you have one week time to send the evaluation, otherwise you will be given a negative point.",
				target = reviewer_info.user,
				link=reverse('request:interview-session', args=[reviewer_info.pk])).save()
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\nHello\nHope you are going well.\nThe interviewer has approved your badge request.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.researchrole.expert_email_address
				send_new_email(e_subject,e_content,e_destination)
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {reviewer}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for approving the interview request, you have one week time to send the evaluation, otherwise you will be given a negative point.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = form.badge_expert.get().user.get_full_name(), email_expert = form.badge_expert.get().user.researchrole.expert_email_address)
				e_destination = reviewer_info.user.email
				send_new_email(e_subject,e_content,e_destination)

			else:
				form.status = 'Review'
				form.save()
				
				Notification.objects.create(
					title = "Request (ID: {u_id})".format(u_id = form.unique_id),
				description = "TECVICO writes this letter to thank you for approving the review request, you have one week time to send the evaluation, otherwise you will be given a negative point.",
				target = reviewer_info.user,
				link=reverse('request:add-score-to-request', args=[form.pk, 'badge'])).save()
				
				
				#  email for expert
				Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The reviewer has approved your badge request.",
											target = form.badge_expert.get().user,
											link=reverse('request:select-interviewer-or-reviewer', args=[form.pk])).save()
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe reviewer has approved your badge request.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.email
				send_new_email(e_subject,e_content,e_destination)
				
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {reviewer}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for approving the reviewe request, you have one week time to send the evaluation, otherwise you will be given a negative point.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = form.badge_expert.get().user.get_full_name(), email_expert = form.badge_expert.get().user.researchrole.expert_email_address)
				e_destination = reviewer_info.user.email
				send_new_email(e_subject,e_content,e_destination)


			reviewer_info.user.researchrole.count_evaluated_reviewer_request += 1
			reviewer_info.user.researchrole.save()
			
			messages.success(request, 'The badge request has been approved successfully.')
			return redirect('request:review-interview')
		else:
			comment = request.POST.get('decline_reason')
			reviewer_info.comment = comment
			reviewer_info.accept_reject = 'decline'
			reviewer_info.save()
			form.status = 'decline-review-interview'
			form.save()
			
			if reviewer_info.status == 'interviewer':
				#  email for expert
				Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The interviewer has declined your badge request.",
											target = form.badge_expert.get().user,
											link = reverse('request:expert'))
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe interviewer has declined your request. Please go to your dashboard and replace it with a new interviewer.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.email
				send_new_email(e_subject,e_content,e_destination)
			else:
				#  email for expert
				Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The reviewer has declined your request.",
											target = form.badge_expert.get().user,
											link = reverse('request:expert'))
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe reviewer has declined your request. Please go to your dashboard and replace it with a new reviewer.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.email
				send_new_email(e_subject,e_content,e_destination)

			reviewer_info.user.researchrole.count_rejected_reviewer_request += 1
			reviewer_info.user.researchrole.save()
			
			messages.error(request, 'The badge request has been declined.')
			return redirect('request:review-interview')


def workshop_expert_detail(request, pk):
	form = WorkshopRequest.objects.get(pk = pk)
	reviewers = Role.objects.filter(position = 'Reviewer')
	form_review = SelectReviewer(request.POST,  request.FILES,)
	if form_review.is_valid():
		reviewer = int(form_review.cleaned_data.get("reviewer"))
		
		
		reviewer_user = ResearchRole.objects.get(id=reviewer)
		deadlien_reviewer = timezone.now() + timedelta(2)
		create_reviewer = WorkshopReview.objects.create(user=reviewer_user.user, workshop=form, deadlien=deadlien_reviewer)
		form.status = "Review"
		form.save()
		

		email_2_day = date.today() + timedelta(2)
		email_7_day = date.today() + timedelta(2)
	
		e_subject = "TECVICO Request (ID: {})".format(form.id_request, )
		e_content = 'Dear {} \nHello\nHope you are going well. \nYou have been requested to review this workshop request. The evaluation form and full information of the request will be available on your dashboard.The reviewer should notify her/his assent to the company to review the request by {}. The system will automatically remove the reviewer if confirmation is not recorded. Furthermore, the deadline of review will be 1 week after the request on {} of final deadline.\nIf you have any questions or concerns, please feel free to contact the expert through {}\n\nThank you\nSincerely\nTECVICO Corp'.format(reviewer_user.user.get_full_name(), email_2_day, email_7_day, form.expert.researchrole.expert_email_address)
		e_destination = reviewer_user.user.email
		send_new_email(e_subject,e_content,e_destination)
	
	
		messages.success(request, "The workshop presenter request has been sent to the reviewer successfully.")
		return redirect(reverse('request:expert'))
	context = {
		'user':request.user,
		'form' : form,
		'last_reviewers': WorkshopReview.objects.filter(status__in=['reject', 'not_see', 'breach_of_promis'], workshop=form),
		'reviewer': ResearchRole.objects.filter(reviewer=True),
	}
	return render(request, 'request/select-reviewer-workshop.html', context)


def workshop_accept(request, pk):
	workshop_request = WorkshopRequest.objects.get(pk = pk)
	workshop_request.status = 'Accept'
	workshop_request.save()
	messages.success(request, 'You have accepted the request.')
	return redirect(reverse('request:expert'))

def workshop_reject(request, pk):
	workshop_request = WorkshopRequest.objects.get(pk = pk)
	workshop_request.status = 'Reject'
	workshop_request.save()
	messages.success(request, 'You have rejected the request.')
	return redirect(reverse('request:expert'))

# def workshop_delete(request, pk):
# 	workshop_request = WorkshopRequest.objects.get(pk = pk)
# 	workshop_request.delete()
# 	messages.success(request, 'The request has been deleted successfully.')
# 	return redirect(reverse('request:request'))

@login_required
def review_interview_page(request):
	if request.method == 'GET':
		badges = BadgeInterviewReview.objects.filter(user = request.user)
		badges_count = BadgeInterviewReview.objects.filter(
		    user = request.user, 
		    status__in=['new', 'approve'],
		    badge__status__in=['New', 'Review', 'Set-session', 'Approve-decline', 'Interview', 'Expert-view', 'send_manager', 'decline-review-interview', 'Reject', 'revise_by_manager', 
		    ]).count

		badges_review_count_1 = BadgeInterviewReview.objects.filter(status='reviewer', badge__status__in=['Reject', 'revise_by_manager', 'Expert-view', 'send_manager', 'Review'], user=request.user).count()
		badges_review_count_2 = BadgeInterviewReview.objects.filter(status='reviewer', accept_reject='new', user=request.user).count()
		badges_review_count_3 = BadgeInterviewReview.objects.filter(status='reviewer', badge__status__in=['decline-review-interview', ], user=request.user).count()

		badges_interview_count_1 = BadgeInterviewReview.objects.filter(status='interviewer', badge__status__in=['Reject', 'revise_by_manager', 'Expert-view', 'send_manager', 'Set-session', 'Interview'], user=request.user).count()
		badges_interview_count_2 = BadgeInterviewReview.objects.filter(status='interviewer', accept_reject='new', user=request.user).count()
		badges_interview_count_3 = BadgeInterviewReview.objects.filter(status='interviewer', badge__status__in=['decline-review-interview', ], user=request.user).count()
		
		badges_declined_count = BadgeInterviewReview.objects.filter(accept_reject='decline', user=request.user).count()
		
		badges_interview_review_count_4 = BadgeInterviewReview.objects.filter(status__in=['interviewer', 'reviewer'], badge__status__in=['Accept-manager', 'Accept', 'Reject-badge-manager', 'Reject-badge-expert'], user=request.user).count()

		context = {
			'badges' : badges,
			'badges_count' : badges_review_count_1 + badges_review_count_2 + badges_interview_count_1 + badges_interview_count_2 + badges_review_count_3 + badges_interview_count_3,

			# Interview count
			'badges_interview_new_count' : BadgeInterviewReview.objects.filter(status='interviewer', accept_reject='new', user=request.user).count(),
			'badges_interview_set_session_count' : BadgeInterviewReview.objects.filter(status='interviewer', badge__status='Set-session', user=request.user).count(),
			'badges_interview_evaluation_count' : BadgeInterviewReview.objects.filter(status='interviewer', badge__status='Interview', user=request.user).count(),
			'badges_interview_evaluated_count' : BadgeInterviewReview.objects.filter(status='interviewer', badge__status__in=['Expert-view', 'send_manager'], user=request.user).count(),
			'badges_interview_revise_count' : BadgeInterviewReview.objects.filter(status='interviewer', badge__status__in=['Reject', 'revise_by_manager'], user=request.user).count(),
			'badges_interview_count' : badges_interview_count_1 + badges_interview_count_2,
			
			# Reviewer count
			'badges_review_new_count' : BadgeInterviewReview.objects.filter(status='reviewer', accept_reject='new', user=request.user).count(),
			'badges_review_evaluation_count' : BadgeInterviewReview.objects.filter(status='reviewer', badge__status='Review', user=request.user).count(),
			'badges_review_evaluated_count' : BadgeInterviewReview.objects.filter(status='reviewer', badge__status__in=['Expert-view', 'send_manager'], user=request.user).count(),
			'badges_review_revise_count' : BadgeInterviewReview.objects.filter(status='reviewer', badge__status__in=['Reject', 'revise_by_manager'], user=request.user).count(),
			'badges_review_count' : badges_review_count_1 + badges_review_count_2,



			'supervisors' : SupervisorReview.objects.filter(user = request.user, status__in=['new', 'accept', 'reject', 'evaluated', 'done', 'revise']),
			'supervisors_count' : SupervisorReview.objects.filter(user=request.user, status__in=['new', 'accept', 'evaluated', 'revise']).count(),
			'supervisors_accept_count' : SupervisorReview.objects.filter(user=request.user, status__in=['accept', 'evaluated', ]).count(),
			'supervisors_revised_count' : SupervisorReview.objects.filter(user=request.user, status__in=['revise']).count(),
			'supervisors_new_count' : SupervisorReview.objects.filter(user=request.user, status='new').count(),
			'supervisors_evaluated_count' : SupervisorReview.objects.filter(user=request.user, status='evaluated').count(),

			'workshops' : WorkshopReview.objects.filter(user = request.user, status__in=['new', 'accept', 'done', 'reject', 'evaluated', 'revise']),
			'workshops_count' : WorkshopReview.objects.filter(user=request.user, status__in=['new', 'accept', 'evaluated', 'revise']).count(),
			'workshops_accept_count' : WorkshopReview.objects.filter(user=request.user, status__in=['accept', 'evaluated']).count(),
			'workshops_revised_count' : WorkshopReview.objects.filter(user=request.user, status__in=['revise']).count(),
			'workshops_new_count' : WorkshopReview.objects.filter(user=request.user, status='new').count(),
			'workshops_evaluated_count' : WorkshopReview.objects.filter(user=request.user, status='evaluated').count(),

		}
		return render(request, 'request/reviewer-page.html', context)


@login_required
def add_score_to_request(request, pk, form_type):
	if form_type == 'badge':
		form = BadgeRequest.objects.get(pk = pk)
		reviewer_info = BadgeInterviewReview.objects.get(user = request.user, badge = form.id)
	elif form_type == 'supervisor':
		form = SupervisorRequest.objects.get(pk = pk)
		reviewer_info = SupervisorReview.objects.get(user = request.user, supervisor = form.id)
	if request.method == 'GET':
		context = {
			'form':form,
			'expert_obj':BadgeExpert.objects.get(badge=form),
			'session_obj':InterviewSession.objects.filter(sender=reviewer_info),
			'reviewer_info': reviewer_info,
		}
		return render(request, 'request/interviewer-reviewer-score.html', context)
	elif request.method == "POST":
		if reviewer_info.score_file == "":
			messages.error(request, 'You must first evaluate the application!')
			return redirect(request.path_info)
		reviewer_info.comment = request.POST.get('comment')
		reviewer_info.save()
		form.status = "Expert-view"
		
		# for badge
		if form_type == 'badge':
			# email for expert
			# if interview
			if reviewer_info.status == 'interviewer':
				#  email for expert
				Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The interviewer has determined badge requester’s score.",
											target = form.badge_expert.get().user,
											link=reverse('request:select-interviewer-or-reviewer', args=[form.id])).save()
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\n\nHello\nHope you are goirviewer has determined badge requester’s score. Please go to your dashboard and see it.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.email
				send_new_email(e_subject,e_content,e_destination)
			
			# if review#
			else:
				# email for expert
				Notification.objects.create(
					title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The reviewer, namely {}, has determined badge requester’s score.".format(reviewer_info.user.get_full_name()),
					target = form.badge_expert.get().user,
					link=reverse('request:select-interviewer-or-reviewer', args=[form.id])).save()
				
				e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
				e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe reviewer has determined badge requester’s score. Please go to your dashboard and see it.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = form.badge_expert.get().user.get_full_name())
				e_destination = form.badge_expert.get().user.researchrole.expert_email_address
				send_new_email(e_subject,e_content,e_destination)
	
			
			# email for interviewer or reviewer
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "Thank you for your effort. Your assessment has been submitted successfully.",
										target = reviewer_info.user,
										link=reverse('request:add-score-to-request', args=[form.pk, 'badge'])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nThank you for your effort. Your assessment has been submitted successfully.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = reviewer_info.user.get_full_name(), email_expert = form.badge_expert.get().user.researchrole.expert_email_address)
			e_destination = reviewer_info.user.email
			send_new_email(e_subject,e_content,e_destination)
		
		
		form.save()
		messages.success(request, "The badge request has been assessed successfully.")
		return redirect(reverse('request:review-interview'))

def reviewer_supervisor_a_or_r(request, pk):
	obj_review = get_object_or_404(SupervisorReview, pk=pk)

	if request.method == "POST":
		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')

			obj_review.status = 'accept'
			obj_review.supervisor.status = 'reviewer_accept'
			obj_review.supervisor.save()
			obj_review.save()

			obj_review.user.researchrole.count_evaluated_reviewer_request += 1
			obj_review.user.researchrole.save()
			
			
			e_subject = "TECVICO Request (ID: {})".format(obj_review.supervisor.id_request, )
			e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe reviewer has approved your supervisor request.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_review.supervisor.expert.get_full_name())
			e_destination = obj_review.supervisor.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
		

			e_subject = "TECVICO request (ID: {})".format(obj_review.supervisor.id_request,)
			e_content = "Dear {reviewer}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for approving the supervisor request review, you have one week time to send the evaluation, otherwise you will be given a negative point.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = obj_review.user.get_full_name(), email_expert = obj_review.supervisor.expert.researchrole.expert_email_address)
			e_destination = obj_review.user.email
			send_new_email(e_subject,e_content,e_destination)
		
		
			messages.success(request, "The supervisor request has been approved successfully.")
			return redirect('request:review-interview')


		form_decline = DeclineReviewerForm(request.POST)
		if form_decline.is_valid():
			decline = form_decline.cleaned_data.get('decline')
			reject_reason = form_decline.cleaned_data.get('reject_reason')

			obj_review.status = 'reject'
			obj_review.comment = reject_reason
			obj_review.supervisor.status = 'reviewer_reject'
			obj_review.save()
			obj_review.supervisor.save()
# 			obj_review.user.researchrole.count_rejected_reviewer_request += 1
# 			obj_review.user.researchrole.count_rejected_reviewer_request.save()

			e_subject = "TECVICO Request (ID: {})".format(obj_review.supervisor.id_request, )
			e_content = 'Dear {} \nHello\nHope you are going well.\n The reviewer, namely {}, has declined to review the supervisor request. \nPlease go to yopur dashboard and replace this reviewer with another one. \nDo not reply to this Email.\nThank you \nBest regards\n TECVICO Corp.'.format(obj_review.supervisor.expert.get_full_name(), obj_review.user.get_full_name())
			e_destination = obj_review.supervisor.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)

			messages.error(request, "You declined to review the supervisor request.")
			return redirect('request:review-interview')

	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-supervisor-approve-decline.html', context)
	


def reviewer_workshop_a_or_r(request, pk):
	obj_review = get_object_or_404(WorkshopReview, pk=pk)

	if request.method == "POST":
		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')

			obj_review.status = 'accept'
			obj_review.save()
			obj_review.workshop.status = 'reviewer_accept'
			obj_review.workshop.save()


			e_subject = "TECVICO Request (ID: {})".format(obj_review.workshop.id_request, )
			e_content = "Dear {expert}\n\nHello\nHope you are going well.\nThe reviewer has approved your workshop presenter request.\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = obj_review.workshop.expert.get_full_name())
			e_destination = obj_review.workshop.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
			
			
			e_subject = "TECVICO request (ID: {})".format(obj_review.workshop.id_request,)
			e_content = "Dear {reviewer}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for approving the workshop presenter request review, you have one week time to send the evaluation, otherwise you will be given a negative point.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = obj_review.user.get_full_name(), email_expert = obj_review.workshop.expert.researchrole.expert_email_address)
			e_destination = obj_review.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request, "The workshop request has been approved successfully.")
			return redirect('request:review-interview')


		form_decline = DeclineReviewerForm(request.POST)
		if form_decline.is_valid():
			decline = form_decline.cleaned_data.get('decline')
			reject_reason = form_decline.cleaned_data.get('reject_reason')

			obj_review.status = 'reject'
			obj_review.comment = reject_reason
			obj_review.workshop.status = 'reviewer_reject'
			obj_review.save()
			obj_review.workshop.save()

			e_subject = "TECVICO Request (ID: {})".format(obj_review.workshop.id_request, )
			e_content = 'Dear {} \nHello\nHope you are going well.\n The reviewer, namely {}, has declined to review the workshop presenter request. \nPlease go to yopur dashboard and replace this reviewer with another one. \nDo not reply to this Email.\nThank you \nBest regards\n TECVICO Corp.'.format(obj_review.workshop.expert.get_full_name(), obj_review.user.get_full_name())
			e_destination = obj_review.workshop.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)

			messages.error(request, "You declined to review the workshop presenter request.")
			return redirect('request:review-interview')

	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-workshop-approve-decline.html', context)


def reviewer_supervisor_accept(request, pk):
	obj_review = get_object_or_404(SupervisorReview, pk=pk)

	if request.method == 'POST':
		form_send = ReviewerSendForExpertForm(request.POST)
		if form_send.is_valid():
			comment = form_send.cleaned_data.get("comment")

			obj_review.status = 'evaluated'
			obj_review.comment = comment
			obj_review.supervisor.status = 'reviewer_evaluated'
			obj_review.supervisor.save()
			obj_review.save()

			
			e_subject = "TECVICO Request (ID: {})".format(obj_review.supervisor.id_request, )
			e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO is writing this letter to thank you for assessing the suprevior request. Your assessment has  been submitted successfully.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}\nThank you\n\nBest regards\nTECVICO Corp.'.format(request.user.get_full_name(), obj_review.supervisor.expert.researchrole.expert_email_address)
			e_destination = request.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			
			e_subject = "TECVICO Request (ID: {})".format(obj_review.supervisor.id_request, )
			e_content = "Dear {}\nHello\nHope you are going well.\nA reviewer, namely {}, sent the assessment of supervisor request. Please go to your dashboard and observe it.\nDo not reply to this Email.\n\nThank you\nBest regards\nTECVICO Corp.".format(obj_review.supervisor.expert.get_full_name(), request.user.get_full_name())
			e_destination = obj_review.supervisor.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request,'Your assessment has been sent successfully.')
			return redirect("request:review-interview")

	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-supervisor-accept.html', context)
	

def reviewer_workshop_accept(request, pk):
	obj_review = get_object_or_404(WorkshopReview, pk=pk)

	if request.method == 'POST':
		form_send = ReviewerSendForExpertForm(request.POST)
		if form_send.is_valid():
			comment = form_send.cleaned_data.get("comment")

			obj_review.status = 'evaluated'
			obj_review.comment = comment
			obj_review.workshop.status = 'reviewer_evaluated'
			obj_review.workshop.save()
			obj_review.save()

			
			e_subject = "TECVICO Request (ID: {})".format(obj_review.workshop.id_request, )
			e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO is writing this letter to thank you for assessing this workshop presenter request. Your assessment has been submitted successfully.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}\nThank you\nBest regards\nTECVICO Corp.'.format(request.user.get_full_name(), obj_review.workshop.expert.researchrole.expert_email_address)
			e_destination = request.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			
			e_subject = "TECVICO Request (ID: {})".format(obj_review.workshop.id_request, )
			e_content = "Dear {}\nHello\nHope you are going well.\nA reviewer, namely {}, sent the assessment of workshop presenter request. Please go to your dashboard and observe it.\nDo not reply to this Email.\n\nThank you\nBest regards\nTECVICO Corp.".format(obj_review.workshop.expert.get_full_name(), request.user.get_full_name())
			e_destination = obj_review.workshop.expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request,'The workshop presenter request assessment has been done successfully.')
			return redirect("request:review-interview")

	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-workshop-accept.html', context)
	

def expert_send_request_to_manager(request, pk):
	obj_expert = get_object_or_404(SupervisorRequest, pk=pk)
	obj_review = get_object_or_404(SupervisorReview, supervisor=obj_expert, status='evaluated')
	managers = Role.objects.filter(position='Request manager')

	if request.method == 'POST':
		form_send = ReviewerSendForExpertForm(request.POST)
		if form_send.is_valid():
			comment = form_send.cleaned_data.get("comment")

			obj_expert.comment = comment
			obj_expert.accepted_date = timezone.now()
			obj_expert.status = 'send_to_manager'
			obj_expert.save()
			
# 			for i in managers:
# 				e_subject = "TECVICO Request (ID: {})".format(obj_expert.id_request, )
# 				e_content = "Dear {}\nHello\nHope you are going well.\nThe expert {} has investigated the martial of the request for the supervisor.\nFor more information, please go to your dashboard and look at the comment(s) and finalize the request.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {}.\n\nThank you\nBest regards\nTECVICO Corp."format(i.user.get_full_name(), obj_expert.expert.get_full_name, obj_expert.expert.researchrole.expert_email_address)
# 				e_destination = i.user.email
# 				send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request,'The supervisor request assessment has been sent to the manager successfully.')
			return redirect('request:expert')

		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')
			obj_expert.status = 'accepted_by_expert'
			obj_expert.accepted_date = timezone.now()
			obj_expert.user.memberprofile.position = 'Supervisor' 
			obj_expert.save()
			obj_expert.user.memberprofile.save()
			
			obj_review.status = 'done'
			obj_review.save()
			

			e_subject="TECVICO Request (ID: {})".format(obj_expert.id_request, )
			e_content = "Dear {}\nHope you are going well.\nCongratulations! Your supervisor request has been accepted. For more information, please go your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_expert.user.get_full_name(),)
			e_destination = obj_expert.user.email
			send_new_email(e_subject,e_content,e_destination)

			
			messages.success(request, "You accepted supervisor request successfully ")
			return redirect('request:expert')

	context = {
		'obj_expert': obj_expert
	}
	return render(request, 'request/expert-send-request-to-manager.html', context)

	

def expert_send_request_workshop_to_manager(request, pk):
	obj_expert = get_object_or_404(WorkshopRequest, pk=pk)
	managers = Role.objects.filter(position='Request manager')
	if request.method == 'POST':
		form_send = ReviewerSendForExpertForm(request.POST)
		if form_send.is_valid():
			comment = form_send.cleaned_data.get("comment")

			obj_expert.comment = comment
			obj_expert.status = 'send_to_manager'
			obj_expert.save()
			
# 			for i in managers:
# 			    e_subject = "TECVICO Request (ID: {})".format(obj_expert.id_request, )
# 			    e_content = "Dear {} \nHello\nHope you are going well. \nThe expert {} has investigated the martial of the request for the workshop presenter\nFor more information, please go to your dashboard and look at the comment(s) and finalize the request. \nDo not reply to this Email. \n\nThank you \nBest regards \nTECVICO Corp.".format(i.user.get_full_name(), obj_expert.expert.get_full_name())
# 			    e_destination = i.user.email
# 			    send_new_email(e_subject,e_content,e_destination)
			
			messages.success(request,'The supervisor request has been sent to the manager successfully.')
			return redirect('request:expert')

		form_approve = ApproveReviewerForm(request.POST)
		if form_approve.is_valid():
			approve = form_approve.cleaned_data.get('approve')
			obj_expert.status = 'accepted_by_expert'
			obj_expert.accepted_date = timezone.now()
			obj_expert.save()

			obj_review = get_object_or_404(WorkshopReview, workshop=obj_expert, status='evaluated')

			obj_review.status = 'done'
			obj_review.save()
			
			
			e_subject="TECVICO Request (ID: {})".format(obj_expert.id_request, )
			e_content = "Dear {}\nHope you are going well.\nCongratulations! Your workshop presenter request has been accepted. For more information, please go your dashboard.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you.\nBest regards\nTECVICO Corp".format(obj_expert.user.get_full_name(),)
			e_destination = obj_expert.user.email
			send_new_email(e_subject,e_content,e_destination)

			
			Role.objects.create(user=obj_expert.user, position='supervisor')
			messages.success(request, "You accepted workshop presenter request successfully ")
			return redirect('request:expert')

	context = {
		'obj_expert': obj_expert,
		'obj_reviewer': WorkshopReview.objects.get(status='evaluated', workshop=obj_expert)
	}
	return render(request, 'request/expert-send-request-workshop-to-manager.html', context)


def reviewer_supervisor_evaluate(request, pk):
	obj_review = get_object_or_404(SupervisorReview, pk=pk)

	if request.method == "POST":
		total_score = int(request.POST.get("score_total"))
		my_dict = json.loads(request.POST['Q_S_list'])
		score0 = int(request.POST.get('score0'))
		score1 = int(request.POST.get('score1'))
		score2 = int(request.POST.get('score2'))
		score3 = int(request.POST.get('score3'))
		score4 = int(request.POST.get('score4'))
		score5 = int(request.POST.get('score5'))
		score6 = int(request.POST.get('score6'))
		score7 = int(request.POST.get('score7'))
		score8 = int(request.POST.get('score8'))
		score9 = int(request.POST.get('score9'))

		my_list = []
		for title, score in my_dict:
			my_list.append("{t}, {s},\n".format(t = str(title), s = str(score)))


		with open('/home/tecvicoc/public_html/media/request/supervisor/reviewer_score/supervisor_{}.txt'.
# 		with open('media/request/supervisor/reviewer_score/supervisor_{}.txt'.
			format(obj_review.id),'w') as f:
			f.writelines(my_list)
			f.close()

		obj_review.score_1 = score0
		obj_review.score_2 = score1
		obj_review.score_3 = score2
		obj_review.score_4 = score3
		obj_review.score_5 = score4
		obj_review.score_6 = score5
		obj_review.score_7 = score6
		obj_review.score_8 = score7
		obj_review.score_9 = score8
		obj_review.score_10 = score9




		total_score = total_score / 10
		total_score = int(total_score)

		obj_review.score = total_score
		obj_review.score_file = 'request/supervisor/reviewer_score/supervisor_{}.txt'.format(obj_review.id)
		obj_review.save()
		
		
		messages.success(request, "Your assessment has been done successfully.")

	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-supervisor-valuate.html', context)

def reviewer_workshop_evaluate(request, pk):
	obj_review = get_object_or_404(WorkshopReview, pk=pk)

	if request.method == "POST":
		total_score = int(request.POST.get("score_total"))
		my_dict = json.loads(request.POST['Q_S_list'])
		score0 = int(request.POST.get('score0'))
		score1 = int(request.POST.get('score1'))
		score2 = int(request.POST.get('score2'))
		score3 = int(request.POST.get('score3'))
		score4 = int(request.POST.get('score4'))
		score5 = int(request.POST.get('score5'))
		score6 = int(request.POST.get('score6'))
		score7 = int(request.POST.get('score7'))
		score8 = int(request.POST.get('score8'))
		score9 = int(request.POST.get('score9'))

		my_list = []
		for title, score in my_dict:
			my_list.append("{t}, {s},\n".format(t = str(title), s = str(score)))

		with open('/home/tecvicoc/public_html/media/request/workshop/reviewer_score/workshop_{}.txt'.
# 		with open('media/request/workshop/reviewer_score/workshop_{}.txt'.
			format(obj_review.id),'w') as f:
			f.writelines(my_list)
			f.close()

		# with open('media/request/workshop/reviewer_score/workshop_{}.txt'.
		#     format(obj_review.id),'w') as f:
		#     f.writelines(my_list)
		#     f.close()

		total_score = total_score / 10
		total_score = int(total_score)


		obj_review.score_1 = score0
		obj_review.score_2 = score1
		obj_review.score_3 = score2
		obj_review.score_4 = score3
		obj_review.score_5 = score4
		obj_review.score_6 = score5
		obj_review.score_7 = score6
		obj_review.score_8 = score7
		obj_review.score_9 = score8
		obj_review.score_10 = score9


		obj_review.score = total_score
		obj_review.score_file = 'request/workshop/reviewer_score/workshop_{}.txt'.format(obj_review.id)
		obj_review.save()

		messages.success(request, "Your assessment has been done successfully.")
	context = {
		'obj_review' : obj_review
	}
	return render(request, 'request/reviewer-workshop-valuate.html', context)


def add_score_detail(request, pk, form_type="badge"):
	if request.method == 'GET':
		if form_type == "badge":
			form = BadgeInterviewReview.objects.get(pk = pk)
		elif form_type == "supervisor":
			form = SupervisorReview.objects.get(pk = pk)
		
		context = {
			'form' : form,
			'form_type': form_type,
		}
		return render(request, 'request/reviewer-score-badge.html',context)
	elif request.method == "POST":
		my_dict = json.loads(request.POST['Q_S_list'])
		sum_of_score = request.POST.get('score_total')
		score0 = int(request.POST.get('score0'))
		score1 = int(request.POST.get('score1'))
		score2 = int(request.POST.get('score2'))
		score3 = int(request.POST.get('score3'))
		score4 = int(request.POST.get('score4'))
		score5 = int(request.POST.get('score5'))
		score6 = int(request.POST.get('score6'))
		score7 = int(request.POST.get('score7'))
		score8 = int(request.POST.get('score8'))
		score9 = int(request.POST.get('score9'))


		if form_type == "badge":
			form = BadgeInterviewReview.objects.get(pk = pk)
			the_name = '_score_badge'
		elif form_type == "supervisor":
			form = SupervisorReview.objects.get(pk = pk)
			the_name = '_score_supervisor'
			
		my_list = []
		for title, score in my_dict:
			my_list.append("{t}, {s},\n".format(t = str(title), s = str(score)))
			
		#return HttpResponse(my_list[4])
		with open('/home/tecvicoc/public_html/media/request/badge_file/{name}.txt'.format(name = str(form.id) + the_name),'w') as f:
# 		with open('media/request/badge_file/{name}.txt'.format(name = str(form.id) + the_name),'w') as f:
			f.writelines(my_list)
			f.close()
		score_file = 'request/badge_file/{name}.txt'.format(name = str(form.id) + the_name)
		#return HttpResponse(score_file)
		
		
		form.score_file = score_file
		the_score = int(sum_of_score) // 10
		form.score = the_score

		form.score_1 = score0
		form.score_2 = score1
		form.score_3 = score2
		form.score_4 = score3
		form.score_5 = score4
		form.score_6 = score5
		form.score_7 = score6
		form.score_8 = score7
		form.score_9 = score8
		form.score_10 = score9


		form.save()
		messages.success(request, "Your submitted has been done successfully.")
		#return redirect(reverse('request:add-score-to-request', kwargs={'pk': form.pk, 'form_type':form_type}))
		return JsonResponse({
				'success': True,
				'score':sum_of_score,
				'url': reverse('request:add-score-to-request', kwargs={'pk': form.badge.pk, 'form_type':form_type}),
		})
		


@login_required
def set_interview_session(request, req_id):
	session = InterviewSession.objects.get(sender_id = req_id)
	request_form = BadgeRequest.objects.get(id = session.sender.badge.id)
	if request.method == 'GET':
		time_zone = pytz.all_timezones
		context = {
			'session':session,
			'time_zone': time_zone,
		}
		return render(request, 'request/interview-session.html', context)
	if request.method == 'POST':
		new_form = SessionForm(request.POST, instance=session)
		if new_form.is_valid():
			new_session = new_form.save()
			request_form.status = "Interview"
			request_form.save()
			
			# email & notif for user
			Notification.objects.create(
			    title = "Request (ID: {u_id})".format(u_id = request_form.unique_id),description = "The interviewer has set a time for interview to determine your badge score. For more information, click on this message.",
				target = request_form.user,
				link=reverse('request:badge-request-detail', args=[request_form.id])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = request_form.unique_id)
			e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nThe interviewer has set a time to determine your badge score. For more information, please go to your ptofile. \nConnection link: {link}\nDate:{date}\nTime:{time}\nTime zone: {time_zone}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {email_expert}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = request_form.user.get_full_name(), link = new_session.meeting_link,date = new_session.start_at.date(), time = new_session.start_at.time(), time_zone = new_session.time_zone, email_expert = request_form.badge_expert.get().user.researchrole.expert_email_address)
			e_destination = request_form.user.email
			send_new_email(e_subject,e_content,e_destination)
			
			# email & notif for expert
# 			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = request_form.unique_id),description = "The interviewer has set a time to determine your badge score. For more information, click on this message.",
# 										target = request_form.badge_expert.get().user,
# 										link = reverse('request:expert'))
			
# 			e_subject = "TECVICO request (ID: {u_id})".format(u_id = request_form.unique_id)
# 			e_content = "Dear {expert}\nHello\nHope you are going well.\nThe interviewer has set a time to determine badge requester’s score. Time and connection way were set as follows.\nConnection link: {link}\nDate:{date}\nTime:{time}\n\nDo not reply to this Email. This Email has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = request_form.badge_expert.get().user.get_full_name(), link = new_session.meeting_link,date = new_session.start_at.date(), time = new_session.start_at.time())
# 			e_destination = request_form.badge_expert.get().user.email
# 			send_new_email(e_subject,e_content,e_destination)


			messages.success(request, "The session has been set successfully.")
			return redirect(reverse('request:review-interview'))
		else:
			messages.error(request, new_form.errors)
			return HttpResponseRedirect(request.path_info)


def accept_request(request, pk, form_type):
	#request_view = InterviewerOrReviewerInfo.objects.get(pk = pk)
	if form_type == 'badge':
		position = request.POST.get("position")
		request_view = BadgeInterviewReview.objects.get(pk = pk)
		badge_request = BadgeRequest.objects.get(id = request_view.badge.id)
		badge_request.score = request_view.score
		if position == "manager":
			badge_request.status = 'Accept-manager'
		else:
			badge_request.status = 'Accept'
		badge_request.accepted_date = timezone.now()
		badge_request.save()
		
		request_view.status = 'done'
		request_view.save()
		
		# email for applicant
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_request.unique_id),description = "Your badge score has been determined. Please go to your dashboard and see it.",
									target = badge_request.user,
									link=reverse('request:badge-request-detail', args=[badge_request.pk])).save()
									
									
		e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge_request.unique_id)
		e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nYour badge score has been determined. Please go to your dashboard and see it.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through researchexpert@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = badge_request.user.get_full_name())
		e_destination = badge_request.user.email
		send_new_email(e_subject,e_content,e_destination)

		
		
		
		if position == "manager":
		    messages.success(request, 'The badge request has been accepted successfully.')
		    return redirect(reverse('request:manager-list'))
		else:
		    messages.success(request, 'The badge request has been accepted successfully.')
		    return redirect(reverse('request:expert'))
	elif form_type == 'supervisor':
		request_view = SupervisorReview.objects.get(pk = pk)
		supervisor_request = SupervisorRequest.objects.get(id = request_view.supervisor.id)
		supervisor_request.score = request_view.score
		supervisor_request.status = 'Accept'
		supervisor_request.save()
		messages.success(request, 'The supervisor request has been accepted.')
		return redirect(reverse('request:expert'))
	else:
		messages.success(request, 'The supervisor request is invalid.')
		return HttpResponseRedirect(request.path_info)


def send_request_badge_to_manager(request, pk):
	if request.method == "POST":
		comment_manager = request.POST.get('comment_manager')
		inp = request.POST.get('slm')
		badge_form = BadgeRequest.objects.get(pk = pk)
		expert_form = BadgeExpert.objects.get(badge = badge_form.id)
		
		badge_form.status = "send_manager"
		badge_form.reason_reject = comment_manager
		badge_form.save()
		# email for interviewer or reviewer
		managers = Role.objects.filter(position='Request manager')
		for i in managers:
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_form.unique_id),
										description = "The expert, namely {}, has sent the badge assessment. Please click on this massage and observe it.".format(expert_form.user.get_full_name()),
										target = i.user,
										link=reverse('request:manager-change-expert', args=[badge_form.pk])).save()
		
		
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge_form.unique_id)
			e_content = "Dear {}\nHello\nHope you are going well.\n\nThe expert, namely {}, sent the badge assessment, please go to your dashboard and observe it.\nDo not reply to this Email. This massage has been sent automatically.\n\nThank you\nBest regards\nTECVICO Corp.".format(i.user.get_full_name(), expert_form.user.get_full_name())
			e_destination = i.user.email
			send_new_email(e_subject,e_content,e_destination)
		
		# e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge_form.unique_id)
		# e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nThere is a revision for you assessment of the badge. Please go to your dashboard and modify the assessment based on comment(s): \n{comment}.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = request.user.get_full_name(), comment = expert_form.comment, expert_email = request.user.email)
		# e_destination = badge_form.badge_request.get().user.email
		# send_new_email(e_subject,e_content,e_destination)

		# Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_form.unique_id),description = "There is a revision for you assessment of the badge. Please go to your dashboard and see it.",
		#                             target = badge_form.badge_request.get().user,
		#                             link = reverse('request:request'))
		
		# messages.success(request, 'The revision has been sent successfully.')
		messages.success(request, 'The badge request assessment has been sent to the manager successfully.')
		return redirect(reverse('request:expert'))




def badge_revise_request(request, pk):
	if request.method == "POST":
		comment = request.POST.get('decline_reason')
		position = request.POST.get('position')
		badge_form = BadgeRequest.objects.get(pk = pk)
		expert_form = BadgeExpert.objects.get(badge = badge_form.id)
		interview_review_form = BadgeInterviewReview.objects.get(badge = badge_form.id)
		# expert_form.comment = comment
		# expert_form.save()
		interview_review_form.comment = comment
		interview_review_form.save()
		
		if position == "manager":
		    badge_form.status = "revise_by_manager"
		else:
		    badge_form.status = "Reject"

		badge_form.revised_date = timezone.now()
		badge_form.save()
		
		# email for interviewer or reviewer
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_form.unique_id),description = "There is a revision for your badge assessment. Please go to your dashboard and see it.",
									target = badge_form.badge_request.get().user,
									link=reverse('request:add-score-to-request', args=[badge_form.pk, 'badge'])).save()
									
# 		if position == "expert":
# 			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_form.unique_id),description = "The expert has revised this assessment. ",
# 										target = expert_form.user,
# 										link = reverse('notification-page'))
# 		if position == "manager":
# 		    managers = Role.objects.filter(position='Request manager')
# 		    for i in managers:
#     			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge_form.unique_id),description = "The manager has revised this assessment. ",
#     										target = i.user,
#     										link = reverse('notification-page'))
    		
		e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge_form.unique_id)
		e_content = "Dear {reviewer}\n\nHello\nHope you are going well.\nThere is a revision for your badge assessment. Please go to your dashboard and modify the assessment based on comment(s): \n{comment}.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the expert through {expert_email}.\n\nThank you\nBest regards\nTECVICO Corp".format(reviewer = request.user.get_full_name(), comment = comment, expert_email = request.user.email)
		e_destination = badge_form.badge_request.get().user.email
		send_new_email(e_subject,e_content,e_destination)
		
		messages.success(request, 'The revision has been sent successfully.')
		if position == "manager":
			return redirect(reverse('request:manager-list'))
		else:
			return redirect(reverse('request:expert'))



def manager_change_expert(request, pk):
	form = BadgeRequest.objects.get(pk = pk)
	if request.method == 'GET':
		experts = Role.objects.filter(position = 'research expert')

		id_form = form.id
		review_obj = None
		id_review = []
		review_all = BadgeInterviewReview.objects.all()
		for i in review_all:
			id_review.append(i.badge.id)
		if id_form in id_review:
			review_obj = BadgeInterviewReview.objects.get(badge=form)

		context = {
			"form": form,
			"expert_obj": BadgeExpert.objects.get(badge=form),
			"review_obj": review_obj,
			"experts": ResearchRole.objects.filter(expert=True),
		}
		return render(request, 'request/manager-change-expert-badge.html', context)
	elif request.method == 'POST':
		access_expert = request.POST.get('access_expert')
		new_expert = request.POST.get('experts')
		comment = request.POST.get('last_exp_comemnt')
		
		if access_expert == None:
			form.access_accept_reject = False
		if access_expert == 'on':
			form.access_accept_reject = True
		form.save()
		
		# if new_expert == '0' :
		#     messages.error(request, 'You should select an expert!!')
		#     return redirect(request.path_info)

		if new_expert != '0':
			current_expert = BadgeExpert.objects.get(badge = form.id)
			last_expert = current_expert.user
			current_expert.user = User.objects.get(id = int(new_expert))
			current_expert.save()

			last_expert.researchrole.count_expert_change_request += 1
			last_expert.researchrole.expert_change_request += str(form.id)
			last_expert.researchrole.expert_change_request += ', '
			last_expert.researchrole.save()


			# email for last expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "You have been replaced with a new expert.",
										target = last_expert,
										link = reverse('request:expert'))
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert because: {comment}\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = last_expert.get_full_name(), comment = comment)
			e_destination = last_expert.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
			
			
			# email for expert
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "A badge request has been added to your list. Please click on this message to see the badge request.",
										target = current_expert.user,
										link=reverse('request:select-interviewer-or-reviewer', args=[form.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA badge request has been added to your list. Please go to your dashboard and observe it.\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp".format(expert = current_expert.user.get_full_name())
			e_destination = current_expert.user.researchrole.expert_email_address
			send_new_email(e_subject,e_content,e_destination)
		
			
			# email for applicant
			Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "The expert on your badge request has been changed. For more information, please click on this massage.",
										target = form.user,
										link=reverse('request:badge-request-detail', args=[form.pk])).save()
			
			e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
			e_content = "Dear {applicant}\nHello\nHope you are going well.\n\nThe expert on your badge request has been changed. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {email}.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = form.user.get_full_name(), email = current_expert.user.researchrole.expert_email_address)
			e_destination = form.user.email
			send_new_email(e_subject,e_content,e_destination)
		
		
		messages.success(request, 'The expert has been changed or given a manager access successfully.')
		return redirect(reverse('request:manager-list'))
		
		
		

# def manager_change_expert(request, pk):
#     form = BadgeRequest.objects.get(pk = pk)
#     if request.method == 'GET':
#         experts = Role.objects.filter(position = 'research expert')
#         context = {
#             "form": form,
#             "expert_obj": BadgeExpert.objects.get(badge=form),
#             "experts": ResearchRole.objects.filter(expert=True),
#         }
#         return render(request, 'request/manager_change_expert.html', context)
#     elif request.method == 'POST':
#         new_expert = request.POST.get('experts')
#         comment = request.POST.get('last_exp_comemnt')
#         if new_expert == 0 :
#             messages.error(request, 'You should select an expert!!')
#             return redirect(request.path_info)
#         current_expert = BadgeExpert.objects.get(badge = form.id)
#         last_expert = current_expert.user
#         current_expert.user = User.objects.get(id = int(new_expert))
#         current_expert.save()
		
#         # email for last expert
#         Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "You have been replaced with a new expert.",
#                                     target = last_expert,
#                                     link = reverse('request:expert'))
		
#         e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
#         e_content = "Dear {expert}\nHello\nHope you are going well.\n\nYou have been replaced with a new expert because: {comment}\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(expert = last_expert.get_full_name(), comment = comment)
#         e_destination = last_expert.researchrole.expert_email_address
#         send_new_email(e_subject,e_content,e_destination)
		
		
#         # email for expert
#         Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = form.unique_id),description = "A badge request has been added to your list. Please click on this message to see the badge request.",
#                                     target = current_expert.user,
#                                     link = reverse('request:expert'))
		
#         e_subject = "TECVICO request (ID: {u_id})".format(u_id = form.unique_id)
#         e_content = "Dear {expert}\nHello\nHope you are going well.\n\nA badge request has been added to your list. Please go to your dashboard and review it.\nIf you have any questions or concerns, please feel free to contact the manager through requestmanager@tecvico.com. \n\nThank you\nBest regards\nTECVICO Corp".format(expert = current_expert.user.get_full_name())
#         e_destination = current_expert.user.researchrole.expert_email_address
#         send_new_email(e_subject,e_content,e_destination)
		
		
#         messages.success(request, 'The expert has been replaced successfully.')
#         return redirect(reverse('request:manager-list'))  
		
		
def sendemailnotifbadgerequest(user,pk,is_pay):
	managers = Role.objects.filter(position='Request manager')
	badge = BadgeRequest.objects.get(pk=pk)

	the_expert = BadgeExpert.objects.get(badge =badge)
	if is_pay:	
		badge.status="New"
		badge.save()
		# email & notif for user
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "Your badge request has been submitted successfully.",
									target = user,
									link=reverse('request:badge-request-detail', args=[badge.pk])).save()
		
		e_subject = "TECVICO request (ID: {u_id})".format(u_id = badge.unique_id)
		e_content = "Dear {applicant}\n\nHello\nHope you are going well.\nYour badge request has been submitted successfully. TECVICO will inform you if you need an interview.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp".format(applicant = user.get_full_name())
		e_destination = user.email
		send_new_email(e_subject,e_content,e_destination)
		
		# email for expert
		Notification.objects.create(title = "Request (ID: {u_id})".format(u_id = badge.unique_id),description = "A badge request has been added to your list, please click on this message to see the badge request.",
									target = the_expert.user,
									link=reverse('request:select-interviewer-or-reviewer', args=[badge.pk])).save()
	
		for i in managers:
			Notification(title='Request (ID: {})'.format(badge.unique_id), 
				description='A badge request has been added to your list and automatically assigned to the expert, namely {}. Click on this message to see more information.'.format(the_expert.user.get_full_name()), target=i.user, 
				link=reverse('request:manager-change-expert', args=[badge.pk])).save()

def sendemailnotifsupervisorrequest(user,pk,is_pay):
	supervisor=SupervisorRequest.objects.get(id=pk)
	expert_obj =ResearchRole.objects.get(user=supervisor.expert)
	if is_pay:
		supervisor.status='New'
		supervisor.save()
		e_subject="TECVICO Request (ID: {})".format(supervisor.id_request, )
		e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with us. Your request has been submitted successfully. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {}.\n\nThank you\nBest regards\nTECVICO Corp'.format(user.get_full_name(), supervisor.expert.researchrole.expert_email_address)
		e_destination = user.email
		send_new_email(e_subject, e_content, e_destination)
		
		
		e_content = "Dear {}\nHello\nHope you are going well.\nYou are requested to undertake this supervisor request as a expert. You are requested to observe progress of the request and do the assigning tasks on it. You must observe on how well the steps of the request are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the manager.\n\nThank you\nBest regards\nTECVICO Corp".format(expert_obj.user.get_full_name(), )
		e_destination = expert_obj.user.researchrole.expert_email_address
		send_new_email(e_subject,e_content,e_destination)
		
		managers = Role.objects.filter(position='Request manager')
		for i in managers:
			e_content = "Dear {} \nHello\nHope you are going well. \nA new request has been submitted recently. To observe it, you can go to your dashboard.\nDo not reply to this Email. This Email has been sent automatically. \n\nThank you \nBest regards \nTECVICO Corp".format(i.user.get_full_name(), )
			e_destination = i.user.email
			send_new_email(e_subject,e_content,e_destination)

def sendemailnotifworkshoprequest(user,pk,is_pay):
	workshop=WorkshopRequest.objects.get(id=pk)
	expert_obj =ResearchRole.objects.get(user=workshop.expert)
	if is_pay:
		workshop.status='New'
		workshop.save()
		e_subject="TECVICO Request (ID: {})".format(workshop.id_request, )
		e_content = 'Dear {}\nHello\nHope you are going well.\nTECVICO writes this letter to thank you for showing interest in working with us. Your request has been submitted successfully. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through {}.\n\nThank you\nBest regards\nTECVICO Corp'.format(user.get_full_name(), workshop.expert.researchrole.expert_email_address)
		e_destination = user.email
		send_new_email(e_subject, e_content, e_destination)
		
		managers = Role.objects.filter(position='Request manager')
		for i in managers:
			e_subject="TECVICO Request (ID: {})".format(workshop.id_request, )
			e_content = 'Dear {}\nHello\nHope you are going well.\nA new request has been submitted recently.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company through request@tecvico.com.\n\nThank you\nBest regards\nTECVICO Corp'.format(i.user.get_full_name(),)
			e_destination = i.user.email
			send_new_email(e_subject, e_content, e_destination)
			
		
		e_content = "Dear {}\nHello\nHope you are going well.\nYou are requested to undertake this workshop request as a expert. You are requested to observe progress of the request and do the assigning tasks on it. You must observe on how well the steps of the request are going forward. You should solve some issues which you can resolve. If the problem is difficult, you should transfer it to the manager.\n\nThank you\nBest regards\nTECVICO Corp".format(expert_obj.user.get_full_name(), )
		e_destination = expert_obj.user.researchrole.expert_email_address
		send_new_email(e_subject,e_content,e_destination)