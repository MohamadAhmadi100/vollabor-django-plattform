import threading

from django.urls import reverse

from dashboard.models import ContractItem, ProjectContractItem
from dashboard.utilities import send_notification, is_user_collaborator, inform_the_superusers, \
    is_user_inside_the_project
from ivc_project.email_sender import send_new_email
from ivc_website.models import ProjectContractReply, Project, ProjectContract, ProjectSupervisor, ProjectMentor, \
    ProjectMember, ProjectLearner


def save_contract_response(request, selected_project, project_contract_reply_form, contract, contract_type):
    project_contract_reply = project_contract_reply_form.save(commit=False)
    project_contract_reply.user = request.user
    project_contract_reply.project = selected_project
    project_contract_reply.contract_type = contract_type

    ProjectContractReply.objects.filter(project=selected_project, user=request.user,
                                        contract_type=contract_type).delete()  # delete
    # previous one if exits

    project_contract_reply.save()
    contract.reply_has_been_sent = True
    contract.save()

    if selected_project.status == "Waiting For Signature":
        selected_project.status = "Inspecting Signature"
        selected_project.save()


def change_state_after_contract_if_necessary(request, selected_project):
    project_collaborator = None
    if ProjectSupervisor.objects.filter(project=selected_project, supervisor=request.user).count() == 1:
        project_collaborator = ProjectSupervisor.objects.get(project=selected_project, supervisor=request.user)

    if ProjectMentor.objects.filter(project=selected_project, mentor=request.user).count() == 1:
        project_collaborator = ProjectMentor.objects.get(project=selected_project, mentor=request.user)

    if ProjectMember.objects.filter(project=selected_project, member=request.user).count() == 1:
        project_collaborator = ProjectMember.objects.get(project=selected_project, member=request.user)

    if ProjectLearner.objects.filter(project=selected_project, learner=request.user).count() == 1:
        project_collaborator = ProjectLearner.objects.get(project=selected_project, learner=request.user)

    if project_collaborator is not None:
        project_collaborator.state = "Inspecting Signature"
        project_collaborator.save()


def inform_superuser_if_necessary(request, selected_project):
    collaborator_is_supervisor = ProjectSupervisor.objects.filter(project=selected_project,
                                                                  supervisor=request.user).count() == 1
    if selected_project.main_supervisor is None and collaborator_is_supervisor:
        inform_the_superusers(selected_project, "Main supervisor accepted the project and signed the contract",
                              reverse('dashboard-project-manage-page', args=[selected_project.pk]))


def send_contract_to_owner_and_wait_for_signature(selected_project):
    # remove previous ones if exists (It shouldn't!)
    ProjectContract.objects.filter(project=selected_project, user=selected_project.owner,
                                   contract_type='Ownership').delete()

    ProjectContract(project=selected_project, user=selected_project.owner, contract_type='Ownership').save()
    for contract_item in ContractItem.objects.all():
        ProjectContractItem(project=selected_project, item=contract_item.item, item_type=contract_item.item_type,
                            from_item='Tecvico').save()

    selected_project.status = "Waiting For Signature"
    selected_project.save()

    send_notification(selected_project.title, "For the project you defined, a contract has been provided. Please "
                                              "read the letter thoroughly and sign it.",
                      selected_project.owner, reverse('project-contract-page',
                                                      args=[selected_project.pk, 'Ownership']))

    email_subject = "A contract has been provided for the project you have defined."
    email_content = f"""
For the project you defined, a contract has been provided. Please read the letter thoroughly and sign it.

Contract Link: https://tecvico.com/dashboard/project-contract/{selected_project.pk}

Regards,
Tecvico team
    """
    threading.Thread(target=send_new_email,
                     args=(email_subject, email_content, selected_project.owner.email)).start()


def accept_contract(request):
    selected_row_primary_key = request.POST['contract-accept-pk']
    selected_project = Project.objects.get(pk=selected_row_primary_key)

    selected_project.is_valid = True
    selected_project.status = "New"
    selected_project.save()

    send_notification(selected_project.title, "The project you defined got accepted",
                      selected_project.owner, reverse('dashboard-projects-page',
                                                      args=[selected_project.project_type]))

    email_subject = "A contract has been provided for the project you have defined."
    email_content = f"""
The project you defined got accepted.

Your project will be managed by a coordinator from one of the branches.

Projects Page: https://www.tecvico.com/dashboard/projects/Industrial

Regards,
Tecvico team
    """

    threading.Thread(target=send_new_email, args=(email_subject, email_content, selected_project.owner.email)).start()


def is_user_eligible_to_send_contract(user, project, contract_type):
    if contract_type == "Collaborator":
        if is_user_collaborator(project, user):
            return False
        else:
            if is_user_inside_the_project(project, user):
                return True
            else:
                return False
    else:
        if project.status != 'Waiting For Signature' and user == project.owner and project.project_type == "Industrial":
            return False
        else:
            return True
