import logging

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

from account.models import User

log = logging.getLogger(__name__)


class Group(models.Model):
    name         = models.CharField(max_length=255,  unique=True,  verbose_name=_('Group name')       )
    description  = models.CharField(max_length=1023, unique=False, verbose_name=_('Group description'))
    displayed_to = models.CharField(max_length=1023, unique=False, verbose_name=_('Group description'))

    owners  = models.ManyToManyField(User,  through='ownership',  through_fields=('group', 'user'), related_name='owner'  )
    members = models.ManyToManyField(User,  through='membership', through_fields=('group', 'user'), related_name='member' )

class ownership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user  = models.ForeignKey(User,  on_delete=models.CASCADE)

class membership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user  = models.ForeignKey(User,  on_delete=models.CASCADE)
