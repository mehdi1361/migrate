# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-13 23:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0006_profile_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='device',
            name='device_id',
            field=models.CharField(max_length=500, verbose_name='device model'),
        ),
    ]
