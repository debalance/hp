import logging
log = logging.getLogger(__name__)
import re

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import FormView
from django.views.generic.base import TemplateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import CreateView
from django.views.generic.edit import FormMixin
from django.views.generic.edit import UpdateView

from account.models import User
from account.models import Confirmation
from account.views import UserObjectMixin
from core.views import StaticContextMixin
from xmpp_backends.base import BackendError
from xmpp_backends.django import xmpp_backend

from .forms import CreateGroupForm
from .forms import EditGroupForm

from .models import Group
from .models import membership
from .models import ownership

#TODO: add user activity logs

#
# context menu
#
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


#
# helper mixins
#
class GroupAuthMixin():
    """Mixin that adds authorization information for Group"""

    def authorized_to_edit(self):
        user = self.request.user
        if user.is_superuser:
            return True
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.owner.all():
            return True
        else:
            return False

    def authorized_to_leave(self):
        user = self.request.user
        if user.is_superuser:
            return True
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.member.all():
            return True
        else:
            return False

    def authorized(self):
        user = self.request.user
        if user.is_superuser:
            return True
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.owner.all():
            return True
        elif group in user.member.all():
            return True
        else:
            return False


#
# menu items
#
class OverView(LoginRequiredMixin, GroupPageMixin, TemplateView):
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


class CreateGroupView(LoginRequiredMixin, GroupPageMixin, FormView):
    template_name = 'groups/create.html'
    groupmenu_item = 'groups:create'
    form_class = CreateGroupForm

    def form_valid(self, form):
        new_group = Group(
            name = form.cleaned_data.get('group_name'),
            description = form.cleaned_data.get('group_description'),
            displayed_to = form.cleaned_data.get('group_name'),
        )
        new_group.save()
        new_ownership = ownership(
            group = new_group,
            user = self.request.user,
        )
        new_ownership.save()
        new_membership = membership(
            group = new_group,
            user = self.request.user,
        )
        new_membership.save()
        return HttpResponseRedirect(new_group.get_absolute_url())


#
# additional views
#
class GroupView(LoginRequiredMixin, GroupPageMixin, GroupAuthMixin, DetailView):
    model = Group
    template_name = 'groups/group.html'

    def display_list(self):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        dlist = re.split("\n", group.displayed_to)
        return dlist


class LeaveView(LoginRequiredMixin, GroupPageMixin, GroupAuthMixin, DetailView):
    model = Group
    template_name = 'groups/leave.html'

    def post(self, request, *args, **kwargs):
        user = self.request.user
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.member.all():
            membership.objects.filter(user=user.id,group=group.id).delete()
            messages.success(self.request, _("You have left the group '%(group)s'.") % { 'group': group.name })
        else:
            messages.error(self.request, _("You are not a member of this group so you cannot leave it!"))
        return HttpResponseRedirect(reverse('groups:membership'))


