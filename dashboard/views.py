"""
PSSF Dashboard Views - Simplified version
"""
import csv
import json
from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.db.models import Count, Sum, Q, F, Value, Avg
from django.db.models.functions import TruncMonth, TruncYear, Coalesce
from django.utils import timezone
from django.core.cache import cache
from .models import *
import logging

logger = logging.getLogger(__name__)

def _months_ago(n):
    today = date.today()
    month = today.month - n
    year = today.year
    while month <= 0:
        month += 12
        year -= 1
    return date(year, month, 1)

@login_required
def home(request):
    ctx = {
        'active_members': Member.objects.filter(status='ACTIVE').count(),
        'inactive_members': Member.objects.filter(status='INACTIVE').count(),
        'open_tickets': Ticket.objects.filter(status__in=['NEW', 'OPEN', 'IN_PROGRESS']).count(),
        'overdue_tickets': Ticket.objects.filter(is_overdue=True).count(),
        'unassigned_tickets': Ticket.objects.filter(assigned_to__isnull=True).count(),
        'total_receipts': ContributionReceipt.objects.count(),
        'total_schemes': Scheme.objects.filter(status='ACTIVE').count(),
        'pending_withdrawals': WithdrawalApplication.objects.filter(status='PENDING').count(),
        'pending_claims': ClaimApplication.objects.filter(status='SUBMITTED').count(),
        'recent_receipts': ContributionReceipt.objects.order_by('-receipt_date')[:10],
    }
    return render(request, 'dashboard/home.html', ctx)

@login_required
def members_dashboard(request):
    status_filter = request.GET.get('status', '')
    scheme_filter = request.GET.get('scheme', '')
    search = request.GET.get('q', '')
    qs = Member.objects.select_related('scheme')
    if status_filter:
        qs = qs.filter(status=status_filter)
    if scheme_filter:
        qs = qs.filter(scheme_id=scheme_filter)
    if search:
        qs = qs.filter(Q(member_number__icontains=search) | Q(first_name__icontains=search) | Q(last_name__icontains=search) | Q(national_id__icontains=search))
    
    status_summary = {r['status']: r['count'] for r in Member.objects.values('status').annotate(count=Count('id'))}
    ctx = {
        'members': qs[:200],
        'total': qs.count(),
        'status_summary': status_summary,
        'status_summary_json': json.dumps(status_summary),
        'schemes': Scheme.objects.all(),
        'current_status': status_filter,
        'current_scheme': scheme_filter,
        'search': search,
    }
    return render(request, 'dashboard/members.html', ctx)

@login_required
def members_export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="members.csv"'
    writer = csv.writer(response)
    writer.writerow(['Member No', 'First Name', 'Last Name', 'DOB', 'National ID', 'Scheme', 'Join Date', 'Status', 'Employer', 'Email'])
    for m in Member.objects.select_related('scheme').iterator(chunk_size=1000):
        writer.writerow([m.member_number, m.first_name, m.last_name, m.date_of_birth, m.national_id, m.scheme.name, m.join_date, m.status, m.employer, m.email])
    return response

@login_required
def contributions_dashboard(request):
    year = int(request.GET.get('year', date.today().year))
    receipts = ContributionReceipt.objects.filter(receipt_date__year=year).order_by('-receipt_date')
    total_received = receipts.aggregate(s=Coalesce(Sum('receipt_amount'), Value(0)))['s']
    total_allocated = receipts.aggregate(s=Coalesce(Sum('allocated_amount'), Value(0)))['s']
    total_unallocated = receipts.aggregate(s=Coalesce(Sum('unallocated_amount'), Value(0)))['s']
    
    monthly = list(receipts.annotate(month=TruncMonth('receipt_date')).values('month').annotate(total=Sum('receipt_amount'), count=Count('id')).order_by('month'))
    by_type = list(receipts.values('receipt_type').annotate(total=Sum('receipt_amount'), count=Count('id')))
    
    ctx = {
        'receipts': receipts[:100],
        'total_received': total_received,
        'total_allocated': total_allocated,
        'total_unallocated': total_unallocated,
        'year': year,
        'years': range(date.today().year, date.today().year - 6, -1),
        'monthly_json': json.dumps([{'month': str(r['month'])[:7], 'total': float(r['total']), 'count': r['count']} for r in monthly], default=str),
        'by_type_json': json.dumps([{'type': r['receipt_type'], 'total': float(r['total'])} for r in by_type], default=str),
    }
    return render(request, 'dashboard/contributions.html', ctx)

