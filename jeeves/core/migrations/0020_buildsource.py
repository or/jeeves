# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0019_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='BuildSource',
            fields=[
                ('build', models.OneToOneField(related_name='source', to='core.Build', serialize=False, primary_key=True, on_delete=models.CASCADE)),
                ('source', models.ForeignKey(related_name='copies', to='core.Build', on_delete=models.CASCADE)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
    ]
