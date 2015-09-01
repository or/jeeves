# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20150831_2319'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='modified_time',
            field=models.DateTimeField(db_index=True, default=datetime.datetime(2015, 9, 1, 19, 24, 32, 265986, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
