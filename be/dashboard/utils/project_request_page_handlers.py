from django.db.models import Q
from django.urls import reverse

from dashboard.utilities import send_notification, get_collaborated_projects, get_all_collaborated_projects, \
    user_has_memberprofile
from ivc_website.models import ProjectMentor, ProjectSupervisor, Project, ProjectMember, ProjectLearner, ProjectContract
from log.models import Log


def accept_requested_collaboration(request):
    """
    In case when a user accepts to be a part of a project. first it becomes a project collaborator and then
    it notifies to his superior.
    """
    # -- previous version
    # selected_primary_key = request.POST['accept-project-pk']
    # selected_project = Project.objects.get(pk=selected_primary_key)
    # if request.user.memberprofile.position == "Supervisor":
    #     selected_project_supervisor = \
    #         selected_project.projectsupervisor_set.filter(supervisor=request.user.memberprofile)[0]
    #     selected_project_supervisor.accepted = True
    #
    #     # set priority to last (add him to the last of the list)
    #     last_priority = ProjectSupervisor.objects.filter(project=selected_project).last().priority
    #     selected_project_supervisor.priority = last_priority + 1
    #
    #     selected_project_supervisor.save()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} accepted your request',
    #                       selected_project.main_supervisor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    #
    # elif request.user.memberprofile.position == "Mentor":
    #     selected_project_mentor = selected_project.projectmentor_set.filter(mentor=request.user.memberprofile)[
    #         0]
    #     selected_project_mentor.accepted = True
    #
    #     # set priority to last (add him to the last of the list)
    #     last_priority = ProjectMentor.objects.filter(project=selected_project).last().priority
    #     selected_project_mentor.priority = last_priority + 1
    #
    #     selected_project_mentor.save()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} accepted your request',
    #                       selected_project_mentor.project_supervisor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    #
    # elif request.user.memberprofile.position == "Member":
    #     selected_project_member = selected_project.projectmember_set.filter(member=request.user.memberprofile)[
    #         0]
    #     selected_project_member.accepted = True
    #
    #     # set priority to last (add him to the last of the list)
    #     last_priority = ProjectMember.objects.filter(project=selected_project).last().priority
    #     selected_project_member.priority = last_priority + 1
    #
    #     selected_project_member.save()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} accepted your request',
    #                       selected_project_member.project_mentor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    # else:
    #     selected_project_learner = selected_project.projectlearner_set.get(learner=request.user.memberprofile)
    #     selected_project_learner.accepted = True
    #
    #     # set priority to last (add him to the last of the list)
    #     last_priority = ProjectLearner.objects.filter(project=selected_project).last().priority
    #     selected_project_learner.priority = last_priority + 1
    #
    #     selected_project_learner.save()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} accepted your request',
    #                       selected_project_learner.project_mentor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    selected_primary_key = request.POST['accept-project-pk']
    selected_collaboration_type = request.POST['accept-collaboration-type']
    if selected_collaboration_type == "Supervisor":
        selected_project_supervisor = ProjectSupervisor.objects.get(pk=selected_primary_key)
        selected_project_supervisor.state = "Waiting For Signature"

        # set priority to last (add him to the last of the list)
        if ProjectSupervisor.objects.filter(project=selected_project_supervisor.project).count() == 0:
            last_priority = -1
        else:
            last_priority = ProjectSupervisor.objects.filter(project=selected_project_supervisor.project).last().priority
        selected_project_supervisor.priority = last_priority + 1

        Log(user=selected_project_supervisor.supervisor,
            log=f'Has become a supervisor in project "{selected_project_supervisor.project}"').save()
        selected_project_supervisor.save()

        """
        Validate Contract
        """
        invalid_contract_exists = ProjectContract.objects.filter(project=selected_project_supervisor.project,
                                                                 user=selected_project_supervisor.supervisor,
                                                                 valid=False).count()
        if invalid_contract_exists:
            contract = ProjectContract.objects.get(project=selected_project_supervisor.project,
                                                   user=selected_project_supervisor.supervisor, valid=False)
            contract.valid = True
            contract.save()

        send_notification(selected_project_supervisor.project.title,
                          f'{request.user.first_name} {request.user.last_name} accepted your request',
                          selected_project_supervisor.project.main_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_supervisor.project.pk]))
    elif selected_collaboration_type == "Mentor":
        selected_project_mentor = ProjectMentor.objects.get(pk=selected_primary_key)
        selected_project_mentor.state = "Waiting For Signature"
        Log(user=selected_project_mentor.mentor,
            log=f'Has become a mentor in project "{selected_project_mentor.project}"').save()

        # set priority to last (add him to the last of the list)
        if ProjectMentor.objects.filter(project=selected_project_mentor.project).count() == 0:
            last_priority = -1
        else:
            last_priority = ProjectMentor.objects.filter(project=selected_project_mentor.project).last().priority
        selected_project_mentor.priority = last_priority + 1

        selected_project_mentor.save()

        """
        Validate Contract
        """
        invalid_contract_exists = ProjectContract.objects.filter(project=selected_project_mentor.project,
                                                                 user=selected_project_mentor.mentor,
                                                                 valid=False).count()
        if invalid_contract_exists:
            contract = ProjectContract.objects.get(project=selected_project_mentor.project,
                                                   user=selected_project_mentor.mentor, valid=False)
            contract.valid = True
            contract.save()

        send_notification(selected_project_mentor.project.title,
                          f'{request.user.first_name} {request.user.last_name} accepted your request',
                          selected_project_mentor.project_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_mentor.project.pk]))
    elif selected_collaboration_type == "Member":
        selected_project_member = ProjectMember.objects.get(pk=selected_primary_key)
        selected_project_member.state = "Waiting For Signature"
        Log(user=selected_project_member.member,
            log=f'Has become a member in project "{selected_project_member.project}"').save()

        # set priority to last (add him to the last of the list)
        if ProjectMember.objects.filter(project=selected_project_member.project).count() == 0:
            last_priority = -1
        else:
            last_priority = ProjectMember.objects.filter(project=selected_project_member.project).last().priority
        selected_project_member.priority = last_priority + 1

        selected_project_member.save()

        """
        Validate Contract
        """
        invalid_contract_exists = ProjectContract.objects.filter(project=selected_project_member.project,
                                                                 user=selected_project_member.member,
                                                                 valid=False).count()
        if invalid_contract_exists:
            contract = ProjectContract.objects.get(project=selected_project_member.project,
                                                   user=selected_project_member.member, valid=False)
            contract.valid = True
            contract.save()

        send_notification(selected_project_member.project.title,
                          f'{request.user.first_name} {request.user.last_name} accepted your request',
                          selected_project_member.project_mentor,
                          reverse("dashboard-project-manage-page", args=[selected_project_member.project.pk]))
    elif selected_collaboration_type == "Learner":
        selected_project_learner = ProjectLearner.objects.get(pk=selected_primary_key)
        selected_project_learner.state = "Waiting For Signature"

        Log(user=selected_project_learner.learner,
            log=f'Has become a learner in project "{selected_project_learner.project}"').save()

        # set priority to last (add him to the last of the list)
        if ProjectLearner.objects.filter(project=selected_project_learner.project).count() == 0:
            last_priority = -1
        else:
            last_priority = ProjectLearner.objects.filter(project=selected_project_learner.project).last().priority
        selected_project_learner.priority = last_priority + 1

        selected_project_learner.save()

        """
        Validate Contract
        """
        invalid_contract_exists = ProjectContract.objects.filter(project=selected_project_learner.project,
                                                                 user=selected_project_learner.learner,
                                                                 valid=False).count()
        if invalid_contract_exists:
            contract = ProjectContract.objects.get(project=selected_project_learner.project,
                                                   user=selected_project_learner.learner, valid=False)
            contract.valid = True
            contract.save()

        send_notification(selected_project_learner.project.title,
                          f'{request.user.first_name} {request.user.last_name} accepted your request',
                          selected_project_learner.project.main_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_learner.project.pk]))


