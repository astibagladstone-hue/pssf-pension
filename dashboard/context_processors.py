"""
Template context processors for global variables
"""


def system_stats(request):
    """
    Temporary safe dashboard stats.

    This prevents the dashboard from crashing when
    database tables are not yet created on Render.
    """

    return {
        "system_stats": {
            "total_members": 0,
            "active_members": 0,
            "total_schemes": 0,
            "active_schemes": 0,
            "pending_tickets": 0,
            "unallocated_receipts": 0,
        }
    }
