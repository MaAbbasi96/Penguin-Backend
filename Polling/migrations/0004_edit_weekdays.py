# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-29 11:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Polling', '0003_weekly_poll'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklypolloption',
            name='weekday',
            field=models.PositiveSmallIntegerField(choices=[(0, 'شنبه'), (1, 'یکشنبه'), (2, 'دوشنبه'), (3, 'سه شنبه'), (4, 'چهارشنبه'), (5, 'پنجشنبه'), (6, 'جمعه')]),
        ),
    ]
