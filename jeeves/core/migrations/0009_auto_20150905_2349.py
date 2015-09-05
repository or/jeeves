# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20150905_2101'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='creation_time',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='build',
            name='start_time',
            field=models.DateTimeField(blank=True, null=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='build',
            name='status',
            field=models.CharField(choices=[('scheduled', 'scheduled'), ('blocked', 'blocked'), ('running', 'running'), ('finished', 'finished'), ('cancelled', 'cancelled')], max_length=16, default='scheduled', db_index=True),
        ),
        migrations.AlterIndexTogether(
            name='build',
            index_together=set([('project', 'blocking_key', 'build_id'), ('project', 'build_id')]),
        ),
    ]
