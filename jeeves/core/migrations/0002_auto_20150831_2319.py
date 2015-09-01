# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='build',
            name='instance',
        ),
        migrations.AddField(
            model_name='build',
            name='creation_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 8, 31, 21, 19, 28, 164245, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='build',
            name='metadata',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='build',
            name='status',
            field=models.CharField(choices=[('scheduled', 'scheduled'), ('running', 'running'), ('finished', 'finished')], default='scheduled', max_length=16),
        ),
    ]
