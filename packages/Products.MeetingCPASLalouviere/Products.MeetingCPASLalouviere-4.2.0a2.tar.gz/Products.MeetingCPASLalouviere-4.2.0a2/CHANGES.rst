Products.MeetingCPASLalouviere Changelog
====================================

The Products.MeetingCommunes version must be the same as the Products.PloneMeeting version

4.2.0a2 (2023-05-12)
--------------------

- Update access right of extra searches.
  [odelaere]
- Update dashboard collection migrations.
  [odelaere]
- Added missing translations.
  [odelaere]


4.2.0a1 (2023-05-11)
--------------------

- migration to 4.2.
  [odelaere]
- Remove useless override in pm_updates.
  [odelaere]


4.1.4 (2020-08-26)
------------------

- updated back transition backToProposedToSecretaire.


4.1.3.1 (2020-08-26)
--------------------

- Change label proposed to secretary to proposed to DG.


4.1.3 (2020-06-22)
------------------

- Adapted item transitions guards to use `MeetingItemWorkflowConditions._check_required_data`.


4.1.2 (2020-06-03)
------------------

- Fix budget reviewers access.


4.1.1 (2020-05-27)
------------------

- Fix overrides.
  [odelaere]


4.1.1rc3 (2020-05-20)
---------------------

- Changes Manifest.in.


4.1.1rc2 (2020-05-20)
---------------------

- Fixed missing CHANGES.rst.


4.1.1rc1 (2020-05-20)
---------------------
- Compatible for PloneMeeting 4.1

4.0 (2018-08-14)
----------------
- Now MeetingCPASLalouviere using MeetingCommunes who using PloneMeeting

3.3 (2015-02-27)
----------------
- Updated regarding changes in PloneMeeting
- Removed profile 'examples' that loaded examples in english
- Removed dependencies already defined in PloneMeeting's setup.py
- Added parameter MeetingConfig.initItemDecisionIfEmptyOnDecide that let enable/disable
  items decision field initialization when meeting 'decide' transition is triggered
- Added MeetingConfig 'CoDir'
- Added MeetingConfig 'CA'
- Field 'MeetingGroup.signatures' was moved to PloneMeeting

3.2.0.1 (2014-03-06)
--------------------
- Updated regarding changes in PloneMeeting
- Moved some translations from the plone domain to the PloneMeeting domain

3.2.0 (2014-02-12)
------------------
- Updated regarding changes in PloneMeeting
- Use getToolByName where necessary

3.1.0 (2013-11-04)
------------------
- Simplified overrides now that PloneMeeting manage this correctly
- Moved 'add_published_state' to PloneMeeting and renamed to 'hide_decisions_when_under_writing'
- Moved 'searchitemstovalidate' topic to PloneMeeting now that PloneMeeting also manage a 'searchitemstoprevalidate' search

3.0.3dev (unreleased)
---------------------
- Adapted all tests to call PloneMeeting ones
- Added specific search for user gdecoster (http://trac.imio.be/trac/ticket/6354)

2.1.2 (2012-09-19)
------------------
- Original release
