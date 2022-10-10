import datetime
from django import template
from django.db.models import Count, Q
from datetime import datetime, timedelta
from ..models import *

register = template.Library()

@register.simple_tag
def count_manager():
	
	badge_new_count = BadgeRequest.objects.filter(status='New').count()
	badge_interview_review_count = BadgeRequest.objects.filter(status__in=['Review','Set-session','Approve-decline','Interview','Expert-view','send_manager','decline-review-interview','Reject', 'revise_by_manager']).count()
	
	supervisor_new_count = SupervisorRequest.objects.filter(status='New').count()
	supervisor_reviewe_count = SupervisorRequest.objects.filter(status__in=['Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', 'revise_by_manager', 'revise_by_expert']).count()
	
	workshop_new_count = WorkshopRequest.objects.filter(status='New').count()
	workshop_reviewe_count = WorkshopRequest.objects.filter(status__in=['Review', 'reviewer_evaluated', 'reviewer_accept', 'reviewer_reject', 'send_to_manager', 'revised_by_manager', 'revised_by_expert']).count()
	return badge_new_count + badge_interview_review_count + supervisor_new_count + supervisor_reviewe_count + workshop_new_count + workshop_reviewe_count 


@register.simple_tag
def count_expert(request):

	badge_interview_review_count = BadgeExpert.objects.filter(user=request.user, 
		badge__status__in=['Review', 'Approve-decline', 'Interview', 'Expert-view', 'decline-review-interview', 'Reject', 'Set-session', 'revise_by_manager', 'send_manager']).count()
		
	badge_new_count = BadgeExpert.objects.filter(user=request.user, badge__status='New').count()
	supervisor_count = SupervisorRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'New', 'revise_by_manager', 'revise_by_expert']).count(),
	workshop_count = WorkshopRequest.objects.filter(expert=request.user, status__in=['reviewer_reject', 'reviewer_accept', 'reviewer_evaluated', 'Review', 'New', 'revised_by_manager', 'revised_by_expert']).count(),


	return badge_interview_review_count + badge_new_count + supervisor_count + workshop_count 

