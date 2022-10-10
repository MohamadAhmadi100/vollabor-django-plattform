from django.urls import path 
from . import views

app_name = 'email'
urlpatterns = [
	path('', views.Home.as_view(), name='home'),
	path('company/<int:pk>', views.detail_company, name='detail-category'),
	path('institute/<int:pk>', views.detail_institute, name='detail-institute'),
	path('workshop/<int:pk>', views.detail_workshop, name='detail-workshop'),
	path('template/category/<slug:slug>', views.detail_template_category, name='detail-template-category'),
	path('send/template/research', views.send_research_project_template, name='send-template-project-research'),
	path('create/company', views.create_company, name='create-category'),
	path('create/category', views.CreateCategory.as_view(), name='create-category-new'),
	path('create/category/template', views.CreateCategoryTemplate.as_view(), name='create-category-template'),
	# path('create/email', create_email, name='create-email'),
	path('upload/img', views.UploadImgCreate.as_view(), name='upload-img'),

	path('select/template', views.select_template, name='selected_template'),
	path('send/template/<int:pk>', views.detail_select_template, name='detail-create-template'),

	path('create/template', views.create_template, name='create-template'),

	path('create/institute', views.create_institute, name='create-institute'),
	path('edit/institute', views.edit_institute, name='edit-institute'),
	path('create/email-institute', views.create_email_institute, name='create-email-institute'),
	path('edit/email-institute', views.edit_email_institute, name='edit-email-institute'),

	path('send/email', views.send_email, name='send-email'),
	path('send/email/template', views.send_email_template, name='send-email-template'),
	path('history', views.History.as_view(), name='history'),
	# path('delete/email/<int:pk>', DeleteEmail.as_view(), name='delete-email'),
	path('delete/projects/<int:pk>', views.DeleteProjectsEmail.as_view(), name='delete-projects-email'),
	# path('delete/category/<int:pk>', DeleteCategory.as_view(), name='delete-category'),
	path('update/email/<int:pk>', views.UpdateEmail.as_view(), name='update-email'),
	path('update/company/<int:pk>', views.UpdateCompany.as_view(), name='category-email'),
	path('research/', views.ResearchListAd.as_view(), name='research-list-ad'),
	path('workshop/', views.WorkshopListView, name='workshop-list'),
	path('research/page/<int:page>', views.ResearchListAd.as_view(), name='research-list-ad'),


# lotfi.........................
	path('send/email-test', views.send_email_test, name='send-email-test'),
	path('send/email/template-test', views.send_email_template_test, name='send-email-template-test'),
	path('send/email/show-last-history', views.show_last_history, name='show-last-history'),
	path('send/email/get-email-details', views.get_email_details, name='get-email-details'),
	path('send/email/check-email', views.check_email, name='check-email'),
	path('send/email/check-email-institute', views.check_email_institute, name='check-email-institute'),
	path('send/email/create-reminder', views.create_reminder, name='create-reminder'),
	path('send/email/email-notif', views.email_notif, name='email-notif'),
	path('send/email/create-new-department', views.create_new_department, name='create-new-department'),
	path('send/email/email-director', views.email_director, name='email-director'),
	path('send/email/update-department', views.update_department, name='update-department'),
	path('send/email/filter-company', views.ajax_filtering_email_company, name='ajax-filtering-company'),
	path('create_tags', views.create_tag, name='create-tags'),
	

]