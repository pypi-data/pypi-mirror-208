# -*- coding: utf-8 -*-

from Products.MeetingCPASLalouviere.tests.MeetingCPASLalouviereTestCase import (
    MeetingCPASLalouviereTestCase,
)
from Products.MeetingCommunes.tests.testCustomMeeting import testCustomMeetingType as mctcm


class testCustomMeetingType(mctcm, MeetingCPASLalouviereTestCase):
    """
        Tests the Meeting adapted methods
    """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomMeetingType, prefix='test_'))
    return suite
