# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-11 19:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_data', '0015_ticket_tickethistory'),
    ]

    operations = [
        migrations.CreateModel(
            name='TicketMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True, verbose_name='created date')),
                ('updated_date', models.DateTimeField(auto_now=True, verbose_name='created date')),
                ('message', models.CharField(max_length=200, verbose_name='message')),
                ('ticket', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='user_data.Ticket', verbose_name='ticket')),
            ],
            options={
                'verbose_name': 'ticket',
                'verbose_name_plural': 'tickets',
                'db_table': 'ticket_message',
            },
        ),
    ]
