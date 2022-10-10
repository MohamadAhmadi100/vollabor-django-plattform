from django.contrib.auth.models import User
from django.db.models import Q

from dashboard.utilities import user_has_memberprofile
from ivc_website.models import ProjectMentor, ProjectMember, ProjectLearner, ProjectSupervisor
from users.models import MemberProfile


def handle_autocomplete_search_in_project_management(request, selected_project):
    if selected_project.project_type == "Research":
        if request.GET.get("meta") == 'Supervisor':
            for term in request.GET.get('term').split():
                # -- previous version
                # profiles = Memberprofile.objects.filter(user__first_name__icontains=term, position="Supervisor")
                # profiles |= MemberProfile.objects.filter(user__last_name__icontains=term, position="Supervisor")
                # profiles |= MemberProfile.objects.filter(industrial_name__icontains=term, position="Supervisor")
                # profiles = profiles.exclude(pk=selected_project.main_supervisor.pk)  # exclude main supervisor
                # profiles = profiles.exclude(
                #     pk__in=ProjectSupervisor.objects.filter(project=selected_project).values("supervisor"))
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Supervisor") |
                                            Q(last_name__icontains=term, memberprofile__position="Supervisor"))
                users = users.exclude(pk=selected_project.main_supervisor.pk)  # exclude main supervisor
                users = users.exclude(
                    pk__in=ProjectSupervisor.objects.filter(project=selected_project).values('supervisor'))

        if request.GET.get("meta") == 'Mentor':
            for term in request.GET.get('term').split():
                # -- previous version
                # profiles = MemberProfile.objects.filter(user__first_name__icontains=term, position="Mentor")
                # profiles |= MemberProfile.objects.filter(user__last_name__icontains=term, position="Mentor")
                # profiles |= MemberProfile.objects.filter(industrial_name__icontains=term, position="Mentor")
                # profiles = profiles.exclude(
                #     pk__in=ProjectMentor.objects.filter(project=selected_project).values("mentor"))
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Mentor") |
                                            Q(last_name__icontains=term, memberprofile__position="Mentor"))
                users = users.exclude(pk__in=ProjectMentor.objects.filter(project=selected_project).values('mentor'))

        if request.GET.get("meta") == "Member":
            for term in request.GET.get('term').split():
                # -- previous version
                # profiles = MemberProfile.objects.filter(user__first_name__icontains=term, position="Member")
                # profiles |= MemberProfile.objects.filter(user__last_name__icontains=term, position="Member")
                # profiles |= MemberProfile.objects.filter(industrial_name__icontains=term, position="Member")
                # profiles = profiles.exclude(
                #     pk__in=ProjectMember.objects.filter(project=selected_project).values("member"))
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Member") |
                                            Q(last_name__icontains=term, memberprofile__position="Member"))
                users = users.exclude(pk__in=ProjectMember.objects.filter(project=selected_project).values('member'))

        if request.GET.get("meta") == "Learner":
            for term in request.GET.get('term').split():
                # -- previous version
                # profiles = MemberProfile.objects.filter(user__first_name__icontains=term, position="Learner")
                # profiles |= MemberProfile.objects.filter(user__last_name__icontains=term, position="Learner")
                # profiles |= MemberProfile.objects.filter(industrial_name__icontains=term, position="Learner")
                # profiles = profiles.exclude(
                #     pk__in=ProjectLearner.objects.filter(project=selected_project).values("learner"))
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Learner") |
                                            Q(last_name__icontains=term, memberprofile__position="Learner"))
                users = users.exclude(pk__in=ProjectLearner.objects.filter(project=selected_project).values('learner'))

    elif selected_project.project_type == "Industrial":
        if request.GET.get("meta") == 'Supervisor':
            for term in request.GET.get('term').split():
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Supervisor",
                                              memberprofile__is_guest=False) |
                                            Q(last_name__icontains=term, memberprofile__position="Supervisor",
                                              memberprofile__is_guest=False) |
                                            Q(first_name__icontains=term, legalprofile__isnull=False) |
                                            Q(last_name__icontains=term, legalprofile__isnull=False) |
                                            Q(legalprofile__company_name__icontains=term))

                if selected_project.main_supervisor:
                    users = users.exclude(pk=selected_project.main_supervisor.pk)  # exclude main supervisor
                users = users.exclude(
                    pk__in=ProjectSupervisor.objects.filter(project=selected_project).values('supervisor'))

        if request.GET.get("meta") == 'Mentor':
            for term in request.GET.get('term').split():
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Mentor",
                                              memberprofile__is_guest=False) |
                                            Q(last_name__icontains=term, memberprofile__position="Mentor",
                                              memberprofile__is_guest=False) |
                                            Q(first_name__icontains=term, legalprofile__isnull=False) |
                                            Q(last_name__icontains=term, legalprofile__isnull=False) |
                                            Q(legalprofile__company_name__icontains=term))
                users = users.exclude(pk__in=ProjectMentor.objects.filter(project=selected_project).values('mentor'))

        if request.GET.get("meta") == "Member":
            for term in request.GET.get('term').split():
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Member",
                                              memberprofile__is_guest=False) |
                                            Q(last_name__icontains=term, memberprofile__position="Member",
                                              memberprofile__is_guest=False) |
                                            Q(first_name__icontains=term, legalprofile__isnull=False) |
                                            Q(last_name__icontains=term, legalprofile__isnull=False) |
                                            Q(legalprofile__company_name__icontains=term))
                users = users.exclude(pk__in=ProjectMember.objects.filter(project=selected_project).values('member'))

        if request.GET.get("meta") == "Learner":
            for term in request.GET.get('term').split():
                users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position="Learner",
                                              memberprofile__is_guest=False) |
                                            Q(last_name__icontains=term, memberprofile__position="Learner",
                                              memberprofile__is_guest=False) |
                                            Q(first_name__icontains=term, legalprofile__isnull=False) |
                                            Q(last_name__icontains=term, legalprofile__isnull=False) |
                                            Q(legalprofile__company_name__icontains=term))
                users = users.exclude(pk__in=ProjectLearner.objects.filter(project=selected_project).values('learner'))

    users_list = []
    for user in users:
        users_list.append(f"{user.first_name} {user.last_name} ({user.id})")

    return users_list


