from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from ivc_project.email_sender import send_new_email

from dashboard.models import Notification
from users.models import Role, MemberProfile
from workshop.models import Workshop, Comment, AcceptReject
from .models import (
	ResearchProject, IndustryExpertForSupervisor, IndustryFormClient, 
	IndustryFormExpert, IndustryReviewer,ResearchRole, TimeProgramming, 
	RequestUserForProject, SuperVizor, Mentor, Member, Lerner, ResearchMeeting
	)
from users.models import MemberProfile
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from datetime import date



# --- Client --- #
@receiver(post_save, sender=IndustryFormClient)
def send_notification_client_table(sender, instance, created, **kwargs):
	users = ResearchRole.objects.all()
	if created:
		pass
				
	#**********
	# Reject Project
		if instance.status == 'r':
			Notification(title='Project (ID: {})'.format(instance.id_project), 
				description='Your project has been rejected. For more information, go to your dashboard.', target=instance.user, 
				link=reverse('industry:industry-reject-detail', args=[instance.pk])).save()

		if instance.status == 'rejected_by_expert':
			Notification(title='Project (ID: {})'.format(instance.id_project), 
				description='Your project has been rejected. For more information, go to your dashboard.', target=instance.user, 
				link=reverse('industry:industry-reject-detail', args=[instance.pk])).save()

			for i in users:
				if i.director == True:
					Notification(title='Project (ID: {})'.format(instance.id_project), 
						description='The expert,{},  has rejected the project. For more information, go to your dashboard.', target=i.user, 
						link=reverse('industry:industry-view-edit', args=[instance.pk])).save()
# --- Expert --- #
# @receiver(post_save, sender=IndustryFormExpert)
# def send_notification_expert_table(sender, instance, created, **kwargs):
	
# 	if created:
# 		if not instance.formclint.main_supervisor:
# 			if instance.formclint.status == 'accept_or_reject_expert':
# 				Notification(title='Project (ID: {})'.format(instance.formclint.id_project), 
# 					description='A new project has been assigned to you. Moreover, you have been given some accesses. For more information, go to your dashboard.', target=instance.expert, 
# 					link=reverse('industry:research-access-expert-detail', args=[instance.pk])).save()
# 			else:
# 				Notification(title='Project (ID: {})'.format(instance.formclint.id_project), 
# 					description='A new project has been assigned to you. For more information, go to your dashboard.', target=instance.expert, 
# 					link=reverse('industry:industry-expert-detail', args=[instance.pk])).save()
		
		


