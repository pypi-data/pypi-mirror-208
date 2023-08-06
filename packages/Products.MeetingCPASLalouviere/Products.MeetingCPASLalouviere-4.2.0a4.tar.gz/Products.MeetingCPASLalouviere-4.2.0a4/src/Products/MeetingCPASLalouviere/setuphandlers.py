# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2016 by Imio.be
# Generator: ArchGenXML Version 2.7
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

import logging
import os
from imio.helpers.catalog import addOrUpdateIndexes
from Products.MeetingCPASLalouviere.config import PROJECTNAME
from Products.PloneMeeting.exportimport.content import ToolInitializer

logger = logging.getLogger('MeetingCPASLalouviere: setuphandlers')


def isNotMeetingCPASLalouviereProfile(context):
    return context.readDataFile("MeetingCPASLalouviere_marker.txt") is None


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotMeetingCPASLalouviereProfile(context):
        return
    logStep("postInstall", context)
    site = context.getSite()
    # need to reinstall PloneMeeting after reinstalling MC workflows to re-apply wfAdaptations
    reinstallPloneMeeting(context, site)
    # Add additional indexes
    showHomeTab(context, site)
    reorderSkinsLayers(context, site)


def logStep(method, context):
    logger.info("Applying '%s' in profile '%s'" %
                (method, '/'.join(context._profile_path.split(os.sep)[-3:])))


def isMeetingCPASLalouviereConfigureProfile(context):
    return context.readDataFile("MeetingCPASLalouviere_lalouviere_marker.txt") or \
        context.readDataFile("MeetingCPASLalouviere_testing_marker.txt")


def installMeetingCPASLalouviere(context):
    """ Run the default profile"""
    if not isMeetingCPASLalouviereConfigureProfile(context):
        return
    logStep("installMeetingCPASLalouviere", context)
    portal = context.getSite()
    portal.portal_setup.runAllImportStepsFromProfile('profile-Products.MeetingCPASLalouviere:default')


def initializeTool(context):
    '''Initialises the PloneMeeting tool based on information from the current
       profile.'''
    if not isMeetingCPASLalouviereConfigureProfile(context):
        return

    logStep("initializeTool", context)
    # PloneMeeting is no more a dependency to avoid
    # magic between quickinstaller and portal_setup
    # so install it manually
    _installPloneMeeting(context)
    return ToolInitializer(context, PROJECTNAME).run()


def reinstallPloneMeeting(context, site):
    '''Reinstall PloneMeeting so after install methods are called and applied,
       like performWorkflowAdaptations for example.'''

    if isNotMeetingCPASLalouviereProfile(context):
        return

    logStep("reinstallPloneMeeting", context)
    _installPloneMeeting(context)


def _installPloneMeeting(context):
    site = context.getSite()
    profileId = u'profile-Products.PloneMeeting:default'
    site.portal_setup.runAllImportStepsFromProfile(profileId)


def showHomeTab(context, site):
    """
       Make sure the 'home' tab is shown...
    """
    if isNotMeetingCPASLalouviereProfile(context):
        return

    logStep("showHomeTab", context)

    index_html = getattr(site.portal_actions.portal_tabs, 'index_html', None)
    if index_html:
        index_html.visible = True
    else:
        logger.info("The 'Home' tab does not exist !!!")


def reorderSkinsLayers(context, site):
    """
       Re-apply MeetingCPASLalouviere skins.xml step as the reinstallation of
       MeetingCPASLalouviere and PloneMeeting changes the portal_skins layers order
    """
    if isNotMeetingCPASLalouviereProfile(context) and not isMeetingCPASLalouviereConfigureProfile(context):
        return

    logStep("reorderSkinsLayers", context)
    site.portal_setup.runImportStepFromProfile(u'profile-Products.MeetingCPASLalouviere:default', 'skins')


def reorderCss(context):
    """
       Make sure CSS are correctly reordered in portal_css so things
       work as expected...
    """
    if isNotMeetingCPASLalouviereProfile(context) and \
       not isMeetingCPASLalouviereConfigureProfile(context):
        return

    site = context.getSite()

    logStep("reorderCss", context)

    portal_css = site.portal_css
    css = ['plonemeeting.css',
           'meeting.css',
           'meetingitem.css',
           'meetingcpaslalouviere.css',
           'imioapps.css',
           'plonemeetingskin.css',
           'imioapps_IEFixes.css',
           'ploneCustom.css']
    for resource in css:
        portal_css.moveResourceToBottom(resource)
