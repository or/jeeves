# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_auto_20150909_0003'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='job',
            unique_together=set([('build', 'name')]),
        ),
        migrations.AlterUniqueTogether(
            name='jobdescription',
            unique_together=set([('project', 'name')]),
        ),
    ]
