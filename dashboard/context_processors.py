"""
Template context processors for global variables
"""
from django.db.models import Count, Sum
from dashboard.models import Member, Scheme, Ticket, ContributionReceipt

def system_stats(request):
    return {
        'system_stats': {
            'total_members': Member.objects.filter(is_active=True).count(),
            'active_members': Member.objects.filter(status='ACTIVE', is_active=True).count(),
            'total_schemes': Scheme.objects.filter(is_active=True).count(),
            'active_schemes': Scheme.objects.filter(status='ACTIVE', is_active=True).count(),
            'pending_tickets': Ticket.objects.filter(status__in=['NEW', 'OPEN', 'IN_PROGRESS'], is_active=True).count(),
            'unallocated_receipts': ContributionReceipt.objects.filter(unallocated_amount__gt=0, is_active=True).count(),
        }
    }
