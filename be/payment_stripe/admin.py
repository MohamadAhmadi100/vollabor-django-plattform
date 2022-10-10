from django.contrib import admin
from .models import InternationalOrder, Payment, Dollar


# Register your models here.
admin.site.register(Payment)
@admin.register(InternationalOrder)
class CoinAdmin(admin.ModelAdmin):
    list_display = ("name", "date_created",
                    "purchased_amount", 'payment_intent', 'has_completed')

    def name(self, obj):
        if obj.user is not None:
            full_name = obj.user.first_name + ' ' + obj.user.last_name
        else:
            full_name = "Not determined!"
        return full_name


class DollarAdmin(admin.ModelAdmin):
    list_display = ['Automatically', 'price', 'last_editor', ]
admin.site.register(Dollar, DollarAdmin)