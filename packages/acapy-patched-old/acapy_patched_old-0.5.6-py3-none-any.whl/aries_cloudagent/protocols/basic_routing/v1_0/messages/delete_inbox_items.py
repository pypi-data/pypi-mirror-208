from marshmallow import EXCLUDE, fields

from .....messaging.agent_message import AgentMessage, AgentMessageSchema

from ..message_types import DELETE_INBOX_ITEMS, PROTOCOL_PACKAGE

HANDLER_CLASS = f"{PROTOCOL_PACKAGE}.handlers.delete_inbox_items_handler.DeleteInboxItemsHandler"


class DeleteInboxItems(AgentMessage):

    class Meta:

        handler_class = HANDLER_CLASS
        message_type = DELETE_INBOX_ITEMS
        schema_class = "DeleteInboxItemsSchema"

    def __init__(self, *, inboxitemids=None, **kwargs):
        super().__init__(**kwargs)
        self.inboxitemids = inboxitemids if inboxitemids else []


class DeleteInboxItemsSchema(AgentMessageSchema):

    class Meta:
        model_class = DeleteInboxItems
        unknown = EXCLUDE

    inboxitemids = fields.List(fields.String())
