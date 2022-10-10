import datetime
from django import forms
from .models import IndustryFormClient, IndustryExpertForSupervisor, ResearchProject, RequestUserForProject
from django.core import validators
from django.core.validators import MaxValueValidator, MinValueValidator, FileExtensionValidator

class SendClintForm(forms.ModelForm):
	class Meta:
		model = IndustryFormClient
		fields = ['user', 'name' , 'title' , 'abstrack', 'equipment', 'requirement',]
	


class CreateForm(forms.Form):

	name = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)
	title = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)

	abstrack = forms.CharField(
		required=False,
		widget=forms.Textarea(),
		label='Abstract'
	)
	data_set_link = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)
	start_date = forms.DateField(
		required=False,
		widget=forms.DateInput()
	)
	end_date = forms.DateField(
		required=False,
		widget=forms.DateInput()
	)
	equipment = forms.CharField(
		required=False,
		widget=forms.Textarea()
	)
	requirement = forms.CharField(
		required=False,
		widget=forms.Textarea()
	)
	main_supervisor = forms.FileField(
		required=False,
		validators=[FileExtensionValidator(['pdf','doc','docx'])]
	)
	pri_file = forms.FileField(
		required=False,
		validators=[FileExtensionValidator(['pdf','doc','docx'])]
	)
	fund = forms.DecimalField(
		initial=0.00,
		required=False
	)
	question_1 = forms.CharField(
		widget=forms.HiddenInput(),
		label=1,
		required=False
	)
	question_2 = forms.CharField(
		widget=forms.HiddenInput(),
		label=2,
		required=False
	)
	question_3 = forms.CharField(
		widget=forms.HiddenInput(),
		label=3,
		required=False
	)
	question_4 = forms.CharField(
		widget=forms.HiddenInput(),
		label=4,
		required=False
	)
	question_5 = forms.CharField(
		widget=forms.HiddenInput(),
		label=5,
		required=False
	)
	question_6 = forms.CharField(
		widget=forms.HiddenInput(),
		label=6,
		required=False
	)
	question_7 = forms.CharField(
		widget=forms.HiddenInput(),
		label=7,
		required=False
	)
	
	main_field = forms.IntegerField(
	)
	sub_field = forms.IntegerField(
	)
	add_sub_field = forms.CharField(
		widget=forms.Textarea(),
		required=False
	)
class SendExpertForm(forms.Form):

	name = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)
	title = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)
	abstrack = forms.CharField(
		required=False,
		widget=forms.Textarea(),
		label = 'Abstract'
	)
	data_set_link = forms.CharField(
		required=False,
		widget=forms.TextInput(),
		label = 'Dataset Link'
	)
	start_date = forms.DateField(
		required=False,
		widget=forms.DateInput()
	)
	end_date = forms.DateField(
		required=False,
		widget=forms.DateInput()
	)
	fund = forms.DecimalField(
		required=False,
	)
	equipment = forms.CharField(
		required=False,
		widget=forms.Textarea()
	)
	requirement = forms.CharField(
		required=False,
		widget=forms.Textarea()
	)
	user_list = forms.CharField(
		widget=forms.TextInput(attrs={"id": "user-list"}),
	

	)

	directo_a_or_r_mainsupervisor = forms.BooleanField(
		required=False,
		label='Access to accept or reject the project'
	)
	directo_see_reviewer = forms.BooleanField(
		required=False,
		label='Access to see the reviewer’s scores'
	)
	directo_create_project = forms.BooleanField(
		required=False,
		label='Access to create a research project '
	)
	director_reject_proposal = forms.BooleanField(
		required=False,
		label='Access to reject the proposal'
	)


class SendRejectForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput(),
	)

	reason_rejectd = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":8, "cols":30}),
		label = 'Reasons for rejection'
	)


class SendExpertForSupervisor(forms.Form):

	name = forms.CharField(
		widget=forms.TextInput(),
		disabled = True
	)
	title = forms.CharField(
		widget=forms.TextInput(),
		disabled = True

	)
	abstrack = forms.CharField(
		widget=forms.Textarea(),
		disabled = True

	)
	equipment = forms.CharField(
		widget=forms.Textarea(),
		disabled = True

	)
	requirement = forms.CharField(
		widget=forms.Textarea(),
		disabled = True

	)


