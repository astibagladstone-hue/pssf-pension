"""
Celery tasks for background processing
"""
from celery import shared_task
from django.db.models import Sum
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

@shared_task
def check_overdue_tickets():
    from dashboard.models import Ticket
    now = timezone.now().date()
    overdue_tickets = Ticket.objects.filter(is_overdue=False, due_date__lt=now, is_active=True).exclude(status__in=['CLOSED', 'ARCHIVED'])
    count = overdue_tickets.update(is_overdue=True)
    logger.info(f"Updated {count} tickets as overdue")
    return {'tickets_updated': count, 'status': 'success'}
