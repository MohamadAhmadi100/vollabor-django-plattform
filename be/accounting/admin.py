from django.contrib import admin
from .models import *


# Register your models here.
models=[CentralRequestPayment,Agency,Discount,Membership,membership_user,WithdrawalBox,User_bank_info,Request_money]


class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('user','amount','service','is_paid','pay_date','fallow_code')
    list_filter = ('service','is_paid','pay_date','fallow_code')


class ServiceAdmin(admin.ModelAdmin):
    list_display = ('user','service_name','workshop','project','badge','badgesupervisor','badgeworkshop','action')
    list_filter = ('user','service_name','workshop','project','badge','badgesupervisor','badgeworkshop','action')

admin.site.register(models)
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Service,ServiceAdmin)