from django import forms
from django.contrib import admin
from django.contrib import messages
from django.db import models
from django.utils.translation import ugettext_lazy as _

from account.models import User
from xmpp_backends.base import BackendError
from xmpp_backends.django import xmpp_backend

from .models import Group
from .models import membership
from .models import ownership

admin.site.disable_action('delete_selected')

class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={'rows':6, 'cols':98}),
            'displayed_to': forms.TextInput(attrs={'size':'100'}),
        }

class GroupAdmin(admin.ModelAdmin):
    form = GroupAdminForm
    list_display = ('name', 'description', 'id')
    fields = ('name', 'description', 'displayed_to')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('name',)
        return self.readonly_fields

    def sync_to_XMPP(modeladmin, request, queryset):
        for group in queryset:
            xmpp_backend.srg_delete(groupname=group.name, domain='jabber.rwth-aachen.de')
            group.save()
            for user in group.members.all():
                    membership.objects.get(user=user.id,group=group.id).save()
            messages.success(request, _("The group '%(group)s' has been synced from Django to ejabberd.") % { 'group': group.name })

    def sync_from_XMPP(modeladmin, request, queryset):
        for group in queryset:
            group_info = xmpp_backend.srg_get_info(groupname=group.name, domain='jabber.rwth-aachen.de')
            #group.displayed_to = group_info[1]['value']
            #group.description = group_info[2]['value']
            group.displayed_to = group_info['displayed_groups']
            group.description = group_info['description']
            group.save_native()
            for user in group.members.all():
                    membership.objects.get(user=user.id,group=group.id).delete_native()
            for user in xmpp_backend.srg_get_members(groupname=group.name, domain='jabber.rwth-aachen.de'):
                try:
                    member = User.objects.get(username=user)
                    new_membership = membership(group=group, user=member)
                    new_membership.save_native()
                except User.DoesNotExist:
                    pass
            messages.success(request, _("The group '%(group)s' has been synced from ejabberd to Django.") % { 'group': group.name })

    def delete(modeladmin, request, queryset):
        for obj in queryset:
            groupname = obj.name
            obj.delete()
            messages.success(request, _("The group '%(group)s' has been deleted.") % { 'group': groupname })

    sync_to_XMPP.short_description = _("Sync to XMPP")
    sync_from_XMPP.short_description = _("Sync from XMPP")
    delete.short_description = _("Delete")

    actions_on_top = True
    actions_on_bottom = True

    actions = [sync_to_XMPP, sync_from_XMPP, delete]
    
admin.site.register(Group, GroupAdmin)

class ShipAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'groupname', 'username')
    
    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('group', 'user')
        return self.readonly_fields

    def delete(modeladmin, request, queryset):
        for obj in queryset:
            objname = obj.__str__
            obj.delete()
            messages.success(request, _("The object '%(object)s' has been deleted.") % { 'object': obj })

    delete.short_description = _("Delete")

    actions_on_top = True
    actions_on_bottom = True

    actions = [delete]

admin.site.register(membership, ShipAdmin)
admin.site.register(ownership, ShipAdmin)
