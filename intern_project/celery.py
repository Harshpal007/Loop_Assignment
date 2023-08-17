# celery.py

import os
from celery import Celery
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'intern_project.settings')


app = Celery('Loop_Assignment')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
