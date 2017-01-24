import logging
import re

from contextlib import contextmanager

from django.conf import settings
from django.contrib.auth.models import PermissionsMixin
from django.contrib.messages import constants as messages
from django.core.mail import EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.template import Context
from django.template import Template
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils import translation
from django.utils.crypto import get_random_string
from django.utils.crypto import salted_hmac
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop

from xmpp_backends.django import xmpp_backend

from account.models import User


log = logging.getLogger(__name__)

#TODO: add hooks to create/change/delete groups in ejabberd

class Group(models.Model):
    name         = models.CharField(max_length=255,  unique=True,  verbose_name=_('Group name')             )
    description  = models.CharField(max_length=1023, unique=False, verbose_name=_('Group description')      )
    displayed_to = models.CharField(max_length=1023, unique=False, verbose_name=_('Displayed to this group'))

    owners  = models.ManyToManyField(User,  through='ownership',  through_fields=('group', 'user'), related_name='owner'  )
    members = models.ManyToManyField(User,  through='membership', through_fields=('group', 'user'), related_name='member' )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('groups:details', args=[str(self.id)])

    def save(self, *args, **kwargs):
        xmpp_backend.srg_create(groupname=self.name, domain='jabber.rwth-aachen.de', text=self.description, displayed=self.displayed_to)
        super(Group, self).save(*args, **kwargs)

    def save_native(self, *args, **kwargs):
        super(Group, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        xmpp_backend.srg_delete(groupname=self.name, domain='jabber.rwth-aachen.de')
        super(Group, self).delete(*args, **kwargs)

    def delete_native(self, *args, **kwargs):
        super(Group, self).delete(*args, **kwargs)


class ownership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user  = models.ForeignKey(User,  on_delete=models.CASCADE)

    def __str__(self):
        return self.group.name + ": " + self.user.username

    def groupname(self):
        return self.group.name

    def username(self):
        return self.user.username


class membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user  = models.ForeignKey(User,  on_delete=models.CASCADE)

    def __str__(self):
        return self.group.name + ": " + self.user.username

    def groupname(self):
        return self.group.name

    def username(self):
        return self.user.username

    def save(self, *args, **kwargs):
        user = re.split('@', self.user.username)[0]
        node = re.split('@', self.user.username)[1]
        xmpp_backend.srg_user_add(username=user, domain=node, groupname=self.group.name)
        super(membership, self).save(*args, **kwargs)

    def save_native(self, *args, **kwargs):
        super(membership, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        user = re.split('@', self.user.username)[0]
        node = re.split('@', self.user.username)[1]
        xmpp_backend.srg_user_del(username=user, domain=node, groupname=self.group.name)
        super(membership, self).delete(*args, **kwargs)

    def delete_native(self, *args, **kwargs):
        super(membership, self).delete(*args, **kwargs)

