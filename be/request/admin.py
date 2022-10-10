from django.contrib import admin
from .models import *
# Register your models here.

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('user','skills','status', 'position', 'created')
    list_filter = ('created','status')
    search_fields = ('skills','user')

admin.site.register(BadgeRequest, BadgeAdmin)

class SupervisorAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'status', 'created')
    list_filter = ('created','status')
    search_fields = ('user',)

admin.site.register(SupervisorRequest, SupervisorAdmin)

class WorkshopAdmin(admin.ModelAdmin):
    list_display = ('user', 'expert', 'status', 'created')
    list_filter = ('created','status')
    search_fields = ('user',)

admin.site.register(WorkshopRequest, WorkshopAdmin)

class WorkshopReviewerAdmin(admin.ModelAdmin):
    list_display = ('user','status', )
    list_filter = ('status',)
    search_fields = ('user',)

admin.site.register(WorkshopReview, WorkshopReviewerAdmin)


admin.site.register(SupervisorReview)
admin.site.register(BadgeInterviewReview)
admin.site.register(BadgeExpert)
admin.site.register(InterviewSession)