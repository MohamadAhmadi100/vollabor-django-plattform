from django.contrib import admin

from users.models import MemberProfile
from .models import *

admin.site.register(AdFormWS)
admin.site.register(Announcement)
admin.site.register(AnnouncementView)

admin.site.register(Notification)

admin.site.register(WeeklyMeetingTime)
admin.site.register(WeeklyMeetingAttendee)

admin.site.register(CompanyCollaboration)
admin.site.register(ProjectRating)
admin.site.register(UserEmail)

admin.site.register(ContractItem)
admin.site.register(ProjectContractItem)

admin.site.register(ExpertAreaItem)
admin.site.register(ProjectExpertAreaItem)

admin.site.register(ApplicantManager)

admin.site.register(Reviewer)
admin.site.register(ProposalOpinion)
admin.site.register(ProposalOpinionItem)


@admin.register(ProposalComment)
class ProposalCommentAdmin(admin.ModelAdmin):
    list_display = ("proposal", 'reviewer', "comment")
