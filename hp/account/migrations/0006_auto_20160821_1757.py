# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-21 17:57
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_gpgkey_userlogentry'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gpgkey',
            options={'verbose_name': 'GPG key', 'verbose_name_plural': 'GPG keys'},
        ),
        migrations.AlterModelOptions(
            name='userlogentry',
            options={'verbose_name': 'User activity log', 'verbose_name_plural': 'User activity logs'},
        ),
    ]
