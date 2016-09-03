# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-03 12:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug_de',
            field=models.CharField(help_text='Slug (used in URLs)', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='slug_en',
            field=models.CharField(help_text='Slug (used in URLs)', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='title_de',
            field=models.CharField(help_text='Page title', max_length=255),
        ),
        migrations.AlterField(
            model_name='blogpost',
            name='title_en',
            field=models.CharField(help_text='Page title', max_length=255),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug_de',
            field=models.CharField(help_text='Slug (used in URLs)', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='slug_en',
            field=models.CharField(help_text='Slug (used in URLs)', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='page',
            name='title_de',
            field=models.CharField(help_text='Page title', max_length=255),
        ),
        migrations.AlterField(
            model_name='page',
            name='title_en',
            field=models.CharField(help_text='Page title', max_length=255),
        ),
    ]
