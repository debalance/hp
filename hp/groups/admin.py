from django.contrib import admin
from .models import Group, ownership, membership

#admin.site.register(ownership)
#admin.site.register(membership)

class membershipInLine(admin.StackedInline):
    model = membership
    extra = 10

class ownershipInLine(admin.StackedInline):
    model = ownership
    extra = 2

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'displayed_to')
    inlines = [membershipInLine, ownershipInLine]

admin.site.register(Group, GroupAdmin)
