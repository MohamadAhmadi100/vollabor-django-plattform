from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.urls import reverse
from ivc_project.email_sender import send_new_email

from .models import Notification, AdFormWS
from users.models import Role, MemberProfile
from workshop.models import Workshop, Comment, AcceptReject
from research.models import (
    ResearchProject, IndustryExpertForSupervisor, IndustryFormClient, 
    IndustryFormExpert, IndustryReviewer,ResearchRole, TimeProgramming, 
    RequestUserForProject, SuperVizor, Mentor, Member, Lerner, 
    )
from users.models import MemberProfile
from django.contrib.auth.models import User


@receiver(post_save, sender=Workshop)
def get_notification(sender, instance, created, **kwargs):
    roles = Role.objects.all()
    if sender == Workshop:
        if created:
            if instance.status == "Set_time_table":
                pass
                """Notification.objects.create(title = "Dear {creator}\nThank you for your submission".format(creator = instance.top_user.get_full_name()),description = "Title: {title}\nSubmission date: {date}\nYour request has successfully been saved.\nTo launch the workshop, you need to set the timetable.\nFor more information, contact: workshop@tecvico.com\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date()),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\nI write this letter to thank you for showing interest in working with us. Your request has successfully been saved.\nTo launch the workshop, you need to set the timetable.\n\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)"""
            
            elif instance.status != "Set_time_table":
                """Notification.objects.create(title = "Dear {creator}\nThank you for your submission".format(creator = instance.top_user.get_full_name()),description = "Title: {title}\nSubmission date: {date}\nThe submission will be carefully reviewd by workshop expert and we will inform workshop team decision to you in 24 hours.\nFor more information, contact: workshop@tecvico.com\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date()),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\nI write this letter to thank you for showing interest in working with us. Your request has successfully been submitted.\n\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)"""
                
                if instance.status != "New":
                    pass
                    """Notification.objects.create(title = "Workshop",description = "{workshop} pending for guarantor's approval".format(workshop = instance.title),
                                                target = instance.top_user,
                                                link = reverse('my-workshop-status'))
                    # Email
                    e_subject = "TECVICO workshop"
                    e_content = "Dear {creator}\nHello\nHope you are going well.\nYour request has successfully been sent to {name} in order to guarantee you. If the guarantor declines your request, you must pay responsibility payment to hold the workshop. We will inform the response of the guarantor to you in 2 days.\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), name = instance.guaranteed, creator = instance.top_user.get_full_name())
                    e_destination = instance.top_user.email
                    send_new_email(e_subject,e_content,e_destination)
                    
                    e_subject = "TECVICO workshop"
                    e_content = "Dear {guarantor}\nHello\nHope you are going well\nyou are selected as guarantor for this workshop.\n\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nWorkshop director".format(title = instance.title, date = instance.created.date(), guarantor = instance.guaranteed)
                    e_destination = instance.guaranteed.user.email
                    send_new_email(e_subject,e_content,e_destination)"""
    
    
                elif instance.status == "pay_guarante":
                    pass
                    # Notif
                    """Notification.objects.create(title = "Workshop",description = "{workshop} , Pending for paying responsibility fee\n".format(workshop = instance.title),
                                                target = instance.top_user,
                                                link = reverse('my-workshop-status'))
                    # Email
                    e_subject = "TECVICO workshop"
                    e_content = "Dear {creator}\nHello\nHope you are going well\nYou must pay $100 as responsibility fee if you would like to launch your workshop\nworkshop: {title}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, creator = instance.top_user.get_full_name())
                    e_destination = instance.top_user.email
                    send_new_email(e_subject,e_content,e_destination)"""
        elif not created:
            if instance.status == "New":
                pass
                """Notification.objects.create(title = "Workshop",description = "{workshop} pending for guarantor's approval".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\nYour request has successfully been sent to {name} in order to guarantee you. If the guarantor declines your request, you must pay responsibility payment to hold the workshop. We will inform the response of the guarantor to you in 2 days.\nTitle: {title}\nSubmission date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), name = instance.guaranteed, creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)
                
                e_subject = "TECVICO workshop"
                e_content = "Dear {guarantor}\nHello\nHope you are going well\nyou are selected as guarantor for this workshop.\n\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), guarantor = instance.guaranteed)
                e_destination = instance.guaranteed.user.email
                send_new_email(e_subject,e_content,e_destination)"""
            elif instance.status == "pay_guarante":
                pass
                """Notification.objects.create(title = "New Alert (Workshop)!",description = "{workshop} , pay for guarantee\nplease click and pay for your workshop guarantee".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content ="Dear {creator}\nHello\nHope you are going well\nYou must pay $100 as responsibility fee if you would like to launch your workshop\nworkshop: {title}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company:\nEmail: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)"""

            elif instance.status == "Guarante_accept":
                pass
                """Notification.objects.create(title = "New Alert (Workshop)!",description = "{workshop} ,your Guarantee request is accepted\nWe will choose an expert for your workshop.".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                
                e_subject = "TECVICO workshop"
                if instance.guaranteed != None:
                    e_content = "Dear {creator}\nHello\nHope you are going well.\n\nGood news! Your guarantee request has been accepted by '{guarantor}'. The workshop team will review your request and inform you.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), guarantor = instance.guaranteed, creator = instance.top_user.get_full_name())
                else:
                    e_content = "Dear {creator}\nHello\nHope you are going well.\n\nGood news! Your guarantee request has been accepted . The workshop team will review your request and inform you.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)

                # email for guarantor
                if instance.guaranteed != None:
                    e_subject = "TECVICO workshop"
                    e_content = "Dear {guarantor}\nHello\nHope you are going well.\n\nThank you for accepting the request on the workshop. We hope the workshop is being gone well.\nTitle: '{title}'\nSubmitted date: '{date}'\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nworkshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), guarantor = instance.guaranteed)
                    e_destination = instance.guaranteed.user.email
                    send_new_email(e_subject,e_content,e_destination)

                for role in roles:
                    if role.position == 'workshop manager':
                        Notification.objects.create(title = "Workshop",description = "A new Workshop has been added: {workshop}, click to see the information".format(workshop = instance.title),
                                                    target = role.user,
                                                    link = reverse('list-workshop'))

                        e_subject = "TECVICO workshop"
                        e_content = "Dear {manager}\nHello\nHope you are going well.\n\nThe guarantee request from '{creator}' on workshop '{title}' submitted in '{date}' has been accepted by '{guarantor}'. Please go to your dashboard and associate an expert with this workshop.\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, creator = instance.top_user, guarantor = instance.guaranteed, date = instance.created.date(), manager = role.user.get_full_name())
                        e_destination = role.user.email
                        send_new_email(e_subject,e_content,e_destination)"""

            elif instance.status == "Expert_comment":
                pass
                """comment = Comment.objects.get(workshop = instance)
                # Notif
                Notification.objects.create(title = "Workshop",description = "{workshop} , An expert was selected\nNow Your workshop is being reviewed by an expert".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email for clients
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\nA workshop expert has been associated with your request. The expert will carefully review the material of you request. Thus, we will inform you if any modification is required or if we need more information. You can contact the workshop expert via 'workshopexpert@tecvico.com'.\nTitle: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)

                # Notif for expert
                Notification.objects.create(title = "Workshop",description = "A new Workshop has been added: {workshop},this workshop has been assigned to you, click to see the workshop information and add your comments in the comment section".format(workshop = instance.title),
                                            target = comment.expert,
                                            link = reverse('list-expert'))
                
                # Email for expert
                e_subject = "TECVICO workshop"
                e_content = "Dear {expert}\nHello\nHope you are going well.\nYou as a workshop expert are requested to undertake this project.\nWorkshop title: {title}\nSubmitted date: {date}\nYou are requested to observe progress of the workshop and do the assigned tasks on it. You must observe on how well the steps of the workshop are going forward. You should solve some issues which you can resolve.\nIf the problem is difficult, you should transfer it to me, and we can resolve it using brainstorming. I also expect you to give weekly report on this project to me.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), expert = comment.expert)
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)"""

            elif instance.status == "Manager_check":
                pass
                """comment = Comment.objects.get(workshop = instance)
                Notification.objects.create(title = "Workshop",description = "{workshop} , in this step, the manager will review your workshop request".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))

                for role in roles:
                    if role.position == 'workshop manager':
                        Notification.objects.create(title = "Workshop",description = "A new workshop is available on accept & reject list: {workshop}, click to see the list".format(workshop = instance.title),
                                                    target = role.user,
                                                    link = reverse('checked-list'))
                        
                        # Email for manager
                        e_subject = "TECVICO workshop"
                        e_content = "Dear {manager}\nHello\nHope you are going well.\nThe expert '{expert}' has investigated the martial of the request for the workshop '{title}' Submitted on '{date}'\nThe comment(s) are listed as follows:\n'{comment}'For more information, please go to your dashboard and look comment(s) at and finalize the workshop request.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), expert = comment.expert, comment = comment.comment, manager = role.user.get_full_name())
                        e_destination = role.user.email
                        send_new_email(e_subject,e_content,e_destination)"""

            elif instance.status == "Reject":
                pass
                """rej_comment = AcceptReject.objects.get(workshop = instance)
                comment = Comment.objects.get(workshop = instance)
                Notification.objects.create(title = "Workshop",description = "{workshop} , Your workshop is rejected\nplease read the manager comment and edit your workshop request".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\nThe workshop manager has reviewed your workshop request.\nTitle: '{title}' Submitted on '{date}'\nI write this letter to thank you for showing interest in working with us. Unfortunately, your workshop request was rejected by our board of directors because '{manager_comment}', as you can completely see those comments on your dashboard. We welcome you to submit other workshop in the future.\nThank you for your efforts and time. We hope to work with you in the near future.\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nOr contact your expert:\nEmail:workshopexpert@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), manager_comment = rej_comment.comment, creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)

                # email for expert
                e_subject = "TECVICO workshop"
                e_content = "Dear {expert}\nHello\nHope you are going well.\nThe workshop manager has rejected the workshop\nTitle: '{title}' Submitted on '{date}'\nI write this letter to thank you for for your efforts and time.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), expert = comment.expert)
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)"""

            elif instance.status == "Accept":
                pass
                """comment = Comment.objects.get(workshop = instance)
                Notification.objects.create(title = "Workshop",description = "Congratulations, your workshop: ({workshop}) is accepted succesfully".format(workshop = instance.title),
                                            target = instance.top_user,
                                            link = reverse('my-workshop-status'))
                # Email
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\n\nCongrats! Your request for holding the workshop '{title}' Submitted on '{date}'has been accepted by workshop team. To hold your workshop, you must follow the workshop steps as below:\n1. You must prepare and finalize your content and upload it in two weeks after acceptance.\n2. You must record a video and upload it in two weeks after acceptance.\nNote: The advertisement team will start advertising after receiving the mention requirements.\n\n Please go to your dashboard and follow the workshop steps. \nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nOr contact your expert:\n{expert_email}\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), expert_email = comment.expert.email, creator = instance.top_user.get_full_name())
                e_destination = instance.top_user.email
                send_new_email(e_subject,e_content,e_destination)

                # Email for expert
                e_subject = "TECVICO workshop"
                e_content = "Dear {creator}\nHello\nHope you are going well.\n\nThe workshop '{title}' Submitted on '{date}'has been accepted by workshop team.\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact workshop director\nEmail:workshop@tecvico.com\n\nOr contact the workshop craetor:\n{user_email}\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(title = instance.title, date = instance.created.date(), user_email = instance.top_user.email, creator = instance.top_user.get_full_name())
                e_destination = comment.expert.email
                send_new_email(e_subject,e_content,e_destination)
                
                for role in roles:
                    if role.position == 'Advertisement manager':
                        Notification.objects.create(title = "Workshop",description = "A new workshop has been added: {workshop}, click to see the information".format(workshop = instance.title),
                                                    target = role.user,
                                                    link = reverse('ad-form', args=[instance.pk]))
                        
                        # Email for advertisement
                        e_subject = "TECVICO workshop"
                        e_content = "Dear {ad_manager}\nHello\nHope you are going well. A new workshop has been accepted by workshop team on “Date”. You are requested to proceed it. The company expects your team to do the best.\nYou should announce the interested people to participate in this workshop. If you need more information, you can contact the workshop expert with '{expert_email}'.\nYou also can go to your dashboard and see some information you need to advertise from this workshop.\n\nTitle: {title}\nSubmitted date: {date}\n\nDo not reply to this Email. If you have any questions or concerns, please feel free to contact the company: workshop@tecvico.com\n\nThank you.\n\nBest regards\n\nTECVICO Corp".format(expert_email = comment.expert.email, title = instance.title, date = instance.created.date(), ad_manager = role.user.get_full_name())
                        e_destination = role.user.email
                        send_new_email(e_subject,e_content,e_destination)"""
                                
@receiver(post_delete, sender=Workshop)
def workshop_delete(sender, instance, **kwargs):
    roles = Role.objects.all()
    for role in roles:
        if role.position == 'workshop manager':
            Notification.objects.create(title = "Workshop",description = "A Workshop has been deleted: {workshop}".format(workshop = instance.title),
                                        target = role.user,
                                        link = reverse('notification-page'))