def accept_industrial_requested_collaboration(request):
    selected_primary_key = request.POST['accept-project-pk']
    selected_collaboration_type = request.POST['accept-collaboration-type']

    if selected_collaboration_type == "Supervisor":
        selected_project_collaborator = ProjectSupervisor.objects.get(pk=selected_primary_key)
        ProjectContract(project=selected_project_collaborator.project,
                        user=selected_project_collaborator.supervisor, contract_type='Collaborator').save()
    elif selected_collaboration_type == "Mentor":
        selected_project_collaborator = ProjectMentor.objects.get(pk=selected_primary_key)
        ProjectContract(project=selected_project_collaborator.project,
                        user=selected_project_collaborator.mentor, contract_type='Collaborator').save()
    elif selected_collaboration_type == "Member":
        selected_project_collaborator = ProjectMember.objects.get(pk=selected_primary_key)
        ProjectContract(project=selected_project_collaborator.project,
                        user=selected_project_collaborator.member, contract_type='Collaborator').save()
    elif selected_collaboration_type == "Learner":
        selected_project_collaborator = ProjectLearner.objects.get(pk=selected_primary_key)
        ProjectContract(project=selected_project_collaborator.project,
                        user=selected_project_collaborator.learner, contract_type='Collaborator').save()
    else:
        selected_project_collaborator = None

    if selected_project_collaborator is not None:
        selected_project_collaborator.state = "Waiting For Signature"
        selected_project_collaborator.save()

        send_notification(selected_project_collaborator.project.title,
                          f'{request.user.first_name} {request.user.last_name} accepted your request, we have to wait for his signature now',
                          selected_project_collaborator.project.main_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_collaborator.project.pk]))


