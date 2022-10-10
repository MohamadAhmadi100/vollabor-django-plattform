from ivc_website.models import ProjectSupervisor, Project, ProjectMentor, ProjectMember, ProjectLearner


def _get_ongoing_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user, project__status="Ongoing",
                                            state="Collaborator").count() + \
           Project.objects.filter(main_supervisor=user, status="Ongoing").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="Ongoing",
                                        state="Collaborator").count() + \
           ProjectMember.objects.filter(member=user, project__status="Ongoing",
                                        state="Collaborator").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="Ongoing",
                                         state="Collaborator").count()


def _get_on_hold_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user, project__status="On Hold",
                                            state="Collaborator").count() + \
           Project.objects.filter(main_supervisor=user, status="On Hold").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="On Hold",
                                        state="Collaborator").count() + \
           ProjectMember.objects.filter(member=user, project__status="On Hold",
                                        state="Collaborator").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="On Hold",
                                         state="Collaborator").count()


def _get_done_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user, project__status="Done",
                                            state="Collaborator").count() + \
           Project.objects.filter(main_supervisor=user, status="Done").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="Done",
                                        state="Collaborator").count() + \
           ProjectMember.objects.filter(member=user, project__status="Done",
                                        state="Collaborator").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="Done",
                                         state="Collaborator").count()


def _get_new_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user, project__status="New",
                                            state="Collaborator").count() + \
           Project.objects.filter(main_supervisor=user, status="New").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="New",
                                        state="Collaborator").count() + \
           ProjectMember.objects.filter(member=user, project__status="New",
                                        state="Collaborator").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="New",
                                         state="Collaborator").count()


def _get_pending_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user, project__status="Pending",
                                            state="Collaborator").count() + \
           Project.objects.filter(main_supervisor=user, status="Pending").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="Pending",
                                        state="Collaborator").count() + \
           ProjectMember.objects.filter(member=user, project__status="Pending",
                                        state="Collaborator").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="Pending",
                                         state="Collaborator").count()


def _get_requested_projects_length(user):
    return ProjectSupervisor.objects.filter(supervisor=user,
                                            state="Accepted Pending").count() + \
           ProjectMentor.objects.filter(mentor=user, project__status="New",
                                        state="Accepted Pending").count() + \
           ProjectMember.objects.filter(member=user, project__status="New",
                                        state="Accepted Pending").count() + \
           ProjectLearner.objects.filter(learner=user, project__status="New",
                                         state="Accepted Pending").count()
