# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationmetadata',
            name='type',
            field=models.CharField(choices=[('flowdock', 'flowdock')], default='flowdock', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='notificationmetadata',
            unique_together=set([('build', 'type')]),
        ),
    ]
