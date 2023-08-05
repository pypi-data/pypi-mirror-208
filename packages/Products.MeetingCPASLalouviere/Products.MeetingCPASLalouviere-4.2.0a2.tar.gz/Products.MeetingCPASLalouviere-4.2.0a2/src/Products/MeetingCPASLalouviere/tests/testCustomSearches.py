from Products.MeetingCPASLalouviere.tests.MeetingCPASLalouviereTestCase import (
    MeetingCPASLalouviereTestCase,
)


class testCustomSearches(MeetingCPASLalouviereTestCase):
    """
    """


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCustomSearches, prefix='test_'))
    return suite
