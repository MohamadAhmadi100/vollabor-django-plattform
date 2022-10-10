from django.contrib import messages
from django.db.models import Q

from dashboard.models import ProposalOpinionItem, Reviewer, ProposalOpinion, ProposalComment
from ivc_website.models import ProjectProposal


def submit_new_proposal_score(project, request, selected_project_proposal):
    """
    At first we make sure that the person submitted all of the numbers.
    so we get the length of request.POST minus 2
    why 3? one for submit-new-proposal-opinion and the other one for csrf_token and last one is reviewer_comment
    """
    submitted_numbers = len(request.POST) - 3
    submitted_all_of_the_items = \
        submitted_numbers == ProposalOpinionItem.objects.filter(project_type=project.project_type).count()
    if submitted_all_of_the_items:  # security check
        for key in request.POST:
            if 'item' in key:
                item_pk = int(key.split('-')[1])
                item = ProposalOpinionItem.objects.get(pk=item_pk)

                score = int(request.POST.get(key))
                reviewer = Reviewer.objects.get(user=request.user, project=project)
                if 0 <= score <= 10:  # security check
                    ProposalOpinion(proposal=selected_project_proposal, item=item, reviewer=reviewer,
                                    score=score).save()
                else:
                    messages.error(request, 'Score must be a number between 0 and 10')

        messages.success(request, 'Scores have been submitted successfully')
    else:
        messages.error(request, 'You have to submit all of the items')


def submit_proposal_score(project, request, selected_project_proposal):
    """
    At first we make sure that the person submitted all of the numbers.
    so we get the length of request.POST minus 2
    why 2? one for submit-proposal-opinion and the other one for csrf_token
    """
    submitted_numbers = len(request.POST) - 2
    submitted_all_of_the_items = submitted_numbers == ProposalOpinion.objects.filter(proposal=selected_project_proposal,
                                                                                     reviewer__user=request.user).count()
    if submitted_all_of_the_items:  # security check
        for key in request.POST:
            if 'item' in key:
                proposal_opinion_pk = int(key.split('-')[1])
                proposal_opinion = ProposalOpinion.objects.get(pk=proposal_opinion_pk)

                score = int(request.POST.get(key))
                reviewer = Reviewer.objects.get(user=request.user, project=project)
                if 0 <= score <= 10:  # security check
                    proposal_opinion.score = score
                    proposal_opinion.save()
                else:
                    messages.error(request, 'Score must be a number between 0 and 10')

        messages.success(request, 'Scores have been submitted successfully')
    else:
        messages.error(request, 'You have to submit all of the items')


def get_unseen_proposal_numbers(user):
    scored_proposals = ProposalOpinion.objects.filter(reviewer__user=user).values_list('proposal', flat=True)
    projects = Reviewer.objects.filter(user=user).values_list('project', flat=True)
    return ProjectProposal.objects.filter(~Q(pk__in=scored_proposals) &
                                          Q(project_supervisor__project__pk__in=projects)).count()


def add_reviewer_comment_to_proposal(user, reviewer_comment, selected_project_proposal):
    selected_reviewer = Reviewer.objects.get(user=user, project=selected_project_proposal.project_supervisor.project)
    comment_already_exists = ProposalComment.objects.filter(proposal=selected_project_proposal, reviewer=selected_reviewer).count()
    if comment_already_exists:
        proposal_comment = ProposalComment.objects.get(proposal=selected_project_proposal, reviewer=selected_reviewer)
        proposal_comment.comment = reviewer_comment
        proposal_comment.save()
    else:
        ProposalComment(proposal=selected_project_proposal, reviewer=selected_reviewer, comment=reviewer_comment).save()
