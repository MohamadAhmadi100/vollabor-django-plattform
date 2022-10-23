from  django.shortcuts import get_object_or_404
from dashboard.models import Notification
from ivc_project.email_sender import send_new_email
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from .models import Timetable,VirtualEvent
from datetime import date


# You applied to this workshop successfully. Title Workshop date:  time time zoon.   Event link
def notifdesc(VE,status):
    start_time=Timetable.objects.filter(vitual_event=VE).first().start_time
    NOTIFICATION_DESCRIPTIONS={
    'Create':_(f'Your {VE.type} has been saved successfully. Go to your dashboard and complete the submission process.'),

    'Select_expert_to_director':_(f'A new {VE.type} has been added to your list, go to your dashboard and select an expert.'),
    'Select_expert_to_presenter':_(f'Your {VE.type} has been submitted successfully. For more information, go to your dashboard.'),

    'Reject':_(f'TECVICO is very sorry to inform you that your {VE.type} request has been rejected. For more information, go to your dashboard.'),

    'Revise':_(f'Your {VE.type} needs a revision. Go to your dashboard and modify it.'),

    'Resubmit_to_expert':_(f'A resubmitted {VE.type} has been added to your list, Go to your dashboard and proceed with it.'),
    'Resubmit_to_director':_(f'A resubmitted {VE.type} has been added to your list, Go to your dashboard and proceed with it.'),
    'Resubmit_to_presenter':_(f'We recieved your resubmitted {VE.type}. For more information, go to your dashboard.'),

    'Expert_decide_to_expert':_(f'You have been selected to undertake this {VE.type}. For more information, go to your dashboard.'),

    'Remove':_(f'You deleted your {VE.type}. For more information, go to your dashboard.'),

    'Published_to_presenter':_(f'Congratulations! Your {VE.type} has been accepted and published onto the site. For more information, go to your dashboard.'),

    'Edit_to_director':_(f"The {VE.type} presenter sent a request to change the event's time. For more information, go to your dashboard."),
    'Edit_to_expert':_(f"The {VE.type} presenter sent a request to change the event's time. For more information, go to your dashboard."),


    'Edit_time_accept':_(f'Your request to change the {VE.type} holding time has been accepted. For more information, go to your dashboard.'),
    'Edit_time_reject':_(f'TECVICO is very sorry to inform you that your request to change the {VE.type} holding time has been rejected. For more information, go to your dashboard.'),

#Send to Members.........
    'Send_to_members':_(f'The {VE.type} holding time has been moved to {VE.start_date} at {start_time}. '),
    'Upload_file':_(f'The {VE.type} presenter uploaded a file for the {VE.type}. For access to this file, go to your dashboard.'),
    'Upload_video':_(f'A recorded video of your {VE.type} has been uploaded. It will completely be removed in 30 days.'),


    'change_expert':_(f'A recorded video of your {VE.type} has been uploaded. It will completely be removed in 30 days.'),


}
    return NOTIFICATION_DESCRIPTIONS[status]


def content(VE,status,date,title,user,id=None):
    start_time=Timetable.objects.filter(vitual_event=VE).first().start_time
    if VE.expert:
        email=VE.expert.email
        related_member='expert'
    else:
        email='virtualeventdirector@tecvico.com'
        related_member='manager'
    content={
        'Create':_(f'"Dear {user}\nHello\nHope you are going well.\nYour {VE.type} has been saved successfully. Go to your dashboard and complete the submission process.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the copany through virtualevent@tecvico.com.\n\nThank you\nSincerely\n\nTECVICO Corp.'),


        'Select_expert_to_director':_(f'"Dear {user}\nHello\nHope you are going well.\nA new {VE.type} has been added to your list, go to your dashboard and select an expert.\n{VE.type} title: {title}\nSubmitted date: {date}\nThis email has been sent automatically, do not reply to this Email.\n\nThank you\nSincerely\n\nTECVICO Corp'),
        'Select_expert_to_presenter':_(f'"Dear {user}\nHello\nHope you are going well.\nYour {VE.type} has been submitted successfully. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the copany through virtualeventdirector@tecvico.com.\n\nThank you\nSincerely\n\nTECVICO Corp'),
       
        'Reject':_(f'"Dear {user}\nHello\nHope you are going well.\nTECVICO is very sorry to inform you that your {VE.type} request has been rejected. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the virtual event {related_member} through {email}.\n\nThank you\nSincerely\n\nTECVICO Corp'),
       
        'Revise':_(f'"Dear {user}\nHello\nHope you are going well.\nYour {VE.type} needs a revision. Go to your dashboard and modify it.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the Virtual event {related_member} through {email}.\n\nThank you\nSincerely\n\nTECVICO Corp'),
        
        'Resubmit_to_expert':_(f'"Dear {user}\nHello\nHope you are going well.\nA resubmitted {VE.type} has been added to your list, Go to your dashboard and proceed with it.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the virtual event {related_member} through virtualeventdirector@tecvico.com.\n\nThank you\nSincerely,s\n\nTECVICO Corp'),
        'Resubmit_to_director':_(f'"Dear {user}\nHello\nHope you are going well.\nA resubmitted {VE.type} has been added to your list, Go to your dashboard and proceed with it.\n{VE.type}t title: {title}\nSubmitted date: {date}\n\nThank you\nSincerely\n\nTECVICO Corp'),
        'Resubmit_to_presenter':_(f'"Dear {user}\nHello\nHope you are going well.\nWe recieved your resubmitted {VE.type}. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely\n\nTECVICO Corp'),
       
        'Expert_decide_to_expert':_(f'"Dear {user}\nHello\nHope you are going well.\nYou have been selected to undertake this {VE.type}. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through Virtualeventdirector@tecvico.com.\n\nThank you\nSincerely,s\n\nTECVICO Corp'),
       
        'Remove':_(f'"Dear {user}\nHello\nHope you are going well.\nYou deleted your {VE.type}. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact the company through {email}.\n\nThank you\nSincerely\n\nTECVICO Corp'),
       
        'Published_to_presenter':_(f'"Dear {user}\nHello\nHope you are going well.\nCongratulations! Your {VE.type} has been accepted and published onto the site. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp'),

        'Edit_to_director':_(f"Dear {user}\nHello\nHope you are going well.\nThe {VE.type} presenter sent a request to change the event's time. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. \nThank you\nSincerely,s\n\nTECVICO Corp"),
        'Edit_to_expert':_(f"Dear {user}\nHello\nHope you are going well.\nThe {VE.type} presenter sent a request to change the event's time. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp"),

        'Edit_time_accept':_(f"Dear {user}\nHello\nHope you are going well.\nYour request to change the {VE.type} holding time has been accepted. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp"),
        'Edit_time_reject':_(f"Dear {user}\nHello\nHope you are going well.\nTECVICO is very sorry to inform you that your request to change the {VE.status} holding time has been rejected. For more information, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through{email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp"),


#Send to Members.........
        'Send_to_members':_(f"Dear {user}\nHello\nHope you are going well.\nThe {VE.type} holding time has been moved to {VE.start_date} at {start_time} (Time zoon).\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp\nFor view detail click:\nhttps://tecvico.com/virtualevents/show/{id}"),
        'Upload_file':_(f"Dear {user}\nHello\nHope you are going well.\nThe {VE.type} presenter uploaded a file for the {VE.type}. For access to this file, go to your dashboard.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp\nFor view detail click:\nhttps://tecvico.com/virtualevents/show/{id}"),
        'Upload_video':_(f"Dear {user}\nHello\nHope you are going well.\nA recorded video of your {VE.type} has been uploaded. It will completely be removed in 30 days.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp\nFor view detail click:\nhttps://tecvico.com/virtualevents/show/{id}"),


        'change_expert':_(f"Dear {user}\nHello\nHope you are going well.\nA recorded video of your {VE.type} has been uploaded. It will completely be removed in 30 days.\n{VE.type} title: {title}\nSubmitted date: {date}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event {related_member} through {email}.\n\nThank you\nSincerely,s\n\nTECVICO Corp\nFor view detail click:\nhttps://tecvico.com/virtualevents/show/{id}"),

    }
    return content[status]



