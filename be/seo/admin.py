from django.contrib import admin
from .models import *

admin.site.register(SEO)
admin.site.register(RobotsMeta)
admin.site.register(TitleAndDescription)


class UserFootprintAdmin(admin.ModelAdmin):
	list_display = ['user', 'url', 'created']
	# list_filter = ('status', )
admin.site.register(UserFootprint, UserFootprintAdmin)
