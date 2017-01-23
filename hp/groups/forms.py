from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from bootstrap.widgets import BootstrapTextInput, BootstrapTextarea

from .models import Group

import re

class GroupDescriptionForm(forms.Form):
    group_description = forms.CharField(
        min_length = 10,
        max_length = 1000,
        label = _('Group description'),
        help_text = _('"Nothing is true, everything is permitted."'),
        widget = BootstrapTextarea,
    )


class CreateGroupForm(GroupDescriptionForm):
    group_name = forms.CharField(
        min_length = 3,
        max_length = 255,
        label = _('Group name'),
        help_text = _('3 - 255 characters, allowed are letters, numbers, space, dash, dot and underscore.'),
        widget = BootstrapTextInput,
    )

    def clean_group_name(self):
        data = self.cleaned_data['group_name']
        if not re.match("^[ A-Za-z0-9._-]+$", data):
            raise ValidationError(_('Invalid group name - special characters not allowed!'))
        elif Group.objects.filter(name=data).exists():
            raise ValidationError(_('Conflicting group name - already in use!'))
        return data


class EditGroupForm(GroupDescriptionForm):
    member_name = forms.CharField(
        min_length = settings.MIN_USERNAME_LENGTH,
        max_length = 255,
        label = _('Add members'),
        help_text = _('Only enter the JID\'s localpart (left side of the @-symbol), separate multiple JIDs with colons.'),
        widget = BootstrapTextInput,
        required = False,
    )

    owner_name = forms.CharField(
        min_length = settings.MIN_USERNAME_LENGTH,
        max_length = 255,
        label = _('Add owners'),
        help_text = _('Do not add users to a group without their consent!'),
        widget = BootstrapTextInput,
        required = False,
    )

    display = forms.CharField(
        min_length = 3,
        max_length = 1000,
        label = _('Displayed to this group'),
        help_text = _('Change which groups will be shown to this group. You must own all involved groups.'),
        widget = BootstrapTextInput,
        required = False,
    )

    def clean_member_name(self):
        data = self.cleaned_data['member_name']
        if re.match('^.*\s.*$', data) or '@' in data:
            raise ValidationError(_('Invalid input - space and @ not allowed!'))
        return data

    def clean_owner_name(self):
        data = self.cleaned_data['owner_name']
        if re.match('^.*\s.*$', data) or '@' in data:
            raise ValidationError(_('Invalid input - space and @ not allowed!'))
        return data

    def clean_display(self):
        data = self.cleaned_data['display']
        if len(data) > 0 and not re.match("^[ A-Za-z0-9.,_-]+$", data):
            raise ValidationError(_('Invalid group name - special characters not allowed!'))
        return data
