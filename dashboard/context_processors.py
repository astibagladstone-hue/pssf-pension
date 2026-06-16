from dashboard.models import Member, Scheme, Ticket, ContributionReceipt


def system_stats(request):

    try:
        total_members = Member.objects.filter(is_active=True).count()
        active_members = Member.objects.filter(
            status='ACTIVE',
            is_active=True
        ).count()

        total_schemes = Scheme.objects.filter(is_active=True).count()
        active_schemes = Scheme.objects.filter(
            status='ACTIVE',
            is_active=True
        ).count()

        pending_tickets = Ticket.objects.filter(
            status__in=['NEW', 'OPEN', 'IN_PROGRESS'],
            is_active=True
        ).count()

        unallocated_receipts = ContributionReceipt.objects.filter(
            unallocated_amount__gt=0,
            is_active=True
        ).count()

    except Exception:
        total_members = 0
        active_members = 0
        total_schemes = 0
        active_schemes = 0
        pending_tickets = 0
        unallocated_receipts = 0

    return {
        'system_stats': {
            'total_members': total_members,
            'active_members': active_members,
            'total_schemes': total_schemes,
            'active_schemes': active_schemes,
            'pending_tickets': pending_tickets,
            'unallocated_receipts': unallocated_receipts,
        }
    }
