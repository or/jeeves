# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20150908_2309'),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('log_file', models.FileField(upload_to='', blank=True, storage=django.core.files.storage.FileSystemStorage(location='logs'), null=True)),
                ('result', models.CharField(choices=[('success', 'success'), ('failure', 'failure')], max_length=16, blank=True, null=True)),
                ('build', models.ForeignKey(to='core.Build')),
                ('job', models.ForeignKey(to='core.JobDescription')),
            ],
        ),
    ]
