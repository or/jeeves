from __future__ import absolute_import

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jeeves.settings')

app = Celery('jeeves')

app.config_from_object('django.conf:settings')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))
