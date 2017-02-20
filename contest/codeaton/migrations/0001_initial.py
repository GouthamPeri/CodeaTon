# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-20 09:53
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('question_code', models.CharField(max_length=10, primary_key=True, serialize=False)),
                ('question_text', models.CharField(max_length=10000)),
                ('question_marks', models.IntegerField()),
                ('sample_input', models.CharField(max_length=1000)),
                ('sample_output', models.CharField(max_length=1000)),
                ('constraints', models.CharField(max_length=1000)),
                ('explanation', models.CharField(max_length=3000)),
            ],
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('team_name', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('status', models.CharField(max_length=10000)),
                ('program_code', models.CharField(max_length=100000)),
                ('time', models.CharField(blank=True, max_length=1000, null=True)),
                ('total_score', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='UserLoginTime',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('login_time', models.CharField(max_length=30)),
            ],
        ),
    ]
