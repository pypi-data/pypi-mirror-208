# -*- coding: utf-8 -*-

from copy import deepcopy
from Products.PloneMeeting.profiles import UserDescriptor
from Products.PloneMeeting.profiles.testing import import_data as pm_import_data
from Products.MeetingCommunes.profiles.testing import import_data as mc_import_data

from Products.MeetingCPASLalouviere.config import LLO_ITEM_CPAS_WF_VALIDATION_LEVELS

data = deepcopy(mc_import_data.data)

# Inherited users
pmReviewer1 = pm_import_data.pmReviewer1
pmReviewer2 = pm_import_data.pmReviewer2
pmReviewerLevel1 = pm_import_data.pmReviewerLevel1
pmReviewerLevel2 = pm_import_data.pmReviewerLevel2
pmManager = pm_import_data.pmManager
# xxx specific to CPAS La louvière
pmN1 = UserDescriptor('pmN1', [])
pmN2 = UserDescriptor('pmN2', [])
pmSecretaire = UserDescriptor('pmSecretaire', [])
pmPresident = UserDescriptor('pmPresident', [])

pmBudgetReviewer1 = UserDescriptor("pmBudgetReviewer1", [])
pmBudgetReviewer2 = UserDescriptor("pmBudgetReviewer2", [])

developers = data.orgs[0]
developers.budgetimpactreviewers.append(pmManager)
developers.budgetimpactreviewers.append(pmBudgetReviewer1)
developers.n1.append(pmReviewerLevel1)
developers.n1.append(pmN1)
developers.n2.append(pmN2)
developers.n2.append(pmManager)
developers.secretaire.append(pmSecretaire)
developers.secretaire.append(pmManager)
developers.president.append(pmReviewer1)
developers.president.append(pmReviewerLevel2)
developers.president.append(pmManager)
developers.president.append(pmPresident)

vendors = data.orgs[1]
vendors.budgetimpactreviewers.append(pmBudgetReviewer2)
vendors.n1.append(pmReviewerLevel1)
vendors.secretaire.append(pmSecretaire)
vendors.president.append(pmReviewerLevel2)
vendors.president.append(pmReviewer2)

# Meeting configurations -------------------------------------------------------
# College communal
bpMeeting = deepcopy(mc_import_data.collegeMeeting)
bpMeeting.id = 'meeting-config-bp'
bpMeeting.title = 'Bureau Permanent'
bpMeeting.folderTitle = 'Bureau Permanent'
bpMeeting.shortName = 'Bureau'
bpMeeting.itemWFValidationLevels = deepcopy(LLO_ITEM_CPAS_WF_VALIDATION_LEVELS)
bpMeeting.itemAdviceStates = ['proposed_to_president', ]
bpMeeting.itemAdviceEditStates = ['proposed_to_president', 'validated']

# Conseil communal
casMeeting = deepcopy(mc_import_data.councilMeeting)
casMeeting.id = 'meeting-config-cas'
casMeeting.title = 'Conseil Action Sociale'
casMeeting.folderTitle = 'Conseil Action Sociale'
casMeeting.shortName = 'CAS'
casMeeting.itemWFValidationLevels = deepcopy(LLO_ITEM_CPAS_WF_VALIDATION_LEVELS)
casMeeting.itemAdviceStates = ['proposed_to_president', ]
casMeeting.itemAdviceEditStates = ['proposed_to_president', 'validated']

data.meetingConfigs = (bpMeeting, casMeeting)
# ------------------------------------------------------------------------------
