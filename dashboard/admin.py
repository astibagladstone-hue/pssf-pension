from django.contrib import admin
from .models import *

@admin.register(Scheme)
class SchemeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'status', 'date_established')
    list_filter = ('status',)
    search_fields = ('code', 'name', 'sponsor_name')

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('member_number', 'full_name', 'scheme', 'status', 'join_date')
    list_filter = ('status', 'scheme', 'gender')
    search_fields = ('member_number', 'first_name', 'last_name', 'national_id')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'subject', 'status', 'priority', 'assigned_to', 'is_overdue')
    list_filter = ('status', 'priority', 'is_overdue')
    search_fields = ('ticket_number', 'subject', 'description')

@admin.register(ContributionReceipt)
class ContributionReceiptAdmin(admin.ModelAdmin):
    list_display = ('receipt_no', 'receipt_type', 'receipt_date', 'receipt_amount', 'scheme', 'status')
    list_filter = ('receipt_type', 'status', 'scheme')
    search_fields = ('receipt_no', 'description')


# Pension administration modules
for model in [
    WithdrawalApplication, ClaimApplication, TrustFundAccount,
    TrustFundTransaction, IncomeDrawdownPlan, DrawdownPayment,
    PensionPayrollRun, Pensioner, MemberInterest, MemberContribution
]:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
