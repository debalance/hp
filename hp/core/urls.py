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
# If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = 'core'
urlpatterns = [
    url(_(r'contact/$'), views.ContactView.as_view(), name='contact'),
    url(r'b/(?P<slug>[a-z0-9-_äöüß]+)/$', views.BlogPostView.as_view(), name='blogpost'),
    url(r'(?P<slug>[a-z0-9-_äöüß]+)/$', views.PageView.as_view(), name='page'),
    url(r'^$', views.BlogPostListView.as_view(), name='home'),
]
