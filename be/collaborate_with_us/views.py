import threading

import jdatetime
import django.utils.timezone as timezone

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from collaborate_with_us.forms import CollaborateStaffForm, ApplicationDeadlineForm
from collaborate_with_us.models import CollaborateStaffInterest, CollaborateStaffProject, ApplicationDeadline, \
    CollaborateStaff, StaffManager
from dashboard.utilities import send_notification
from ivc_project.email_sender import send_new_email
from ivc_website.models import Project


def collaborate_with_us(request):
    collaborate_stuff_form = CollaborateStaffForm()
    application_deadline = ApplicationDeadline.objects.get(type='Course')

    tehran_tz = timezone.get_fixed_timezone(270)
    now = jdatetime.datetime.now(tz=tehran_tz)

    deadline_is_passed = (application_deadline.to_time - now).total_seconds() < 0

    if request.method == "POST":
        collaborate_stuff_form = CollaborateStaffForm(request.POST, request.FILES)
        if collaborate_stuff_form.is_valid():
            collaborate_stuff = collaborate_stuff_form.save()
            interest_areas = request.POST.getlist('interest-areas')
            for interest in interest_areas:
                CollaborateStaffInterest(staff=collaborate_stuff, interest=interest).save()
                if interest == "Others":
                    collaborate_stuff.recommendation = request.POST['recommendation']
                    collaborate_stuff.save()

            if collaborate_stuff.is_member:
                projects_collaborated = request.POST.getlist('projects-collaborated')
                if projects_collaborated[0] == "Without Project":
                    collaborate_stuff.without_project = True
                    collaborate_stuff.save()
                else:
                    for project_id in projects_collaborated:
                        project = Project.objects.get(id=project_id)
                        CollaborateStaffProject(staff=collaborate_stuff, project=project).save()

            for manager in StaffManager.objects.all():
                send_notification("Collaborate With us", "Someone sent a new collaboration application", manager.user,
                                  reverse('staff-manager-page'))

            email_subject = "Someone requested to be the course collaborator :)"
            email_content = f"""
Candidate name: {collaborate_stuff.first_name} {collaborate_stuff.last_name}
City: {collaborate_stuff.city}
Email: {collaborate_stuff.email}
Phone: ({collaborate_stuff.phone_region.upper()}) {collaborate_stuff.phone}
CV: https://tecvico.com/{collaborate_stuff.cv.url}
Eligibility Reason : {collaborate_stuff.about}
Time can spend: {collaborate_stuff.time_spend} Hours
Interest:\n"""
            for interest in collaborate_stuff.collaboratestaffinterest_set.all():
                email_content += f'* {interest.interest}\n'
            if collaborate_stuff.recommendation:
                email_content += f'Recommendation: {collaborate_stuff.recommendation}\n'
            email_content += f"Is member: {collaborate_stuff.is_member}\n"
            if collaborate_stuff.is_member:
                email_content += 'Projects:\n'
                if collaborate_stuff.without_project:
                    email_content += "Without Project :("
                else:
                    for staff_project in collaborate_stuff.collaboratestaffproject_set.all():
                        email_content += f" * {staff_project.project.title}\n"

            threading.Thread(target=send_new_email,
                             args=(email_subject, email_content, "education@tecvico.com")).start()
            messages.success(request, "Application has been submitted successfully. We will notify you soon :)")
            return HttpResponseRedirect(request.path_info)  # redirect to the same page
        else:
            messages.error(request, "An error occurred, look at the form to see what it is")

    context = {
        'form': collaborate_stuff_form,
        'projects': Project.objects.filter(is_valid=True),
        'deadline_is_passed': deadline_is_passed,
        'deadline_time': application_deadline
    }
    return render(request, 'collaborate_with_us/collaborate_with_us.html', context)


@login_required
def manage_staff(request):
    if StaffManager.objects.filter(user=request.user).count() == 0:
        return render(request, 'ivc_website/403.html')

    application_deadline = ApplicationDeadline.objects.get(type="Course")
    application_deadline_form = ApplicationDeadlineForm(instance=application_deadline)

    if request.method == "POST":
        application_deadline_form = ApplicationDeadlineForm(request.POST, instance=application_deadline)
        if application_deadline_form.is_valid():
            application_deadline_form.save()
            messages.success(request, "Deadline has been changed successfully")
            return HttpResponseRedirect(request.path_info)  # redirect to the same page
        else:
            messages.error(request, 'An error has been occurred')

    paginator = Paginator(CollaborateStaff.objects.all(), 5)
    current_page_number = request.GET.get('page')
    page_obj = paginator.get_page(current_page_number)
    context = {
        'deadline_form': application_deadline_form,
        'applications': page_obj
    }
    return render(request, 'collaborate_with_us/staff_manager.html', context)
