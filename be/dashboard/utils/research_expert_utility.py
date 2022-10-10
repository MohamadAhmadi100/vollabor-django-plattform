from django.contrib import messages
from django.contrib.auth.models import User
from ivc_website.models import Project, ProjectProposal
from dashboard.models import Reviewer, ProposalOpinion, ProposalOpinionItem


def assign_reviewers_to_the_project(project_pk, request):
    the_project = Project.objects.get(pk=project_pk)
    for key in request.POST:
        if 'reviewer-pk' in key:
            user_pk = request.POST.get(key)
            user_reviewer = User.objects.get(pk=user_pk)
            Reviewer(user=user_reviewer, project=the_project).save()
    messages.success(request, f'Reviewer has been assigned successfully')


def get_total_number_of_reviewers(project_pk, request):
    number_of_assign_reviewer = Reviewer.objects.filter(project__pk=project_pk).count()
    for key in request.POST:
        if 'reviewer-pk' in key:
            number_of_assign_reviewer += 1
    return number_of_assign_reviewer


def has_every_reviewer_scored(project):
    scored_item_numbers = ProposalOpinion.objects.filter(proposal__project_supervisor__project=project,
                                                         reviewer__project=project).count()

    number_of_proposals = ProjectProposal.objects.filter(project_supervisor__project=project).count()
    number_of_reviewers = Reviewer.objects.filter(project=project).count()
    item_numbers = ProposalOpinionItem.objects.filter(project_type=project.project_type).count()

    return scored_item_numbers == number_of_proposals * number_of_reviewers * item_numbers
