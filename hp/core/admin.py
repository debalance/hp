# -*- coding: utf-8 -*-
#
# This file is part of the jabber.at homepage (https://github.com/jabber-at/hp).
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with django-xmpp-account.
# If not, see <http://www.gnu.org/licenses/.

from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from composite_field.l10n import LocalizedField
from composite_field.base import CompositeField
from mptt.admin import DraggableMPTTAdmin
from tinymce.widgets import TinyMCE

from .models import Address
from .models import AddressActivity
from .models import BlogPost
from .models import Page
from .models import MenuItem

User = get_user_model()


class BaseModelAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        fields = list(super(BaseModelAdmin, self).get_readonly_fields(request, obj=obj))

        if obj is not None:
            if 'updated' not in fields:
                fields.append('updated')
            if 'created' not in fields:
                fields.append('created')
        return fields

    def get_fields(self, request, obj=None):
        fields = list(super(BaseModelAdmin, self).get_fields(request, obj=obj))

        if obj is not None:
            if 'updated' not in fields:
                fields.append('updated')
            if 'created' not in fields:
                fields.append('created')

        return fields


class BasePageAdmin(BaseModelAdmin):
    formfield_overrides = {
        models.TextField: {
            'widget': TinyMCE(attrs={'cols': 80, 'rows': 20}, mce_attrs={
                'theme': "advanced",
            }),
        },
    }

    def get_fields(self, request, obj=None):
        fields = list(super(BasePageAdmin, self).get_fields(request, obj=obj))
        if obj is not None and 'author' not in fields:
            fields.append('author')
        return fields

    def get_readonly_fields(self, request, obj=None):
        fields = list(super(BasePageAdmin, self).get_readonly_fields(request, obj=obj))
        if obj is not None and 'author' not in fields:
            fields.append('author')
        return fields

    def get_actions(self, request):
        actions = super(BasePageAdmin, self).get_actions(request)

        context = {
            'models': self.model._meta.verbose_name_plural,
        }

        actions['make_publish'] = (
            self.make_publish, 'make_publish', self.make_publish.short_description % context,
        )
        actions['make_unpublish'] = (
            self.make_unpublish, 'make_unpublish', self.make_unpublish.short_description % context,
        )
        return actions

    def _get_composite_field_tuple(self, fields):
        new_fields = []
        for name in fields:
            if not isinstance(name, str):  # don't handle tuples et al
                new_fields.append(name)
                continue

            field = self.model._meta.get_field(name)

            if isinstance(field, LocalizedField):
                new_fields.append(tuple([f.name for f in field.subfields.values()]))
            elif isinstance(field, CompositeField):
                new_fields += [f.name for f in field.subfields.values()]
            else:
                new_fields.append(name)
        return new_fields

    def _get_subfields(self, name):
        return tuple([f.name for f in self.model._meta.get_field(name).subfields.values()])

    def get_fieldsets(self, request, obj=None):
        fieldsets = super(BasePageAdmin, self).get_fieldsets(request, obj=obj)

        if self.fieldsets is None and self.fields is None:
            # The ModelAdmin class doesn't set fields or fieldsets - we replace localized
            # fields with tuples.
            fields = []
            has_title = has_slug = has_text = False
            title_fields = self._get_subfields('title')
            slug_fields = self._get_subfields('slug')
            text_fields = self._get_subfields('text')
            for field in fieldsets[0][1]['fields']:
                if field in title_fields:
                    if has_title is False:
                        fields.append(title_fields)
                        has_title = True
                elif field in slug_fields:
                    if has_slug is False:
                        fields.append(slug_fields)
                        has_slug = True
                elif field in text_fields:
                    if has_text is False:
                        fields.append(text_fields)
                        has_text = True
                else:
                    fields.append(field)

            fieldsets[0][1]['fields'] = list(fields)
        else:
            # ModelAdmin sets fields or fieldsets. This means that e.g. 'title' should
            # be replaced with ('title_de', 'title_en').
            for name, options in fieldsets:
                options['fields'] = self._get_composite_field_tuple(options['fields'])

        return fieldsets

    def render_change_form(self, request, context, add, **kwargs):
        """Override to add javascript only when adding an object.

        It adds Javascript to dynamically calculate the slug of a BasePage object and set the field
        accordingly.

        Ordinarily you would add Javascript in a Media subclass, but then it would get *always*
        added. The form for adding/changing an object is identical, so there is no way to only
        act when adding a form (and you don't normally want to change existing slugs, since they're
        part of the URL).
        """

        if add:
            context['media'] += forms.Media(js=("core/js/basepage-add.js", ))
        return super(BasePageAdmin, self).render_change_form(request, context, add, **kwargs)

    def save_model(self, request, obj, form, change):
        if change is False:  # adding a new object
            obj.author = request.user
        obj.save()

    #################
    # Admin actions #
    #################
    def make_publish(self, request, queryset):
        queryset.update(published=True)
    make_publish.short_description = _('Publish selected %(models)s')

    def make_unpublish(self, request, queryset):
        queryset.update(published=False)
    make_unpublish.short_description = _('Unpublish selected %(models)s')

    class Media:
        css = {
            'all': ('core/admin/css/basepage.css', ),
        }


