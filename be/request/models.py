from django.db import models
from django.contrib.auth.models import User
from django.db.models.base import Model
from django.utils import timezone

# Create your models here.


# badge request
class BadgeRequest(models.Model):
    REQUEST_STATUS = (
        ('Notpay', 'Notpay'),
        ('trash', 'trash'),
        ('New', 'New'),
        ('Reject-badge-manager', 'Reject-badge-manager'),
        ('Reject-badge-expert', 'Reject-badge-expert'),
        ('Review', 'Review'),
        ('Set-session', 'Set-session'),
        ('Approve-decline', 'Approve-decline'),
        ('Interview', 'Interview'),
        ('Expert-view', 'Expert-view'),
        ('send_manager', 'Send to manager'),
        ('decline-review-interview', 'Decline review, interview'),
        ('Accept', 'Accept'),
        ('Accept-manager', 'Accept-manager'),
        ('Reject', 'Reject'),
        ('revise_by_manager', 'Revise by manager'),
    )
    REQUEST_POSITION = (
        ('Interview', 'Interview'),
        ('Review', 'Review'),
    )
    unique_id = models.CharField(max_length=30,editable = False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skills = models.CharField(max_length=150, default="")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    other = models.BooleanField(null=True, default=False)
    reason_reject = models.TextField(null=True)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default="Notpay")
    position = models.CharField(max_length=20, choices=REQUEST_POSITION, null=True)
    score = models.IntegerField(default=0, null=True)
    access_accept_reject = models.BooleanField(null=True, default=False)
    accepted_date = models.DateField(null=True)
    rejected_date = models.DateField(null=True)
    revised_date = models.DateField(null=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.skills + " by " + str(self.user.get_full_name())


class BadgeInterviewReview(models.Model):
    STATUS_CHIOCE = (
        ('interviewer', 'interviewer'),
        ('reviewer', 'reviewer'),
    )
    ACCEPT_REJECT_CHIOCE = (
        ('new', 'new'),
        ('approve', 'approve'),
        ('decline', 'decline'),
        ('not_see', 'not see'),
        ('breach_of_promis', 'breach of promis'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, choices=STATUS_CHIOCE)
    badge = models.ForeignKey(BadgeRequest, on_delete=models.CASCADE, related_name='badge_request')
    comment = models.TextField(default="", null=True, blank=True)
    score = models.IntegerField(default=0,null=True)
    score_file = models.FileField(default="", blank="True", null=True, upload_to='requets/badge/')
    accept_reject = models.CharField(max_length=50, choices=ACCEPT_REJECT_CHIOCE, default="new")
    score_1 = models.IntegerField(default=0, null=True)
    score_2 = models.IntegerField(default=0, null=True)
    score_3 = models.IntegerField(default=0, null=True)
    score_4 = models.IntegerField(default=0, null=True)
    score_5 = models.IntegerField(default=0, null=True)
    score_6 = models.IntegerField(default=0, null=True)
    score_7 = models.IntegerField(default=0, null=True)
    score_8 = models.IntegerField(default=0, null=True)
    score_9 = models.IntegerField(default=0, null=True)
    score_10 = models.IntegerField(default=0, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " for " + str(self.badge)


class SupervisorRequest(models.Model):
    REQUEST_STATUS = (
        ('Notpay', 'Notpay'),
        ('trash', 'trash'),
        ('New', 'New'),
        ('Review', 'Review'),
        # ('Expert-view', 'Expert-view'),
        # ('Accept', 'Accept'),
        # ('Reject', 'Reject'),

        ('reviewer_evaluated', 'evaluated Reviewer'),
        ('reviewer_accept', 'Accept Reviewer '),
        ('reviewer_reject', 'Reject Reviewer '),
        ('send_to_manager', 'Send to manager'),
        ('revise_by_manager', 'Revise by manager'),
        ('revise_by_expert', 'Revise by expert'),

        ('accepted_by_manager', 'Accepted by manager'),
        ('accepted_by_expert', 'Accepted by expert'),

        ('rejected_by_manager', 'Rejected by manager'),
        ('rejected_by_expert', 'Rejected by expert'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_request = models.CharField(max_length=20, null=True)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="expert_supervisor")
    latest_degree = models.FileField(default="", upload_to="request/supervisor/latest_degree/", null=True, verbose_name="Latest academic degree")
    valid_evidence = models.FileField(default="", upload_to="request/supervisor/valid_evidence/", null=True, verbose_name="Valid evidence")
    identification = models.FileField(default="", upload_to="request/supervisor/identification/", null=True, verbose_name="Identification")
    latest_resume = models.FileField(default="", upload_to="request/supervisor/latest_resume/", null=True, verbose_name="Latest resume")
    state_of_purpose = models.CharField(max_length=3000, default="", blank=True, null=True)
    comment = models.TextField(default="", blank=True, null=True)
    recommendation_letter = models.FileField(default="", upload_to="request/supervisor/recommendation_letter/", null=True, verbose_name="Recommendation letter")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default="Notpay")
    # score = models.IntegerField(default=0, null=True)
    accepted_date = models.DateField(null=True)
    rejected_date = models.DateField(null=True)
    revised_date = models.DateField(null=True)

    access_accept_reject = models.BooleanField(null=True, default=False)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.user.get_full_name())

class SupervisorReview(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('reject', 'Reject'),
        ('accept', 'Accept'),
        ('evaluated', 'Evaluated'),
        ('revise', 'Revise'),
        ('done', 'Done'),
        ('not_see', 'Not see'),
        ('breach_of_promis', 'Breach or promis'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    supervisor = models.ForeignKey(SupervisorRequest, on_delete=models.CASCADE, related_name='supervisor_request')
    comment = models.TextField(default="", null=True, blank=True)
    score = models.IntegerField(default=0,null=True)
    score_file = models.FileField(default="", null=True, upload_to='requets/badge/')
    status = models.CharField(max_length=20, null=True, default='new', choices=STATUS_CHOICES)
    deadlien = models.DateTimeField(default=timezone.now(), null=True)
    score_1 = models.IntegerField(default=0, null=True)
    score_2 = models.IntegerField(default=0, null=True)
    score_3 = models.IntegerField(default=0, null=True)
    score_4 = models.IntegerField(default=0, null=True)
    score_5 = models.IntegerField(default=0, null=True)
    score_6 = models.IntegerField(default=0, null=True)
    score_7 = models.IntegerField(default=0, null=True)
    score_8 = models.IntegerField(default=0, null=True)
    score_9 = models.IntegerField(default=0, null=True)
    score_10 = models.IntegerField(default=0, null=True)
    declined_date = models.DateField(null=True)

    def __str__(self):
        return str(self.user.get_full_name()) + " for " + str(self.supervisor)


class InterviewSession(models.Model):
    sender = models.ForeignKey(BadgeInterviewReview, on_delete=models.CASCADE)
    target = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(default="", null=True ,blank=True)
    meeting_link = models.CharField(max_length=200, default="", null=True)
    start_at = models.DateTimeField(null=True)
    time_zone = models.CharField(max_length=400, default="")
    finished = models.BooleanField(default=False)

    def __str__(self):
        return "Meeting with {user}".format(user = self.target.get_full_name())


class WorkshopRequest(models.Model):
    REQUEST_STATUS = (
        ('Notpay', 'Notpay'),
        ('trash', 'trash'),
        ('New', 'New'),
        ('Review', 'Review'),

        ('reviewer_evaluated', 'evaluated Reviewer'),
        ('reviewer_reject', 'Reject Reviewer '),
        ('reviewer_accept', 'Accept Reviewer '),
        ('send_to_manager', 'Send to manager'),
        ('accepted_by_manager', 'Accepted by manager'),
        ('accepted_by_expert', 'Accepted by expert'),

        ('rejected_by_manager', 'Rejected by manager'),
        ('rejected_by_expert', 'Rejected by expert'),

        ('revised_by_manager', 'Revised by manager'),
        ('revised_by_expert', 'Revised by expert'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_request = models.CharField(max_length=20, null=True)
    expert = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="expert_workshop")
    latest_degree = models.FileField(default="", upload_to="request/workshop/latest_degree/", null=True, verbose_name="Latest academic degree")
    valid_evidence = models.FileField(default="", upload_to="request/workshop/valid_evidence/", null=True, verbose_name="Valid evidence")
    identification = models.FileField(default="", upload_to="request/workshop/identification/", null=True, verbose_name="Identification")
    latest_resume = models.FileField(default="", upload_to="request/workshop/latest_resume/", null=True, verbose_name="Latest resume")
    state_of_purpose = models.TextField(default="", blank=True, null=True)
    recommendation_letter = models.FileField(default="", upload_to="request/workshop/recommendation_letter/", null=True, verbose_name="Recommendation letter")
    certificate = models.FileField(default="", upload_to="request/workshop/certificate/", null=True, verbose_name="Certificate")
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, choices=REQUEST_STATUS, default="Notpay")
    comment = models.TextField(default="", blank=True, null=True)
    accepted_date = models.DateField(null=True)
    rejected_date = models.DateField(null=True)
    revised_date = models.DateField(null=True)



    access_accept_reject = models.BooleanField(null=True, default=False)
    class Meta:
        ordering = ['-created']

    def __str__(self):
        return str(self.user.get_full_name())



class WorkshopReview(models.Model):
    STATUS_CHOICES = (
        ('new', 'New'),
        ('reject', 'Reject'),
        ('accept', 'Accept'),
        ('evaluated', 'Evaluated'),
        ('revise', 'Revise'),
        ('done', 'Done'),
        ('not_see', 'Not see'),
        ('breach_of_promis', 'Breach or promis'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    workshop = models.ForeignKey(WorkshopRequest, on_delete=models.CASCADE, related_name='workshop_request')
    comment = models.TextField(default="", null=True, blank=True)
    score = models.IntegerField(default=0,null=True)
    score_file = models.FileField(default="", null=True, upload_to='requets/badge/')
    status = models.CharField(max_length=20, null=True, default='new', choices=STATUS_CHOICES)
    deadlien = models.DateTimeField(default=timezone.now(), null=True)
    score_1 = models.IntegerField(default=0, null=True)
    score_2 = models.IntegerField(default=0, null=True)
    score_3 = models.IntegerField(default=0, null=True)
    score_4 = models.IntegerField(default=0, null=True)
    score_5 = models.IntegerField(default=0, null=True)
    score_6 = models.IntegerField(default=0, null=True)
    score_7 = models.IntegerField(default=0, null=True)
    score_8 = models.IntegerField(default=0, null=True)
    score_9 = models.IntegerField(default=0, null=True)
    score_10 = models.IntegerField(default=0, null=True)
    declined_date = models.DateField(null=True)
    
    def __str__(self):
        return str(self.user.get_full_name()) + " for " + str(self.workshop)

class BadgeExpert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    badge = models.ForeignKey(BadgeRequest, on_delete=models.CASCADE, related_name="badge_expert")
    comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user.get_full_name())
