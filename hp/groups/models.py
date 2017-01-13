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


log = logging.getLogger(__name__)


#class Group(models.Model):
#    name = models.CharField(max_length=255, unique=True, verbose_name=_('SharedRosterGroup'))
#    Members = models.ManyToManyField(
#        Member,
#        through='Membership',
#        through_fields=('Group', 'Member'),
#    )
#    owners = models.ManyToManyField(
#        Member,
#        through='Ownership',
#        through_fields=('Group', 'Member'),
#    )
#    display = models.ManyToManyFiled(
#        Member,
#        through='Display',
#        through_fields=('Group', 'Member'),
#    )
#
#class Member(models.Model):
#    name = models.CharField(max_length=255, unique=True, verbose_name=_('Membername'))
#    Group = models.ForeignKey(Group)
#
#class Membership(models.Model):
#    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
#    Member = models.ForeignKey(Member, on_delete=models.CASCADE)
#
#class Ownership(models.Model):
#    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
#    Member = models.ForeignKey(Member, on_delete=models.CASCADE)
#
#class Display(models.Model):
#    Group = models.ForeignKey(Group, on_delete=models.CASCADE)
#    Member = models.ForeignKey(Member, on_delete=models.CASCADE)
