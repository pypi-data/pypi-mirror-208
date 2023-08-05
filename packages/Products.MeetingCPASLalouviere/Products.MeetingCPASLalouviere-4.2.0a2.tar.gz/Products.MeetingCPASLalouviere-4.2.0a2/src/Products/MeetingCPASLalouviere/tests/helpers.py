# -*- coding: utf-8 -*-
#
# Copyright (c) 2013 by Imio.be
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

from Products.MeetingCommunes.tests.helpers import MeetingCommunesTestingHelpers


class MeetingCPASLalouviereTestingHelpers(MeetingCommunesTestingHelpers):
    '''Override some values of MeetingCommunesTestingHelpers.'''

    TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_1 = TRANSITIONS_FOR_PROPOSING_ITEM_FIRST_LEVEL_2 = ("proposeToN1",)
    TRANSITIONS_FOR_PROPOSING_ITEM_1 = TRANSITIONS_FOR_PROPOSING_ITEM_2 = ('proposeToN1',
                                                                           'proposeToN2',
                                                                           'proposeToSecretaire',
                                                                           'proposeToPresident',)
    TRANSITIONS_FOR_VALIDATING_ITEM_1 = TRANSITIONS_FOR_VALIDATING_ITEM_2 = ('proposeToN1',
                                                                             'proposeToN2',
                                                                             'proposeToSecretaire',
                                                                             'proposeToPresident',
                                                                             'validate',)
    TRANSITIONS_FOR_PRESENTING_ITEM_1 = TRANSITIONS_FOR_PRESENTING_ITEM_2 = ('proposeToN1',
                                                                             'proposeToN2',
                                                                             'proposeToSecretaire',
                                                                             'proposeToPresident',
                                                                             'validate',
                                                                             'present',)
    BACK_TO_WF_PATH_1 = BACK_TO_WF_PATH_2 = {
        # Meeting
        "created": ("backToDecided", "backToPublished", "backToFrozen", "backToCreated",),
        # MeetingItem
        "itemcreated": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToProposedToPresident",
            "backToProposedToSecretaire",
            "backToProposedToN2",
            "backToProposedToN1",
            "backToItemCreated",
        ),
        "proposed_to_n1": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToProposedToPresident",
            "backToProposedToSecretaire",
            "backToProposedToN2",
            "backToProposedToN1",
        ),
        "proposed_to_n2": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToProposedToPresident",
            "backToProposedToSecretaire",
            "backToProposedToN2",
        ),
        "proposed_to_secretaire": (
            "backToItemFrozen",
            "backToPresented",
            "backToValidated",
            "backToProposedToPresident",
            "backToProposedToSecretaire",
        ),
        "proposed_to_president": ("backToItemFrozen", "backToPresented", "backToValidated", "backToProposedToPresident"),
        "validated": ("backToItemFrozen", "backToPresented", "backToValidated",),
    }

    WF_ITEM_STATE_NAME_MAPPINGS_1 = WF_ITEM_STATE_NAME_MAPPINGS_2 = {
        "itemcreated": "itemcreated",
        "proposed_first_level": "proposed_to_n1",
        "proposed": "proposed_to_president",
        "validated": "validated",
        "presented": "presented",
        "itemfrozen": "itemfrozen",
    }

    def _enablePrevalidation(self, cfg, enable_extra_suffixes=False):
        if self._testMethodName in ('test_pm_WFA_waiting_advices_with_prevalidation',):
            super(MeetingCPASLalouviereTestingHelpers, self)._enablePrevalidation(cfg, enable_extra_suffixes)
        cfg.at_post_edit_script()

    def _enable_mc_Prevalidation(self, cfg, enable_extra_suffixes=False):
        self._setUpDefaultItemWFValidationLevels(cfg)
        super(MeetingCPASLalouviereTestingHelpers, self)._enablePrevalidation(cfg, enable_extra_suffixes)