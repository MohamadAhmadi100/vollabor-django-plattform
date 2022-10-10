from django import forms
from django.db import models
from django.db.models import fields
from .models import BadgeRequest, InterviewSession, SupervisorRequest, WorkshopRequest


class BadgeForm(forms.ModelForm):

    class Meta:
        model = BadgeRequest
        fields = ['skills']


class SessionForm(forms.ModelForm):
    class Meta:
        model = InterviewSession
        fields = ['description','meeting_link','start_at', 'time_zone']


class SupervisorForm(forms.ModelForm):

    class Meta:
        model = SupervisorRequest
        fields = ['latest_degree','valid_evidence','identification','latest_resume','state_of_purpose','recommendation_letter']

class WorkshopRequestForm(forms.ModelForm):

    class Meta:
        model = WorkshopRequest
        fields = ['latest_degree','valid_evidence','identification','latest_resume','state_of_purpose','recommendation_letter', 'certificate']
        

class SelectReviewer(forms.Form):
    reviewer = forms.CharField(
        widget=forms.TextInput()
    )

class ApproveReviewerForm(forms.Form):
    approve = forms.CharField(
        widget=forms.TextInput()
    )

class DeclineReviewerForm(forms.Form):
    decline = forms.CharField(
        widget=forms.TextInput()
    )
    reject_reason = forms.CharField(
        widget=forms.TextInput()
    )

class ReviewerSendForExpertForm(forms.Form):
    comment = forms.CharField()

class ChangeExpertManager(forms.Form):
    access_accept_reject = forms.BooleanField(
        required=False
        )
    id_expert = forms.CharField()