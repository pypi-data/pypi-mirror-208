# -*- coding: utf-8 -*-
#
# File: testWorkflows.py
#
# Copyright (c) 2007-2010 by PloneGov
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

from Products.MeetingCPASLalouviere.tests.MeetingCPASLalouviereTestCase import MeetingCPASLalouviereTestCase
from Products.MeetingCommunes.tests.testWorkflows import testWorkflows as mctw

from AccessControl import Unauthorized
from Products.MeetingCPASLalouviere.config import LLO_APPLYED_CPAS_WFA

from Products.CMFCore.permissions import ModifyPortalContent


class testWorkflows(MeetingCPASLalouviereTestCase, mctw):

    def _check_users_can_modify(self, item, users=None, annex=None):
        if users is None:
            users = [self.member.id]
        for user_id in users:
            self.changeUser(user_id)
            if annex is None:
                self.failUnless(self.hasPermission(ModifyPortalContent, item))
            else:
                self.failUnless(self.hasPermission(ModifyPortalContent, (item, annex)))

    def test_pm_WholeDecisionProcess(self):
        """
            This test covers the whole decision workflow. It begins with the
            creation of some items, and ends by closing a meeting.
            This call sub test for each process : BP and CAS (same wf)
        """
        self._testWholeDecisionProcessCollege()

    def _testWholeDecisionProcessCollege(self):
        '''This test covers the whole decision workflow. It begins with the
           creation of some items, and ends by closing a meeting.'''
        # pmCreator1 creates an item with 1 annex and proposes it
        self._activate_wfas(LLO_APPLYED_CPAS_WFA)
        self.meetingConfig.setItemAdviceStates(("itemcreated_waiting_advices",))
        self.meetingConfig.setItemAdviceEditStates(("itemcreated_waiting_advices",))
        self.changeUser('pmCreator1')
        item1 = self.create('MeetingItem')
        item1.setOptionalAdvisers((self.vendors_uid,))
        item1._update_after_edit()
        self.addAnnex(item1)
        self.addAnnex(item1, relatedTo='item_decision')
        self.do(item1, "wait_advices_from_itemcreated")
        self.assertEqual("itemcreated_waiting_advices", item1.query_state())
        self.do(item1, "backTo_itemcreated_from_waiting_advices")
        self.do(item1, "proposeToBudgetImpactReviewer")
        self.assertEqual("proposed_to_budget_reviewer", item1.query_state())
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission("PloneMeeting: Add annex", item1))
        self.changeUser("pmBudgetReviewer1")
        self._check_users_can_modify(item1)
        self.do(item1, "backTo_itemcreated_from_proposed_to_budget_reviewer")
        self.assertEqual("itemcreated", item1.query_state())
        self.changeUser("pmCreator1")
        self.do(item1, 'proposeToN1')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the N1 validation level
        self.changeUser('pmN1')
        self._check_users_can_modify(item1)
        self.do(item1, 'proposeToN2')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the N2 validation level
        self.changeUser('pmN2')
        self._check_users_can_modify(item1)
        self.do(item1, 'proposeToSecretaire')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the secretariat validation level
        self.changeUser('pmSecretaire')
        self._check_users_can_modify(item1)
        self.do(item1, 'proposeToPresident')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # the president validation level
        self.changeUser('pmPresident')
        self._check_users_can_modify(item1)
        self.do(item1, 'validate')
        self.failIf(self.transitions(item1))  # He may trigger no more action
        self.failIf(self.hasPermission('PloneMeeting: Add annex', item1))
        # pmManager creates a meeting
        self.changeUser('pmManager')
        meeting = self.create('Meeting')
        self.addAnnex(item1, relatedTo='item_decision')
        # pmCreator2 creates and proposes an item
        self.changeUser('pmCreator2')
        item2 = self.create('MeetingItem', title='The second item',
                            preferredMeeting=meeting.UID())
        self.do(item2, 'proposeToN1')
        # pmReviewer1 validates item1 and adds an annex to it
        self.changeUser('pmPresident')
        self.failIf(self.hasPermission('Modify portal content', item2))
        self.changeUser('pmManager')
        # pmManager inserts item1 into the meeting and publishes it
        managerAnnex = self.addAnnex(item1)
        self.portal.restrictedTraverse('@@delete_givenuid')(managerAnnex.UID())
        self.do(item1, 'present')
        self.changeUser('pmManager')
        self.do(meeting, 'freeze')
        # validate item2 after meeting freeze
        self.changeUser('pmReviewer2')
        self.do(item2, 'validate')
        self.changeUser('pmManager')
        self.do(item2, 'present')
        self.addAnnex(item2)
        # So now we should have 3 normal item (2 recurring + 1) and one late item in the meeting
        self.failUnless(len(meeting.get_items()) == 4)
        self.failUnless(len(meeting.get_items(list_types=['late'])) == 1)
        self.do(meeting, 'decide')
        self.do(item1, 'refuse')
        self.assertEquals(item1.query_state(), 'refused')
        self.assertEquals(item2.query_state(), 'itemfrozen')
        self.assertListEqual(self.transitions(item2),
                             ['accept', 'accept_but_modify', 'backToPresented', 'delay', 'postpone_next_meeting',
                              'pre_accept', 'refuse',
                              'remove', 'return_to_proposing_group'])
        self.do(meeting, 'close')
        self.assertEquals(item1.query_state(), 'refused')
        # every items without a decision are automatically accepted
        self.assertEquals(item2.query_state(), 'accepted')


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testWorkflows, prefix='test_pm_'))
    return suite
