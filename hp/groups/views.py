import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.db import transaction
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.shortcuts import resolve_url
from django.template.response import TemplateResponse
from django.utils import timezone
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ugettext_noop
from django.views.generic import View
from django.views.generic import DetailView
from django.views.generic.base import RedirectView
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin

from .models import Group
from account.models import User
from account.models import Confirmation
from account.views import UserObjectMixin
from core.views import StaticContextMixin
from xmpp_backends.django import xmpp_backend


User = get_user_model()
log = logging.getLogger(__name__)
_confirmation_qs = Confirmation.objects.valid().select_related('user')


class GroupPageMixin(StaticContextMixin):
    """Mixin that adds the groupmenu on the left to views where the user is logged in."""

    groupmenu = (
        ('groups:overview',  {'title':_('Overview'),          'requires_confirmation': False }),
        ('groups:ownership', {'title':_('My groups'),         'requires_confirmation': True  }),
        ('groups:membership',{'title':_('My memberships'),    'requires_confirmation': True  }),
        ('groups:create',    {'title':_('Create new group'),  'requires_confirmation': True  }),
    )
    groupmenu_item = None
    requires_email = False
    requires_confirmation = True

    def dispatch(self, request, *args, **kwargs):
        if self.requires_confirmation and not request.user.created_in_backend:
            kwargs = {}
            if isinstance(self, SingleObjectMixin):
                self.object = self.get_object()
                kwargs['object'] = self.object
            context = self.get_context_data(**kwargs)

            return TemplateResponse(request, 'account/requires_confirmation.html', context)
        elif self.requires_email and not request.user.email:
            kwargs = {}
            if isinstance(self, SingleObjectMixin):
                self.object = self.get_object()
                kwargs['object'] = self.object
            context = self.get_context_data(**kwargs)

            return TemplateResponse(request, 'account/requires_email.html', context)

        return super(GroupPageMixin, self).dispatch(request, *args, **kwargs)

    def get_groupmenu(self):
        groupmenu = []
        for urlname, config in self.groupmenu:
            req_confirmation = config.get('requires_confirmation', True)
            if self.request.user.created_in_backend is False and req_confirmation is True:
                continue

            groupmenu.append({
                'path': reverse(urlname),
                'title': config.get('title', 'No title'),
                'active': ' active' if urlname == self.groupmenu_item else '',
            })
        return groupmenu

    def get_context_data(self, **kwargs):
        context = super(GroupPageMixin, self).get_context_data(**kwargs)
        context['groupmenu'] = self.get_groupmenu()
        return context


class OverView(LoginRequiredMixin, GroupPageMixin, UserObjectMixin, TemplateView):
    """Main group settings view (/groups)."""
    template_name = 'groups/overview.html'
    groupmenu_item = 'groups:overview'
    requires_confirmation = False


class OwnershipView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/ownership.html'
    groupmenu_item = 'groups:ownership'


class MembershipView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/membership.html'
    groupmenu_item = 'groups:membership'


class CreateView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/create.html'
    groupmenu_item = 'groups:create'
    #TODO


class GroupView(LoginRequiredMixin, GroupPageMixin, DetailView):
    #TODO: only allow members+owners to see group information, show edit button only to owners
    model = Group
    template_name = 'groups/group.html'
    #TODO


class EditView(LoginRequiredMixin, GroupPageMixin, DetailView):
    #TODO: only allow members+owners to see and edit group information
    model = Group
    template_name = 'groups/edit.html'
    #TODO

class LeaveView(LoginRequiredMixin, GroupPageMixin, DetailView):
    #TODO: only allow members+owners to see and use this
    model = Group
    template_name = 'groups/leave.html'
    #TODO

class DeleteView(LoginRequiredMixin, GroupPageMixin, DetailView):
    #TODO: only allow owners to see and use this
    model = Group
    template_name = 'groups/delete.html'
    #TODO
