# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-26 17:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20161226_1719'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='account_expires_notified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='notifications',
            name='gpg_expires_notified',
            field=models.BooleanField(default=False),
        ),
    ]
