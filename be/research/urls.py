from django.urls import path
from . import views
app_name = 'industry'

urlpatterns = [
	path('form/clint', views.create_form_clint, name='form-clint'),
	path('form/clint/Ajax', views.load_field, name='main-field-ajax'),
	path('contract/list', views.contract_client_list, name='contract-client-list'),
	path('director/', views.ResearchDirectorPanel.as_view(), name='industry-director'),
	path('director/evaluated', views.director_filter_evaluated, name='director-filter-evaluated'),
	path('director/resubmition', views.director_filter_resubmition, name='director-filter-resubmition'),
	path('director/contract', views.director_filter_contract, name='director-filter-contract'),

	path('view&edit/<int:pk>', views.direcotr_select_expert, name='industry-view-edit'),
	path('director/reject-project', views.direcotr_reject_project, name='director-reject-project'),

	# Management project
	path('director/management-project', views.ReseachDirectorManageProject.as_view(), name='research-director-manage-project'),
	path('director/applicant/<int:pk>', views.director_Manageproject_applicant_detail, name='director-applicant-detail'),
	path('director/applicant-remove/<int:pk>', views.director_Manageproject_applicant_remove, name='director-applicant-remove'),

	path('director/contract-detail/<int:pk>', views.contract_client_detail, name='director-contract-client-detail'),
	path('director/change-status/<int:pk>', views.director_statuschange_detail, name='research-director-change-status'),
	path('director/report/<int:pk>', views.director_project_report, name='research-director-report-detail'),
	path('director/report/time-pro/<int:pk>', views.reseach_director_WBS, name='research-director-report-time-pro'),
	path('reject/special-expert/<int:pk>', views.form_reject_special_expert, name='research-reject-special-expert'),
	path('director/list-supervisor/<int:pk>', views.DirectorListScoresAndSupervisor.as_view(), name='industry-director-supervisor-list'),
	path('director/list-resubmition/<int:pk>', views.DirectorListResubmition.as_view(), name='industry-director-resubmition-list'),
	path('director/see-score/<int:pk>', views.director_see_score, name='industry-director-see-score'),
	path('director/see-score-project/<int:pk>', views.director_see_score_project, name='director-see-score-project'),
	path('director/see/total/score<int:pk>', views.DirectorSeeTotalScore.as_view(), name='industry-director-see-total-score'),

	path('director/revise-proposal', views.revise_proposal_to_expert, name='director-revise-proposal'),
	path('director/change-permissions-expert', views.change_permissions_expert, name='change-permissions-expert'),
	path('director/change-expert', views.change_expert, name='project-change-expert'),

	path('director/history/not-created/<int:pk>', views.director_history_not_created_detail, name='project-director-history-not-created-detail'),
	path('director/history/created/<int:pk>', views.director_history_created_detail, name='project-director-history-created-detail'),
	path('director/main-supervisor/<int:pk>', views.director_detail_createproject, name='industry-director-main-supervisor'),
	path('rejects/<int:pk>', views.reject_detail, name='industry-reject-detail'),

	path('director/revise-contract', views.director_revise_contract, name='project-director-revise-contract'),
	path('expert', views.ExpertProjectList.as_view(), name='industry-expert-list'),
	path('expert/filter/resubmition/', views.expert_filter_resubmition, name='expert-filter-resubmition'),
	path('expert/filter/revise/', views.expert_filter_revise, name='expert-filter-revise'),
	path('expert/filter/contract/', views.expert_filter_contract, name='expert-filter-contract'),
	path('expert/filter/new-project', views.expert_filter_newproject, name='expert-filter-newproject'),
	path('expert/filter/evaluate', views.expert_filter_evaluate, name='expert-filter-evaluate'),
	path('revised/page', views.revise_filter_applicant, name='project-revised-page'),
	path('rejected/page', views.rejected_filter_applicant, name='project-rejected-page'),

	path('expert/send-contract-to-director', views.action_contract_client, name='send-contract-client-to-director'),
	path('expert/<int:pk>', views.expert_detail, name='industry-expert-detail'),
	path('expert/history/<int:pk>', views.expert_history_notcreated_detail, name='research-expert-history-detail'),
	path('expert/history/created/<int:pk>', views.expert_history_created_detail, name='project-expert-history-created-detail'),
	path('expert/manage/ptoject', views.ExpertManageProject.as_view(), name='research-expert-manage-project'),
	path('expert/view/table-time-programming/<int:pk>', views.expert_view_table_timeprogramming, name='industry-expert-view-timeprogramming'),
	path('expert/manage/change-status/<int:pk>', views.expert_view_change_status, name='research-manage-change-status'),

	path('expert/review/project/<int:pk>', views.expert_review_project_detail, name='research-access-expert-detail'),
	path('supervisor', views.SupervisorPanel.as_view(), name='industry-supervisor-list'),
	path('supervisor/deleted', views.delete_supervisor, name='project-supervisor-delete'),
	path('supervisor/filter', views.SupervisoeFilterNewProjectList.as_view(), name='industry-supervisor-filter-list'),
	path('supervisor/<int:pk>', views.supervisor_form_detail, name='industry-supervisor-detail'),
	path('supervisor/revise/<int:pk>', views.supervisor_detail_revise, name='industry-supervisor-revise-detail'),
	path('supervisor/resubmit/<int:pk>', views.agian_resubmit_supervisor, name='industry-supervisor-resubmit-agian'),

	path('withdraw/project', views.withdraw_project, name='project-withdraw'),

	path('expert/list-supervisor/<int:pk>', views.ExpertListSupervisor.as_view(), name='industry-expert-supervisor-list'),
	path('expert/send/reviewer/<int:form_id>', views.sepervisor_send_review, name='industry-supervisor-reviewer'),
	path('expert/list-resubmition/<int:pk>', views.ExpertListResubmition.as_view(), name='industry-expert-resubmition-list'),
	path('expert/list-not-response-proposal/<int:pk>', views.ExpertListNotResponseProposal.as_view(), name='expert-not-response-proposal-list'),
	path('expert/list-not-response-proposal/director/<int:pk>', views.ExpertListNotResponseProposalDirector.as_view(), name='expert-not-response-proposal-list-director'),
	path('expert/list-reviewer/<int:pk>', views.ExpertListReviewer.as_view(), name='industry-expert-reviewer-list'),

	path('expert/reviewer/<int:pk>', views.expert_review_detail, name='industry-expert-reviewer-detail'),
	path('expert/notresponse/proposal/<int:pk>', views.expert_notresponse_proposal_detail, name='expert-notresponse-proposal-detail'),
	path('director/notresponse/proposal/<int:pk>', views.director_notresponse_proposal_detail, name='director-notresponse-proposal-detail'),
	path('expert/send-to-reviewer', views.expert_send_reviewer, name='research-send-to reviewer'),

	path('expert/cancel/reviewer', views.cancel_request_reviewer, name='expert-cancel-reviewer'),
	path('expert/revise/reviewer', views.revise_request_reviewer, name='revise-request-reviewer'),
	path('expert/revise/proposal', views.revised_proposal, name='expert-revise-proposal'),
	path('expert/revise/list/<int:pk>', views.ExpertReviseList.as_view(), name='expert-revise-list'),

	path('expert/reviewer/total/<int:pk>', views.expert_see_totoal_score, name='industry-expert-reviewer-total-detail'),
	path('expert/contract/<int:pk>', views.expert_contract_detail, name='industry-expert-contract'),
	path('expert/supervisor/<int:pk>', views.expert_supervisor_detail, name='industry-supervisor-expert-detail'),
	path('expert/chek&send/contract', views.ExpertSendOrChekContract.as_view(), name='industry-supervisor-send-or-chek-contract'),
	path('expert/list/contract/client/', views.expert_list_contract_client, name='expert-contract-list-client'),
	path('expert/special/send/reviewer/<int:form_id>', views.expert_send_to_reviewer, name='research-expert-send-reviewer'),
	path('expert/special/panel', views.SpecialExpertPanel.as_view(), name='research-access-expert-panel'),
	path('expert/special/accept-reject', views.SpecialExpertAcceptOrRejectPage.as_view(), name='research-special-expert-accept-reject'),
	path('expert/special/main/<int:pk>', views.special_expert_detail_mainsupervisor, name='research-access-expert-detail-main'),
	path('expert/special/scores/<int:pk>', views.special_expert_detail_see_review, name='research-sepcial-expert-detail-main'),
	path('supervisor/contract/<int:pk>', views.supervisor_detail_contract, name='industry-supervisor-see-contract'),

	path('supervisor/contract/total/<int:pk>', views.supervisor_detail_contract_total, name='industry-supervisor-see-contract-total'),
	path('supervisor/contract/supervisor/send/<int:pk>', views.supervisor_send_contract, name='industry-supervisor-send-contract'),
	path('supervisor/reject/project/<int:pk>', views.SupervisorDetailRejectProject.as_view(), name='industry-supervisor-reject'),
	path('supervisor/send-from/adverstiment/<int:pk>', views.send_form_adverstiment, name='industry-form-advertiment'),
	path('supervisor/time-programmin/<int:pk>', views.create_time_programming, name='industry-time-programming'),
	path('supervisor/delete/time-programmin/<int:pk>', views.deletetimeprogramming, name='industry-delete-time-programming'),
	path('supervisor/vewe/form/adverstiment/<int:pk>', views.view_adverstiment, name='industry-view-adverstiment'),
	path('supervisor/filter', views.SupervisoeFilterNewProjectList.as_view(), name='industry-supervisor-filter-list'),
	path('supervisor/reject/proposal/<int:pk>', views.reject_supervisor_reject, name='industry-supervisor-reject-proposal-detail'),
	path('supervisor/reject/proposal/<int:pk>', views.reject_supervisor_reject, name='industry-supervisor-reject-proposal-detail'),
	path('supervisor/contract', views.SupervisorContractList.as_view(), name='industry-supervisor-contract-list'),
	path('reviewer', views.reviewer_list, name='research-reviewer-list-dashboard'),
	path('reviewer/projects', views.reviewer_project_list, name='research-reviewer-list-project'),
	path('reviewer/proposal', views.reviewer_proposal_list, name='industry-reviewer-list'),
	path('reviewer/project/<int:pk>', views.reviewer_project_detail, name='research-reviewer-project-detail'),
	path('reviewer/<int:pk>', views.reviewer_detail, name='industry-reviewer-detail'),
	path('reviewer/send-score/<int:pk>', views.reviewer_send_score, name='industry-reviewer-send-score'),
	path('reviewer/send-score/project/<int:pk>', views.reviewer_send_score_project, name='research-reviewer-send-score-project'),
	path('reviewer/send-to-director', views.reviewer_send_score_director, name='research-reviewer-send-director'),
	path('reviewer/send-to-expert', views.proposal_send_score_score, name='proposal-send-expert'),

	path('project/delete/time-programmin/<int:pk>', views.delete_time_programming_project, name='research-delete-time-programming-project'),
	path('project/apply/<int:pk>', views.applyproject, name='industry-project-apply'),
	path('project/edit/request/<int:pk>', views.detail_request_project, name='industry-project-edit-request-detail'),
	
	path('project/delete/<int:pk>', views.DeleteProject.as_view(), name='industry-project-delete'),
	path('expert/detail/report/<int:pk>', views.detail_expert_report, name='research-expert-detail-report'),


	path('project/search', views.ListSreach.as_view(), name='industry-project-search'),
	path('project/view&add/time-programmin/<int:pk>', views.view_add_time_programming, name='industry-view-add-time-programming'),

	path('project/evaluation-applicant/<int:pk>', views.evaluation_applicant, name='evaluation-applicant-page'),
	path('project/applicant-information-remove/', views.applicant_information_remove, name='research-project-applicant-information-remove'),
	path('project/create-edit-metting/', views.create_edit_metting, name='project-create-edit-metting'),

	path('information-expert/', views.expert_information, name='project-information-expert'),
	path('information-expert/ajax', views.expert_information_ajax, name='project-information-expert-ajax'),
	path('upload/paper/<int:pk>', views.upload_paper, name='project-upload-paper'),

	path('applicant/list/contract', views.contract_list_applicant, name='applicant-list-contract'),
	path('report/applicant/wbs', views.report_applicant_wbs, name='project-report-applicant-wbs'),
	path('expert/manage-project/applicant/<int:pk>', views.Manageproject_applicant_detail, name='manageproject-applicant-detail'),
	path('expert/manage-project/applicant-remove/<int:pk>', views.Manageproject_applicant_detail_remove, name='manageproject-applicant-remove'),
	path('applicant-send-contarct-to-expert', views.applicant_send_contract_to_expert, name='applicant-send-contarct-to-expert'),

	path('change-status', views.change_status, name='change-status-done'),
	path('change-status-to-home', views.change_status_to_home, name='change-status-to-home'),

	path('confirm-produc/<int:pk>', views.confirm_produc, name='confirm-produc'),
	path('form-request/change/status/<int:pk>', views.form_request_status_done, name='form-request-change-status-done'),

	# path('ajax-seen-comment-expert', views.seen_expert_comments, name='ajax-seen-expert-comment'),

	# Messenger
	path('messenger/page/<int:pk>', views.messenger_page, name='messenger-page'),

	path('client/detail-revised/<int:pk>', views.detail_client_revised, name='client-detail-revised'),
    path("client/<int:pk>", views.detail_client, name='client-detail'),
    path("pay/contract/client/<int:pk>", views.pay_contract_client, name='pay-contract-client'),


    path("request/project/<int:pk>", views.request_project_detail, name='request-project-detail'),
    path("advisor/<int:pk>", views.applicant_advisor_detail, name='applicant-advisor-detail'),
    path("mentor/<int:pk>", views.applicant_mentor_detail, name='applicant-mentor-detail'),
    path("member/<int:pk>", views.applicant_member_detail, name='applicant-member-detail'),
    path("learner/<int:pk>", views.applicant_learner_detail, name='applicant-learner-detail'),

    path("main-supervisor/detail/<int:pk>", views.mainsupervisor_detail, name='mainsupervisor-detail'),

    path("send/proposal/<int:pk>", views.detail_send_proposal, name='detail-send-proposal'),

    path("selecting-supervisor/detail/<int:pk>", views.selecting_supervisor_detail, name='selecting-supervisor-detail'),
]