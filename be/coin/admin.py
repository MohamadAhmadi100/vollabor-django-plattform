from django.contrib import admin
from .models import *

admin.site.register(ExperienceBadge)


@admin.register(PersonExperienceBadge)
class PersonExperienceBadgeAdmin(admin.ModelAdmin):
    list_display = ("badge", 'user', "score")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("name", 'price', "date_created", "is_verified")

    def name(self, obj):
        full_name = obj.user.first_name + ' ' + obj.user.last_name
        return full_name
