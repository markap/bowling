# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-31 14:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20180831_1329'),
    ]

    operations = [
        migrations.AddField(
            model_name='frame',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
