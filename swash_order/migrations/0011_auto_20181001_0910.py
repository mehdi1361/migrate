# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-01 05:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('swash_order', '0010_ordermessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('draft', 'draft'), ('confirmed', 'confirmed'), ('paid', 'paid'), ('pickup', 'pickup'), ('progress', 'progress'), ('packing', 'packing'), ('on_the_way_delivered', 'on_the_way_delivered'), ('on_the_way_pickedup', 'on_the_way_pickedup'), ('delivered', 'delivered'), ('pending', 'pending'), ('cancel', 'cancel'), ('pickedup', 'pickedup'), ('done', 'done')], default='draft', max_length=20, verbose_name='status'),
        ),
    ]
