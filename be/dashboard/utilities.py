import datetime
import threading

from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from django.urls import reverse

from coin.util import get_project_required_responsibility_fee, increase_user_balance, decrease_user_balance
from ivc_project.email_sender import send_new_email
from ivc_website.models import ProjectContract, ProjectContractReply
from competition.models import CompetitionManager
from log.models import Log
from users.models import MemberProfile
from .models import Notification, ProposalOpinion
from itertools import chain

from .utils.html_info_utils import *
from .utils.html_info_utils import _get_requested_projects_length, _get_new_projects_length, \
    _get_pending_projects_length, _get_ongoing_projects_length, _get_done_projects_length, _get_on_hold_projects_length


def get_user_info_in_html(user):
    if not user_has_memberprofile(user):
        user_image = user.legalprofile.image.url
        sub_header = user.legalprofile.company_name
        sub_header2 = user.legalprofile.work_area
    else:
        user_image = user.memberprofile.image.url

        sub_header = user.memberprofile.field_of_study
        sub_header2 = user.memberprofile.degree

    requested_projects_length = _get_requested_projects_length(user)
    new_projects_length = _get_new_projects_length(user)
    pending_projects_length = _get_pending_projects_length(user)
    ongoing_projects_length = _get_ongoing_projects_length(user)
    on_hold_projects_length = _get_on_hold_projects_length(user)
    done_projects_length = _get_done_projects_length(user)

    html_response = f"""
<div class="container">
    <div class="row">
        <img alt="image" class="m-1 mx-auto" src="{user_image}" style="width:180px;height:180px">
    </div>
    <div class="row mb-2">
        <div class="mx-auto"><span class="h5">{user.first_name} {user.last_name}</span> </br>
         {sub_header} </br> {sub_header2}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-warning">Requested</span> Projects: </strong> {requested_projects_length}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-secondary">New</span> Projects: </strong> {new_projects_length}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-info">Pending</span> Projects: </strong> {pending_projects_length}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-primary">Ongoing</span> Projects: </strong> {ongoing_projects_length}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-danger">On Hold</span> Projects: </strong> {on_hold_projects_length}</div>
    </div>
    <div class="row">
        <div><strong><span class="text-success">Done</span> Projects: </strong> {done_projects_length}</div>
    </div>
</div>
    """

    return html_response


def get_collaborators(user_profile):
    collaborated_projects = get_all_collaborated_projects(user_profile)

    collaborators = []
    for project in collaborated_projects:
        collaborators = list(
            chain(collaborators, MemberProfile.objects.filter(pk=project.main_supervisor.pk)))
        collaborators = list(chain(collaborators, MemberProfile.objects.filter(projectsupervisor__project=project,
                                                                               projectsupervisor__state="Collaborator")))
        collaborators = list(chain(collaborators, [project_mentor.mentor for project_mentor in
                                                   ProjectMentor.objects.filter(project=project,
                                                                                state="Collaborator")]))
        collaborators = list(chain(collaborators, [project_member.member for project_member in
                                                   ProjectMember.objects.filter(project=project,
                                                                                state="Collaborator")]))

    if user_profile in collaborators:
        collaborators.remove(user_profile)
    return collaborators


def get_all_collaborated_projects(user):
    # --previous version
    # if user_profile.position == "Learner":
    #     projects = Project.objects.filter(projectlearner__learner=user_profile,
    #                                       projectlearner__pending=False,
    #                                       projectlearner__accepted=True,
    #                                       is_valid=True).distinct()
    # if user_profile.position == "Member":
    #     projects = Project.objects.filter(projectmember__member=user_profile,
    #                                       projectmember__pending=False,
    #                                       projectmember__accepted=True,
    #                                       is_valid=True).distinct()
    # elif user_profile.position == "Mentor":
    #     projects = Project.objects.filter(projectmentor__mentor=user_profile,
    #                                       projectmentor__pending=False,
    #                                       projectmentor__accepted=True,
    #                                       is_valid=True).distinct()
    #     projects |= Project.objects.filter(projectmember__member=user_profile,
    #                                        projectmember__pending=False,
    #                                        projectmember__accepted=True,
    #                                        is_valid=True).distinct()
    # elif user_profile.position == "Supervisor":
    #     projects = Project.objects.filter(projectsupervisor__supervisor=user_profile, projectsupervisor__pending=False,
    #                                       projectsupervisor__accepted=True,
    #                                       is_valid=True).distinct()
    #     projects |= Project.objects.filter(projectmember__member=user_profile,
    #                                        projectmember__pending=False,
    #                                        projectmember__accepted=True,
    #                                        is_valid=True).distinct()
    #
    # projects |= Project.objects.filter(main_supervisor=user_profile,
    #                                    is_valid=True).distinct()
    #
    # return projects.exclude()
    return Project.objects.filter(Q(main_supervisor=user, is_valid=True) |
                                  Q(projectsupervisor__supervisor=user, projectsupervisor__state="Collaborator",
                                    is_valid=True) |
                                  Q(projectmentor__mentor=user, projectmentor__state="Collaborator", is_valid=True) |
                                  Q(projectmember__member=user, projectmember__state="Collaborator", is_valid=True) |
                                  Q(projectlearner__learner=user, projectlearner__state="Collaborator",
                                    is_valid=True)).distinct()


def get_collaborated_projects(user, project_type):
    # -- previous version
    # if user_profile.position == "Learner":
    #     projects = Project.objects.filter(projectlearner__learner=user_profile,
    #                                       projectlearner__pending=False,
    #                                       projectlearner__accepted=True,
    #                                       project_type=project_type,
    #                                       is_valid=True).distinct()
    # if user_profile.position == "Member":
    #     projects = Project.objects.filter(projectmember__member=user_profile,
    #                                       projectmember__pending=False,
    #                                       projectmember__accepted=True,
    #                                       project_type=project_type,
    #                                       is_valid=True).distinct()
    # elif user_profile.position == "Mentor":
    #     projects = Project.objects.filter(projectmentor__mentor=user_profile,
    #                                       projectmentor__pending=False,
    #                                       projectmentor__accepted=True,
    #                                       project_type=project_type,
    #                                       is_valid=True).distinct()
    #     projects |= Project.objects.filter(projectmember__member=user_profile,
    #                                        projectmember__pending=False,
    #                                        projectmember__accepted=True,
    #                                        project_type=project_type,
    #                                        is_valid=True).distinct()
    # elif user_profile.position == "Supervisor":
    #     projects = Project.objects.filter(projectsupervisor__supervisor=user_profile, projectsupervisor__pending=False,
    #                                       projectsupervisor__accepted=True, project_type=project_type,
    #                                       is_valid=True).distinct()
    #     projects |= Project.objects.filter(projectmember__member=user_profile,
    #                                        projectmember__pending=False,
    #                                        projectmember__accepted=True,
    #                                        project_type=project_type,
    #                                        is_valid=True).distinct()
    #
    # projects |= Project.objects.filter(main_supervisor=user_profile, project_type=project_type,
    #                                    is_valid=True).distinct()
    #
    # return projects.exclude()
    return Project.objects.filter(Q(main_supervisor=user, is_valid=True, project_type=project_type) |
                                  Q(projectsupervisor__supervisor=user, projectsupervisor__state="Collaborator",
                                    is_valid=True, project_type=project_type) |
                                  Q(projectmentor__mentor=user, projectmentor__state="Collaborator", is_valid=True,
                                    project_type=project_type) |
                                  Q(projectmember__member=user, projectmember__state="Collaborator", is_valid=True,
                                    project_type=project_type) |
                                  Q(projectlearner__learner=user, projectlearner__state="Collaborator", is_valid=True,
                                    project_type=project_type)).distinct()