def virtualevent_Send_NotifEmail(virtual_event,target_user,reverse_url_name,status=None):
    if status:
        pass
    else:
        status=virtual_event.status
    if status == 'Expert_decide':
        if reverse_url_name == 'expert':
            status='Expert_decide_to_expert'
        elif reverse_url_name == 'director':
            status='Expert_decide_to_director'


    elif status == 'Select_expert':
            if reverse_url_name == 'director':
                status='Select_expert_to_director'
            elif reverse_url_name == 'presenter':
                status='Select_expert_to_presenter'

    elif status == 'Resubmit_to_expert' or status == 'Resubmit_to_director' :
        if reverse_url_name == 'presenter':
                status='Resubmit_to_presenter'



    elif status == 'Published':
            if reverse_url_name == 'director':
                status='Published_to_director'
            elif reverse_url_name == 'expert':
                status='Published_to_expert'
            elif reverse_url_name == 'presenter':
                status='Published_to_presenter'

    elif status=="Edit_time":
        if reverse_url_name == 'director':
                status='Edit_to_director'
        elif reverse_url_name == 'expert':
                status='Edit_to_expert'
        elif reverse_url_name == 'presenter':
                status='Edit_to_presenter'




    sub=f'TECVICO virtual event (ID: {virtual_event.unique_id})'
    txt=content(virtual_event,status,virtual_event.created,virtual_event.title,target_user,reverse_url_name)
    destination=target_user.email
    send_new_email(sub,txt,destination)
    Notification.objects.create(title = f"virtual event (ID: {virtual_event.unique_id})",description=notifdesc(virtual_event,status),
                                            target = target_user,
                                            #link = reverse(reverse_url_name)
                                            )



def AutomateSendingEmail():
    published=VirtualEvent.objects.filter(status="Published")
    for ve in published:
        # start_date=strptime(ve.start_date,'%d/%m/%Y')
        today=date.today()
        print(today)
        print(ve.start_date)
        if ve.start_date > today:
            diff=ve.start_date -today
            days=diff.days
            sub=f'TECVICO virtual event (ID: {ve.unique_id})'
            content=_(f'"Dear {ve.top_user}\nHello\nHope you are going well.\nA There are {days} days left until your meeting, if you want to upload a file for this meeting. Go to your dashboard to upload.\nVirtual event title : {ve.title}\nSubmitted date: {ve.created}\nDo not reply to this Email. If you have any questions or concerns, please contact to the Virtual event director through Virtualeventdirector@tecvico.com.\n\nThank you\nSincerely,s\n\nTECVICO Corp\nFor upload file please click:\nhttp://127.0.0.1:8000/virtualevents/presenter?filter=Upload')
            destination=ve.top_user.email
            send_new_email(sub,content,destination)
            description=f'There are {days} days left until your meeting, if you want to upload a file for this meeting. Go to your dashboard to upload.',
            Notification.objects.create(title = f"virtual event (ID: {ve.unique_id})",description =description,
                                            target = ve.top_user,
                                            #link = reverse(reverse_url_name)
                                            )