class ExpertSendSupervisor(forms.Form):
	form_id = forms.IntegerField(
	)
	deadline = forms.DateField(
	)

class ExpertSendSupervisor_(forms.Form):
	status_supervisor = forms.CharField(
		widget=forms.TextInput(),
	)
	deadline = forms.DateField()

class Reviewer(forms.Form):
	user_list = forms.CharField(
		widget=forms.TextInput(attrs={"id": "user-list"}),

	)
	status = forms.CharField(
		widget=forms.TextInput(),
	)


class DeleteProjectUser(forms.ModelForm):
	class Meta:
		model = IndustryFormClient
		fields = ['status']
	
class ReturnedProjectForSupervisor(forms.ModelForm):
	class Meta:
		model = IndustryExpertForSupervisor
		fields = ['status', 'reason_reject']




class SendContractForSupervisor(forms.Form):
	Contract = forms.FileField(
		label = "Upload the contract",
		validators=[FileExtensionValidator(['pdf', ])]
	)
	status = forms.CharField(
		widget=forms.TextInput()
	)

class ReviseContract(forms.Form):
	Contract = forms.FileField(
		label = "Upload the contract",
		required=False,
		validators=[FileExtensionValidator(['pdf', ])]
	)
	comment = forms.CharField(
		widget=forms.Textarea(),
	)
	
class SendContractToDirector(forms.Form):
	Contract_d = forms.FileField(
	    label = "Upload the contract",
		validators=[FileExtensionValidator(['pdf', ])]
	)
	status_d = forms.CharField(
		widget=forms.TextInput()
	)

	status_value_d = forms.CharField(
		widget=forms.TextInput(),
		required=False
	)
	valeu_d = forms.IntegerField(
		widget=forms.NumberInput(),
		label='Spiritual value ($)',
		required=False,
		validators=[MinValueValidator(0)],
	)



class CreateNewProject(forms.Form):

	status = forms.CharField(
		widget=forms.TextInput()
	)
	
class FormStatus(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)


class StatusAcceptDirectorFrom(forms.Form):
	status_d = forms.CharField(
		widget=forms.TextInput()
	)

	status_value = forms.CharField(
		widget=forms.TextInput()
	)

	value = forms.IntegerField(
		label="Spiritual value ($)",
		required=False,
		validators=[MinValueValidator(0)],
	)
class FormSupervisorAccept(forms.Form):
	propzar = forms.FileField(
		required=False,
		label= 'Upload proposal'
	)

	status = forms.CharField(
		widget=forms.TextInput()
	)
	
	
class FormDeclineRequestSupervisor(forms.Form):
  	status_d = forms.CharField(
		widget=forms.TextInput()
	)  
	
class FormWithdrew(forms.Form):
    status = forms.CharField(
        widget=forms.TextInput()
    )  

    reason = forms.CharField(
        required=False,
        widget=forms.Textarea()
    )
	
class FormAdvestiment(forms.Form):
	grade = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Grade of project'
	)

	skills_required = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Skills required to attend in project (Add some bullets)'
	)

	project_ponsored = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Project will be sponsored by (Company or University or Institute)'
	)

	informative_bullets = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Few informative bullets to describe content of project(maximum 6 bullets)'
	)

	social_platforms = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Suggested helpful social media platforms (name of related groups and links) which you think they are useful to advertise'
	)

	fruitful_countries = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Suggest fruitful countries'
	)

	motivating_keywords = forms.CharField(
		required=False,
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Motivating keywords (Maximum: 6 keywords)'
	)

	upload_pictures = forms.ImageField(
		label='⦁ Upload high quality related pictures for project'
	)

	benefit_of_members = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ What is the benefit of members being present in the project for them?'
	)
	supervisor_information = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁	First supervisor’s information', 
	)

