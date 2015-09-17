# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20150909_0036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='build',
            name='metadata',
            field=jsonfield.fields.JSONField(default={}),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='jobdescription',
            name='report_result',
            field=models.BooleanField(help_text='flag whether the result of this job should be reported on GitHub'),
        ),
    ]
