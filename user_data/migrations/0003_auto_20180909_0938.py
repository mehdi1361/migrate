# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-09 06:08
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0002_accounts'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Accounts',
            new_name='Account',
        ),
    ]