class AuthorFilter(admin.SimpleListFilter):
    title = _('Author')
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        qs = User.objects.annotate(num_posts=models.Count('blogpost')).filter(num_posts__gt=1)
        return [(u.pk, u.username) for u in qs]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(author_id=self.value())


@admin.register(BlogPost)
class BlogPostAdmin(BasePageAdmin):
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'text'),
        }),
        (_('Descriptions'), {
            'fields': ('meta_summary', 'twitter_summary', 'opengraph_summary', 'html_summary', ),
            'description': _('Descriptions are used by various systems (RSS readers, Facebook, '
                             '...) to generate previous of this content.'),
            'classes': ('description', ),
        }),
        (_('Meta'), {
            'fields': (('published', 'sticky'), ),
        }),
    )
    list_display = ['__str__', 'created', ]
    list_filter = [AuthorFilter, 'published', 'sticky', ]
    ordering = ('sticky', '-created', )
    search_fields = ['title_de', 'title_en', 'text_en', 'text_de']


@admin.register(Page)
class PageAdmin(BasePageAdmin):
    fields = ['title', 'slug', 'text', 'published', ]
    ordering = ('-title', )
    search_fields = ['title_de', 'title_en', 'text_en', 'text_de']


@admin.register(MenuItem)
class MenuItemAdmin(DraggableMPTTAdmin):
    list_display = (
        'tree_actions',
        'indented_title',
    )
    list_display_links = (
        'indented_title',
    )


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('address', 'count_activities', 'count_confirmations', 'timerange', )
    search_fields = ['address']

    def get_queryset(self, request):
        qs = super(AddressAdmin, self).get_queryset(request)
        # NOTE: We add ordering here because the system check framework checks that each name given
        #       in the "ordering" class property is actually a model field.
        return qs.count_activities().count_confirmations()\
            .first_activity().last_activity().order_by('-count_activities')

    def timerange(self, obj):
        if obj.count_activities <= 1:
            return '-'
        diff = obj.last_activity - obj.first_activity
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        obj.timerange = diff

        return '%s days, %s:%s:%s' % (diff.days, hours, minutes, seconds)
    timerange.short_description = _('Timerange of activities')

    def count_activities(self, obj):
        return obj.count_activities
    count_activities.short_description = _('Number of activities')
    count_activities.admin_order_field = 'count_activities'

    def count_confirmations(self, obj):
        return obj.count_confirmations
    count_confirmations.short_description = _('Number of confirmations')
    count_confirmations.admin_order_field = 'count_confirmations'


@admin.register(AddressActivity)
class AddressActivityAdmin(admin.ModelAdmin):
    list_filter = ('activity', )
    list_display = ('address', 'activity', 'user', 'note', 'timestamp', )
    list_select_related = ('user', 'address', )
    ordering = ('-timestamp', )
    search_fields = ['user__username', 'address__address', 'note', ]
