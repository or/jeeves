# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_buildsource'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='modified_time',
            field=models.DateTimeField(default=datetime.datetime(2015, 9, 30, 16, 13, 19, 382239, tzinfo=utc), auto_now=True, db_index=True),
            preserve_default=False,
        ),
    ]
