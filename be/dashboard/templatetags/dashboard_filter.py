from django import template
from django.contrib.auth.models import User
from django.db.models import Q

from coin.models import PersonExperienceBadge
from coin.util import get_project_required_responsibility_fee
from dashboard.forms import MeetingForm
from dashboard.models import WeeklyMeetingAttendee, ProjectRating, ProposalOpinion, Reviewer
from dashboard.utils.html_info_utils import _get_requested_projects_length, _get_pending_projects_length, \
    _get_new_projects_length, _get_done_projects_length, _get_on_hold_projects_length, _get_ongoing_projects_length
from ivc_website.models import ProjectMember, ProjectMentor, ProjectSupervisor, ProjectLearner, \
    ProjectContract, ProjectContractReply, ProjectProposal, ProjectArea
from users.models import MemberProfile
from competition.models import CompetitionManager
from dashboard.utilities import get_project_collaborators, get_limit_on_projects, competition_manager_eligible_to_see

register = template.Library()


@register.filter
def has_experience_badge(user):
    return PersonExperienceBadge.objects.filter(user=user).count()


@register.filter
def get_experience_badges(user):
    return PersonExperienceBadge.objects.filter(user=user)


@register.filter
def all_proposals_have_been_scored(project, user):
    all_project_proposal_numbers = ProjectProposal.objects.filter(project_supervisor__project=project).count()
    scored_project_proposal_numbers = ProposalOpinion.objects.filter(proposal__project_supervisor__project=project,
                                                                     reviewer__user=user).values('proposal'
                                                                                                 ).distinct().count()

    return all_project_proposal_numbers == scored_project_proposal_numbers


@register.filter
def get_required_responsibility_fee(project, position):
    learner_numbers = project.projectlearner_set.filter(state="Collaborator").count()
    return get_project_required_responsibility_fee(project.project_value, position, learner_numbers)


@register.filter
def multiply(a, b):
    return a * b


@register.filter
def get_class_background(proposal):
    result_dict = {
        'Golden': 'bg-warning text-dark',
        'Silver': 'bg-secondary text-white',
        'Bronze': 'bg-danger text-white',
        'Normal': 'bg-dark text-white'
    }
    return result_dict[proposal.project_class]


@register.filter
def has_a_scored_proposal(user, project):
    return ProposalOpinion.objects.filter(proposal__project_supervisor__supervisor=user,
                                          proposal__project_supervisor__project=project).count()


@register.filter
def is_project_reviewer_exists(project):
    return Reviewer.objects.filter(project=project).count()


@register.filter
def form_is_completed(project_area):
    if project_area.projectexpertareaitem_set.filter(agree=None).count():
        return False
    else:
        return True


@register.filter
def get_mean_score(proposal, reviewer):
    submitted_scores = ProposalOpinion.objects.filter(proposal=proposal, reviewer=reviewer).values_list('score',
                                                                                                        flat=True)
    try:
        return sum(submitted_scores) / len(submitted_scores)
    except ZeroDivisionError:
        return "NG"


@register.filter
def has_been_scored(project_proposal, user):
    return ProposalOpinion.objects.filter(proposal=project_proposal, reviewer__user=user).count()


@register.filter
def get_scored_numbers(reviewer):
    return ProjectProposal.objects.filter(proposalopinion__reviewer=reviewer).distinct().count()


@register.filter
def to_str(number):
    return str(number)


@register.filter
def no_others_area(project):
    return project.projectarea_set.filter(area__confirmed=False).count() == 0


@register.filter
def is_competition_manager(user):
    return CompetitionManager.objects.filter(user=user).count()


@register.filter
def get_rating_number(project, user):
    return ProjectRating.objects.filter(project=project, collaborator=user).count()


@register.filter
def get_rating(project, user):
    ratings = ProjectRating.objects.filter(project=project, collaborator=user)
    rating_sum = 0

    for rating in ratings:
        rating_sum += rating.rating
    if ratings.count() > 0:
        return int(rating_sum / ratings.count())
    else:
        return 0


@register.filter
def get_list(dictionary, key):
    return dictionary.getlist(key)


@register.filter
def get_meeting_form(project):
    return MeetingForm(instance=project)


@register.filter
def calculate_id(loop_counter, page_number):
    return loop_counter + ((page_number - 1) * 7)


@register.filter
def get_request_numbers_all(project):
    return project.projectmember_set.filter(state="Accepted Pending").count() + \
           project.projectmentor_set.filter(state="Accepted Pending").count() + \
           project.projectsupervisor_set.filter(state="Accepted Pending").count() + \
           project.projectlearner_set.filter(state="Accepted Pending").count()


