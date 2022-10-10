from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.html import format_html
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from workshop.models import MainField, SubField
# My manager
class ExpertSupManager(models.Manager):
    def Active(self):
        return self.filter(status='a')
    def status_review(self):
        return self.filter(status='v')
    def resubmition_count(self):
        return self.filter(status='resubmition')
    def status_check_score_director(self):
        return self.filter(status='d')
    def resubmition_director(self):
        return self.filter(status='resubmition-to-director')
    def status_revise(self):
        return self.filter(status='revise-proposal-to-expert')

    def list_history(self):
        return self.filter(~Q(status__in=["r", "u"]))

    def not_response_proposal(self):
        return self.filter(status='not_response_proposal')

    def not_response_proposal_director(self):
        return self.filter(status='not_response_proposal_send_to_director')



# Applicant managers
class Applicant(models.Manager):
    def Active(self):
        return self.filter(~Q(status_remove__in=["request-accpet-by-director", "request-accpet-by-expert"]), status__in=['confirmed', 'confirmed-by-expert'], )

    def Accepted(self):
        return self.filter(status__in=['confirmed', 'confirmed-by-expert'])

# Applicant comment managers
class ApplicantComment(models.Manager):
    def Expert(self):
        return self.filter(position='send_to_expert')
    def Expert_count(self):
        return self.filter(seen=False, position='send_to_expert').count()

    def Main_supervisor(self):
        return self.filter(position='send_to_main_supervisor')
    def Main_supervisor_count(self):
        return self.filter(seen=False, position='send_to_main_supervisor').count()

# Request managers
class Request(models.Manager):
    def Active(self):
        return self.filter(status='request')
        
    def under_process(self):
        return self.filter(status__in=['reject', 'request'])

# WBS managers
class WBS(models.Manager):
    def Active(self):
        return self.filter(status='end_of_report')

# Expert managers
class ExpertManager(models.Manager):
    def Not_Change(self):
        return self.filter(~Q(status="is_change"), )

# Create your models here.

