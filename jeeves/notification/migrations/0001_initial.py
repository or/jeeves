# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_auto_20150920_2059'),
    ]

    operations = [
        migrations.CreateModel(
            name='NotificationMetadata',
            fields=[
                ('build', models.OneToOneField(primary_key=True, to='core.Build', serialize=False)),
                ('data', jsonfield.fields.JSONField()),
            ],
        ),
        migrations.CreateModel(
            name='NotificationTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('type', models.CharField(max_length=10, choices=[('flowdock', 'flowdock')])),
                ('token', models.CharField(max_length=128)),
                ('channel', models.CharField(max_length=256)),
                ('project', models.ForeignKey(to='core.Project')),
            ],
        ),
    ]
