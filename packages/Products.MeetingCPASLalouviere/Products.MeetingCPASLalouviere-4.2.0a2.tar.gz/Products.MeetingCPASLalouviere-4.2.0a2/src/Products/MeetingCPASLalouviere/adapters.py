# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
# File: adapters.py
#
# Copyright (c) 2014 by Imio.be
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
# ------------------------------------------------------------------------------
from copy import deepcopy
from Products.MeetingCommunes.adapters import CustomToolPloneMeeting, CustomMeetingConfig, \
    MeetingItemCommunesWorkflowActions
from Products.MeetingCommunes.interfaces import IMeetingItemCommunesWorkflowActions
from Products.PloneMeeting.interfaces import IToolPloneMeetingCustom, IMeetingConfigCustom
from Products.PloneMeeting.model import adaptations
from Products.PloneMeeting.MeetingConfig import MeetingConfig
from Products.PloneMeeting.model.adaptations import _addIsolatedState


from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from collections import OrderedDict
from collective.contact.plonegroup.utils import get_all_suffixes
from zope.interface import implements
from zope.i18n import translate


customWfAdaptations = list(deepcopy(MeetingConfig.wfAdaptations))
customWfAdaptations.append('propose_to_budget_reviewer')
# disable not compatible waiting advice wfa
# customWfAdaptations.remove('waiting_advices_adviser_may_validate')
# customWfAdaptations.remove('waiting_advices_from_before_last_val_level')
# customWfAdaptations.remove('waiting_advices_from_every_val_levels')
# customWfAdaptations.remove('waiting_advices_from_last_val_level')
# customWfAdaptations.remove('waiting_advices_given_advices_required_to_validate')
# customWfAdaptations.remove('waiting_advices_given_and_signed_advices_required_to_validate')
MeetingConfig.wfAdaptations = tuple(customWfAdaptations)

class LLMeetingConfig(CustomMeetingConfig):
    """Adapter that adapts a meetingConfig implementing IMeetingConfig to the
       interface IMeetingConfigCustom."""

    implements(IMeetingConfigCustom)
    security = ClassSecurityInfo()

    def _extraSearchesInfo(self, infos):
        """Add some specific searches."""
        super(LLMeetingConfig, self)._extraSearchesInfo(infos)
        cfg = self.getSelf()
        itemType = cfg.getItemTypeName()
        extra_infos = [
            (
                "searchproposedtobudgetreviewer",
                {
                    "subFolderId": "searches_items",
                    "active": True,
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": [itemType, ],
                        },
                        {
                            "i": "review_state",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": ["proposed_to_budget_reviewer"],
                        },
                    ],
                    "sort_on": u"modified",
                    "sort_reversed": True,
                    "showNumberOfItems": True,
                    "tal_condition": "",
                    "roles_bypassing_talcondition": ["Manager", ],
                },
            ),
            (
                "searchproposedton1",
                {
                    "subFolderId": "searches_items",
                    "active": True,
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": [itemType, ],
                        },
                        {
                            "i": "review_state",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": ["proposed_to_n1"],
                        },
                    ],
                    "sort_on": u"modified",
                    "sort_reversed": True,
                    "showNumberOfItems": True,
                    "tal_condition": "python:tool.userIsAmong(['n1', 'n2', 'secretaire', 'president'])",
                    "roles_bypassing_talcondition": ["Manager", ],
                },
            ),
            (
                "searchproposedton2",
                {
                    "subFolderId": "searches_items",
                    "active": True,
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": [itemType, ],
                        },
                        {
                            "i": "review_state",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": ["proposed_to_n2"],
                        },
                    ],
                    "sort_on": u"modified",
                    "sort_reversed": True,
                    "showNumberOfItems": True,
                    "tal_condition": "python:tool.userIsAmong(['n2', 'secretaire', 'president'])",
                    "roles_bypassing_talcondition": ["Manager", ],
                },
            ),
            (
                "searchproposedtosecretaire",
                {
                    "subFolderId": "searches_items",
                    "active": True,
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": [itemType, ],
                        },
                        {
                            "i": "review_state",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": ["proposed_to_secretaire"],
                        },
                    ],
                    "sort_on": u"modified",
                    "sort_reversed": True,
                    "showNumberOfItems": True,
                    "tal_condition": "python:tool.userIsAmong(['secretaire', 'president'])",
                    "roles_bypassing_talcondition": ["Manager", ],
                },
            ),
            (
                "searchproposedtopresident",
                {
                    "subFolderId": "searches_items",
                    "active": True,
                    "query": [
                        {
                            "i": "portal_type",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": [itemType, ],
                        },
                        {
                            "i": "review_state",
                            "o": "plone.app.querystring.operation.selection.is",
                            "v": ["proposed_to_president"],
                        },
                    ],
                    "sort_on": u"modified",
                    "sort_reversed": True,
                    "showNumberOfItems": True,
                    "tal_condition": "python:tool.userIsAmong(['president'])",
                    "roles_bypassing_talcondition": ["Manager", ],
                },
            ),
        ]
        infos.update(OrderedDict(extra_infos))
        return infos

    def _custom_reviewersFor(self):
        '''Manage reviewersFor Bourgmestre because as some 'creators' suffixes are
           used after reviewers levels, this break the _highestReviewerLevel and other
           related hierarchic level functionalities.'''
        reviewers = [
            ('president', ['proposed_to_president',
                           'proposed_to_secretaire',
                           'proposed_to_n2',
                           'proposed_to_n1',
                           ]),
            ('secretaire',
             ['proposed_to_secretaire',
              'proposed_to_n2',
              'proposed_to_n1',]),
            ('n2',
             ['proposed_to_n2',
              'proposed_to_n1',]),
            ('n1',
             ['proposed_to_n1',]),
        ]
        return OrderedDict(reviewers)

    def get_item_custom_suffix_roles(self, item, item_state):
        '''See doc in interfaces.py.'''
        suffix_roles = {}
        if item_state == 'proposed_to_budget_reviewer':
            for suffix in get_all_suffixes(item.getProposingGroup()):
                suffix_roles[suffix] = ['Reader']
                if suffix == 'budgetimpactreviewers':
                    suffix_roles[suffix] += ['Contributor', 'Editor', 'Reviewer']

        return True, suffix_roles