class Area(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class ResearchRole(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)
    director = models.BooleanField(default=False, null=True)
    expert = models.BooleanField(default=False, null=True)
    reviewer = models.BooleanField(default=False, null=True)
    advertisement = models.BooleanField(default=False, null=True)
    comment_management = models.BooleanField(default=False, null=True)
    interviewer = models.BooleanField(default=False, null=True)
    count_evaluated_reviewer = models.IntegerField(null=True, default=0, blank=True)
    count_rejected_reviewer = models.IntegerField(null=True, default=0, blank=True)
    count_breach_of_promis_reviewer = models.IntegerField(null=True, default=0, blank=True)
    expert_email_address = models.EmailField(max_length=200, blank=True, null=True, )

    count_expert_change_request = models.IntegerField(null=True, default=0, blank=True)
    count_evaluated_reviewer_request = models.IntegerField(null=True, default=0, blank=True)
    count_rejected_reviewer_request = models.IntegerField(null=True, default=0, blank=True)
    count_breach_of_promis_reviewer_request = models.IntegerField(null=True, default=0, blank=True)

    expert_change_request = models.TextField(null=True, blank=True)
    area = models.ManyToManyField(Area, null=True, blank=True)
    ongoing_project_expert = models.IntegerField(null=True, default=0, blank=True)
    ongoing_detail_project_expert = models.TextField(null=True, default='', blank=True)

    class Meta():
        verbose_name = 'Project Role'
        verbose_name_plural = 'Project Roles'


class IndustryFormClient(models.Model):
    STATUS_CHOICES = (
        ('n', 'is_new'),

        ('e', 'is_expert'),
        ###
        ('s', 'is_supervisor'),
        ('not-pay', 'Not pay'),

        # Rejected by director
        ('r', 'Rejected by director'),
        ('rejected_by_expert', 'Rejected by expert'),
        ('m', 'is_main_supervisor'),
        ('withdrew', 'withdrew'),

        ('send-contract-to-client', 'send-contract-to-client'),
        ('send-signed-contract', 'send-signed-contract'),
        ('revised-contract', 'revised-contract'),
        ('send-contract-to-director', 'send-contract-to-director'),
        ('revise-contract-by-director', 'revise-contract-to-director'),
        ('accept-contract-by-director', 'accept-contract-by-director'),
        ('not-response-contract', 'not-response-contract'),
        
        ('d', 'delete_project'),
        ('created', 'created'),
        ('hidden', 'hidden'),

        ('expert_reviewer', 'Expert reviewer'),
        ('expert_send_scores_to_director', 'expert_send_scores_to_director'),

        ('revise_director_to_expert', 'revise_director_to_expert'),
        ('revise_director_to_client', 'revise_director_to_client'),
        ('resubmited_project', 'resubmited_project'),
        ('accept_project_pending_send_contarct_client', 'accept_project_pending_send_contarct_client'),
        ('resubmited_project_send_to_director', 'resubmited_project_send_to_director'),
        
    )
    STATUS_FOLLOW_PROJECT = (
        ('new', 'New'),
        ('send_review', 'Send review'),
        ('check_score', 'Check score'),
        ('change_to_new_status', 'Change to new status'),


        ('p_main_new', 'new main supervisor'),
        ('p_main_send_review', 'new main supervisor'),
        ('p_main_send_proposal_director', 'p_main_send_proposal_director'),
        ('p_main_revise_project_director', 'p_main_revise_project_director'),
        ('p_main_revise_proposal_by_expert', 'p_main_revise_proposal_by_expert'),
        ('p_main_revise_proposal_by_director', 'p_main_revise_proposal_by_director'),
        ('p_main_not_response_revised_proposal', 'p_main_not_response_revised_proposal'),
        ('p_main_not_response_revised_proposal_send_to_director', 'p_main_not_response_revised_proposal_send_to_director'),
        ('p_main_resubmition_proposal', 'p_main_resubmition_proposal'),
        ('p_main_accept_proposal_director', 'p_main_accept_proposal_director'),
        ('p_main_contract_sent_supervisor', 'p_main_contract_sent_supervisor'),
        ('p_main_contract_sent_to_expert', 'p_main_contract_sent_to_expert'),
        ('p_main_contract_revise', 'p_main_contract_revise'),
        ('p_main_contract_revise_by_director', 'p_main_contract_revise_by_director'),
        ('p_main_change_to_new_to_status', 'p_main_change_to_new_to_status'),
        ('under-process-by-expert', 'under-process-by-expert'),

        ('send_contract_to_client', 'send_contract_to_client'),
        ('sent_contract_to_client', 'sent_contract_to_client'),
        ('send_signed_contract', 'send_signed_contract'),
        ('revised_contract', 'revised_contract'),
        ('under_process_by_expert', 'Under process by expert'),
    )
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='users')
    main_field = models.ForeignKey(MainField, null=True, on_delete=models.SET_NULL, related_name="workshop_main_field")
    sub_field = models.ForeignKey(SubField, null=True, on_delete=models.SET_NULL, related_name="workshop_sub_field")
    name = models.CharField(max_length=1000, verbose_name = 'Company Name')
    title = models.CharField(max_length=1000)
    id_project = models.CharField(max_length=1000, unique=True,)
    start_date = models.DateField(default=timezone.now(), null=True, verbose_name='Strat Date')
    end_date = models.DateField(default=timezone.now(), null=True, verbose_name='End Date')
    data_set_link = models.URLField(max_length=500, null=True)
    abstrack = models.TextField( verbose_name='abstract')
    equipment = models.TextField(max_length=2000)
    requirement = models.TextField(max_length=2000)
    main_supervisor = models.FileField(upload_to='propzar/', default=None, blank=True, null=True, verbose_name='Main Supervisor')
    contract = models.FileField(upload_to='contarct-client/', default=None, blank=True, null=True, verbose_name='Contract')
    signed_contract = models.FileField(upload_to='contarct-client/', default=None, blank=True, null=True, verbose_name='Signed contract')
    pri_file = models.FileField(upload_to='pri/', default=None, blank=True, null=True, verbose_name='PRI')
    fund = models.IntegerField(null=True, blank=True)
    is_new = models.BooleanField(default=True)
    is_rejects = models.BooleanField(default=False)
    is_expert = models.BooleanField(default=False)
    is_supervisor = models.BooleanField(default=False)
    is_main_supervisor = models.BooleanField(default=False)
    reason_rejectd = models.TextField(default=None, null=True)
    status = models.CharField(max_length=50, default='n', null=True, choices=STATUS_CHOICES)
    project_created = models.BooleanField(null=True, default=False)
    follow_project = models.CharField(max_length=100, default=None, null=True, choices=STATUS_FOLLOW_PROJECT)
    question_1 = models.CharField(max_length=100, null=True, verbose_name='1')
    question_2 = models.CharField(max_length=100, null=True, verbose_name='2')
    question_3 = models.CharField(max_length=100, null=True, verbose_name='3')
    question_4 = models.CharField(max_length=100, null=True, verbose_name='4')
    question_5 = models.CharField(max_length=100, null=True, verbose_name='5')
    question_6 = models.CharField(max_length=100, null=True, verbose_name='6')
    question_7 = models.CharField(max_length=100, null=True, blank=True, verbose_name='7')
    created = models.DateTimeField(auto_now_add=True)
    rejected_date = models.DateField(null=True)
    created_date = models.DateField(null=True)
    deadline = models.DateTimeField(null=True)

    def __str__(self):
        return self.title

    class Meta():
        verbose_name = 'Project client'
        verbose_name_plural = 'Project clients'

