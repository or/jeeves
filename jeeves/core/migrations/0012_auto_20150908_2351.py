# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_job'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='job',
        ),
        migrations.AddField(
            model_name='build',
            name='result',
            field=models.CharField(choices=[('success', 'success'), ('failure', 'failure')], null=True, max_length=16, blank=True),
        ),
        migrations.AddField(
            model_name='job',
            name='name',
            field=models.CharField(max_length=128, default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='job',
            name='status',
            field=models.CharField(db_index=True, choices=[('running', 'running'), ('finished', 'finished')], max_length=16, default='running'),
        ),
    ]