@register.filter
def is_project_supervisor(project, user):
    if project.projectsupervisor_set.filter(supervisor=user).count():
        return True
    return False


@register.filter
def is_project_accepted_supervisor(project, user):
    if project.projectsupervisor_set.filter(supervisor=user, state="Collaborator").count():
        return True
    return False


@register.filter
def get_project_supervisor_by_priority(project, priority):
    if ProjectSupervisor.objects.filter(project=project, priority=priority, state="Collaborator").count():
        return ProjectSupervisor.objects.filter(project=project, priority=priority)[0]
    else:
        return None


@register.filter
def is_project_mentor(project, user):
    if project.projectmentor_set.filter(mentor=user).count():
        return True
    return False


@register.filter
def is_project_accepted_mentor(project, user):
    if project.projectmentor_set.filter(mentor=user, state="Collaborator").count():
        return True
    return False


@register.filter
def is_project_member(project, user):
    if project.projectmember_set.filter(member=user).count():
        return True
    return False


@register.filter
def get_request_numbers_mentor(project):
    return project.projectmember_set.filter(state="Accepted Pending").count() + \
           project.projectmentor_set.filter(state="Accepted Pending").count() + \
           project.projectlearner_set.filter(state="Accepted Pending").count()


@register.filter
def get_collaborators(project):
    """
    Template filter:
    gets project as a parameter and returns its collaborators
    """
    return get_project_collaborators(project)


@register.filter
def get_requested_limit(user):
    return get_limit_on_projects(user)


@register.filter
def is_member_profile(user):
    return MemberProfile.objects.filter(user=user).count()


@register.filter
def get_project_supervisors(project):
    """
    gets project as a parameter and returns its supervisors
    """

    # ---- previous version
    # result_set = MemberProfile.objects.filter(projectsupervisor__project=project, projectsupervisor__pending=False,
    #                                           projectsupervisor__accepted=True).distinct()
    # if project.main_supervisor is not None:
    #     result_set |= MemberProfile.objects.filter(industrial_name=project.main_supervisor.industrial_name).distinct()

    # -- now:
    result_set = User.objects.filter(projectsupervisor__project=project,
                                     projectsupervisor__state="Collaborator").distinct()

    if project.main_supervisor is not None:
        result_set |= User.objects.filter(id=project.main_supervisor.id).distinct()

    return result_set


@register.filter
def get_project_supervisors_without_main(project):
    return ProjectSupervisor.objects.filter(project=project, state="Collaborator").distinct()


@register.filter
def get_project_mentors(project):
    """
    gets project as a parameter and returns its mentors
    """

    # --- previous version
    # project_mentors = ProjectMentor.objects.filter(project=project, pending=False, accepted=True)
    # mentor_list = []
    #
    # for project_mentor in project_mentors:
    #     mentor_list.append(project_mentor.mentor)

    return User.objects.filter(project_mentor_mentor__project=project,
                               project_mentor_mentor__state="Collaborator").distinct()


@register.filter
def get_project_members(project):
    """
    gets project as a parameter and returns its members
    """

    # --- previous version
    # project_members = ProjectMember.objects.filter(project=project, pending=False, accepted=True)
    # member_list = []
    #
    # for project_member in project_members:
    #     member_list.append(project_member.member)

    return User.objects.filter(project_member_member__project=project,
                               project_member_member__state="Collaborator").distinct()


@register.filter
def get_project_learners(project):
    """
    gets project as a parameter and returns its members
    """

    # --- previous version
    # project_learners = ProjectLearner.objects.filter(project=project, pending=False, accepted=True)
    # learner_list = []
    #
    # for project_learner in project_learners:
    #     learner_list.append(project_learner.learner)

    return User.objects.filter(project_learner_learner__project=project,
                               project_learner_learner__state="Collaborator").distinct()


@register.filter
def get_project_project_mentors(project):
    return ProjectMentor.objects.filter(project=project, state="Collaborator")


@register.filter
def get_project_project_members(project):
    # --- previous version
    # if user.is_superuser:  # in that case he should see all members
    #     return ProjectMember.objects.filter(project=project)
    # else:
    #     if userprofile.position == "Mentor":
    #         return ProjectMember.objects.filter(project=project, project_mentor=userprofile)
    #     else:
    #         result_set = ProjectMember.objects.filter(project=project, project_mentor=userprofile) | \
    #                      ProjectMember.objects.filter(project=project, project__main_supervisor=userprofile)
    #         project_mentors = get_user_mentors(project, userprofile)
    #         for project_mentor in project_mentors:
    #             result_set |= ProjectMember.objects.filter(project=project, project_mentor=project_mentor.mentor)
    #
    #         return result_set

    return ProjectMember.objects.filter(project=project, state="Collaborator")