class IndustryFormExpert(models.Model):
    STATUS_CHOICES = (
        ('m', 'main__supervisor'),
        ('n', 'new'),
        ('s', 'supervisor'),
        ('v', 'view_main__supervisor'),
        ('h', 'hidden'),
        ('view_projects', 'view_projects'),
        ('review', 'Review'),

        ('review_project', 'Review project'),
        ('expert_send_scores_to_director', 'expert_send_scores_to_director'),
        ('revise_director_to_expert', 'revise_director_to_expert'),
        ('revise_director_to_client', 'revise_director_to_client'),
        ('resubmited_project', 'resubmited_project'),
        ('resubmited_project_send_to_director', 'resubmited_project_send_to_director'),
        ('accept_project_pending_send_contarct_client', 'accept_project_pending_send_contarct_client'),

        ('send-contract-to-client', 'send-contract-to-client'),
        ('send-signed-contract', 'send-signed-contract'),
        ('revised-contract', 'revised-contract'),
        ('send-contract-to-director', 'send-contract-to-director'),
        ('revise-contract-to-director', 'revise-contract-to-director'),
        ('accept-contract-by-director', 'accept-contract-by-director'),
        ('not-response-contract', 'not-response-contract'),

        ('reviewer_project', 'Reviewer project'),
        ('chek_score', 'Chek score'),
        ('is_change', 'is_change'),
    )
    
    STATUS_FUND = (
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    )
    # STATUS_FOLLOW_PROJECT = (
    #     ('new', 'New'),
    # )
    expert = models.ForeignKey(
        User, null=True, on_delete=models.CASCADE, related_name='experts')
    formclint = models.ForeignKey(
        IndustryFormClient, null=True, on_delete=models.CASCADE, related_name='forms_client')
    is_supervisor  = models.BooleanField(default=False)
    is_mainsupervisor  = models.BooleanField(default=False)
    status = models.CharField(max_length=50, default=None, null=True, choices=STATUS_CHOICES)
    # follow_project = models.CharField(max_length=50, default=None, null=True, choices=STATUS_FOLLOW_PROJECT)
    status_value = models.CharField(max_length=50, null=True, choices=STATUS_FUND, default=None)
    valeu = models.IntegerField(default=0, null=True)
    slug_forum = models.SlugField(max_length=100, null=True)
    description_forum = models.TextField(null=True)
    # icon_forum = models.CharField(max_length=100, null=True)
    directo_a_or_r_mainsupervisor = models.BooleanField(default=False) 
    directo_see_reviewer = models.BooleanField(default=False) 
    directo_create_project = models.BooleanField(default=False) 
    director_reject_proposal = models.BooleanField(default=False) 

    #Phase 2
    contract_applicant = models.BooleanField(default=False) 
    remove_applicant = models.BooleanField(default=False) 
    change_status = models.BooleanField(default=False) 

    created = models.DateTimeField(auto_now_add=True)
    deadline = models.DateTimeField(default=None, null=True)

    objects = ExpertManager()
    def __str__(self):
        return self.formclint.title

    class Meta():
        verbose_name = 'Project expert'
        verbose_name_plural = 'Project experts'