def reject_requested_collaboration(request):
    """
        In case when a user rejects to be a part of a project. first it becomes a project collaborator and then
        it notifies to his superior.
    """
    # -- previous version
    # selected_primary_key = request.POST['reject-project-pk']
    # selected_project = Project.objects.get(pk=selected_primary_key)
    # if request.user.memberprofile.position == "Supervisor":
    #     selected_project_supervisor = \
    #         selected_project.projectsupervisor_set.filter(supervisor=request.user.memberprofile)[0]
    #     selected_project_supervisor.delete()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} rejected your request',
    #                       selected_project.main_supervisor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    #
    # elif request.user.memberprofile.position == "Mentor":
    #     selected_project_mentor = selected_project.projectmentor_set.filter(mentor=request.user.memberprofile)[
    #         0]
    #     selected_project_mentor.delete()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} rejected your request',
    #                       selected_project_mentor.project_supervisor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    # elif request.user.memberprofile.position == "Member":
    #     selected_project_member = selected_project.projectmember_set.filter(member=request.user.memberprofile)[
    #         0]
    #     selected_project_member.delete()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} rejected your request',
    #                       selected_project_member.project_mentor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    # else:
    #     selected_project_learner = selected_project.projectlearner_set.get(learner=request.user.memberprofile)
    #     selected_project_learner.delete()
    #     send_notification(selected_project.title,
    #                       f'{request.user.first_name} {request.user.last_name} rejected your request',
    #                       selected_project_learner.project_mentor,
    #                       reverse("dashboard-project-manage-page", args=[selected_project.pk]))
    selected_primary_key = request.POST['reject-project-pk']
    selected_collaboration_type = request.POST['reject-collaboration-type']
    if selected_collaboration_type == "Supervisor":
        selected_project_supervisor = ProjectSupervisor.objects.get(pk=selected_primary_key)
        selected_project_supervisor.delete()
        send_notification(selected_project_supervisor.project.title,
                          f'{request.user.first_name} {request.user.last_name} rejected your request',
                          selected_project_supervisor.project.main_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_supervisor.project.pk]))
    if selected_collaboration_type == "Mentor":
        selected_project_mentor = ProjectMentor.objects.get(pk=selected_primary_key)
        selected_project_mentor.delete()
        send_notification(selected_project_mentor.project.title,
                          f'{request.user.first_name} {request.user.last_name} rejected your request',
                          selected_project_mentor.project_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_mentor.project.pk]))
    if selected_collaboration_type == "Member":
        selected_project_member = ProjectMember.objects.get(pk=selected_primary_key)
        selected_project_member.delete()
        send_notification(selected_project_member.project.title,
                          f'{request.user.first_name} {request.user.last_name} rejected your request',
                          selected_project_member.project.main_supervisor,
                          reverse("dashboard-project-manage-page", args=[selected_project_member.project.pk]))
    if selected_collaboration_type == "Learner":
        selected_project_learner = ProjectLearner.objects.get(pk=selected_primary_key)
        selected_project_learner.delete()
        send_notification(selected_project_learner.project.title,
                          f'{request.user.first_name} {request.user.last_name} rejected your request',
                          selected_project_learner.project_mentor,
                          reverse("dashboard-project-manage-page", args=[selected_project_learner.project.pk]))


