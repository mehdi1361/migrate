# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-30 13:39
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('swash_order', '0007_auto_20180930_0909'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='orderaddress',
            unique_together=set([]),
        ),
    ]