@register.filter
def get_project_project_learners(project):
    # -- previous version
    # if userprofile.user.is_superuser:  # in that case he should see all members
    #     return ProjectLearner.objects.filter(project=project, pending=False, accepted=True)
    # else:
    #     if userprofile.position == "Mentor":
    #         return ProjectLearner.objects.filter(project=project, project_mentor=userprofile)
    #     else:
    #         result_set = ProjectLearner.objects.filter(project=project, project_mentor=userprofile, pending=False,
    #                                                    accepted=True) \
    #                      | \
    #                      ProjectLearner.objects.filter(project=project, project__main_supervisor=userprofile,
    #                                                    pending=False, accepted=True)
    #         project_mentors = get_user_mentors(project, userprofile)
    #         for project_mentor in project_mentors:
    #             result_set |= ProjectLearner.objects.filter(project=project, project_mentor=project_mentor.mentor,
    #                                                         pending=False, accepted=True)
    #
    #         return result_set
    return ProjectLearner.objects.filter(project=project, state="Collaborator")


@register.filter
def get_accepted_pending_collaborators(project):
    """
    gets project as a parameter and returns its collaborator which they requested before
    """
    # -- previous version
    # collaborators = []
    #
    # project_learners = project.projectlearner_set.all().filter(pending=True, accepted=True)
    # for project_learner in project_learners:
    #     collaborators.append(project_learner.learner)
    #
    # project_members = project.projectmember_set.all().filter(pending=True, accepted=True)
    # for project_member in project_members:
    #     collaborators.append(project_member.member)
    #
    # project_mentors = project.projectmentor_set.all().filter(pending=True, accepted=True)
    # for project_mentor in project_mentors:
    #     collaborators.append(project_mentor.mentor)
    #
    # project_supervisors = project.projectsupervisor_set.all().filter(pending=True, accepted=True)
    # for project_supervisor in project_supervisors:
    #     collaborators.append(project_supervisor.supervisor)
    #
    # return collaborators
    return User.objects.filter(Q(project_learner_learner__project=project,
                                 project_learner_learner__state="Accepted Pending") |
                               Q(project_member_member__project=project,
                                 project_member_member__state="Accepted Pending") |
                               Q(project_mentor_mentor__project=project,
                                 project_mentor_mentor__state="Accepted Pending") |
                               Q(projectsupervisor__project=project,
                                 projectsupervisor__state="Accepted Pending"))


@register.filter
def get_accepted_pending_collaborators(project):
    return User.objects.filter(Q(project_learner_learner__project=project,
                                 project_learner_learner__state="Accepted Pending") |
                               Q(project_member_member__project=project,
                                 project_member_member__state="Accepted Pending") |
                               Q(project_mentor_mentor__project=project,
                                 project_mentor_mentor__state="Accepted Pending") |
                               Q(projectsupervisor__project=project,
                                 projectsupervisor__state="Accepted Pending") |
                               Q(project_learner_learner__project=project,
                                 project_learner_learner__state="Accepted Pending") |
                               Q(project_member_member__project=project,
                                 project_member_member__state="Accepted Pending") |
                               Q(project_mentor_mentor__project=project,
                                 project_mentor_mentor__state="Accepted Pending") |
                               Q(projectsupervisor__project=project,
                                 projectsupervisor__state="Accepted Pending"))


@register.filter
def is_inside_project(project, user):
    return ProjectSupervisor.objects.filter(project=project, supervisor=user).count() + \
           ProjectMentor.objects.filter(project=project, mentor=user).count() + \
           ProjectMember.objects.filter(project=project, member=user).count() + \
           ProjectLearner.objects.filter(project=project, learner=user).count()


@register.filter
def is_able_to_edit_status(project):
    contract_has_been_sent_to_owner = ProjectContract.objects.filter(project=project, user=project.owner).count()
    if project.project_type == "Industrial" and not contract_has_been_sent_to_owner:
        return False
    else:
        return True


