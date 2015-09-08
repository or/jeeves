# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_auto_20150909_0005'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='end_time',
            field=models.DateTimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='start_time',
            field=models.DateTimeField(default='2015-09-05 00:00:00', auto_now_add=True, db_index=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='jobdescription',
            name='report_result',
            field=models.BooleanField(default=False),
            preserve_default=False,
        ),
    ]
