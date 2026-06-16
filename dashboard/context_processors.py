"""
Template context processors for global variables
"""

def system_stats(request):
    """
    Temporary dashboard preview mode.
    Database queries removed so dashboard loads
    even before migrations/tables exist.
    """

    return {
        'system_stats': {
            'total_members': 0,
            'active_members': 0,
            'total_schemes': 0,
            'active_schemes': 0,
            'pending_tickets': 0,
            'unallocated_receipts': 0,
        }
    }