def get_users_who_want_to_be_part_of_my_projects(request):
    # -- previous version
    # collaborated_projects = get_all_collaborated_projects(request.user)
    # request_dictionary = {}
    # if request.user.memberprofile.position == "Mentor":
    #     for collaborated_project in collaborated_projects:
    #         project_learners = collaborated_project.projectlearner_set.filter(pending=True, accepted=True)
    #         project_members = collaborated_project.projectmember_set.filter(pending=True, accepted=True)
    #         request_dictionary[collaborated_project] = {
    #             "members": project_members,
    #             "learners": project_learners
    #         }
    #
    # elif request.user.memberprofile.position == "Supervisor":
    #     for collaborated_project in collaborated_projects:
    #         project_learners = collaborated_project.projectlearner_set.filter(pending=True, accepted=True)
    #         project_members = collaborated_project.projectmember_set.filter(pending=True, accepted=True)
    #         project_mentors = collaborated_project.projectmentor_set.filter(pending=True, accepted=True)
    #         request_dictionary[collaborated_project] = {
    #             'members': project_members,
    #             'mentors': project_mentors,
    #             'learners': project_learners,
    #         }
    #
    #         if collaborated_project.main_supervisor == request.user.memberprofile:
    #             project_supervisors = collaborated_project.projectsupervisor_set.filter(pending=True, accepted=True)
    #             request_dictionary[collaborated_project]['supervisors'] = project_supervisors

    return {
        "project_supervisors": ProjectSupervisor.objects.filter(Q(state="Accepted Pending",
                                                                  project__main_supervisor=request.user,
                                                                  project__project_type="Research")
                                                                & ~Q(project__status="Deleted")).distinct(),
        "project_mentors": ProjectMentor.objects.filter((Q(state="Accepted Pending",
                                                           project__main_supervisor=request.user,
                                                           project__project_type="Research") |
                                                         Q(state="Accepted Pending",
                                                           project__projectsupervisor__supervisor=request.user,
                                                           project__project_type="Research"))
                                                        & ~Q(project__status="Deleted")).distinct(),
        "project_members": ProjectMember.objects.filter((Q(state="Accepted Pending",
                                                           project__main_supervisor=request.user,
                                                           project__project_type="Research") |
                                                         Q(state="Accepted Pending",
                                                           project__projectsupervisor__supervisor=request.user,
                                                           project__project_type="Research") |
                                                         Q(state="Accepted Pending",
                                                           project__projectmentor__mentor=request.user,
                                                           project__project_type="Research"))
                                                        & ~Q(project__status="Deleted")).distinct(),
        "project_learners": ProjectLearner.objects.filter((Q(state="Accepted Pending",
                                                             project__main_supervisor=request.user,
                                                             project__project_type="Research") |
                                                           Q(state="Accepted Pending",
                                                             project__projectsupervisor__supervisor=request.user,
                                                             project__project_type="Research") |
                                                           Q(state="Accepted Pending",
                                                             project__projectmentor__mentor=request.user,
                                                             project__project_type="Research"))
                                                          & ~Q(project__status="Deleted")).distinct(),
    }