def get_research_request_numbers(user):
    # -- previous version
    # if user.memberprofile.position == "Mentor":
    #     member_numbers = 0
    #     learner_numbers = 0
    #     """
    #     my projects numbers
    #     """
    #     for collaborated_project in collaborated_projects:
    #         member_numbers += collaborated_project.projectmember_set.filter(pending=True, accepted=True).count()
    #         learner_numbers += collaborated_project.projectlearner_set.filter(pending=True, accepted=True).count()
    #
    #     """
    #     requested projects numbers
    #     """
    #     member_numbers += ProjectMentor.objects.filter(mentor=user, pending=False, accepted=False).count()
    #     return member_numbers + learner_numbers
    #
    # elif user.memberprofile.position == "Supervisor":
    #     learner_numbers = 0
    #     member_numbers = 0
    #     mentor_numbers = 0
    #     supervisor_numbers = 0
    #     for collaborated_project in collaborated_projects:
    #         learner_numbers += collaborated_project.projectlearner_set.filter(pending=True, accepted=True).count()
    #         member_numbers += collaborated_project.projectmember_set.filter(pending=True, accepted=True).count()
    #         mentor_numbers += collaborated_project.projectmentor_set.filter(pending=True, accepted=True).count()
    #         if collaborated_project.main_supervisor == user:
    #             supervisor_numbers += collaborated_project.projectsupervisor_set.filter(pending=True,
    #                                                                                     accepted=True).count()
    #
    #     requested_numbers = ProjectSupervisor.objects.filter(supervisor=user, pending=False,
    #                                                          accepted=False).count()
    #     return member_numbers + mentor_numbers + supervisor_numbers + requested_numbers + learner_numbers
    #
    # elif user.memberprofile.position == "Member":
    #     return ProjectMember.objects.filter(member=user, pending=False, accepted=False).count()
    # else:
    #     return ProjectLearner.objects.filter(learner=user, pending=False, accepted=False).count()

    number_of_people_who_want_to_be_part_of_my_project = \
        ProjectSupervisor.objects.filter(Q(state="Accepted Pending",
                                           project__main_supervisor=user,
                                           project__project_type="Research") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMentor.objects.filter(Q(Q(state="Accepted Pending",
                                         project__main_supervisor=user,
                                         project__project_type="Research") |
                                       Q(state="Accepted Pending",
                                         project__projectsupervisor__supervisor=user,
                                         project__project_type="Research")) & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMember.objects.filter(Q(Q(state="Accepted Pending",
                                         project__main_supervisor=user,
                                         project__project_type="Research") |
                                       Q(state="Accepted Pending",
                                         project__projectsupervisor__supervisor=user,
                                         project__project_type="Research") |
                                       Q(state="Accepted Pending",
                                         project__projectmentor__mentor=user,
                                         project__project_type="Research")) & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectLearner.objects.filter(Q(Q(state="Accepted Pending",
                                          project__main_supervisor=user,
                                          project__project_type="Research") |
                                        Q(state="Accepted Pending",
                                          project__projectsupervisor__supervisor=user,
                                          project__project_type="Research") |
                                        Q(state="Accepted Pending",
                                          project__projectmentor__mentor=user,
                                          project__project_type="Research")) & ~Q(
            project__status="Deleted")).distinct().count()

    number_of_projects_who_want_me_to_be_part_of_them = \
        ProjectSupervisor.objects.filter(Q(supervisor=user, state="Waiting For Acceptance",
                                           project__project_type="Research") & ~Q(project__status="Deleted")).count() + \
        ProjectMentor.objects.filter(Q(mentor=user, state="Waiting For Acceptance",
                                       project__project_type="Research") & ~Q(project__status="Deleted")).count() + \
        ProjectMember.objects.filter(Q(member=user, state="Waiting For Acceptance",
                                       project__project_type="Research") & ~Q(project__status="Deleted")).count() + \
        ProjectLearner.objects.filter(Q(learner=user, state="Waiting For Acceptance",
                                        project__project_type="Research") & ~Q(project__status="Deleted")).count()

    return number_of_projects_who_want_me_to_be_part_of_them + number_of_people_who_want_to_be_part_of_my_project


def get_industrial_request_numbers(user):
    number_of_people_who_want_to_be_part_of_my_project = \
        ProjectSupervisor.objects.filter(Q(state="Accepted Pending",
                                           project__main_supervisor=user,
                                           project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMentor.objects.filter(Q(state="Accepted Pending",
                                       project__main_supervisor=user,
                                       project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMember.objects.filter(Q(state="Accepted Pending",
                                       project__main_supervisor=user,
                                       project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectLearner.objects.filter(Q(state="Accepted Pending",
                                        project__main_supervisor=user,
                                        project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count()

    number_of_people_who_want_to_be_main_supervisor = ProjectSupervisor.objects.filter(state="Accepted Pending",
                                                                                       project__expert=user) \
        .exclude(Q(project__expert=user, project__projectsupervisor__state='Waiting for Admin Acceptance')
                 | Q(project__expert=user, project__projectsupervisor__state='Waiting For Acceptance')
                 | Q(project__expert=user, project__projectsupervisor__state='Waiting For Signature')
                 | Q(project__expert=user, project__projectsupervisor__state='Inspecting Signature')
                 | Q(project__status="Deleted")).count()

    number_of_people_who_signed_my_signature = \
        ProjectSupervisor.objects.filter(Q(state="Inspecting Signature",
                                           project__main_supervisor=user,
                                           project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMentor.objects.filter(Q(state="Inspecting Signature",
                                       project__main_supervisor=user,
                                       project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectMember.objects.filter(Q(state="Inspecting Signature",
                                       project__main_supervisor=user,
                                       project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count() + \
        ProjectLearner.objects.filter(Q(state="Inspecting Signature",
                                        project__main_supervisor=user,
                                        project__project_type="Industrial") & ~Q(
            project__status="Deleted")).distinct().count()

    number_of_projects_who_want_me_to_be_part_of_them = \
        ProjectSupervisor.objects.filter(Q(supervisor=user, state="Waiting For Acceptance",
                                           project__project_type="Industrial") & ~Q(
            project__status="Deleted")).count() + \
        ProjectMentor.objects.filter(Q(mentor=user, state="Waiting For Acceptance",
                                       project__project_type="Industrial") & ~Q(project__status="Deleted")).count() + \
        ProjectMember.objects.filter(Q(member=user, state="Waiting For Acceptance",
                                       project__project_type="Industrial") & ~Q(project__status="Deleted")).count() + \
        ProjectLearner.objects.filter(Q(learner=user, state="Waiting For Acceptance",
                                        project__project_type="Industrial") & ~Q(project__status="Deleted")).count() + \
        ProjectSupervisor.objects.filter(Q(supervisor=user, state="Waiting For Signature",
                                           project__project_type="Industrial") & ~Q(
            project__status="Deleted")).count() + \
        ProjectMentor.objects.filter(Q(mentor=user, state="Waiting For Signature",
                                       project__project_type="Industrial") & ~Q(project__status="Deleted")).count() + \
        ProjectMember.objects.filter(Q(member=user, state="Waiting For Signature",
                                       project__project_type="Industrial") & ~Q(project__status="Deleted")).count() + \
        ProjectLearner.objects.filter(Q(learner=user, state="Waiting For Signature",
                                        project__project_type="Industrial") & ~Q(project__status="Deleted")).count()

    number_of_ownership_contracts = ProjectContract.objects.filter(Q(user=user, contract_type="Ownership",
                                                                     reply_has_been_sent=False)
                                                                   & ~Q(project__status="Deleted")).count()

    return number_of_people_who_want_to_be_part_of_my_project + number_of_people_who_want_to_be_main_supervisor \
           + number_of_people_who_signed_my_signature + number_of_projects_who_want_me_to_be_part_of_them + \
           number_of_ownership_contracts


def get_competition_request_numbers(user):
    number_of_people_who_want_to_be_part_of_my_project = \
        ProjectSupervisor.objects.filter(Q(state="Accepted Pending",
                                           project__main_supervisor=user,
                                           project__project_type="Competition")
                                         & ~Q(project__status="Deleted")).distinct().count() + \
        ProjectMentor.objects.filter(Q(state="Accepted Pending",
                                       project__main_supervisor=user,
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).distinct().count() + \
        ProjectMember.objects.filter(Q(state="Accepted Pending",
                                       project__main_supervisor=user,
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).distinct().count() + \
        ProjectLearner.objects.filter(Q(state="Accepted Pending",
                                        project__main_supervisor=user,
                                        project__project_type="Competition")
                                      & ~Q(project__status="Deleted")).distinct().count()

    query_condition = Q(project__main_supervisor=user, state="Inspecting Signature",
                        project__project_type='Competition')
    if user.is_superuser:
        query_condition |= Q(project__main_supervisor=None, state="Inspecting Signature",
                             project__project_type='Competition')
    query_condition &= ~Q(project__status="Deleted")
    number_of_people_who_signed_my_signature = \
        ProjectSupervisor.objects.filter(query_condition).distinct().count() + \
        ProjectMentor.objects.filter(query_condition).distinct().count() + \
        ProjectMember.objects.filter(query_condition).distinct().count() + \
        ProjectLearner.objects.filter(query_condition).distinct().count()

    number_of_projects_who_want_me_to_be_part_of_them = \
        ProjectSupervisor.objects.filter(Q(supervisor=user, state="Waiting For Acceptance",
                                           project__project_type="Competition")
                                         & ~Q(project__status="Deleted")).count() + \
        ProjectMentor.objects.filter(Q(mentor=user, state="Waiting For Acceptance",
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).count() + \
        ProjectMember.objects.filter(Q(member=user, state="Waiting For Acceptance",
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).count() + \
        ProjectLearner.objects.filter(Q(learner=user, state="Waiting For Acceptance",
                                        project__project_type="Competition")
                                      & ~Q(project__status="Deleted")).count() + \
        ProjectSupervisor.objects.filter(Q(supervisor=user, state="Waiting For Signature",
                                           project__project_type="Competition")
                                         & ~Q(project__status="Deleted")).count() + \
        ProjectMentor.objects.filter(Q(mentor=user, state="Waiting For Signature",
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).count() + \
        ProjectMember.objects.filter(Q(member=user, state="Waiting For Signature",
                                       project__project_type="Competition")
                                     & ~Q(project__status="Deleted")).count() + \
        ProjectLearner.objects.filter(Q(learner=user, state="Waiting For Signature",
                                        project__project_type="Competition")
                                      & ~Q(project__status="Deleted")).count()

    return number_of_people_who_want_to_be_part_of_my_project + number_of_people_who_signed_my_signature + \
           number_of_projects_who_want_me_to_be_part_of_them


def get_project_collaborators(project):
    # -- previous version
    # collaborators = []
    #
    # project_supervisors = project.projectsupervisor_set.filter(pending=False, accepted=True)
    # for project_supervisor in project_supervisors:
    #     collaborators.append(project_supervisor.supervisor)
    #
    # project_mentors = project.projectmentor_set.filter(pending=False, accepted=True)
    # for project_mentor in project_mentors:
    #     collaborators.append(project_mentor.mentor)
    #
    # project_members = project.projectmember_set.filter(pending=False, accepted=True)
    # for project_member in project_members:
    #     collaborators.append(project_member.member)
    #
    # project_learners = project.projectlearner_set.filter(pending=False, accepted=True)
    # for project_learner in project_learners:
    #     collaborators.append(project_learner.learner)
    #
    # collaborators.append(project.main_supervisor)
    #
    # return collaborators
    return User.objects.filter(Q(projectsupervisor__state="Collaborator",
                                 projectsupervisor__project=project) |
                               Q(project_mentor_mentor__state="Collaborator",
                                 project_mentor_mentor__project=project) |
                               Q(project_member_member__state="Collaborator",
                                 project_member_member__project=project) |
                               Q(project_learner_learner__state="Collaborator",
                                 project_learner_learner__project=project) |
                               Q(project_main_supervisor__pk=project.pk)).distinct()


def is_project_mentor(project, user):
    if ProjectMentor.objects.filter(mentor=user, project=project, state="Collaborator").count() == 1:
        return True
    else:
        return False


def is_project_member(project, user):
    if ProjectMember.objects.filter(member=user, project=project, state="Collaborator").count() == 1:
        return True
    else:
        return False


def is_project_supervisor(project, user):
    if ProjectSupervisor.objects.filter(project=project, supervisor=user, state="Collaborator").count() == 1:
        return True
    else:
        return False


def add_pending_member(request, selected_project, parent):
    try:
        selected_id = int(request.POST.get('member-profile'))
    except ValueError:
        return False, None

    selected_user = User.objects.get(id=selected_id)
    member_is_already_collaborator = ProjectMember.objects.filter(member=selected_user,
                                                                  project=selected_project).count()

    if not member_is_already_collaborator:
        pending_collaborator = ProjectMember(project=selected_project,
                                             member=selected_user,
                                             project_mentor=parent,
                                             priority=-1,
                                             state="Pending")

        pending_collaborator.save()
        Log(user=request.user,
            log=f"added {selected_user} as a member on project {selected_project.title}").save()

        return True, selected_user
    else:
        return False, None


def add_learner(request, selected_project):
    try:
        selected_id = int(request.POST.get('learner-profile'))
    except ValueError:
        return False, None

    selected_user = User.objects.get(id=selected_id)
    member_is_already_learner = ProjectLearner.objects.filter(learner=selected_user,
                                                              project=selected_project).count()
    if not member_is_already_learner:
        new_project_learner = ProjectLearner(project=selected_project,
                                             learner=selected_user,
                                             priority=-1,
                                             state="Pending")

        Log(user=request.user, log=f'Added {selected_user} as a learner to {selected_project.title}').save()
        new_project_learner.save()
        return True, selected_user
    else:
        return False, None


def add_mentor(request, selected_project):
    selected_id = int(request.POST.get('mentor-profile'))
    selected_user = User.objects.get(id=selected_id)
    member_is_already_mentor = ProjectMentor.objects.filter(mentor=selected_user,
                                                            project=selected_project).count()
    mentor_is_a_project_member = ProjectMember.objects.filter(member=selected_user,
                                                              project=selected_project).count()
    if not member_is_already_mentor or not mentor_is_a_project_member:
        new_project_mentor = ProjectMentor(project=selected_project,
                                           mentor=selected_user,
                                           priority=-1,
                                           state="Pending")

        Log(user=request.user, log=f'Added {selected_user} as a mentor to {selected_project.title}').save()
        new_project_mentor.save()
        return True, selected_user
    else:
        return False, None


def add_supervisor(request, selected_project):
    selected_id = int(request.POST.get('supervisor-profile'))
    try:
        selected_user = User.objects.filter(id=selected_id)[0]
        if ProjectMember.objects.filter(project=selected_project, member=selected_user).count() > 0:
            return False, "Selected Collaborator is a member"
    except IndexError:  # skipping post request in the middle
        return True, None
    member_is_already_supervisor = ProjectSupervisor.objects.filter(supervisor=selected_user,
                                                                    project=selected_project).count()
    if not member_is_already_supervisor:
        new_project_supervisor = ProjectSupervisor(project=selected_project,
                                                   supervisor=selected_user,
                                                   priority=-1,
                                                   state="Pending")
        new_project_supervisor.save()
        Log(user=request.user, log=f'Added {selected_user} as a supervisor to {selected_project.title}').save()
        return True, None
    else:
        return False, "Selected member is already a mentor"


def accept_collaborator(post_request, selected_mentor, contract_file):
    collaboration_primary_key = post_request.get('accept-collaborator')

    selected_collaboration = ProjectMember.objects.get(pk=collaboration_primary_key)
    selected_collaboration.project_mentor = selected_mentor

    if selected_collaboration.state == "Pending":
        ProjectContract(project=selected_collaboration.project, user=selected_collaboration.member, valid=False,
                        contract_type='Collaborator', contract_file=contract_file).save()
        selected_collaboration.state = "Waiting For Acceptance"
    elif selected_collaboration.state == "Accepted Pending":
        selected_collaboration.state = "Waiting For Signature"
        ProjectContract(project=selected_collaboration.project, user=selected_collaboration.member,
                        contract_type='Collaborator', contract_file=contract_file).save()

    selected_collaboration.save()
    Log(user=selected_collaboration.member,
        log=f'Has become a member in project "{selected_collaboration.project}"').save()
    return True, None, selected_collaboration


def reject_collaborator(request):
    collaboration_primary_key = request.POST.get('reject-collaborator')
    selected_collaboration = ProjectMember.objects.get(pk=collaboration_primary_key)
    selected_user = selected_collaboration.member
    selected_project = selected_collaboration.project
    selected_collaboration.delete()

    Log(user=request.user,
        log=f"rejected {selected_user} on project {selected_project.title}").save()
    return selected_collaboration


def user_has_memberprofile(given_user):
    return MemberProfile.objects.filter(user=given_user).count() == 1


def withdraw_legal_profile_from_a_project(project_primary_key, requester_user):
    selected_project = Project.objects.get(pk=project_primary_key)

    project_supervisor = ProjectSupervisor.objects.filter(project=selected_project, supervisor=requester_user,
                                                          state="Accepted Pending")
    project_mentor = ProjectMentor.objects.filter(project=selected_project, mentor=requester_user,
                                                  state="Accepted Pending")
    project_member = ProjectMember.objects.filter(project=selected_project, member=requester_user,
                                                  state="Accepted Pending")
    project_learner = ProjectLearner.objects.filter(project=selected_project, learner=requester_user,
                                                    state="Accepted Pending")

    Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
    if project_supervisor.count():
        project_supervisor.delete()
        return "WITHDRAW", "Supervisor"
    if project_mentor.count():
        project_mentor.delete()
        return "WITHDRAW", "Mentor"
    if project_member.count():
        project_member.delete()
        return "WITHDRAW", "Member"
    if project_learner.count():
        project_learner.delete()
        return "WITHDRAW", "Learner"


def request_or_withdraw_a_project(project_primary_key, requester_user, position):
    selected_project = Project.objects.get(pk=project_primary_key)

    # legal person cannot be main supervisor
    if selected_project.main_supervisor is None and not user_has_memberprofile(
            requester_user) and position == 'Supervisor':
        return None

    if position == "Supervisor":
        """
        Supervisors can apply to to project as supervisors and members.
        so after security check, we check whether he has applied to the project as supervisor or member before or not.
        in case he did, we withdraw the request otherwise we make him a new collaborator
        """
        if user_has_memberprofile(requester_user) and requester_user.memberprofile.position != 'Supervisor':  # for
            # security check
            return None

        project_supervisor = ProjectSupervisor.objects.filter(project=selected_project, supervisor=requester_user)
        project_mentor = ProjectMentor.objects.filter(project=selected_project, mentor=requester_user)
        project_member = ProjectMember.objects.filter(project=selected_project, member=requester_user)
        project_learner = ProjectLearner.objects.filter(project=selected_project, learner=requester_user)
        if project_supervisor.count() == 1:  # withdraw
            if project_supervisor[0].state == "Accepted Pending":  # for security check
                has_a_scored_proposal = ProposalOpinion.objects.filter(
                    proposal__project_supervisor=project_supervisor[0]).count()
                if not has_a_scored_proposal:
                    if user_has_memberprofile(requester_user):
                        increase_user_balance(selected_project, requester_user, "Supervisor")
                    project_supervisor.delete()
                    Log(user=requester_user,
                        log=f'withdrew his application for project "{selected_project.title}"').save()
                    return "WITHDRAW"
                else:
                    return None
        elif project_mentor.count() == 1:  # withdraw
            if project_mentor[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Mentor")
                project_mentor.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        elif project_member.count() == 1:  # withdraw
            if project_member[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Member")
                project_member.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        elif project_learner.count() == 1:  # withdraw
            if project_learner[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Learner")
                project_learner.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        else:  # request
            if not user_has_memberprofile(requester_user) or get_limit_on_projects(requester_user) < 3:
                if user_has_memberprofile(requester_user):
                    decrease_user_balance(selected_project, requester_user, "Supervisor")
                new_project_supervisor = ProjectSupervisor(project=selected_project, supervisor=requester_user,
                                                           state="Accepted Pending", priority=-1)
                new_project_supervisor.save()

                Log(user=requester_user, log=f'applied as supervisor to "{selected_project.title}"').save()
                return "REQUEST"
            else:
                return None

    elif position == "Mentor":
        project_mentor = ProjectMentor.objects.filter(project=selected_project, mentor=requester_user)
        project_member = ProjectMember.objects.filter(project=selected_project, member=requester_user)
        project_learner = ProjectLearner.objects.filter(project=selected_project, learner=requester_user)
        if project_mentor.count() == 1:  # withdraw
            if project_mentor[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Mentor")
                project_mentor.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        elif project_member.count() == 1:  # withdraw
            if project_member[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Member")
                project_member.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        elif project_learner.count() == 1:  # withdraw
            if project_learner[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Learner")
                project_learner.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        else:  # request
            if not user_has_memberprofile(requester_user) or get_limit_on_projects(requester_user) < 3:
                if user_has_memberprofile(requester_user):
                    decrease_user_balance(selected_project, requester_user, "Mentor")
                new_project_mentor = ProjectMentor(project=selected_project, mentor=requester_user,
                                                   state="Accepted Pending", priority=-1)
                new_project_mentor.save()

                Log(user=requester_user, log=f'applied as mentor to "{selected_project.title}"').save()
                return "REQUEST"
            else:
                return None

    elif position == "Member":
        project_member = ProjectMember.objects.filter(project=selected_project, member=requester_user)
        project_learner = ProjectLearner.objects.filter(project=selected_project, learner=requester_user)
        if project_member.count() == 1:  # withdraw
            if project_member[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Member")
                project_member.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        if project_learner.count() == 1:  # withdraw
            if project_learner[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Learner")
                project_learner.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        else:  # request
            if not user_has_memberprofile(requester_user) or get_limit_on_projects(requester_user) < 3:
                if user_has_memberprofile(requester_user):
                    decrease_user_balance(selected_project, requester_user, "Member")
                new_project_member = ProjectMember(project=selected_project, member=requester_user,
                                                   state="Accepted Pending", priority=-1)
                new_project_member.save()

                Log(user=requester_user, log=f'applied as member to "{selected_project.title}"').save()
                return "REQUEST"
            else:
                return None
    elif position == "Learner":
        project_learner = ProjectLearner.objects.filter(project=selected_project, learner=requester_user)
        if project_learner.count() == 1:  # withdraw
            if project_learner[0].state == "Accepted Pending":  # for security check
                if user_has_memberprofile(requester_user):
                    increase_user_balance(selected_project, requester_user, "Learner")
                project_learner.delete()
                Log(user=requester_user, log=f'withdrew his application for project "{selected_project.title}"').save()
                return "WITHDRAW"
        else:  # request
            if not user_has_memberprofile(requester_user) or get_limit_on_projects(requester_user) < 3:
                if user_has_memberprofile(requester_user):
                    decrease_user_balance(selected_project, requester_user, "Learner")
                new_project_learner = ProjectLearner(project=selected_project, learner=requester_user,
                                                     state="Accepted Pending", priority=-1)
                new_project_learner.save()

                Log(user=requester_user, log=f'applied as learner to "{selected_project.title}"').save()
                return "REQUEST"
            else:
                return None


def send_notification_to_supervisor_and_mentors(project_primary_key, requester_user, position):
    selected_project = Project.objects.get(pk=project_primary_key)
    if position == "Supervisor":
        if selected_project.main_supervisor is not None:
            send_notification("Someone has applied to a project.", f"{requester_user.first_name}"
                                                                   f" {requester_user.last_name} wants to be on a project as a supervisor. Click to "
                                                                   f"see what it is.",
                              selected_project.main_supervisor,
                              reverse('dashboard-project-manage-page', args=[selected_project.pk]))
    if position == "Mentor":
        send_notification("Someone has applied to a project.", f"{requester_user.first_name}"
                                                               f" {requester_user.last_name} wants to be on a "
                                                               f"project as a mentor. Click to see what it is.",
                          selected_project.main_supervisor,
                          reverse('dashboard-project-manage-page', args=[selected_project.pk]))
        for project_supervisor in selected_project.projectsupervisor_set.filter(state="Collaborator"):
            send_notification("Someone has applied to a project.",
                              f"{requester_user.first_name} {requester_user.last_name} wants to be on a "
                              f"project as a mentor. Click to see what it is.",
                              project_supervisor.supervisor,
                              reverse('dashboard-project-manage-page', args=[selected_project.pk]))

    if position == "Member" or position == "Learner":
        send_notification("Someone has applied to a project.", f"{requester_user.first_name}"
                                                               f" {requester_user.last_name} wants to be on a "
                                                               f"project as a {position}. Click to see what it is.",
                          selected_project.main_supervisor,
                          reverse('dashboard-project-manage-page', args=[selected_project.pk]))
        for project_supervisor in selected_project.projectsupervisor_set.filter(state="Collaborator"):
            send_notification("Someone has applied to a project.",
                              f"{requester_user.first_name} {requester_user.last_name} wants to be on a "
                              f"project as a {position}. Click to see what it is.",
                              project_supervisor.supervisor,
                              reverse('dashboard-project-manage-page', args=[selected_project.pk]))
        for project_mentor in selected_project.projectmentor_set.filter(state="Collaborator"):
            send_notification("Someone has applied to a project.",
                              f"{requester_user.first_name} {requester_user.last_name} wants to be on a "
                              f"project as a {position}. Click to see what it is.",
                              project_mentor.mentor,
                              reverse('dashboard-project-manage-page', args=[selected_project.pk]))


def remove_notification_from_supervisor_and_mentors(project_primary_key, requester_user, position):
    selected_project = Project.objects.get(pk=project_primary_key)
    if position == "Supervisor":
        Notification.objects.filter(title="Someone has applied to a project.",
                                    description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                    target=selected_project.main_supervisor,
                                    link=reverse('dashboard-project-manage-page', args=[selected_project.pk])).delete()
    if position == "Mentor":
        Notification.objects.filter(title="Someone has applied to a project.",
                                    description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                    target=selected_project.main_supervisor,
                                    link=reverse('dashboard-project-manage-page', args=[selected_project.pk])).delete()
        for project_supervisor in selected_project.projectsupervisor_set.filter(state="Collaborator"):
            Notification.objects.filter(title="Someone has applied to a project.",
                                        description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                        target=project_supervisor.supervisor,
                                        link=reverse('dashboard-project-manage-page',
                                                     args=[selected_project.pk])).delete()

    if position == "Member" or position == "Learner":
        Notification.objects.filter(title="Someone has applied to a project.",
                                    description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                    target=selected_project.main_supervisor,
                                    link=reverse('dashboard-project-manage-page', args=[selected_project.pk])).delete()
        for project_supervisor in selected_project.projectsupervisor_set.filter(state="Collaborator"):
            Notification.objects.filter(title="Someone has applied to a project.",
                                        description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                        target=project_supervisor.supervisor,
                                        link=reverse('dashboard-project-manage-page',
                                                     args=[selected_project.pk])).delete()
        for project_mentor in selected_project.projectmentor_set.filter(state="Collaborator"):
            Notification.objects.filter(title="Someone has applied to a project.",
                                        description__icontains=f"{requester_user.first_name} {requester_user.last_name}",
                                        target=project_mentor.mentor,
                                        link=reverse('dashboard-project-manage-page',
                                                     args=[selected_project.pk])).delete()


def delete_collaborator_from_project(user, project, position):
    if position == "Supervisor":
        """
        At first we remove his contract if not a collaborator
        """
        selected_project_supervisor = ProjectSupervisor.objects.get(project=project, supervisor=user)
        if selected_project_supervisor.state != "Collaborator":
            ProjectContract.objects.filter(project=project, user=user, contract_type='Collaborator').delete()

        """
        In case if he has any sort of mentors, we change their supervisors to the main supervisor
        """
        project_mentors = ProjectMentor.objects.filter(project=project, project_supervisor=user)
        for project_mentor in project_mentors:
            project_mentor.project_supervisor = project.main_supervisor
            project_mentor.save()

        """
        In case if he has any members, we change their mentors to the main supervisor
        """
        project_members = ProjectMember.objects.filter(project=project, project_mentor=user)
        for project_member in project_members:
            project_member.project_mentor = project.main_supervisor
            project_member.save()

        """
        at the end, we decrease priority of the ones who were greater than him
        """
        for project_supervisor in ProjectSupervisor.objects.filter(project=project,
                                                                   priority__gte=selected_project_supervisor.priority):
            project_supervisor.priority = project_supervisor.priority - 1
            project_supervisor.save()
        selected_project_supervisor.delete()

    elif position == "Mentor":
        """
        At first we remove contract if not a collaborator
        """
        selected_project_mentor = ProjectMentor.objects.get(project=project, mentor=user)
        if selected_project_mentor.state != "Collaborator":
            ProjectContract.objects.filter(project=project, user=user, contract_type='Collaborator').delete()

        """
        In case if he has any members, we change their mentors to the main supervisor
        """
        project_members = ProjectMember.objects.filter(project=project, project_mentor=user)
        for project_member in project_members:
            project_member.project_mentor = project.main_supervisor
            project_member.save()

        """
        at the end, we decrease priority of the ones who were greater than him
        """
        for project_mentor in ProjectMentor.objects.filter(project=project,
                                                           priority__gte=selected_project_mentor.priority):
            project_mentor.priority = project_mentor.priority - 1
            project_mentor.save()
        selected_project_mentor.delete()
    elif position == "Member":
        selected_project_member = ProjectMember.objects.get(project=project, member=user)
        if selected_project_member.state != "Collaborator":
            ProjectContract.objects.filter(project=project, user=user, contract_type='Collaborator').delete()

        """
        we decrease priority of the ones who were greater than him
        """
        for project_member in ProjectSupervisor.objects.filter(project=project,
                                                               priority__gte=selected_project_member.priority):
            project_member.priority = project_member.priority - 1
            project_member.save()
        selected_project_member.delete()
    else:
        selected_project_learner = ProjectLearner.objects.get(project=project, learner=user)
        if selected_project_learner.state != "Collaborator":
            ProjectContract.objects.filter(project=project, user=user, contract_type='Collaborator').delete()

        """
        we decrease priority of the ones who were greater than him
        """
        for project_learner in ProjectLearner.objects.filter(project=project,
                                                             priority__gte=selected_project_learner.priority):
            project_learner.priority = project_learner.priority - 1
            project_learner.save()
        selected_project_learner.delete()

    increase_user_balance(project, user, position)


def send_notification(title, description, target, link):
    new_notification = Notification(title=title, description=description, target=target, link=link)
    new_notification.save()


def accept_supervisor(selected_supervisor, selected_project, contract_file):
    """
    gets supervisor and the project and returns true if he is added successfully and false if he's not.
    """
    if selected_project.project_type == "Industrial" and selected_project.main_supervisor is None:  # just for
        # security check
        return None

    if selected_supervisor.state == "Pending":
        ProjectContract(project=selected_project, user=selected_supervisor.supervisor, valid=False,
                        contract_type='Collaborator', contract_file=contract_file).save()
        selected_supervisor.state = "Waiting For Acceptance"
        selected_supervisor.save()

    elif selected_supervisor.state == "Accepted Pending":
        ProjectContract(project=selected_project, user=selected_supervisor.supervisor,
                        contract_type='Collaborator', contract_file=contract_file).save()
        selected_supervisor.state = "Waiting For Signature"
        selected_supervisor.save()


def accept_mentor(selected_project, selected_mentor, uploaded_file):
    if selected_project.main_supervisor is None:  # just for security check
        return None

    if selected_mentor.state == "Pending":
        ProjectContract(project=selected_project, user=selected_mentor.mentor, contract_type='Collaborator', valid=False,
                        contract_file=uploaded_file).save()
        selected_mentor.state = "Waiting For Acceptance"
        selected_mentor.save()

    elif selected_mentor.state == "Accepted Pending":
        ProjectContract(project=selected_project, user=selected_mentor.mentor, contract_type='Collaborator',
                        contract_file=uploaded_file).save()
        selected_mentor.state = "Waiting For Signature"
        selected_mentor.save()


def accept_learner(selected_learner, selected_project, contract_file):
    if selected_learner.state == "Pending":
        ProjectContract(project=selected_project, user=selected_learner.learner,
                        contract_type='Collaborator', contract_file=contract_file, valid=False).save()
        selected_learner.state = "Waiting For Acceptance"
        selected_learner.save()
    elif selected_learner.state == "Accepted Pending":
        ProjectContract(project=selected_project, user=selected_learner.learner,
                        contract_type='Collaborator', contract_file=contract_file).save()
        selected_learner.state = "Waiting For Signature"
        selected_learner.save()


def make_him_supervisor_of_the_owner(supervisor, selected_project):
    owner = selected_project.owner
    owner_position = owner.memberprofile.position

    if owner_position == "Mentor":
        project_mentor = ProjectMentor.objects.get(mentor=owner, project=selected_project)
        project_mentor.project_supervisor = supervisor
        project_mentor.save()
    elif owner_position == "Member":
        project_member = ProjectMember.objects.get(member=owner, project=selected_project)
        project_member.project_mentor = supervisor
        project_member.save()
    elif owner_position == "Learner":
        project_learner = ProjectLearner.objects.get(learner=owner, project=selected_project)
        project_learner.project_mentor = supervisor
        project_learner.save()


def email_the_collaborator(position, issuer, selected_project, destination_email, collaborator_state):
    if collaborator_state == "Waiting For Acceptance":
        email_subject = f"You have a request to be a {position}"
        email_content = f"""
{issuer.first_name} {issuer.last_name} wants you to be on the project "{selected_project.title}"

Please visit our website and respond to the request
Link: https://tecvico.com/dashboard/requests/

Regards,
Tecvico Team
"""
        threading.Thread(target=send_new_email,
                         args=(email_subject, email_content, destination_email)).start()
    elif collaborator_state == "Waiting For Signature":
        email_subject = f"A contract has been provided for the project you requested to be {position}"
        email_content = f"""
For the project you requested ({selected_project.title}), a contract has been provided. Please read the letter thoroughly and sign it.

Contract Link: https://tecvico.com/dashboard/project-contract/{selected_project.pk}

Regards,
Tecvico team
"""
        threading.Thread(target=send_new_email,
                         args=(email_subject, email_content, destination_email)).start()


def accept_main_supervisor(selected_supervisor, selected_project):
    if selected_project.project_type == "Research":
        selected_project.main_supervisor = selected_supervisor.supervisor
        selected_project.save()
        make_him_supervisor_of_the_owner(selected_supervisor.supervisor, selected_project)
        selected_supervisor.delete()

        send_notification(selected_project.title, "You got accepted as main supervisor",
                          selected_supervisor.supervisor, reverse('dashboard-projects-page',
                                                                  args=[selected_project.project_type]))
    else:
        if selected_supervisor.state == "Accepted Pending":
            selected_supervisor.state = "Waiting for Admin Acceptance"
        selected_supervisor.save()

        if selected_supervisor.state == "Waiting for Admin Acceptance":
            inform_the_superusers(selected_project,
                                  "A main supervisor is accepted in a project, please verify the request",
                                  reverse('dashboard-project-manage-page', args=[selected_project.pk]))


def inform_the_superusers(selected_project, notification_text, destination_url):
    superusers = User.objects.filter(is_superuser=True)
    for superuser in superusers:
        send_notification(selected_project.title, notification_text,
                          superuser, destination_url)


def competition_manager_eligible_to_see(project):
    return (is_competition_manager(project.main_supervisor) or
            not ProjectSupervisor.objects.filter(Q(project=project, state="Waiting For Acceptance") |
                                                 Q(project=project, state="Waiting for Admin Acceptance") |
                                                 Q(project=project, state='Waiting For Signature') |
                                                 Q(project=project, state='Inspecting Signature')).count()) \
           and project.main_supervisor is None


def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0:  # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def handle_sort(request, chosen_members):
    sort_by = request.GET.get('sort')
    if sort_by == "join date (ascending)":
        return chosen_members.order_by('date_joined')
    elif sort_by == "join date (descending)":
        return chosen_members.order_by('-date_joined')
    elif sort_by == "name":
        return chosen_members.order_by('first_name')
    else:
        return chosen_members


def handle_advanced_search(request, chosen_members):
    if request.GET.get('project-logic') is None:  # in case there is not any advanced search
        return chosen_members

    logic_is_and = request.GET.get('project-logic') == 'AND'
    if logic_is_and:
        function_result = User.objects.all()
    else:
        function_result = User.objects.none()

    if 'new-project-numbers' in request.GET:
        try:
            new_project_numbers = int(request.GET.get('new-project-numbers'))
            more_than = request.GET.get('new-project-limit') == "More Than"
            less_than = request.GET.get('new-project-limit') == "Less Than"

            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # -- previous version
                # user_project_numbers = ProjectMember.objects.filter(member=user,
                #                                                            project__status='New',
                #                                                            pending=False, accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user,
                #                                                                 project__status='New',
                #                                                                 pending=False
                #                                                                 , accepted=True).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                                     project__status='New',
                #                                                                     pending=False,
                #                                                                     accepted=True).count()
                #     user_project_numbers += Project.objects.filter(main_supervisor=user,
                #                                                           status='New').count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, project__status='New',
                                                                        state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, project__status='New',
                                                                    state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, project__status='New',
                                                                    state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, project__status='New',
                                                                     state="Collaborator").count() + \
                                       Project.objects.filter(main_supervisor=user, status='New').count()

                if more_than:
                    if user_project_numbers > new_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < new_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == new_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result
        except ValueError:
            if len(request.GET.get('new-project-numbers')) > 0:
                messages.error(request, "New project limits should be a number!")

    if 'pending-project-numbers' in request.GET:
        try:
            pending_project_numbers = int(request.GET.get('pending-project-numbers'))
            more_than = request.GET.get('pending-project-limit') == "More Than"
            less_than = request.GET.get('pending-project-limit') == "Less Than"
            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # -- previous version
                # user_project_numbers = ProjectMember.objects.filter(member=user,
                #                                                     project__status='Pending',
                #                                                     pending=False, accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user,
                #                                                          project__status='Pending',
                #                                                          pending=False, accepted=True
                #                                                                 ).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                              project__status='Pending',
                #                                                              pending=False, accepted=True).count()
                #     user_project_numbers += Project.objects.filter(main_supervisor=user,
                #                                                    status='Pending').count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, project__status='Pending',
                                                                        state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, project__status='Pending',
                                                                    state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, project__status='Pending',
                                                                    state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, project__status='Pending',
                                                                     state="Collaborator").count() + \
                                       Project.objects.filter(main_supervisor=user, status='Pending').count()

                if more_than:
                    if user_project_numbers > pending_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < pending_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == pending_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result

        except ValueError:
            if len(request.GET.get('pending-project-numbers')) > 0:
                messages.error(request, "Pending project limits number should be a number!")

    if 'ongoing-project-numbers' in request.GET:
        try:
            ongoing_project_numbers = int(request.GET.get('ongoing-project-numbers'))
            more_than = request.GET.get('ongoing-project-limit') == "More Than"
            less_than = request.GET.get('ongoing-project-limit') == "Less Than"
            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # -- previous version
                # user_project_numbers = ProjectMember.objects.filter(member=user,
                #                                                     project__status='Ongoing',
                #                                                     pending=False, accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user,
                #                                                          project__status='Ongoing',
                #                                                          pending=False, accepted=True).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                              project__status='Ongoing',
                #                                                              pending=False, accepted=True).count()
                #     user_project_numbers += Project.objects.filter(main_supervisor=user,
                #                                                    status='Ongoing').count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, project__status='Ongoing',
                                                                        state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, project__status='Ongoing',
                                                                    state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, project__status='Ongoing',
                                                                    state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, project__status='Ongoing',
                                                                     state="Collaborator").count() + \
                                       Project.objects.filter(main_supervisor=user, status='Ongoing').count()

                if more_than:
                    if user_project_numbers > ongoing_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < ongoing_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == ongoing_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result

        except ValueError:
            if len(request.GET.get('ongoing-project-numbers')) > 0:
                messages.error(request, "Ongoing project limits number should be a number!")

    if 'on-hold-project-numbers' in request.GET:
        try:
            on_hold_project_numbers = int(request.GET.get('on-hold-project-numbers'))
            more_than = request.GET.get('on-hold-project-limit') == "More Than"
            less_than = request.GET.get('on-hold-project-limit') == "Less Than"
            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # --previous version
                # user_project_numbers = ProjectMember.objects.filter(member=user,
                #                                                     project__status='On Hold',
                #                                                     pending=False,
                #                                                     accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user,
                #                                                          project__status='On Hold',
                #                                                          pending=False, accepted=True).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                              project__status='On Hold',
                #                                                              pending=False, accepted=True).count()
                #     user_project_numbers += Project.objects.filter(main_supervisor=user,
                #                                                    status='On Hold').count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, project__status='On Hold',
                                                                        state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, project__status='On Hold',
                                                                    state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, project__status='On Hold',
                                                                    state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, project__status='On Hold',
                                                                     state="Collaborator").count() + \
                                       Project.objects.filter(main_supervisor=user, status='On Hold').count()

                if more_than:
                    if user_project_numbers > on_hold_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < on_hold_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == on_hold_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result

        except ValueError:
            if len(request.GET.get('on-hold-project-numbers')) > 0:
                messages.error(request, "On Hold project limits number should be a number!")

    if 'done-project-numbers' in request.GET:
        try:
            done_project_numbers = int(request.GET.get('done-project-numbers'))
            more_than = request.GET.get('done-project-limit') == "More Than"
            less_than = request.GET.get('done-project-limit') == "Less Than"
            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # -- previous version
                # user_project_numbers = ProjectMember.objects.filter(member=user,
                #                                                     project__status='Done',
                #                                                     pending=False,
                #                                                     accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user,
                #                                                          project__status='Done',
                #                                                          pending=False, accepted=True).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                              project__status='Done',
                #                                                              pending=False, accepted=True).count()
                #     user_project_numbers += Project.objects.filter(main_supervisor=user, status='Done').count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, project__status='Done',
                                                                        state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, project__status='Done',
                                                                    state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, project__status='Done',
                                                                    state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, project__status='Done',
                                                                     state="Collaborator").count() + \
                                       Project.objects.filter(main_supervisor=user, status='Done').count()

                if more_than:
                    if user_project_numbers > done_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < done_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == done_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result

        except ValueError:
            if len(request.GET.get('done-project-numbers')) > 0:
                messages.error(request, "Done project limits number should be a number!")

    if 'requested-project-numbers' in request.GET:
        try:
            requested_project_numbers = int(request.GET.get('requested-project-numbers'))
            more_than = request.GET.get('requested-project-limit') == "More Than"
            less_than = request.GET.get('requested-project-limit') == "Less Than"
            result = User.objects.none()  # empty queryset

            for user in chosen_members:
                # user_project_numbers = ProjectMember.objects.filter(member=user, pending=True, accepted=True).count()
                # if user.position == "Mentor":
                #     user_project_numbers += ProjectMentor.objects.filter(mentor=user, pending=True,
                #                                                          accepted=True).count()
                # elif user.position == "Supervisor":
                #     user_project_numbers += ProjectSupervisor.objects.filter(supervisor=user,
                #                                                              pending=True, accepted=True).count()
                user_project_numbers = ProjectSupervisor.objects.filter(supervisor=user, state="Collaborator").count() + \
                                       ProjectMentor.objects.filter(mentor=user, state="Collaborator").count() + \
                                       ProjectMember.objects.filter(member=user, state="Collaborator").count() + \
                                       ProjectLearner.objects.filter(learner=user, state="Collaborator").count()

                if more_than:
                    if user_project_numbers > requested_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                elif less_than:
                    if user_project_numbers < requested_project_numbers:
                        result |= User.objects.filter(pk=user.pk)
                else:
                    if user_project_numbers == requested_project_numbers:
                        result |= User.objects.filter(pk=user.pk)

            if logic_is_and:
                function_result &= result
            else:
                function_result |= result

        except ValueError:
            if len(request.GET.get('requested-project-numbers')) > 0:
                messages.error(request, "Requested project limits number should be a number!")

    if request.GET.get('search-degree'):
        temp_result = User.objects.none()
        for selected_degree in request.GET.getlist('search-degree'):
            temp_result |= User.objects.filter(memberprofile__degree=selected_degree)
        chosen_members &= temp_result

    if request.GET.get('search-field-of-study'):
        temp_result = User.objects.none()
        for selected_field_of_study in request.GET.getlist('search-field-of-study'):
            temp_result |= User.objects.filter(memberprofile__field_of_study=selected_field_of_study)
        chosen_members &= temp_result

    if request.GET.get('search-status'):
        temp_result = User.objects.none()
        for selected_field_of_study in request.GET.getlist('search-status'):
            temp_result |= User.objects.filter(memberprofile__status=selected_field_of_study)
        chosen_members &= temp_result

    if request.GET.get('joined_since'):
        date, time = request.GET.get('joined_since').split()

        year, month, day = map(int, date.split('/'))
        hour, minute = map(int, time.split(":"))

        chosen_members &= User.objects.filter(date_joined__gte=datetime.datetime(year, month, day, hour, minute))

    return chosen_members & function_result


def change_sort(get_params, selected_project):
    from_priority = int(get_params.get('from-sort-priority'))
    target_priority = int(get_params.get('target-sort-priority'))
    from_list = get_params.get('from_list')
    target_list = get_params.get('target_list')

    if from_list == target_list:
        if from_list == 'draggable-learners':
            other_element = ProjectLearner.objects.get(project=selected_project, priority=target_priority)
            our_element = ProjectLearner.objects.get(project=selected_project, priority=from_priority)

        elif from_list == 'draggable-members':
            other_element = ProjectMember.objects.get(project=selected_project, priority=target_priority)
            our_element = ProjectMember.objects.get(project=selected_project, priority=from_priority)

        elif from_list == 'draggable-mentors':
            other_element = ProjectMentor.objects.get(project=selected_project, priority=target_priority)
            our_element = ProjectMentor.objects.get(project=selected_project, priority=from_priority)
        else:
            other_element = ProjectSupervisor.objects.get(project=selected_project, priority=target_priority)
            our_element = ProjectSupervisor.objects.get(project=selected_project, priority=from_priority)

        other_element.priority = from_priority
        our_element.priority = target_priority

        other_element.save()
        our_element.save()

        return "SUCCESS"
    else:
        if from_list == 'draggable-learners':
            our_element = ProjectLearner.objects.get(project=selected_project, priority=from_priority)

            greater_elements = ProjectLearner.objects.filter(project=selected_project, priority__gt=from_priority)
            for greater_element in greater_elements:
                greater_element.priority = greater_element.priority - 1
                greater_element.save()

            sort_to_another_position(selected_project, our_element, our_element.learner, our_element.project_mentor,
                                     target_list, target_priority)

        if from_list == 'draggable-members':
            our_element = ProjectMember.objects.get(project=selected_project, priority=from_priority)

            greater_elements = ProjectMember.objects.filter(project=selected_project, priority__gt=from_priority)
            for greater_element in greater_elements:
                greater_element.priority = greater_element.priority - 1
                greater_element.save()

            sort_to_another_position(selected_project, our_element, our_element.member, our_element.project_mentor,
                                     target_list, target_priority)

        if from_list == 'draggable-mentors':
            our_element = ProjectMentor.objects.get(project=selected_project, priority=from_priority)

            greater_elements = ProjectMentor.objects.filter(project=selected_project, priority__gt=from_priority)
            for greater_element in greater_elements:
                greater_element.priority = greater_element.priority - 1
                greater_element.save()

            sort_to_another_position(selected_project, our_element, our_element.mentor, our_element.project_supervisor,
                                     target_list, target_priority)

        if from_list == 'draggable-supervisors':
            our_element = ProjectSupervisor.objects.get(project=selected_project, priority=from_priority)

            greater_elements = ProjectSupervisor.objects.filter(project=selected_project, priority__gt=from_priority)
            for greater_element in greater_elements:
                greater_element.priority = greater_element.priority - 1
                greater_element.save()

            sort_to_another_position(selected_project, our_element, our_element.supervisor,
                                     selected_project.main_supervisor, target_list, target_priority)
        return "SUCCESS - REFRESH"


def sort_to_another_position(selected_project, our_element, our_element_collaborator, our_element_superior, target_list,
                             target_priority):
    if target_list == 'draggable-supervisors':
        greater_target_elements = ProjectSupervisor.objects.filter(project=selected_project,
                                                                   priority__gte=target_priority)
        for greater_target_element in greater_target_elements:
            greater_target_element.priority = greater_target_element.priority + 1
            greater_target_element.save()

        new_project_supervisor = ProjectSupervisor(supervisor=our_element_collaborator, project=selected_project,
                                                   state="Collaborator", priority=target_priority,
                                                   tasks=our_element.tasks,
                                                   is_email_sent=our_element.is_email_sent)
        new_project_supervisor.save()

    if target_list == 'draggable-mentors':
        greater_target_elements = ProjectMentor.objects.filter(project=selected_project,
                                                               priority__gte=target_priority)
        for greater_target_element in greater_target_elements:
            greater_target_element.priority = greater_target_element.priority + 1
            greater_target_element.save()

        project_supervisor_is_actually_a_mentor = ProjectMentor.objects.filter(project=selected_project,
                                                                               mentor=our_element_superior).count()
        if project_supervisor_is_actually_a_mentor:
            new_project_mentor = ProjectMentor(project_supervisor=selected_project.main_supervisor,
                                               mentor=our_element_collaborator, project=selected_project,
                                               state="Collaborator", priority=target_priority, tasks=our_element.tasks,
                                               is_email_sent=our_element.is_email_sent)
        else:
            new_project_mentor = ProjectMentor(project_supervisor=our_element_superior,
                                               mentor=our_element_collaborator, project=selected_project,
                                               state="Collaborator", priority=target_priority, tasks=our_element.tasks,
                                               is_email_sent=our_element.is_email_sent)
        new_project_mentor.save()

    if target_list == 'draggable-members':
        greater_target_elements = ProjectMember.objects.filter(project=selected_project,
                                                               priority__gte=target_priority)
        for greater_target_element in greater_target_elements:
            greater_target_element.priority = greater_target_element.priority + 1
            greater_target_element.save()
        new_project_member = ProjectMember(member=our_element_collaborator,
                                           project_mentor=our_element_superior,
                                           project=selected_project, state="Collaborator",
                                           priority=target_priority, tasks=our_element.tasks,
                                           is_email_sent=our_element.is_email_sent)
        new_project_member.save()

    if target_list == 'draggable-learners':
        greater_target_elements = ProjectLearner.objects.filter(project=selected_project,
                                                                priority__gte=target_priority)
        for greater_target_element in greater_target_elements:
            greater_target_element.priority = greater_target_element.priority + 1
            greater_target_element.save()

        new_project_learner = ProjectLearner(learner=our_element_collaborator,
                                             project_mentor=our_element_superior,
                                             project=selected_project, state="Collaborator",
                                             priority=target_priority, tasks=our_element.tasks,
                                             is_email_sent=our_element.is_email_sent)
        new_project_learner.save()

    our_element.delete()


def is_project_learner(selected_project, user):
    return ProjectLearner.objects.filter(project=selected_project, learner=user).count() == 1


def is_inside_project(project, user):
    return ProjectSupervisor.objects.filter(project=project, supervisor=user).count() + \
           ProjectMentor.objects.filter(project=project, mentor=user).count() + \
           ProjectMember.objects.filter(project=project, member=user).count() + \
           ProjectLearner.objects.filter(project=project, learner=user).count() + \
           int(project.expert == user) + int(user == project.main_supervisor)


def is_member_in_forbidden_state(selected_project, user):
    return (selected_project.status == "New" or selected_project.status == "Pending") and is_project_member(
        selected_project, user)


def make_user_collaborator(position, collaborator_pk):
    """
    position: position of someone who is supposed to be added on our project
    collaborator_pk: primary key of either of these: ProjectSupervisor, ProjectMentor, ProjectMember, ProjectLearner

    position determines which primary key it is

    returns: True if it's added as main supervisor and false if it's not
    """
    accepted_as_main_supervisor = False
    if position == "Supervisor":
        project_collaborator = ProjectSupervisor.objects.get(pk=collaborator_pk)
        collaborator_user = project_collaborator.supervisor

        if project_collaborator.project.main_supervisor is None:
            the_project = project_collaborator.project
            the_project.main_supervisor = project_collaborator.supervisor
            the_project.save()
            Log(user=project_collaborator.supervisor,
                log=f'Has become main supervisor in project "{the_project}"').save()
            project_collaborator.delete()

            accepted_as_main_supervisor = True

            # Send email
            email_subject = "You got accepted as main supervisor"
            email_content = f"""
You got accepted on project "{the_project.title}"

you can visit it by going to the link below:
link: https://tecvico.com/dashboard/projects/{the_project.project_type}?pk={the_project.pk}

Regards,
Tecvico
"""
            destination_email = the_project.main_supervisor.email
            send_notification(the_project.title, "You got accepted as main supervisor",
                              the_project.main_supervisor,
                              reverse('dashboard-projects-page', args=[the_project.project_type]))

        else:
            # set priority to last (add to the last of the list)
            last_priority = ProjectSupervisor.objects.filter(project=project_collaborator.project).last().priority
            project_collaborator.state = "Collaborator"
            project_collaborator.priority = last_priority + 1
            project_collaborator.save()
            Log(user=project_collaborator.supervisor,
                log=f'Has become a supervisor in project "{project_collaborator.project}"').save()

            send_notification(project_collaborator.project.title, "You got accepted as supervisor",
                              project_collaborator.supervisor, reverse('dashboard-projects-page',
                                                                       args=[
                                                                           project_collaborator.project.project_type]))

            # Send email
            email_subject = "You got accepted as supervisor"
            email_content = f"""
            You got accepted on project "{project_collaborator.project.title}"

            you can visit it by going to the link below:
            link: https://tecvico.com/dashboard/projects/{project_collaborator.project.project_type}?pk={project_collaborator.project.pk}

            Regards,
            Tecvico
            """
            destination_email = project_collaborator.supervisor.email

    if position == "Mentor":
        project_collaborator = ProjectMentor.objects.get(pk=collaborator_pk)
        collaborator_user = project_collaborator.mentor

        last_priority = ProjectMentor.objects.filter(project=project_collaborator.project).last().priority
        project_collaborator.priority = last_priority + 1
        project_collaborator.save()
        Log(user=project_collaborator.mentor,
            log=f'Has become a mentor in project "{project_collaborator.project}"').save()

        send_notification(project_collaborator.project.title, "You got accepted as mentor",
                          project_collaborator.mentor, reverse('dashboard-projects-page',
                                                               args=[project_collaborator.project.project_type]))

        # Send email
        email_subject = "You got accepted as mentor"
        email_content = f"""
        You got accepted on project "{project_collaborator.project.title}"

        you can visit it by going to the link below:
        link: https://tecvico.com/dashboard/projects/{project_collaborator.project.project_type}?pk={project_collaborator.project.pk}

        Regards,
        Tecvico
                """
        destination_email = project_collaborator.mentor.email

    if position == "Member":
        project_collaborator = ProjectMember.objects.get(pk=collaborator_pk)
        collaborator_user = project_collaborator.member

        last_priority = ProjectMember.objects.filter(project=project_collaborator.project).last().priority
        project_collaborator.priority = last_priority + 1
        project_collaborator.save()
        Log(user=project_collaborator.member,
            log=f'Has become a member in project "{project_collaborator.project}"').save()

        send_notification(project_collaborator.project.title, "You got accepted as member",
                          project_collaborator.member, reverse('dashboard-projects-page',
                                                               args=[project_collaborator.project.project_type]))

        # Send email
        email_subject = "You got accepted as member"
        email_content = f"""
You got accepted on project "{project_collaborator.project.title}"

you can visit it by going to the link below:
link: https://tecvico.com/dashboard/projects/{project_collaborator.project.project_type}?pk={project_collaborator.project.pk}

Regards,
Tecvico
                        """
        destination_email = project_collaborator.member.email

    if position == "Learner":
        project_collaborator = ProjectLearner.objects.get(pk=collaborator_pk)
        collaborator_user = project_collaborator.learner

        last_priority = ProjectLearner.objects.filter(project=project_collaborator.project).last().priority
        project_collaborator.priority = last_priority + 1
        project_collaborator.save()
        Log(user=project_collaborator.learner,
            log=f'Has become a learner in project "{project_collaborator.project}"').save()

        send_notification(project_collaborator.project.title, "You got accepted as learner",
                          project_collaborator.learner, reverse('dashboard-projects-page',
                                                                args=[project_collaborator.project.project_type]))

        # Send email
        email_subject = "You got accepted as learner"
        email_content = f"""
You got accepted on project "{project_collaborator.project.title}"

you can visit it by going to the link below:
link: https://tecvico.com/dashboard/projects/{project_collaborator.project.project_type}?pk={project_collaborator.project.pk}

Regards,
Tecvico
                                """
        destination_email = project_collaborator.learner.email

    threading.Thread(target=send_new_email,
                     args=(email_subject, email_content, destination_email)).start()

    if not accepted_as_main_supervisor:
        project_collaborator.state = "Collaborator"
        project_collaborator.save()


def get_collaborator_thresholds(project):
    supervisor_threshold = get_project_required_responsibility_fee(project.project_value, "Supervisor")
    mentor_threshold = get_project_required_responsibility_fee(project.project_value, "Mentor")
    member_threshold = get_project_required_responsibility_fee(project.project_value, "Member")

    learner_numbers = project.projectlearner_set.filter(state='Collaborator').count()
    learner_threshold = get_project_required_responsibility_fee(project.project_value, "Learner",
                                                                n_learner=learner_numbers)
    return supervisor_threshold, mentor_threshold, member_threshold, learner_threshold


def add_members_to_context(context, selected_project):
    if selected_project.project_type == "Research":
        supervisor_threshold, mentor_threshold, member_threshold, learner_threshold = get_collaborator_thresholds(
            selected_project)

        context['all_supervisors'] = User.objects.filter(memberprofile__position="Supervisor",
                                                         memberprofile__balance__gte=supervisor_threshold
                                                         ).exclude(projectsupervisor__project=selected_project)
        if selected_project.main_supervisor is not None:
            context['all_supervisors'] = context['all_supervisors'].exclude(username=
                                                                            selected_project.main_supervisor.username)
        context['all_mentors'] = User.objects.filter(memberprofile__position="Mentor",
                                                     memberprofile__balance__gte=mentor_threshold
                                                     ).exclude(project_mentor_mentor__project=selected_project)
        context['all_members'] = User.objects.filter(memberprofile__position="Member",
                                                     memberprofile__balance__gte=member_threshold
                                                     ).exclude(project_member_member__project=selected_project)
        context['all_learners'] = User.objects.filter(memberprofile__position="Learner",
                                                      memberprofile__balance__gte=learner_threshold
                                                      ).exclude(project_learner_learner__project=selected_project)
    elif selected_project.project_type == 'Competition':
        context['all_supervisors'] = User.objects.filter(memberprofile__position="Supervisor").exclude(
            projectsupervisor__project=selected_project)
        if selected_project.main_supervisor is not None:
            context['all_supervisors'] = context['all_supervisors'].exclude(username=
                                                                            selected_project.main_supervisor.username)
        context['all_mentors'] = User.objects.filter(memberprofile__position="Mentor").exclude(
            project_mentor_mentor__project=selected_project)
        context['all_members'] = User.objects.filter(memberprofile__position="Member").exclude(
            project_member_member__project=selected_project)
        context['all_learners'] = User.objects.filter(memberprofile__position="Learner").exclude(
            project_learner_learner__project=selected_project)
    elif selected_project.project_type == 'Industrial':
        context['all_supervisors'] = User.objects.filter(Q(memberprofile__position="Supervisor",
                                                           memberprofile__is_guest=False) &
                                                         ~Q(projectsupervisor__project=selected_project) &
                                                         ~Q(project_expert__pk=selected_project.pk) &
                                                         ~Q(project_main_supervisor__pk=selected_project.pk))

        context['all_mentors'] = User.objects.filter(Q(memberprofile__position="Mentor",
                                                       memberprofile__is_guest=False) &
                                                     ~Q(project_mentor_mentor__project=selected_project) &
                                                     ~Q(project_expert__pk=selected_project.pk))
        context['all_members'] = User.objects.filter(Q(memberprofile__position="Member",
                                                       memberprofile__is_guest=False) &
                                                     ~Q(project_expert__pk=selected_project.pk) &
                                                     ~Q(project_member_member__project=selected_project))
        context['all_learners'] = User.objects.filter(Q(memberprofile__position="Learner",
                                                        memberprofile__is_guest=False) &
                                                      ~Q(project_learner_learner__project=selected_project) &
                                                      ~Q(project_expert__pk=selected_project.pk)).exclude()


def is_user_collaborator(project, user):
    return ProjectSupervisor.objects.filter(project=project, supervisor=user, state="Collaborator").count() + \
           ProjectMentor.objects.filter(project=project, mentor=user, state="Collaborator").count() + \
           ProjectMember.objects.filter(project=project, member=user, state="Collaborator").count() + \
           ProjectLearner.objects.filter(project=project, learner=user, state="Collaborator").count() + \
           int(project.main_supervisor == user)


def is_user_inside_the_project(project, user):
    return ProjectSupervisor.objects.filter(project=project, supervisor=user).count() + \
           ProjectMentor.objects.filter(project=project, mentor=user).count() + \
           ProjectMember.objects.filter(project=project, member=user).count() + \
           ProjectLearner.objects.filter(project=project, learner=user).count() + \
           int(project.main_supervisor == user)


def get_limit_on_projects(user):
    if user.memberprofile.position == "Member" or user.memberprofile.position == "Learner":
        return Project.objects.filter(Q(projectsupervisor__supervisor=user, is_valid=True)
                                      | Q(projectmentor__mentor=user, is_valid=True)
                                      | Q(projectmember__member=user, is_valid=True)
                                      | Q(projectlearner__learner=user, is_valid=True)).distinct().count()
    else:
        return 0


def is_competition_manager(user):
    return CompetitionManager.objects.filter(user=user).count()


def get_new_project_numbers():
    return Project.objects.filter(is_valid=False, status="Inspecting",
                                  project_type="Research").count() + Project.objects.filter(
        status="Inspecting For Signature",
        projectcontractreply__isnull=False).distinct().count()