class EditView(LoginRequiredMixin, GroupPageMixin, GroupAuthMixin, FormMixin, DetailView):
    template_name = 'groups/edit.html'
    model = Group
    form_class = EditGroupForm

    def get_initial(self):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        initial = super(EditView, self).get_initial()
        initial['group_description'] = group.description
        return initial

    def get_context_data(self, **kwargs):
        context = super(EditView, self).get_context_data(**kwargs)
        context['form'] = self.get_form()
        return context

    def display_list(self):
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        dlist = re.split("\n", group.displayed_to)
        return dlist

    def post(self, request, *args, **kwargs):
        user = self.request.user
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.owner.all() or user.is_superuser:
            self.object = self.get_object()
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form, group)
            else:
                return self.form_invalid(form)
        else:
            messages.error(self.request, _("You are not an owner of this group so you cannot edit it!"))
            return HttpResponseRedirect(reverse('groups:ownership'))

    def form_valid(self, form, group):
        user = self.request.user

        if 'delete_owner' in self.request.POST:
            owner_object = User.objects.get(username = self.request.POST["delete_owner"])
            ownership.objects.get(user=owner_object.id,group=group.id).delete()
            messages.success(self.request, _("Removed %(user)s as owner of this group.") % { 'user': owner_object.username })

        elif 'delete_member' in self.request.POST:
            member_object = User.objects.get(username = self.request.POST["delete_member"])
            membership.objects.get(user=member_object.id,group=group.id).delete()
            messages.success(self.request, _("Removed %(user)s as member of this group.") % { 'user': member_object.username })

        elif 'add_member' in self.request.POST:
            member_string = form.cleaned_data.get('member_name')
            if len(member_string) < settings.MIN_USERNAME_LENGTH:
                messages.error(self.request, _("Invalid input in 'Add members' field: username too short!"))
            else:
                member_list = re.split(",", member_string)
                valid_member_list = []
                already_member_list = []
                for member in member_list:
                    try:
                        member_object = User.objects.get(username = '%s@jabber.rwth-aachen.de' % member)
                        if membership.objects.filter(user=member_object.id,group=group.id).count() == 0:
                            new_membership = membership(
                                group = group,
                                user = member_object,
                            )
                            new_membership.save()
                            valid_member_list.append(member)
                        else:
                            already_member_list.append(member)
                    except User.DoesNotExist:
                        messages.error(self.request, _("Invalid user in 'Add members' field: '%(user)s'") % { 'user': member })
                member_string = ", ".join(valid_member_list)
                if len(member_string) > 0:
                    messages.success(self.request, _("The following members have been added to the group: %(member)s")
                        % { 'member': member_string })
                already_member_string = ", ".join(already_member_list)
                if len(already_member_string) > 0:
                    messages.info(self.request, _("The following users have already been members of the group: %(member)s")
                        % { 'member': already_member_string })

        elif 'add_owner' in self.request.POST:
            owner_string = form.cleaned_data.get('owner_name')
            if len(owner_string) < settings.MIN_USERNAME_LENGTH:
                messages.error(self.request, _("Invalid input in 'Add owners' field: username too short!"))
            else:
                owner_list = re.split(",", owner_string)
                valid_owner_list = []
                already_owner_list = []
                for owner in owner_list:
                    try:
                        owner_object = User.objects.get(username = '%s@jabber.rwth-aachen.de' % owner)
                        if ownership.objects.filter(user=owner_object.id,group=group.id).count() == 0:
                            new_ownership = ownership(
                                group = group,
                                user = owner_object,
                            )
                            new_ownership.save()
                            valid_owner_list.append(owner)
                        else:
                            already_owner_list.append(owner)
                    except User.DoesNotExist:
                        messages.error(self.request, _("Invalid user in 'Add owners' field: '%(user)s'") % { 'user': owner })
                owner_string = ", ".join(valid_owner_list)
                if len(owner_string) > 0:
                    messages.success(self.request, _("The following owners have been added to the group: %(owner)s")
                        % { 'owner': owner_string })
                already_owner_string = ", ".join(already_owner_list)
                if len(already_owner_string) > 0:
                    messages.info(self.request, _("The following users have already been owners of the group: %(owner)s")
                        % { 'owner': already_owner_string })

        elif 'change_display' in self.request.POST:
            display_string = form.cleaned_data.get('display')
            if len(display_string) < 3:
                messages.error(self.request, _("Invalid input in 'Displayed to this group' field: groupname too short!"))
            else:
                display_list = re.split(",", display_string)
                valid_display_list = []
                invalid_display_list = []
                for display in display_list:
                    try:
                        display_object = Group.objects.get(name = display)
                        if display_object in user.owner.all() or user.is_superuser:
                            valid_display_list.append(display_object.name)
                        else:
                            invalid_display_list.append(display_object.name)
                    except Group.DoesNotExist:
                            invalid_display_list.append(display)
                valid_display_string = ", ".join(valid_display_list)
                if len(valid_display_string) > 0:
                    group.displayed_to = "\n".join(valid_display_list)
                    group.save()
                    messages.success(self.request, _("The following groups are now displayed to this group: %(display)s")
                        % { 'display': valid_display_string })
                invalid_display_string = ", ".join(invalid_display_list)
                if len(invalid_display_string) > 0:
                    messages.error(self.request, _("The following groups do not exist or do not belong to you: %(display)s")
                        % { 'display': invalid_display_string })

        elif 'update_description' in self.request.POST:
            group.description = form.cleaned_data.get('group_description')
            group.save()
            messages.success(self.request, _("The group description has been updated!") % { 'group': group.name })

        else:
            messages.error(self.request, _("Invalid POST action submitted!"))

        return HttpResponseRedirect(reverse('groups:edit', args=(group.id,)))


