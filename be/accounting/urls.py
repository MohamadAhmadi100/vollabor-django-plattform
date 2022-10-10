from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required


app_name = 'accounting'

urlpatterns = [
    # create pdf screenshot
    path('createpdf/<int:pk>',views.GeneratePdf.as_view() ,name='create-pdf'),
    # path('screenshot/',views.screenshot ,name='screenshot'),


    path('',views.accounting_dashboard ,name='accounting'),
    
    # Discounting
    path('create/discount',views.create_discount ,name='create-discount'),
    path('list/discount',views.list_discount ,name='list-discount'),
    path('check/discount',views.check_discount ,name='check-discount'),

    # Invoice
    path('invoice/<int:pk>',views.invoice_detail ,name='invoice-detail'),
    path('invoice/remove/<int:pk>',views.remove_invoice ,name='remove-invoice'),
    path('invoice/pay/<int:pk>',views.invoice_pay ,name='invoice-pay'),

    # Reporting
    path('reporting/balance',views.reporting_balance ,name='reporting-balance'),
    path('reporting/zarinpal',views.reporting_zarinpal ,name='reporting-zarinpal'),
    path('reporting/strip',views.reporting_strip ,name='reporting-strip'),
    path('reporting/paypal',views.reporting_paypal ,name='reporting-paypal'),
    path('reporting/exel',views.create_exel ,name='reporting-exel'),

    # Membership
    path('membership/create',views.create_membership ,name='create-membership'),
    path('membership/edit/<int:pk>',views.edit_membership ,name='edit-membership'),
    path('list/membership',views.list_membership ,name='list-membership'),

    #Financial & requests money
    path('bank-info',login_required(views.CompleteBankInfoView.as_view()),name="bank-info"),
    path('bank-info-submited',views.IR_bank_info_submited.as_view(),name="IR-bank-info-submited"),
    path('request-money',login_required(views.request_money.as_view()),name="request-money"),
    path('submit-request',views.submit_request,name="submit-request"),
    path('financial',views.financial_page,name="financial"),
    path('request-list',login_required(views.RequestListView.as_view()),name="request-list"),

    path('agency-list',login_required(views.AgencyListview.as_view()),name="agency-list"),
    path('agency-create',login_required(views.AgencyCreateView.as_view()),name="agency-create"),
    path('agency-edit/<int:pk>',login_required(views.AgencyEditView.as_view()),name="agency-edit"),
    path('agency-manage',login_required(views.AgencyManageView.as_view()),name="agency-manage"),

    # Ajax url
    path('generation',views.generate_code ,name='generate-code'),
    path('membershipcheck',views.membership_check ,name='membershipcheck'),
]