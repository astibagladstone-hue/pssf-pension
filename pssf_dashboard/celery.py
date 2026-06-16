import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pssf_dashboard.settings')
app = Celery('pssf_dashboard')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