class IndustryExpertForSupervisor(models.Model):
    STATUS_CHOICES = (
        ('u', 'u'),
        ('a', 'Accept'),
        ('r', 'Reject'),
        ('not-pay', 'not-pay'),
        ('resubmition', 'Resubmition'),
        ('m', 'Main supervisor'),
        ('b', 'Returned'),
        ('v', 'Reviewer'),

        ('not_response_proposal', 'Not response proposal'),
        ('not_response_proposal_send_to_director', 'Not response proposal send to the director'),
        ('reject_proposal_by_expert', 'Reject proposal by director'),
        # ('v', 'Reviewer'),

        ('resubmition-to-director', 'resubmition-to-director'),
        ('d', 'Director'),
        ('h', 'Reject proposal by director'),
        ('t', 'Sned contract to supervisor'),
        ('director_revise_contract', 'Director revise contract'),
        ('withdrew', 'withdrew'),
        ('z', 'Send contract supervisor for director'),####
        ('g', 'expert chek contract'),
        ('n', 'Create new project'),
        ('x', 'Send contract to expert by director'),
        ('reject_contract', 'Reject contract'),
        ('not_see', 'Not see'),
        ('revise-proposal-to-expert', 'Revise proposal to the expert'),
        # special expert accept or reject main supervisor
        ('special_expert', 'special expert'),
        # special expert see review
        ('special_expert_review', 'special expert review'),
        # special expert create project
        ('special_expert_create_project', 'special expert create project'),
        # send report by main supervisor
        ('report', 'report expert'),
        ('report_d', 'report director'),
        ('deleted', 'deleted'),
    )

    STATUS_FOLLOW_PROJECT = (
        ('accept_project', 'Accept project'),
        ('reject_project', 'Reject project'),
        ('reject_by_expert', 'Reject by expert'),
        ('send_to_reviewer', 'Send to reviewer'),
        ('send_to_director', 'Send to director'),
        ('reject_by_director', 'Reject by director'),
        ('accept_by_director', 'Accept by director'),
        ('create_project', 'Reject contract'),
    )

    supervisor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='supervisors')
    propzar = models.FileField(upload_to='propzar/', default=None, null=True, verbose_name='Proposal File', blank=True)
    Contract = models.FileField(upload_to='Contract/', default=None, null=True, verbose_name='Contract File', blank=True)
    contract_supervisor = models.FileField(upload_to='Contract/', default=None, null=True, verbose_name='Contract File', blank=True)
    client_form = models.ForeignKey(IndustryFormExpert, null=True, unique=False, on_delete=models.CASCADE, related_name='forms_clients')
    status = models.CharField(max_length=50, default='u',null=True, choices=STATUS_CHOICES)
    follow_project = models.CharField(max_length=30, default='None',null=True, choices=STATUS_FOLLOW_PROJECT)
    text = models.TextField(default=None, null=True, verbose_name='Comment')
    reason_reject = models.TextField(null=True, verbose_name="Rejection Reason")
    is_new_reject = models.IntegerField(default=0, null=True)
    created = models.DateTimeField(auto_now_add=True)

    #form adverstiment
    grade = models.CharField(max_length=200, null=True, verbose_name='Grade of project')
    skills_required = models.CharField(max_length=200, null=True, verbose_name='Skills required to attend in project (Add some bullets)')
    project_ponsored = models.CharField(max_length=200, null=True, verbose_name='Project will be sponsored by (Company or University or Institute) ')
    supervisor_information = models.CharField(max_length=200, null=True, verbose_name='Few informative bullets to describe content of project (maximum 6 bullets)')
    informative_bullets = models.CharField(max_length=200, null=True, verbose_name='Few informative bullets to describe content of project (maximum 6 bullets)')
    social_platforms = models.CharField(max_length=200, null=True, verbose_name='Suggested helpful social media platforms (name of related groups and links) which you think they are useful to advertise')
    fruitful_countries = models.CharField(max_length=200, null=True, verbose_name='Suggest fruitful countries')
    motivating_keywords = models.CharField(max_length=200, null=True, verbose_name='Motivating keywords (Maximum: 6 keywords)')
    upload_pictures = models.ImageField(upload_to='upload_pictures/', default=None, null=True, verbose_name='Upload high quality related pictures for project')
    benefit_of_members = models.CharField(max_length=200, null=True, verbose_name='What is the benefit of members being present in the project for them?')
    
    main_supervisor = models.BooleanField(null=True, default=False)
    deleted = models.BooleanField(null=True, default=False)
    view_report = models.BooleanField(null=True, default=False)
    status_review = models.CharField(max_length=30, null=True)
    rejected_date = models.DateField(null=True)
    deadline = models.DateTimeField(null=True)


    def upload_pictures_tags(self):
        return format_html("<img width=80 height=80 style='border-radius: 1000px;' src='{}'>".format(self.upload_pictures.url))
    upload_pictures_tags.short_description = "upload pictures"

    objects = ExpertSupManager()
  
    class Meta():
        verbose_name = 'Project supervisor'
        verbose_name_plural = 'Project supervisors'


        
class TimeProgramming(models.Model):
    STATUS_CHOICES = (
        ('send_report', 'Send report'),
        ('end_of_report', 'End of report'),
        ('unanswered', 'Unanswered'),
    ) 
    sub = models.ForeignKey(IndustryExpertForSupervisor, null=True, on_delete=models.CASCADE, related_name='time_programmins')
    topic = models.CharField(max_length=50, null=True)
    start_date = models.DateField(default=timezone.now(), null=True)
    end_date = models.DateField(default=timezone.now(), null=True)
    report = models.TextField(null=True)
    status = models.CharField(max_length=30, default=None, blank=True, null=True, choices=STATUS_CHOICES)


    question_1 = models.TextField(null=True, blank=True)
    question_2 = models.TextField(null=True, blank=True)
    question_3 = models.TextField(null=True, blank=True)
    question_4 = models.TextField(null=True, blank=True)
    question_5 = models.TextField(null=True, blank=True)
    question_6 = models.TextField(null=True, blank=True)
    question_7 = models.TextField(null=True, blank=True)
    question_8 = models.TextField(null=True, blank=True)
    upload_file = models.FileField(upload_to='upload_pictures/', default=None, null=True, )
    upload_pictures = models.ImageField(upload_to='upload_pictures/', default=None, null=True, verbose_name='Upload high quality related pictures for project')

    confirm = models.BooleanField(null=True, default=False)
    objects = WBS()

    class Meta():
        verbose_name = 'Project WBS'
        verbose_name_plural = 'Project WBS'


