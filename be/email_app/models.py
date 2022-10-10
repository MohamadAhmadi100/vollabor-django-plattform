from django.core.files.storage import FileSystemStorage
from django.db import models
import os
from django.contrib.auth.models import User
# from django_mysql.models import ListCharField


sex_choices = {
	('Male', 'Male'),
	('Female', 'Female'),
}


STATUS_CHOICES = (
	('visible', 'Visible'),
	('deleted', 'Deleted'),
)

#Managers
class CompanyManager(models.Manager):
	def Active(self):
		return self.filter(status='visible')

class CategoryTemplateManager(models.Manager):
	def Active(self):
		primary_category = CategoryTemplate.objects.get(slug='primary')
		return self.filter(slug!='primary')

class EmailManager(models.Manager):
	def Published(self):
		return self.filter(status='visible')


# Create your models here.

class AdRole(models.Model):
	user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

	create_company = models.BooleanField(default=False, blank=True, verbose_name="Create company")
	edit_delete_company = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete compnay")
	
	create_category = models.BooleanField(default=False, blank=True, verbose_name="Create category")
	
	create_email = models.BooleanField(default=False, blank=True, verbose_name="Create email")
	edit_delete_email = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete email")
	
	create_template = models.BooleanField(default=False, blank=True, verbose_name="Create template")
	edit_delete_template = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete template")
	
	create_template_category = models.BooleanField(default=False, blank=True, verbose_name="Create category template")
	edit_delete_template_category = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete category template")
	
	send_email = models.BooleanField(default=False, blank=True, verbose_name="Send email")
	send_email_template = models.BooleanField(default=False, blank=True, verbose_name="Send email template")
	
	upload_image = models.BooleanField(default=False, blank=True, verbose_name="Upload image")
	research_workshop_projects = models.BooleanField(default=False, blank=True, verbose_name="Research & Workshop projects")
	
	create_institute = models.BooleanField(default=False, blank=True, verbose_name="Create institute")
	edit_delete_institute = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete institute")
	create_email_institute = models.BooleanField(default=False, blank=True, verbose_name="Create email institute")
	edit_delete_email_institute = models.BooleanField(default=False, blank=True, verbose_name="Edit, delete email institute")


	Director = models.BooleanField(default=False, blank=True, verbose_name="aprrove departments")

	is_staff = models.BooleanField(default=False, blank=True, verbose_name="Is staff")
	
	created = models.DateTimeField(auto_now_add=True)
	

class Country(models.Model):
	title = models.CharField(max_length=200)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.title


class Institute(models.Model):
	institute_name = models.CharField(max_length=200)
	country = models.ForeignKey(Country, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name = 'country_institute')
	location = models.CharField(max_length=200)
	web_address = models.CharField(max_length=200)
	last_editor = models.TextField(null=True, default=',')
	deletor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'deletor_institute')
	creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'creator_institute')

	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)
	created = models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return self.institute_name


class EmailsInstitute(models.Model):
	full_name  = models.CharField(max_length=200, null=True)
	position = models.CharField(max_length=200, null=True)
	degree = models.CharField(max_length=200, null=True)
	gender = models.CharField(max_length=6, choices=sex_choices, null=True, verbose_name='Gender')
	email_address = models.EmailField(max_length=200, null=True)
	laboratory_website = models.CharField(max_length=200, null=True)
	google_scholar = models.CharField(max_length=200, null=True)
	department = models.CharField(max_length=200, null=True)

	last_editor = models.TextField(null=True, blank=True, default=',')
	deletor = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'deletor_email_institute')
	creator = models.ForeignKey(User,  null=True, on_delete=models.SET_NULL, related_name = 'creator_email_institute')

	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)
	institute = models.ForeignKey(Institute, blank=True, default=None, null=True, on_delete=models.CASCADE, related_name = 'emails_institute')
	created = models.DateTimeField(auto_now_add=True)
	linkdin=models.CharField(max_length=200,null=True)
	linkdin_nick=models.CharField(max_length=200,null=True)
	tags=models.TextField(max_length=1000,null=True)

	def __str__(self):
		return self.email_address
	objects = EmailManager()

class Company(models.Model):
	company_name = models.CharField(max_length=200)
	country = models.ForeignKey(Country, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name = 'country_compony')
	state = models.CharField(max_length=200)
	city = models.CharField(max_length=200)
	street_number = models.CharField(max_length=200)
	building_number  = models.CharField(max_length=200)
	unit = models.CharField(max_length=200)
	zip_code = models.CharField(max_length=200)
	size = models.CharField(max_length=200)
	company_website_link  = models.CharField(max_length=200)
	outsource = models.TextField(null=True)
	services = models.TextField(null=True)
	products = models.TextField(null=True)
	current_need = models.TextField(null=True)
	future_need = models.TextField(null=True)
	last_editor = models.TextField(null=True, default=',')
	deleted_user = models.CharField(max_length=200, null=True)
	creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'creator_company')

	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)
	created = models.DateTimeField(auto_now_add=True, null=True)


	def __str__(self):
		return self.company_name

	objects = CompanyManager()


