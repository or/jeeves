# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20150916_2234'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationMetadata',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('data', jsonfield.fields.JSONField()),
                ('build', models.ForeignKey(to='core.Build')),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTarget',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, primary_key=True, verbose_name='ID')),
                ('type', models.CharField(max_length=10, choices=[('flowdock', 'flowdock')])),
                ('token', models.CharField(max_length=128)),
                ('channel', models.CharField(max_length=256)),
                ('project', models.ForeignKey(to='core.Project')),
            ],
        ),
    ]