@register.filter
def get_pending_collaborators(project):
    """
    gets project as a parameter and returns its collaborator which they're added by supervisor (or mentor)
    """
    # -- previous version
    # collaborators = []
    #
    # project_learners = project.projectlearner_set.all().filter(pending=True, accepted=False)
    # for project_learner in project_learners:
    #     collaborators.append(project_learner.learner)
    #
    # project_members = project.projectmember_set.all().filter(pending=True, accepted=False)
    # for project_member in project_members:
    #     collaborators.append(project_member.member)
    #
    # project_mentors = project.projectmentor_set.all().filter(pending=True, accepted=False)
    # for project_mentor in project_mentors:
    #     collaborators.append(project_mentor.mentor)
    #
    # project_supervisors = project.projectsupervisor_set.all().filter(pending=True, accepted=False)
    # for project_supervisor in project_supervisors:
    #     collaborators.append(project_supervisor.supervisor)
    #
    # return collaborators
    return User.objects.filter(Q(project_learner_learner__project=project, project_learner_learner__state="pending") |
                               Q(project_member_member__project=project, project_member_member__state="pending") |
                               Q(project_mentor_mentor__project=project, project_mentor_mentor__state="pending") |
                               Q(projectsupervisor__project=project, projectsupervisor__state="pending"))


@register.filter
def get_waiting_for_acceptance_collaborators(project):
    """
    gets project as a parameter and returns its collaborator which they're added by supervisor (or mentor)
    """
    # -- previous version
    # collaborators = []
    #
    # project_learners = project.projectlearner_set.all().filter(pending=False, accepted=False)
    # for project_learner in project_learners:
    #     collaborators.append(project_learner.learner)
    #
    # project_members = project.projectmember_set.all().filter(pending=False, accepted=False)
    # for project_member in project_members:
    #     collaborators.append(project_member.member)
    #
    # project_mentors = project.projectmentor_set.all().filter(pending=False, accepted=False)
    # for project_mentor in project_mentors:
    #     collaborators.append(project_mentor.mentor)
    #
    # project_supervisors = project.projectsupervisor_set.all().filter(pending=False, accepted=False)
    # for project_supervisor in project_supervisors:
    #     collaborators.append(project_supervisor.supervisor)
    #
    # return collaborators
    return User.objects.filter(Q(project_learner_learner__project=project,
                                 project_learner_learner__state="Waiting For Acceptance") |
                               Q(project_member_member__project=project,
                                 project_member_member__state="Waiting For Acceptance") |
                               Q(project_mentor_mentor__project=project,
                                 project_mentor_mentor__state="Waiting For Acceptance") |
                               Q(projectsupervisor__project=project,
                                 projectsupervisor__state="Waiting For Acceptance"))


@register.filter
def get_item(dictionary, key):
    """
    gets dictionary and key as a parameter and returns value of dictionary
    """
    return dictionary[key]


@register.filter
def get_contract_reply_url(project, user):
    return ProjectContractReply.objects.get(project=project, user=user, contract_type='Collaborator').contract_file.url


@register.filter
def delete_filter(url, given_filter):
    return url.replace(f"&filter={given_filter}", "").replace(f"filter={given_filter}", "")


@register.filter
def get_proposal_url(project, user):
    return ProjectProposal.objects.get(project_supervisor__project=project,
                                       project_supervisor__user=user).proposal_file.url


@register.filter
def is_competition_manager_eligible_to_see(project):
    return competition_manager_eligible_to_see(project)


@register.filter
def get_ongoing_projects_length(user):
    return _get_ongoing_projects_length(user)


@register.filter
def get_distinct_experts(project):
    result = []
    project_areas = ProjectArea.objects.filter(project=project)
    for project_area in project_areas:
        if project_area.expert not in result:
            result.append(project_area.expert)
    return result


@register.filter
def get_areas(project):
    result = ""
    for area in project.projectarea_set.all().values('area'):
        result += f"{area['area']}, "

    return (result[:75] + '..') if len(result) > 75 else result[:-2]


@register.filter
def get_on_hold_projects_length(user):
    return _get_on_hold_projects_length(user)


@register.filter
def get_done_projects_length(user):
    return _get_done_projects_length(user)


@register.filter
def get_new_projects_length(user):
    return _get_new_projects_length(user)


@register.filter
def get_pending_projects_length(user):
    return _get_pending_projects_length(user)


@register.filter
def get_requested_projects_length(user):
    return _get_requested_projects_length(user)


@register.filter
def is_attended(time, user):
    return WeeklyMeetingAttendee.objects.filter(weekly_meeting=time, attendee=user,
                                                acceptable_absence=False).count()


@register.filter
def has_acceptable_absence(time, user):
    return WeeklyMeetingAttendee.objects.filter(weekly_meeting=time, attendee=user,
                                                acceptable_absence=True).count()