def get_users_who_want_to_be_part_of_my_projects_with_contract(request, project_type):
    return {
        "project_supervisors": ProjectSupervisor.objects.filter(Q(state="Accepted Pending",
                                                                  project__main_supervisor=request.user,
                                                                  project__project_type=project_type) |
                                                                Q(state="Accepted Pending",
                                                                  project__main_supervisor=None,
                                                                  project__expert=request.user,
                                                                  project__project_type=project_type))
            .exclude(Q(project__expert=request.user, project__projectsupervisor__state='Waiting for Admin Acceptance')
                     | Q(project__expert=request.user, project__projectsupervisor__state='Waiting For Acceptance')
                     | Q(project__expert=request.user, project__projectsupervisor__state='Waiting For Signature')
                     | Q(project__expert=request.user, project__projectsupervisor__state='Inspecting Signature'))
            .distinct(),
        "project_mentors": ProjectMentor.objects.filter(state="Accepted Pending",
                                                        project__main_supervisor=request.user,
                                                        project__project_type=project_type).distinct(),
        "project_members": ProjectMember.objects.filter(state="Accepted Pending",
                                                        project__main_supervisor=request.user,
                                                        project__project_type=project_type).distinct(),
        "project_learners": ProjectLearner.objects.filter(state="Accepted Pending",
                                                          project__main_supervisor=request.user,
                                                          project__project_type=project_type).distinct(),
    }


def get_projects_that_want_me_to_be_part_of_them(request):
    # --- previous version
    # if request.user.memberprofile.position == "Mentor":
    #     return ProjectMentor.objects.filter(mentor=request.user,
    #                                         pending=False, accepted=False)
    # elif request.user.memberprofile.position == "Supervisor":
    #     return ProjectSupervisor.objects.filter(supervisor=request.user,
    #                                                                      pending=False, accepted=False)
    # elif request.user.memberprofile.position == "Member":
    #     return ProjectMember.objects.filter(member=request.user, pending=False, accepted=False)
    # else:
    #     return ProjectLearner.objects.filter(learner=request.user, pending=False, accepted=False)
    return [ProjectSupervisor.objects.filter(Q(supervisor=request.user, state="Waiting For Acceptance",
                                               project__project_type="Research") & ~Q(project__status="Deleted")),
            ProjectMentor.objects.filter(Q(mentor=request.user, state="Waiting For Acceptance",
                                           project__project_type="Research") & ~Q(project__status="Deleted")),
            ProjectMember.objects.filter(Q(member=request.user, state="Waiting For Acceptance",
                                           project__project_type="Research") & ~Q(project__status="Deleted")),
            ProjectLearner.objects.filter(Q(learner=request.user, state="Waiting For Acceptance",
                                            project__project_type="Research") & ~Q(project__status="Deleted"))]


def get_projects_with_contract_that_want_me_to_be_part_of_them(request, project_type):
    return [ProjectSupervisor.objects.filter(Q(supervisor=request.user, state="Waiting For Acceptance",
                                               project__project_type=project_type) & ~Q(project__status="Deleted")),
            ProjectMentor.objects.filter(Q(mentor=request.user, state="Waiting For Acceptance",
                                           project__project_type=project_type) & ~Q(project__status="Deleted")),
            ProjectMember.objects.filter(Q(member=request.user, state="Waiting For Acceptance",
                                           project__project_type=project_type) & ~Q(project__status="Deleted")),
            ProjectLearner.objects.filter(Q(learner=request.user, state="Waiting For Acceptance",
                                            project__project_type=project_type) & ~Q(project__status="Deleted"))]


def get_projects_that_collaborator_has_signed_the_signature(request, project_type):
    query_condition = Q(main_supervisor=request.user, projectsupervisor__state="Inspecting Signature",
                        project_type=project_type) | \
                      Q(main_supervisor=request.user, projectmentor__state="Inspecting Signature",
                        project_type=project_type) | \
                      Q(main_supervisor=request.user, projectmember__state="Inspecting Signature",
                        project_type=project_type) | \
                      Q(main_supervisor=request.user, projectlearner__state="Inspecting Signature",
                        project_type=project_type)
    if request.user.is_superuser:
        query_condition |= Q(main_supervisor=None, projectsupervisor__state="Inspecting Signature",
                             project_type=project_type)

    query_condition &= ~Q(status="Deleted")
    return Project.objects.filter(query_condition).distinct()


def get_project_contracts(request, project_type):
    return ProjectContract.objects.filter((Q(user=request.user, reply_has_been_sent=False,
                                             project__project_type=project_type, contract_type='Collaborator') |
                                           Q(user=request.user, reply_has_been_sent=False,
                                             project__project_type=project_type,
                                             ready_to_be_printed=True, contract_type='Ownership'))
                                          & ~Q(project__status="Deleted")).distinct()
