from django import forms
from django.utils.safestring import mark_safe

from ivc_website.models import Project
from .models import Announcement

week_days = (
    ("", '-----'),
    ("Monday", 'Monday'),
    ("Tuesday", 'Tuesday'),
    ("Wednesday", 'Wednesday'),
    ("Thursday", 'Thursday'),
    ("Friday", 'Friday'),
    ("Saturday", 'Saturday'),
    ("Sunday", 'Sunday'),
)


class DateInput(forms.DateInput):
    """
    Date input class which is a widget we can use to show date format input instead of plain text in our form
    """
    input_type = 'date'


class TimeInput(forms.DateInput):
    """
    Time input class which is a widget we can use to show time format input instead of plain text in our form
    """
    input_type = 'time'


class MeetingForm(forms.ModelForm):
    """
    form to inform project meeting times
    """
    week_day = forms.ChoiceField(required=False, label="Day of the week", choices=week_days)
    meeting_time = forms.TimeField(widget=TimeInput)
    meeting_timezone = forms.CharField(required=False, label="",
                                       widget=forms.TextInput(attrs={'placeholder': 'Meeting Timezone'}))
    meeting_link = forms.URLField(required=False, label="",
                                  widget=forms.TextInput(attrs={'placeholder': 'Meeting Link'}))

    class Meta:
        model = Project
        fields = ['week_day', 'meeting_time', 'meeting_timezone', 'meeting_link', 'meeting_language']


class EditProjectForm(forms.ModelForm):
    start_date = forms.DateField(widget=DateInput)
    end_date = forms.DateField(widget=DateInput, required=False)

    class Meta:
        model = Project
        fields = ['title', 'start_date', 'end_date', 'description', 'project_equipment', 'project_requirements',
                  'slack_channel_address', 'slack_workspace_address', 'skype_address', 'google_drive_address',
                  'conference_url', 'journal_url']

    def clean(self):
        cleaned_data = super(EditProjectForm, self).clean()
        status = cleaned_data.get("status")
        end_date = cleaned_data.get("end_date")

        if status == 'Ongoing':
            total_percentage = 0
            project_members = self.instance.projectmember_set.all()

            if end_date is None:
                raise forms.ValidationError("You should specify end date when project status is ongoing")

        return cleaned_data


class ProjectSocialForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['slack_workspace_address', 'slack_channel_address', 'google_drive_address', 'skype_address',
                  'supervisor_message']


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'description']


class UploadMemberContractForm(forms.Form):
    contract = forms.FileField(help_text=mark_safe('<a href="/static/dashboard/Employment-Contract-Agreement.pdf" '
                                                   'target="_blank" class="text-muted d-block">download empty '
                                                   'contract</a>'), required=True,
                               widget=forms.FileInput(attrs={'accept': 'application/pdf'}))
                               
                               
                               

class ChangeDeadLineResearch(forms.Form):
	deadline = forms.DateField(
	)
	

class AcceptCommentResearch(forms.Form):
    status = forms.CharField()
    id_comment = forms.CharField()

class RejectCommentResearch(forms.Form):
    id_comment = forms.CharField()
    

class DeleteRequestForm(forms.Form):
    status = forms.CharField()
    