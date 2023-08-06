from Products.Archetypes.atapi import RichWidget
from Products.Archetypes.atapi import Schema
from Products.Archetypes.atapi import TextField
from Products.PloneMeeting.MeetingItem import MeetingItem
from Products.PloneMeeting.config import WriteDecision


def update_item_schema(baseSchema):

    specificSchema = Schema((
        # specific field for council added for MeetingManagers to transcribe interventions
        TextField(
            name='emergencyMotivation',
            widget=RichWidget(
                rows=15,
                condition="python: here.attribute_is_used('emergencyMotivation')",
                label='emergencyMotivation',
                label_msgid='MeetingCPASLalouviere_label_emergencyMotivation',
                i18n_domain='PloneMeeting',
            ),
            default_content_type="text/html",
            read_permission="PloneMeeting: Read decision",
            searchable=False,
            allowable_content_types=('text/html',),
            default_output_type="text/x-html-safe",
            optional=True,
            write_permission=WriteDecision,
        ),
    ),)
    completeItemSchema = baseSchema + specificSchema.copy()
    return completeItemSchema


MeetingItem.schema = update_item_schema(MeetingItem.schema)


# Classes have already been registered, but we register them again here
# because we have potentially applied some schema adaptations (see above).
# Class registering includes generation of accessors and mutators, for
# example, so this is why we need to do it again now.
from Products.PloneMeeting.config import registerClasses

registerClasses()
