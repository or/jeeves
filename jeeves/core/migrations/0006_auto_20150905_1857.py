# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_build_commit'),
    ]

    operations = [
        migrations.AddField(
            model_name='build',
            name='blocked_by',
            field=models.ForeignKey(null=True, blank=True, to='core.Build'),
        ),
        migrations.AddField(
            model_name='build',
            name='blocking_key',
            field=models.CharField(null=True, blank=True, max_length=1024),
        ),
        migrations.AddField(
            model_name='project',
            name='blocking_key_template',
            field=models.CharField(help_text='a template for a blocking key, builds with the same key will block each other; a constant key will result in a blocking build queue', null=True, blank=True, max_length=2048),
        ),
    ]
