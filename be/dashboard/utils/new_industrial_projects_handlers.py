import threading

from django.contrib.auth.models import User
from django.core import serializers
from django.db.models import Q
from django.urls import reverse

from dashboard.utilities import send_notification
from ivc_project.email_sender import send_new_email
from ivc_website.models import Project, ProjectSupervisor, ProjectContract, ProjectContractReply, ProjectArea, \
    IndustrialArea, ProjectAreaOpinion, AreaReason
from log.models import Log


def accept_industrial_project_and_email_the_owner_and_corresponding_expert(selected_project):
    selected_project.status = "New"
    selected_project.is_valid = True
    selected_project.save()

    # Owner
    send_notification(selected_project.title, "The project you defined has been accepted",
                      selected_project.owner, reverse('dashboard-projects-page', args=[selected_project.project_type]))
    email_subject = "The project you defined has been accepted"
    email_content = f"""Hello, {selected_project.owner.first_name}.
The project you proposed is approved. Our members are currently applying to work on your project, and once a team is formed, we will notify you.

Regards,
Tecvico Team
    """
    threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_project.owner.email)).start()

    # Corresponding expert
    send_notification(selected_project.title, "The project state has become NEW. please select reviewers.",
                      selected_project.expert, reverse('corresponding-expert-page'))
    email_subject = "The project state has become NEW. please select reviewers."
    email_content = f"Hello, {selected_project.expert.first_name}.\n" \
                    f'The project "{selected_project.title}" state has become NEW.\n' \
                    "Now you have to select reviewers.\n" \
                    "\n" \
                    "Regards,\n" \
                    "Tecvico Team"
    threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_project.expert.email)).start()


def accept_main_supervisor_and_send_contract(technical_manager, project_supervisor):
    # delete previous contracts if exist
    ProjectContract.objects.filter(project=project_supervisor.project, user=project_supervisor.supervisor,
                                   contract_type='Collaborator').delete()
    ProjectContractReply.objects.filter(project=project_supervisor.project, user=project_supervisor.supervisor,
                                        contract_type='Collaborator').delete()

    ProjectContract(project=project_supervisor.project, user=project_supervisor.supervisor, contract_type='Collaborator').save()
    project_supervisor.state = 'Waiting For Signature'
    project_supervisor.save()

    send_notification(project_supervisor.project.title, "A Contract has been sent for you."
                                              "read the letter thoroughly and sign it.",
                      project_supervisor.supervisor,
                      reverse('project-contract-page', args=[project_supervisor.project.pk, 'Collaborator']))

    Log(user=technical_manager, log=f"TECHNICAL MANAGER: accepted {project_supervisor.supervisor.first_name}"
                                    f" {project_supervisor.supervisor.last_name} on {project_supervisor.project.title}.").save()


def reject_main_supervisor_and_inform_expert(technical_manager, project_supervisor, reject_reason):
    project_supervisor.state = "Accepted Pending"
    project_supervisor.save()

    send_notification("Main supervisor is rejected by the technical manager",
                      f"Project: {project_supervisor.project.title}\n"
                      f"<b>Reason:</b> {reject_reason}", project_supervisor.project.expert,
                      reverse('corresponding-expert-page'))
    Log(user=technical_manager, log=f"TECHNICAL MANAGER: rejected {project_supervisor.supervisor.first_name}"
                               f" {project_supervisor.supervisor.last_name} from {project_supervisor.project.title}.\n"
                               f"Reason: {reject_reason}").save()


def approve_the_project(request, selected_project):
    for key in request.POST:
        if 'checked' in key:
            area = key.split('-')[1]
            project_area = ProjectArea.objects.get(project=selected_project, area=area)
            project_area.expert = request.user
            project_area.save()


def get_new_industrial_projects(user):
    return Project.objects.filter(Q(projectarea__expert=user) & ~Q(status="Rejected") & ~Q(is_valid=True)).distinct()


def delete_unconfirmed_areas(selected_project):
    unconfirmed_project_areas = selected_project.projectarea_set.filter(area__confirmed=False)
    for unconfirmed_project_area in unconfirmed_project_areas:
        industrial_area = unconfirmed_project_area.area
        industrial_area.delete()


def reject_the_project_and_inform_the_owner(selected_project, project_reason):
    if selected_project.project_type == "Industrial":
        delete_unconfirmed_areas(selected_project)

    selected_project.status = "Rejected"
    selected_project.reject_reason = project_reason
    selected_project.save()

    send_notification(selected_project.title,
                      f"The project you defined has been rejected. Reason: {project_reason}",
                      selected_project.owner, reverse('dashboard-projects-page',
                                                      args=[selected_project.project_type]))

    email_subject = "The project you defined has been rejected."
    email_content = f"""
The project you defined has been rejected.


Here is the reason:
{project_reason}

Regards,
Tecvico team
        """
    threading.Thread(target=send_new_email,
                     args=(email_subject, email_content, selected_project.owner.email)).start()


def get_project_areas(project_pk):
    project = Project.objects.get(pk=project_pk)
    project_areas = ProjectArea.objects.filter(project=project)
    return serializers.serialize('json', list(project_areas), fields=['area', 'expert'])


def add_area_to_project(new_area, project_pk):
    project = Project.objects.get(pk=project_pk)
    ProjectArea(project=project, area=new_area).save()


