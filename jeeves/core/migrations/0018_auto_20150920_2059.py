# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_job_result_details'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='result_details',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='build',
            name='result',
            field=models.CharField(blank=True, null=True, choices=[('success', 'success'), ('failure', 'failure'), ('error', 'error')], max_length=16),
        ),
        migrations.AlterField(
            model_name='job',
            name='result',
            field=models.CharField(blank=True, null=True, choices=[('success', 'success'), ('failure', 'failure'), ('failure', 'failure')], max_length=16),
        ),
        migrations.AlterField(
            model_name='job',
            name='result_details',
            field=models.TextField(blank=True, null=True),
        ),
    ]
