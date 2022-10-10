import datetime
import threading

from dashboard.forms import ProjectSocialForm
from dashboard.models import UnSubscriber
from dashboard.utilities import get_project_collaborators, request_or_withdraw_a_project, \
    send_notification_to_supervisor_and_mentors, remove_notification_from_supervisor_and_mentors, \
    user_has_memberprofile, withdraw_legal_profile_from_a_project
from ivc_project.email_sender import send_new_email
from ivc_website.models import Project, ProjectSupervisor


def try_to_change_project_state_to_ongoing(request):
    error_messages = []
    error_is_occurred = False

    project_primary_key = request.POST['ongoing-project-pk']
    selected_project = Project.objects.get(pk=project_primary_key)
    if selected_project.main_supervisor == request.user:

        if selected_project.start_date is None:
            error_messages.append("You have to determine start date before changing to ongoing")
            error_is_occurred = True
        if selected_project.end_date is None:
            error_messages.append("You have to determine end date before changing to ongoing")
            error_is_occurred = True

        if error_is_occurred:
            return error_messages

        if 'send-email' in request.POST:
            social_form = ProjectSocialForm(request.POST)
            if social_form.is_valid():
                slack_workspace = social_form.cleaned_data['slack_workspace_address']
                slack_channel = social_form.cleaned_data['slack_channel_address']
                google_drive = social_form.cleaned_data['google_drive_address']
                skype = social_form.cleaned_data['skype_address']
                supervisor_message = social_form.cleaned_data['supervisor_message']

                a_field_is_entered = slack_workspace is not None or slack_channel is not None \
                                     or google_drive is not None or skype is not None
                if a_field_is_entered:
                    selected_project.slack_workspace_address = slack_workspace
                    selected_project.slack_channel_address = slack_channel
                    selected_project.google_drive_address = google_drive
                    selected_project.skype_address = skype
                    selected_project.supervisor_message = supervisor_message

                    email_subject = f'Project "{selected_project.title}" has started its activity'
                    collaborators = get_project_collaborators(selected_project)
                    for collaborator in collaborators:
                        email_content = f"""Hello, {collaborator.first_name}.
The project "{selected_project.title}" which you are employed as a "{collaborator.memberprofile.position}" has been changed its status to ongoing.

Here are the information provided by the main supervisor:\n"""
                        if slack_workspace:
                            email_content += f'Slack workspace: {slack_workspace}\n'
                        if slack_channel:
                            email_content += f'Slack channel: {slack_channel}\n'
                        if google_drive:
                            email_content += f'Google Drive: {google_drive}\n'
                        if skype:
                            email_content += f'Skype: {skype}\n'
                        if supervisor_message:
                            email_content += f"\nMessage from the main supervisor:\n {supervisor_message}"

                        threading.Thread(target=send_new_email,
                                         args=(email_subject, email_content, collaborator.email)).start()
                else:
                    error_messages.append("You should enter one address at least before sending email")
                    return error_messages

        selected_project.status = 'Ongoing'
        selected_project.save()

        return error_messages


def change_project_state_to_anything_except_ongoing(request):
    project_primary_key = request.POST['project-pk']
    new_status = request.POST['status-change']
    selected_project = Project.objects.get(pk=project_primary_key)
    if selected_project.main_supervisor == request.user:
        selected_project.status = new_status
        selected_project.save()


def delete_project(request):
    project_primary_key = request.POST['data-project-delete']
    selected_project = Project.objects.get(pk=project_primary_key)
    if selected_project.main_supervisor == request.user or request.user.is_superuser:  # if request is valid
        selected_project.is_valid = False
        selected_project.status = "Deleted"
        selected_project.date_added = datetime.datetime(1, 1, 1)
        selected_project.save()


def email_to_subscribed_supervisors(project_primary_key, state, user):
    selected_project = Project.objects.get(pk=project_primary_key)

    if state == "Request":
        email_subject = f"{user.first_name} {user.last_name} wants to be on a project"
        email_content = f"""
{user.first_name} {user.last_name} wants to be on {selected_project.title}

you can either accept or reject by going to the link below:
https://tecvico.com/dashboard/manage/{project_primary_key}

if you want to unsubscribe from receiving these emails for this project, go to the link below:
https://tecvico.com/dashboard/unsubscribe/{project_primary_key}
"""
    elif state == "Withdraw":
        email_subject = f"{user.first_name} {user.last_name} have taken back the request"
        email_content = f"""
{user.first_name} {user.last_name} took back his request from the project {selected_project.title}

if you want to unsubscribe from receiving these emails for this project, go to the link below:
https://tecvico.com/dashboard/unsubscribe/{project_primary_key}
        """
    else:
        return

    for supervisor in ProjectSupervisor.objects.filter(project=selected_project, state='Collaborator'):
        if UnSubscriber.objects.filter(user=supervisor.supervisor, project=selected_project).count() == 0:
            threading.Thread(target=send_new_email, args=(email_subject, email_content,
                                                          supervisor.supervisor.email)).start()

    if selected_project.main_supervisor is not None and UnSubscriber.objects.filter(user=selected_project.main_supervisor, project=selected_project).count() == 0:
        threading.Thread(target=send_new_email, args=(email_subject, email_content,
                                                      selected_project.main_supervisor.email)).start()


def try_to_request_or_withdraw_a_project(request):
    project_primary_key = request.POST['data-project-request']
    apply_as = None
    if 'apply_as' in request.POST:
        apply_as = request.POST['apply_as']
        action = request_or_withdraw_a_project(project_primary_key, request.user, apply_as)
    else:  # if there's not any option, apply based on user position
        if user_has_memberprofile(request.user):
            action = request_or_withdraw_a_project(project_primary_key, request.user,
                                                   request.user.memberprofile.position)
        else:  # withdraw from legal profile
            action, apply_as = withdraw_legal_profile_from_a_project(project_primary_key, request.user)

    """FOR NOTIFICATION"""
    if action == "REQUEST":
        if apply_as:
            send_notification_to_supervisor_and_mentors(project_primary_key, request.user,
                                                        apply_as)
        else:
            send_notification_to_supervisor_and_mentors(project_primary_key, request.user,
                                                        request.user.memberprofile.position)
        email_to_subscribed_supervisors(project_primary_key, "Request", request.user)
    if action == "WITHDRAW":
        if apply_as:
            remove_notification_from_supervisor_and_mentors(project_primary_key, request.user,
                                                            apply_as)
        else:
            remove_notification_from_supervisor_and_mentors(project_primary_key, request.user,
                                                            request.user.memberprofile.position)
        email_to_subscribed_supervisors(project_primary_key, "Withdraw", request.user)