class MLLCustomToolPloneMeeting(CustomToolPloneMeeting):
    '''Adapter that adapts portal_plonemeeting.'''

    implements(IToolPloneMeetingCustom)
    security = ClassSecurityInfo()

    def performCustomWFAdaptations(
            self, meetingConfig, wfAdaptation, logger, itemWorkflow, meetingWorkflow):
        ''' '''
        if wfAdaptation == 'propose_to_budget_reviewer':
            _addIsolatedState(
                new_state_id='proposed_to_budget_reviewer',
                origin_state_id='itemcreated',
                origin_transition_id='proposeToBudgetImpactReviewer',
                origin_transition_title=translate("proposeToBudgetImpactReviewer", "plone"),
                # origin_transition_icon=None,
                origin_transition_guard_expr_name='mayCorrect()',
                back_transition_guard_expr_name="mayCorrect()",
                back_transition_id='backTo_itemcreated_from_proposed_to_budget_reviewer',
                back_transition_title=translate("validateByBudgetImpactReviewer", "plone"),
                # back_transition_icon=None
                itemWorkflow=itemWorkflow)
            return True
        return False


class MeetingItemMLLWorkflowActions(MeetingItemCommunesWorkflowActions):
    '''Adapter that adapts a meeting item implementing IMeetingItem to the
       interface IMeetingItemCommunesWorkflowActions'''

    implements(IMeetingItemCommunesWorkflowActions)
    security = ClassSecurityInfo()

    def doProposeToBudgetImpactReviewer(self, stateChange):
        pass


InitializeClass(MLLCustomToolPloneMeeting)
InitializeClass(LLMeetingConfig)

LLO_WAITING_ADVICES_FROM_STATES = {
    '*':
    (
        {'from_states': ('itemcreated', ),
         'back_states': ('itemcreated', ),
         'perm_cloned_state': 'itemcreated',
         'use_custom_icon': False,
         # default to "validated", this avoid using the backToValidated title that
         # is translated to "Remove from meeting"
         'use_custom_back_transition_title_for': ("validated", ),
         # we can define some back transition id for some back_to_state
         # if not, a generated transition is used, here we could have for example
         # 'defined_back_transition_ids': {"validated": "validate"}
         'defined_back_transition_ids': {},
         # if () given, a custom transition icon is used for every back transitions
         'only_use_custom_back_transition_icon_for': ("validated", ),
         'use_custom_state_title': False,
         'use_custom_transition_title_for': {},
         'remove_modify_access': True,
         'adviser_may_validate': True,
         # must end with _waiting_advices
         'new_state_id': None,
         },
        {'from_states': ('proposed_to_president', ),
         'back_states': ('proposed_to_president', ),
         'perm_cloned_state': 'validated',
         'use_custom_icon': False,
         # default to "validated", this avoid using the backToValidated title that
         # is translated to "Remove from meeting"
         'use_custom_back_transition_title_for': ("validated", ),
         # we can define some back transition id for some back_to_state
         # if not, a generated transition is used, here we could have for example
         # 'defined_back_transition_ids': {"validated": "validate"}
         'defined_back_transition_ids': {},
         # if () given, a custom transition icon is used for every back transitions
         'only_use_custom_back_transition_icon_for': ("validated", ),
         'use_custom_state_title': True,
         'use_custom_transition_title_for': {},
         'remove_modify_access': True,
         'adviser_may_validate': False,
         # must end with _waiting_advices
         'new_state_id': None,
         },
    ),
}
adaptations.WAITING_ADVICES_FROM_STATES.update(LLO_WAITING_ADVICES_FROM_STATES)