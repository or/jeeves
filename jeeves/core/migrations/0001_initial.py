# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('build_id', models.IntegerField(blank=True, null=True)),
                ('status', models.CharField(default='created', choices=[('created', 'created'), ('running', 'running'), ('finished', 'finished')], max_length=16)),
                ('instance', models.CharField(max_length=1024)),
                ('branch', models.CharField(max_length=1024, null=True, blank=True)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('log_file', models.FileField(storage=django.core.files.storage.FileSystemStorage(location='logs'), upload_to='', null=True, blank=True)),
                ('result', models.CharField(blank=True, choices=[('success', 'success'), ('failure', 'failure')], null=True, max_length=16)),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(help_text='the name of the project', max_length=64)),
                ('slug', models.SlugField(help_text='the slug to identify the project')),
                ('description', models.CharField(help_text='a description of the project', max_length=1024)),
                ('script', models.TextField(help_text='the script to run for the build')),
            ],
        ),
        migrations.AddField(
            model_name='build',
            name='project',
            field=models.ForeignKey(to='core.Project', on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='build',
            unique_together=set([('project', 'build_id')]),
        ),
    ]