class FormTimeProgramming(forms.Form):
	topic = forms.CharField(
		widget=forms.TextInput()
	)

	start_date = forms.DateField(
		widget=forms.DateInput(),
		label='Strat Date'
	)

	end_date = forms.DateField(
		widget=forms.DateInput(),
		label='End Date'
	)

class FormViewAdvestiment(forms.Form):
	title = forms.CharField(
		widget=forms.TextInput(),
		label='⦁ Title', 
		disabled=True,
		required=False
	)

	start_date = forms.CharField(
		widget=forms.TextInput(),
		label='⦁ Start Date', 
		disabled=True,
		required=False
	)

	end_date = forms.CharField(
		widget=forms.TextInput(),
		label='⦁ End Date', 
		disabled=True,
		required=False
	)

	email = forms.CharField(
		widget=forms.TextInput(),
		label='⦁ Email', 
		disabled=True,
		required=False
	)

	phone = forms.CharField(
		widget=forms.TextInput(),
		label='⦁ Phone', 
		disabled=True,
		required=False
	)

	supervisor_information = forms.CharField(
		widget=forms.TextInput(),
		label='⦁	First supervisor’s information', 
		disabled=True,
		required=False
	)

	grade = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Grade of project', 
		disabled=True,
		required=False
	)

	skills_required = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Skills required to attend in project (Add some bullets)', 
		disabled=True,
		required=False
	)

	project_ponsored = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Project will be sponsored by (Company or University or Institute)', 
		disabled=True,
		required=False
	)

	informative_bullets = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Few informative bullets to describe content of project(maximum 6 bullets)', 
		disabled=True,
		required=False
	)

	social_platforms = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Suggested helpful social media platforms (name of related groups and links) which you think they are useful to advertise', 
		disabled=True,
		required=False
	)

	fruitful_countries = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Suggest fruitful countries', 
		disabled=True,
		required=False

	)

	motivating_keywords = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ Motivating keywords (Maximum: 6 keywords)', 
		disabled=True,
		required=False

	)

	upload_pictures = forms.ImageField(
		label='⦁ Upload high quality related pictures for project', 
		disabled=True,
		required=False

	)

	benefit_of_members = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁ What is the benefit of members being present in the project for them?', 
		disabled=True,
		required=False

	)
	supervisor_information = forms.CharField(
		widget=forms.Textarea(attrs={"class":"form-control", "rows":3, "cols":30}),
		label='⦁	First supervisor’s information', 
		disabled=True,
		required=False
	)
class FormSupervisorSendContract(forms.Form):
	contract_supervisor = forms.FileField(
		label='Upload the contract',
		validators=[FileExtensionValidator(['pdf', ])]
	)
	status = forms.CharField(
		widget=forms.TextInput()
	)

