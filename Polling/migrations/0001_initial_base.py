# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-12-21 11:16
from __future__ import unicode_literals

import Polling.enums
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, max_length=2048, null=True)),
                ('status', models.PositiveSmallIntegerField(choices=[(0, Polling.enums.PollStatus(0)), (1, Polling.enums.PollStatus(1))], default=0)),
            ],
        ),
        migrations.CreateModel(
            name='PollOption',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.CharField(max_length=255)),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polling.Poll')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=255, unique=True)),
                ('email', models.EmailField(max_length=254, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPoll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choices', django.contrib.postgres.fields.jsonb.JSONField()),
                ('poll', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polling.Poll')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polling.User')),
            ],
        ),
        migrations.AddField(
            model_name='poll',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='Polling.User'),
        ),
    ]
