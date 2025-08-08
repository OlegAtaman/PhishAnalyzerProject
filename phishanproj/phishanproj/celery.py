import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'phishanproj.settings')

phishanalyzer = Celery('phishanproj')

phishanalyzer.config_from_object('django.conf:settings', namespace='CELERY')

phishanalyzer.autodiscover_tasks()

# @phishanalyzer.task(bind=True, ignore_result=True)
# def debug_task(self):
#     print(f'Request: {self.request!r}')