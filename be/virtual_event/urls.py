from django.urls import path
from . import views 
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('create',login_required(views.CreateVirtualEventView.as_view()),name='create-virtualevents'),
    path('edit/<int:pk>',views.ModifyVirtualEventView.as_view(),name='edit-virtualevents'),
    path('accept-contract/<int:pk>',login_required(views.ContractAccept.as_view()),name='accept-contract'),
    #presenter
    path('presenter',login_required(views.PresenterView.as_view()),name='presenter'),
    path('presenter/detail/<int:pk>',login_required(views.VirtualEventDetailePersenterView.as_view()),name='presenter-detail'),
    path('presenter/upload/',login_required(views.UploadFileView.as_view()),name='presenter-upload'),
    #expert
    path('expert',login_required(views.ExpertView.as_view()),name='expert'),
    path('expert/detail/<int:pk>',login_required(views.VirtualEventDetaileExpertView.as_view()),name='expert-detail'),
    #director
    path('director',login_required(views.DirectorView.as_view()),name='director'),
    path('director/detail/<int:pk>',login_required(views.VirtualEventDetaileDirectorView.as_view()),name='director-detail'),

    #change status virtual event
    path('change_status',views.ChangeStatusVirtualEvent ,name='change-status'),
    path('change_expert',login_required(views.ChangeExpetview.as_view()) ,name='change_expert'),

    #shows and registrant
    path('show/<int:pk>',views.ShowVirtualEventView.as_view() ,name='show-virtual_event'),
    path('virtual_event-list/',views.VirtualEventListView.as_view() ,name='virtual_event-list'),
    path('registrant/<int:pk>',login_required(views.Registrant.as_view()) ,name='registrant'),
    path('show-to-users/',login_required(views.VirtualEventShowToUsersView.as_view()) ,name='show-virtualevents-to-users'),
    path('buy/<int:pk>',views.BuyVirtuaEventView ,name='virtualevents-buy'),
    path('managerpanel',views.ManagerPanelView.as_view() ,name='managerpanel'),
    
    #Ajax
    path('ajax/load-fields/', views.load_field, name='virtual_event_ajax_load_fields'), 
    path('mainfield-adding',views.Mainfield_adding,name='mainfield-adding'),



    #Edit time
    path('edit-time/',login_required(views.EditTimeRequest.as_view()),name='edit-time'),
    path('decide-edit-time/',login_required(views.DecideForEditTimeView.as_view()),name='decide-edit-time'),
    #Automate emails
    path('Automatic-Emails/',views.AutomateEmails,name='Automatic-Emails'),

]


