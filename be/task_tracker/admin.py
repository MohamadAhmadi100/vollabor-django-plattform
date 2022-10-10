from django.contrib import admin
from task_tracker.models import TaskTracker, ManagerList, AttendanceList

admin.site.register(TaskTracker)
admin.site.register(ManagerList)
admin.site.register(AttendanceList)


