# -*- coding: utf-8 -*-

from Products.MeetingCPASLalouviere.tests.MeetingCPASLalouviereTestCase import (
    MeetingCPASLalouviereTestCase,
)
from Products.MeetingCommunes.tests.testCustomViews import testCustomViews as mctcv


class testCustomViews(mctcv, MeetingCPASLalouviereTestCase):
    """
        Tests the custom views
    """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomViews, prefix="test_"))
    return suite