class IndustryReviewer(models.Model):
    STATUS_CHOICES = (
        ('n', 'New'),
        ('r', 'reject'),
        ('a', 'accept'),
        ('e', 'expert'),
        ('s', 'not_see'),
        ('breach_of_promis_p', 'Breach of promise proposal'),

        ('cancel_by_expert', 'Cancel by expert'),
        ('cancel_by_expert_p', 'Cancel by expert project'),

        ('automatically_cancel', 'Automatically Revise proposal'),
        ('automatically_cancel_p', 'Automatically Revise project'),

        ('revise_by_expert', 'Revise by expert'),
        ('revise_by_expert_p', 'Revise by expert project'),

        ('new_project', 'New project'),
        ('reject_project', 'Reject project'),
        ('accept_project', 'Accept project'),
        ('send_director_project','Send to director project'),
        ('not_see_project', 'Not see project'),
        ('breach_of_promis', 'Breach of promise'),

    )
    reviewer = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='reviewers')
    object_supervisor = models.ForeignKey(IndustryExpertForSupervisor, blank=True, null=True, on_delete=models.CASCADE, related_name='object_supervisors')
    object_client = models.ForeignKey(IndustryFormClient, blank=True, null=True, on_delete=models.CASCADE, related_name='object_clients')
    object_expert = models.ForeignKey(IndustryFormExpert, blank=True, null=True, on_delete=models.CASCADE, related_name='object_experts')
    score = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_1 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_2 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_3 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_4 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_5 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    score_6 = models.IntegerField(default=0, null=True, validators=[MaxValueValidator(100), MinValueValidator(0)], verbose_name='')
    text = models.TextField(null=True, verbose_name='Comment')
    status = models.CharField(max_length=30, null=True, choices=STATUS_CHOICES, default='n')
    create = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(null=True)
    deadline = models.DateTimeField(null=True)
    event_date = models.DateTimeField(null=True)
    deleted = models.BooleanField(null=True, default=False)

    class Meta():
        verbose_name = 'Project reviewer'
        verbose_name_plural = 'Project reviewers'


class ResearchProject(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('on_going', 'On going'),
        ('pending', 'Pending'),
        ('on_hold', 'On hold'),
        ('done', 'Done'),
        ('delete', 'Delete'),
        ('under_process_supervisor', 'under_process_supervisor'),
        ('send_proposal', 'Send proposal'),
        ('deadline_is_over', 'The deadline is over'),
    )
    STATUS_FUND = (
        ('hard', 'Hard'),
        ('normal', 'Normal'),
        ('easy', 'Easy'),
    )
    CHANGE_STATUS = (
        ('send_to_expert', 'Send to expert'),
        ('send_to_director', 'Send to director'),
        ('reject', 'Reject'),
        ('accept', 'Accept'),
    )
    STATUS_CHANGE_CHOICES = (
        ('new', 'New'),
        ('on_going', 'On going'),
        ('pending', 'Pending'),
        ('on_hold', 'On hold'),
        ('done', 'Done'),
    )
    # id_project = models.CharField(max_length=100,null=True)
    project = models.ForeignKey(IndustryExpertForSupervisor, null=True, on_delete=models.CASCADE, related_name='projects')
    proposal_supervisor = models.ForeignKey(IndustryFormExpert, blank=True, null=True, on_delete=models.CASCADE, related_name='expert_foreignkey')
    main_supervisor = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='main_supervisor_pr')
    # link = models.CharField(max_length=100, null=True)
    # link_time = models.DateTimeField(default=timezone.now(), null=True)
    # publish = models.DateTimeField(default=timezone.now(), null=True, verbose_name='Start Date')
    # end_date = models.DateTimeField(default=timezone.now(), null=True, verbose_name='End Date')
    status = models.CharField(max_length=50, null=True, choices=STATUS_CHOICES, default='new')
    status_value = models.CharField(max_length=10, null=True, choices=STATUS_FUND, default=None)
    money = models.IntegerField(null=True, default=0, verbose_name='Valeu')
    reason_reject_expert = models.TextField(null=True)
    text_change_status = models.TextField(null=True)
    status_change = models.CharField(max_length=20, null=True, choices=CHANGE_STATUS, default=None)
    status_change_choices = models.CharField(max_length=20, null=True, choices=STATUS_CHANGE_CHOICES, default=None)
    view_project_home = models.BooleanField(default=False, null=True ,verbose_name='Show the project on the home page?')
    value_supervisor = models.IntegerField(null=True, default=0)
    value_mentor = models.IntegerField(null=True, default=0)
    value_mmber = models.IntegerField(null=True, default=0)
    value_lerner = models.IntegerField(null=True, default=0)

    # progress_report_end_project = models.FileField(upload_to='report_project/', default=None, null=True, blank=True, verbose_name='Progress report end project')
    progress_report_middle_project = models.FileField(upload_to='report_project/', default=None, null=True, blank=True, verbose_name='Progress report middle project')
    final_document = models.FileField(upload_to='report_project/', default=None, null=True, blank=True, verbose_name='Final document')

    created = models.DateTimeField(auto_now_add=True, null=True)


    class Meta():
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        
    def __str__(self):
        if self.project:
            return self.project.client_form.formclint.title
        else:
            return self.proposal_supervisor.formclint.title


