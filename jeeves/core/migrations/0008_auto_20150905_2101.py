# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20150905_1932'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='status',
            field=models.CharField(max_length=16, choices=[('scheduled', 'scheduled'), ('blocked', 'blocked'), ('running', 'running'), ('finished', 'finished'), ('cancelled', 'cancelled')], default='scheduled'),
        ),
    ]
