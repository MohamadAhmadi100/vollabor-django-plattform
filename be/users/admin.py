from django.contrib import admin
from .models import *

@admin.action(description='Remove balance amount ')
def make_published(modeladmin, request, queryset):
	updated = queryset.update(balance=0)
	if updated == 1:
		message = 'removed'
	else:
		message = 'removed'
	modeladmin.message_user(request, "{} balance {}".format(updated, message))

admin.site.register(CompanyMail)
admin.site.register(TopSupervisor)
admin.site.register(LegalProfile)
admin.site.register(Interviewer)
admin.site.register(Expert)
admin.site.register(ResearchExpert)
admin.site.register(ExpertArea)

class RoleAdmin(admin.ModelAdmin):
    list_display = ('user','position','email')
    list_filter = ('position',)
    search_fields = ('position','user')
    #ordering = ['status', 'date']

admin.site.register(Role, RoleAdmin)

@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("name", "balance", "profile_is_complete")
    search_fields = ['user__first_name', 'user__last_name']
    actions = [make_published]

    def name(self, obj):
        full_name = obj.user.first_name + ' ' + obj.user.last_name
        return full_name

    def profile_is_complete(self, obj):
        if obj.about_me is None:
            is_none = True
        else:
            is_none = False

        return is_none

    profile_is_complete.boolean = True
