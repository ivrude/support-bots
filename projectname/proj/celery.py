from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proj.settings")
app = Celery("proj")

# Use the Django settings for the Celery configuration.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Use billiard pool to spawn child processes on Windows
if os.name == "nt":
    app.conf.worker_pool = "solo"
else:
    app.conf.worker_pool = "prefork"

# Load task modules from all registered Django app configs.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)