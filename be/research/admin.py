from django.contrib import admin
from .models import *
from django.contrib.auth.models import User


# Register your models here.
# aran_farasi = User.objects.get(id=406)
# @admin.action(description='Mark selected stories as published')
# def make_published(modeladmin, request, queryset):
#     queryset.update(expert=aran_farasi)


class ResearchRoleAdmin(admin.ModelAdmin):
	list_filter = ('director', 'expert', 'reviewer', 'advertisement')
	list_display = ['user', 'director', 'expert', 'reviewer', 'count_evaluated_reviewer', 'count_rejected_reviewer', 'count_breach_of_promis_reviewer']
admin.site.register(ResearchRole, ResearchRoleAdmin)

class FormClintAdmin(admin.ModelAdmin):
	list_filter = ('status', )
	list_display = ['name', 'id_project', 'title', 'user', 'fund', 'created', 'status']
admin.site.register(IndustryFormClient, FormClintAdmin)

class FormExpertAdmin(admin.ModelAdmin):
	list_filter = ('status', )
	list_display = ['expert', 'formclint', 'created', 'status', ]
# 	actions = [make_published]
admin.site.register(IndustryFormExpert, FormExpertAdmin)


class FormSupervisorAdmin(admin.ModelAdmin):
	list_filter = ('status', )
	list_display = ['client_form', 'supervisor', 'created', 'status']
admin.site.register(IndustryExpertForSupervisor, FormSupervisorAdmin)

class TimeProgrammingAdmin(admin.ModelAdmin):
	list_display = ['topic', 'start_date', 'end_date', 'sub', 'status']
admin.site.register(TimeProgramming, TimeProgrammingAdmin)

class IndustryReviewerAdmin(admin.ModelAdmin):
	list_filter = ('status', )
	list_display = ['status', 'create', 'status']
admin.site.register(IndustryReviewer, IndustryReviewerAdmin)


class CommentProjectAdmin(admin.ModelAdmin):
	list_filter = ('status', )
	list_display = ['user', 'email', 'created', 'status', ]
admin.site.register(CommentProject, CommentProjectAdmin)


class AreaAdmin(admin.ModelAdmin):
	list_display = ['title', ]
admin.site.register(Area, AreaAdmin)

class ResearchMeetingAdmin(admin.ModelAdmin):
	list_display = ['link_meeting', 'time_meeting', 'created', ]
admin.site.register(ResearchMeeting, ResearchMeetingAdmin)



class SuperVizorAdmin(admin.TabularInline):
	model = SuperVizor

class MentorAdmin(admin.TabularInline):
	model = Mentor

class MemberAdmin(admin.TabularInline):
	model = Member

class LernerAdmin(admin.TabularInline):
	model = Lerner

class ResearchProjectAdmin(admin.ModelAdmin):
	list_display = ['project', 'proposal_supervisor', 'main_supervisor', 'status', 'status_value', 'created', ]
	list_filter = ('status', 'status_value')
	# inlines = [
	# 	SuperVizorAdmin,
	# 	MentorAdmin,
	# 	MemberAdmin,
	# 	LernerAdmin
	# 	]

	
admin.site.register(ResearchProject, ResearchProjectAdmin)



class RequestUserForProjectAdmin(admin.ModelAdmin):
	list_filter = ('supervisor', 'mentor', 'member', 'learner', 'status')
	list_display = ['project_request', 'user', 'supervisor', 'mentor', 'member', 'learner', 'status']
admin.site.register(RequestUserForProject, RequestUserForProjectAdmin)



# Tracing project
class TracingAdmin(admin.ModelAdmin):
	list_filter = ('position', )
	list_display = ['position', 'user', 'status', 'event_date']
admin.site.register(Tracing, TracingAdmin)

# Comment
class ApplicantCommentAdmin(admin.ModelAdmin):
	list_display = ['sender', 'recipient', 'position', 'project', 'seen', 'created']
admin.site.register(ApplicantComment, ApplicantCommentAdmin)

# Comment reply
class ApplicantReplyCommentAdmin(admin.ModelAdmin):
	list_display = ['replycomment', 'position', 'comment', 'seen', 'created']
admin.site.register(ApplicantReplyComment, ApplicantReplyCommentAdmin)



admin.site.register(ReportApplicant)


class SuperVizorAdmin(admin.ModelAdmin):
	list_display = ['user', 'research', 'status', 'status_remove', 	'created']
admin.site.register(SuperVizor, SuperVizorAdmin)

class MentorAdmin(admin.ModelAdmin):
	list_display = ['user', 'research', 'status', 'status_remove', 	'created']
admin.site.register(Mentor, MentorAdmin)

class MemberAdmin(admin.ModelAdmin):
	list_display = ['user', 'research', 'status', 'status_remove', 	'created']
admin.site.register(Member, MemberAdmin)

class LernerAdmin(admin.ModelAdmin):
	list_display = ['user', 'research', 'status', 'status_remove', 	'created']
admin.site.register(Lerner, LernerAdmin)
