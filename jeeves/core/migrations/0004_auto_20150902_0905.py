# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_build_modified_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='reason',
            field=models.CharField(null=True, max_length=128),
        ),
        migrations.AddField(
            model_name='build',
            name='repository',
            field=models.CharField(blank=True, null=True, max_length=512),
        ),
    ]
