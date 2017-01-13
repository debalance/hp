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
from django.views.generic.edit import CreateView
#from django.views.generic.edit import TemplateView
from django.views.generic.edit import UpdateView

from celery import chain
from xmpp_http_upload.models import Upload
from xmpp_backends.django import xmpp_backend

from core.constants import ACTIVITY_REGISTER
from core.constants import ACTIVITY_RESET_PASSWORD
from core.constants import ACTIVITY_SET_EMAIL
from core.constants import ACTIVITY_SET_PASSWORD
from core.constants import ACTIVITY_FAILED_LOGIN
from core.models import AddressActivity
from core.views import AnonymousRequiredMixin
from core.views import BlacklistMixin
from core.views import DnsBlMixin
from core.views import RateLimitMixin
from core.views import StaticContextMixin

from account.models import Confirmation
from account.views import UserObjectMixin

#from .forms import TODO
#from .forms import TODO
#from .forms import TODO
#from .forms import TODO

#from .models import *

User = get_user_model()
log = logging.getLogger(__name__)
_confirmation_qs = Confirmation.objects.valid().select_related('user')


class GroupPageMixin(StaticContextMixin):
    """Mixin that adds the groupmenu on the left to views where the user is logged in."""

    groupmenu = (
        ('group:detail',    _('Overview'),          False),
        ('group:ownership', _('My Groups'),         True),
        ('group:membership',_('My Memberships'),    True),
        ('group:create',    _('Create new Group'),  True),
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
        return self.groupmenu

    def get_context_data(self, **kwargs):
        context = super(GroupPageMixin, self).get_context_data(**kwargs)
        context['groupmenu'] = self.get_groupmenu()
        return context


class GroupView(LoginRequiredMixin, GroupPageMixin, UserObjectMixin, TemplateView):
    """Main group settings view (/groups)."""
    template_name = 'groups/detail.html'
    groupmenu_item = 'group:detail'
    requires_confirmation = False


class OwnershipView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/ownership.html'
    groupmenu_item = 'group:ownership'


class MembershipView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/membership.html'
    groupmenu_item = 'group:membership'


class CreateView(LoginRequiredMixin, GroupPageMixin, TemplateView):
    template_name = 'groups/create.html'
    groupmenu_item = 'group:create'