# --- Supervisors --- #
@receiver(post_save, sender=IndustryExpertForSupervisor)
def send_notification_supervisor_table(sender, instance, created, **kwargs):
	users = ResearchRole.objects.all()

	# Send proposal for expert
	if not created:
		if instance.status == 'a':
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='A supervisor has been applied for the project. For more information, go to your dashboard.', target=instance.client_form.expert, 
				link=reverse('industry:industry-supervisor-expert-detail', args=[instance.pk])).save()

	# Reject Proposal 
	# if not created:
	# 	if instance.status == 'b':
	# 		Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
	# 			description='There is a revision for your proposal. You are strongly recommend to resubmit your proposal according to the comments. For more information, go to your dashboard.', target=instance.supervisor, 
	# 			link='industry:industry-supervisor-list').save()

	# Resubmitted proposal send to the director 
	if not created:
		if instance.status == 'resubmition-to-director':
			for i in users:
				if i.director == True:
					Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
						description='The resubmitted proposal has been sent to you. For more information, go to your dashboard.', target=i.user, 
						link=reverse('industry:industry-director-see-score', args=[instance.pk])).save()

	# Send to the director to see the grades
	if not created:
		if instance.status == 'd':
			for i in users:
				if i.director == True:
					Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
						description='A review evaluation has been sent to you. For more information, go to your dashboard.', target=i.user, 
						link=reverse('industry:industry-director-see-score', args=[instance.pk])).save()

	# Reject supervisor by director
	if not created:
		if instance.status == 'h' and instance.client_form.formclint.main_supervisor is None:
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='Your propposal has been rejected. For more information, go to your dashboard.', target=instance.supervisor, 
				link='industry:industry-supervisor-list').save()

	# Send for expert to send the contract
	if not created:
		if instance.status == 'x':
			if instance.client_form.directo_see_reviewer == True:
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='You accepted the proposal successfully. Further, you must send the contract to the supervisor. For more information, go to your dashboard.', target=instance.client_form.expert, 
					link=reverse('industry:industry-expert-contract', args=[instance.pk])).save()
			else:
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='The proposal has been accepted by the director. You must send the contact to the supervisor. For more information, go to your dashboard.', target=instance.client_form.expert, 
					link=reverse('industry:industry-expert-contract', args=[instance.pk])).save()

	# Send contract to supervisor
	if not created:
		if instance.status == 't':
			if instance.grade is None:
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='Congrats, your proposal has been accepted. You must sing the contact and submit it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(instance.client_form.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.supervisor, 
					link=reverse('industry:industry-supervisor-see-contract', args=[instance.pk])).save()

	# Contract review by expert
	if not created:
		if instance.status == 'g':
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='A signed contract has been added to your list. For more information, go to your dashboard.'.format(instance.client_form.formclint.title), target=instance.client_form.expert, 
				link=reverse('industry:industry-expert-contract', args=[instance.pk])).save()

            
	# Reject contract by Expert
# 	if not created:
# 		if instance.status == 'reject_contract':
# 			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
# 				description='Your contract needs a revision. You are strongly recommended to modify the contact and then submit it to the company by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.supervisor, 
# 				link=reverse('industry:industry-supervisor-see-contract', args=[instance.pk])).save()

	# Send contract for director
	if not created:
		if instance.status == 'z':
			for i in users:
				if i.director == True:
					Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
						description='A signed contract has been added to your list. For more information, go to your dashboard.', target=i.user, 
						link='industry:industry-director').save()

	# Create project
	if not created:
		if instance.status == 'n':
			if instance.client_form.formclint.main_supervisor:
				# Client
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='Congrats, your project has been moved to new status. For more information, go to your dashboard.', target=instance.client_form.formclint.user, 
					link='dashboard-page').save()
				
				# Director
				for i in users:
					if i.director == True:
						Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
							description='The project has been moved to new status. For more information, go to your dashboard.'.format(instance.client_form.formclint.title), target=i.user, 
							link='industry:industry-director').save()
			else:
				
				# Supervisor
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='Your request to undertake the project has been approved. For more information, go to your dashboard.', target=instance.supervisor, 
					link='dashboard-page').save()
				
				# Client
				Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
					description='Congrats, your project status has been changed to new. For more information, go to your dashboard.', target=instance.client_form.formclint.user, 
					link='dashboard-page').save()
				
				# Director
				for i in users:
					if i.director == True:
						Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
							description='The project has been moved to new status. For more information, go to your dashboard.'.format(instance.client_form.formclint.title), target=i.user, 
							link='industry:industry-director').save()


	# Expert access accept or reject (main sopervisor)
	if not created:
		if instance.status == 'special_expert':
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='You have been given the access to accept or reject the project. For more information, go to your dashboard.', target=instance.client_form.expert, 
				link='industry:research-access-expert-panel').save()


	# Expert access review
	if not created:
		if instance.status == 'special_expert_review':
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='A new assessment has been sent to you. You have an access to accept or reject the proposal. For more information, go to your dashboard.', target=instance.client_form.expert, 
				link=reverse('industry:research-sepcial-expert-detail-main', args=[instance.pk])).save()


	# Expert access create project
	if not created:
		if instance.status == 'special_expert_create_project':
			Notification(title='Project (ID: {})'.format(instance.client_form.formclint.id_project), 
				description='You have been given the access to change the project status. For more information, go to your dashboard.', target=instance.client_form.expert, 
				link=reverse('industry:industry-director-main-supervisor', args=[instance.pk])).save()