class Category(models.Model):
	title = models.CharField(max_length=200)
	company = models.ForeignKey(Company, default=None, blank=True, null=True, on_delete=models.SET_NULL, related_name = 'category_compony')
	created = models.DateTimeField(auto_now_add=True)
	def __str__(self):
		return self.title


# class InstituteFieldName(models.Model):
# 	title = models.CharField(max_length=200)
# 	position = models.CharField(max_length=200)
# 	institute = models.ForeignKey(Institute, default=None, on_delete=models.CASCADE, related_name = 'findname_nstitute')
# 	def __str__(self):
# 		return self.title

class CompanySocialMedia(models.Model):
	title = models.CharField(max_length=200)
	link = models.CharField(max_length=200)
	company = models.ForeignKey(Company, default=None, on_delete=models.CASCADE, related_name = 'CompanySocialMedia_compony')

class Emails(models.Model):
	company_agent_first_name  = models.CharField(max_length=200, null=True)
	company_agent_surname = models.CharField(max_length=200, null=True)
	agent_position = models.CharField(max_length=200, null=True)
	agent_academic_degree = models.CharField(max_length=200, null=True)
	gender = models.CharField(max_length=6, choices=sex_choices, null=True, verbose_name='Gender')
	agent_email_address = models.EmailField(max_length=200, null=True)
	last_editor = models.TextField(null=True, blank=True, default=',')
	deleted_user = models.CharField(max_length=200, blank=True, null=True)
	creator = models.ForeignKey(User,  null=True, on_delete=models.SET_NULL, related_name = 'creator_email')

	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)
	company = models.ForeignKey(Company, blank=True, default=None, null=True, on_delete=models.CASCADE, related_name = 'company_email')
	created = models.DateTimeField(auto_now_add=True)
	tags=models.TextField(max_length=1000,null=True)

	def __str__(self):
		return self.agent_email_address


	objects = EmailManager()


class HistorySendEmail(models.Model):
	user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='users_send')
	text = models.TextField()
	template_name = models.TextField()
	subject = models.CharField(max_length=100)
	created = models.DateTimeField(auto_now_add=True)
# 	selection_name=models.CharField(max_length=100,null=True)
 
	def __str__(self) -> str:
		return self.subject


class SendEmail(models.Model):
	email = models.CharField(max_length=100, null=True)
	sent = models.BooleanField(null=True, default=False)
	history = models.ForeignKey(HistorySendEmail, null=True, blank=True, on_delete=models.CASCADE, related_name='history_emails')

	def __str__(self):
		return self.email

class CategoryTemplate(models.Model):
	title = models.CharField(max_length=200, null=True)
	slug = models.SlugField(max_length=400, unique=True)
	created = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)

	last_editor = models.TextField(null=True, default=',')
	deletor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name = 'deletor_category_template')
	creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'creator_category_template')

	def __str__(self):
		return self.title
address = FileSystemStorage(location='email_app/templates/emails/email/')
# address = os.path.join('./email_app/templates/emails/email/')




class TemplateEmail(models.Model):
	description = models.TextField(null=True)
	title = models.CharField(max_length=200, null=True)
	img = models.ImageField(upload_to='email/template/img', null=True, blank=True)
	template = models.FileField(upload_to='email/template', null=True, blank=True)
	categories = models.ForeignKey(CategoryTemplate, default=None, on_delete=models.CASCADE, related_name = 'category_template')
	created = models.DateTimeField(auto_now_add=True)
	status = models.CharField(max_length=10, default='visible', null=True, choices=STATUS_CHOICES)
	
	last_editor = models.TextField(null=True, default=',')
	deletor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name = 'deletor_template')
	creator = models.ForeignKey(User, null=True, on_delete=models.SET_NULL, related_name = 'creator_template')

	

class UploadImg(models.Model):
	title = models.CharField(max_length=200, null=True)
	img = models.FileField(upload_to='email/img/', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True)

class SendEmailProject(models.Model):
	description = models.TextField(null=True, blank=False)
	img = models.ImageField(upload_to='email/img/', null=True, blank=True)
	projectlink=models.CharField(max_length=300,null=True)
	title=models.CharField(max_length=1000,null=True)
	created = models.DateTimeField(auto_now_add=True)

class ReminderEmails(models.Model):
	subject  = models.CharField(max_length=200, null=True)
	text = models.CharField(max_length=200, null=True)
	send_date = models.DateTimeField(null=True)
	created = models.DateTimeField(auto_now_add=True)
	emaillist=models.CharField(max_length=70000,null=True)
	user=models.ForeignKey(User,null=True,blank=True,on_delete=models.CASCADE)



class DepartmentInstitu(models.Model):
	name=models.CharField(max_length=200)
	approove=models.BooleanField(null=True, default=False)
	created=models.DateField(auto_now_add=True)
	viwed=models.BooleanField(null=True, default=False)
	user=models.ForeignKey(User,on_delete=models.CASCADE)



class Tag(models.Model):
	name=models.CharField(max_length=20)
	description=models.TextField(max_length=300)
	created=models.DateTimeField(auto_now=True)