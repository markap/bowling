# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-31 14:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_frame_is_closed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='frame',
            name='is_closed',
        ),
    ]
