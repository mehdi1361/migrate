# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-09-30 17:22
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('swash_order', '0009_auto_20180930_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='created date')),
                ('text_message', models.TextField(verbose_name='text message')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sender_messages', to='swash_order.Order', verbose_name='order')),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='order_messages', to=settings.AUTH_USER_MODEL, verbose_name='sender')),
            ],
            options={
                'verbose_name': 'message',
                'verbose_name_plural': 'messages',
                'db_table': 'messages',
            },
        ),
    ]