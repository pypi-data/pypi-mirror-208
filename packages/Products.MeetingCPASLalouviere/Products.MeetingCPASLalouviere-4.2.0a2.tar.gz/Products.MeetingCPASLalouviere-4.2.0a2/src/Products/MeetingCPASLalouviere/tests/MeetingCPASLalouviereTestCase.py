# -*- coding: utf-8 -*-
#
# Copyright (c) 2008-2010 by PloneGov
#
# GNU General Public License (GPL)
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#

from Products.MeetingCPASLalouviere.testing import MLL_TESTING_PROFILE_FUNCTIONAL
from Products.MeetingCPASLalouviere.tests.helpers import MeetingCPASLalouviereTestingHelpers
from Products.MeetingCommunes.tests.MeetingCommunesTestCase import MeetingCommunesTestCase


class MeetingCPASLalouviereTestCase(
    MeetingCommunesTestCase, MeetingCPASLalouviereTestingHelpers
):
    """Base class for defining MeetingCPASLalouviere test cases."""

    layer = MLL_TESTING_PROFILE_FUNCTIONAL
    cfg1_id = 'meeting-config-bp'
    cfg2_id = 'meeting-config-cas'

    def setUp(self):
        super(MeetingCPASLalouviereTestCase, self).setUp()
