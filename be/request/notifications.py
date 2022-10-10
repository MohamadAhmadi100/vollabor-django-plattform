from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from ivc_project.email_sender import send_new_email

from dashboard.models import Notification
from users.models import Role, MemberProfile 
from users.models import MemberProfile
from django.contrib.auth.models import User

from .models import(
        BadgeInterviewReview, 
        SupervisorRequest, 
        SupervisorReview, 
        InterviewSession, 
        WorkshopRequest, 
        WorkshopReview, 
        BadgeExpert, 
    )


# -----> Supervisor <-----
@receiver(post_save, sender=SupervisorRequest)
def send_notification_supervisor_r_table(sender, instance, created, **kwargs):
    managers = Role.objects.filter(position='Request manager')
    if created:
        for i in managers:
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='A new supervisor request has been submitted recently. Go to your dashboard to see more information.', target=i.user, 
                link=reverse('request:manager-change-expert-supervisor', args=[instance.pk])).save()
                    
        Notification(title='Request (ID: {})'.format(instance.id_request), 
            description='Your supervisor request has been submitted successfully.', target=instance.user, 
            link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()

        Notification(title='Request (ID: {})'.format(instance.id_request), 
            description='A supervisor request has been added to your list, Go to your dashboard to see more information.', target=instance.expert, 
            link=reverse('request:select-reviewer-supervisor', args=[instance.pk])).save()

    if not created:
        if instance.status == 'send_to_manager':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='A supervisor request assessment has been sent to you. Go to your dashboard to see it.', target=i.user, 
                    link=reverse('request:manager-detail-supervisor', args=[instance.pk])).save()
                    

        if instance.status == 'accepted_by_expert':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='The supervisor request has been accepted by the expert. Go to your dashboard to see it.', target=i.user, 
                    link='notification-page').save()
                        
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Congratulations! Your supervisor request has been accepted. Go to your dashboard to see it.', target=instance.user, 
                link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()

        if instance.status == 'accepted_by_manager':

            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Congratulations! Your supervisor request has been accepted. Go to your dashboard to see it.', target=instance.user, 
                link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='The supervisor request the accepeted by manager. Go to your dashboard to see it.', target=instance.expert, 
                link=reverse('request:select-reviewer-supervisor', args=[instance.pk])).save()


        if instance.status == 'rejected_by_manager':
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Your supervisor request has been rejected. Go to your dashboard to see more information.', target=instance.user, 
                link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='The supervisor request has been rejected by manager. Go to your dashboard to see more information.', target=instance.user, 
                link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()
                    

        if instance.status == 'rejected_by_expert':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='The supervisor request has been rejected by the expert. Go to your dashboard to see more information.', target=i.user, 
                    link=reverse('request:manager-change-expert-supervisor', args=[instance.pk])).save()
            
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Your supervisor request has been rejected. Go to your dashboard to see more information.', target=instance.user, 
                link=reverse('request:supervisor-request-detail', args=[instance.pk])).save()
                    
@receiver(post_save, sender=SupervisorReview)
def send_notification_supervisor_reviewer_r_table(sender, instance, created, **kwargs):
    managers = Role.objects.filter(position='Request manager')
    if created:
        Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
            description='You have been requested to review the supervisor application. Go to your dashboard to observe it.', target=instance.user, 
            link=reverse('request:reviewer_interview-request-supervisor', args=[instance.pk])).save()
    if not created:

        if instance.status == 'reject':
            Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
                description='The reviewer, namely {}, has been declined to assess the supervisor request.'.format(instance.user.get_full_name()), target=instance.supervisor.expert, 
                link=reverse('request:select-reviewer-supervisor', args=[instance.supervisor.pk])).save() 

        if instance.status == 'evaluated':
            Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
                description='The reviewer, {}, has assessed the supervisor request, Go to your dashboard to see the score.'.format(instance.user.get_full_name()), target=instance.supervisor.expert,
                link=reverse('request:expert-send-request-to-manager', args=[instance.supervisor.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
                description='TECVICO writes this letter to thank you for assessing the supervisor request.', target=instance.user, 
                link="notification-page").save()
                

        if instance.status == 'accept':
            if instance.score_2 == 0:
                Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
                    description='TECVICO writes this letter to thank you for approving the review request. You have one week to send the evaluation, otherwise you will be given a negative point.', target=instance.user, 
                    link=reverse('request:reviewer-supervisor-accept', args=[instance.pk])).save()
                    
                Notification(title='Request (ID: {})'.format(instance.supervisor.id_request), 
                    description='The reviewer {}, has approved the supervisor request review. Go to your dashboard to see it.'.format(instance.user.get_full_name()), target=instance.supervisor.expert,
                    link=reverse('request:select-reviewer-supervisor', args=[instance.supervisor.pk])).save() 
    

            
            
