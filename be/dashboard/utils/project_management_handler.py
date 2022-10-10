from django.urls import reverse

from coin.util import get_project_required_responsibility_fee
from dashboard.models import ProposalOpinion, Notification
from django.db.models import Avg, Q

from dashboard.utilities import get_collaborator_thresholds


def get_average_of_proposal_score(user, project):
    proposal_opinions = ProposalOpinion.objects.filter(proposal__project_supervisor__project=project,
                                                       proposal__project_supervisor__supervisor=user)
    if proposal_opinions.count() == 0:  # project is defined before this system (Recent definition method was without
        # proposal)
        return 0
    else:
        return proposal_opinions.aggregate(Avg('score'))['score__avg']


def send_notification(title, description, target, link):
    """
    Even though I know there is another send_notification in utilities.py, I created this function because it is impossible
    to import it here (because of circular import)
    """
    new_notification = Notification(title=title, description=description, target=target, link=link)
    new_notification.save()


def send_notification_to_collaborators_below_the_coin(project):
    supervisor_threshold, mentor_threshold, member_threshold, learner_threshold = get_collaborator_thresholds(project)

    project_supervisors = project.projectsupervisor_set.filter((Q(state="Pending") | Q(state="Accepted Pending")) &
                                                               Q(supervisor__memberprofile__balance__lt=
                                                                 supervisor_threshold))
    project_mentors = project.projectmentor_set.filter((Q(state="Pending") | Q(state="Accepted Pending")) &
                                                       Q(mentor__memberprofile__balance__lt=
                                                         mentor_threshold))
    project_members = project.projectmember_set.filter((Q(state="Pending") | Q(state="Accepted Pending")) &
                                                       Q(member__memberprofile__balance__lt=
                                                         member_threshold))
    project_learners = project.projectlearner_set.filter((Q(state="Pending") | Q(state="Accepted Pending")) &
                                                         Q(learner__memberprofile__balance__lt=
                                                           learner_threshold))

    for project_supervisor in project_supervisors:
        send_notification("Your responsibility fee is not enough",
                          f'The project "{project.title}" needs {supervisor_threshold} responsibility fees while you '
                          f'have ${project_supervisor.supervisor.memberprofile.balance}.'
                          f' Click here to purchase them',

                          project_supervisor.supervisor,
                          reverse('create-checkout-session'))
    for project_mentor in project_mentors:
        send_notification("Your responsibility fee is not enough",
                          f'The project "{project.title}" needs {mentor_threshold} responsibility fees while you have '
                          f'${project_mentor.mentor.memberprofile.balance}.'
                          f' Click here to purchase them',

                          project_mentor.mentor,
                          reverse('create-checkout-session'))

    for project_member in project_members:
        send_notification("Your responsibility fee is not enough",
                          f'The project "{project.title}" needs {member_threshold} responsibility fees while you have '
                          f'${project_member.member.memberprofile.balance}.'
                          f' Click here to purchase them',

                          project_member.member,
                          reverse('create-checkout-session'))

    for project_learner in project_learners:
        send_notification("Your responsibility fee is not enough",
                          f'The project "{project.title}" needs {learner_threshold} responsibility fees while you have'
                          f' ${project_learner.learner.memberprofile.balance}. '
                          f' Click here to purchase them',

                          project_learner.learner,
                          reverse('create-checkout-session'))
