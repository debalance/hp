from django.contrib import admin
from .models import Group, ownership, membership

class membershipInLine(admin.StackedInline):
    model = membership
    extra = 10

class ownershipInLine(admin.StackedInline):
    model = ownership
    extra = 2

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'displayed_to')
    inlines = [membershipInLine, ownershipInLine]
    def sync_from_XMPP(modeladmin, request, queryset):
        pass #TODO
    def sync_to_XMPP(modeladmin, request, queryset):
        pass #TODO
    actions = [sync_from_XMPP, sync_to_XMPP]

admin.site.register(Group, GroupAdmin)
admin.site.disable_action('delete_selected')
