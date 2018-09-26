# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-12 05:57
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0004_auto_20180909_2049'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='created date')),
                ('first_name', models.CharField(blank=True, max_length=50, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=50, verbose_name='last name')),
                ('gender', models.CharField(choices=[('male', 'male'), ('female', 'female')], default='male', max_length=6, verbose_name='gender')),
                ('email', models.CharField(blank=True, max_length=200, null=True, verbose_name='email field')),
            ],
            options={
                'verbose_name': 'profile',
                'verbose_name_plural': 'profiles',
                'db_table': 'profiles',
            },
        ),
    ]