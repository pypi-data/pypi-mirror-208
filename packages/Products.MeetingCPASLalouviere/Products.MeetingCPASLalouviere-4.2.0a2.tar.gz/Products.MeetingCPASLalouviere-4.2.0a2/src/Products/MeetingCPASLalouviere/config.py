# -*- coding: utf-8 -*-

from Products.PloneMeeting import config as PMconfig

product_globals = globals()

PROJECTNAME = "MeetingCPASLalouviere"

# Roles
STYLESHEETS = [{'id': 'meetingcpaslalouviere.css',
                'title': "MeetingCPASLalouvière CSS styles"}]

# group suffixes
PMconfig.EXTRA_GROUP_SUFFIXES = [
    {
        "fct_id": u"budgetimpactreviewers",
        "fct_title": u"Correspondants Financier",
        "fct_orgs": [],
        "enabled": True,
        "fct_management": False,
    },
    {
        "fct_id": u"n1",
        "fct_title": u"N+1",
        "fct_orgs": [],
        "enabled": True,
        "fct_management": False,
    },
    {
        "fct_id": u"n2",
        "fct_title": u"N+2",
        "fct_orgs": [],
        "enabled": True,
        "fct_management": False,
    },
    {
        "fct_id": u"secretaire",
        "fct_title": u"Secrétaire",
        "fct_orgs": [],
        "enabled": True,
        "fct_management": False,
    },
    {
        "fct_id": u"president",
        "fct_title": u"Président",
        "fct_orgs": [],
        "enabled": True,
        "fct_management": False,
    },
]

LLO_ITEM_CPAS_WF_VALIDATION_LEVELS = (
    {'state': 'itemcreated',
     'state_title': 'itemcreated',
     'leading_transition': '-',
     'leading_transition_title': '-',
     'back_transition': 'backToItemCreated',
     'back_transition_title': 'backToItemCreated',
     'suffix': 'creators',
     'extra_suffixes': ['n1', 'n2', 'secretaire', 'president'],
     'enabled': '1',
     },
    {'state': 'proposed_to_n1',
     'state_title': 'proposed_to_n1',
     'leading_transition': 'proposeToN1',
     'leading_transition_title': 'proposeToN1',
     'back_transition': 'backToProposedToN1',
     'back_transition_title': 'backToProposedToN1',
     'suffix': 'n1',
     'extra_suffixes': ['n2', 'secretaire', 'president'],
     'enabled': '1',
     },
    {'state': 'proposed_to_n2',
     'state_title': 'proposed_to_n2',
     'leading_transition': 'proposeToN2',
     'leading_transition_title': 'proposeToN2',
     'back_transition': 'backToProposedToN2',
     'back_transition_title': 'backToProposedToN2',
     'suffix': 'n2',
     'enabled': '1',
     'extra_suffixes': ['secretaire', 'president'],
     },
    {'state': 'proposed_to_secretaire',
     'state_title': 'proposed_to_secretaire',
     'leading_transition': 'proposeToSecretaire',
     'leading_transition_title': 'proposeToSecretaire',
     'back_transition': 'backToProposedToSecretaire',
     'back_transition_title': 'backToProposedToSecretaire',
     'suffix': 'secretaire',
     'enabled': '1',
     'extra_suffixes': ['president'],
     },
    {'state': 'proposed_to_president',
     'state_title': 'proposed_to_president',
     'leading_transition': 'proposeToPresident',
     'leading_transition_title': 'proposeToPresident',
     'back_transition': 'backToProposedToPresident',
     'back_transition_title': 'backToProposedToPresident',
     'suffix': 'president',
     'enabled': '1',
     'extra_suffixes': [],
     },
)

LLO_APPLYED_CPAS_WFA = (
    "accepted_but_modified",
    "pre_accepted",
    "refused",
    "delayed",
    "removed",
    "return_to_proposing_group",
    "no_publication",
    'propose_to_budget_reviewer',
    'waiting_advices',
    'waiting_advices_proposing_group_send_back',
    'item_validation_shortcuts',
    'postpone_next_meeting',
)