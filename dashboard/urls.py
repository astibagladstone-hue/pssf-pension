from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('executive/', views.executive_dashboard, name='executive'),
    path('enrollment/', views.enrollment_dashboard, name='enrollment'),
    path('members/', views.members_dashboard, name='members'),
    path('members/export/', views.members_export, name='members_export'),
    path('contributions/', views.contributions_dashboard, name='contributions'),
    path('contributions/export/', views.contributions_export, name='contributions_export'),
    path('interest/', views.interest_dashboard, name='interest'),
    path('withdrawals/', views.withdrawals_dashboard, name='withdrawals'),
    path('claims/', views.claims_dashboard, name='claims'),
    path('trust-fund/', views.trust_fund_dashboard, name='trust_fund'),
    path('income-drawdown/', views.income_drawdown_dashboard, name='income_drawdown'),
    path('pensioners-payroll/', views.pensioners_payroll_dashboard, name='pensioners_payroll'),
    path('crm/', views.crm_dashboard, name='crm'),
    path('api/contributions/monthly/', views.api_contributions_monthly, name='api_contributions_monthly'),
    path('api/members/status/', views.api_members_status, name='api_members_status'),
    path('api/claims/status/', views.api_claims_status, name='api_claims_status'),
    path('api/trust-fund/trend/', views.api_trust_fund_trend, name='api_trust_fund_trend'),
    path('api/withdrawals/monthly/', views.api_withdrawals_monthly, name='api_withdrawals_monthly'),
    path('api/payroll/monthly/', views.api_payroll_monthly, name='api_payroll_monthly'),
]

# V8 Production Operations
urlpatterns += [
    path('operations/claims/', views.claims_approval, name='claims_approval'),
    path('operations/withdrawals/', views.withdrawals_approval, name='withdrawals_approval'),
    path('operations/payments/', views.payment_processing, name='payment_processing'),
    path('reports/', views.reporting_centre, name='reporting_centre'),
    path('member/statement/', views.member_statement, name='member_statement'),
    path('audit/', views.audit_history, name='audit_history'),
]