# --- Reviewer --- #
@receiver(post_save, sender=IndustryReviewer)
def send_notification_reviewer_table(sender, instance, created, **kwargs):
	users = ResearchRole.objects.all()
	if created:
		if instance.status == 'n':
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='You have been requested to review the proposal. If you are interested in assessing the proposal, you must approve the request by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.reviewer, 
				link=reverse('industry:industry-reviewer-detail', args=[instance.pk])).save()
		if instance.status == 'new_project':
			if instance.object_client:
				Notification(title='Project (ID: {})'.format(instance.object_client.id_project), 
					description='You have been requested to review the project. If you are interested in assessing the project, you must approve the request by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.reviewer, 
					link=reverse('industry:research-reviewer-project-detail', args=[instance.pk])).save()
					
			if instance.object_expert:
				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='You have been requested to review the project. If you are interested in assessing the project, you must approve the request by {} (Coordinated Universal Time (UTC)). For more information, go to your dashboard.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.reviewer, 
					link=reverse('industry:research-reviewer-project-detail', args=[instance.pk])).save()

	# Reject Project
	if not created:
		if instance.status == 'r':
			# Send for expert
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='The reviewer, namely {}, declined to assess the proposal. You should go to your dashboard and select a new reviewer. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_supervisor.client_form.expert, 
				link=reverse('industry:industry-expert-reviewer-detail', args=[instance.object_supervisor.pk])).save()
				

	# Send score for expert
		if instance.status == 'a' and instance.score_1 == 0:
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='TECVICO writes this letter to thank you for approving the review request, you are given one week by {} (Coordinated Universal Time (UTC)) to send the evaluation, otherwise you will be given a negative point and replaced with a new reviewer.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.reviewer, 
				link=reverse('industry:industry-reviewer-detail', args=[instance.pk])).save()

			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='The reviewer, {}, has approved the review request. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_supervisor.client_form.expert,
				link=reverse('industry:industry-expert-reviewer-detail', args=[instance.object_supervisor.pk])).save()
			

	# Send score for expert
		if instance.status == 'e':
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='The reviewer, {}, sent the assessment. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_supervisor.client_form.expert,
				link=reverse('industry:industry-expert-reviewer-detail', args=[instance.object_supervisor.pk])).save()
				
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='TECVICO is writing this letter to thank you for assessing this proposal. Your assessment has been submitted successfully. For more information, go to your dashboard.', target=instance.reviewer, 
				link=reverse('industry:industry-reviewer-detail', args=[instance.pk])).save()

	# Not see 
		if instance.status == 's':
			# Send for expert
			Notification(title='Project (ID: {})'.format(instance.object_supervisor.client_form.formclint.id_project), 
				description='The reviewer, {}, has not answered to your request yet. For more information, go to your dashboard.'.format(instance.reviewer), target=instance.object_supervisor.client_form.expert,
				link='industry:industry-expert-list').save()
			 

		if instance.status == 'reject_project':
			if instance.object_client:
				for i in users:
					if i.director == True:
						Notification(title='Project (ID: {})'.format(instance.object_client.id_project), 
							description='The reviewer, namely {}, has been declined to assess the project. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=i.user, 
							link=reverse('industry:research-reviewer-project-detail', args=[instance.object_client.pk])).save()
					
			if instance.object_expert:
				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='The reviewer, namely {}, has been declined to assess the project. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_expert.expert, 
					link=reverse('industry:research-access-expert-detail', args=[instance.object_expert.pk])).save()


		if instance.status == 'send_director_project':
			if instance.object_client:
				for i in users:
					if i.director == True:
						Notification(title='Project (ID: {})'.format(instance.object_client.id_project), 
							description='The reviewer, {}, sent the assessement. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=i.user, 
							link=reverse('industry:industry-view-edit', args=[instance.object_client.pk])).save()
							
				Notification(title='Project (ID: {})'.format(instance.object_client.id_project), 
					description='TECVICO is writing this letter to thank you for assessing this project. Your assessment has been submitted successfully. For more information, go to your dashboard.', target=instance.reviewer, link="notification-page").save()
						
			if instance.object_expert:
				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='The reviewer, {}, sent the assessment. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_expert.expert, 
					link=reverse('industry:research-access-expert-detail', args=[instance.object_expert.pk])).save()
					
				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='TECVICO is writing this letter to thank you for assessing the project. Your assessment has been submitted successfully.', target=instance.reviewer, link="notification-page").save()
						

		if instance.status == 'accept_project':
			if instance.object_expert and instance.score_1 == 0:
				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='TECVICO writes this letter to thank you for approving the project review request, you are given one week by {} (Coordinated Universal Time (UTC)) to send the evaluation, otherwise you will be given a negative point and replaced with a new reviewer.'.format(instance.deadline.strftime('%Y/%m/%d %H:%M')), target=instance.reviewer, 
					link=reverse('industry:research-reviewer-project-detail', args=[instance.pk])).save()

				Notification(title='Project (ID: {})'.format(instance.object_expert.formclint.id_project), 
					description='The reviewer, {}, approved the evaluation request. For more information, go to your dashboard.'.format(instance.reviewer.get_full_name()), target=instance.object_expert.expert,
					link=reverse('industry:research-access-expert-detail', args=[instance.object_expert.pk])).save()
			
			

			

