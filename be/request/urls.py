from django.urls import path
from . import views


app_name = "request"
urlpatterns = [
    path('', views.request, name='request'),
    # badge
    path('badge/', views.the_badge_request, name='badge-request'),
    path('badge_detail/<int:pk>', views.badge_request_detail, name='badge-request-detail'),
    # supervisor
    path('supervisor/', views.supervisor_request, name='supervisor-request'),
    path('supervisor_detail/<int:pk>', views.supervisor_request_detail, name='supervisor-request-detail'),

    path('supervisor/reject', views.reject_supervisor, name='supervisor-reject'),
    path('supervisor/revise', views.revise_supervisor, name='supervisor-revise'),

    # workshop
    path('workshop/', views.workshop_request, name='workshop-request'),

    path('workshop/reject', views.reject_workshop, name='workshop-reject'),
    path('workshop/revise', views.revise_workshop, name='workshop-revise'),
    
    path('workshop_detail/<int:pk>', views.workshop_request_detail, name='workshop-request-detail'),
    # path('workshop/delete/<int:pk>', views.workshop_delete, name='workshop-delete'),
    path('workshop/update/<int:pk>', views.workshop_update, name='workshop-update'),

    # expert
    path('expert/', views.expert, name='expert'),
    # expert badge
    path('expert/reject-badge', views.reject_badge, name='expert-reject-badge'),
    path('expert/select_interviewer_or_reviewer/<int:pk>', views.select_interviewer_or_reviewer, name='select-interviewer-or-reviewer'),
    # expert supervisor
    path('expert/select_reviewer/<int:pk>', views.select_reviewer_supervisor, name='select-reviewer-supervisor'),
    # expert workshop
    path('expert/review_workshop/<int:pk>', views.workshop_expert_detail, name='expert-workshop-detail'),
    path('expert/workshop/accept/<int:pk>', views.workshop_accept, name='workshop-accept'),
    path('expert/workshop/reject/<int:pk>', views.workshop_reject, name='workshop-reject'),
    
    path('reviewer_interview/request/<int:pk>', views.reviewer_supervisor_a_or_r, name='reviewer_interview-request-supervisor'),
    path('reviewer_interview/request/workshop/<int:pk>', views.reviewer_workshop_a_or_r, name='reviewer_interview-request-workshop'),
    path('reviewer/supervisor/accept/<int:pk>', views.reviewer_supervisor_accept, name='reviewer-supervisor-accept'),
    path('reviewer/workshop/accept/<int:pk>', views.reviewer_workshop_accept, name='reviewer-workshop-accept'),
    path('reviewer/supervisor/evaluate/<int:pk>', views.reviewer_supervisor_evaluate, name='reviewer-supervisor-evaluate'),
    path('reviewer/workshop/evaluate/<int:pk>', views.reviewer_workshop_evaluate, name='reviewer-workshop-evaluate'),
    #
    path('expert/accept_request/<int:pk>/<str:form_type>', views.accept_request, name='expert-accept-request'),
    path('expert/send-to-manager/<int:pk>', views.send_request_badge_to_manager, name='expert-badge-send-to-manager'),
    path('manager/revise-badge/<int:pk>', views.badge_revise_request, name='manager-revise-badge'),
    path('expert/send_request_to/manager/<int:pk>', views.expert_send_request_to_manager, name='expert-send-request-to-manager'),
    path('expert/send_request_workshop_to/manager/<int:pk>', views.expert_send_request_workshop_to_manager, name='expert-send-request-workshop-to-manager'),
    
    
    path('reviewer_interview/', views.review_interview_page, name='review-interview'),
    path('reviewer_interview/approve_decline/<int:pk>/<str:form_type>', views.interview_review_approve_decline, name='approve-or-decline'),
    path('reviewer_interview/add_score_to_request/<int:pk>/<str:form_type>', views.add_score_to_request, name='add-score-to-request'),
    path('reviewer_interview/set_interview_session/<int:req_id>', views.set_interview_session, name='interview-session'),
    path('reviewer_interview/add_score_detail/<int:pk>/<str:form_type>', views.add_score_detail, name="add-score-detail"),
    
    # request manager
    path('manager/', views.request_manager, name="manager-list"),
    path('manager/detail-supervisor/<int:pk>', views.manager_detail_supervisor, name="manager-detail-supervisor"),
    path('manager/detail-workshop/<int:pk>', views.manager_detail_workshop, name="manager-detail-workshop"),
    path('manager/change_expert/supervisor/<int:pk>', views.manager_supervusor_change_expert, name="manager-change-expert-supervisor"),
    path('manager/change_expert/workshop/<int:pk>', views.manager_workshop_change_expert, name="manager-change-expert-workshop"),
    path('manager/change_expert/<int:pk>', views.manager_change_expert, name="manager-change-expert")
]