# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20150908_2351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='job',
            name='name',
            field=models.SlugField(max_length=128),
        ),
        migrations.AlterField(
            model_name='jobdescription',
            name='name',
            field=models.SlugField(help_text='the name of the job inside the build', max_length=128),
        ),
    ]