@receiver(post_save, sender=ResearchProject)
def send_notification_request_table(sender, instance, created, **kwargs):
	if not created:
		if instance.status == 'done':
		    pass
# 			instance.project.client_form.expert.ResearchRole.ongoing_project_expert += 1
# 			instance.project.client_form.expert.ResearchRole.save()



@receiver(post_save, sender=RequestUserForProject)
def send_notification_request_table(sender, instance, created, **kwargs):
	if created:
		pass
			
	if not created:
		if instance.status == 'reject':
			Notification(title='Project (ID: {})'.format(instance.project_request.project.client_form.formclint.id_project),
			description='Your request has been rejected. For more information, go to your dashboard.', target=instance.user,
			link='').save()

		if instance.status == 'accept':
			Notification(title='Project (ID: {})'.format(instance.project_request.project.client_form.formclint.id_project),
			description='The supervisor accepted an applicant’s request to join the project. For more information, go to your dashboard and send the contract.', target=instance.project_request.project.client_form.expert,
			link='').save()



@receiver(post_save, sender=SuperVizor)
def notification_supervisor_project_table(sender, instance, created, **kwargs):
	if created:
		Notification(title='Project (ID: {})'.format(instance.research.project.client_form.formclint.id_project), 
			description='Congrats, your application has been approved to be as an advisor. Please wait for contract. For more information, go to your dashboard.', target=instance.user, 
			link='').save()
			
@receiver(post_save, sender=Mentor)
def notification_mentor_project_table(sender, instance, created, **kwargs):
	if created:
		Notification(title='Project (ID: {})'.format(instance.research.project.client_form.formclint.id_project), 
			description='Congrats, your application has been approved to be as a mentor. Please wait for contract. For more information, go to your dashboard.', target=instance.user, 
			link='').save()
			
@receiver(post_save, sender=Member)
def notification_member_project_table(sender, instance, created, **kwargs):
	if created:
		Notification(title='Project (ID: {})'.format(instance.research.project.client_form.formclint.id_project), 
			description='Congrats, your application has been approved to be as a member. Please wait for contract. For more information, go to your dashboard.', target=instance.user, 
			link='').save()
			
@receiver(post_save, sender=Lerner)
def notification_learner_project_table(sender, instance, created, **kwargs):
	if created:
		Notification(title='Project (ID: {})'.format(instance.research.project.client_form.formclint.id_project), 
			description='Congrats, your application has been approved to be as a learner. Please wait for contract. For more information, go to your dashboard.', target=instance.user, 
			link='').save()