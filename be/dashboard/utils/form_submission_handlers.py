import threading

from django.contrib.auth.models import User

from dashboard.project_request_handler import add_new_project
from dashboard.utilities import user_has_memberprofile
from ivc_project.email_sender import send_new_email
from ivc_project.recaptcha_validator import is_recaptcha_valid
from ivc_website.models import Project, ProjectArea, IndustrialArea


def try_to_add_new_project(request, form, info_form=None):
    """
    try to add a new project
    returns: (added_successfully, response
    - added_successfully: True if it is and False if it's not.
    - response: a message to show to the user.
    """

    is_valid = is_recaptcha_valid(request)
    if not is_valid:
        return False, 'reCAPTCHA is invalid, please try again', None

    added_successfully, error, project_pk = add_new_project(form, request.user, info_form)
    if not added_successfully:
        return False, error, None
    else:
        return True, 'Request submitted successfully, wait until we accept your project', project_pk


def save_the_project_area(request, project_pk):
    project = Project.objects.get(pk=project_pk)

    selected_areas = request.POST.getlist('project-area')
    for area in selected_areas:
        if area == "Other":
            other_suggestions = request.POST.get('other-suggestions').split(',')

            for other_suggestion in other_suggestions:
                standard_other_suggestion = other_suggestion.strip().capitalize()
                suggestion_already_exists = IndustrialArea.objects.filter(area__icontains=standard_other_suggestion).count() == 1
                if suggestion_already_exists:
                    new_area = IndustrialArea.objects.get(area__icontains=standard_other_suggestion)
                    area_is_repetitious = ProjectArea.objects.filter(project=project, area=new_area).count() == 1
                    if not area_is_repetitious:
                        ProjectArea(project=project, area=new_area).save()
                else:
                    new_area = IndustrialArea(area=standard_other_suggestion, confirmed=False)
                    new_area.save()
                    ProjectArea(project=project, area=new_area).save()
        else:
            ProjectArea(project=project, area=IndustrialArea.objects.get(area=area)).save()