class Tracing(models.Model):
    tracing_project =  models.ForeignKey(IndustryFormClient, blank=True, null=True, on_delete=models.CASCADE, related_name='tracing_projects')
    tracing_project_phase_2 =  models.ForeignKey(ResearchProject, blank=True, null=True, on_delete=models.CASCADE, related_name='tracing_projects_phase_2')
    tracing_main_supervisor =  models.ForeignKey(ResearchProject, blank=True, null=True, on_delete=models.CASCADE, related_name='tracing_main_supervisor')
    tracing_supervisor =  models.ForeignKey(IndustryExpertForSupervisor, blank=True, null=True, on_delete=models.CASCADE, related_name='tracing_supervisors')
    tracing_reviewer =  models.ForeignKey(IndustryReviewer, blank=True, null=True, on_delete=models.CASCADE, related_name='tracing_reviewers')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='users_tracing')
    position = models.CharField(max_length=50, null=True)
    status = models.CharField(max_length=1000, null=True)
    event_date = models.DateTimeField(null=True)

class ResearchMeeting(models.Model):
    STATUS_CHOICES = (
        ('visible', 'Visible'),
        ('deleted', 'Deleted'),
    )


    project_research = models.ForeignKey(ResearchProject, null=True, on_delete=models.CASCADE, related_name='research_meeting')
    link_meeting = models.URLField(max_length=300, null=True)
    date_meeting = models.DateField(default=timezone.now())
    time_meeting = models.TimeField(default=timezone.now())
    created = models.DateTimeField(auto_now_add=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='visible', verbose_name='Choose your position!')
    time_zone = models.CharField(max_length=50, null=True)

    class Meta():
        verbose_name = 'Project meeting'
        verbose_name_plural = 'Project meetings'


class RequestUserForProject(models.Model):
    STATUS_REQUEST = (
        ('not-pay', 'not-pay'),
        ('accept', 'Accept'),
        ('reject', 'Reject'),
        ('remove', 'Remove'),
        ('rejection-contract', 'rejection-contract'),
        ('request', 'Request'),
        ('delete', 'Deleted'),
    )

    supervisor = models.BooleanField(default=False, null=True)
    mentor = models.BooleanField(default=False, null=True)
    member = models.BooleanField(default=False, null=True)
    learner = models.BooleanField(default=False, null=True)
    reason_for_rejection = models.TextField(null=True)

    project_request = models.ForeignKey(ResearchProject, null=True, on_delete=models.CASCADE, related_name='project_requests')
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='requests')
    status = models.CharField(max_length=50, choices=STATUS_REQUEST, default='request', verbose_name='Choose your position!')
    created = models.DateTimeField(auto_now_add=True, null=True)

    objects = Request()
    class Meta():
        verbose_name = 'Project request'
        verbose_name_plural = 'Project requests'
    
    def __str__(self):
        return self.project_request.project.client_form.formclint.title


