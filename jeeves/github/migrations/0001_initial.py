# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='GithubRepository',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(unique=True, help_text='the name of the GitHub repository in <account>/<repository> form', max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='GithubWebhookMatch',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('branch_match', models.CharField(help_text='a wildcard pattern of the branches to match', max_length=512)),
                ('exclude', models.BooleanField()),
                ('project', models.ForeignKey(to='core.Project', help_text='the Jeeves project', on_delete=models.CASCADE)),
                ('repository', models.ForeignKey(to='github.GithubRepository', help_text='the repository on GitHub', on_delete=models.CASCADE)),
            ],
        ),
        migrations.AlterUniqueTogether(
            name='githubwebhookmatch',
            unique_together=set([('project', 'repository', 'branch_match')]),
        ),
    ]