@login_required
def contributions_export(request):
    year = request.GET.get('year', date.today().year)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="contributions_{year}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Receipt No', 'Type', 'Date', 'Description', 'Receipt Amount', 'Allocated', 'Unallocated'])
    for r in ContributionReceipt.objects.filter(receipt_date__year=year):
        writer.writerow([r.receipt_no, r.receipt_type, r.receipt_date, r.description, r.receipt_amount, r.allocated_amount, r.unallocated_amount])
    return response

@login_required
def interest_dashboard(request):
    year = int(request.GET.get('year', date.today().year - 1))
    records = MemberInterest.objects.filter(year=year).select_related('member')
    totals = records.aggregate(total_interest=Coalesce(Sum('interest_amount'), Value(0)), avg_rate=Avg('interest_rate'), total_closing=Coalesce(Sum('closing_balance'), Value(0)))
    top_earners = list(records.order_by('-interest_amount').values('member__member_number', 'member__first_name', 'member__last_name', 'interest_amount', 'interest_rate', 'closing_balance')[:20])
    ctx = {'year': year, 'years': range(date.today().year - 1, date.today().year - 8, -1), 'totals': totals, 'top_earners': top_earners, 'record_count': records.count()}
    return render(request, 'dashboard/interest.html', ctx)

@login_required
def withdrawals_dashboard(request):
    status_filter = request.GET.get('status', '')
    qs = WithdrawalApplication.objects.select_related('member')
    if status_filter:
        qs = qs.filter(status=status_filter)
    by_status = {r['status']: r['count'] for r in WithdrawalApplication.objects.values('status').annotate(count=Count('id'))}
    ctx = {
        'withdrawals': qs[:100],
        'by_status': by_status,
        'by_status_json': json.dumps(by_status),
        'current_status': status_filter,
        'total_pending': by_status.get('PENDING', 0),
        'total_paid': by_status.get('PAID', 0),
    }
    return render(request, 'dashboard/withdrawals.html', ctx)

@login_required
def claims_dashboard(request):
    status_filter = request.GET.get('status', '')
    qs = ClaimApplication.objects.select_related('member')
    if status_filter:
        qs = qs.filter(status=status_filter)
    by_status = {r['status']: r['count'] for r in ClaimApplication.objects.values('status').annotate(count=Count('id'))}
    totals = ClaimApplication.objects.aggregate(total_claimed=Coalesce(Sum('claimed_amount'), Value(0)), total_approved=Coalesce(Sum('approved_amount'), Value(0)), total_paid=Coalesce(Sum('paid_amount'), Value(0)))
    ctx = {'claims': qs[:100], 'by_status': by_status, 'by_status_json': json.dumps(by_status), 'totals': totals, 'current_status': status_filter}
    return render(request, 'dashboard/claims.html', ctx)

@login_required
def trust_fund_dashboard(request):
    accounts = TrustFundAccount.objects.all()
    total_fund = accounts.aggregate(s=Coalesce(Sum('current_balance'), Value(0)))['s']
    recent_transactions = TrustFundTransaction.objects.select_related('account').order_by('-transaction_date')[:50]
    ctx = {'accounts': accounts, 'total_fund': total_fund, 'recent_transactions': recent_transactions}
    return render(request, 'dashboard/trust_fund.html', ctx)

@login_required
def income_drawdown_dashboard(request):
    plans = IncomeDrawdownPlan.objects.select_related('member').all()
    active_plans = plans.filter(status='ACTIVE')
    total_fund_under_drawdown = active_plans.aggregate(s=Coalesce(Sum('fund_value'), Value(0)))['s']
    monthly_obligations = active_plans.aggregate(s=Coalesce(Sum('monthly_drawdown'), Value(0)))['s']
    recent_payments = DrawdownPayment.objects.select_related('plan__member').order_by('-payment_date')[:50]
    payment_totals = DrawdownPayment.objects.aggregate(total_gross=Coalesce(Sum('gross_amount'), Value(0)), total_tax=Coalesce(Sum('tax_withheld'), Value(0)), total_net=Coalesce(Sum('net_amount'), Value(0)))
    ctx = {'plans': plans[:100], 'active_count': active_plans.count(), 'total_fund_under_drawdown': total_fund_under_drawdown, 'monthly_obligations': monthly_obligations, 'recent_payments': recent_payments, 'payment_totals': payment_totals}
    return render(request, 'dashboard/income_drawdown.html', ctx)

