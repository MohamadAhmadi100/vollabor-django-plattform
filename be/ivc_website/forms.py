from django import forms

from .models import Project, News, ProjectContract, ProjectContractReply, ProjectProposal, NewsCategory, Event, SuggestionBox, Video, VideoCategory
from django.utils.translation import gettext_lazy as _


class DateInput(forms.DateInput):
    """
    Date input class which is a widget we can use to show date format input instead of plain text in our form
    """
    input_type = 'date'


class ProjectForm(forms.ModelForm):
    """
    With this form, Members can add a new project
    """
    start_date = forms.DateField(widget=DateInput, label=_("Start Date"), required=False)
    end_date = forms.DateField(widget=DateInput, label=_("End Date"), required=False)

    project_rfp = forms.FileField(help_text="Format should be PDF", label="RFP (Request For Proposal)",
                                    widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    class Meta:
        model = Project
        fields = ['title', 'start_date', 'end_date', 'description', 'project_equipment', 'project_requirements', 'fund', 'project_rfp']

    def clean_project_rfp(self):
        project_rfp = self.cleaned_data.get('project_rfp')
        if project_rfp.content_type != 'application/pdf':
            raise forms.ValidationError('Proposal File must be in PDF format')
        return project_rfp


class ProjectInfoForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_information']


class ProjectProposalForm(forms.ModelForm):
    proposal_file = forms.FileField(help_text="Format should be PDF",
                                    widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    class Meta:
        model = ProjectProposal
        fields = ['proposal_file']
    
    def clean_proposal_file(self):
        proposal_file = self.cleaned_data.get('proposal_file')
        if proposal_file.content_type != 'application/pdf':
            raise forms.ValidationError('Proposal File must be in PDF format')
        return proposal_file


class ProjectContractForm(forms.ModelForm):
    contract_file = forms.FileField(help_text="Format should be PDF",
                                    widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    class Meta:
        model = ProjectContract
        fields = ['contract_file']


class ProjectContractReplyForm(forms.ModelForm):
    contract_file = forms.FileField(help_text="Format should be PDF",
                                    widget=forms.FileInput(attrs={'accept': 'application/pdf'}))

    class Meta:
        model = ProjectContractReply
        fields = ['contract_file']


class NewsForm(forms.ModelForm):
    description = forms.CharField(label='Description',
                   widget=forms.Textarea(attrs={'class': 'ckeditor'}))

    class Meta:
        model = News
        fields = ["author","title", "description", "thumbnail", "date", "status", "category", "home"]

class CategoryForm(forms.ModelForm):
    class Meta:
        model = NewsCategory
        fields = ["title", "slug", "status"]
        
class EventForm(forms.ModelForm):
    description = forms.CharField(label='Description',
                   widget=forms.Textarea(attrs={'class': 'ckeditor'}))
    class Meta:
        model = Event
        fields = ["author","title", "description", "thumbnail", "date", "status", "home"]
        
class SendRepoertByMainSupervisor(forms.Form):
    # Status
    status_new = forms.BooleanField(
        required = False
    )
    status_on_going = forms.BooleanField(
        required = False
    )
    status_done = forms.BooleanField(
        required = False
    )

    #Grade
    grade_hard = forms.BooleanField(
        required = False
    )
    grade_normal = forms.BooleanField(
        required = False
    )
    grade_easy = forms.BooleanField(
        required = False
    )
    
    
class SuggestionForm(forms.ModelForm):
    class Meta:
        model = SuggestionBox
        fields = ["email", "title", "description"]


class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ['user','title','category','description','link','image','status', 'is_top']

class VideoCategoryForm(forms.ModelForm):
    class Meta:
        model = VideoCategory
        fields = ["title", "slug", "status"]

class CommentProjectForm(forms.Form):
    email = forms.CharField(
        widget=forms.TextInput()
    )
    comment = forms.CharField(
        widget=forms.Textarea(),
    )
    id_project = forms.IntegerField( )
