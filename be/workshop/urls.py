from django.conf.urls.i18n import urlpatterns
from django.urls import path
from workshop import views

urlpatterns = [
    path("create_workshop/",views.add_workshop, name="add-workshop-page"),
    path("list_workshop/",views.workshops_list, name="list-workshop"),
    path("add_expert/<int:pk>/", views.add_expert, name="add_expert"),
    path("list-expert/", views.list_expert, name="list-expert"),
    path("comment-expert/<int:pk>/", views.add_comment_expert, name="comment-expert"),
    path("checked-list/", views.checked_list, name="checked-list"),
    path("accept-reject/<int:pk>/", views.accept_reject, name="accept-reject"),
    
    path("expert/approve-decline/<int:pk>/", views.expert_approve_decline, name="expert-approve-decline"),
    path("expert/add_video/<int:pk>/", views.add_video_workshop, name="add-workshop-video"),

    # path('request/<int:pk>/', views.send_request, name='request'),
    # path('verify/', views.verify , name='verify'),
    
    path('show-workshops-to-users/',views.show_workshops_to_user, name="show-workshops-to-users"),
    path('is-accept/<int:pk>', views.is_workshop_accept, name="is-accept"),
    path('view-workshop/<int:pk>/',views.view_workshop, name="view-workshop"),
   
    path('register/',views.view_workshop_persian, name="view-persian"),
    path('list-for-all/',views.list_for_all, name="list-for-all"),
    path('accepted-list',views.accepted_list, name="accepted-list"),
    path('my-workshops-status/',views.my_workshops_status, name="my-workshop-status"),
    path('completing-my-workshop/', views.completing_my_workshop, name="completing-my-workshop"),
    path('add-workshop-file/<int:pk>', views.add_workshop_file, name="add-workshop-file"),
    
    path('edit_my_workshop/<int:pk>', views.edit_workshop, name="edit-my-workshop"),
    path('delete-workshop/<int:pk>',views.delete_workshop, name="delete-workshop"),
    path('add_workshop_for_user/<int:pk>', views.add_workshop_for_user, name="add-workshop-for-user"),
    path('my_workshop_signuped', views.my_workshop_signuped, name="my-workshop-signuped"),
    path('show-video/<int:pk>/<int:number>', views.show_workshop_video, name="show-workshop-video"),
    path('is-login/<int:pk>', views.is_login, name="is-login"),
    path('show-workshop-for-expert', views.show_workshops_for_expert, name="show-workshop-for-expert"),
    path('view-registrants-workshop/<int:pk>', views.view_registrants_workshop, name="view-registrants-workshop"),
    path('pay/<int:pk>', views.pay, name="pay"),

    path('done-workshops', views.done_workshops, name="done-workshops"),
    path('done-workshops-for-expert', views.done_workshops_for_expert, name="done-workshops-for-expert"),

    path('upload-video/<int:pk>', views.upload_video, name="upload-video"),
    path('guarante-request/', views.Guarante_request, name="guarante-request"),
    path("guarante-accept-reject/<int:pk>/", views.guarante_accept_reject, name="guarante-accept-reject"),
    path("guarante-pay/<int:pk>/", views.guarante_pay, name="guarante-pay"),
    path("expert/", views.view_expert_workshop, name="expert-workshop"),
    path("manager/", views.view_manager_workshop, name="manager-workshop"),
    path('ajax/load-fields/', views.load_field, name='ajax_load_fields'), # AJAX
    path("advertisement-form/pdf/", views.generate_pdf, name='generate-pdf-ad'),
    path('advertisement-form/<int:pk>/', views.show_ad_form, name='ad-form'),
    path('ajax/load-workshop/', views.workshop_main_field_filter, name='ajax_load_workshop'), # AJAX
    path('ajax/load-subfield/', views.load_subfield, name='ajax_load_subfield'), # AJAX
    
    path('create_workshop/time_table/<int:pk>', views.set_time_table, name="set-time-table"),
    path('supervisor/view_workshop/<int:pk>', views.show_supervisor_detail, name="show-supervisor-detail"),


    path('workshop_history/<int:pk>',views.workshop_history,name='workshop-history'),
    path('expert/contract-status/<int:pk>',views.view_contract_expert,name='expert-contract-status'),
    path('manager/contract-status/<int:pk>',views.view_contract_manager,name='manager-contract-status'),
    path('supervisor/contract-status/<int:pk>',views.view_contract_supervisor,name='supervisor-contract-status'),


    path('create-landingpage/<int:pk>', views.create_landingpage, name="create-landingpage"),
    path('specific/<int:pk>', views.view_landingpage, name="landingpage"),
    path('specific/delete', views.delete_landingpage, name="landingpage-delete"),
    path('specific/edit/<int:pk>', views.edit_landingpage, name="landingpage-edit"),

    path('upload/certificate/<int:pk>',views.upload_certificate, name="upload-certificate"),
    path('download/<int:pk>/', views.download_certificate, name="download-certificate"),
    
]
