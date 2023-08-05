# -*- coding: utf-8 -*-

from Products.MeetingCPASLalouviere.tests.MeetingCPASLalouviereTestCase import MeetingCPASLalouviereTestCase
from Products.MeetingCommunes.tests.testCustomWFAdaptations import testCustomWFAdaptations as mctcwfa


class testCustomWFAdaptations(mctcwfa, MeetingCPASLalouviereTestCase):
    ''' '''


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomWFAdaptations, prefix='test_'))
    return suite