class FormRejectDirector(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
	reason_reject = forms.CharField(
	    label = "Reasons for rejection",
	    required=False,
		widget=forms.Textarea()
	)

class AccessExpert(forms.Form):
	directo_a_or_r_mainsupervisor = forms.BooleanField(
		required=False,
		label='Access to accept or reject the project'
	)
	directo_see_reviewer = forms.BooleanField(
		required=False,
		label='Access to see the reviewer’s scores'
	)
	directo_create_project = forms.BooleanField(
		required=False,
		label='Access to create a research project '
	)
	director_reject_proposal = forms.BooleanField(
		required=False,
		label='Access to reject the proposal'
	)
	is_supervisor = forms.BooleanField(
	)
	
	
class SendRepoertByMainSupervisorForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
	report = forms.CharField(
		widget=forms.Textarea()
	)
	id_pr = forms.IntegerField(
		label = 'Score'
	)

	
	
class SendScoreForDirector(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)

	status_value = forms.CharField(
		widget=forms.TextInput()
	)

	value = forms.IntegerField(
		label="Spiritual value",
		required=False,
        validators=[MinValueValidator(0)],
	)

	text = forms.CharField(
		required=False,
		label='Comment',
		widget=forms.Textarea()
	)
	
class SendScoreReview(forms.Form):
	score = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	score_1 = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	score_2 = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	score_3 = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	score_4 = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	score_5 = forms.IntegerField(
	    required=False,
        label = 'Score'
    )
	score_6 = forms.IntegerField(
	    required=False,
        label = 'Score',
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
	
	status = forms.CharField(
		widget=forms.TextInput()
	)	
	
	
class SendRepoertByMainSupervisor(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
	report = forms.CharField(
		widget=forms.Textarea()
	)
	
class ResendProjectForm(forms.Form):
	name = forms.CharField(
		widget=forms.TextInput()
	)
	title = forms.CharField(
		widget=forms.TextInput()
	)

	abstrack = forms.CharField(
		widget=forms.Textarea(),
		label='Abstract'
	)
	data_set_link = forms.CharField(
		widget=forms.TextInput()
	)
	start_date = forms.DateField(
		widget=forms.DateInput()
	)
	end_date = forms.DateField(
		widget=forms.DateInput()
	)
	equipment = forms.CharField(
		widget=forms.Textarea()
	)
	requirement = forms.CharField(
		widget=forms.Textarea()
	)
	main_supervisor = forms.FileField(
		required=False,
		validators=[FileExtensionValidator(['pdf', ])]
	)
	fund = forms.DecimalField(
		initial=0.00,
		required=False
	)

class ChangeStatusProjectForm(forms.Form):
	status_ = forms.CharField(
		widget=forms.Textarea()
	)

	final_document = forms.FileField(
		label='Progress report middle ',
		required=False,
		validators=[FileExtensionValidator(['pdf', ])]
	)
	description = forms.CharField(
		widget=forms.Textarea()
	)

class ProgressReportEndProjectForm(forms.Form):
	progress_report_end_project = forms.FileField(
		label='Progress report end ',
		validators=[FileExtensionValidator(['pdf', ])]
	)

class ProgressReportMiddleProjectForm(forms.Form):
	progress_report_middle_project = forms.FileField(
		label='Progress report middle ',
		validators=[FileExtensionValidator(['pdf', ])]
	)

class StatusHomeForm(forms.Form):
	status_home = forms.BooleanField()
	
	
class DeclineReviewerForm(forms.Form):
	status_r = forms.CharField(
		widget=forms.TextInput()
	)

	comment = forms.CharField(
		widget=forms.Textarea(),
		label='Decline reason'
	)
	
class RejectReviewForm(forms.Form):
	status_r = forms.CharField(
		widget=forms.TextInput()
	)
	


class DeleteProjectReviewer(forms.Form):
	status_delete = forms.CharField(
		widget=forms.Textarea()
	)


class ApplyProjectForm(forms.Form):
	learner = forms.BooleanField(
		label= 'learner',
		required=False,
		)

	member = forms.BooleanField(
		label= 'member',
		required=False,
		)

	mentor = forms.BooleanField(
		label= 'mentor',
		required=False,
		)

	supervisor = forms.BooleanField(
		label= 'supervisor',
		required=False,
		)

	status = forms.CharField(
		widget=forms.TextInput(),
	)

	position = forms.CharField(
		widget=forms.TextInput(),
		required=False,
	)


class RejectApplicantForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)

	reason_for_rejection = forms.CharField(
		widget=forms.Textarea()
	)


class SendContractApplicantForm(forms.Form):
	obj_id = forms.CharField()
	position_user = forms.CharField()
	status = forms.CharField()

	contract = forms.FileField(
		required=False,
		validators=[FileExtensionValidator(['pdf','doc','docx'])]
	)
	reason_rejection = forms.CharField(
		required=False,
		widget=forms.Textarea()
	)



class ContractApplicantForm(forms.Form):
	obj_id = forms.CharField()
	position_user = forms.CharField()
	status = forms.CharField()

	contract = forms.FileField(
		validators=[FileExtensionValidator(['pdf','doc','docx'])]
	)

class SeeReportForm(forms.Form):
	status = forms.CharField(
		required=False,
	)
	

	
class ChangeStatusForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
	comment = forms.CharField(
		required=False,
	)