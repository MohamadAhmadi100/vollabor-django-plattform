from django.contrib import admin
from .models import *

# Register your models here.

app_list=[
    MainField,SubField,VirtualEvent,Seminar,Course,Workshop,Timetable,VirtualEventTracking,VirtualEventMemebers,EditRequest,
    EditTimetableRequest
]
admin.site.register(app_list)