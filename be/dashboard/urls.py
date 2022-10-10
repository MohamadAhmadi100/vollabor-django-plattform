from django.urls import path, include
from . import views

urlpatterns = [
    path("", views.dashboard, name='dashboard-page'),

    path("technical-manager/", views.technical_manager, name='technical-manager-page'),
    path("research-director/", views.research_director_panel, name='research-director-panel'),

    path("corresponding-expert/", views.corresponding_expert_panel, name='corresponding-expert-page'),
    path("research-expert/", views.research_expert_panel, name='research-expert-panel'),
    path("recently-added-expertises/", views.recently_added_expertises, name='recently-added-expertises'),
    
    path('ajax/project_filter/dashboard', views.project_filter, name='ajax_project_filter_dashboard'), # AJAX
    path("projects/research", views.dashboard_projects, name='dashboard-projects-page'),
    
    
    path("myprojects/research", views.DashboardMyProjectResearch.as_view(), name='dashboard-myprojects-reserach'),
    path("myprojects/research/client/<int:pk>", views.myproject_detail_client, name='myprojects-research-detail-client'),
    # path("myprojects/research/client/<int:pk>", views.MyprojecDetailClient.as_view(), name='myprojects-research-detail-client'),
    path("myprojects/research/expert/<int:pk>", views.myprojec_detail_expert, name='myprojects-research-detail-expert'),
    path("myprojects/research/supervisor/<int:pk>", views.MyprojecDetailSupervisor.as_view(), name='myprojects-research-detail-supervisor'),
    path("myprojects/research/project/<int:pk>", views.MyprojecDetailProjectResearch.as_view(), name='myprojects-research-detail-project'),
    
    path("contract/", views.myproject_contract_list, name='myprojects-contract-list'),
    
    path("myprojects/research/mainsupervisor/<int:pk>", views.myproject_mainsupervisor_detail, name='myprojects-research-mainsupervisor'),
    path("myprojects/research/request/project/<int:pk>", views.myproject_request_project_detail, name='myprojects-research-request-project'),
    path("myprojects/research/applicant/advisor/<int:pk>", views.myproject_applicant_advisor, name='myprojects-research-applicant-supervisor'),
    path("myprojects/research/applicant/mentor/<int:pk>", views.myproject_applicant_mentor, name='myprojects-research-applicant-mentor'),
    path("myprojects/research/applicant/member/<int:pk>", views.myproject_applicant_member, name='myprojects-research-applicant-member'),
    path("myprojects/research/applicant/learner/<int:pk>", views.myproject_applicant_learner, name='myprojects-research-applicant-learner'),
    
    path("project-view/<int:project_primary_key>", views.project_view, name='dashboard-project-view-page'),
    path("manage/<int:project_primary_key>", views.project_management, name='dashboard-project-manage-page'),
    path("edit_project/<int:project_pk>/", views.edit_project, name='dashboard-edit-project-page'),
    path("project/detail/<int:pk>", views.project_detail, name='project-detail-research'),

    path("edit_meeting/<int:project_pk>/", views.dashboard_edit_meeting, name='edit-meeting'),
    path("weekly-meeting-attendees/<int:project_pk>/", views.weekly_meeting_page, name='weekly-meeting-attendees-page'),
    path("define-projects", views.define_project, name='define-projects-page'),
    path("project-proposal/<int:project_pk>", views.proposal_page, name='project-proposal-page'),

    path("requests/", views.dashboard_request, name='dashboard-requests-page'),
    path("request-with-contracts/<str:project_type>", views.dashboard_request_with_contract,
         name='requests-with-contracts-page'),

    path("new-industrial/", views.new_industrial_areas, name='new-industrial-areas'),
    path("review/", views.review, name='review-page'),
    path("review-in-detail/<int:proposal_pk>/<int:reviewer_pk>", views.review_in_detail, name='review-in-detail-page'),

    path("members/", views.dashboard_members, name='dashboard-members-page'),
    path("profile/<int:user_id>/", views.dashboard_profile, name='dashboard-profile-page'),

    path("project-contract/<int:project_pk>/<str:contract_type>", views.project_contract, name='project-contract-page'),
    path("contract-list/", views.contract_list, name='contract-list-page'),
    path('dollar/change-status/', views.change_status_dollar, name='change-status-dollar'),

    path("question-and-answer/", views.question_and_answer_panel, name='question-and-answer-page'),
    path('unsubscribe/<int:project_pk>', views.unsubscribe, name='unsubscribe'),
    path('task-tracker/', include('task_tracker.urls'), name='task-tracker-app'),
    path("announcements/", views.announcement, name='dashboard-announcement-page'),
    path("notifications/", views.notification_page, name='notification-page'),

    path('interviewer/', views.interviewer_panel, name='interviewer-panel'),
    path('change-experience-badges/<int:user_pk>/', views.change_experience_badges, name='change-experience-badges'),
    path('research/comment-management/', views.research_comment_management, name='research-comment-management'),
    
    path('forum/', views.forum_list, name='forum'),
    # path('forum/page/<int:page>/', views.forum_list, name='forum'),
    path('news/', views.admin_news, name='news-view'),
    path('news/update/<int:pk>', views.news_update, name='news-update'),
    path('news/create/', views.create_news, name='news-create'),
    path('news/delete/<int:pk>', views.delete_news, name='news-delete'),
    path('news/preview/<int:pk>', views.news_preview, name='news-preview'),
    path('news/category/create/', views.create_category, name='category-create'),
    path('event/', views.admin_event, name='event-view'),
    path('event/create/', views.create_event, name='event-create'),
    path('event/update/<int:pk>', views.event_update, name='event-update'),
    path('event/delete/<int:pk>', views.delete_event, name='event-delete'),
    path('event/preview/<int:pk>', views.event_preview, name='event-preview'),
]
