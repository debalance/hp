import re

from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from account.models import User
from xmpp_backends.django import xmpp_backend


class Group(models.Model):
    name         = models.CharField(max_length=255,  unique=True,  verbose_name=_('Group name')             )
    description  = models.CharField(max_length=1023, unique=False, verbose_name=_('Group description')      )
    displayed_to = models.CharField(max_length=1023, unique=False, verbose_name=_('Displayed to this group'),
        help_text=_('Multiple groups must be separated with line-breaks, i.e. one group per line!')         )

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

