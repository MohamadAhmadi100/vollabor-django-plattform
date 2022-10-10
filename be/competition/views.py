from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render

from competition.models import CompetitionManager
from ivc_website.forms import ProjectForm


@login_required
def competition_manager(request):
    if CompetitionManager.objects.filter(user=request.user).count() == 0:
        return render(request, 'ivc_website/403.html')

    project_form = ProjectForm()
    if request.method == "POST":
        project_form = ProjectForm(request.POST)
        if project_form.is_valid():
            the_project = project_form.save(commit=False)
            the_project.owner = request.user
            the_project.project_type = "Competition"
            the_project.status = "New"
            the_project.is_valid = True
            the_project.save()
            messages.success(request, "Project has been defined successfully")
            return HttpResponseRedirect(request.path_info)  # redirect to the same page
        else:
            messages.success(request, "An error has occurred")

    return render(request, 'competition/competition_manager.html', context={
        'form': project_form
    })
