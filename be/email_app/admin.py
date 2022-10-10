from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Country)
admin.site.register(CompanySocialMedia)
admin.site.register(Category)
admin.site.register(Company)
admin.site.register(EmailsInstitute)
admin.site.register(Institute)
admin.site.register(Emails)
admin.site.register(HistorySendEmail)
admin.site.register(CategoryTemplate)
admin.site.register(TemplateEmail)
admin.site.register(UploadImg)
admin.site.register(SendEmailProject)
admin.site.register(Tag)

class AdRoleAdmin(admin.ModelAdmin):
# 	list_filter = ('user', 'create_company', 'edit_delete_company', 'create_category')
# 	list_display = [
# 	    'user', 'create_company', 'edit_delete_company', 'create_category', 'create_email', 'edit_delete_email', 'create_template', 'create_template_category', 'edit_delete_template', 'edit_delete_template_category', 'send_email',
# 	    'send_email_template', 'upload_image', 'research_workshop_projects']
	list_display = [
		'user', 'is_staff']
admin.site.register(AdRole, AdRoleAdmin)


class SendEmailAdmin(admin.ModelAdmin):
	list_filter = ('sent',)
	list_display = ['email', 'history', 'sent']
admin.site.register(SendEmail, SendEmailAdmin)