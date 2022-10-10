from django.contrib import admin
from .models import *

admin.site.register(Project)

admin.site.register(IndustrialArea)
admin.site.register(ProjectArea)

admin.site.register(ProjectAreaOpinion)
admin.site.register(AreaReason)

admin.site.register(ProjectContract)
admin.site.register(ProjectProposal)
admin.site.register(ProjectContractReply)
admin.site.register(ProjectSupervisor)
admin.site.register(ProjectMentor)
admin.site.register(ProjectMember)
admin.site.register(ProjectLearner)
admin.site.register(ProjectNotification)
admin.site.register(Video)
admin.site.register(VideoCategory)
admin.site.register(Document)
admin.site.register(Visitor)
admin.site.register(News)
admin.site.register(NewsManager)
admin.site.register(NewsCategory)
admin.site.register(Event)
admin.site.register(SuggestionBox)