class DeleteView(LoginRequiredMixin, GroupPageMixin, GroupAuthMixin, DetailView):
    template_name = 'groups/delete.html'
    model = Group

    def post(self, request, *args, **kwargs):
        user = self.request.user
        group = get_object_or_404(Group, pk=self.kwargs['pk'])
        if group in user.owner.all():
            groupname = group.name
            group.delete()
            messages.success(self.request, _("The group '%(group)s' has been deleted.") % { 'group': groupname })
        else:
            messages.error(self.request, _("You are not an owner of this group so you cannot delete it!"))
        return HttpResponseRedirect(reverse('groups:ownership'))


def SyncView(request, action=None):
    user = request.user
    group_count = 0
    member_count = 0
    if not user.is_superuser:
        raise Http404("The requested URL " + request.path + " was not found on this server.")
    elif action == "to":
        for group in Group.objects.all():
            xmpp_backend.srg_delete(groupname=group.name, domain='jabber.rwth-aachen.de')
            group.save()
            group_count += 1
            for user in group.members.all():
                membership.objects.get(user=user.id,group=group.id).save()
                member_count += 1
        messages.success(request, _("Sync from Django to XMPP completed! Exported %(group)s groups and %(member)s memberships to ejabberd.")
            % { 'group': group_count, 'member': member_count })
        return HttpResponseRedirect(reverse('admin:groups_group_changelist'))
    elif action == "from":
        for group in xmpp_backend.srg_list(domain='jabber.rwth-aachen.de'):
            group_info = xmpp_backend.srg_get_info(groupname=group, domain='jabber.rwth-aachen.de')
            try:
                group_object = Group.objects.get(name = group)
                group_object.displayed_to = group_info[1]['value']
                group_object.description = group_info[2]['value']
                group_object.save_native()
            except Group.DoesNotExist:
                group_object = Group(
                    name = group,
                    displayed_to = group_info[1]['value'],
                    description = group_info[2]['value'],
                )
                group_object.save_native()
            group_count += 1
            for user in group_object.members.all():
                    membership.objects.filter(user=user.id,group=group_object.id).delete() 
            try:
                for user in xmpp_backend.srg_get_members(groupname=group, domain='jabber.rwth-aachen.de'):
                    try:
                        member_count += 1
                        member_object = User.objects.get(username=user)
                        if membership.objects.filter(user=member_object.id,group=group_object.id).count() == 0:
                            new_membership = membership(
                                group = group_object,
                                user = member_object,
                            )
                            new_membership.save_native()
                    except User.DoesNotExist:
                        pass
            except BackendError:
                messages.error(request, _("There was a BackendError when trying to get members of group '%(group)s' !") % { 'group': group })
        messages.success(request, _("Sync from XMPP to Django completed! Imported %(group)s groups and %(member)s memberships from ejabberd.")
            % { 'group': group_count, 'member': member_count })
        return HttpResponseRedirect(reverse('admin:groups_group_changelist'))
    else:
        raise Http404("The requested URL " + request.path + " was not found on this server.")
