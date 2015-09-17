# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20150916_2234'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='result_details',
            field=models.CharField(blank=True, null=True, max_length=1024),
        ),
    ]
