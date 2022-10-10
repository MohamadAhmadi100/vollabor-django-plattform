from django import template
import datetime
from research.models import *
from django.utils.html import format_html
from datetime import date

register = template.Library()

@register.filter
def total_score(reviewer):
    total=reviewer.score
    for i in range(1,7):
        total+=getattr(reviewer,f'score_{i}')
    return total

@register.filter()
def date_7(value):
	return value + datetime.timedelta(days=8)

@register.filter()
def date_2(value):
	return value + datetime.timedelta(days=2)

@register.simple_tag
def count_message(id_project, id_user):
    obj_project = ResearchProject.objects.get(id=id_project)

    comment_to_expert = ApplicantComment.objects.filter(project_id=id_project, sender_id=id_user, position='send_to_expert')
    comment_to_applicant = ApplicantComment.objects.filter(project_id=id_project, recipient_id=id_user, sender=obj_project.project.client_form.expert, position='send-to-applicant', seen=False).count()

    count = 0
    for i in comment_to_expert:
        for r in i.comments.filter(seen=False):
            count += 1

    x = count + comment_to_applicant
    return x



@register.simple_tag
def count_project_message(id_project):
    count = 0

    count_meesage_applicant = ApplicantComment.objects.filter(position='send_to_expert', project_id=id_project, seen=False).count()

    for i in ApplicantComment.objects.filter(position='send-to-applicant', project_id=id_project):
        for e in i.comments.filter(seen=False):
            count += 1
    return count + count_meesage_applicant

@register.simple_tag
def count_applicant_message(id_project, id_user):


    count_meesage_applicant = ApplicantComment.objects.filter(position='send_to_expert', sender_id=id_user, project_id=id_project, seen=False).count()
    
    count = 0
    for i in ApplicantComment.objects.filter(position='send-to-applicant', recipient_id=id_user, project_id=id_project):
        for e in i.comments.filter(seen=False):
            count += 1

    return count + count_meesage_applicant


@register.simple_tag
def applicant_wbs_button(project_id, wbs_id, applicant):

    obj_wbs = TimeProgramming.objects.get(id=wbs_id)

    applicant_report = ReportApplicant.objects.filter(applicant=applicant, project_id=project_id, wbs_obj_id=wbs_id).count()

    if obj_wbs.end_date <= date.today() and applicant_report == 0:
        return format_html("<button type='button' data-bs-toggle='modal' data-bs-target='#send_report-{}' class='btn btn-primary'>Report</button>".format(wbs_id))
    else:
        return format_html("<button disabled class='btn btn-primary'>Report</button>")


@register.simple_tag
def applicant_wbs_status(project_id, wbs_id, applicant):

    obj_wbs = TimeProgramming.objects.get(id=wbs_id)

    applicant_report = ReportApplicant.objects.filter(applicant=applicant, project_id=project_id, wbs_obj_id=wbs_id).count()

    if applicant_report == 1:
        return 'Done'
    elif date.today() < obj_wbs.end_date:
        return 'The time is left'
    else:
        return 'You must send the report'
