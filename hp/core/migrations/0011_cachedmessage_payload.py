# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-01-08 16:04
from __future__ import unicode_literals

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20161125_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='cachedmessage',
            name='payload',
            field=jsonfield.fields.JSONField(default=dict),
        ),
    ]
