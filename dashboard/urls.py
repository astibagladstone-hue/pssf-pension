from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.home, name="dashboard"),

    path("enrollment/", views.enrollment, name="enrollment"),
    path("members/", views.members, name="members"),
    path("contributions/", views.contributions, name="contributions"),
    path("interest/", views.interest, name="interest"),
    path("withdrawals/", views.withdrawals, name="withdrawals"),
    path("claims/", views.claims, name="claims"),
    path("trust-fund/", views.trust_fund, name="trust_fund"),
    path("income-drawdown/", views.income_drawdown, name="income_drawdown"),
    path("pensioners-payroll/", views.pensioners_payroll, name="pensioners_payroll"),
]