@login_required
def pensioners_payroll_dashboard(request):
    runs = PensionPayrollRun.objects.order_by('-run_date')[:24]
    latest_run = runs.first()
    pensioners = Pensioner.objects.select_related('member').filter(status='ACTIVE')
    total_monthly = pensioners.aggregate(s=Coalesce(Sum('monthly_pension'), Value(0)))['s']
    ctx = {'payroll_runs': runs, 'latest_run': latest_run, 'active_pensioners': pensioners.count(), 'total_monthly': total_monthly}
    return render(request, 'dashboard/pensioners_payroll.html', ctx)

@login_required
def crm_dashboard(request):
    status_filter = request.GET.get('status', '')
    qs = Ticket.objects.all()
    if status_filter:
        qs = qs.filter(status=status_filter)
    status_counts = {r['status']: r['count'] for r in Ticket.objects.values('status').annotate(count=Count('id'))}
    unassigned_count = Ticket.objects.filter(assigned_to__isnull=True).count()
    overdue_count = Ticket.objects.filter(is_overdue=True).count()
    ctx = {'tickets': qs.order_by('-created_at')[:100], 'status_counts': status_counts, 'status_counts_json': json.dumps(status_counts), 'unassigned_count': unassigned_count, 'overdue_count': overdue_count, 'current_status': status_filter}
    return render(request, 'dashboard/crm.html', ctx)

# API Views
@login_required
def api_contributions_monthly(request):
    data = list(ContributionReceipt.objects.filter(receipt_date__gte=_months_ago(12)).annotate(month=TruncMonth('receipt_date')).values('month').annotate(total=Sum('receipt_amount'), count=Count('id')).order_by('month'))
    return JsonResponse([{'month': str(r['month'])[:7], 'total': float(r['total']), 'count': r['count']} for r in data], safe=False)

@login_required
def api_members_status(request):
    data = {r['status']: r['count'] for r in Member.objects.values('status').annotate(count=Count('id'))}
    return JsonResponse(data)

@login_required
def api_claims_status(request):
    data = {r['status']: r['count'] for r in ClaimApplication.objects.values('status').annotate(count=Count('id'))}
    return JsonResponse(data)

@login_required
def api_trust_fund_trend(request):
    data = list(TrustFundTransaction.objects.filter(transaction_date__gte=_months_ago(12)).annotate(month=TruncMonth('transaction_date')).values('month').annotate(total=Sum('amount')).order_by('month'))
    return JsonResponse([{'month': str(r['month'])[:7], 'total': float(r['total'])} for r in data], safe=False)

@login_required
def api_withdrawals_monthly(request):
    data = list(WithdrawalApplication.objects.filter(application_date__gte=_months_ago(12)).annotate(month=TruncMonth('application_date')).values('month').annotate(count=Count('id'), total=Sum('net_benefit')).order_by('month'))
    return JsonResponse([{'month': str(r['month'])[:7], 'count': r['count'], 'total': float(r['total'] or 0)} for r in data], safe=False)

@login_required
def api_payroll_monthly(request):
    data = list(PensionPayrollRun.objects.order_by('-run_date').values('run_date', 'period_month', 'period_year', 'total_pensioners', 'gross_payroll', 'net_payroll')[:12])
    return JsonResponse(data, safe=False)


@login_required
def executive_dashboard(request):
    ctx = {
        'member_total': Member.objects.count(),
        'active_members': Member.objects.filter(status='ACTIVE').count(),
        'receipt_total': ContributionReceipt.objects.count(),
        'claims_total': ClaimApplication.objects.count(),
        'withdrawals_total': WithdrawalApplication.objects.count(),
        'pensioners_total': Pensioner.objects.count(),
    }
    return render(request, 'dashboard/executive_dashboard.html', ctx)

# ================= V8 Production Operations =================
@login_required
def claims_approval(request):
    claims = ClaimApplication.objects.all().order_by('-id')[:100]
    return render(request, 'dashboard/v8_claims_approval.html', {'claims': claims})

@login_required
def withdrawals_approval(request):
    withdrawals = WithdrawalApplication.objects.all().order_by('-id')[:100]
    return render(request, 'dashboard/v8_withdrawals_approval.html', {'withdrawals': withdrawals})

@login_required
def payment_processing(request):
    return render(request, 'dashboard/v8_payment_processing.html')

@login_required
def reporting_centre(request):
    return render(request, 'dashboard/v8_reporting_centre.html')

@login_required
def member_statement(request):
    return render(request, 'dashboard/v8_member_statement.html')

@login_required
def audit_history(request):
    return render(request, 'dashboard/v8_audit_history.html')
