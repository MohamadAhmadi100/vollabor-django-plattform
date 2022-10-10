import datetime

from django.contrib.auth.models import User

from dashboard.utilities import send_notification, user_has_memberprofile
from ivc_website.models import Project, ProjectSupervisor, ProjectMentor, ProjectMember, ProjectLearner
from django.urls import reverse


def add_new_project(form, owner, info_form=None):
    new_project = form.save(commit=False)  # new project based on form

    new_project.owner = owner  # assign project owner

    if new_project.start_date is not None or new_project.end_date is not None:
        both_are_not_none = new_project.start_date is not None and new_project.end_date is not None
        if both_are_not_none and new_project.start_date > new_project.end_date:
            return False, "Project start date should be earlier than project end date!", None

        if new_project.start_date is not None and new_project.start_date < datetime.date.today():
            return False, "Project start date is earlier than today", None

        if new_project.end_date is not None and new_project.end_date < datetime.date.today():
            return False, "Project end date is earlier than today", None

    if not user_has_memberprofile(owner):  # if company is defining a project (Industrial)
        if new_project.fund > 10000:
            new_project.project_type = "Industrial"
        else:
            new_project.project_type = "Research"

        if info_form is not None:  # Which should not be!
            if info_form.is_valid():
                project_information_file = info_form.cleaned_data.get('project_information')
                new_project.project_information = project_information_file
                new_project.save()

    new_project.save()
    return True, None, new_project.pk


def make_owner_a_collaborator(selected_project):
    if selected_project.owner.memberprofile.position == "Supervisor":
        ProjectSupervisor(project=selected_project, supervisor=selected_project.owner,
                          state='Collaborator').save()
    if selected_project.owner.memberprofile.position == "Mentor":
        ProjectMentor(project=selected_project, mentor=selected_project.owner,
                      project_supervisor=selected_project.main_supervisor,
                      state='Collaborator').save()
    if selected_project.owner.memberprofile.position == "Member":
        ProjectMember(project=selected_project, member=selected_project.owner,
                      project_mentor=selected_project.main_supervisor,
                      state='Collaborator').save()
    if selected_project.owner.memberprofile.position == "Learner":
        ProjectLearner(project=selected_project, learner=selected_project.owner,
                       project_mentor=selected_project.main_supervisor,
                       state='Collaborator').save()


def accept_new_project(selected_project, accept_supervisor):
    # make project valid
    selected_project.is_valid = True
    selected_project.status = "New"

    """
    at first we notify the owner that his project got accepted
    """
    send_notification(selected_project.title, "The project you defined got accepted by Tecvico",
                      selected_project.owner, reverse('dashboard-projects-page', args=[selected_project.project_type]))

    if not accept_supervisor:
        selected_project.main_supervisor = None

    else:  # in case when someone assigned a supervisor and superusers accept him
        if selected_project.main_supervisor is not None:  # just for security check
            """
            then we send a notification to main supervisor:
            """
            send_notification(selected_project.title, "You got accepted as main supervisor",
                              selected_project.main_supervisor,
                              reverse('dashboard-projects-page', args=[selected_project.project_type]))

    selected_project.save()

    if selected_project.project_type == "Research" and selected_project.owner != selected_project.main_supervisor:
        make_owner_a_collaborator(selected_project)
