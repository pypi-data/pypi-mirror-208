# -*- coding: utf-8 -*-
from datetime import datetime

from DateTime import DateTime
from Products.GenericSetup.tool import DEPENDENCY_STRATEGY_NEW
from plone import api
from Products.MeetingCommunes.migrations.migrate_to_4200 import Migrate_To_4200 as MCMigrate_To_4200
from Products.MeetingCPASLalouviere.config import LLO_APPLYED_CPAS_WFA
from Products.MeetingCPASLalouviere.config import LLO_ITEM_CPAS_WF_VALIDATION_LEVELS
import logging

logger = logging.getLogger('MeetingCPASLalouviere')


class Migrate_To_4200(MCMigrate_To_4200):

    def _applyMeetingConfig_fixtures(self):
        logger.info('applying meetingconfig fixtures...')
        self.updateTALConditions("year()", "year")
        self.updateTALConditions("month()", "month")
        logger.info("Adapting 'meetingWorkflow/meetingItemWorkflow' for every MeetingConfigs...")
        for cfg in self.tool.objectValues('MeetingConfig'):
            used_item_attr = list(cfg.getUsedItemAttributes())
            used_item_attr.append("votesResult")
            cfg.setUsedItemAttributes(tuple(used_item_attr))
            cfg.setWorkflowAdaptations(LLO_APPLYED_CPAS_WFA)
            # replace action and review_state column by async actions
            self.updateColumns(to_replace={'actions': 'async_actions',
                                           'review_state': 'review_state_title',})
            # cfg.setItemBudgetInfosStates(self.replace_in_list(u'proposed_to_budgetimpact_reviewer',
            #                                                   u'proposed_to_budget_reviewer',
            #                                                   cfg.getItemBudgetInfosStates())
            #                              )
            # cfg.setItemAdviceStates(self.replace_in_list(u'proposed_to_budgetimpact_reviewer',
            #                                              u'proposed_to_budget_reviewer',
            #                                              cfg.getItemAdviceStates())
            #                         )
            # cfg.setItemAdviceViewStates(self.replace_in_list(u'proposed_to_budgetimpact_reviewer',
            #                                                  u'proposed_to_budget_reviewer',
            #                                                  cfg.getItemAdviceViewStates())
            #                             )
            # cfg.setItemAdviceEditStates(self.replace_in_list(u'proposed_to_budgetimpact_reviewer',
            #                                                  u'proposed_to_budget_reviewer',
            #                                                  cfg.getItemAdviceEditStates())
            #                             )
            cfg.setUseVotes(True)
            cfg.setVotesResultTALExpr(
                "python: item.getPollType() == 'no_vote' and '' or '<p>&nbsp;</p>' + pm_utils.print_votes(item)")
            cfg.setEnabledAnnexesBatchActions(('delete', 'download-annexes'))

    def replace_in_list(self, to_replace, new_value, list):
        result = set()
        for value in list:
            if value == to_replace:
                result.add(new_value)
            else:
                result.add(value)
        return tuple(result)

    def _fixUsedMeetingWFs(self):
        # remap states and transitions
        for cfg in self.tool.objectValues('MeetingConfig'):
            # ensure attr exists
            cfg.getCommittees()
            cfg.getItemCommitteesStates()
            cfg.getItemCommitteesViewStates()
            cfg.getItemPreferredMeetingStates()
            cfg.getItemObserversStates()
            cfg.setMeetingWorkflow('meeting_workflow')
            cfg.setItemWorkflow('meetingitem_workflow')
            cfg.setItemConditionsInterface(
                'Products.MeetingCommunes.interfaces.IMeetingItemCommunesWorkflowConditions')
            cfg.setItemActionsInterface(
                'Products.MeetingCommunes.interfaces.IMeetingItemCommunesWorkflowActions')
            cfg.setMeetingConditionsInterface(
                'Products.MeetingCommunes.interfaces.IMeetingCommunesWorkflowConditions')
            cfg.setMeetingActionsInterface(
                'Products.MeetingCommunes.interfaces.IMeetingCommunesWorkflowActions')

        # delete old unused workflows
        wfs_to_delete = [wfId for wfId in self.wfTool.listWorkflows()
                         if any(x in wfId for x in (
                'meetingitemcpaslalouviere_workflow',
                'meetingcpaslalouviere_workflow',
                'meeting-config-cas__meetingcpaslalouviere_workflow',
                'meeting-config-cas__meetingitemcpaslalouviere_workflow',
                'meeting-config-bp__meetingcpaslalouviere_workflow',
                'meeting-config-bp__meetingitemcpaslalouviere_workflow',
            ))]
        if wfs_to_delete:
            self.wfTool.manage_delObjects(wfs_to_delete)
        logger.info('Done.')

    def _get_wh_key(self, itemOrMeeting):
        """Get workflow_history key to use, in case there are several keys, we take the one
           having the last event."""
        keys = itemOrMeeting.workflow_history.keys()
        if len(keys) == 1:
            return keys[0]
        else:
            lastEventDate = DateTime('1950/01/01')
            keyToUse = None
            for key in keys:
                if itemOrMeeting.workflow_history[key][-1]['time'] > lastEventDate:
                    lastEventDate = itemOrMeeting.workflow_history[key][-1]['time']
                    keyToUse = key
            return keyToUse

    def _adaptWFHistoryForItemsAndMeetings(self):
        """We use PM default WFs, no more meeting(item)lalouviere_workflow..."""
        logger.info('Updating WF history items and meetings to use new WF id...')
        catalog = api.portal.get_tool('portal_catalog')
        for cfg in self.tool.objectValues('MeetingConfig'):
            # this will call especially part where we duplicate WF and apply WFAdaptations
            cfg.registerPortalTypes()
            for brain in catalog(portal_type=(cfg.getItemTypeName(), cfg.getMeetingTypeName())):
                itemOrMeeting = brain.getObject()
                itemOrMeetingWFId = self.wfTool.getWorkflowsFor(itemOrMeeting)[0].getId()
                if itemOrMeetingWFId not in itemOrMeeting.workflow_history:
                    wf_history_key = self._get_wh_key(itemOrMeeting)
                    itemOrMeeting.workflow_history[itemOrMeetingWFId] = \
                        tuple(itemOrMeeting.workflow_history[wf_history_key])
                    del itemOrMeeting.workflow_history[wf_history_key]
                    # do this so change is persisted
                    itemOrMeeting.workflow_history = itemOrMeeting.workflow_history
                else:
                    # already migrated
                    break
        logger.info('Done.')

    def _doConfigureItemWFValidationLevels(self, cfg):
        """Apply correct itemWFValidationLevels and fix WFAs."""
        cfg.setItemWFValidationLevels(LLO_ITEM_CPAS_WF_VALIDATION_LEVELS)
        cfg.setWorkflowAdaptations(LLO_APPLYED_CPAS_WFA)

    def _hook_custom_meeting_to_dx(self, old, new):
        pass

    def _hook_after_meeting_to_dx(self):
        self._applyMeetingConfig_fixtures()
        self._adaptWFHistoryForItemsAndMeetings()
        self.update_wf_states_and_transitions()

    def update_wf_states_and_transitions(self):
        self.updateWFStatesAndTransitions(
            query={'portal_type': ('MeetingItemPb', 'MeetingItemcas'),
                   "review_state": "proposed_to_budgetimpact_reviewer"},
            review_state_mappings={
                'proposed_to_budgetimpact_reviewer': 'proposed_to_budget_reviewer',
            },
            # will be done by next step in migration
            update_local_roles=False)

    def _remove_old_dashboardcollection(self):
        for cfg in self.tool.objectValues('MeetingConfig'):
            items = cfg.searches.searches_items
            meetings = cfg.searches.searches_items
            decided = cfg.searches.searches_items
            for folder in (items, meetings, decided):
                api.content.delete(objects=folder.listFolderContents())
            cfg.setToDoListSearches(())

    def post_migration_fixtures(self):
        logger.info("Adapting todo searches ...")
        for cfg in self.tool.objectValues('MeetingConfig'):
            cfg_dashboard_path = "portal_plonemeeting/{}/searches/searches_items/".format(cfg.getId())
            to_dashboard_ids = ["searchallitemstoadvice",
                                "searchallitemsincopy",
                                "searchitemstocorrect",
                                "searchproposedtobudgetreviewer",
                                "searchproposedton1",
                                "searchproposedton2",
                                "searchproposedtosecretaire",
                                "searchproposedtopresident",
                                ]
            searches = [self.catalog.resolve_path(cfg_dashboard_path + id) for id in to_dashboard_ids]
            cfg.setToDoListSearches(tuple([search.UID() for search in searches if search is not None]))

    def run(self,
            profile_name=u'profile-Products.MeetingCPASLalouviere:default',
            extra_omitted=[]):
        self._remove_old_dashboardcollection()
        super(Migrate_To_4200, self).run(extra_omitted=extra_omitted)
        self.reinstall(profiles=[profile_name],
                       ignore_dependencies=True,
                       dependency_strategy=DEPENDENCY_STRATEGY_NEW)
        self.post_migration_fixtures()
        logger.info('Done migrating to MeetingCPASLalouviere 4200...')


# The migration function -------------------------------------------------------
def migrate(context):
    '''
    This migration function:
       1) Change MeetingConfig workflows to use meeting_workflow/meetingitem_workflow;
       2) Call PloneMeeting migration to 4200 and 4201;
       3) In _after_reinstall hook, adapt items and meetings workflow_history
          to reflect new defined workflow done in 1);
    '''
    migrator = Migrate_To_4200(context)
    migrator.run()
    migrator.finish()
