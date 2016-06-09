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

from django.utils.translation import ugettext_lazy as _


REGISTRATION_WEBSITE = 0
REGISTRATION_INBAND = 1
REGISTRATION_MANUAL = 2
REGISTRATION_UNKNOWN = 9

TARGET_URL = 0
TARGET_NAMED_URL = 1
TARGET_PAGE = 2
TARGET_BLOGPOST = 3
TARGET_CHOICES = {
    TARGET_URL: _('URL'),
#    TARGET_NAMED_URL: _('Named URL'),
    TARGET_PAGE: _('Page'),
#    TARGET_BLOGPOST: _('Blog Post'),
}