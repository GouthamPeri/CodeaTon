# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-25 13:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('codeaton', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='registration',
            name='member_1_phone_no',
            field=models.CharField(max_length=15),
        ),
        migrations.AlterField(
            model_name='registration',
            name='member_2_phone_no',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='registration',
            name='team_name',
            field=models.CharField(max_length=30, primary_key=True, serialize=False),
        ),
    ]
