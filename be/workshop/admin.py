from django.contrib import admin
from workshop.models import Workshop, Comment, Users_Workshops, AcceptReject, Role, Guarante, SubField, MainField, TimeTable,Workshop_log
admin.site.register(Guarante)
# Register your models here.
admin.site.register(Workshop)
admin.site.register(Comment)
admin.site.register(Users_Workshops)
admin.site.register(AcceptReject)
admin.site.register(Role)
# admin.site.register(Member)
admin.site.register(MainField)
admin.site.register(SubField)
admin.site.register(TimeTable)
admin.site.register(Workshop_log)