def handle_autocomplete_search_in_main_dashboard(request):
    # -- previous version
    # profiles_list = []
    #
    # if request.GET.get("meta") == 'Supervisor':
    #     term = request.GET.get('term')
    #     profiles = MemberProfile.objects.filter(user__first_name__icontains=term, position="Supervisor")
    #     profiles |= MemberProfile.objects.filter(user__last_name__icontains=term, position="Supervisor")
    #     profiles |= MemberProfile.objects.filter(industrial_name__icontains=term, position="Supervisor")
    #
    #     for profile in profiles:
    #         profile_info = f"{profile.user.first_name} {profile.user.last_name} ({profile.industrial_name})"
    #         profiles_list.append(profile_info)

    users_list = []

    if request.GET.get('meta') == 'Supervisor':
        term = request.GET.get('term')

        if user_has_memberprofile(request.user):
            users = User.objects.filter(Q(first_name__icontains=term, memberprofile__position='Supervisor') |
                                        Q(last_name__icontains=term, memberprofile__position='Supervisor')).distinct()
        else:
            users = User.objects.filter(Q(first_name__icontains=term, legalprofile__isnull=False) |
                                        Q(last_name__icontains=term, legalprofile__isnull=False) |
                                        Q(legalprofile__company_name__icontains=term) |
                                        Q(first_name__icontains=term, memberprofile__position='Supervisor',
                                          memberprofile__is_guest=False) |
                                        Q(last_name__icontains=term, memberprofile__position='Supervisor',
                                          memberprofile__is_guest=False)).distinct()
        for user in users:
            if user_has_memberprofile(user):
                users_list.append(f"{user.first_name} {user.last_name} ({user.id})")
            else:
                users_list.append(f"{user.legalprofile.company_name} ({user.id})")

    return users_list
