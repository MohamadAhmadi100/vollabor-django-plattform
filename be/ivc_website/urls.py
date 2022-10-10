from django.urls import path
from . import views

urlpatterns = [
    path("membership/", views.membership, name='membership-page'),
    path("", views.home, name='home-page'),
    path("projects/", views.project, name='projects-page'),
    path("projects/page/<int:page>/", views.Projectlist.as_view(), name='projects-page'),
    path("project/detail/<int:pk>", views.detail_project, name='projects-page-detail'),
    path('ajax/project_filter/', views.project_filter, name='ajax_project_filter'), # AJAX
    path("videos/", views.videos_page, name='videos-page'),
    path("ajax/videos_filter/", views.video_filter, name='ajax-videos-filter'),
    path("videos/detail/<int:pk>", views.video_detail, name='video-detail'),
    path("archives/documents", views.documents_page, name='documents-page'),
    path("goals/", views.goals_page, name='goals-page'),
    path("news/", views.news, name='news-page'),
    path("news_detail/<int:pk>", views.news_detail, name='news-detail'),
    path("ajax/news_filter/", views.news_filter, name='news-filter'), #AJAX
    path("news/<slug:slug>", views.news_category, name='news-category'),
    path("about-us", views.about_us, name="about-us"),
    path("guideline", views.guideline, name="guideline"),
    path("event/", views.event, name='event-page'),
    path("event_detail/<int:pk>", views.event_detail, name='event-detail'),
    path("suggestion_box", views.suggestion_box, name="suggestion-box"),
    
    path("video/manager", views.video_manager, name='video-view'),
    path("video/manager/create", views.create_video, name='video-create'),
    path("video/manager/update/<int:pk>", views.update_video, name='video-update'),
    path("video/manager/delete/<int:pk>", views.delete_video, name='video-delete'),
    path("video/manager/category/create/", views.create_video_category, name='video-ceate-category'),
    path('membership',views.membership_front ,name='membership'),
    path('messages',views.messages_box ,name='messages'),
    path('contact-us',views.contact_us ,name='contact-us'),
]
