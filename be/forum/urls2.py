from django.urls import path
from .views import *
app_name = 'forum'
urlpatterns = [
	path('history/', HistoryList.as_view(), name='post-history'),
	path('history/page/<int:page>/', HistoryList.as_view(), name='post-history'),

	path('topic-like/<int:pk>', like_topic, name='topic-like'),
	path('comment-dislike/<int:pk>', dislike_comment, name='comment-dislike'),

	path('topic/<int:pk>', detail_topic, name='detail-title'),
	path('', CategoryList.as_view(), name='category' ),
	path('category/page/<int:page>/', CategoryList.as_view(), name='category' ),
	path('category/<slug:slug>', CategorySubList.as_view(), name='category-detail'),
	path('category/<slug:slug>/<int:page>/', CategorySubList.as_view(), name='category-detail'),
	path('category/edit/<int:pk>', EditCategory.as_view(), name='category-edit'),
	path('category/<slug:slug>/topic/', category_topic_create, name='category-topic'),
	path('category/<slug:slug>/topic/page/<int:page>/', category_topic_create, name='category-topic'),

]