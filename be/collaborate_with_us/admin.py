from django.contrib import admin
from .models import CollaborateStaff, CollaborateStaffProject, CollaborateStaffInterest, StaffManager, ApplicationDeadline

admin.site.register(CollaborateStaff)
admin.site.register(CollaborateStaffProject)
admin.site.register(CollaborateStaffInterest)
admin.site.register(StaffManager)
admin.site.register(ApplicationDeadline)
