from pyexpat import model
from django import forms
from .models import Tag, TemplateEmail,SendEmailProject

class EmailForm(forms.Form):
	text = forms.CharField(
		widget=forms.Textarea(
			)
	)
	categories = forms.CharField(
		widget=forms.Textarea(
			attrs={"id": "text-email"}
			)
	)
	
	subject = forms.CharField(widget=forms.TextInput())

class SendTemplateEmailStart(forms.Form):
	title = forms.CharField(
		widget=forms.TextInput(
			)
	)
	description = forms.CharField(
		widget=forms.Textarea(
            attrs = {'class':'ckeditor'}
			)
	)


class CreateTemplate(forms.ModelForm):
	class Meta:
		model = TemplateEmail
		fields = ['description', 'title', 'img', 'template', 'categories']

class CreateForm(forms.Form):

	description = forms.CharField(
		widget=forms.TextInput()
	)
	title = forms.CharField(
		widget=forms.TextInput()
	)

	img = forms.ImageField(
	)
	template = forms.FileField(
	)

	categories = forms.CharField(
	)

class DeleteForm(forms.Form):

	id_template = forms.IntegerField(
	)

class EditTemplateForm(forms.Form):
	id_template = forms.IntegerField(
	)
	description = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)
	title = forms.CharField(
		required=False,
		widget=forms.TextInput()
	)

	img = forms.ImageField(
		required=False,
	)
	template = forms.FileField(
		required=False,
	)

	categories = forms.CharField(
		required=False,
	)

class EditTemplateCategoryForm(forms.Form):
	
	status = forms.BooleanField()
	
	title = forms.CharField(
		widget=forms.TextInput()
	)


class EmailRasouliForm(forms.Form):
	
	description = forms.CharField(
		widget=forms.Textarea()
	)

	subject = forms.CharField(
		widget=forms.TextInput()
	)




class EmailProject(forms.Form):
	title = forms.CharField(
		widget=forms.TextInput()
	)
	projectlink = forms.CharField(
		widget=forms.TextInput()
	)
	description = forms.CharField(
		widget=forms.Textarea(
		    attrs = {'class':'ckeditor'}
		    )
	)
	img = forms.ImageField(
		required=False
	)
	class Meta:
		model=SendEmailProject
		fields=['title','projectlink','description','img']


class CreateEmailForm(forms.Form):
	company_agent_first_name = forms.CharField(
		widget=forms.TextInput()
	
	)

	company_agent_surname = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_position = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_academic_degree = forms.CharField(
		widget=forms.TextInput()
	
	)

	gender = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_email_address = forms.CharField(
		widget=forms.TextInput(
			attrs={'id':'check_email'})	
	)

	tags = forms.CharField(
		widget=forms.TextInput(
			attrs={'id':'edit_Tag '})	
	)



class UpdateEmailForm(forms.Form):
	email_id = forms.IntegerField()

	company_first_name = forms.CharField(
		widget=forms.TextInput()
	
	)

	company_agent_surname = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_position = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_academic_degree = forms.CharField(
		widget=forms.TextInput()
	
	)

	gender = forms.CharField(
		widget=forms.TextInput()
		
	)

	agent_email_address = forms.CharField(
		widget=forms.TextInput()
		
	)

	tags = forms.CharField(
		widget=forms.TextInput(
			attrs={'id':'edit_Tag '})
		
	)


	


class CreateCompanyForm(forms.Form):
	company_name = forms.CharField(
		widget=forms.TextInput()
	)
	
	state = forms.CharField(
		widget=forms.TextInput()
	)
	
	city = forms.CharField(
		widget=forms.TextInput()
	)
	
	street_number = forms.CharField(
		widget=forms.TextInput()
	)
	
	building_number = forms.CharField(
		widget=forms.TextInput()
	)
	
	unit = forms.CharField(
		widget=forms.TextInput()
	)
	
	zip_code = forms.CharField(
		widget=forms.TextInput()
	)
	
	size = forms.CharField(
		widget=forms.TextInput()
	)
	
	company_website_link = forms.CharField(
		widget=forms.TextInput()
	)
	country = forms.CharField(
		widget=forms.TextInput()
	)



class DeleteCompanyForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
class DeleteEmailForm(forms.Form):
	status = forms.CharField(
		widget=forms.TextInput()
	)
	email_id = forms.IntegerField()



	