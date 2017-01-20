from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from bootstrap.widgets import BootstrapTextInput, BootstrapTextarea

from .models import Group

import re

class CreateGroupForm(forms.Form):
    group_name = forms.CharField(
        min_length = 3,
        max_length = 255,
        label = _('Group name'),
        help_text = _('3 - 255 characters, allowed are letters, numbers, space, dash, dot and underscore.'),
        widget = BootstrapTextInput,
    )
    group_description = forms.CharField(
        min_length = 10,
        max_length = 1023,
        label = _('Group description'),
        help_text = _('10 - 1023 characters. "Nothing is true, everything is permitted."'),
        widget = BootstrapTextarea,
    )

    def clean_group_name(self):
        #TODO: check if group already exists
        data = self.cleaned_data['group_name']
        if not re.match("^[ A-Za-z0-9._-]+$", data):
            raise ValidationError(_('Invalid group name - special characters not allowed!'))
        elif Group.objects.filter(name=data).exists():
            raise ValidationError(_('Conflicting group name - already in use!'))
        return data
    
