# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20150902_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='commit',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
