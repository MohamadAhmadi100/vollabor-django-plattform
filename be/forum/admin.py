from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(ForumRole)
admin.site.register(History)

class CategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug',  'status', 'workshop_and_research')
	search_fields = ('title',)
	prepopulated_fields = {'slug':('title',)}
admin.site.register(Category, CategoryAdmin)


class MainCategoryAdmin(admin.ModelAdmin):
	list_display = ('title', 'slug',  'status', )
	search_fields = ('title',)
	prepopulated_fields = {'slug':('title',)}
admin.site.register(MainCategory, MainCategoryAdmin)

class PostesAdmin(admin.ModelAdmin):
	list_display = ('title', 'author', 'deleted', 'created')
	search_fields = ('title', 'description')
	list_filter = ('created', )
admin.site.register(Postes, PostesAdmin)

class TopicCommentAdmin(admin.ModelAdmin):
	list_display = ('description',)
	search_fields = ('description', )
admin.site.register(TopicComment, TopicCommentAdmin)

admin.site.register(ReplyComment)


class LikeAdmin(admin.ModelAdmin):
	list_display = ('user', 'topic', 'comment', 'replycomment', 'status', 'created', )
	list_filter = ('status', )
admin.site.register(Like, LikeAdmin)

class ViewTopicAdmin(admin.ModelAdmin):
	list_display = ('user', 'topic', 'created', )
	list_filter = ('created', )
admin.site.register(ViewTopic, ViewTopicAdmin)