class SuperVizor(models.Model):
    STATUS_REQUEST = (
        ('new', 'New'),
        ('send-contract', 'Send contract'),
        ('send-contract-to-expert', 'Send contract to the contract'),
        ('not-response', 'Not response '),
        ('confirmed', 'Confirmed'),
        ('confirmed-by-expert', 'Confirmed by expert'),

        ('send-to-director', 'send-to-director'),

        ('revised_by_expert', 'revised_by_expert'),
        ('revised-director-to-expert', 'revised-director-to-expert'),

        ('reject', 'Reject'),
    )

    STATUS_REMOVE = (
        ('request-remove', 'request-remove'),
        ('request-remove-send-to-the-director', 'request-remove-send-to-the-director'),
        ('request-reject-by-director', 'request-reject-by-director'),
        ('request-accpet-by-director', 'request-accept-by-director'),

        ('request-accpet-by-expert', 'request-accept-by-expert'),
        ('request-reject-by-expert', 'request-reject-by-expert'),
    )

    research = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='supervisors_project')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_REQUEST, null=True, default='new', verbose_name='Choose your position!')
    status_remove = models.CharField(max_length=60, choices=STATUS_REMOVE, null=True, default=None, blank=True, verbose_name='Choose your position!')
    contract = models.FileField(upload_to='contract-expert-applicant', null=True)
    contract_applicant = models.FileField(upload_to='contract-applicant', null=True)
    event_date = models.DateField(default=None, null=True)
    deadline = models.DateTimeField(default=None, null=True)
    reason_rejection = models.TextField(null=True)
    comment = models.TextField(null=True)

    question_1 = models.CharField(max_length=100,null=True, blank=True)
    question_2 = models.CharField(max_length=100,null=True, blank=True)
    question_3 = models.CharField(max_length=100,null=True, blank=True)
    question_4 = models.CharField(max_length=100,null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    objects = Applicant()

    class Meta():
        verbose_name = 'Supervisor'
        verbose_name_plural = 'Supervisors'


class Mentor(models.Model):
    STATUS_REQUEST = (
        ('new', 'New'),
        ('send-contract', 'Send contract'),
        ('send-contract-to-expert', 'Send contract to the contract'),
        ('not-response', 'Not response '),
        ('confirmed', 'Confirmed'),
        ('confirmed-by-expert', 'Confirmed by expert'),

        ('send-to-director', 'send-to-director'),

        ('revised_by_expert', 'revised_by_expert'),
        ('revised-director-to-expert', 'revised-director-to-expert'),

        ('reject', 'Reject'),
    )

    STATUS_REMOVE = (
        ('request-remove', 'request-remove'),
        ('request-remove-send-to-the-director', 'request-remove-send-to-the-director'),
        ('request-reject-by-director', 'request-reject-by-director'),
        ('request-accpet-by-director', 'request-accept-by-director'),

        ('request-accpet-by-expert', 'request-accept-by-expert'),
        ('request-reject-by-expert', 'request-reject-by-expert'),
    )

    research = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='mentor_project')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=60, choices=STATUS_REQUEST, null=True, default='new', verbose_name='Choose your position!')
    status_remove = models.CharField(max_length=60, choices=STATUS_REMOVE, null=True, default=None, blank=True, verbose_name='Choose your position!')
    contract = models.FileField(upload_to='contract-expert-applicant', null=True)
    contract_applicant = models.FileField(upload_to='contract-applicant', null=True)
    event_date = models.DateField(default=None, null=True)
    deadline = models.DateTimeField(default=None, null=True)
    reason_rejection = models.TextField(null=True)
    comment = models.TextField(null=True)

    question_1 = models.CharField(max_length=100,null=True, blank=True)
    question_2 = models.CharField(max_length=100,null=True, blank=True)
    question_3 = models.CharField(max_length=100,null=True, blank=True)
    question_4 = models.CharField(max_length=100,null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    objects = Applicant()

    class Meta():
        verbose_name = 'Mentor'
        verbose_name_plural = 'Mentors'


class Member(models.Model):
    STATUS_REQUEST = (
        ('new', 'New'),
        ('send-contract', 'Send contract'),
        ('send-contract-to-expert', 'Send contract to the contract'),
        ('not-response', 'Not response '),
        ('confirmed', 'Confirmed'),
        ('confirmed-by-expert', 'Confirmed by expert'),

        ('send-to-director', 'send-to-director'),

        ('revised_by_expert', 'revised_by_expert'),
        ('revised-director-to-expert', 'revised-director-to-expert'),

        ('reject', 'Reject'),
    )

    STATUS_REMOVE = (
        ('request-remove', 'request-remove'),
        ('request-remove-send-to-the-director', 'request-remove-send-to-the-director'),
        ('request-reject-by-director', 'request-reject-by-director'),
        ('request-accpet-by-director', 'request-accept-by-director'),

        ('request-accpet-by-expert', 'request-accept-by-expert'),
        ('request-reject-by-expert', 'request-reject-by-expert'),
    )

    research = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='mmber_project')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_REQUEST, null=True, default='new', verbose_name='Choose your position!')
    status_remove = models.CharField(max_length=60, choices=STATUS_REMOVE, null=True, default=None, blank=True, verbose_name='Choose your position!')
    contract = models.FileField(upload_to='contract-expert-applicant', null=True)
    contract_applicant = models.FileField(upload_to='contract-applicant', null=True)
    event_date = models.DateField(default=None, null=True)
    deadline = models.DateTimeField(default=None, null=True)
    reason_rejection = models.TextField(null=True)
    comment = models.TextField(null=True)

    question_1 = models.CharField(max_length=100,null=True, blank=True)
    question_2 = models.CharField(max_length=100,null=True, blank=True)
    question_3 = models.CharField(max_length=100,null=True, blank=True)
    question_4 = models.CharField(max_length=100,null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    objects = Applicant()

    class Meta():
        verbose_name = 'Member'
        verbose_name_plural = 'Members'

class Lerner(models.Model):
    STATUS_REQUEST = (
        ('new', 'New'),
        ('send-contract', 'Send contract'),
        ('send-contract-to-expert', 'Send contract to the contract'),
        ('not-response', 'Not response '),
        ('confirmed', 'Confirmed'),
        ('confirmed-by-expert', 'Confirmed by expert'),

        ('send-to-director', 'send-to-director'),

        ('revised_by_expert', 'revised_by_expert'),
        ('revised-director-to-expert', 'revised-director-to-expert'),

        ('reject', 'Reject'),
    )

    STATUS_REMOVE = (
        ('request-remove', 'request-remove'),
        ('request-remove-send-to-the-director', 'request-remove-send-to-the-director'),
        ('request-reject-by-director', 'request-reject-by-director'),
        ('request-accpet-by-director', 'request-accept-by-director'),

        ('request-accpet-by-expert', 'request-accept-by-expert'),
        ('request-reject-by-expert', 'request-reject-by-expert'),
    )

    research = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='lerner_project')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, choices=STATUS_REQUEST, null=True, default='new', verbose_name='Choose your position!')
    status_remove = models.CharField(max_length=60, choices=STATUS_REMOVE, null=True, default=None, blank=True, verbose_name='Choose your position!')
    contract = models.FileField(upload_to='contract-expert-applicant', null=True)
    contract_applicant = models.FileField(upload_to='contract-applicant', null=True)
    event_date = models.DateField(default=None, null=True)
    deadline = models.DateTimeField(default=None, null=True)
    reason_rejection = models.TextField(null=True)
    comment = models.TextField(null=True)

    question_1 = models.CharField(max_length=100,null=True, blank=True)
    question_2 = models.CharField(max_length=100,null=True, blank=True)
    question_3 = models.CharField(max_length=100,null=True, blank=True)
    question_4 = models.CharField(max_length=100,null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    objects = Applicant()

    class Meta():
        verbose_name = 'Learner'
        verbose_name_plural = 'Learners'
    
    

class CommentProject(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('accepted', 'Accepted'),
        ('rejected', 'rejected'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    commentproject = models.ForeignKey(ResearchProject, null=True, on_delete=models.CASCADE, related_name='project_comment')
    comment = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    email = models.EmailField(max_length=20, )
    created = models.DateTimeField(auto_now_add=True)

    class Meta():
        verbose_name = 'Project comment'
        verbose_name_plural = 'Project comments'



class ReportApplicant(models.Model):
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='applicants_wbs')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, null=True, related_name='project_wbs')
    position = models.CharField(max_length=100, null=True)
    wbs_obj = models.ForeignKey(TimeProgramming, on_delete=models.CASCADE, related_name='wbs_objects')
    question_1 = models.CharField(max_length=100, null=True)
    question_2 = models.CharField(max_length=100, null=True)
    question_3 = models.CharField(max_length=100, null=True)
    question_4 = models.CharField(max_length=100, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta():
        verbose_name = 'Project report applocant'
        verbose_name_plural = 'Project report applocant'

#   send_to_expert
#   send-to-applicant
#   send_to_main_supervisor
class ApplicantComment(models.Model):
    sender  = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='comment_sender')
    recipient  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comment_recipient')

    project = models.ForeignKey(ResearchProject, null=True, on_delete=models.CASCADE, related_name='comment_project')
    position = models.CharField(max_length=100, null=True)
    comment = models.TextField(null=True)
    seen = models.BooleanField(default=False, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    objects = ApplicantComment()

class ApplicantReplyComment(models.Model):
    replycomment = models.ForeignKey(ApplicantComment, null=True, on_delete=models.CASCADE, related_name='comments')
    position = models.CharField(max_length=100, null=True)
    comment = models.TextField(null=True)
    seen = models.BooleanField(default=False, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)
