# -*- coding: utf-8 -*-
# Generated by Django 1.10.3 on 2016-11-25 14:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_auto_20161125_1312'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='old_author_post', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='page',
            name='author',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='old_author_page', to=settings.AUTH_USER_MODEL),
        ),
    ]
