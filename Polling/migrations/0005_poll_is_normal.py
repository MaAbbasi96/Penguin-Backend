# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-29 13:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polling', '0004_edit_weekdays'),
    ]

    operations = [
        migrations.AddField(
            model_name='poll',
            name='is_normal',
            field=models.BooleanField(default=True),
        ),
    ]
