import os

from celery import Celery
from celery.schedules import crontab
from django.conf import settings

# from django.apps import apps
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tealcrm.settings")

app = Celery("tealcrm")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