def reject_industrial_area(request, selected_project):
    area_pk = request.POST.get('reject-area')
    industrial_area = IndustrialArea.objects.get(pk=area_pk)

    is_already_confirmed = industrial_area.confirmed
    if is_already_confirmed:
        return False, "Area is already accepted"

    if 'manual-reject-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-reject-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=industrial_area, action='reject',
                           reason=reason).save()
        industrial_area.delete()
    if 'reject-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('reject-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=industrial_area, action='reject',
                           reason=reason_str).save()
        industrial_area.delete()

    return True, "Area has been rejected successfully"


def reject_project_area(request, selected_project):
    area_pk = request.POST.get('reject-project-area')
    project_area = ProjectArea.objects.get(pk=area_pk)

    if 'manual-reject-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-reject-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='reject',
                           reason=reason).save()
        if project_area.action == "add":
            project_area.delete()
        else:
            project_area.is_confirmed = True
            project_area.save()
    if 'reject-project-area-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('reject-project-area-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='reject',
                           reason=reason_str).save()
        if project_area.action == "add":
            project_area.delete()
        else:
            project_area.is_confirmed = True
            project_area.save()

    return True, "Area has been rejected successfully"


def accept_industrial_area(request, selected_project):
    area_pk = request.POST.get('accept-area')
    industrial_area = IndustrialArea.objects.get(pk=area_pk)

    is_already_confirmed = industrial_area.confirmed
    if is_already_confirmed:
        return False, "Area is already accepted"

    if 'manual-accept-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-accept-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=industrial_area, action='accept',
                           reason=reason).save()
        industrial_area.confirmed = True
        industrial_area.save()
    if 'accept-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('accept-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=industrial_area, action='accept',
                           reason=reason_str).save()
        industrial_area.confirmed = True
        industrial_area.save()

    return True, "Area has been accepted successfully"


def accept_project_area(request, selected_project):
    area_pk = request.POST.get('accept-project-area')
    project_area = ProjectArea.objects.get(pk=area_pk)

    if 'manual-accept-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-accept-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='accept',
                           reason=reason).save()
        if project_area.action == "add":
            project_area.is_confirmed = True
            project_area.save()
        else:
            project_area.delete()
    if 'accept-project-area-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('accept-project-area-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='accept',
                           reason=reason_str).save()
        if project_area.action == "add":
            project_area.is_confirmed = True
            project_area.save()
        else:
            project_area.delete()

    return True, "Area has been accepted successfully"


def remove_project_area(request, selected_project, user_is_project_expert):
    area_pk = request.POST.get('remove-area')
    project_area = ProjectArea.objects.get(pk=area_pk)
    if 'manual-remove-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-remove-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='remove',
                           reason=reason).save()

    if 'remove-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('remove-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=project_area.area, action='remove',
                           reason=reason_str).save()

    if user_is_project_expert:
        project_area.is_confirmed = False
        project_area.action = 'remove'
        project_area.save()

        technical_managers = User.objects.filter(memberprofile__is_technical_manager=True)
        for technical_manager in technical_managers:
            send_notification(title="An area is suggested to be removed",
                              description=f"Expert on project {selected_project.title} wants to remove an area."
                                          f" please verify that.", target=technical_manager,
                              link=reverse('dashboard-project-view-page', args=[selected_project.pk]))
    else:
        project_area.delete()

    return True, "Project Area has been removed successfully"


def add_industrial_area_to_project(request, selected_project, user_is_project_expert):
    suggested_industrial_area = request.POST.get('add-industrial-area').strip().capitalize()
    already_exists = IndustrialArea.objects.filter(area=suggested_industrial_area).count() > 0
    if already_exists:
        the_industrial_area = IndustrialArea.objects.get(area=suggested_industrial_area)
        if not the_industrial_area.confirmed:
            the_industrial_area.confirmed = True
            the_industrial_area.save()
    else:  # create one
        the_industrial_area = IndustrialArea(area=suggested_industrial_area, confirmed=True)
        the_industrial_area.save()

    project_area_does_not_exist = ProjectArea.objects.filter(project=selected_project, area=the_industrial_area).count() == 0
    if project_area_does_not_exist:
        if user_is_project_expert:
            ProjectArea(project=selected_project, area=the_industrial_area, is_confirmed=False, action='add').save()

            technical_managers = User.objects.filter(memberprofile__is_technical_manager=True)
            for technical_manager in technical_managers:
                send_notification(title="A new area is suggested to be added",
                                  description=f"Expert on project {selected_project.title} suggested a new area."
                                              f" please verify that.", target=technical_manager,
                                  link=reverse('dashboard-project-view-page', args=[selected_project.pk]))
        else:
            ProjectArea(project=selected_project, area=the_industrial_area).save()
    else:
        return False, "This area is already assigned to the project areas (Just look at the Project areas below to " \
                      "see that) "

    # REASON
    if 'manual-add-reason' in request.POST:  # Manual reason
        reason = request.POST.get('manual-add-reason')
        ProjectAreaOpinion(user=request.user, project=selected_project, area=suggested_industrial_area, action='add',
                           reason=reason).save()
    if 'add-reason' in request.POST:  # Reason from template
        reason_pks = request.POST.getlist('add-reason')
        reasons = AreaReason.objects.filter(pk__in=reason_pks)
        reason_str = ""
        for reason in reasons:
            reason_str += f"{reason.reason}. "
        reason_str = reason_str[:-2]

        ProjectAreaOpinion(user=request.user, project=selected_project, area=suggested_industrial_area, action='accept',
                           reason=reason_str).save()

    return True, 'Area is added to the project successfully'
