# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20150905_2349'),
    ]

    operations = [
        migrations.CreateModel(
            name='JobDescription',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(help_text='the name of the job inside the build', max_length=128)),
                ('dependencies', models.CharField(help_text='a list of job names this job depends on', blank=True, max_length=1024, null=True)),
                ('script', models.TextField(help_text='the script to run for the job')),
            ],
        ),
        migrations.RemoveField(
            model_name='build',
            name='log_file',
        ),
        migrations.RemoveField(
            model_name='build',
            name='result',
        ),
        migrations.RemoveField(
            model_name='project',
            name='script',
        ),
        migrations.AddField(
            model_name='jobdescription',
            name='project',
            field=models.ForeignKey(to='core.Project'),
        ),
    ]