# -----> Workshop <-----
@receiver(post_save, sender=WorkshopRequest)
def send_notification_workshop_r_table(sender, instance, created, **kwargs):
    managers = Role.objects.filter(position='Request manager')
    if created:
        for i in managers:
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='A workshop presenter request has been submitted recently. Go to your dashboard to see more information.', target=i.user, 
                link=reverse('request:manager-change-expert-workshop', args=[instance.pk])).save()
                    
        Notification(title='Request (ID: {})'.format(instance.id_request), 
            description='Your workshop presenter request has been submitted successfully.', target=instance.user, 
            link=reverse('request:workshop-request-detail', args=[instance.pk])).save()

        Notification(title='Request (ID: {})'.format(instance.id_request), 
            description='A workshop presenter request has been added to your list, Go to your dashboard to see more information.', target=instance.expert, 
            link=reverse('request:expert-workshop-detail', args=[instance.pk])).save()

    if not created:
        if instance.status == 'send_to_manager':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='A workshop presenter request assessment has been sent to you. Go to your dashboard to see it.', target=i.user, 
                    link=reverse('request:manager-detail-workshop', args=[instance.pk])).save()
                    

        if instance.status == 'accepted_by_expert':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='The workshop presenter request has been accepted by the expert. Go to your dashboard to see it.', target=i.user, 
                    link=reverse('request:manager-change-expert-workshop', args=[instance.pk])).save()
                        
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Congratulations! Your workshop presenter request has been accepted. Go to your dashboard to see it.', target=instance.user, 
                link=reverse('request:workshop-request-detail', args=[instance.pk])).save()

        if instance.status == 'accepted_by_manager':

            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Congratulations! Your workshop presenter request has been accepted. Go to your dashboard to see it.', target=instance.user, 
                link=reverse('request:workshop-request-detail', args=[instance.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='The workshop presenter request has been accepeted by manager. Go to your dashboard to see it.', target=instance.expert, 
                link=reverse('request:expert-workshop-detail', args=[instance.pk])).save()


        if instance.status == 'rejected_by_manager':
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Your workshop presenter request has been rejected. Go to your dashboard to see more information.', target=instance.user, 
                link=reverse('request:workshop-request-detail', args=[instance.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='The workshop presenter request has been rejected by the manager. Go to your dashboard to see more information.', target=instance.expert, 
                link=reverse('request:expert-workshop-detail', args=[instance.pk])).save()
                    

        if instance.status == 'rejected_by_expert':
            for i in managers:
                Notification(title='Request (ID: {})'.format(instance.id_request), 
                    description='The workshop presenter request has been rejected by the expert. Go to your dashboard to see more information.', target=i.user, 
                    link=reverse('request:manager-change-expert-workshop', args=[instance.pk])).save()
            
            Notification(title='Request (ID: {})'.format(instance.id_request), 
                description='Your workshop presenter request has been rejected. Go to your dashboard to see more information.', target=instance.user, 
                link=reverse('request:workshop-request-detail', args=[instance.pk])).save()

                    
@receiver(post_save, sender=WorkshopReview)
def send_notification_workshop_reviewer_r_table(sender, instance, created, **kwargs):
    managers = Role.objects.filter(position='Request manager')
    if created:
        Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
            description='You have been requested to review the workshop presenter application. Go to your dashboard to observe it.', target=instance.user, 
            link=reverse('request:reviewer_interview-request-workshop', args=[instance.pk])).save()
    if not created:

        if instance.status == 'reject':
            Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                description='The reviewer, namely {}, has been declined to assess the workshop presenter request.'.format(instance.user.get_full_name()), target=instance.workshop.expert, 
                link=reverse('request:expert-workshop-detail', args=[instance.workshop.pk])).save() 

        if instance.status == 'evaluated':
            Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                description='The reviewer, {}, has assessed the workshop presenter request, Go to your dashboard to see the score.'.format(instance.user.get_full_name()), target=instance.workshop.expert,
                link=reverse('request:expert-send-request-workshop-to-manager', args=[instance.workshop.pk])).save()
                
            Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                description='TECVICO writes this letter to thank you for assessing the workshop presenter request.', target=instance.user, 
                link=reverse('request:reviewer-workshop-accept', args=[instance.pk])).save()
                

        if instance.status == 'accept':
            if instance.score_2 == 0:
                Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                    description='TECVICO writes this letter to thank you for approving the review request. You have one week to send the evaluation, otherwise you will be given a negative point.', target=instance.user, 
                    link=reverse('request:reviewer-workshop-accept', args=[instance.pk])).save() 
                    
                Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                    description='The reviewer {}, has approved  to review the workshop presenter request. Go to your dashboard and see it.'.format(instance.user.get_full_name()), target=instance.workshop.expert,
                    link=reverse('request:expert-workshop-detail', args=[instance.workshop.pk])).save() 

        if instance.status == 'revise':
            if instance.workshop.status == 'revised_by_manager':
                Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                    description='There is a revision for your assessment of the workshop presenter request. Go to your dashboard and see it.', target=instance.user, 
                    link=reverse('request:reviewer-workshop-accept', args=[instance.pk])).save()
                    
                Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                    description='The manager has revised the workshop presenter request assessment. Go to your dashboard and see it. '.format(instance.user.get_full_name()), target=instance.workshop.expert,
                    link=reverse('request:expert-workshop-detail', args=[instance.workshop.pk])).save()

            if instance.workshop.status == 'revised_by_expert':
                Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                    description='There is a revision for your assessment of the workshop presenter request. Go to your dashboard and see it.', target=instance.user, 
                    link=reverse('request:reviewer-workshop-accept', args=[instance.pk])).save()
                    
                for i in managers:
                    Notification(title='Request (ID: {})'.format(instance.workshop.id_request), 
                        description='The expert has revised the workshop presenter request assessment. Go to your dashboard and see it.'.format(instance.user.get_full_name()), target=i.user,
                        link=reverse('request:manager-change-expert-workshop', args=[instance.workshop.pk])).save()
